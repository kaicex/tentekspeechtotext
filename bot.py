import os
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BOT_TOKEN
from handlers.audio_handler import router as audio_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Определяем, работаем ли мы в режиме вебхука (на Render.com)
WEBHOOK_MODE = os.environ.get('WEBHOOK_MODE', 'False').lower() == 'true'
# Порт для Render.com (будет использоваться переменная окружения PORT)
PORT = int(os.environ.get('PORT', 8080))

# Настройка вебхука
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST', 'https://your-app-name.onrender.com')
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Создаем список команд бота
async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Получить помощь")
    ]
    await bot.set_my_commands(commands)

# Настройка вебхука
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

# Запуск бота в режиме Long Polling
async def start_polling():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(audio_router)
    
    await on_startup(bot)
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await on_shutdown(bot)
        await bot.session.close()

# Запуск бота в режиме Webhook (для Render.com)
async def start_webhook():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(audio_router)
    
    # Настраиваем aiohttp
    app = web.Application()
    
    # Настраиваем обработчик вебхуков
    webhook_requests_handler = SimpleRequestHandler(dp, bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Главная страница для проверки статуса
    app.router.add_get("/", lambda request: web.Response(text="Бот для распознавания речи работает!"))
    
    # Регистрируем функции запуска и остановки
    setup_application(app, dp, bot=bot, 
                     on_startup=on_startup, 
                     on_shutdown=on_shutdown)
    
    # Запускаем веб-сервер
    logging.info(f"Запуск веб-сервера на порту {PORT}")
    return app

# Главная функция
async def main():
    if WEBHOOK_MODE:
        app = await start_webhook()
        web_runner = web.AppRunner(app)
        await web_runner.setup()
        site = web.TCPSite(web_runner, host='0.0.0.0', port=PORT)
        await site.start()
        
        # Держим приложение работающим
        while True:
            await asyncio.sleep(3600)
    else:
        await start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен!")
