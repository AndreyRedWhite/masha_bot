import json
import random
import os

def generate_prompt():
    """Генерация случайного промта."""

    DATA_FILE = os.getenv("DATA_FILE", "/app/shared_data/data.json")

    with open(DATA_FILE) as f:
        data = json.load(f)
    pers = random.choice(data['персонаж/предмет'])
    mat = random.choice(data['материал'])
    place = random.choice(data['место'])
    style = random.choice(data['стили'])
    return pers, mat, place, style
    # return f"{format_choice} {material_choice} {subject_choice} {color_choice} {location_choice}"
