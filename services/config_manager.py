"""
Configuration Management Module for Firestore Integration

This module provides functionality for managing configuration settings using Google Cloud Firestore.
It offers a streamlined interface for storing, retrieving, and updating configuration data.

Key features:
- Initialization of default configuration settings
- Reading existing configuration or creating a new one with default values
- Updating configuration settings with validation

The module includes:
- A ConfigManager class for handling all configuration-related operations
- Integration with Google Cloud Firestore for persistent storage
- Error handling and logging for configuration operations

Dependencies:
- google-cloud-firestore: For interacting with Google Cloud Firestore
- logging: For logging operations and errors

Usage:
Initialize the ConfigManager with a Firestore collection name, then use its methods
to read, initialize, or update configuration settings as needed.

Note: Proper Google Cloud authentication and Firestore setup are required for this
module to function correctly.
"""

from typing import Dict, Any
import logging
from google.cloud import firestore

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages configuration storage and retrieval using Google Cloud Firestore.

    This class provides an interface to interact with a Firestore collection for storing,
    retrieving, and updating configuration settings. It handles the connection to Firestore
    and offers methods to manage configuration data securely and efficiently.

    Attributes:
        db (firestore.Client): Firestore client for database operations.
        collection_name (str): Name of the Firestore collection where config is stored.
        default_config (Dict[str, Any]): Default configuration settings used for initialization.

    Methods:
        read_or_initialize_config() -> Dict[str, Any]:
            Retrieves existing configuration or initializes with default values.
        update_config(lang: str, words_limit: int, telegram_message_size_limit: int = 4096) -> bool:
            Updates the configuration with new values, including validation.

    The class includes error handling and logging to manage potential issues
    during configuration operations.
    """

    def __init__(self, collection_name: str):
        """
        Initialize the ConfigManager with a Firestore collection name.

        Args:
            collection_name (str): The name of the Firestore collection to use for config storage.
        """
        self.db = firestore.Client()
        self.collection_name = collection_name
        self.default_config = {
            'lang': 'eng',
            'words_limit': 300,
            'telegram_message_size_limit': 4096
        }

    def read_or_initialize_config(self) -> Dict[str, Any]:
        """
        Read the configuration from Firestore or initialize with default values.

        Returns:
            Dict[str, Any]: The configuration dictionary.
        """
        doc_ref = self.db.collection(self.collection_name).document('config')
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            doc_ref.set(self.default_config)
            return self.default_config.copy()

    def update_config(self, lang: str, words_limit: int, telegram_message_size_limit: int = 4096) -> bool:
        """
        Update the configuration in Firestore.

        Args:
            lang (str): Language setting ('eng' or 'heb').
            words_limit (int): Word limit for summaries.
            telegram_message_size_limit (int, optional): Maximum character limit for Telegram messages. 
                                                         Defaults to 4096.

        Returns:
            bool: True if update was successful, False otherwise.

        Raises:
            ValueError: If invalid language, words_limit, or telegram_message_size_limit is provided.
        """
        if lang not in ['eng', 'heb']:
            raise ValueError("Language must be either 'eng' or 'heb'")
        if not isinstance(words_limit, int) or words_limit < 0 or words_limit > 800:
            raise ValueError("words_limit must be an integer between 0 and 800")
        if not isinstance(telegram_message_size_limit, int) or telegram_message_size_limit < 1 or telegram_message_size_limit > 4096:
            raise ValueError("telegram_message_size_limit must be an integer between 1 and 4096")

        try:
            doc_ref = self.db.collection(self.collection_name).document('config')
            doc_ref.set({
                'lang': lang,
                'words_limit': words_limit,
                'telegram_message_size_limit': telegram_message_size_limit
            })
            return True
        except Exception as e:
            logger.error("Error updating config: %s", e)
            return False
