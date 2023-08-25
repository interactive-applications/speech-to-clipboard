# Whisper Clip

Simple UI tool for recording from the microphone and transferring the audio to *OpenAI*'s *Whisper* Model via OpenAI's API for automatic **transcription**. Copies the transcription to the clipboard so it can be pasted into other applications.

# Installation

1. Clone the repository
1. Setup a virtual environment (highly recommended, especially when you want to build to `exe`). Use **Python 3.11** or higher
1. Install the requirements, with either:
    - `pip install -r requirements.in` - for requirements with the latest versions (recommended)
    - `pip install -r requirements.txt` - for pinned requirements
1. If you want to build to exe, also intall the dev requirements with
    - `pip install -r requirements-dev.in`
1. Set the environment variable `WHISPER_KEYBOARD_API_KEY` to your *OpenAI API Key*, e.g. in an `.env` file.<br>
    Find your API key in the [OpenAI Dashboard](https://platform.openai.com/account/api-keys). Ideally create a new one just for this app. While you're at it, always good to [set billing limits](https://platform.openai.com/account/billing/limits).<br>
    Alternatively, the API key can be set via the [config.ini](config.ini) file, under `[openai] api_key`.<br>
    **NOTE:** _The environment variable takes precedence over the config file_.
1. Run the application with `python whisper_clip.pyw`

# Usage

1. Select the correct microphone in the dropdown
1. Press **REC** to start recording
1. Press **Stop recording** to stop recording. The audio will then be sent to the OpenAI API for transcription and the result will be copied to the clipboard.

# AutoPyToExe

1. Install dev requirements with `pip install -r requirements-dev.in`
1. Run `auto-py-to-exe`
1. Load the configuration file `auto-py-to-exe-config.json` (**Settings** → **Configuration** → **Import Config From JSON File**)
1. Click **Convert .py to .exe**