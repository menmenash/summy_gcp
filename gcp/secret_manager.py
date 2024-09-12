"""
Google Cloud Secret Manager Integration Module

This module provides a wrapper for interacting with Google Cloud Secret Manager.
It offers functionality to retrieve both plain text and JSON secrets securely.

The module includes:
- A SecretManager class for handling secret retrieval operations
- Methods for fetching individual secrets and JSON-formatted secrets
- Error handling and logging for secret retrieval operations

Dependencies:
- google-cloud-secret-manager: For interacting with Google Cloud Secret Manager
- json: For parsing JSON-formatted secrets
- logging: For logging operations and errors

Usage:
Initialize the SecretManager with a Google Cloud project ID, then use its methods
to retrieve secrets as needed.

Note: Proper Google Cloud authentication and permissions are required for this 
module to function correctly.
"""

import json
from google.cloud import secretmanager
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SecretManager:
    """
    A class for managing and retrieving secrets from Google Cloud Secret Manager.

    This class provides an interface to fetch both plain text and JSON-formatted
    secrets from Google Cloud Secret Manager. It handles the connection to the 
    Secret Manager service and offers methods to retrieve secrets securely.

    Attributes:
        client (secretmanager.SecretManagerServiceClient): The client for 
            interacting with Secret Manager.
        project_id (str): The Google Cloud project ID.

    Methods:
        get_secret(secret_id: str) -> str:
            Retrieves a plain text secret by its ID.
        get_json_secret(secret_id: str) -> Dict[str, Any]:
            Retrieves and parses a JSON-formatted secret by its ID.

    Each method includes error handling and logging to manage potential issues
    during secret retrieval and parsing.
    """

    def __init__(self, project_id):
        """
        Initializes the SecretManager with a Google Cloud project ID.

        Args:
            project_id (str): The Google Cloud project ID where the secrets are stored.
        """
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id

    def get_secret(self, secret_id: str) -> str:
        """
        Retrieve a secret from Google Secret Manager.

        Args:
            secret_id (str): The ID of the secret to retrieve.

        Returns:
            str: The secret value as a string.

        Raises:
            Exception: If there's an error retrieving the secret.
        """
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Error retrieving secret {secret_id}: {e}")
            raise

    def get_json_secret(self, secret_id: str) -> Dict[str, Any]:
        """
        Retrieve a JSON secret from Google Secret Manager.

        Args:
            secret_id (str): The ID of the secret to retrieve.

        Returns:
            Dict[str, Any]: The secret value as a dictionary.

        Raises:
            Exception: If there's an error retrieving or parsing the secret.
        """
        try:
            secret_value = self.get_secret(secret_id)
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON secret {secret_id}: {e}")
            raise