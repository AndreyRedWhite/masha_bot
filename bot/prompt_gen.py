import json
import random

def generate_prompt():
    """Генерация случайного промта."""

    with open('data.json') as f:
        data = json.load(f)
    pers = random.choice(data['персонаж'])
    mat = random.choice(data['материал'])
    place = random.choice(data['место'])
    style = random.choice(data['стили'])
    return pers, mat, place, style
    # return f"{format_choice} {material_choice} {subject_choice} {color_choice} {location_choice}"
