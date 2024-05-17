import json
import os
from typing import List, Dict

import whisper
from dotenv import load_dotenv

from huggingsound import SpeechRecognitionModel
from docx import Document

from app.src.GlobalLogger import log_info


class Transcriber:

    def __init__(self):
        """
        This class is responsible for transcribing audio files. It uses the whisper or huggingface models for local
        transcription based on the config.
        """
        load_dotenv()
        self.model_source = self._get_model_source()
        self.model = self._get_model()
        self.audio = None

    def prepare_audio(self, audio_path):
        self.audio = whisper.load_audio(audio_path)

    def detect_language(self):
        audio_trimmed = whisper.pad_or_trim(self.audio)
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio_trimmed).to(self.model.device)
        # detect the spoken language
        _, probs = self.model.detect_language(mel)
        log_info(f"Detected language: {max(probs, key=probs.get)}")

    def transcribe(self, audio_paths, fp16=False):
        log_info(f'Transcribing audio files with {self.model_source}.')
        if self.model_source == 'whisper':
            if not self.audio:
                self.prepare_audio(audio_paths)
            self.detect_language()
            transcriptions = self.model.transcribe(self.audio, fp16=fp16)
        else:
            transcriptions = self.model.transcribe(audio_paths)
        log_info('Transcription done.')
        return self.get_texts(transcriptions)

    def _get_model_source(self):
        log_info('Get model source.')
        model_source = os.getenv("MODEL_SOURCE")
        if model_source not in ["whisper", "huggingface"]:
            raise ValueError("MODEL_SOURCE must be either 'whisper' or 'huggingface'")
        log_info(f'Model source: {model_source}')
        return model_source

    def _get_model(self):
        log_info('Get model.')
        if self.model_source == "whisper":
            model_path = os.path.join("app", "src", "whisper_model", "base.pt")
            if os.path.exists(model_path):
                log_info('Load local model.')
                return whisper.load_model(model_path)
            log_info('Load model from web.')
            return whisper.load_model('base')
        elif self.model_source == "huggingface":
            log_info('Load model from web.')
            return SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-english")

    def get_texts(self, transcriptions):
        log_info('Get texts from transcriptions.')
        if self.model_source == "whisper":
            return transcriptions["text"]
        elif self.model_source == "huggingface":
            return transcriptions


def save_list_to_file(filename: str, to_be_saved_list: List[str], save_as_docs=False):
    log_info(f'Save list to file: {filename}')
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if save_as_docs:
            doc = Document()

            for text in to_be_saved_list:
                doc.add_paragraph(text)

            doc.save(filename)
            return True
        else:
            with open(filename, 'w') as file:
                log_info('Saving to file.')
                for text in to_be_saved_list:
                    file.write(text)
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
    transcriber = Transcriber()

    # audiobooks = [file for file in os.listdir('audiobooks') if file.endswith('.mp3')]

    #
    # for audiobook in audiobooks:
    #     transcriptions = transcriber.transcribe(os.path.join('audiobooks', audiobook))
    #     save_list_to_file(os.path.join('../transcriptions', audiobook.replace('.mp3', '.txt')), transcriptions)

    book_title = 'Rainer_Sachse_personality_types_converted.mp3'
    audiobook = os.path.join('audiobooks', book_title)
    transcriptions = transcriber.transcribe(audiobook)
    print(transcriptions[:1000])
    save_list_to_file(os.path.join('transcriptions', book_title.replace('.mp3', '.txt')), transcriptions)
