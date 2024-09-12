"""
This module provides the TextExtractor class which is designed for extracting text content from web pages and PDF files.
It leverages the Playwright library to scrape web content and the pdfminer library to extract text from PDF documents.
This class supports asynchronous web scraping with options to extract the main article content or the full page text,
and a method for extracting text from PDF files loaded into a BytesIO buffer.
"""
from telegram.ext import ContextTypes
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from io import BytesIO
from typing import Tuple, Any
import logging
logger = logging.getLogger(__name__)

class TextExtractor:
    """
    A utility class for extracting text from either web pages or PDF files.

    This class provides:
    - Asynchronous methods to fetch and extract text from specified URLs using the Playwright browser automation library.
    - A method to extract text from PDF files using the pdfminer library.

    Methods:
        extract_from_url(url: str) -> Tuple[str, bool]:
            Extracts text from the specified URL. Determines whether the text is from the full page or just the main article.

        extract_from_pdf(pdf_file: BytesIO) -> str:
            Extracts and returns text content from a PDF file provided as a BytesIO object.
    """

    @staticmethod
    async def extract_from_url(url: str) -> Tuple[str, bool]:
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_timeout(10000)
            content = await page.content()
            await browser.close()

            soup = BeautifulSoup(content, 'html.parser')
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            article_body = soup.find('article') or soup.find('div', class_='article-content') or soup.find('main')
            if article_body:
                text = " ".join(article_body.stripped_strings)
                is_full_page = False
            else:
                text = " ".join(soup.stripped_strings)
                is_full_page = True

            return text, is_full_page

    @staticmethod
    async def extract_from_pdf(document: Any, context: ContextTypes.DEFAULT_TYPE) -> str:
        file = await context.bot.get_file(document.file_id)
        bio_content = BytesIO()
        await file.download_to_memory(out=bio_content)
        article_text = extract_text(bio_content)
        return article_text