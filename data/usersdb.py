import sqlite3
import json
from typing import Optional, List, Dict
from datetime import datetime

DATABASE_PATH = '/data/users.db'

# Функция для создания таблиц пользователей, заказов и корзины
def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Создаем таблицу пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        additional_phones TEXT DEFAULT '[]'
    )
    ''')

    # Создаем таблицу заказов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        order_time TEXT NOT NULL,
        order_details TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # Создаем таблицу корзины
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        PRIMARY KEY (user_id, item_id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

# Функция для добавления столбца additional_phones, если он отсутствует
def add_additional_phones_column():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Добавляем столбец additional_phones, если он не существует
    try:
        cursor.execute('''
        ALTER TABLE users
        ADD COLUMN additional_phones TEXT DEFAULT '[]'
        ''')
    except sqlite3.OperationalError:
        pass  # Если столбец уже существует, игнорируем ошибку

    conn.commit()
    conn.close()

# Функция для добавления нового пользователя
def add_user(user_id: int, name: str, phone: str, address: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO users (id, name, phone, address) VALUES (?, ?, ?, ?)
    ''', (user_id, name, phone, address))

    conn.commit()
    conn.close()

# Функция для проверки, зарегистрирован ли пользователь
def is_user_registered(user_id: int) -> bool:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    conn.close()
    return user is not None

# Функция для получения информации о пользователе
def get_user_info(user_id: int) -> Dict[str, Optional[str]]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT name, phone, address, additional_phones FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        name, phone, address, additional_phones_str = result
        try:
            additional_phones = json.loads(additional_phones_str) if additional_phones_str else []
        except json.JSONDecodeError:
            additional_phones = []  # Если JSON некорректен, возвращаем пустой список

        user_info = {
            'name': name,
            'phone': phone,
            'address': address,
            'additional_phones': additional_phones
        }

        print(f"DEBUG: Загруженные данные для пользователя {user_id}: {user_info}")  # Отладочный вывод

        return user_info
    return {}

# Функция для обновления информации о пользователе
def update_user(user_id: int, name: Optional[str] = None, phone: Optional[str] = None,
                address: Optional[str] = None, additional_phones: Optional[List[str]] = None):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Получаем текущие данные пользователя
    cursor.execute('SELECT additional_phones FROM users WHERE id = ?', (user_id,))
    current_additional_phones_str = cursor.fetchone()[0] or "[]"

    try:
        current_additional_phones = json.loads(current_additional_phones_str)
    except json.JSONDecodeError:
        current_additional_phones = []  # Если JSON некорректен, используем пустой список

    if additional_phones is not None:
        current_additional_phones = additional_phones

    # Обновляем информацию о пользователе
    cursor.execute('''
    UPDATE users
    SET name = COALESCE(?, name),
        phone = COALESCE(?, phone),
        address = COALESCE(?, address),
        additional_phones = ?
    WHERE id = ?
    ''', (name, phone, address, json.dumps(current_additional_phones), user_id))

    conn.commit()
    conn.close()

# Функция для добавления заказа в базу данных
def save_order_to_db(user_id: int, order_details: str):
    # Подключаемся к базе данных
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Получаем текущее время для записи времени заказа
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Выполняем SQL-запрос для вставки нового заказа в базу данных
    cursor.execute('''
        INSERT INTO orders (user_id, order_time, order_details)
        VALUES (?, ?, ?)
    ''', (user_id, order_time, order_details))

    # Подтверждаем изменения и закрываем соединение с базой данных
    conn.commit()
    conn.close()


def get_order_history_from_db(user_id: int) -> List[Dict[str, str]]:
    # Подключаемся к базе данных
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Выполняем SQL-запрос для получения истории заказов пользователя
    cursor.execute('''
        SELECT order_time, order_details 
        FROM orders 
        WHERE user_id = ? 
        ORDER BY order_time DESC
    ''', (user_id,))

    # Извлекаем результаты и закрываем соединение
    orders = cursor.fetchall()
    conn.close()

    # Преобразуем результаты в список словарей
    return [{'time': order[0], 'details': order[1]} for order in orders]

def get_cart(user_id: int) -> Dict[int, Dict[str, any]]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT item_id, item_name, quantity, price
    FROM cart WHERE user_id = ?
    ''', (user_id,))
    items = cursor.fetchall()

    print("DEBUG: Items fetched from database:", items)  # Отладочный вывод

    conn.close()

    cart = {}
    for item in items:
        item_id, name, quantity, price = item
        cart[item_id] = {
            'name': name,
            'quantity': quantity,
            'price': price
        }
    return cart


def update_cart(user_id: int, item_id: int, item_name: str, quantity: int, price: float):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Получаем текущее количество товара
    cursor.execute('SELECT quantity FROM cart WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    result = cursor.fetchone()
    current_quantity = result[0] if result else 0

    new_quantity = current_quantity + quantity
    if new_quantity <= 0:
        # Удаляем элемент, если количество становится 0 или меньше
        cursor.execute('DELETE FROM cart WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    else:
        # Обновляем количество товара
        cursor.execute('''
        INSERT INTO cart (user_id, item_id, item_name, quantity, price)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, item_id)
        DO UPDATE SET quantity = excluded.quantity, price = excluded.price
        ''', (user_id, item_id, item_name, new_quantity, price))

    conn.commit()
    conn.close()

    print(f"DEBUG: Cart updated for user {user_id}, item {item_id} - new quantity {new_quantity}")


# Функция для удаления конкретного элемента из корзины
async def clear_cart_item(user_id: int):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))

    conn.commit()
    conn.close()

    print(f"DEBUG: Cart cleared for user {user_id}")

# Инициализация базы данных
def initialize_users_db():
    create_tables()
    add_additional_phones_column()
