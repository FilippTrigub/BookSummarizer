import os
import shutil
import threading
from datetime import datetime
from typing import List

import openai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from Summarizer import Summarizer
from Transcriber import Transcriber, save_list_to_file, save_dict_to_file
from send_mail import send_mail

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
APP_URI = '0.0.0.0'
APP_PORT = 8081


@app.get("/")
async def root():
    return {'hello': 'world'}


@app.get("/check")
async def check():
    return {'status': 200}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with open(file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        print('File uploaded.')
    return {"status": 200}


class UserInput(BaseModel):
    title: str
    description: str
    name: str
    email: str
    delimiters: List[str]
    file_name: str


@app.post("/run_summarization")
async def run_summarization(user_input: UserInput):
    # Start a new thread that runs the summarization process
    print('Run summarization in separate thread.')
    threading.Thread(target=transcribe_and_summarize, args=(user_input,)).start()

    # Immediately return a status of 200
    print('Return success status.')
    return {"status": 200}


@app.post("/transcribe_and_summarize")
def transcribe_and_summarize(user_input: UserInput):
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '_'

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
    print('Transcribe audio file.')
    transcriber = Transcriber()

    transcriptions = transcriber.transcribe(user_input.file_name, fp16=False)
    save_list_to_file(transcription_path, transcriptions)

    # summarize
    print('Summarize transcribed text.')
    summary_of_book, summaries_of_parts, tokens_used, text_length = Summarizer().summarize_book(
        transcription_path,
        user_input.delimiters,
        user_input.title)

    print('Save results.')
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

    send_mail(recipient_email=user_input.email,
              subject='Your Summary is here!',
              attachment_paths=[book_summary_path, chapter_summary_path],
              book_title=user_input.title)


if __name__ == "__main__":
    for dir_name in ['transcriptions', 'book_summaries', 'chapter_summaries']:
        if dir_name not in os.listdir():
            os.mkdir(dir_name)

    uvicorn.run(app, host=APP_URI, port=APP_PORT)

    # user_input = UserInput
    # user_input.title = 'test'
    # user_input.email = 'filipp.trigub@gmail.com'
    # user_input.file_name = 'test.mp3'
    # user_input.delimiters = ['test']
    # user_input.description = ' test'
    # user_input.name = 'test'
    # transcribe_and_summarize(user_input)
