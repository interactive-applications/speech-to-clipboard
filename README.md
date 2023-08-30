# Whisper Clip

Simple UI tool for **recording audio from a microphone, and automatically transcribing the recording** using *OpenAI*'s *Whisper* Model via OpenAI's API. Copies the transcription to the clipboard so it can be pasted quickly into other applications. Also supports configurable text replacements, similar to the voice recording feature on iOS, e.g. replacing the text "`new line`" with an actual new line, or "bullet point" with "`• `".

By [Claus Helfenschneider Interactive Applications](https://interactive-applications.com)

UI made with [CustomTKinter](https://github.com/TomSchimansky/CustomTkinter)

<img src="resources/screenshot_01.png" alt="Screenshot" width="400"/>

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

1. Select the microphone to record with in the dropdown
1. Press **REC** to start recording
1. Press **Stop recording** to stop recording. The audio will then be sent to the OpenAI API for transcription and the result will be copied to the clipboard.

# AutoPyToExe

1. Install dev requirements with `pip install -r requirements-dev.in`
1. Run `auto-py-to-exe -c auto-py-to-exe-config.json`
1. Load the configuration file `auto-py-to-exe-config.json` (**Settings** → **Configuration** → **Import Config From JSON File**)
1. Click **Convert .py to .exe**

# Text Replacer

A simple naive text replacement system is implemented, which, if enabled using the **Replacer** checkbox, replaces certain expressions, e.g:

| Expression | Replacement |
|--|--|
| `new line` | `\n` |
| `bullet point` | `• ` |
| `en dash` | `–` |
| … | … |

The replacements are defined (and can be configured/edited) in the [resources/replacements.json](resources/replacements.json) file, which should be rather self-explanatory.