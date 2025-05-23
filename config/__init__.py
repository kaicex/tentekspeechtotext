import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not BOT_TOKEN:
    raise ValueError("Отсутствует токен бота. Укажите BOT_TOKEN в .env файле")

# Проверка API ключей для сервисов распознавания речи
if not ELEVENLABS_API_KEY and not OPENAI_API_KEY:
    raise ValueError("Отсутствуют API ключи для распознавания речи. Укажите хотя бы один: ELEVENLABS_API_KEY или OPENAI_API_KEY в .env файле")

# Если хотя бы один ключ есть, предупреждаем о недостающем
if not ELEVENLABS_API_KEY:
    print("Предупреждение: Отсутствует API ключ ElevenLabs. Будет использоваться только OpenAI Whisper.")

if not OPENAI_API_KEY:
    print("Предупреждение: Отсутствует API ключ OpenAI. Будет использоваться только ElevenLabs.")
