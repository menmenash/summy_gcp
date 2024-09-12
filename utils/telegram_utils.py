"""
Telegram Utils

This module contains utility functions for preparing messages to be sent via Telegram.

Functions:
    prepare_message_for_telegram(summary: str, max_chars: int = 4096) -> str:
        Prepares a message for sending via Telegram by removing HTML tags,
        formatting list items, and truncating if necessary.

        Args:
            summary (str): The original message to be prepared.
            max_chars (int, optional): The maximum number of characters allowed
                                       in the message. Defaults to 4096.

        Returns:
            str: The prepared message, ready to be sent via Telegram.
"""
import logging
logger = logging.getLogger(__name__)

def prepare_message_for_telegram(summary: str, max_chars: int = 4096) -> str:
    tags_to_remove = ["<html>", "</html>", "<body>", "</body>", "<p>", "</p>", "<ul>", "</ul>"]
    tags_to_replace = {"<li>": "\n- ", "</li>": ""}
    
    for tag, replacement in tags_to_replace.items():
        summary = summary.replace(tag, replacement)
    for tag in tags_to_remove:
        summary = summary.replace(tag, "")

    summary = summary.replace("&", "").replace("<", "").replace(">", "")
    summary = summary.replace('- ', '\n-  ').replace('. ', '.\n')

    if len(summary) > max_chars:
        summary = summary[:max_chars-3] + "..."

    return summary