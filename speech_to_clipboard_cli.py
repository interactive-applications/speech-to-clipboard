import argparse
from settings import Settings
from core.speech_to_clipboard import SpeechToClipboard


def verbose_interactive_mode(
    s2c: SpeechToClipboard, loop: bool = True, replace: bool = True
):
    while True:
        s2c.print_selected_device()
        user_input = input(
            "\n> Select action:\n  s = select audio device\n  q = quit\n  r/any = start audio recording: \n"
        )
        if user_input == "q":
            s2c.cleanup()
            break
        if user_input == "s":
            print(s2c.get_available_audio_devices_str())
            s2c.print_selected_device()
            device_index = input("> Select device (index): ")
            s2c.try_set_audio_device_by_index(device_index)
        else:
            s2c.start_recording()
            print("Recording...")
            user_input = input(
                "> Press ENTER to stop recording and transcribe, x or q to cancel: "
            )
            if user_input in ["x", "q"]:
                print("Recording canceled.")
                continue
            duration = s2c.stop_and_save_recording()
            duration_str = s2c.get_humanized_duration(duration)
            print(f"Recording stopped. Duration: {duration_str}")
            transcript = s2c.transcribe_recording(replace=replace)
            print("Transcript:\n")
            print(transcript)
            print("")
            s2c.copy_to_clipboard(transcript)
            print("Copied to clipboard.")
        
        if not loop:
            break


def silent_mode(
    s2c: SpeechToClipboard, loop: bool = True, replace: bool = True
):
    while True:
        s2c.start_recording()
        user_input = input("")
        if user_input in ["x"]:
            continue
        if user_input in ["q"]:
            s2c.cleanup()
            break
        duration = s2c.stop_and_save_recording()
        s2c.get_humanized_duration(duration)
        transcript = s2c.transcribe_recording(replace=replace)
        print(transcript)
        s2c.copy_to_clipboard(transcript)
        
        if not loop:
            break


def main():
    parser = argparse.ArgumentParser(description=Settings.APP_TITLE)
    # Define an argument
    parser.add_argument(
        '-i',
        '--interactive',
        action="store_true",
        help=
        "Interactive mode. When on, the program will keep prompting for new recordings",
        default=True
    )
    parser.add_argument(
        '-s',
        '--silent',
        action="store_true",
        help=
        "Silent mode. In silent mode, hit 'ENTER' to stop recording and transcribe, enter 'x'+ENTER to cancel the recording, 'q'+ENTER to quit."
    )
    parser.add_argument(
        '-a',
        '--select_audio_device',
        action="store_true",
        help="Select audio device"
    )
    parser.add_argument(
        '-n',
        '--noreplace',
        action="store_true",
        help="Omit replacing text using the replacements file",
        default=False
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    s2c = SpeechToClipboard(
        config_file_path=Settings.CONFIG_FILE_PATH,
        replacemetns_file_path=Settings.REPLACEMENTS_FILE_PATH,
        audio_file_path=Settings.AUDIO_FILE_PATH,
        openai_api_key_env_var=Settings.OPENAI_API_KEY_ENV_VAR
    )
    
    if args.select_audio_device:
        print(s2c.get_available_audio_devices_str())
        s2c.print_selected_device()
        device_index = input("> Select device (index): ")
        s2c.try_set_audio_device_by_index(device_index)
        s2c.print_selected_device()
    elif args.silent:
        silent_mode(s2c, loop=args.interactive, replace=not args.noreplace)
    else:
        verbose_interactive_mode(
            s2c, loop=args.interactive, replace=not args.noreplace
        )


if __name__ == "__main__":
    main()
