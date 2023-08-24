import os
import openai
import pyaudio
import wave


# API_KEY = os.getenv("WHISPER_KEYBOARD_API_KEY")
# #print(API_KEY[-5:])

# openai.api_key = API_KEY 

# audio_file= open("./jfk.flac", "rb")
# transcript = openai.Audio.transcribe("whisper-1", audio_file)

#print(transcript)

# record from microphone

import wave
import sys

import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 #  if sys.platform == 'darwin' else 2
RATE = 44100
RECORD_SECONDS = 5

p =  pyaudio.PyAudio()
# list all available input devices
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev['maxInputChannels'] > 0:
        print(f"Device {i}: {dev['name']} (max channels: {dev['maxInputChannels']})")

with wave.open('./output.wav', 'wb') as wf:
    
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=1)

    print('Recording...')
    for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
        wf.writeframes(stream.read(CHUNK))
    print('Done')

    stream.close()
    p.terminate()
