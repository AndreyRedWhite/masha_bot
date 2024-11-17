import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import logging
from prompt_gen import generate_prompt  # Импорт функции генерации промта

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Обработчик команды /start
@dp.message(F.text == "/start")
async def send_welcome(message: Message):
    # Получаем имя и фамилию пользователя
    first_name = message.from_user.first_name or "Гость"
    last_name = message.from_user.last_name or ""

    # Создание кнопки "Дай задание"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Дай задание!", callback_data="generate_prompt")]]
    )

    # Приветственное сообщение
    welcome_text = (
        f"Привет,<b>{first_name} {last_name}</b>! 👋\n\n"
        "Этот бот создан, чтобы помочь тебе развивать воображение и учиться создавать креативные работы в MidJourney.\n\n"
        "🎯 <b>Что я умею?</b>\n"
        "Я генерирую задания, которые станут основой для ярких и точных промптов. Нажми кнопку, и я выберу:\n\n"
        "📌 Формат изображения.\n"
        "📌 Персонажа или предмет.\n"
        "📌 Описание материала или стиля.\n"
        "📌 Место действия.\n\n"
        "💡 <b>Твоя задача:</b>\n"
        "Составь промпт на основе этих данных и прокачай свои навыки генерации!\n\n"
        "Нажимай <b>«Дай задание!»</b>, чтобы начать! 🚀"
    )

    # Отправка приветствия
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# Обработчик нажатия кнопки "Дай задание!"
@dp.callback_query(F.data == "generate_prompt")
async def process_generate_prompt(callback: CallbackQuery):
    # Генерация случайного промта
    prompt = generate_prompt()
    # Отправка промта пользователю
    await callback.message.answer(f"Вот твое задание: <b>{prompt}</b>", parse_mode=ParseMode.HTML)
    # Подтверждение нажатия
    await callback.answer()

# Запуск бота
async def main():
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
