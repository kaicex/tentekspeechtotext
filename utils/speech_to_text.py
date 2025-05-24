import logging
import os
import tempfile
import httpx
from elevenlabs.client import ElevenLabs
import openai
from config import ELEVENLABS_API_KEY, OPENAI_API_KEY

class SpeechToTextConverter:
    """Класс для преобразования аудио в текст с использованием OpenAI Whisper API и ElevenLabs API"""
    
    def __init__(self):
        """Инициализация клиентов API"""
        self.elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else None
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        
        # Определяем, какой API использовать по умолчанию
        if self.openai_client:
            logging.info("Используем OpenAI Whisper API по умолчанию")
            self.use_whisper = True
        elif self.elevenlabs_client:
            logging.info("Используем ElevenLabs API по умолчанию")
            self.use_whisper = False
        else:
            logging.error("Не найдено ни одного действующего API ключа")
            raise ValueError("Требуется хотя бы один API ключ: OPENAI_API_KEY или ELEVENLABS_API_KEY")
    
    async def convert_audio_to_text(self, audio_data, language="ru"):
        """
        Преобразует аудио в текст
        
        :param audio_data: байты аудио файла
        :param language: язык аудио (по умолчанию русский)
        :return: распознанный текст
        """
        if self.use_whisper:
            return await self._convert_with_whisper(audio_data, language)
        else:
            return await self._convert_with_elevenlabs(audio_data, language)
    
    async def _convert_with_whisper(self, audio_data, language="ru"):
        """Использует OpenAI Whisper API для преобразования аудио в текст"""
        if not self.openai_client:
            logging.error("Отсутствует OpenAI API ключ")
            if self.elevenlabs_client:
                return await self._convert_with_elevenlabs(audio_data, language)
            return "❌ Не настроен OpenAI API ключ. Добавьте OPENAI_API_KEY в настройки."
            
        try:
            # Создаем временный файл для аудио
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
                temp_filename = temp_file.name
                temp_file.write(audio_data)
            
            # Отправляем аудио на распознавание в Whisper API
            with open(temp_filename, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",  # Используем модель whisper-1
                    file=audio_file,
                    language=language,
                    response_format="text"
                )
            
            # Удаляем временный файл
            os.unlink(temp_filename)
            
            logging.info("Успешно распознано с помощью Whisper API")
            return transcript
            
        except Exception as e:
            logging.error(f"Ошибка при использовании Whisper API: {e}")
            # Если Whisper не работает, пробуем ElevenLabs
            if self.elevenlabs_client:
                logging.info("Переключаемся на ElevenLabs API")
                return await self._convert_with_elevenlabs(audio_data, language)
            return "❌ Ошибка Whisper API: " + str(e)
    
    async def _convert_with_elevenlabs(self, audio_data, language="ru"):
        """Использует ElevenLabs API для преобразования аудио в текст"""
        if not self.elevenlabs_client:
            logging.error("Отсутствует ElevenLabs API ключ")
            if self.openai_client:
                return await self._convert_with_whisper(audio_data, language)
            return "❌ Не настроен ElevenLabs API ключ. Добавьте ELEVENLABS_API_KEY в настройки."
            
        try:
            # Отправляем аудио на распознавание
            # Согласно документации ElevenLabs API, используем параметр 'file'
            result = self.elevenlabs_client.speech_to_text.convert(
                model_id="scribe_v1",  # Используем доступную модель scribe_v1
                file=audio_data,        # Передаем байты аудиофайла
                language_code=language  # Код языка
            )
            logging.info("Успешно распознано с помощью ElevenLabs API")
            return result.text
        
        except Exception as e:
            error_message = self._handle_elevenlabs_error(e)
            logging.error(f"ElevenLabs API ошибка: {e}")
            return error_message
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logging.error(f"HTTP ошибка: {status_code} - {e}")
            
            if status_code == 401:
                return "❌ Ошибка авторизации в ElevenLabs API. Возможно, истек бесплатный план или API ключ недействителен."
            elif status_code == 429:
                return "⚠️ Превышен лимит запросов к ElevenLabs API. Попробуйте позже."
            else:
                return f"❌ Ошибка сервера: {status_code}. Попробуйте позже."
        except Exception as e:
            logging.error(f"Неизвестная ошибка при распознавании речи: {e}")
            return "❌ Ошибка при распознавании речи. Попробуйте позже или отправьте аудио меньшего размера."
    
    def _handle_elevenlabs_error(self, error):
        """Обрабатывает специфические ошибки API ElevenLabs"""
        error_str = str(error)
        
        if "detected_unusual_activity" in error_str:
            # Если бесплатный план ElevenLabs заблокирован, переключаемся на Whisper
            self.use_whisper = True
            logging.info("Переключение на Whisper API из-за блокировки ElevenLabs")
            return "⚠️ ElevenLabs обнаружил необычную активность. Используем Whisper API."
        elif "free tier" in error_str.lower():
            self.use_whisper = True
            logging.info("Переключение на Whisper API из-за ограничения ElevenLabs")
            return "⚠️ Исчерпан лимит бесплатного плана ElevenLabs. Используем Whisper API."
        elif "invalid api key" in error_str.lower():
            self.use_whisper = True
            logging.info("Переключение на Whisper API из-за недействительного ключа ElevenLabs")
            return "❌ Недействительный ключ API ElevenLabs. Используем Whisper API."
        else:
            self.use_whisper = True
            logging.info("Переключение на Whisper API из-за ошибки ElevenLabs")
            return "❌ Ошибка ElevenLabs API. Используем Whisper API."
