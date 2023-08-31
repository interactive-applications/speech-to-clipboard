from settings import Settings
from core.speech_to_clipboard import SpeechToClipboard


speech_to_clip = SpeechToClipboard(
    audio_file_path=Settings.AUDIO_FILE_PATH,
    config_file_path=Settings.CONFIG_FILE_PATH,
    replacemetns_file_path=Settings.REPLACEMENTS_FILE_PATH,
    openai_api_key_env_var=Settings.OPENAI_API_KEY_ENV_VAR,
)

speech_to_clip.start_recording()
print("Recording...")
input("Press Enter to stop recording...")
speech_to_clip.stop_and_save_recording()
transcription = speech_to_clip.transcribe_recording()
print(transcription)
