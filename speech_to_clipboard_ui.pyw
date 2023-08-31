from settings import Settings
from core.speech_to_clipboard import SpeechToClipboard
from core.speech_to_clipboard_ui import SpeechToClipboardUI


def main():
    try:
        speech_to_clip = SpeechToClipboard(
            audio_file_path=Settings.AUDIO_FILE_PATH,
            config_file_path=Settings.CONFIG_FILE_PATH,
            replacemetns_file_path=Settings.REPLACEMENTS_FILE_PATH,
            openai_api_key_env_var=Settings.OPENAI_API_KEY_ENV_VAR,
        )
        SpeechToClipboardUI(
            win_title=Settings.APP_TITLE,
            icon_file_path=Settings.ICON_FILE_PATH,
            speech_to_clip=speech_to_clip,
        )
    except Exception as e: #pylint: disable=broad-except
        # create simple window with error message
        SpeechToClipboardUI.create_warning_dialog(
            "Error", str(e), Settings.ICON_FILE_PATH
        )


if __name__ == "__main__":
    main()
