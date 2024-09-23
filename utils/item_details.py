import json

# Загрузка данных о товарах из файла JSON
def load_items():
    with open('path/to/items.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# Получение деталей товара по его ID
def get_item_details(item_id: str) -> dict:
    items = load_items()
    return items.get(item_id, {"name": "Неизвестный товар", "price": 0})
