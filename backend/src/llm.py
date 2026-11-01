from langchain.chat_models import init_chat_model
from tools import *
from envar import OLLAMA_URL

CHAT_MODEL = 'llama3.2:latest'

bare_llm = init_chat_model(CHAT_MODEL, model_provider='ollama', base_url=OLLAMA_URL)
llm = init_chat_model(CHAT_MODEL, model_provider='ollama', base_url=OLLAMA_URL)