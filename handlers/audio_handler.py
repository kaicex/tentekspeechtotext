from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.speech_to_text import SpeechToTextConverter

# Создаем роутер для обработки аудио сообщений
router = Router()

# Инициализируем конвертер речи в текст
speech_converter = SpeechToTextConverter()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для преобразования голосовых сообщений в текст.\n\n"
        "Отправь мне голосовое сообщение или аудиофайл, и я верну его текстовую расшифровку."
    )

@router.message(F.voice)
async def handle_voice(message: Message):
    """Обработчик голосовых сообщений"""
    # Отправляем сообщение о начале обработки
    processing_msg = await message.answer("🔍 Обрабатываю голосовое сообщение...")
    
    try:
        # Получаем файл голосового сообщения
        voice_file = await message.bot.get_file(message.voice.file_id)
        voice_data = await message.bot.download_file(voice_file.file_path)
        
        # Преобразуем голосовое сообщение в текст
        text = await speech_converter.convert_audio_to_text(voice_data.read())
        
        # Отправляем результат
        await message.reply(f"{text}")
        
    except Exception as e:
        await message.reply(f"❌ Произошла ошибка при обработке голосового сообщения: {str(e)}")
    
    finally:
        # Удаляем сообщение о обработке
        await processing_msg.delete()

@router.message(F.audio)
async def handle_audio(message: Message):
    """Обработчик аудиофайлов"""
    # Отправляем сообщение о начале обработки
    processing_msg = await message.answer("🔍 Обрабатываю аудиофайл...")
    
    try:
        # Получаем аудиофайл
        audio_file = await message.bot.get_file(message.audio.file_id)
        audio_data = await message.bot.download_file(audio_file.file_path)
        
        # Преобразуем аудио в текст
        text = await speech_converter.convert_audio_to_text(audio_data.read())
        
        # Отправляем результат
        await message.reply(f"{text}")
        
    except Exception as e:
        await message.reply(f"❌ Произошла ошибка при обработке аудиофайла: {str(e)}")
    
    finally:
        # Удаляем сообщение о обработке
        await processing_msg.delete()
