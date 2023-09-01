import os
import openai
from openai.openai_object import OpenAIObject


class Transcriber:
    
    def __init__(self, openai_api_key: str = "") -> None:
        """
        Initialize the Transcriber class.
        
        :param openai_api_key: OpenAI API key
        """
        openai.api_key = openai_api_key
    
    def transcribe(
        self,
        wav_file_path: str = "./audio/output.wav",
        delete_file_on_success: bool = True
    ) -> str:
        """
        Trnascribe the given wav file.
        
        :param wav_file_path: The path to the wav file to transcribe.
        :return: The transcription of the wav file.
        """
        
        # strip the extension from the file path and look for any files with that name, but with a different extension
        file_path = wav_file_path
        base_path = os.path.splitext(wav_file_path)[0]
        base_dir = os.path.dirname(base_path)
        basename = os.path.basename(base_path)
        
        for file in os.listdir(base_dir):
            if os.path.splitext(file)[0] == basename:
                file_path = os.path.join(base_dir, file)
                break
        
        try:
            with open(file_path, "rb") as audio_file:
                transcript: OpenAIObject = openai.Audio.transcribe(
                    "whisper-1", audio_file
                )
                transcript = transcript['text']
            
            if delete_file_on_success:
                os.remove(file_path)
            
            return transcript
        except openai.error.InvalidRequestError as e:
            return "Error: " + str(e)
        except Exception as e: #pylint: disable=broad-except
            return "Error: " + str(e)
