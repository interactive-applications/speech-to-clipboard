import os
import configparser
import humanize
import pyperclip

from core.replacer import Replacer
from core.transcriber import Transcriber
from core.audiorecorder import AudioRecorder, AudioDevice


class SpeechToClipboard:
    
    def __init__(
        self,
        audio_file_path: str,
        config_file_path: str,
        replacemetns_file_path: str,
        openai_api_key_env_var: str = "WHISPER_KEYBOARD_API_KEY"
    ) -> None:
        
        self.audio_file_path = audio_file_path
        self.config_file_path = config_file_path
        self.replacements_file_path = replacemetns_file_path
        
        # audio device to use
        self.device_index = 0
        self.last_recording_duration = 0
        
        self.config = configparser.ConfigParser(
            interpolation=configparser.Interpolation()
        )
        
        self.recorder = AudioRecorder(wav_file_path=self.audio_file_path)
        
        # create config file if it does not exist
        self.ensure_config_file()
        self.read_config_file()
        
        openai_api_key = os.getenv(openai_api_key_env_var) or self.config.get(
            'openai', 'api_key', fallback='no-api-key-found-in-config'
        )
        print(
            f"Using OpenAI API Key: {openai_api_key[:3]}...{openai_api_key[-4:]}"
        )
        
        self.transcriber = Transcriber(openai_api_key=openai_api_key)
        self.replacer = Replacer(self.replacements_file_path)
    
    def ensure_config_file(self) -> None:
        """
        Create config file if it does not exist.
        """
        if not os.path.exists(self.config_file_path):
            self.config['audio'] = {'device': self.recorder.get_device_name(0)}
            self.config['openai'] = {'api_key': 'your-api-key-here'}
            with open(self.config_file_path, 'w',
                        encoding='utf-8') as configfile:
                self.config.write(configfile)
    
    def read_config_file(self) -> None:
        """
        Read and parse the config file.
        """
        self.config.read(self.config_file_path, encoding='utf-8')
        device_name = self.config.get(
            'audio', 'device', fallback=self.recorder.get_device_name(0)
        )
        self.try_set_audio_device_by_name(device_name)
    
    def write_config_file(self) -> None:
        """
        Write the config file.
        """
        with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
    
    def set_audio_device_by_name(self, device_name: str) -> None:
        """
        Set the audio device by name.
        
        :param device_name: The name of the device to set.
        :raises ValueError: If the device name is invalid.
        """
        available_devices = self.get_available_audio_devices()
        
        for device in available_devices:
            if device.name_equals(device_name):
                self.device_index = device.index
                self.set_audio_device_by_index(self.device_index)
                return
        
        raise ValueError(
            f"Invalid device name: '{device_name}'.\n {self.get_available_audio_devices_str()}"
        )
    
    def try_set_audio_device_by_name(self, device_name: str) -> bool:
        """
        Try to set the audio device by name, without raising an exception.
        Falls back to previously selected device or default device, if the device name is invalid.
        
        :param device_name: The name of the device to set.
        :return: True if the device was set, False otherwise.
        """
        try:
            self.set_audio_device_by_name(device_name)
            return True
        except ValueError:
            pass
        
        self.try_set_audio_device_by_index(self.device_index)
        
        return False
    
    def set_audio_device_by_index(self, device_index: int) -> None:
        """
        Set the audio device by index.
        
        :param device_index: The index of the device to set.
        :raises ValueError: If the device index is invalid.
        """
        available_devices = self.get_available_audio_devices()
        for device in available_devices:
            if device.index == device_index:
                self.device_index = device.index
                self.config['audio']['device'] = device.safe_name
                self.write_config_file()
                return
        
        raise ValueError(
            f"Invalid device index: '{device_index}'.\n {self.get_available_audio_devices_str()}"
        )
    
    def try_set_audio_device_by_index(self, device_index: int | str) -> bool:
        """
        Try to set the audio device by index, without raising an exception.
        Falls back to previously selected device or default device, if the device index is invalid.
        
        :param device_index: The index of the device to set.
        :return: True if the device was set, False otherwise.
        """
        try:
            self.set_audio_device_by_index(int(device_index))
            return True
        except ValueError:
            pass
        
        if str(device_index) != "0":
            print(
                f"Unable to set device by index {device_index}. Trying previously selected {self.device_index}."
            )
            
            try:
                self.set_audio_device_by_index(self.device_index)
                return True
            except ValueError:
                pass
        
        if self.device_index != 0:
            print(
                f"Unable to set device by index {device_index}. Trying default (0)."
            )
            
            try:
                self.set_audio_device_by_index(0)
                return True
            except ValueError:
                pass
        
        return False
    
    def get_available_audio_devices(self) -> list[AudioDevice]:
        """
        Get a list of available audio devices.
        """
        return self.recorder.get_devices()
    
    def get_available_audio_devices_str(self) -> str:
        """
        Get a single-string representation (listing) of available audio devices.
        """
        res = "Available devices:\n"
        for device in self.get_available_audio_devices():
            res += f"  {device.index}. {device.simplified_name}\n"
        return res.rstrip()
    
    def get_available_audio_device_names(self) -> list[str]:
        """
        Get a list of available audio device names.
        """
        return [device.name for device in self.get_available_audio_devices()]
    
    def get_selected_audio_device_name(self) -> str:
        """
        Get the name of the selected audio device.
        """
        return self.recorder.get_device_name(self.device_index)
    
    def get_selected_audio_device_index(self) -> int:
        """
        Get the index of the selected audio device.
        """
        return self.device_index
    
    def print_selected_device(self) -> None:
        """
        Print the selected audio device.
        """
        print(
            f"Selected device: {self.get_selected_audio_device_index()}. {AudioDevice.simplify_name(self.get_selected_audio_device_name())}"
        )
    
    def get_humanized_duration(self, duration: float) -> str:
        """
        Get a humanized duration string.
        """
        return humanize.precisedelta(duration, format='%0.2f')
    
    def start_recording(self) -> None:
        """
        Start recording with the selected audio device.
        """
        self.recorder.start_recording(self.device_index)
    
    def is_recording(self) -> bool:
        """
        Check if recording is in progress.
        """
        return self.recorder.is_recording
    
    def stop_and_save_recording(self) -> float:
        """
        Stop recording and save the audio file.
        
        :return: The duration of the recording in seconds.
        """
        self.recorder.stop_recording()
        self.recorder.delete_audio()
        self.last_recording_duration = self.recorder.save_audio()
        return self.last_recording_duration
    
    def transcribe_recording(self, replace: bool = True) -> str:
        """
        Transcribes the last recording and returns the transcript.
        
        :param replace: If True, the result will be replaced using the replacements file.
        :return: The transcript.
        """
        if self.last_recording_duration < 1:
            return "Recording duration too short. Must be at least 1 second."
        transcript = self.transcriber.transcribe(self.audio_file_path)
        if replace:
            transcript = self.replace_text(transcript)
        return transcript
    
    def replace_text(self, text: str) -> str:
        """
        Replace the given text using the replacements file.
        """
        return self.replacer.replace(text)
    
    def copy_to_clipboard(self, text: str) -> None:
        """
        Copy the given text to the clipboard.
        """
        pyperclip.copy(text)
    
    def cleanup(self) -> None:
        """
        Cleanup. 
        Stop recording and delete the audio file.
        """
        self.recorder.stop_recording()
        self.recorder.delete_audio()
