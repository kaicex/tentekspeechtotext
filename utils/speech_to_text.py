from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY

class SpeechToTextConverter:
    """Класс для преобразования аудио в текст с использованием ElevenLabs API"""
    
    def __init__(self):
        """Инициализация клиента ElevenLabs"""
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    
    async def convert_audio_to_text(self, audio_data, language="ru"):
        """
        Преобразует аудио в текст
        
        :param audio_data: байты аудио файла
        :param language: язык аудио (по умолчанию русский)
        :return: распознанный текст
        """
        try:
            # Отправляем аудио на распознавание
            # Согласно документации ElevenLabs API, используем параметр 'file'
            result = self.client.speech_to_text.convert(
                model_id="scribe_v1",  # Используем доступную модель scribe_v1
                file=audio_data,        # Передаем байты аудиофайла
                language_code=language  # Код языка
            )
            return result.text
        
        except Exception as e:
            print(f"Ошибка при распознавании речи: {e}")
            return f"Ошибка при распознавании речи: {e}"
