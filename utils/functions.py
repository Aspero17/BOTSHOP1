def get_categories():
    """Retrieve all categories from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_name FROM categories")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_manufacturers(category_name):
    """Retrieve manufacturers for a specific category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT manufacturer_name 
        FROM manufacturers 
        WHERE category_id = (
            SELECT category_id 
            FROM categories 
            WHERE category_name = ?
        )
    """, (category_name,))
    manufacturers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return manufacturers

def get_products_by_manufacturer(manufacturer_name):
    """Retrieve products by a specific manufacturer."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_id, product_name, price 
        FROM products 
        WHERE manufacturer_id = (
            SELECT manufacturer_id 
            FROM manufacturers 
            WHERE manufacturer_name = ?
        )
    """, (manufacturer_name,))
    products = cursor.fetchall()
    conn.close()
    return products

def get_products_by_category(category_name):
    """Retrieve products by category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_id, product_name, price 
        FROM products 
        WHERE manufacturer_id IN (
            SELECT manufacturer_id 
            FROM manufacturers 
            WHERE category_id = (
                SELECT category_id 
                FROM categories 
                WHERE category_name = ?
            )
        )
    """, (category_name,))
    products = cursor.fetchall()
    conn.close()
    return products
