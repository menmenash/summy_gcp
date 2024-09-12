"""
Telegram Bot for Article Summarization and Interaction

This module implements a Telegram bot that provides article summarization and interaction
capabilities. The bot can summarize articles from URLs, handle PDF documents, and respond
to follow-up questions about summaries. It integrates with various services including
text extraction, summarization, and OpenAI's language model.

Key features:
- Article summarization from URLs
- PDF document summarization
- Configuration management for language and summary length
- Follow-up responses to summaries using OpenAI
- Integration with Google Cloud Storage for storing article content
- User authorization for specific commands

Classes:
- TelegramBot: Main class that handles bot initialization and command routing

Dependencies:
- telegram: For Telegram bot API interaction
- google.cloud.storage: For Google Cloud Storage integration
- logging: For logging events and errors
- Various custom services and utilities (config_manager, text_extractor, text_summarizer, etc.)

Usage:
Initialize the TelegramBot with required parameters and call the run() method to start the bot.

Note: Ensure all required environment variables and configurations are set before running the bot.
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from services.config_manager import ConfigManager
from services.text_extractor import TextExtractor
from services.text_summarizer import TextSummarizer
from utils.telegram_utils import prepare_message_for_telegram
from utils.openai_utils import OpenAIUtils
from constants.telegram_constants import TELEGRAM_MESSAGE_SIZE_LIMIT
from google.cloud import storage
from typing import List
import sys
import logging
logger = logging.getLogger(__name__)


class TelegramBot:
    """
    A Telegram bot for article summarization and interaction.

    This class encapsulates the functionality of a Telegram bot that can summarize articles,
    handle PDF documents, manage configurations, and interact with users through various commands.

    Attributes:
        application (Application): The Telegram bot application instance.
        allowed_users (List[int]): List of user IDs authorized to use certain commands.
        config_manager (ConfigManager): Manages bot configuration settings.
        text_extractor (TextExtractor): Extracts text from URLs and documents.
        text_summarizer (TextSummarizer): Summarizes extracted text.
        storage_client (storage.Client): Google Cloud Storage client for storing article content.
        bucket_name (str): Name of the Google Cloud Storage bucket.
        openai_utils (OpenAIUtils): Utility for interacting with OpenAI's API.

    Methods:
        setup_handlers(): Sets up command and message handlers for the bot.
        start(update, context): Handles the /start command.
        help(update, context): Provides help information about available commands.
        set_config(update, context): Updates bot configuration settings.
        set_config(update, context): Print bot configuration settings.
        summarize_article(update, context): Summarizes an article from a given URL.
        respond_summary(update, context): Provides a follow-up response to the last summary.
        summarize_pdf(update, context): Handles PDF document summarization.
        shutdown(update, context): Shuts down the bot (for authorized users only).
        run(): Starts the bot and begins polling for updates.

    The bot supports various commands including /start, /help, /set, /summ, /resp, and /shut.
    It integrates with external services for text extraction, summarization, and natural language processing.
    """
    def __init__(self, token: str, allowed_users: List[int], config_manager: ConfigManager,
                 text_extractor: TextExtractor, text_summarizer: TextSummarizer,
                 storage_client: storage.Client, bucket_name: str, openai_api_key: str):
        self.application = Application.builder().token(token).build()
        self.allowed_users = allowed_users
        self.config_manager = config_manager
        self.text_extractor = text_extractor
        self.text_summarizer = text_summarizer
        self.storage_client = storage_client
        self.bucket_name = bucket_name
        self.openai_utils = OpenAIUtils(openai_api_key)

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("set", self.set_config))
        self.application.add_handler(CommandHandler("get", self.get_config))
        self.application.add_handler(CommandHandler("summ", self.summarize_article))
        self.application.add_handler(CommandHandler("resp", self.respond_summary))
        self.application.add_handler(CommandHandler("shut", self.shutdown))
        self.application.add_handler(MessageHandler(filters.ALL, self.summarize_pdf))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Hi! Welcome to summy')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "Summy is at your service!\n"
            "- /summ <url>: Summarize the article at the given URL.\n"
            "- /summ pdf: Summarize an uploaded PDF file.\n"
            "- /resp <response>: Get a follow-up response to the last article.\n"
            "- /set <lang> <word limit> [max chars]: Set configuration.\n"
            "- /get: Print configuration.\n"
            "- /shut: Shut down the bot (authorized users only)."
        )
        await update.message.reply_text(help_text)

    async def set_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /set command to update configuration."""
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return

        args = context.args
        if not args or len(args) < 2 or len(args) > 3 or args[0] not in ['heb', 'eng'] or not args[1].isdigit():
            await update.message.reply_text('Please provide valid configuration, i.e., /set <heb/eng> <word limit> [max chars].')
            return

        lang, words_limit = args[0], int(args[1])
        telegram_message_size_limit = int(args[2]) if len(args) == 3 and args[2].isdigit() else TELEGRAM_MESSAGE_SIZE_LIMIT

        if self.config_manager.update_config(lang, words_limit, telegram_message_size_limit):
            await update.message.reply_text('Configuration updated successfully.')
        else:
            await update.message.reply_text('Failed to update configuration.')

    async def get_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /get command to print current configuration."""
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return
        
        config = self.config_manager.read_or_initialize_config()
        config_msg = f"language: {config.get('lang')}\nsummary words limit: {config.get('words_limit')}\ntelegram_msg_limit: {config.get('telegram_message_size_limit')}\n"

        if config:
            await update.message.reply_text(config_msg)
        else:
            await update.message.reply_text('Failed to retrieve configuration.')
        
    async def summarize_article(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /summ command to summarize articles."""
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return

        args = context.args
        if not args:
            await update.message.reply_text('Please provide a URL after the command, e.g., /summ <URL>.')
            return

        if args[0].lower() == 'pdf':
            await update.message.reply_text('Please upload the PDF file.')
            return
        
        url = args[0]
        article_text, is_webpage = await self.text_extractor.extract_from_url(url)
        if article_text:
            config = self.config_manager.read_or_initialize_config()
            summary = await self.text_summarizer.summarize(article_text, is_webpage, config)
            await update.message.reply_html(summary)

            # Store the full article in GCS bucket
            try:
                bucket = self.storage_client.bucket(self.bucket_name)
                blob = bucket.blob('Last_Article')
                blob.upload_from_string(article_text)
                logger.info("Article stored successfully in GCS.")
            except Exception as e:
                logger.error(f"Failed to store article in GCS: {str(e)}")

    async def respond_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /resp command to respond to the last summary."""
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return

        args = context.args
        if not args:
            await update.message.reply_text('Please provide a response for the last summary, e.g., /resp <RESPONSE>.')
            return

        config = self.config_manager.read_or_initialize_config()
        user_resp = ' '.join(args)
        
        # Retrieve last article text from the GCS storage
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob('Last_Article')
            last_text = blob.download_as_text()
            logger.info("Article read successfully from GCS.")
        except Exception as e:
            logger.error(f"Failed to read article from GCS: {str(e)}")
            await update.message.reply_text('Failed to retrieve the last article. Please try summarizing a new article.')
            return

        prompt = f"{last_text}\n\n\n\n\n\n{user_resp}\n\n"
        response = self.openai_utils.get_openai_response(prompt)

        telegram_response = prepare_message_for_telegram(response, config['telegram_message_size_limit'])
        await update.message.reply_html(telegram_response)

    async def summarize_pdf(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the command to summarize PDF - when its uploaded."""
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return
        
        # Verify that the file is a valid PDF
        document = update.message.document
        if (document == None):
            await update.message.reply_text('Please upload a valid PDF file.')
            return

        if document.mime_type == 'application/pdf':
            # Handle the pdf
            article_text = await self.text_extractor.extract_from_pdf(document, context)
            config = self.config_manager.read_or_initialize_config()
            summary = await self.text_summarizer.summarize(article_text, False, config)  
            await update.message.reply_html(summary)
        else:
            await update.message.reply_text('Please upload a valid PDF file.')
            return

        # Store the full article in GCS bucket
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob('Last_Article')
            blob.upload_from_string(article_text)
            logger.info("Article stored successfully in GCS.")
        except Exception as e:
            logger.error(f"Failed to store article in GCS: {str(e)}")

    async def shutdown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return
        await update.message.reply_text("Shutting down the bot. Goodbye!")
        await self.application.stop()
        await self.application.shutdown()
        sys.exit(0)

    def run(self):
        self.setup_handlers()
        self.application.run_polling(stop_signals=None)