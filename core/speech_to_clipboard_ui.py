import os
from tkinter import Event
import customtkinter as tk

from core.speech_to_clipboard import SpeechToClipboard
from core.ui.components import FramedLabel, CachedText


class SpeechToClipboardUI:
    ready_color = "#b8e994"
    recording_color = "#ff6961"
    transcribing_color = "#FFA500"
    record_text = "REC"
    pad = 10
    
    raw_transcript = ""
    disable_replace_warning = "Disable 'Replacement' to edit text."
    
    def __init__(
        self,
        master: tk.CTk = None,
        win_title: str = "Whisper Clip",
        icon_file_path: str = "./resources/icon.ico",
        speech_to_clip: SpeechToClipboard = None,
    ) -> None:
        root_created = False
        if master is None:
            master = self.create_root_window()
            root_created = True
        
        self.speech_to_clip = speech_to_clip
        
        self.master = master
        self.master.title(win_title)
        
        SpeechToClipboardUI.try_set_icon_to(self.master, icon_file_path)
        
        self.master.minsize(width=500, height=200)
        
        pad = self.pad
        v_pad = (pad, 0)
        row = 0
        
        master.columnconfigure(0, weight=0)
        master.columnconfigure(1, weight=1)
        
        master.grid_rowconfigure(row, weight=0)
        
        self.device_var = tk.StringVar(master)
        selected_device = self.speech_to_clip.get_selected_audio_device_name()
        self.device_var.set(selected_device)
        self.device_dropdown = tk.CTkOptionMenu(
            master,
            variable=self.device_var,
            command=self.speech_to_clip.try_set_audio_device_by_name,
            values=self.speech_to_clip.get_available_audio_device_names()
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
        
        row += 1
        
        self.credits = FramedLabel(
            master,
            "— Claus Helfenschneider Interactive Applications —",
        )
        self.credits.configure(
            justify=tk.RIGHT,
            text_color="#aaaaaa",
            anchor=tk.CENTER,
        )
        self.credits.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            padx=pad,
            pady=(0, pad)
        )
        
        self.print_status("Ready")
        self.ready_color = self.record_button.cget('fg_color')
        
        if root_created:
            self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)
            self.master.mainloop()
    
    def on_window_close(self) -> None:
        self.speech_to_clip.cleanup()
        self.master.destroy()
    
    @staticmethod
    def create_root_window() -> tk.CTk:
        root = tk.CTk()
        return root
    
    @staticmethod
    def abs_path(path: str) -> str:
        # return absolute path of file relative to the parent dir of this file
        file_path = os.path.dirname(__file__)
        parent_dir_path = os.path.dirname(file_path)
        return os.path.join(parent_dir_path, path)
    
    @staticmethod
    def try_set_icon_to(master: tk.CTk, path: str) -> None:
        try:
            icon_file = SpeechToClipboardUI.abs_path(path)
            # if windows
            if os.name == 'nt':
                # the following lines make the icon work in the windows taskbar
                import ctypes #pylint: disable=import-outside-toplevel
                myappid = u'com.chia.whisperkeyboard' #pylint: disable=redundant-u-string-prefix
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    myappid
                )
            
            master.iconbitmap(icon_file)
            master.wm_iconbitmap(icon_file)
        except Exception as e: #pylint: disable=broad-except
            print(e)
    
    @staticmethod
    def create_warning_dialog(
        win_title: str, msg: str, icon_file_path: str
    ) -> tk.CTk:
        root = SpeechToClipboardUI.create_root_window()
        row = 0
        root.columnconfigure(0, weight=1)
        root.grid_rowconfigure(row, weight=1)
        root.title(win_title)
        text_output = CachedText(root, wrap=tk.WORD)
        text_output.grid(
            row=row,
            column=0,
            sticky=tk.NSEW,
            padx=10,
            pady=(10, 0),
        )
        text_output.set_text(msg)
        button = tk.CTkButton(root, text="OK", command=root.destroy)
        button.grid(
            row=row + 1,
            column=0,
            padx=10,
            pady=10,
            sticky=tk.NSEW,
        )
        SpeechToClipboardUI.try_set_icon_to(root, icon_file_path)
        
        root.mainloop()
        return root
    
    def on_text_changed(self, event: Event, text: str) -> None: #pylint: disable=unused-argument
        if not self.replace.get():
            self.raw_transcript = text
            if self.get_status() == self.disable_replace_warning:
                self.print_status("Ready")
        else:
            if self.get_status() != self.disable_replace_warning:
                self.print_status(self.disable_replace_warning)
    
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
            self.write_text_output(
                self.speech_to_clip.replace_text(self.raw_transcript)
            )
        else:
            self.write_text_output(self.raw_transcript)
        
        if copy_to_clipboard:
            self.copy_to_clipboard()
    
    def copy_to_clipboard(self) -> None:
        # wysiwyg - copy the current text
        self.speech_to_clip.copy_to_clipboard(self.get_text_output())
        self.print_status("Done. Copied to clipboard.")
    
    def toggle_recording(self) -> None:
        if not self.speech_to_clip.is_recording():
            self.record_button.configure(fg_color=self.recording_color)
            self.record_button.configure(text="Stop")
            self.print_status("Recording...")
            self.refresh_ui()
            self.speech_to_clip.start_recording()
        else:
            self.print_status("Stopping recording...")
            duration = self.speech_to_clip.stop_and_save_recording()
            
            self.record_button.configure(text="Transcribing...")
            self.record_button.configure(fg_color=self.transcribing_color)
            
            duration_str = self.speech_to_clip.get_humanized_duration(duration)
            self.print_status(f"Saved. Length: {duration_str}")
            
            if duration > 1:
                # transcribe
                self.print_status(f"Transcribing {duration_str}...")
                
                # refresh ui
                self.refresh_ui()
                
                # transribe
                try:
                    transcript = self.speech_to_clip.transcribe_recording(
                        replace=False
                    )
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
