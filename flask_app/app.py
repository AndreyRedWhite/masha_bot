from flask import Flask, render_template, request, redirect, flash, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import json

# Загрузка переменных окружения
load_dotenv()

# Инициализация приложения и секретного ключа
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Инициализация HTTP Basic Auth
auth = HTTPBasicAuth()

# Настройка пользователей для авторизации
users = {
    os.getenv("FLASK_USERNAME", "admin"): generate_password_hash(
        os.getenv("FLASK_PASSWORD", "secure_password_here")
    )
}


@auth.verify_password
def verify_password(username, password):
    """Проверка логина и пароля"""
    if username in users and check_password_hash(users.get(username), password):
        return username


# Путь к файлу данных
DATA_FILE = os.getenv("DATA_FILE", "/app/shared_data/data.json")


def load_data():
    """Загрузка данных из файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data):
    """Сохранение данных в файл"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@app.route('/')
@auth.login_required
def index():
    """Главная страница"""
    data = load_data()
    counters = {category: len(items) for category, items in data.items()}  # Подсчёт элементов в каждой категории
    return render_template("index.html", data=data, counters=counters)


@app.route('/add_item/<category>', methods=['POST'])
@auth.login_required
def add_item(category):
    """Добавление элемента"""
    data = load_data()
    item = request.form.get("item")
    if category in data and item:
        data[category].append(item)
        save_data(data)
        flash(f"Добавлено: {item} в категорию {category}.")
    else:
        flash("Ошибка: категория не найдена или элемент пустой.")
    return redirect(url_for("index"))


@app.route('/delete_item/<category>/<int:index>', methods=['POST'])
@auth.login_required
def delete_item(category, index):
    """Удаление элемента"""
    data = load_data()
    try:
        removed_item = data[category].pop(index)
        save_data(data)
        flash(f"Удалено: {removed_item} из категории {category}.")
    except (IndexError, KeyError):
        flash("Ошибка при удалении.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
