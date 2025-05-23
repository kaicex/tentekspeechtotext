# Telegram Бот для Преобразования Аудио в Текст

Этот Telegram бот преобразует голосовые сообщения и аудиофайлы в текст с помощью ElevenLabs API.

## Настройка для локального запуска

1. Создайте файл `.env` в папке `config`:
```bash
cp config/.env.example config/.env
```

2. Отредактируйте файл и добавьте:
```
BOT_TOKEN=ваш_токен_телеграм_бота
ELEVENLABS_API_KEY=ваш_api_ключ_elevenlabs
```

3. Установите зависимости:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Запустите бота:
```bash
python bot.py
```

## Деплой на Render.com

1. Создайте новый веб-сервис на Render.com
2. Подключите ваш GitHub репозиторий
3. Настройте следующие параметры:
   - **Тип**: Web Service
   - **Среда**: Python 3
   - **Команда для сборки**: `pip install -r requirements.txt`
   - **Команда для запуска**: `python bot.py`

4. Добавьте переменные окружения:
   - `BOT_TOKEN` - токен вашего Telegram бота
   - `ELEVENLABS_API_KEY` - ваш API ключ от ElevenLabs
   - `WEBHOOK_MODE` - установите в `True`
   - `WEBHOOK_HOST` - URL вашего приложения на Render.com (например, `https://your-app-name.onrender.com`)

5. Нажмите "Create Web Service"

## Функциональность бота

- Бот принимает голосовые сообщения и аудиофайлы
- Преобразует их в текст с помощью ElevenLabs API
- Возвращает пользователю распознанный текст

## Команды бота

- `/start` - запуск бота и приветственное сообщение
- `/help` - инструкция по использованию
