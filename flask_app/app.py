from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from dotenv import load_dotenv


# Загрузка переменных из .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# HTTP Basic Auth
auth = HTTPBasicAuth()

# Логин и пароль из переменных окружения
users = {
    os.getenv("FLASK_USERNAME", "admin"): generate_password_hash(
        os.getenv("FLASK_PASSWORD", "default_password")
    )
}

@auth.verify_password
def verify_password(username, password):
    """Проверка логина и пароля"""
    if username in users and check_password_hash(users.get(username), password):
        return username


DATA_FILE = os.getenv("DATA_FILE", "/app/shared_data/data.json")


def load_data():
    """Загрузка данных из data.json"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data):
    """Сохранение данных в data.json"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@app.route("/")
def index():
    """Главная страница"""
    data = load_data()
    return render_template("index.html", data=data)


@app.route("/add_item/<category>", methods=["POST"])
def add_item(category):
    """Добавление элемента в категорию"""
    data = load_data()
    item = request.form.get("item")
    if category in data and item:
        data[category].append(item)
        save_data(data)
        flash(f"Добавлено: {item} в категорию {category}.")
    return redirect(url_for("index"))


@app.route("/delete_item/<category>/<int:index>", methods=["POST"])
def delete_item(category, index):
    """Удаление элемента из категории"""
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