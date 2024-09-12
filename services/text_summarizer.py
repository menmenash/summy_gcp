"""
This module provides the TextSummarizer class, which is designed to interface with the OpenAI API for text summarization
and response generation. It also includes functionality to format these responses for Telegram messaging. The class
utilizes helper utilities from the `utils` package to handle specific interactions with OpenAI and Telegram.
"""
from utils.openai_utils import OpenAIUtils
from utils.telegram_utils import prepare_message_for_telegram
import logging
logger = logging.getLogger(__name__)

class TextSummarizer:
    """
    A utility class for generating summaries and responses using the OpenAI API, tailored for Telegram messaging.

    This class provides methods to:
    - Summarize text with considerations for its source (e.g., webpage or other) using OpenAI's language models.
    - Generate a response based on a provided prompt, using OpenAI's language models.
    - Format both summaries and responses to comply with Telegram's message size limitations.

    Constructor Args:
        openai_api_key (str): The API key required to authenticate requests to OpenAI.

    Methods:
        summarize(text: str, is_webpage: bool, config: dict) -> str:
            Asynchronously generates a summary of the provided text. The summary is then formatted for Telegram.

        respond(prompt: str, config: dict) -> str:
            Asynchronously generates a response to the given prompt. The response is then formatted for Telegram.
    """

    def __init__(self, openai_api_key: str):
        self.openai_utils = OpenAIUtils(openai_api_key)

    async def summarize(self, text: str, is_webpage: bool, config: dict) -> str:
        summary = self.openai_utils.get_openai_summary(text, is_webpage, config)
        return prepare_message_for_telegram(summary, config['telegram_message_size_limit'])

    async def respond(self, prompt: str, config: dict) -> str:
        response = self.openai_utils.get_openai_response(prompt, config)
        return prepare_message_for_telegram(response, config['telegram_message_size_limit'])