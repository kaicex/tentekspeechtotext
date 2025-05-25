import os
import logging

# Загрузка переменных окружения напрямую из файла
def load_env_vars():
    env_vars = {}
    try:
        with open(".env", "r", encoding="utf-8") as f:  # Явно указываем кодировку UTF-8
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key, value = line.split('=', 1)
                env_vars[key] = value
                os.environ[key] = value
    except Exception as e:
        logging.error(f"Ошибка при чтении .env: {e}")
    return env_vars

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
        print(f"Предупреждение: Некорректный формат OpenAI API ключа. Проверьте значение в .env файле")
        # Устанавливаем в None, чтобы бот не пытался использовать неверный ключ
        OPENAI_API_KEY = None
else:
    logging.warning("OPENAI_API_KEY не найден")
    print("Предупреждение: Отсутствует API ключ OpenAI. Будет использоваться только ElevenLabs.")

# Проверка на наличие обязательных ключей
if not BOT_TOKEN:
    raise ValueError("Отсутствует токен бота. Укажите BOT_TOKEN в .env файле")

# Проверка API ключей для сервисов распознавания речи
if not ELEVENLABS_API_KEY and not OPENAI_API_KEY:
    raise ValueError("Отсутствуют API ключи для распознавания речи. Укажите хотя бы один: ELEVENLABS_API_KEY или OPENAI_API_KEY в .env файле")

# Если хотя бы один ключ есть, предупреждаем о недостающем
if not ELEVENLABS_API_KEY and OPENAI_API_KEY:
    # Используем обычную строку вместо f-строки без плейсхолдеров
    print("Предупреждение: Отсутствует API ключ ElevenLabs. Будет использоваться только OpenAI Whisper.")
