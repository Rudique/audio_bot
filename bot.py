import asyncio
import logging
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ChatAction

from config import BOT_TOKEN
from speech_recognition import transcribe_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаем директорию для временных файлов
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# Executor для выполнения синхронных операций в отдельных потоках
executor = ThreadPoolExecutor(max_workers=3)


async def process_audio(message: Message, file_id: str, file_extension: str = "ogg") -> str:
    """
    Скачать и распознать аудио файл

    Args:
        message: сообщение от пользователя
        file_id: ID файла в Telegram
        file_extension: расширение файла

    Returns:
        распознанный текст
    """
    file_path = None
    try:
        logger.info(f"[Пользователь {message.from_user.id}] Начало обработки аудио")

        # Получаем информацию о файле
        file = await bot.get_file(file_id)
        logger.info(f"[Пользователь {message.from_user.id}] Информация о файле получена")

        # Путь для сохранения
        file_path = TEMP_DIR / f"{message.from_user.id}_{message.message_id}.{file_extension}"

        # Скачиваем файл
        logger.info(f"[Пользователь {message.from_user.id}] Скачивание файла...")
        await bot.download_file(file.file_path, file_path)
        logger.info(f"[Пользователь {message.from_user.id}] Файл скачан: {file_path}")

        # Распознаем речь в отдельном потоке чтобы не блокировать event loop
        logger.info(f"[Пользователь {message.from_user.id}] Начинаю распознавание речи...")
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(
            executor,
            transcribe_audio,
            str(file_path),
            "ru"
        )
        logger.info(f"[Пользователь {message.from_user.id}] Распознавание завершено, длина текста: {len(text) if text else 0}")

        return text

    except Exception as e:
        logger.error(f"[Пользователь {message.from_user.id}] Ошибка при обработке аудио: {e}", exc_info=True)
        raise
    finally:
        # Удаляем временный файл
        if file_path and file_path.exists():
            os.remove(file_path)
            logger.info(f"[Пользователь {message.from_user.id}] Временный файл удален: {file_path}")


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для распознавания аудио сообщений.\n\n"
        "📤 Отправь мне голосовое сообщение или аудио файл, "
        "и я распознаю текст из него.\n\n"
        "Жду твое аудио! 🎤"
    )


@dp.message(F.voice)
async def handle_voice(message: Message):
    """Обработчик голосовых сообщений"""
    status_msg = None
    try:
        logger.info(f"[Пользователь {message.from_user.id}] Получено голосовое сообщение")

        # Отправляем сообщение о начале обработки
        status_msg = await message.answer("🎤 Обрабатываю голосовое сообщение...")

        # Показываем индикатор "печатает"
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Обрабатываем аудио
        text = await process_audio(message, message.voice.file_id, "ogg")

        if text:
            # Отправляем распознанный текст
            await status_msg.edit_text(f"✅ Распознанный текст:\n\n{text}")
            logger.info(f"[Пользователь {message.from_user.id}] Текст успешно отправлен")
        else:
            await status_msg.edit_text("❌ Не удалось распознать текст. Попробуйте записать сообщение заново.")
            logger.warning(f"[Пользователь {message.from_user.id}] Пустой результат распознавания")

    except Exception as e:
        logger.error(f"[Пользователь {message.from_user.id}] Ошибка при обработке голосового сообщения: {e}", exc_info=True)
        error_text = "❌ Произошла ошибка при распознавании. Попробуйте еще раз."
        if status_msg:
            try:
                await status_msg.edit_text(error_text)
            except:
                await message.answer(error_text)
        else:
            await message.answer(error_text)


@dp.message(F.audio)
async def handle_audio(message: Message):
    """Обработчик аудио файлов"""
    status_msg = None
    try:
        logger.info(f"[Пользователь {message.from_user.id}] Получен аудио файл")

        # Отправляем сообщение о начале обработки
        status_msg = await message.answer("🎵 Обрабатываю аудио файл...")

        # Показываем индикатор "печатает"
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Получаем расширение файла
        file_name = message.audio.file_name or "audio.mp3"
        file_extension = file_name.split(".")[-1] if "." in file_name else "mp3"
        logger.info(f"[Пользователь {message.from_user.id}] Файл: {file_name}, расширение: {file_extension}")

        # Обрабатываем аудио
        text = await process_audio(message, message.audio.file_id, file_extension)

        if text:
            # Отправляем распознанный текст
            await status_msg.edit_text(f"✅ Распознанный текст:\n\n{text}")
            logger.info(f"[Пользователь {message.from_user.id}] Текст успешно отправлен")
        else:
            await status_msg.edit_text("❌ Не удалось распознать текст в аудио файле.")
            logger.warning(f"[Пользователь {message.from_user.id}] Пустой результат распознавания")

    except Exception as e:
        logger.error(f"[Пользователь {message.from_user.id}] Ошибка при обработке аудио файла: {e}", exc_info=True)
        error_text = "❌ Произошла ошибка при распознавании. Попробуйте еще раз."
        if status_msg:
            try:
                await status_msg.edit_text(error_text)
            except:
                await message.answer(error_text)
        else:
            await message.answer(error_text)


async def main():
    """Запуск бота"""
    try:
        logger.info("Бот запускается...")
        logger.info("Модель Whisper будет загружена при первом запросе")
        await dp.start_polling(bot)
    finally:
        logger.info("Бот завершает работу...")
        executor.shutdown(wait=True)
        logger.info("Executor закрыт")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
