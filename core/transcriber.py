import openai
from openai.openai_object import OpenAIObject


class Transcriber:
    
    def __init__(self, openai_api_key: str = "") -> None:
        """
        Initialize the Transcriber class.
        
        :param openai_api_key: OpenAI API key
        """
        openai.api_key = openai_api_key
    
    def transcribe(self, wav_file_path: str = "./audio/output.wav") -> str:
        """
        Trnascribe the given wav file.
        
        :param wav_file_path: The path to the wav file to transcribe.
        :return: The transcription of the wav file.
        """
        with open(wav_file_path, "rb") as audio_file:
            try:
                transcript: OpenAIObject = openai.Audio.transcribe(
                    "whisper-1", audio_file
                )
                return transcript['text']
            except openai.error.InvalidRequestError as e:
                return "Error: " + str(e)
            except Exception as e: #pylint: disable=broad-except
                return "Error: " + str(e)
