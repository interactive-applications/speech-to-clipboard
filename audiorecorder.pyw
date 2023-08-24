import os
import sys
import configparser
import humanize
import tkinter as tk
import sounddevice as sd
import soundfile as sf

class AudioRecorder:
    
    WAV_FILE = "./audio/output.wav"
    
    def __init__(self):
        self.frames = []
        self.is_recording = False
        self.device_index = None
        self.channels = 1
        self.rate = 44100
        self.record_seconds = 5
        self.devices = self.get_devices()
    
    def get_devices(self):
        devices = sd.query_devices()
        # filter out devices that do not support recording
        devices = [device for device in devices if device['max_input_channels'] > 0]
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
        sd.InputStream(callback=self.callback).start()

    def stop_recording(self):
        self.is_recording = False

    def callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.frames.append(indata.copy())
    
    def delete_audio(self):
        if os.path.exists(self.WAV_FILE):
            os.remove(self.WAV_FILE)
    
    def save_audio(self):
        # create the path if it does not exist. the path is relative to the current working directory
        os.makedirs(os.path.dirname(self.WAV_FILE), exist_ok=True)
        
        data = [item for sublist in self.frames for item in sublist]
        sf.write(self.WAV_FILE, data, self.rate)

class App:
    def __init__(self, master):
        self.recorder = AudioRecorder()
        self.master = master
        self.config = configparser.ConfigParser()
        
        # create config file if it does not exist
        if not os.path.exists('config.ini'):
            self.config['audio'] = {'device': self.recorder.devices[0]['name']}
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
        
        self.config.read('config.ini')
        self.device_var = tk.StringVar(master)
        self.device_var.set(self.config.get('audio', 'device', fallback=self.recorder.devices[0]['name']))
        self.device_dropdown = tk.OptionMenu(master, self.device_var, *[device['name'] for device in self.recorder.devices])
        self.device_dropdown.pack()
        self.record_button = tk.Button(master, text="Record", command=self.toggle_recording)
        self.record_button.pack()
        self.status_output = tk.Label(master, text="")
        self.status_output.pack()
        self.text_output = tk.Text(master, height=10, width=50)
        self.text_output.pack()
        self.print_status("Ready")
    
    def print_status(self, text):
        print(text)
        self.status_output.config(text=text)
    
    def toggle_recording(self):
        if not self.recorder.is_recording:
            device_index = [device['name'] for device in self.recorder.devices].index(self.device_var.get())
            self.recorder.start_recording(device_index)
            self.record_button.config(text="Stop")
            self.print_status("Recording...")
        else:
            self.print_status("Stopping recording...")
            self.recorder.stop_recording()
            self.print_status("Deleting existing file...")
            self.recorder.delete_audio()
            self.print_status("Saving audio...")
            self.recorder.save_audio()
            self.record_button.config(text="Record")
            length = len(self.recorder.frames) / float(self.recorder.rate) * 1000
            self.print_status(f"Saved. Length: {humanize.precisedelta(length, format='%0.2f')}")
            # save config file
            self.config['audio'] = {'device': self.device_var.get()}
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

root = tk.Tk()
app = App(root)
root.mainloop()