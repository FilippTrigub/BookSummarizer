import copy
import os
import re
import time
from datetime import datetime
from typing import List, Tuple

import tiktoken
import openai
from dotenv import load_dotenv
from urllib3.exceptions import ReadTimeoutError

from app.src.GlobalLogger import log_info
from app.src.Transcriber import save_list_to_file, save_dict_to_file


class Summarizer:
    TOKENS_USED = 0

    DEFAULT_LOOP_THRESHOLD_PER_100000_CHARS = None
    DEFAULT_TIMEOUT_IN_MIN_PER_100000_CHARS = None
    MODEL_NAME = None
    MAX_INPUT_TOKENS = 14000

    TOKEN_THRESHOLD = None

    def __init__(self):
        self.MODEL_NAME = os.getenv('GENERATOR_MODEL')
        self.MODEL_TEMPERATURE = 0.2
        self.MAX_OUTPUT_TOKENS = 1000
        self.book_title = None
        self.TOKEN_THRESHOLD = float(os.getenv('CASH_THRESHOLD')) * 1000 / 0.02
        self.DEFAULT_LOOP_THRESHOLD_PER_100000_CHARS = int(os.getenv('DEFAULT_LOOP_THRESHOLD_PER_100000_CHARS'))
        self.DEFAULT_TIMEOUT_IN_MIN_PER_100000_CHARS = int(os.getenv('DEFAULT_TIMEOUT_IN_MIN_PER_100000_CHARS'))

    def summarize_book(self, text: str, delimiters: List[str], book_title: str, load_text_from_file: bool = False,
                       filename: str = '', user_budget: str = None):
        self.book_title = book_title
        self.TOKEN_THRESHOLD = float(user_budget) * 1000 / 0.02 if user_budget else self.TOKEN_THRESHOLD

        # prepare parts
        log_info("Prepare parts")
        if load_text_from_file:
            log_info('Load text from file')
            text = self._get_text(filename)
        parts = self.prepare_parts(text, delimiters)

        log_info("Summarizing parts")
        summaries_of_parts = self.summarize_parts(parts)

        log_info("Summarizing book")
        summary_of_book = self.summarize_summaries_of_parts(copy.deepcopy(summaries_of_parts), len(text))

        log_info("Summarizing book finished. Formatting summary")
        summary_of_book, summaries_of_parts = self.format_summaries(summary_of_book, summaries_of_parts)

        return summary_of_book, summaries_of_parts, self.TOKENS_USED, len(text)

    def summarize_summaries_of_parts(self, summaries_of_parts: List[str], len_text: int) -> str:
        log_info("Summarizing summaries of parts")
        # Summarize summaries of parts initially
        summary_of_book = self.summarize_concatenated_summaries(summaries_of_parts, True)
        # Loop recursively until only a short summary is left
        summary_of_book = self._summarize_recursively(summary_of_book, len_text)

        return summary_of_book

    def summarize_concatenated_summaries(self, chunks: List[str], summarize_summaries: bool = False) -> str:
        summary_of_part = ''
        for chunk in chunks:
            summary_of_part = summary_of_part + self._summarize_chunk(chunk, summarize_summaries) + '\n'
        return summary_of_part

    def prepare_parts(self, text: str, delimiters: List[str]):
        parts = self._split_in_parts(text, delimiters)
        parts = self._clean_parts(parts)
        return parts

    def summarize_parts(self, parts: List[str]) -> List[str]:
        return self._summarize_parts(parts)

    def _summarize_parts(self, parts: List[str]) -> List[str]:
        summaries_of_parts = []
        for part in parts:
            log_info(f'Summarizing part {parts.index(part) + 1} of {len(parts)}')
            summaries_of_parts.append(self.summarize_part(part))
        return summaries_of_parts

    def summarize_part(self, part: str) -> str:
        if len(self._split_in_chunks(part)) == 1:
            # Summarize summaries of parts initially
            summary_of_part = self._summarize_chunk(part, False)
        else:
            # Loop recursively until only a short summary is left
            summary_of_part = self._summarize_recursively(part, len(part))
        return summary_of_part

    def _summarize_recursively(self, summary: str, len_text: int) -> str:
        # Prepare while loop:
        # Split in chunks, loop only of summary longer than 1 chunk
        chunks = self.split_into_chunks(summary)
        # Set timeout and loop threshold
        timeout, loop_threshold = self._set_loop_threshold_and_timeout(len_text)
        while (len(chunks) > 1 or summary.count('Summary') > 1) \
                and loop_threshold > 0 \
                and time.time() < timeout \
                and self.TOKENS_USED < self.TOKEN_THRESHOLD:
            log_info(f"Running recursive summarization. "
                     f"Loop {loop_threshold}/{self.DEFAULT_LOOP_THRESHOLD_PER_100000_CHARS}.")
            # with iterations, chunks should get smaller so that list of summaries gets smaller
            # until only 1 element remains.
            summary = self.summarize_concatenated_summaries(chunks, True)
            chunks = self.split_into_chunks(summary)

            loop_threshold -= 1
            if loop_threshold == 0 or time.time() > timeout and os.getenv('DEV'):
                reset = input('Reset parameters and continue? (y/n)')
                if reset == 'y':
                    timeout, loop_threshold = self._set_loop_threshold_and_timeout(len_text)

            if self.TOKENS_USED > self.TOKEN_THRESHOLD:
                log_info(f'Used up {self.TOKENS_USED}.')
                if os.getenv('DEV'):
                    reset = input('Double threshold? (y/n)')
                    if reset == 'y':
                        self.TOKEN_THRESHOLD *= 2

        if len(chunks) > 1:
            log_info('Summarization did not converge.')
            if loop_threshold == 0:
                log_info('Loop threshold exceeded.')
                summary = 'Summarization unfinished, because loop threshold was exceeded.\n\n' + summary
            elif time.time() > timeout:
                log_info('Timeout reached.')
                summary = 'Summarization unfinished, because timeout was reached.\n\n' + summary
            elif self.TOKENS_USED > self.TOKEN_THRESHOLD:
                log_info(f'Used up {self.TOKENS_USED}.')
                summary = 'Summarization unfinished, because token threshold was reached.\n\n' + summary

        return summary

    def _summarize_chunk(self, chunk: str, summarize_summaries: bool = False) -> str:
        if summarize_summaries:
            prompt = f"""
                You are a Summarizer AI. 
                You will be given a list of summaries of parts of the book {self.book_title}. 
                No matter the language of the book, write a summary in English.
                Your task is to merge these summaries.
                You should use 20 bullet points.
                Summarize according to the following four points.
                - What are the main points derived by the author?
                - What are actionable recommendations provided by the author?
                - What are caveats the author highlights?
                Follow the output format under any circumstances.                  

                OUTPUT FORMAT: \n\n
                SUMMARY: \n\n
                Main Points:\n
                1: xxx.\n 
                2: xxx.\n 
                ...\n  
                N: xxx.\n\n   
                Recommendations:\n
                1: xxx.\n 
                2: xxx.\n 
                ...\n  
                N: xxx.\n\n   
                Caveats:\n
                1: xxx.\n 
                2: xxx.\n 
                ...\n  
                N: xxx.\n\n   

                Be sure to use statements as concise and precise.
                Base all your statements directly on the text. 
                Review the answer to make sure it fits the format. 
                Provide 1 complete summary of all previously made summaries.                

                INPUT TEXT: \n\n
                {chunk}
            """

        else:
            prompt = f"""
                You are a Summarizer AI. 
                You will be given a text, which is part of the book {self.book_title}. 
                Your task is to summarize the text in 10 points.
                Summarize according to the following four points.
                Summarize according to the following four points.
                - What are the main points derived by the author?
                - What are actionable recommendations provided by the author?
                - What are caveats the author highlights?
                Follow the output format under any circumstances.                  

                OUTPUT FORMAT: \n\n
                SUMMARY: \n\n
                Main Points:\n
                1: xxx.\n 
                2: xxx.\n 
                ...\n  
                N: xxx.\n\n   
                Recommendations:\n
                1: xxx.\n 
                2: xxx.\n 
                ...\n  
                N: xxx.\n\n   
                Caveats:\n
                1: xxx.\n 
                2: xxx.\n 
                ...\n  
                N: xxx.\n\n   

                Be sure to use statements as concise and precise.
                Base all your statements directly on the text. 
                Review the answer to make sure it fits the format.               

                INPUT TEXT: \n
            """

        summary = self.generate_completion(prompt, chunk)
        self.TOKENS_USED += self._num_tokens_from_string(prompt)
        return summary

    def _set_loop_threshold_and_timeout(self, len_text: int) -> Tuple[float, int]:
        timeout = time.time() + 60 * self.DEFAULT_TIMEOUT_IN_MIN_PER_100000_CHARS * len_text / 100000
        loop_threshold = max(int(self.DEFAULT_LOOP_THRESHOLD_PER_100000_CHARS * len_text / 100000), 1)
        return timeout, loop_threshold

    @staticmethod
    def _get_text(filename: str) -> str:
        for encoding in ['utf8', 'ISO-8859-1']:
            try:
                with open(filename, 'r', encoding=encoding) as file:
                    text = file.read()
            except UnicodeDecodeError:
                continue
        if not text:
            raise ValueError('No text found in file.')

        return text

    @staticmethod
    def _split_in_parts(text: str, delimiters: List[str]) -> List[str]:
        def _split_text_disregarding_case(lowercase_delimiter: str, lowercase_text: str, text: str):
            delimiter_index = lowercase_text.index(lowercase_delimiter)
            first_part = text[:delimiter_index].strip()
            second_part = text[delimiter_index + len(lowercase_delimiter):]
            if second_part[0] == '.':
                second_part = second_part[1:].strip()
            return first_part, second_part

        lowercase_text = text.lower()
        lowercase_delimiters = [delimiter.lower() for delimiter in delimiters]
        if not isinstance(lowercase_text, str):
            raise ValueError("Text must be a string.")
        if not isinstance(lowercase_delimiters, list):
            raise ValueError("Delimiters must be a list.")
        for lowercase_delimiter in lowercase_delimiters:
            if not isinstance(lowercase_delimiter, str):
                raise ValueError("All delimiters must be strings.")
            if lowercase_delimiter not in lowercase_text:
                raise ValueError(f"Delimiter '{lowercase_delimiter}' not found in text.")
            if text.count(lowercase_delimiter) > 1:
                raise ValueError(f"Delimiter {lowercase_delimiter} is not unique.")

        if len(delimiters) == 1:
            return [part for part in
                    _split_text_disregarding_case(lowercase_delimiters[0], lowercase_text, text) if part]
        else:
            parts = []
            unsegmented_text = text
            lowercase_unsegmented_text = unsegmented_text.lower()
            for lowercase_delimiter in lowercase_delimiters:
                split_text = _split_text_disregarding_case(
                    lowercase_delimiter, lowercase_unsegmented_text, unsegmented_text)
                # add the first part. As unsegmented text gets updated every loop, this should be the desired cutout
                parts.append(split_text[0])
                # set the rest of the text as unsegmented text for the next loop
                unsegmented_text = split_text[1]
                lowercase_unsegmented_text = unsegmented_text.lower()

            # add final part
            parts.append(unsegmented_text)

            return [part.strip() for part in parts if part]

    @staticmethod
    def _clean_parts(parts: List[str]) -> List[str]:
        # todo implement
        return parts

    def _num_tokens_from_string(self, string: str, model_name: str = None) -> int:
        """Returns the number of tokens in a text string."""
        model_name = self.MODEL_NAME if not model_name else model_name
        encoding = tiktoken.encoding_for_model(model_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def split_into_chunks(self, text: str) -> List[str]:
        sentences = re.split('(?<=[.!?]) +', text)
        chunks = []
        chunk = ""
        for sentence in sentences:
            if self._num_tokens_from_string(chunk + sentence) <= self.MAX_INPUT_TOKENS:
                chunk += sentence + " "
            else:
                chunks.append(chunk)
                chunk = sentence + " "
        if chunk:
            chunks.append(chunk)
        return chunks

    def _split_in_chunks(self, part: str) -> List[str]:
        if self._num_tokens_from_string(part) < self.MAX_INPUT_TOKENS:
            return [part]
        else:
            return self.split_into_chunks(part)

    def generate_completion(self, prompt: str, chunk: str):
        attempts_left = 2
        response = None
        while attempts_left >= 0 and not response:
            try:
                response = openai.ChatCompletion.create(
                    model=self.MODEL_NAME,
                    temperature=self.MODEL_TEMPERATURE,
                    max_tokens=self.MAX_OUTPUT_TOKENS,
                    messages=[
                        {"role": "system",
                         "content": prompt},
                        {"role": "user",
                         "content": chunk}
                    ]
                )
            except ReadTimeoutError:
                if attempts_left > 1:
                    attempts_left -= 1
                else:
                    raise ReadTimeoutError

        return response.choices[0].message['content'].strip()

    def format_summaries(self, summary_of_book, summaries_of_parts):
        summary_of_book = f'Summary of {self.book_title}:\n\n' + summary_of_book
        summaries_of_parts = [f'\n\nSummary of Part {i + 1}:\n\n' + summary for i, summary in
                              enumerate(summaries_of_parts)]
        return summary_of_book, summaries_of_parts


if __name__ == '__main__':
    load_dotenv()
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    book_file_name = 'Rainer_Sachse_personality_types_converted.txt'
    # delimiters = ['Part \d+\. ']

    # book_file_name = 'test.txt'
    delimiters = [
        'Kapitel 1',
        'Kapitel 2',
        'Kapitel 3',
        'Kapitel 4',
        'Kapitel 5',
        'Kapitel 6',
        'Kapitel 7',
        'Kapitel 8',
        'Kapitel 9',
        'Kapitel 10',
        'Kapitel 11',
        'Kapitel 12',
        'Kapitel 13',
    ]

    summary_of_book, summaries_of_parts, tokens_used, text_length = Summarizer().summarize_book(
        text='',
        filename=os.path.join('transcriptions', book_file_name),
        delimiters=delimiters,
        book_title='Rainer Sachse Personality types.',
        load_text_from_file=True)

    save_list_to_file(
        os.path.join(
            'book_summaries',
            timestamp + '_' + book_file_name),
        [summary_of_book])
    save_list_to_file(
        os.path.join(
            'chapter_summaries',
            timestamp + '_' + book_file_name),
        summaries_of_parts)

    log_info(f"Used up {tokens_used} tokens.\n"
             f"This is {tokens_used * 0.02 / 1000} $\n"
             f"This is {tokens_used * 0.02 / 1000 / text_length * 1000} $ per 1000 characters.")

    save_dict_to_file(
        os.path.join('openai_costs', timestamp + '_' + book_file_name[:-4] + '.json'),
        {'book_title': book_file_name[:-4],
         'text_length': text_length,
         'tokens_used': tokens_used,
         'costs': tokens_used * 0.02 / 1000,
         'costs_per_1000_characters': tokens_used * 0.02 / 1000 / text_length * 1000}
    )

# may 29th total usage 0.03 $
