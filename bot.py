import os
import boto3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from botocore.client import Config
from dotenv import load_dotenv

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
    # Создание inline-клавиатуры с кнопками
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Скачать пак с картинками", callback_data="download_images")
    keyboard.button(text="Скачать пак с обоями", callback_data="download_wallpapers")
    await message.answer("Привет! Это Бот маши. Выберите, что хотите скачать:", reply_markup=keyboard.as_markup())


# Обработка нажатий на inline-кнопки
@dp.callback_query(F.data.in_({"download_images", "download_wallpapers"}))
async def process_callback(callback: CallbackQuery):
    if callback.data == "download_images":
        file_key = "archive.zip"  # Путь к файлу, который лежит в бакете (пак с картинками)
    elif callback.data == "download_wallpapers":
        file_key = "wallpapers_pack.zip"  # Оставляем, чтобы в будущем добавить второй файл

    file_path = f"/tmp/{file_key}"  # Временный локальный путь для сохранения файла

    try:
        # Загрузка файла из MinIO и отправка пользователю
        s3.download_file(bucket_name, file_key, file_path)
        await bot.send_document(callback.from_user.id, document=open(file_path, 'rb'))
        os.remove(file_path)  # Удаляем файл после отправки
    except Exception as e:
        await bot.send_message(callback.from_user.id, f"Ошибка при скачивании файла: {e}")



# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
