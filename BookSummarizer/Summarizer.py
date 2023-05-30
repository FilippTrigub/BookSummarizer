import copy
import os
import re
import time
from typing import List, Union, Tuple

import tiktoken
import openai

from BookSummarizer.Transcriber import save_text_to_file


class Summarizer:
    TOKENS_USED = 0

    DEFAULT_LOOP_THRESHOLD_PER_100000_CHARS = 5
    DEFAULT_TIMEOUT_IN_MIN_PER_100000_CHARS = 5
    MODEL_NAME = "text-davinci-002"
    TOKEN_THRESHOLD = 4000

    def __init__(self):
        self.book_title = None

    def summarize_book(self, filename: str, delimiter: str, book_title: str):
        self.book_title = book_title

        text = self._get_text(filename)
        summaries_of_parts = self.summarize_parts(text, delimiter)
        summary_of_book = self.summarize_summaries_of_parts(copy.deepcopy(summaries_of_parts), len(text))

        return summary_of_book, summaries_of_parts, self.TOKENS_USED, len(text)

    def summarize_parts(self, text: str, delimiter: str) -> List[str]:
        parts = self._split_in_parts(text, delimiter)
        parts = self._clean_parts(parts)
        return self._summarize_parts(parts)

    def _summarize_parts(self, parts: List[str]) -> List[str]:
        summaries_of_parts = []
        for part in parts:
            chunks = self._split_in_chunks(part)
            summary_of_part = ''
            for chunk in chunks:
                summary_of_part = summary_of_part + self._summarize_chunk(chunk) + '\n'
            summaries_of_parts.append(summary_of_part)
        return summaries_of_parts

    def summarize_summaries_of_parts(self, summaries_of_parts: List[str], len_text: int) -> List[str]:
        timeout, loop_threshold = self._set_loop_threshold_and_timeout(len_text)

        while len(summaries_of_parts) > 1 and loop_threshold > 0 and time.time() < timeout:
            # with iterations, chunks should get smaller so that list of summaries gets smaller
            # until only 1 element remains.
            summaries_of_parts = self._summarize_parts(summaries_of_parts)
            loop_threshold -= 1
            if loop_threshold == 0 or time.time() > timeout:
                print('Loop count exceeded or timeout reached.')
                reset = input('Reset parameters and continue? (y/n)')
                if reset == 'y':
                    timeout, loop_threshold = self._set_loop_threshold_and_timeout(len_text)

        if len(summaries_of_parts) > 1:
            print('Summarization did not converge.')

        return summaries_of_parts

    def _set_loop_threshold_and_timeout(self, len_text: int) -> Tuple[float, int]:
        timeout = time.time() + 60 * self.DEFAULT_LOOP_THRESHOLD_PER_100000_CHARS * len_text
        loop_threshold = self.DEFAULT_LOOP_THRESHOLD_PER_100000_CHARS * len_text
        return timeout, loop_threshold

    @staticmethod
    def _get_text(filename: str) -> str:
        with open(filename, 'r') as file:
            text = file.read()
        return text

    @staticmethod
    def _split_in_parts(text: str, delimiter: str) -> List[str]:
        return text.split(delimiter)

    @staticmethod
    def _clean_parts(parts: List[str]) -> List[str]:
        # todo implement
        return parts

    @staticmethod
    def _num_tokens_from_string(string: str, model_name: str = None) -> int:
        """Returns the number of tokens in a text string."""
        model_name = "gpt-3.5-turbo" if not model_name else model_name
        encoding = tiktoken.encoding_for_model(model_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def split_into_chunks(self, text: str) -> List[str]:
        sentences = re.split('(?<=[.!?]) +', text)
        chunks = []
        chunk = ""
        for sentence in sentences:
            if self._num_tokens_from_string(chunk + sentence) <= 3000:
                chunk += sentence + " "
            else:
                chunks.append(chunk)
                chunk = sentence + " "
        if chunk:
            chunks.append(chunk)
        return chunks

    def _split_in_chunks(self, part: str) -> List[str]:
        if self._num_tokens_from_string(part) < self.TOKEN_THRESHOLD:
            return [part]
        else:
            return self.split_into_chunks(part)

    def generate_completion(self, prompt: str):
        response = openai.Completion.create(
            engine=self.MODEL_NAME,
            prompt=prompt,
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0].text.strip()

    def _summarize_chunk(self, chunk: str):
        prompt = f"""
            You are a Language AI. 
            You will be given a text, which is part of the book {self.book_title}. 
            Your task is to summarize the text in 10 points.
            Summarize according to the following four points.
            - (1): What are the main statements in the text?
            - (2): What is the core problem the author addresses?
            - (3): What are points of nuance the author highlights?
            - (4): What are open questions the author points out?
            Follow the format of the output that follows:                  
            Summary: \n\n
            - (1):xxx;\n 
            - (2):xxx;\n 
            - (3):xxx;\n  
            - (4):xxx.\n\n     
            
            Be sure to use statements as concise and academic as possible, do not have too much repetitive information.                 
            
            Text: \n\n
            {chunk}
        """

        summary = self.generate_completion(prompt)
        self.TOKENS_USED += self._num_tokens_from_string(prompt)
        return summary


if __name__ == '__main__':
    os.chdir('..')
    openai.api_key = "YOUR_API_KEY"
    summary_of_book, summaries_of_parts, tokens_used, text_length = Summarizer().summarize_book(
        'transcriptions/test.txt',
        '<Part \d+\.>',
        'Test')

    save_text_to_file(
        os.path.join(
            'summaries',
            f'test_{summary_of_book}.txt'),
        summary_of_book)
    save_text_to_file(
        os.path.join(
            'summaries',
            f'test_{summaries_of_parts}.txt'),
        summaries_of_parts)

    print(f"Used up {tokens_used} tokens.\n"
          f"This is {tokens_used * 0.02 / 1000} $\n"
          f"This is {tokens_used * 0.02 / 1000 / text_length * 1000} $ per 1000 characters.")
    save_text_to_file(
        os.path.join('openai_costs', 'test.txt'),
        {'book_title': 'Test',
         'text_length': text_length,
         'tokens_used': tokens_used,
         'costs': tokens_used * 0.02 / 1000,
         'costs_per_1000_characters': tokens_used * 0.02 / 1000 / text_length * 1000}
    )

# may 29th total usage 0.03 $
