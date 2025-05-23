import os
import asyncio
import logging
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
# На Render.com всегда используем вебхук
WEBHOOK_MODE = True
if os.environ.get('RENDER', False):
    logging.info("Запущено на Render.com, используется режим вебхука")
else:
    logging.info("Запущено локально, но всё равно используем режим вебхука для избежания конфликтов")

# Порт для Render.com (будет использоваться переменная окружения PORT)
PORT = int(os.environ.get('PORT', 8080))
logging.info(f"Используется порт: {PORT}")

# Настройка вебхука
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST', 'https://your-app-name.onrender.com')
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
    async def health_check(request):
        return web.Response(text="Бот для распознавания речи работает!")
    
    app.router.add_get("/", health_check)
    logging.info("Добавлен эндпоинт здоровья по пути /")
    
    # Регистрируем функции запуска и остановки
    setup_application(app, dp, bot=bot, 
                     on_startup=on_startup, 
                     on_shutdown=on_shutdown)
    
    # Запускаем веб-сервер
    logging.info(f"Запуск веб-сервера на порту {PORT} по адресу 0.0.0.0")
    return app

# Главная функция
async def main():
    # Всегда используем режим вебхука на Render.com
    logging.info("Запуск в режиме вебхука")
    
    # Принудительно удаляем предыдущий вебхук
    bot = Bot(token=BOT_TOKEN)
    try:
        logging.info("Пытаемся получить информацию о вебхуке...")
        webhook_info = await bot.get_webhook_info()
        logging.info(f"Текущий вебхук: {webhook_info.url if webhook_info.url else 'Не установлен'}")
        
        if webhook_info.url:
            await bot.delete_webhook(drop_pending_updates=True)
            logging.info("Предыдущий вебхук удален с отбрасыванием обновлений")
    except Exception as e:
        logging.error(f"Ошибка при получении информации о вебхуке: {e}")
    finally:
        await bot.session.close()
    
    # Запускаем веб-сервер
    app = await start_webhook()
    web_runner = web.AppRunner(app)
    await web_runner.setup()
    
    # Явно указываем привязку к порту и IP
    site = web.TCPSite(web_runner, host='0.0.0.0', port=PORT)
    await site.start()
    logging.info(f"Сайт запущен на 0.0.0.0:{PORT}")
    
    # Держим приложение работающим
    try:
        while True:
            logging.info(f"Бот работает, слушает порт {PORT}")
            await asyncio.sleep(60)  # Логируем каждую минуту для наблюдения
    except asyncio.CancelledError:
        logging.info("Приложение остановлено")
        await web_runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен!")
