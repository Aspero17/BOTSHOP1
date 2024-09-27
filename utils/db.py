import sqlite3

def get_db_connection():
    conn = sqlite3.connect("data/products.db")
    return conn

def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = cursor.fetchall()
    conn.close()
    return [category[0] for category in categories]

def get_manufacturers_by_category(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT manufacturer FROM products WHERE category=?", (category,))
    manufacturers = cursor.fetchall()
    conn.close()
    return [manufacturer[0] for manufacturer in manufacturers]

def get_products_by_category(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products WHERE category=?", (category,))
    products = cursor.fetchall()
    conn.close()
    return [{'name': product[0], 'price': product[1]} for product in products]

# Добавьте функции для изменения наименования и цены товара
