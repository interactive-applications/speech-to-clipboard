import os
import sys
import configparser
import tkinter as tk
from tkinter.font import Font
import openai
import humanize
import pyperclip
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
from openai.openai_object import OpenAIObject


WAV_FILE_PATH = "./audio/output.wav"
OPENAI_API_KEY_ENV_VAR = "WHISPER_KEYBOARD_API_KEY"


class Transcriber:
    
    def __init__(self, openai_api_key=""):
        openai.api_key = openai_api_key
    
    def transcribe(self, wav_file_path="./audio/output.wav"):
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


class AudioRecorder:
    
    def __init__(self, wav_file_path="./audio/output.wav"):
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
    def trim_leading_silence(audio_file):
        return audio_file[detect_leading_silence(audio_file):]
    
    @staticmethod
    def trim_trailing_silence(audio_file):
        return AudioRecorder.trim_leading_silence(audio_file.reverse()
                                                 ).reverse()
    
    @staticmethod
    def strip_silence(audio_file):
        # from: https://stackoverflow.com/a/69331596
        return AudioRecorder.trim_trailing_silence(
            AudioRecorder.trim_leading_silence(audio_file)
        )
    
    def get_devices(self):
        devices = sd.query_devices()
        # filter out devices that do not support recording
        devices = [
            device for device in devices if device['max_input_channels'] > 0
        ]
        return devices
    
    def start_recording(self, device_index):
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
    
    def stop_recording(self):
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        self.stream = None
    
    def callback(self, indata, frames, time, status): #pylint: disable=unused-argument
        if status:
            print(status, file=sys.stderr)
        self.frames.append(indata.copy())
    
    def delete_audio(self):
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
    halfpad = pad // 2
    
    config_file_path = "./resources/config.ini"
    
    def __init__(
        self,
        master,
        win_title="Whisper Clip",
        wav_file_path="./audio/output.wav",
        openai_api_key_env_var="WHISPER_KEYBOARD_API_KEY"
    ):
        self.master = master
        self.master.title(win_title)
        
        # font setup
        mono = Font(
            family=self.abs_path("./resources/IBMPlexMono-Regular.ttf"),
            size=10
        )
        self.master.option_add("*Font", mono)
        #sans = Font(family="./resources/IBMPlexSans-Regular", size=10)
        #self.master.option_add("*Font", sans)
        
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
        
        self.master.minsize(width=500, height=300)
        
        self.config = configparser.ConfigParser()
        
        self.wav_file = wav_file_path
        self.recorder = AudioRecorder(wav_file_path=self.wav_file)
        
        # create config file if it does not exist
        if not os.path.exists(self.config_file_path):
            self.config['audio'] = {'device': self.recorder.devices[0]['name']}
            self.config['openai'] = {'api_key': 'your-api-key-here'}
            with open(self.config_file_path, 'w',
                        encoding='utf-8') as configfile:
                self.config.write(configfile)
        
        self.config.read(self.config_file_path, encoding='utf-8')
        self.device_var = tk.StringVar(master)
        #self.device_var.set(self.config.get('audio', 'device', fallback=self.recorder.devices[0]['name']))
        selected_device = self.config.get(
            'audio', 'device', fallback=self.recorder.devices[0]['name']
        )
        available_devices = [device['name'] for device in self.recorder.devices]
        print("Devices:" + "\n".join(available_devices))
        if selected_device in available_devices:
            self.device_var.set(selected_device)
        else:
            try:
                self.device_var.set(self.recorder.devices[0]['name'])
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
        half_pad = self.halfpad
        
        row_frame = tk.Frame(master)
        row_frame.pack(fill=tk.X, padx=pad, pady=half_pad)
        
        self.device_dropdown = tk.OptionMenu(
            row_frame, self.device_var, *available_devices
        )
        self.device_dropdown.pack(side=tk.LEFT)
        self.status_output = tk.Label(
            row_frame, text="", anchor=tk.W, justify=tk.LEFT
        )
        self.status_output.pack(side=tk.LEFT, fill=tk.X)
        self.record_button = tk.Button(
            master,
            text=self.record_text,
            command=self.toggle_recording,
            bg=self.ready_color
        )
        self.record_button.pack(fill=tk.X, padx=pad, pady=half_pad)
        self.text_output = tk.Text(master, height=10, width=50, font=mono)
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)
        
        self.status_output.config(font=mono)
        
        self.print_status("Ready")
    
    def abs_path(self, path):
        return os.path.join(os.path.dirname(__file__), path)
    
    def print_status(self, text):
        print(text)
        self.status_output.config(text=text)
    
    def clear_text_output(self):
        self.text_output.delete(1.0, tk.END)
    
    def write_text_output(self, text):
        self.clear_text_output()
        self.text_output.insert(tk.END, text)
    
    def refresh_ui(self):
        self.master.update()
    
    def toggle_recording(self):
        if not self.recorder.is_recording:
            device_index = [device['name'] for device in self.recorder.devices
                           ].index(self.device_var.get())
            self.record_button.config(bg=self.recording_color)
            self.record_button.config(text="Stop")
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
            
            self.record_button.config(text="...")
            self.record_button.config(bg=self.transcribing_color)
            
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
                self.clear_text_output()
                # refresh ui
                self.refresh_ui()
                # transribe
                transcript = self.transcriber.transcribe(self.wav_file)
                # write to output
                self.write_text_output(transcript)
                pyperclip.copy(transcript)
                self.print_status("Done. Copied to clipboard.")
            else:
                self.print_status("Recording too short or silence.")
            
            self.record_button.config(text=self.record_text)
            self.record_button.config(bg=self.ready_color)


root = tk.Tk()
app = App(
    root,
    win_title="Whisper Clip",
    wav_file_path=WAV_FILE_PATH,
    openai_api_key_env_var=OPENAI_API_KEY_ENV_VAR
)
root.mainloop()
