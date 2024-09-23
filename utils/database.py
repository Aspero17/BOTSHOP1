import sqlite3
from typing import List, Dict, Optional

# Функция для подключения к базе данных
def connect_db():
    return sqlite3.connect("data/products.db")

# Функция для инициализации базы данных
def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Создание таблицы категорий, если не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Создание таблицы производителей, если не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manufacturers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    # Создание таблицы товаров, если не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            category_id INTEGER NOT NULL,
            manufacturer_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id)
        )
    ''')

    conn.commit()
    conn.close()

# Функция для получения всех категорий
def get_categories() -> List[str]:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

# Функция для получения производителей по категории
def get_manufacturers_by_category(category: str) -> List[str]:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.name FROM manufacturers m
        JOIN products p ON m.id = p.manufacturer_id
        JOIN categories c ON p.category_id = c.id
        WHERE c.name = ?
        GROUP BY m.name
    """, (category,))
    manufacturers = [row[0] for row in cursor.fetchall()]
    conn.close()
    print(f"Manufacturers for category '{category}': {manufacturers}")  # Debug info
    return manufacturers

# Функция для получения товаров по производителю
def get_products_by_manufacturer(manufacturer: str) -> List[Dict[str, str]]:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.price FROM products p
        JOIN manufacturers m ON p.manufacturer_id = m.id
        WHERE m.name = ?
    """, (manufacturer,))
    products = [{"name": row[0], "price": row[1]} for row in cursor.fetchall()]
    conn.close()
    print(f"Products for manufacturer '{manufacturer}': {products}")  # Debug info
    return products

# Функция для получения товаров по категории
def get_products_by_category(category: str) -> List[Dict[str, str]]:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.price FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE c.name = ?
    """, (category,))
    products = [{"name": row[0], "price": row[1]} for row in cursor.fetchall()]
    conn.close()
    print(f"Products for category '{category}': {products}")  # Debug info
    return products

# Функция для получения товара по его названию
def get_product_by_name(product_name: str) -> Optional[Dict[str, str]]:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.price FROM products p
        WHERE p.name = ?
    """, (product_name,))
    row = cursor.fetchone()
    conn.close()
    print(f"Product with name '{product_name}': {row}")  # Debug info
    return {"name": row[0], "price": row[1]} if row else None

# Основная часть кода
if __name__ == "__main__":
    initialize_db()  # Инициализация базы данных
    print("Database initialized successfully.")
