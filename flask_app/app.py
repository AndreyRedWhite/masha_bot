import os
import boto3
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from botocore.client import Config

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Настройка MinIO
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
    config=Config(signature_version='s3v4')
)
bucket_name = os.getenv("MINIO_BUCKET_NAME")

# Хранилище для кнопок (временный вариант, можно заменить на базу данных)
buttons = []


@app.route('/')
def index():
    """Главная страница управления"""
    return render_template("index.html", buttons=buttons)


@app.route('/upload', methods=['POST'])
def upload_file():
    """Загрузка архива в MinIO и добавление кнопки в боте"""
    file = request.files['file']
    button_text = request.form['button_text']

    if file and button_text:
        # Загрузка файла в MinIO
        file_key = file.filename
        s3.upload_fileobj(file, bucket_name, file_key)

        # Добавление кнопки
        buttons.append({"text": button_text, "file_key": file_key})

        flash("Файл успешно загружен и кнопка добавлена!")
    else:
        flash("Ошибка: необходимо выбрать файл и задать текст кнопки.")

    return redirect(url_for('index'))


@app.route('/delete_button/<int:button_index>', methods=['POST'])
def delete_button(button_index):
    """Удаление кнопки"""
    try:
        button = buttons.pop(button_index)
        flash(f"Кнопка '{button['text']}' удалена.")
    except IndexError:
        flash("Ошибка: кнопка не найдена.")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
