import os
import hashlib
import asyncio
import aiofiles
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BufferedInputFile
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from botocore.client import Config
from dotenv import load_dotenv
import logging
import boto3

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Инициализация бота и диспетчера
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

# Словарь для хранения file_id
file_ids = {}


def calculate_file_hash(file_path):
    """Вычисление хеша для файла."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


async def download_file_from_minio(file_key, file_path):
    """Загрузка файла из MinIO."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, s3.download_file, bucket_name, file_key, file_path)
    logger.info(f"Файл {file_key} успешно загружен в {file_path}")


@dp.message(F.text == "/start")
async def send_welcome(message: Message):
    # Получаем имя и фамилию пользователя
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    # Создание кнопок
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Скачать пак хэллоуин", callback_data="download_images")
    keyboard.button(text="Скачать пак котики", callback_data="download_wallpapers")
    await message.answer(f"Привет, <b>{first_name} {last_name}</b>! Это бот Маши 🤗\nНа данный момент бот позволяет "
                         f"скачивать различные паки с крутыми сгенерированными изображениями 🔥 🔝\nВыбери, что хочешь"
                         f" скачать:", reply_markup=keyboard.as_markup(), parse_mode=ParseMode.HTML)


@dp.callback_query(F.data.in_({"download_images", "download_wallpapers"}))
async def process_callback(callback: CallbackQuery):
    # Подтверждение нажатия, чтобы убрать значок "время" с кнопки
    await callback.answer()

    if callback.data == "download_images":
        file_key = "archive.zip"
        logger.info("Пользователь запросил файл: archive.zip")
    elif callback.data == "download_wallpapers":
        file_key = "wallpapers_pack.zip"

    # Если file_id уже сохранен, используем его для отправки файла напрямую
    if file_key in file_ids:
        await bot.send_document(callback.from_user.id, file_ids[file_key])
        logger.info(f"Файл {file_key} отправлен через file_id пользователю {callback.from_user.id}")
        return

    file_path = f"/tmp/{file_key}"

    try:
        # Уведомляем пользователя о загрузке
        loading_message = await bot.send_message(callback.from_user.id, "Пожалуйста, подождите, файл загружается из "
                                                                        "хранилища...")

        # Проверка актуальности локального файла
        need_download = True
        if os.path.exists(file_path):
            local_file_hash = calculate_file_hash(file_path)
            minio_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
            minio_file_hash = hashlib.md5(minio_obj['Body'].read()).hexdigest()
            if local_file_hash == minio_file_hash:
                logger.info("Локальный файл актуален, загрузка из MinIO не требуется.")
                need_download = False

        # Если нужно, загружаем файл из MinIO
        if need_download:
            await download_file_from_minio(file_key, file_path)

        # Обновляем сообщение на "Готово! Сейчас загрузим его на сервер ТГ и передадим вам, буквально 5-6 секунд..."
        await bot.edit_message_text("Готово! Сейчас загрузим его на сервер Телеграм и передадим вам, буквально 5-6 секунд...",
                                    chat_id=callback.from_user.id, message_id=loading_message.message_id)

        # Чтение файла в буфер и отправка
        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
            document = BufferedInputFile(file_data, filename=file_key)
            sent_message = await bot.send_document(callback.from_user.id, document=document)
            logger.info(f"Файл {file_key} успешно отправлен пользователю {callback.from_user.id}")

            # Сохранение file_id для будущего использования
            file_ids[file_key] = sent_message.document.file_id

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
