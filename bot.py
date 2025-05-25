#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv
from handlers.audio_handler import router as audio_router
from config import BOT_TOKEN, OPENAI_API_KEY, ELEVENLABS_API_KEY

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Определяем, работаем ли мы в режиме вебхука (на Render.com)
if os.environ.get('RENDER', False):
    WEBHOOK_MODE = True
    logging.info("Запущено на Render.com, используется режим вебхука")
else:
    WEBHOOK_MODE = False
    logging.info("Запущено локально, используется режим Long Polling")

# Порт для Render.com (будет использоваться переменная окружения PORT)
PORT = int(os.environ.get('PORT', 8080))
logging.info(f"Используется порт: {PORT}")

# Настройка вебхука
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST', 'https://tentekspeechtotext.onrender.com')
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
logging.info(f"WEBHOOK_URL: {WEBHOOK_URL}")

# Создаем список команд бота
async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Получить помощь")
    ]
    await bot.set_my_commands(commands)

# Настройка при запуске
async def on_startup(bot: Bot):
    await setup_bot_commands(bot)
    if WEBHOOK_MODE:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Вебхук установлен на {WEBHOOK_URL}")

# Функция при остановке
async def on_shutdown(bot: Bot):
    if WEBHOOK_MODE:
        await bot.delete_webhook()
        logging.info("Вебхук удален")

# Запуск бота
async def main():
    # Создаем объекты бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрируем роутеры
    dp.include_router(audio_router)
    
    # Настраиваем хэндлеры запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Выводим информацию о доступных API
    if OPENAI_API_KEY:
        logging.info(f"Используется OpenAI Whisper API (ключ: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-5:]})")
    if ELEVENLABS_API_KEY:
        logging.info(f"Используется ElevenLabs API (ключ: {ELEVENLABS_API_KEY[:5]}...{ELEVENLABS_API_KEY[-5:]})")
    
    # Запускаем бота в соответствующем режиме
    if WEBHOOK_MODE:
        logging.info("Запуск в режиме вебхука не поддерживается в этой версии")
        return
    else:
        logging.info("Запуск в режиме Long Polling")
        await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен!")
