import os
import shutil
import threading
import openai
import uvicorn

from datetime import datetime
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.GlobalLogger import log_info
from src.Summarizer import Summarizer
from src.Transcriber import Transcriber, save_list_to_file, save_dict_to_file
from src.send_mail import send_mail

app = FastAPI(title='Audio Summarizer', debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
HOST_IFACE = '0.0.0.0'
APP_PORT = 8081

for dir_name in ['transcriptions', 'book_summaries', 'chapter_summaries']:
    if dir_name not in os.listdir():
        os.mkdir(dir_name)


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
        log_info('File uploaded.')
    return {"status": 200}


class UserInput(BaseModel):
    title: str
    description: str
    name: str
    email: str
    delimiters: List[str]
    file_name: str
    model_key: str
    budget: str


@app.post("/run_summarization")
async def run_summarization(user_input: UserInput):
    # Start a new thread that runs the summarization process
    log_info('Run summarization in separate thread.')
    threading.Thread(target=transcribe_and_summarize, args=(user_input,)).start()

    # Immediately return a status of 200
    log_info('Return success status.')
    return {"status": 200}


def save_and_send(book_summary_path, summary_of_book, chapter_summary_path, summaries_of_parts, tokens_used,
                  text_length, costs_path, user_input):
    log_info('Save results.')
    save_list_to_file(
        book_summary_path,
        [summary_of_book])
    save_list_to_file(
        chapter_summary_path,
        summaries_of_parts)

    log_info(f"Used up {tokens_used} tokens.\n"
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


@app.post("/transcribe_and_summarize")
def transcribe_and_summarize(user_input: UserInput):
    transcription_path, book_summary_path, chapter_summary_path, costs_path = set_up_params(user_input)

    # transcribe file
    log_info('Transcribe audio file.')
    transcriber = Transcriber()

    transcriptions = transcriber.transcribe(user_input.file_name, fp16=False)
    save_list_to_file(transcription_path, transcriptions)

    # summarize
    log_info('Summarize transcribed text.')
    summary_of_book, summaries_of_parts, tokens_used, text_length = Summarizer().summarize_book(
        text=transcriptions,
        delimiters = user_input.delimiters,
        book_title=user_input.title,
        user_budget=user_input.budget,
        load_text_from_file=False)

    save_and_send(book_summary_path, summary_of_book, chapter_summary_path, summaries_of_parts, tokens_used,
                  text_length, costs_path, user_input)


@app.post("/transcribe_and_summarize_first_part")
def transcribe_and_summarize_first_part(user_input: UserInput):
    transcription_path, book_summary_path, chapter_summary_path, costs_path = set_up_params(user_input)

    # transcribe file
    log_info('Transcribe audio file.')
    transcriber = Transcriber()

    transcriptions = transcriber.transcribe(user_input.file_name, fp16=False)
    parts = Summarizer().prepare_parts(transcriptions, user_input.delimiters)

    save_list_to_file(transcription_path, parts)

    # summarize
    log_info('Summarize first part of the transcribed text.')
    summary_of_book, summaries_of_parts, tokens_used, text_length = Summarizer().summarize_book(
        parts[0],
        user_input.delimiters,
        user_input.title,
        load_text_from_file=False)

    save_and_send(book_summary_path, summary_of_book, chapter_summary_path, summaries_of_parts, tokens_used,
                  text_length, costs_path, user_input)


def set_up_params(user_input: UserInput):
    load_dotenv()
    openai.api_key = user_input.model_key

    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '_'

    # set paths
    transcription_path = os.path.join(
        'transcriptions',
        timestamp + user_input.title + '.txt')
    book_summary_path = os.path.join(
        'book_summaries',
        timestamp + user_input.title + '.txt')
    chapter_summary_path = os.path.join(
        'chapter_summaries',
        timestamp + user_input.title + '.txt')
    costs_path = os.path.join(
        'openai_costs',
        timestamp + user_input.title[:-4] + '.json')

    return transcription_path, book_summary_path, chapter_summary_path, costs_path


if __name__ == "__main__":
    log_info('Start App')
    uvicorn.run(app, host=HOST_IFACE, port=APP_PORT)

    # user_input = UserInput
    # user_input.title = 'test'
    # user_input.email = 'filipp.trigub@gmail.com'
    # user_input.file_name = 'test.mp3'
    # user_input.delimiters = ['test']
    # user_input.description = ' test'
    # user_input.name = 'test'
    # transcribe_and_summarize(user_input)
