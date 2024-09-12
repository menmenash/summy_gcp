"""
OpenAI Utils

This module contains utility functions for interacting with the OpenAI API.

Classes:
    OpenAIUtils: A class that provides methods for summarizing text and generating responses using OpenAI's API.

Methods:
    __init__(self, api_key: str):
        Initializes the OpenAIUtils class with the provided API key.

    get_openai_summary(self, text: str, is_webpage: bool, config: dict) -> str:
        Generates a summary of the given text using OpenAI's API.

        Args:
            text (str): The text to be summarized.
            is_webpage (bool): Indicates whether the text is from a webpage.
            config (dict): Configuration parameters for the summary.

        Returns:
            str: The generated summary.

    get_openai_response(self, prompt: str, config: dict) -> str:
        Generates a response to the given prompt using OpenAI's API.

        Args:
            prompt (str): The prompt to generate a response for.
            config (dict): Configuration parameters for the response.

        Returns:
            str: The generated response.

Note:
    This class requires a valid OpenAI API key to function properly.
    Ensure that the API key is set correctly before using these methods.
"""

import openai
import logging
logger = logging.getLogger(__name__)

class OpenAIUtils:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = self.api_key

    def get_openai_summary(self, text: str, is_webpage: bool, config: dict) -> str:
        translation_instruction = "Translate the answer to Hebrew, except Brands or technology terms and definitions. " if config.get('lang') == 'heb' else ""
        
        base_prompt = (
            f"{translation_instruction}"
            f"Summarize this text extracted from a {'webpage' if is_webpage else 'article'}."
        )

        if is_webpage:
            base_prompt += "Remove any non-article elements like ads or navigation links. "

        base_prompt += (
            f"Please provide a concise summary of the following article, "
            f"focusing on the main points, arguments, and conclusions. "
            f"The summary should be clear, informative, and no longer than {config.get('words_limit')} words. "
            f"Replace bullet points with dashes (-), and use spaces to indicate indentation. "
        )

        prompt = f"{base_prompt}\n\n{text}"

        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                max_tokens=2048,
                temperature=0.7,
                n=1,
                stop=None,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            summary = response.choices[0].message.content.strip()
            logger.info("Summarized using OpenAI, length: %d words", len(summary.split()))
            return summary
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise

    def get_openai_response(self, prompt: str) -> str:
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                max_tokens=2048,
                temperature=0.7,
                n=1,
                stop=None,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.choices[0].message.content.strip()
            logger.info("Received response from OpenAI, length: %d words", len(response_text.split()))
            return response_text
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise