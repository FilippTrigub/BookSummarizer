import os
import re
import time

import tiktoken
from transformers import AutoTokenizer, AutoModelForCausalLM

from BookSummarizer.Transcriber import save_text_to_file


class Summarizer:

    def summarize_book(self, filename, delimiter, book_title):
        self.book_title = book_title

        text = self._get_text(filename)
        parts = self._split_in_parts(text, delimiter)
        parts = self._clean_parts(parts)
        summaries = self._summarize_parts(parts)

        timeout = time.time() + 60 * 5
        max_loops = 5
        while len(summaries) > 1 and max_loops > 0 and time.time() < timeout:
            summaries = self._summarize_parts(summaries)
        if len(summaries) > 1:
            print('Summarization did not converge.')
        return summaries

    def _summarize_parts(self, parts):
        summaries = []
        for part in parts:
            chunks = self._split_in_chunks(part)
            summary = ''
            for chunk in chunks:
                summary = summary + self._summarize_chunk(chunk) + '\n'
            summaries.append(summary)
        return summaries

    def _get_text(self, filename):
        with open(filename, 'r') as file:
            text = file.read()
        return text

    def _split_in_parts(self, text, delimiter):
        return text.split(delimiter)

    def _clean_parts(self, parts):
        # todo implement
        return parts

    @staticmethod
    def _num_tokens_from_string(string: str, encoding_name: str = None) -> int:
        """Returns the number of tokens in a text string."""
        encoding_name = "gpt-3.5-turbo" if not encoding_name else encoding_name
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def split_into_chunks(self, text):
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

    def _split_in_chunks(self, part):
        if self._num_tokens_from_string(part) < 4000:
            return [part]
        else:
            return self.split_into_chunks(part)

    def _summarize_chunk(self, chunk):
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

        # todo use palm2 model
        vertex_api_key = 'AIzaSyCBqlTdxhHY6e42-Lg3vCgXKjVGihZKUXQ'
        # tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom")
        # model = AutoModelForCausalLM.from_pretrained("bigscience/bloom",
        #                                              device_map="auto",
        #                                              torch_dtype='auto')
        #
        # inputs = tokenizer(prompt, return_tensors="pt")
        # summary = tokenizer.decode(model.generate(inputs["input_ids"],
        #                                           max_length=4000
        #                                           )[0])
        return summary


if __name__ == '__main__':
    summaries = Summarizer().summarize_book(
        'transcriptions/Getting_To_Yes_Negotiating_Agreement_Without_Giving_In_Roger_Fisher_&_William_Ury.txt',
        '<Part \d+\.>',
        'Getting To Yes Negotiating Agreement Without Giving In')
    save_text_to_file(os.path.join('summaries',
                                   'Getting_To_Yes_Negotiating_Agreement_Without_Giving_In_Roger_Fisher_&_William_Ury.txt'),
                      summaries)
