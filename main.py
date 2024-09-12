"""
Summy GCP Test   

This script sets up and runs a Telegram bot that summarizes articles and PDFs using GCP services.

The bot uses the following GCP services:
- Google storage: For storing and retrieving articles
- Firestore: For managing configuration
- Secrets Manager: For securely storing API keys and tokens

The main components of the system are:
1. TelegramBot: Handles user interactions and commands
2. ConfigManager: Manages bot configuration using DynamoDB
3. TextExtractor: Extracts text from URLs and PDFs
4. TextSummarizer: Summarizes extracted text using OpenAI's API
5. ????: Handles storing and retrieving articles from Google storage
6. SecretManager: Retrieves secrets from GCP Secrets Manager

Usage:
    Run this script to start the Telegram bot. Ensure all required GCP credentials
    and configurations are set up beforehand.

Note:
    This script requires various GCP permissions to be
    set up correctly. Refer to GCP Documentation in case of PermissionsError0s
"""

import os
import glob
import logging
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    filename='bot_summy.log',  
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set the logging level for httpx to WARNING
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

from bot.telegram_bot import TelegramBot
from gcp.secret_manager import SecretManager
from services.config_manager import ConfigManager
from services.text_extractor import TextExtractor
from services.text_summarizer import TextSummarizer
from google.cloud import storage

def main():
    # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    project_id = "zeta-bebop-416515"  # Replace with your actual project ID
 
    # Find the credentials file that starts with project_id and has a .json extension
    credentials_files = glob.glob(f"{project_id}*.json")
    if not credentials_files:
        raise FileNotFoundError(f"No credentials file found starting with '{project_id}' and ending with '.json'.")

    credentials_file = credentials_files[0]  # Take the first matching file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file

    # Initialize the Secret Manager
    secret_manager = SecretManager(project_id)

    # Get secrets from Google Secret Manager
    telegram_token = secret_manager.get_secret('Telegram_Token')
    openai_token = secret_manager.get_secret('OpenAI_Token')
    allowed_users_str = secret_manager.get_secret('Telegram_Allowed_Users_ID')

    # Extract allowed users, with a default empty list if the string is empty
    allowed_users = [int(user_id.strip()) for user_id in allowed_users_str.split(',') if user_id.strip()]

    # Setup Google Cloud Storage
    storage_client = storage.Client()
    bucket_name = 'summy-telegrambot-bucket'

    # Setup Firestore
    config_manager = ConfigManager('ConfigCollection')

    # Setup text extractor and summarizer
    text_extractor = TextExtractor()
    text_summarizer = TextSummarizer(openai_token)

    # Setup bot
    bot = TelegramBot(
        token=telegram_token,
        allowed_users=allowed_users,
        config_manager=config_manager,
        text_extractor=text_extractor,
        text_summarizer=text_summarizer,
        storage_client=storage_client,
        bucket_name=bucket_name,
        openai_api_key=openai_token
    )
    
    # Run bot
    bot.run()

if __name__ == '__main__':
    main()