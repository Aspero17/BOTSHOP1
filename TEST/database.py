import sqlite3


def initialize_db():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    # Создание таблицы категорий, если не существует
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Создание таблицы производителей, если не существует
    c.execute('''
        CREATE TABLE IF NOT EXISTS manufacturers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    # Создание таблицы товаров, если не существует
    c.execute('''
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


def get_db_connection():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_manufacturers(category_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем идентификатор категории по имени
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category_id = cursor.fetchone()

    if not category_id:
        conn.close()
        return []

    category_id = category_id['id']

    # Получаем производителей для данной категории
    cursor.execute("SELECT name FROM manufacturers WHERE category_id = ?", (category_id,))
    manufacturers = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return manufacturers


def get_products_by_manufacturer(manufacturer_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем идентификатор производителя по имени
    cursor.execute("SELECT id FROM manufacturers WHERE name = ?", (manufacturer_name,))
    manufacturer_id = cursor.fetchone()

    if not manufacturer_id:
        conn.close()
        return []

    manufacturer_id = manufacturer_id['id']

    # Получаем продукты для данного производителя
    cursor.execute("SELECT id, name, price FROM products WHERE manufacturer_id = ?", (manufacturer_id,))
    products = cursor.fetchall()
    conn.close()
    return products


def get_products_in_category(category_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем идентификатор категории по имени
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category_id = cursor.fetchone()

    if not category_id:
        conn.close()
        return {}

    category_id = category_id['id']

    # Получаем все продукты для данной категории
    cursor.execute("SELECT id, name, price, manufacturer_id FROM products WHERE category_id = ?", (category_id,))
    products = cursor.fetchall()

    # Формируем словарь с деталями продуктов
    products_dict = {
        row['id']: {
            'name': row['name'],
            'price': row['price'],
            'manufacturer_id': row['manufacturer_id']
        }
        for row in products
    }
    conn.close()
    return products_dict


def get_product_details_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем детали продукта по его идентификатору
    cursor.execute("SELECT name, price, manufacturer_id FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        return None

    # Получаем название производителя по идентификатору
    cursor.execute("SELECT name FROM manufacturers WHERE id = ?", (product['manufacturer_id'],))
    manufacturer_name = cursor.fetchone()

    conn.close()

    return {
        'name': product['name'],
        'price': product['price'],
        'manufacturer': manufacturer_name['name'] if manufacturer_name else 'Неизвестно'
    }
