import os
from datetime import datetime
from typing import List

import openai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from app.Summarizer import Summarizer
from app.Transcriber import Transcriber, save_list_to_file, save_dict_to_file

app = FastAPI()
APP_URI = '0.0.0.0'
APP_PORT = 5555


class UserInput(BaseModel):
    title: str
    description: str
    name: str
    email: str
    delimiters: List[str]
    file_path: str


@app.post("/transcribe_and_summarize")
async def transcribe_and_summarize(user_input: UserInput):
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    # set paths
    transcription_path = os.path.join('transcriptions', timestamp + user_input.title)
    book_summary_path = os.path.join(
        'book_summaries',
        timestamp + user_input.title)
    chapter_summary_path = os.path.join(
        'chapter_summaries',
        timestamp + user_input.title)
    costs_path = os.path.join('openai_costs', timestamp + user_input.title[:-4] + '.json')

    # transcribe file
    transcriber = Transcriber()

    transcriptions = transcriber.transcribe(user_input.file_path)
    save_list_to_file(transcription_path, transcriptions)

    # summarize
    summary_of_book, summaries_of_parts, tokens_used, text_length = Summarizer().summarize_book(
        transcription_path,
        user_input.delimiters,
        user_input.title)

    save_list_to_file(
        book_summary_path,
        [summary_of_book])
    save_list_to_file(
        chapter_summary_path,
        summaries_of_parts)

    print(f"Used up {tokens_used} tokens.\n"
          f"This is {tokens_used * 0.02 / 1000} $\n"
          f"This is {tokens_used * 0.02 / 1000 / text_length * 1000} $ per 1000 characters.")

    save_dict_to_file(
        costs_path,
        {'book_title': user_input.title[:-4],
         'text_length': text_length,
         'tokens_used': tokens_used,
         'costs': tokens_used * 0.02 / 1000,
         'costs_per_1000_characters': tokens_used * 0.02 / 1000 / text_length * 1000}
    )
    return {'transcription_path': transcription_path,
            'chapter_summary_path': chapter_summary_path,
            'book_summary_path': chapter_summary_path}


if __name__ == "__main__":
    for dir_name in ['transcriptions', 'book_summaries', 'chapter_summaries']:
        if dir_name not in os.listdir():
            os.mkdir(dir_name)

    uvicorn.run(app, host=APP_URI, port=APP_PORT)
