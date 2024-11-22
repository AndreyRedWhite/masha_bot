"""
Модуль для загрузки актуальных данных из бекапа
"""
import json

with open('backup') as f:
    data = json.load(f)

with open('data.json', 'w') as f:
    res = json.dump(data, f, ensure_ascii=False, indent=4)

