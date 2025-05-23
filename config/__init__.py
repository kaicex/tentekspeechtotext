import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

if not BOT_TOKEN:
    raise ValueError("Отсутствует токен бота. Укажите BOT_TOKEN в .env файле")

if not ELEVENLABS_API_KEY:
    raise ValueError("Отсутствует API ключ ElevenLabs. Укажите ELEVENLABS_API_KEY в .env файле")
