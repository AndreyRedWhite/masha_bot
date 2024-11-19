# Используем официальный образ Python
FROM python:3.12-bookworm

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY bot/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код бота
COPY bot/ .

# Команда для запуска бота
CMD ["python", "bot.py"]
