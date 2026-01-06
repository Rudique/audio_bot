import os
import logging
from pathlib import Path
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

# Глобальная модель (загружается один раз при запуске)
_model = None


def get_model():
    """Получить или инициализировать модель Whisper"""
    global _model
    if _model is None:
        logger.info("Загрузка модели Whisper...")
        # Используем модель "tiny" для максимальной скорости на CPU
        # Она в 2-3 раза быстрее "base" при хорошем качестве для коротких голосовых
        _model = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8",
            cpu_threads=4,  # Используем 4 потока для ускорения
            num_workers=2   # Параллельная обработка
        )
        logger.info("Модель Whisper загружена")
    return _model


def transcribe_audio(audio_path: str, language: str = "ru") -> str:
    """
    Распознать речь из аудио файла

    Args:
        audio_path: путь к аудио файлу
        language: язык распознавания (по умолчанию русский)

    Returns:
        распознанный текст
    """
    try:
        model = get_model()

        logger.info(f"Начало распознавания файла: {audio_path}")

        # Распознавание с оптимизированными параметрами для скорости
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=1,  # Минимальный для максимальной скорости
            vad_filter=True,  # Фильтр голосовой активности
            vad_parameters=dict(
                min_silence_duration_ms=500  # Быстрее пропускаем паузы
            ),
            condition_on_previous_text=False,  # Отключаем контекст - ускоряет
            temperature=0.0,  # Детерминированный вывод
        )

        logger.info(f"Начинаю сбор сегментов...")

        # Собираем все сегменты в один текст
        segments_list = list(segments)
        text = " ".join([segment.text.strip() for segment in segments_list])

        logger.info(f"Распознавание завершено. Язык: {info.language}, "
                   f"вероятность: {info.language_probability:.2f}, "
                   f"сегментов: {len(segments_list)}")

        return text.strip()

    except Exception as e:
        logger.error(f"Ошибка при распознавании аудио: {e}")
        raise
