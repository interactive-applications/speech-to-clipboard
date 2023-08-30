import os
import sys
import configparser
from tkinter import Event
from typing import Callable
import customtkinter as tk
import openai
import humanize
import pyperclip
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
from openai.openai_object import OpenAIObject
from utils.replacer import Replacer


WAV_FILE_PATH = "./audio/output.wav"
REPLACEMENTS_FILE_PATH = "./resources/replacements.json"
OPENAI_API_KEY_ENV_VAR = "WHISPER_KEYBOARD_API_KEY"


class Transcriber:
    
    def __init__(self, openai_api_key: str = "") -> None:
        openai.api_key = openai_api_key
    
    def transcribe(self, wav_file_path: str = "./audio/output.wav") -> str:
        with open(wav_file_path, "rb") as audio_file:
            try:
                transcript: OpenAIObject = openai.Audio.transcribe(
                    "whisper-1", audio_file
                )
                return transcript['text']
            except openai.error.InvalidRequestError as e:
                return "Error: " + str(e)
            except Exception as e: #pylint: disable=broad-except
                return "Error: " + str(e)


class FramedLabel(tk.CTkFrame):
    
    def __init__(self, master, text: str, justify=tk.LEFT, **kwargs) -> None:
        super().__init__(master, **kwargs)
        
        self.label = tk.CTkLabel(self, text=text, justify=justify)
        self.label.grid(row=0, column=0, padx=10)
    
    def configure(self, *args, **kwargs) -> None:
        self.label.configure(*args, **kwargs)
    
    def cget(self, *args, **kwargs) -> None:
        try:
            return self.label.cget(*args, **kwargs)
        except AttributeError:
            return super().cget(*args, **kwargs)


class CachedText(tk.CTkTextbox):
    
    def __init__(self, *args, **kwargs) -> None:
        """A Text widget that caches the text and only calls the modified event when the text is changed."""
        self.text_cache = ""
        super().__init__(*args, **kwargs)
        self.on_changed_callbacks = []
        self.bind("<<Modified>>", self._on_text_changed)
    
    def add_on_changed_callback(
        self, func: Callable[[Event, str], None]
    ) -> None:
        self.on_changed_callbacks.append(func)
    
    def remove_on_changed_callback(
        self, func: Callable[[Event, str], None]
    ) -> None:
        self.on_changed_callbacks.remove(func)
    
    def _on_text_changed(self, event: Event) -> None:
        """
        NOTE: this is called twice when the text is changed. 
        This is not handled. Be aware of this.
        At the end of this function, the modified flag must be reset.
        Otherwise, the event will not be called again.
        """
        curr_text = self.get_text()
        
        if curr_text != self.text_cache:
            # does not seem to work
            self.event_generate("<<TextChanged>>")
            # thus, call our probprietary subscribers' functions
            for subscriber in self.on_changed_callbacks:
                try:
                    subscriber(event, curr_text)
                except Exception: #pylint: disable=broad-except
                    pass
        
        self.text_cache = curr_text
        # reset the modified flag
        # if this is not done, the modified event will not be called again
        event.widget.edit_modified(False)
    
    def get_text(self) -> str:
        txt = self.get(1.0, tk.END)
        # remove the last newline, which tkinter seems to add automatically
        if txt.endswith("\n"):
            txt = txt[:-1]
        return txt
    
    def get_text_from_cache(self) -> str:
        return self.text_cache
    
    def insert(self, *args, **kwargs) -> str:
        super().insert(*args, **kwargs)
        self.text_cache = self.get_text()
        return self.text_cache
    
    def clear(self) -> None:
        super().delete(1.0, tk.END)
        self.text_cache = self.get_text()
    
    def set_text(self, text) -> str:
        self.clear()
        self.insert(tk.END, text)
        self.text_cache = self.get_text()
        return self.text_cache
    
    def append_text(self, text, add_space=True) -> str:
        if add_space:
            self.insert(tk.END, " ")
        self.insert(tk.END, text)
        self.text_cache = self.get_text()
        return self.text_cache


class AudioRecorder:
    
    def __init__(self, wav_file_path: str = "./audio/output.wav") -> None:
        self.frames = []
        self.is_recording = False
        self.device_index = None
        self.channels = 1
        self.rate = 44100
        self.record_seconds = 5
        self.devices = self.get_devices()
        self.stream = None
        self.wav_file = wav_file_path
    
    @staticmethod
    def trim_leading_silence(audio_file) -> AudioSegment:
        return audio_file[detect_leading_silence(audio_file):]
    
    @staticmethod
    def trim_trailing_silence(audio_file) -> AudioSegment:
        return AudioRecorder.trim_leading_silence(audio_file.reverse()
                                                 ).reverse()
    
    @staticmethod
    def strip_silence(audio_file) -> AudioSegment:
        # from: https://stackoverflow.com/a/69331596
        return AudioRecorder.trim_trailing_silence(
            AudioRecorder.trim_leading_silence(audio_file)
        )
    
    def get_devices(self) -> list[str]:
        devices = sd.query_devices()
        # filter out devices that do not support recording
        devices = [
            device for device in devices if device['max_input_channels'] > 0
        ]
        return devices
    
    def get_device_name(self, device_index: int) -> str:
        if device_index >= len(self.devices) or device_index < 0:
            return f"invalid device index: {device_index}"
        return self.devices[device_index]['name']
    
    def start_recording(self, device_index: int) -> None:
        self.device_index = device_index
        self.is_recording = True
        self.frames = []
        sd.default.device = device_index
        sd.default.channels = self.channels
        sd.default.samplerate = self.rate
        sd.default.dtype = 'int16'
        sd.default.blocksize = 1024
        sd.default.latency = 'low'
        self.stream = sd.InputStream(callback=self.callback)
        self.stream.start()
    
    def stop_recording(self) -> None:
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        self.stream = None
    
    def callback(self, indata, frames, time, status): #pylint: disable=unused-argument
        if status:
            print(status, file=sys.stderr)
        self.frames.append(indata.copy())
    
    def delete_audio(self) -> None:
        if os.path.exists(self.wav_file):
            os.remove(self.wav_file)
    
    def save_audio(self) -> float:
        # create the path if it does not exist. the path is relative to the current working directory
        os.makedirs(os.path.dirname(self.wav_file), exist_ok=True)
        
        data = [item for sublist in self.frames for item in sublist]
        sf.write(self.wav_file, data, self.rate)
        
        # load the audio file using pydub
        audio = AudioSegment.from_wav(self.wav_file)
        
        # trim silence from start and end
        trimmed_audio: AudioSegment = self.strip_silence(audio)
        
        # get the length of the resulting file in seconds
        length = trimmed_audio.duration_seconds
        
        # save the trimmed audio file
        trimmed_audio.export(self.wav_file, format='wav')
        
        return length


class App:
    ready_color = "#b8e994"
    recording_color = "#ff6961"
    transcribing_color = "#FFA500"
    record_text = "REC"
    pad = 10
    
    config_file_path = "./resources/config.ini"
    
    raw_transcript = ""
    disable_replace_warning = "Disable 'Replacement' to edit text."
    
    def __init__(
        self,
        master: tk.CTk,
        win_title: str = "Whisper Clip",
        wav_file_path: str = "./audio/output.wav",
        openai_api_key_env_var: str = "WHISPER_KEYBOARD_API_KEY"
    ) -> None:
        self.master = master
        self.master.title(win_title)
        
        icon_file = self.abs_path('./resources/icon.ico')
        
        # if windows
        if os.name == 'nt':
            # the following lines make the icon work in the windows taskbar
            import ctypes #pylint: disable=import-outside-toplevel
            myappid = u'com.chia.whisperkeyboard' #pylint: disable=redundant-u-string-prefix
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                myappid
            )
        self.master.iconbitmap(icon_file)
        self.master.wm_iconbitmap(icon_file)
        
        self.master.minsize(width=500, height=200)
        
        self.config = configparser.ConfigParser()
        
        self.wav_file = wav_file_path
        self.recorder = AudioRecorder(wav_file_path=self.wav_file)
        
        # create config file if it does not exist
        if not os.path.exists(self.config_file_path):
            self.config['audio'] = {'device': self.recorder.get_device_name(0)}
            self.config['openai'] = {'api_key': 'your-api-key-here'}
            with open(self.config_file_path, 'w',
                        encoding='utf-8') as configfile:
                self.config.write(configfile)
        
        self.config.read(self.config_file_path, encoding='utf-8')
        self.device_var = tk.StringVar(master)
        selected_device = self.config.get(
            'audio', 'device', fallback=self.recorder.get_device_name(0)
        )
        
        available_devices = [device['name'] for device in self.recorder.devices]
        print("Devices:\n - " + "\n - ".join(available_devices))
        
        if selected_device in available_devices:
            self.device_var.set(selected_device)
        else:
            try:
                self.device_var.set(self.recorder.get_device_name(0))
            except IndexError:
                self.device_var.set("No devices found")
        
        openai_api_key = os.getenv(openai_api_key_env_var) or self.config.get(
            'openai', 'api_key', fallback='no-api-key-found-in-config'
        )
        print(
            f"Using OpenAI API Key: {openai_api_key[:3]}...{openai_api_key[-4:]}"
        )
        
        self.transcriber = Transcriber(openai_api_key=openai_api_key)
        
        pad = self.pad
        v_pad = (pad, 0)
        row = 0
        
        master.columnconfigure(0, weight=0)
        master.columnconfigure(1, weight=1)
        
        master.grid_rowconfigure(row, weight=0)
        
        self.device_dropdown = tk.CTkOptionMenu(
            master, variable=self.device_var, values=available_devices
        )
        self.device_dropdown.grid(row=row, column=0, padx=(pad, 0), pady=v_pad)
        
        self.status_output = FramedLabel(master, text="", justify=tk.LEFT)
        self.status_output.grid(
            row=row, column=1, padx=pad, pady=v_pad, sticky=tk.EW
        )
        
        row += 1
        
        settings_frame = tk.CTkFrame(master)
        settings_frame.grid(
            row=row, column=0, columnspan=2, sticky=tk.EW, padx=pad, pady=v_pad
        )
        
        self.append = tk.CTkCheckBox(settings_frame, text="Append")
        self.append.grid(row=0, column=0, padx=pad, pady=pad, sticky=tk.W)
        
        self.replace = tk.CTkCheckBox(
            settings_frame,
            text="Replacement",
            command=lambda: self.on_replace_changed(copy_to_clipboard=True)
        )
        self.replace.grid(row=0, column=1, padx=pad, pady=pad, sticky=tk.W)
        self.replace.select()
        
        row += 1
        
        self.record_button = tk.CTkButton(
            master, text=self.record_text, command=self.toggle_recording
        )
        self.record_button.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            padx=pad,
            pady=v_pad,
        )
        
        row += 1
        
        master.grid_rowconfigure(row, weight=1)
        
        self.text_output = CachedText(master, wrap=tk.WORD)
        self.text_output.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky=tk.NSEW,
            padx=pad,
            pady=pad,
        )
        self.text_output.add_on_changed_callback(self.on_text_changed)
        
        self.print_status("Ready")
        self.ready_color = self.record_button.cget('fg_color')
        
        # add replacer
        try:
            self.replacer = Replacer(REPLACEMENTS_FILE_PATH)
        except Exception as e: #pylint: disable=broad-except
            self.print_status("Error loading Replacer.")
            self.text_output.set_text(str(e))
    
    def on_text_changed(self, event: Event, text: str) -> None: #pylint: disable=unused-argument
        if not self.replace.get():
            self.raw_transcript = text
            if self.get_status() == self.disable_replace_warning:
                self.print_status("Ready")
        else:
            if self.get_status() != self.disable_replace_warning:
                self.print_status(self.disable_replace_warning)
    
    def abs_path(self, path: str) -> str:
        return os.path.join(os.path.dirname(__file__), path)
    
    def print_status(self, text: str) -> None:
        print(text)
        self.status_output.configure(text=text)
    
    def get_status(self) -> str:
        return self.status_output.cget('text')
    
    def write_text_output(self, text: str, append: bool = False) -> None:
        if not append:
            self.text_output.set_text(text)
        else:
            self.text_output.append_text(text, add_space=True)
    
    def get_text_output(self) -> str:
        return self.text_output.get_text()
    
    def refresh_ui(self) -> None:
        self.master.update()
    
    def on_replace_changed(self, copy_to_clipboard: True) -> None:
        if self.replace.get():
            self.write_text_output(self.replacer.replace(self.raw_transcript))
        else:
            self.write_text_output(self.raw_transcript)
        
        if copy_to_clipboard:
            self.copy_to_clipboard()
    
    def copy_to_clipboard(self) -> None:
        # wysiwyg - copy the current text
        pyperclip.copy(self.get_text_output())
        self.print_status("Done. Copied to clipboard.")
    
    def toggle_recording(self) -> None:
        if not self.recorder.is_recording:
            device_index = [device['name'] for device in self.recorder.devices
                           ].index(self.device_var.get())
            self.record_button.configure(fg_color=self.recording_color)
            self.record_button.configure(text="Stop")
            self.print_status("Recording...")
            self.refresh_ui()
            self.recorder.start_recording(device_index)
        else:
            self.print_status("Stopping recording...")
            self.recorder.stop_recording()
            self.print_status("Deleting existing file...")
            self.recorder.delete_audio()
            self.print_status("Saving audio...")
            length = self.recorder.save_audio()
            
            self.record_button.configure(text="...")
            self.record_button.configure(fg_color=self.transcribing_color)
            
            length_str = humanize.precisedelta(length, format='%0.2f')
            self.print_status(f"Saved. Length: {length_str}")
            # save config file
            self.config['audio'] = {'device': self.device_var.get()}
            with open(self.config_file_path, 'w',
                        encoding='utf-8') as configfile:
                self.config.write(configfile)
            
            if length > 1:
                # transcribe
                self.print_status(f"Transcribing {length_str}...")
                
                # refresh ui
                self.refresh_ui()
                
                # transribe
                try:
                    transcript = self.transcriber.transcribe(self.wav_file)
                except Exception as e: #pylint: disable=broad-except
                    self.print_status("Error transcribing.")
                    self.text_output.set_text(str(e))
                    return
                
                if self.append.get():
                    self.raw_transcript = self.raw_transcript + " " + transcript
                else:
                    self.raw_transcript = transcript
                
                # replace if enabled, and write to output
                self.on_replace_changed(copy_to_clipboard=False)
                
                # copy to clipboard
                self.copy_to_clipboard()
            else:
                self.print_status("Recording too short or silence.")
            
            self.record_button.configure(text=self.record_text)
            self.record_button.configure(fg_color=self.ready_color)


root = tk.CTk()
app = App(
    root,
    win_title="Whisper Clip",
    wav_file_path=WAV_FILE_PATH,
    openai_api_key_env_var=OPENAI_API_KEY_ENV_VAR
)
root.mainloop()
