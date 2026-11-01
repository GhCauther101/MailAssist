import os
from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_USER = os.getenv('IMAP_USER')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')
IMAP_FOLDER = 'INBOX'

DEPLOY_PORT = os.getenv('DEPLOY_PORT')
OLLAMA_URL = os.getenv('OLLAMA_URL')