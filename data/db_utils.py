import sqlite3

def get_db_connection():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories")
    categories = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_manufacturers(category_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category_id = cursor.fetchone()
    if not category_id:
        conn.close()
        return []
    category_id = category_id['id']
    cursor.execute("SELECT name FROM manufacturers WHERE category_id = ?", (category_id,))
    manufacturers = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return manufacturers

def get_products_by_manufacturer(manufacturer_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM manufacturers WHERE name = ?", (manufacturer_name,))
    manufacturer_id = cursor.fetchone()
    if not manufacturer_id:
        conn.close()
        return []
    manufacturer_id = manufacturer_id['id']
    cursor.execute("SELECT id, name, price FROM products WHERE manufacturer_id = ?", (manufacturer_id,))
    products = cursor.fetchall()
    conn.close()
    return products

def get_products_in_category(category_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category_id = cursor.fetchone()
    if not category_id:
        conn.close()
        return {}
    category_id = category_id['id']
    cursor.execute("SELECT id, name, price, manufacturer_id FROM products WHERE category_id = ?", (category_id,))
    products = cursor.fetchall()
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
    cursor.execute("SELECT name, price, manufacturer_id FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        return None
    cursor.execute("SELECT name FROM manufacturers WHERE id = ?", (product['manufacturer_id'],))
    manufacturer_name = cursor.fetchone()
    conn.close()
    return {
        'name': product['name'],
        'price': product['price'],
        'manufacturer': manufacturer_name['name'] if manufacturer_name else 'Неизвестно'
    }
