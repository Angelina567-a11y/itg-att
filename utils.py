import json
from datetime import datetime

def сохранить_историю(данные, файл='history.json'):
    try:
        with open(файл, 'w', encoding='utf-8') as f:
            json.dump(данные, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения истории: {e}")

def загрузить_историю(файл='history.json'):
    try:
        with open(файл, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def добавить_в_историю (данные, файл='history.json'):
    история = загрузить_историю(файл)
    история.append(данные)
    сохранить_историю(история, файл)

def валидировать_сумму(значение):
    try:
        число = float(значение)
        return число > 0
    except:
        return False