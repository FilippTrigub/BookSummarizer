import json
import os
from typing import List, Dict

import whisper
from dotenv import load_dotenv

from huggingsound import SpeechRecognitionModel
from docx import Document

from src.GlobalLogger import log_info


class Transcriber:

    def __init__(self):
        """
        This class is responsible for transcribing audio files. It uses the whisper or huggingface models for local
        transcription based on the config.
        """
        load_dotenv()
        self.model_source = self._get_model_source()
        self.model = self._get_model()

    def transcribe(self, audio_paths, fp16=False):
        if self.model_source == 'whisper':
            transcriptions = self.model.transcribe(audio_paths, fp16=fp16)
        else:
            transcriptions = self.model.transcribe(audio_paths)
        log_info('Transcription done.')
        return self.get_texts(transcriptions)

    def _get_model_source(self):
        model_source = os.getenv("MODEL_SOURCE")
        if model_source not in ["whisper", "huggingface"]:
            raise ValueError("MODEL_SOURCE must be either 'whisper' or 'huggingface'")
        return model_source

    def _get_model(self):
        if self.model_source == "whisper":
            model_path = os.path.join("src", "whisper_model", "base.pt")
            if os.path.exists(model_path):
                log_info('Load local model.')
                return whisper.load_model(model_path)
            log_info('Load model from web.')
            return whisper.load_model('base')
        elif self.model_source == "huggingface":
            log_info('Load model from web.')
            return SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-english")

    def get_texts(self, transcriptions):
        if self.model_source == "whisper":
            return transcriptions["text"]
        elif self.model_source == "huggingface":
            return transcriptions


def save_list_to_file(filename: str, to_be_saved_list: List[str]):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        doc = Document()

        for text in to_be_saved_list:
            doc.add_paragraph(text)

        doc.save(filename)
        return True
    except Exception as e:
        print(f"An error occurred while saving the Word file: {str(e)}")
        return False
    # log_info(f'Save list to file: {filename}')
    # try:
    #     log_info('Making directory.')
    #     os.makedirs(os.path.dirname(filename), exist_ok=True)
    #     with open(filename, 'w') as file:
    #         log_info('Saving to file.')
    #         for text in to_be_saved_list:
    #             file.write(text)
    #     return True
    # except Exception as e:
    #     log_info(f"An error occurred while saving the file: {str(e)}")
    #     return False
    #


def save_dict_to_file(filename: str, dictionary: Dict[str, str]):
    log_info(f'Save dict to file: {filename}')
    try:
        log_info('Making directory.')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as file:
            log_info('Saving to file.')
            json.dump(dictionary, file)
    except Exception as e:
        log_info(f"Failed to save dictionary: {e}")


if __name__ == '__main__':

    audiobooks = [file for file in os.listdir('audiobooks') if file.endswith('.mp3')]

    transcriber = Transcriber()

    for audiobook in audiobooks:
        transcriptions = transcriber.transcribe(os.path.join('audiobooks', audiobook))
        save_list_to_file(os.path.join('../transcriptions', audiobook.replace('.mp3', '.txt')), transcriptions)
