import os
import logging
import boto3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputFile
from aiogram.types import InputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from botocore.client import Config
from dotenv import load_dotenv
import aiofiles
from aiogram.types import URLInputFile


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Инициализация бота
session = AiohttpSession()
bot = Bot(token=os.getenv("BOT_TOKEN"), session=session)
dp = Dispatcher()

# Настройка клиента S3 для MinIO
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
    config=Config(signature_version='s3v4')
)

bucket_name = os.getenv("MINIO_BUCKET_NAME")


# Обработчик команды /start
@dp.message(F.text == "/start")
async def send_welcome(message: Message):
    logger.info("Пользователь начал работу с ботом")
    # Создание inline-клавиатуры с кнопками
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Скачать пак с картинками", callback_data="download_images")
    keyboard.button(text="Скачать пак с обоями", callback_data="download_wallpapers")
    await message.answer("Привет! Выберите, что хотите скачать:", reply_markup=keyboard.as_markup())


from aiogram.types import BufferedInputFile

import asyncio
from aiogram.types import BufferedInputFile

import asyncio
from aiogram.types import BufferedInputFile


@dp.callback_query(F.data.in_({"download_images", "download_wallpapers"}))
async def process_callback(callback: CallbackQuery):
    if callback.data == "download_images":
        file_key = "archive.zip"
        logger.info("Пользователь запросил файл: archive.zip")
    elif callback.data == "download_wallpapers":
        file_key = "wallpapers_pack.zip"

    file_path = f"/tmp/{file_key}"

    try:
        # Уведомляем пользователя, что файл готовится к загрузке, и сохраняем ID сообщения
        loading_message = await bot.send_message(callback.from_user.id,
                                                 "Пожалуйста, подождите, ваш файл загружается...")

        # Параллельная загрузка файла из MinIO
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, s3.download_file, bucket_name, file_key, file_path)
        logger.info(f"Файл {file_key} успешно загружен в {file_path}")

        # Обновляем сообщение на "Готово!"
        await bot.edit_message_text("Готово!", chat_id=callback.from_user.id, message_id=loading_message.message_id)

        # Чтение файла в буфер и отправка
        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
            document = BufferedInputFile(file_data, filename=file_key)
            await bot.send_document(callback.from_user.id, document=document)
            logger.info(f"Файл {file_key} успешно отправлен пользователю {callback.from_user.id}")

        # Удаляем файл после отправки
        os.remove(file_path)
        logger.info(f"Файл {file_path} удален после отправки")

    except Exception as e:
        error_message = f"Ошибка при скачивании файла: {e}"
        await bot.send_message(callback.from_user.id, error_message)
        logger.error(error_message)


# Запуск бота
async def main():
    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
