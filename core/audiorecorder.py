import os
import sys
import codecs
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from pydub.silence import detect_leading_silence


class AudioDevice:
    
    def __init__(self, index: int, name: str, max_input_channels: int):
        """
        :param index: The index of the audio device.
        :param name: The name of the audio device.
        :param max_input_channels: The number of input channels the audio device supports.
        """
        self.index = index
        self.name = name
        self.max_input_channels = max_input_channels
    
    @property
    def simplified_name(self) -> str:
        """
        Get the simplified name of the audio device for UI or CLI display.
        """
        return AudioDevice.simplify_name(self.safe_name)
    
    @property
    def safe_name(self) -> str:
        """
        Get the safe name of the audio device for use in a config file.
        
        :return: The safe name of the audio device.
        """
        return AudioDevice.make_name_safe(self.name)
    
    @staticmethod
    def simplify_name(name: str) -> str:
        """
        Simplify the given string for UI or CLI display.
        
        :param name: The name of the audio device.
        :return: The simplified name of the audio device.
        """
        res = name.replace('\n', ' ').replace('\r', ' ')
        if len(res) > 65:
            return res[:65] + "..."
        return res
    
    @staticmethod
    def make_name_safe(name: str) -> str:
        """
        Convert the given string safe for use in a config file.
        
        :param name: The string to convert.
        :return: The converted string.
        """
        return codecs.encode(name, 'unicode_escape').decode('utf-8')
    
    def name_equals(self, other: str) -> bool:
        """
        Check if the name of the audio device equals the given string.
        
        :param other: The string to compare to.
        :return: True if the name of the audio device equals the given string, False otherwise.
        """
        if self.safe_name == other or self.simplified_name == other or self.safe_name == AudioDevice.make_name_safe(
                other) or self.simplified_name == AudioDevice.simplify_name(
                    other):
            return True
        return False


class AudioRecorder:
    
    def __init__(self, wav_file_path: str = "./audio/output.wav") -> None:
        """
        :param wav_file_path: The path to the wav file to save the recorded audio to.
        """
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
        """
        Trim silence from the start of the given audio file.
        """
        return audio_file[detect_leading_silence(audio_file):]
    
    @staticmethod
    def trim_trailing_silence(audio_file) -> AudioSegment:
        """
        Trim silence from the end of the given audio file.
        """
        return AudioRecorder.trim_leading_silence(audio_file.reverse()
                                                 ).reverse()
    
    @staticmethod
    def strip_silence(audio_file) -> AudioSegment:
        """
        Trim silence from the start and end of the given audio file.
        """
        # from: https://stackoverflow.com/a/69331596
        return AudioRecorder.trim_trailing_silence(
            AudioRecorder.trim_leading_silence(audio_file)
        )
    
    def get_devices(self) -> list[AudioDevice]:
        """
        Get a list of available audio devices.
        """
        devices = sd.query_devices()
        # filter out devices that do not support recording
        devices = [
            device for device in devices if device['max_input_channels'] > 0
        ]
        # convert to AudioDevice objects
        devices = [
            AudioDevice(
                device['index'], device['name'], device['max_input_channels']
            ) for device in devices
        ]
        return devices
    
    def get_device(self, device_index: int) -> dict[str]:
        """
        Get the audio device with the given index.
        """
        for device in self.devices:
            if device.index == device_index:
                return device
        return None
    
    def get_device_name(self, device_index: int) -> str:
        """
        Get the name of the audio device with the given index.
        """
        device = self.get_device(device_index)
        if device is not None:
            return device.name
        return f"invalid device index: {device_index}"
    
    def start_recording(self, device_index: int) -> None:
        """
        Start recording with the given audio device.
        """
        self.device_index = device_index
        self.is_recording = True
        self.frames = []
        sd.default.device = device_index
        sd.default.channels = self.channels
        sd.default.samplerate = self.rate
        sd.default.dtype = 'int16'
        sd.default.blocksize = 1024
        sd.default.latency = 'low'
        self.stream = sd.InputStream(callback=self._callback)
        self.stream.start()
    
    def stop_recording(self) -> None:
        """
        Stop recording.
        """
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def _callback(self, indata, frames, time, status): #pylint: disable=unused-argument
        if status:
            print(status, file=sys.stderr)
        self.frames.append(indata.copy())
    
    def delete_audio(self) -> None:
        """
        Delete the recorded audio file.
        """
        if os.path.exists(self.wav_file):
            os.remove(self.wav_file)
        alt_file = self.get_alt_file()
        if os.path.exists(alt_file):
            os.remove(alt_file)
    
    def get_alt_file(self, file_format: str = "mp3") -> str:
        """
        Get the path to the mp3 file.
        """
        basename = os.path.splitext(self.wav_file)[0]
        return f"{basename}.{file_format}"
    
    def save_audio(self) -> float:
        """
        Save the recorded audio file.
        """
        # create the path if it does not exist. the path is relative to the current working directory
        os.makedirs(os.path.dirname(self.wav_file), exist_ok=True)
        
        data = [item for sublist in self.frames for item in sublist]
        sf.write(self.wav_file, data, self.rate)
        
        # load the audio file using pydub
        audio = AudioSegment.from_wav(self.wav_file)
        
        # trim silence from start and end
        
        trimmed_audio: AudioSegment = self.strip_silence(audio)
        
        # get the length of the resulting file in seconds
        duration = trimmed_audio.duration_seconds
        
        # save the trimmed audio file
        try:
            alt_format = "mp3"
            # save the trimmed audio file as mp3
            alt_path = self.get_alt_file(alt_format)
            
            trimmed_audio.export(
                alt_path,
                format=alt_format,
                bitrate="64k",
                parameters=["-ac", "1", "-ar", "16000"]
            )
            
            # delete the original WAV file
            if os.path.exists(self.wav_file):
                os.remove(self.wav_file)
        
        except Exception: #pylint: disable=broad-except
            # save as WAV if mp3 fails
            trimmed_audio.export(self.wav_file, format='wav')
        
        return duration
