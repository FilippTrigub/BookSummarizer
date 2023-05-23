import os

import whisper
from dotenv import load_dotenv

from huggingsound import SpeechRecognitionModel


class Transcriber:

    def __init__(self):
        """
        This class is responsible for transcribing audio files. It uses the whisper or huggingface models for local
        transcription based on the config.
        """
        load_dotenv()
        self.model_source = self._get_model_source()
        self.model = self._get_model()

    def transcribe(self, audio_paths):
        transcriptions = self.model.transcribe(audio_paths)
        return self.get_texts(transcriptions)

    def _get_model_source(self):
        model_source = os.getenv("MODEL_SOURCE")
        if model_source not in ["whisper", "huggingface"]:
            raise ValueError("MODEL_SOURCE must be either 'whisper' or 'huggingface'")
        return model_source

    def _get_model(self):
        if self.model_source == "whisper":
            return whisper.load_model("base")
        elif self.model_source == "huggingface":
            return SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-english")

    def get_texts(self, transcriptions):
        if self.model_source == "whisper":
            return transcriptions["text"]
        elif self.model_source == "huggingface":
            return transcriptions


def save_text_to_file(filename, transcriptions):
    with open(filename, 'w') as file:
        for text in transcriptions:
            file.write(text)


if __name__ == '__main__':

    audiobooks = [file for file in os.listdir('audiobooks') if file.endswith('.mp3')]

    transcriber = Transcriber()

    for audiobook in audiobooks:
        transcriptions = transcriber.transcribe(os.path.join('audiobooks', audiobook))
        save_text_to_file(os.path.join('transcriptions', audiobook.replace('.mp3', '.txt')), transcriptions)
