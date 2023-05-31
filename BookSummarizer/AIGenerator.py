import os

import openai
import google.generativeai as palm


class BaseGenerator:
    def __init__(self):
        pass

    def generate_completion(self, prompt: str):
        raise NotImplemented


class PalmGenerator(BaseGenerator):
    def __init__(self):
        super().__init__()
        palm.configure(api_key='PALM_API_KEY')

    def generate_completion(self, prompt: str):
        completion = palm.generate_text(
            model=os.getenv("GENERATOR_MODEL"),
            prompt=prompt,
            temperature=os.getenv("GENERATOR_TEMPERATURE"),
            max_output_tokens=1000,
        )
        return completion.result


class GPTGenerator(BaseGenerator):
    def __init__(self):
        super().__init__()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_completion(self, prompt: str):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        response = openai.Completion.create(
            engine=os.getenv("GENERATOR_MODEL"),
            prompt=prompt,
            temperature=os.getenv("GENERATOR_TEMPERATURE"),
            max_tokens=1000
        )
        return response.choices[0].text.strip()
