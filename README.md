# Summy GCP Bot

Summy GCP Bot is a Telegram bot that summarizes articles.
URL\PDF need to be supplied as an input.
Leverages OpenAI's API for text summarization and various GCP services for storage and configuration management.

## Features

- Summarize articles from URLs
- Summarize text from PDF files
- Store and retrieve articles using Google Cloud Storage
- Manage bot configuration with Google Cloud Firestore
- Secure storage of API keys and tokens using Google Secret Manager

## Prerequisites

- Python 3.7+
- Google Cloud Platform account with appropriate permissions
- Telegram Bot Token
- OpenAI API Key

## GCP Services Used

- Cloud Storage
- Firestore
- Secret Manager
- Compute Engine (optional, for easier deployment)

## Installation & Configuration

1. Clone the repository:
   ```
   git clone https://github.com/menmenash/summy_gcp.git
   cd summy_gcp
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
   
3. Set up GCP services:
   - Configure gcloud CLI or set environment variables for GCP access or use Compute Engine (optional)
   - Create a Cloud Storage bucket named `summy-telegrambot-bucket`
   - Create a Firestore database and a collection named `ConfigCollection`
   - Store the following secrets in Secret Manager:
     - `Telegram_Token`: Your Telegram Bot Token
     - `OpenAI_Token`: Your OpenAI API Key
     - `Telegram_Allowed_Users_ID`: Comma-separated list of allowed Telegram user IDs
       
4. Run main.py in detached mode.
   
## Usage

"Summy is at your service!\n"
            "- /set <lang> <word limit> [max chars]: Set configuration.\n"
            "- /summ <url>: Summarize the article at the given URL.\n"
            "- /summ pdf: Summarize an uploaded PDF file.\n"
            "- /resp <response>: Get a follow-up response to the last summary.\n"
