import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Проверяем, запущены ли мы на Render
is_render = os.environ.get('RENDER', False)

# Загрузка переменных окружения
def load_env_vars():
    # Если мы на Render, используем только переменные окружения
    if is_render:
        logging.info("Запущено на Render, используем переменные окружения Render")
        return {
            'BOT_TOKEN': os.environ.get('BOT_TOKEN'),
            'ELEVENLABS_API_KEY': os.environ.get('ELEVENLABS_API_KEY'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
            'WEBHOOK_HOST': os.environ.get('WEBHOOK_HOST', 'https://tentekspeechtotext.onrender.com')
        }
    
    # Для локальной разработки пробуем загрузить из .env файла
    env_vars = {}
    try:
        # Пытаемся сначала использовать python-dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logging.info("Загружены переменные окружения с помощью python-dotenv")
        except ImportError:
            logging.warning("python-dotenv не установлен, читаем .env вручную")
            # Если python-dotenv не установлен, читаем .env вручную
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    env_vars[key] = value
                    os.environ[key] = value
                    
        # В любом случае получаем переменные из окружения
        return {
            'BOT_TOKEN': os.environ.get('BOT_TOKEN'),
            'ELEVENLABS_API_KEY': os.environ.get('ELEVENLABS_API_KEY'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
            'WEBHOOK_HOST': os.environ.get('WEBHOOK_HOST', 'https://tentekspeechtotext.onrender.com')
        }
    except Exception as e:
        logging.error(f"Ошибка при чтении переменных окружения: {e}")
        # В случае ошибки возвращаем значения из окружения
        return {
            'BOT_TOKEN': os.environ.get('BOT_TOKEN'),
            'ELEVENLABS_API_KEY': os.environ.get('ELEVENLABS_API_KEY'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
            'WEBHOOK_HOST': os.environ.get('WEBHOOK_HOST', 'https://tentekspeechtotext.onrender.com')
        }

# Загружаем переменные окружения
env_vars = load_env_vars()

# Получаем ключи из загруженных переменных
BOT_TOKEN = env_vars.get('BOT_TOKEN')
ELEVENLABS_API_KEY = env_vars.get('ELEVENLABS_API_KEY')
OPENAI_API_KEY = env_vars.get('OPENAI_API_KEY')

# Проверяем и логируем значения ключей
if BOT_TOKEN:
    logging.info(f"BOT_TOKEN: {BOT_TOKEN[:5]}...{BOT_TOKEN[-5:]} (длина: {len(BOT_TOKEN)})")
else:
    logging.warning("BOT_TOKEN не найден")
    
if ELEVENLABS_API_KEY:
    logging.info(f"ELEVENLABS_API_KEY: {ELEVENLABS_API_KEY[:5]}...{ELEVENLABS_API_KEY[-5:]} (длина: {len(ELEVENLABS_API_KEY)})")
else:
    logging.warning("ELEVENLABS_API_KEY не найден")
    
if OPENAI_API_KEY:
    if OPENAI_API_KEY.startswith(('sk-', 'sk-prod-', 'sk-org-', 'sk-proj-')):
        logging.info(f"OPENAI_API_KEY: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-5:]} (длина: {len(OPENAI_API_KEY)})")
        print(f"Используется OpenAI API ключ: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-5:]}")    
    else:
        logging.warning(f"Формат OPENAI_API_KEY не соответствует ожидаемому: {OPENAI_API_KEY[:5]}...")
        # Используем обычную строку вместо f-строки без плейсхолдеров
        print("Предупреждение: Некорректный формат OpenAI API ключа. Проверьте значение в .env файле")
        # Устанавливаем в None, чтобы бот не пытался использовать неверный ключ
        OPENAI_API_KEY = None
else:
    logging.warning("OPENAI_API_KEY не найден")
    print("Предупреждение: Отсутствует API ключ OpenAI. Будет использоваться только ElevenLabs.")

# Проверка на наличие обязательных ключей
if not BOT_TOKEN:
    logging.error("Отсутствует токен бота (BOT_TOKEN). Укажите его в переменных окружения")
    if not is_render:
        raise ValueError("Отсутствует токен бота. Укажите BOT_TOKEN в .env файле")

# Проверка API ключей для сервисов распознавания речи
if not ELEVENLABS_API_KEY and not OPENAI_API_KEY:
    logging.error("Отсутствуют API ключи для распознавания речи. Укажите хотя бы один: ELEVENLABS_API_KEY или OPENAI_API_KEY")
    if not is_render:
        raise ValueError("Отсутствуют API ключи для распознавания речи. Укажите хотя бы один: ELEVENLABS_API_KEY или OPENAI_API_KEY в .env файле")

# Если хотя бы один ключ есть, предупреждаем о недостающем
if not ELEVENLABS_API_KEY and OPENAI_API_KEY:
    logging.info("Найден только ключ OpenAI API")
    # Используем обычную строку вместо f-строки без плейсхолдеров
    print("Предупреждение: Отсутствует API ключ ElevenLabs. Будет использоваться только OpenAI Whisper.")
