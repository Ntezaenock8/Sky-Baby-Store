from config import get_db

# ─── USER FUNCTIONS ─────────────────────────────────────

def create_user(name, email, password_hash):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, password_hash)
    )
    db.commit()
    db.close()

def get_user_by_email(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    db.close()
    return user

def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    db.close()
    return user

# ─── PRODUCT FUNCTIONS ──────────────────────────────────

def get_all_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    db.close()
    return products

def get_product_by_id(product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    db.close()
    return product

def add_product(name, description, price, stock, image_url, category):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO products (name, description, price, stock, image_url, category)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (name, description, price, stock, image_url, category)
    )
    db.commit()
    db.close()

# ─── CART FUNCTIONS ─────────────────────────────────────

def get_cart(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT cart.id, cart.quantity, products.name,
               products.price, products.image_url, products.id as product_id
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = %s
    """, (user_id,))
    items = cursor.fetchall()
    db.close()
    return items

def add_to_cart(user_id, product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO cart (user_id, product_id, quantity)
        VALUES (%s, %s, 1)
        ON CONFLICT (user_id, product_id)
        DO UPDATE SET quantity = cart.quantity + 1
    """, (user_id, product_id))
    db.commit()
    db.close()

def remove_from_cart(user_id, product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
        (user_id, product_id)
    )
    db.commit()
    db.close()

def clear_cart(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    db.commit()
    db.close()

# ─── ORDER FUNCTIONS ────────────────────────────────────

def place_order(user_id):
    db = get_db()
    cursor = db.cursor()
    try:
        # Get cart items
        cursor.execute("""
            SELECT cart.quantity, products.price,
                   products.id, products.stock
            FROM cart
            JOIN products ON cart.product_id = products.id
            WHERE cart.user_id = %s
        """, (user_id,))
        cart_items = cursor.fetchall()

        # Calculate total server-side (never trust the frontend)
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        # Create the order
        cursor.execute(
            "INSERT INTO orders (user_id, total, status) VALUES (%s, %s, 'confirmed') RETURNING id",
            (user_id, total)
        )
        order_id = cursor.fetchone()['id']

        # Insert order items and decrement stock
        for item in cart_items:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (order_id, item['id'], item['quantity'], item['price'])
            )
            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE id = %s",
                (item['quantity'], item['id'])
            )

        # Clear the cart
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))

        # Commit everything at once
        db.commit()
        db.close()
        return order_id

    except Exception as e:
        # If anything fails, roll everything back
        db.rollback()
        db.close()
        raise e