import random

# Списки для генерации промтов
formats = ["3D", "фотография", "иллюстрация"]
subjects = ["человека-паука", "робота", "эльфа", "кота", "здания", "древесного духа"]
materials = ["хрустального", "металлического", "стеклянного", "деревянного", "каменного"]
colors = ["красного цвета", "синего цвета", "зелёного цвета", "золотого оттенка", "чёрного цвета"]
locations = ["в Москве", "в Нижневартовске", "в космосе", "в лесу", "на пляже", "в замке"]

def generate_prompt():
    """Генерация случайного промта."""
    format_choice = random.choice(formats)
    subject_choice = random.choice(subjects)
    material_choice = random.choice(materials)
    color_choice = random.choice(colors)
    location_choice = random.choice(locations)
    return f"{format_choice} {material_choice} {subject_choice} {color_choice} {location_choice}"
