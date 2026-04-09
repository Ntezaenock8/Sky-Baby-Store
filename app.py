from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from config import get_db, SECRET_KEY
import bcrypt
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from functools import wraps

# ─── CONFIG ───────────────────────────────────────────

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images', 'products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'jfif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
TOKEN_EXPIRY_DAYS = 30  # Token expires after 30 days

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE  # Flask request size limit
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Session expires after 30 days
app.secret_key = SECRET_KEY

# Token serializer for creating secure tokens
serializer = URLSafeTimedSerializer(SECRET_KEY)

# ─── DB INIT ──────────────────────────────────────────
# Runs on every startup — CREATE TABLE IF NOT EXISTS is safe to repeat
_db = get_db()
_db.autocommit = True
_cur = _db.cursor()
_base = os.path.dirname(__file__)

# Always run schema first (creates tables if missing)
with open(os.path.join(_base, 'schema.sql'), encoding='utf-8-sig') as _f:
    _cur.execute(_f.read())

# Load seed data once if the file exists (one-time migration)
_seed = os.path.join(_base, 'seed_data.sql')
if os.path.exists(_seed):
    with open(_seed, encoding='utf-8') as _f:
        _cur.execute(_f.read())
    print("DB seed data loaded.")

_cur.close()
_db.close()
print("DB schema ready.")

# ─── TOKEN UTILITIES ──────────────────────────────────

def generate_auth_token(user_id):
    """Generate a secure auth token that expires after TOKEN_EXPIRY_DAYS"""
    return serializer.dumps({'user_id': user_id})

def validate_auth_token(token, max_age=TOKEN_EXPIRY_DAYS*24*3600):
    """Validate and retrieve user_id from token"""
    try:
        data = serializer.loads(token, max_age=max_age)
        return data.get('user_id')
    except:
        return None

# ─── AUTO-LOGIN FROM TOKEN ────────────────────────────

@app.before_request
def auto_login_from_token():
    """Check for valid auth token and auto-login user"""
    # Skip auto-login for logout endpoint
    if request.endpoint == 'logout':
        return
    
    # Only check if user is not already logged in
    if 'user_id' not in session:
        auth_token = request.cookies.get('auth_token')
        if auth_token:
            user_id = validate_auth_token(auth_token)
            if user_id:
                # Auto-login user
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT id, name, role FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                db.close()
                
                if user:
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['role'] = user['role']
                    session.permanent = True

# ─── RESPONSE HEADERS FOR SMART CACHING ──────────────────

@app.after_request
def set_cache_headers(response):
    """Prevent ALL HTML pages from being stored in browser cache or bfcache.
    This ensures the back button always makes a fresh server request,
    so a logged-out session can never be restored by going back."""
    if 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# ─── HOME ────────────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    
    # Get category filter
    category = request.args.get('category', None)
    
    # Fetch products with their images
    if category:
        cursor.execute("""
            SELECT p.*, 
                   json_agg(json_build_object('image_url', pi.image_url, 'image_order', pi.image_order) 
                           ORDER BY pi.image_order) FILTER (WHERE pi.image_url IS NOT NULL) as images
            FROM products p
            LEFT JOIN product_images pi ON p.id = pi.product_id
            WHERE p.category = %s
            GROUP BY p.id
            ORDER BY p.id DESC
        """, (category,))
    else:
        cursor.execute("""
            SELECT p.*, 
                   json_agg(json_build_object('image_url', pi.image_url, 'image_order', pi.image_order) 
                           ORDER BY pi.image_order) FILTER (WHERE pi.image_url IS NOT NULL) as images
            FROM products p
            LEFT JOIN product_images pi ON p.id = pi.product_id
            GROUP BY p.id
            ORDER BY p.id DESC
        """)
    
    products = cursor.fetchall()
    
    # Get unique categories
    cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category")
    categories = cursor.fetchall()
    
    db.close()
    
    return render_template('index.html', products=products, categories=categories, selected_category=category)

# ─── API: GET PRODUCTS BY CATEGORY (AJAX) ────────────────

@app.route('/api/products')
def api_get_products():
    """API endpoint for AJAX category filtering - returns JSON"""
    category = request.args.get('category', None)
    
    db = get_db()
    cursor = db.cursor()
    
    if category:
        cursor.execute("""
            SELECT p.*, 
                   json_agg(json_build_object('image_url', pi.image_url, 'image_order', pi.image_order) 
                           ORDER BY pi.image_order) FILTER (WHERE pi.image_url IS NOT NULL) as images
            FROM products p
            LEFT JOIN product_images pi ON p.id = pi.product_id
            WHERE p.category = %s
            GROUP BY p.id
            ORDER BY p.id DESC
        """, (category,))
    else:
        cursor.execute("""
            SELECT p.*, 
                   json_agg(json_build_object('image_url', pi.image_url, 'image_order', pi.image_order) 
                           ORDER BY pi.image_order) FILTER (WHERE pi.image_url IS NOT NULL) as images
            FROM products p
            LEFT JOIN product_images pi ON p.id = pi.product_id
            GROUP BY p.id
            ORDER BY p.id DESC
        """)
    
    products = cursor.fetchall()
    db.close()
    
    # Convert to list of dicts for JSON
    products_list = [dict(p) for p in products]
    return jsonify({'products': products_list, 'category': category})

# ─── FAQ ─────────────────────────────────────────────────

@app.route('/faq')
def faq():
    return render_template('faq.html')

# ─── SITEMAP ─────────────────────────────────────────────

@app.route('/sitemap')
def sitemap():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category")
    categories = cursor.fetchall()
    db.close()
    return render_template('sitemap.html', categories=categories)

# ─── REGISTER ────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']

        # Hash the password before saving
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        db = get_db()
        cursor = db.cursor()

        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()

        if existing:
            flash('Email already registered. Please log in.', 'danger')
            db.close()
            return redirect(url_for('login'))

        # Save new user
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed.decode('utf-8'))
        )
        db.commit()
        db.close()

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ─── LOGIN ───────────────────────────────────────────────

@app.route('/api/auth-status')
def auth_status():
    """Lightweight endpoint for the client to verify current session state."""
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'user': session.get('user_name')})
    return jsonify({'logged_in': False})

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Already logged in — go home
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        db.close()

        # Check user exists and password matches
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            session.permanent = True

            # Generate auth token and set as cookie (lasts 30 days)
            token = generate_auth_token(user['id'])
            response = make_response(redirect(url_for('index') if user['role'] != 'admin' else url_for('admin_dashboard')))
            response.set_cookie(
                'auth_token',
                token,
                max_age=TOKEN_EXPIRY_DAYS * 24 * 3600,  # 30 days in seconds
                secure=False,  # Set to True if using HTTPS in production
                httponly=True,  # Prevent JavaScript access for security
                samesite='Lax'
            )

            # Merge guest cart into user cart on login
            merge_guest_cart(user['id'])

            flash(f"Welcome back {user['name']}!", 'success')
            
            return response
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# ─── LOGOUT ──────────────────────────────────────────────

@app.route('/logout')
def logout():
    user_name = session.get('user_name', 'Guest')
    user_id = session.get('user_id', None)
    session.clear()
    
    flash(f'{user_name}, you have been logged out successfully.', 'info')
    
    # Create response and clear auth token
    response = make_response(redirect(url_for('index')))
    response.set_cookie('auth_token', '', max_age=0)  # Delete the cookie
    
    # Add headers to prevent back button from showing cached authenticated content
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

# ─── API: SESSION STATUS ─────────────────────────────────

@app.route('/api/session')
def api_session():
    """API endpoint to check session status (for frontend validation)"""
    is_logged_in = session.get('user_id') is not None
    return jsonify({
        'is_logged_in': is_logged_in,
        'user_name': session.get('user_name', None),
        'user_id': session.get('user_id', None),
        'role': session.get('role', None)
    })

# ─── PRODUCT DETAIL ──────────────────────────────────────

@app.route('/product/<int:product_id>')
def product(product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.*,
               json_agg(json_build_object('image_url', pi.image_url, 'image_order', pi.image_order)
                       ORDER BY pi.image_order) FILTER (WHERE pi.image_url IS NOT NULL) as images
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE p.id = %s
        GROUP BY p.id
    """, (product_id,))
    product = cursor.fetchone()
    db.close()
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('product.html', product=product)

# ─── CART ────────────────────────────────────────────────

@app.route('/cart')
def cart():
    if session.get('role') == 'admin':
        flash('Admins cannot access the shopping cart.', 'warning')
        return redirect(url_for('index'))
    if 'user_id' in session:
        # Logged in — get cart from database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT cart.id, cart.quantity, products.name,
                   products.price, products.image_url, products.id as product_id
            FROM cart
            JOIN products ON cart.product_id = products.id
            WHERE cart.user_id = %s
        """, (session['user_id'],))
        items = cursor.fetchall()
        db.close()
    else:
        # Guest — get cart from session
        items = session.get('guest_cart', [])

    total = sum(item['price'] * item['quantity'] for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/cart/add/<int:product_id>')
def add_to_cart(product_id):
    if session.get('role') == 'admin':
        flash('Admins cannot add products to a cart.', 'warning')
        return redirect(url_for('index'))
    if 'user_id' in session:
        # Logged in — save to database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id, product_id)
            DO UPDATE SET quantity = cart.quantity + 1
        """, (session['user_id'], product_id))
        db.commit()
        db.close()
    else:
        # Guest — save to session
        guest_cart = session.get('guest_cart', [])
        for item in guest_cart:
            if item['product_id'] == product_id:
                item['quantity'] += 1
                break
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            db.close()
            guest_cart.append({
                'product_id': product_id,
                'name': product['name'],
                'price': float(product['price']),
                'image_url': product['image_url'],
                'quantity': 1
            })
        session['guest_cart'] = guest_cart

    flash('Item added to cart.', 'success')
    return redirect(url_for('cart'))

@app.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart_quantity(product_id):
    if session.get('role') == 'admin':
        return redirect(url_for('index'))

    change = int(request.form.get('change', 0))

    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s",
            (session['user_id'], product_id)
        )
        row = cursor.fetchone()
        if row:
            new_qty = row['quantity'] + change
            if new_qty <= 0:
                cursor.execute(
                    "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
                    (session['user_id'], product_id)
                )
            else:
                cursor.execute(
                    "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
                    (new_qty, session['user_id'], product_id)
                )
            db.commit()
        db.close()
    else:
        guest_cart = session.get('guest_cart', [])
        updated = []
        for item in guest_cart:
            if item['product_id'] == product_id:
                item['quantity'] += change
                if item['quantity'] > 0:
                    updated.append(item)
            else:
                updated.append(item)
        session['guest_cart'] = updated

    return redirect(url_for('cart'))


@app.route('/cart/empty')
def empty_cart():
    if session.get('role') == 'admin':
        return redirect(url_for('index'))
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (session['user_id'],))
        db.commit()
        db.close()
    else:
        session['guest_cart'] = []
    flash('Your cart has been emptied.', 'info')
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
            (session['user_id'], product_id)
        )
        db.commit()
        db.close()
    else:
        guest_cart = session.get('guest_cart', [])
        session['guest_cart'] = [i for i in guest_cart if i['product_id'] != product_id]

    return redirect(url_for('cart'))

# ─── CART MERGE (guest → logged in user) ─────────────────

def merge_guest_cart(user_id):
    guest_cart = session.get('guest_cart', [])
    if not guest_cart:
        return

    db = get_db()
    cursor = db.cursor()
    for item in guest_cart:
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, product_id)
            DO UPDATE SET quantity = cart.quantity + EXCLUDED.quantity
        """, (user_id, item['product_id'], item['quantity']))
    db.commit()
    db.close()

    # Clear guest cart from session after merging
    session.pop('guest_cart', None)

# ─── CHECKOUT ────────────────────────────────────────────

@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        flash('Please log in to checkout.', 'warning')
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT cart.quantity, products.name, products.price,
               products.id as product_id
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = %s
    """, (session['user_id'],))
    items = cursor.fetchall()
    db.close()

    total = sum(item['price'] * item['quantity'] for item in items)
    
    response = make_response(render_template('checkout.html', items=items, total=total))
    
    # Add no-cache headers to prevent back button from showing this page
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    try:
        # Get cart from database
        cursor.execute("""
            SELECT cart.quantity, products.price, products.id, products.stock
            FROM cart
            JOIN products ON cart.product_id = products.id
            WHERE cart.user_id = %s
        """, (user_id,))
        cart_items = cursor.fetchall()

        # Calculate total server-side
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        # Create order
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
        return redirect(url_for('order_confirm', order_id=order_id))

    except Exception as e:
        db.rollback()
        db.close()
        flash('Something went wrong. Your order was not placed.', 'danger')
        return redirect(url_for('cart'))

# ─── ORDER CONFIRMATION ───────────────────────────────────

@app.route('/order_confirm/<int:order_id>')
def order_confirm(order_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT order_items.quantity, order_items.price,
               products.name, orders.total, orders.created_at
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        JOIN orders ON order_items.order_id = orders.id
        WHERE order_items.order_id = %s
    """, (order_id,))
    items = cursor.fetchall()
    db.close()
    
    response = make_response(render_template('order_confirm.html', items=items, order_id=order_id))
    
    # Add no-cache headers to prevent back button from showing this page
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

# ─── ADMIN ───────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access only.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return result dict with success and url/message"""
    if not file or file.filename == '':
        return {'success': False, 'message': 'No file selected'}
    
    # Check file extension
    if not allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'
        return {'success': False, 'message': f'File type .{ext} not allowed. Use: png, jpg, jpeg, gif, webp'}
    
    # Check file size before saving
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        return {'success': False, 'message': f'File too large ({size_mb:.1f}MB). Max: {max_mb:.0f}MB'}
    
    try:
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = secure_filename(timestamp + file.filename)
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Return URL path
        url = url_for('static', filename=f'images/products/{filename}')
        return {'success': True, 'url': url}
    except Exception as e:
        return {'success': False, 'message': f'Save error: {str(e)}'}

@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.execute("SELECT orders.id, orders.total, orders.status, users.name FROM orders JOIN users ON orders.user_id = users.id ORDER BY orders.created_at DESC")
    orders = cursor.fetchall()
    db.close()
    return render_template('admin/dashboard.html', products=products, orders=orders)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        name        = request.form['name']
        description = request.form['description']
        price       = request.form['price']
        stock       = request.form['stock']
        category    = request.form['category']
        action      = request.form.get('action', None)
        discount    = request.form.get('discount', 0)

        db = get_db()
        cursor = db.cursor()
        
        try:
            # Insert product
            cursor.execute(
                """INSERT INTO products (name, description, price, stock, category, action, discount) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (name, description, price, stock, category, action, discount)
            )
            product_id = cursor.fetchone()['id']

            # Handle up to 3 image uploads
            image_count = 0
            error_messages = []
            for i in range(1, 4):  # Images 1, 2, 3
                file_key = f'image_{i}'
                
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename != '':
                        result = save_uploaded_file(file)
                        if result['success']:
                            cursor.execute(
                                """INSERT INTO product_images (product_id, image_url, image_order) 
                                   VALUES (%s, %s, %s)""",
                                (product_id, result['url'], image_count + 1)
                            )
                            image_count += 1
                        else:
                            error_messages.append(f"Image {i}: {result['message']}")
            
            # If no files uploaded, check for image URLs
            if image_count == 0:
                for i in range(1, 4):
                    url_key = f'image_url_{i}'
                    image_url = request.form.get(url_key, '').strip()
                    if image_url:
                        cursor.execute(
                            """INSERT INTO product_images (product_id, image_url, image_order) 
                               VALUES (%s, %s, %s)""",
                            (product_id, image_url, image_count + 1)
                        )
                        image_count += 1

            db.commit()
            db.close()
            
            # Show success message with any warnings
            if error_messages and image_count == 0:
                flash(f'Product added but image uploads failed: {" | ".join(error_messages)}', 'warning')
            elif error_messages:
                flash(f'Product added with {image_count} image(s). Skipped: {" | ".join(error_messages)}', 'info')
            else:
                flash(f'Product added successfully with {image_count} image(s).', 'success')
            
            return redirect(url_for('admin_dashboard'))
        
        except Exception as e:
            db.rollback()
            db.close()
            flash(f'Error adding product: {str(e)}', 'danger')
            return redirect(url_for('admin_add_product'))

    return render_template('admin/products.html')

@app.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    """Delete a product and all its images"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get product to delete associated images
        cursor.execute("SELECT name FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        # Delete associated images from filesystem
        cursor.execute("SELECT image_url FROM product_images WHERE product_id = %s", (product_id,))
        images = cursor.fetchall()
        
        for img in images:
            if img['image_url']:
                filename = img['image_url'].split('/')[-1]
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except:
                    pass  # Continue even if file deletion fails
        
        # Remove from active carts
        cursor.execute("DELETE FROM cart WHERE product_id = %s", (product_id,))
        
        # Remove from order history (detach from past orders)
        cursor.execute("DELETE FROM order_items WHERE product_id = %s", (product_id,))
        
        # Delete from database (cascade will delete product_images)
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        db.commit()
        db.close()
        
        flash(f'Product "{product["name"]}" deleted successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    
    except Exception as e:
        db.rollback()
        db.close()
        flash(f'Error deleting product: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/product/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    """Edit an existing product"""
    db = get_db()
    cursor = db.cursor()
    
    # Get product
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        name        = request.form['name']
        description = request.form['description']
        price       = request.form['price']
        stock       = request.form['stock']
        category    = request.form['category']
        action      = request.form.get('action', None)
        discount    = request.form.get('discount', product['discount'] or 0)
        
        try:
            # Update product
            cursor.execute(
                """UPDATE products SET name=%s, description=%s, price=%s, stock=%s, 
                   category=%s, action=%s, discount=%s WHERE id=%s""",
                (name, description, price, stock, category, action, discount, product_id)
            )
            
            # Handle image uploads
            error_messages = []
            for i in range(1, 4):
                file_key = f'image_{i}'
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename != '':
                        result = save_uploaded_file(file)
                        if result['success']:
                            # Delete old image if exists
                            cursor.execute(
                                "SELECT image_url FROM product_images WHERE product_id=%s AND image_order=%s",
                                (product_id, i)
                            )
                            old_img = cursor.fetchone()
                            if old_img and old_img['image_url']:
                                try:
                                    filepath = os.path.join(UPLOAD_FOLDER, old_img['image_url'].split('/')[-1])
                                    if os.path.exists(filepath):
                                        os.remove(filepath)
                                except:
                                    pass
                                # Delete from database
                                cursor.execute(
                                    "DELETE FROM product_images WHERE product_id=%s AND image_order=%s",
                                    (product_id, i)
                                )
                            
                            # Insert new image
                            cursor.execute(
                                """INSERT INTO product_images (product_id, image_url, image_order) 
                                   VALUES (%s, %s, %s)""",
                                (product_id, result['url'], i)
                            )
                        else:
                            error_messages.append(f"Image {i}: {result['message']}")
            
            db.commit()
            db.close()
            
            if error_messages:
                flash(f'Product updated. Warnings: {" | ".join(error_messages)}', 'info')
            else:
                flash(f'Product "{name}" updated successfully.', 'success')
            
            return redirect(url_for('admin_dashboard'))
        
        except Exception as e:
            db.rollback()
            db.close()
            flash(f'Error updating product: {str(e)}', 'danger')
            return redirect(url_for('edit_product', product_id=product_id))
    
    # GET request - show edit form
    cursor.execute(
        """SELECT id, image_url, image_order FROM product_images 
           WHERE product_id = %s ORDER BY image_order""",
        (product_id,)
    )
    images = cursor.fetchall()
    db.close()
    
    return render_template('admin/edit_product.html', product=product, images=images)

@app.route('/admin/order/<int:order_id>/update', methods=['POST'])
@admin_required
def update_order_status(order_id):
    status = request.form['status']
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE orders SET status = %s WHERE id = %s",
        (status, order_id)
    )
    db.commit()
    db.close()
    flash('Order status updated.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.context_processor
def inject_cart_count():
    count = 0
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT SUM(quantity) as total FROM cart WHERE user_id = %s",
            (session['user_id'],)
        )
        result = cursor.fetchone()
        db.close()
        count = result['total'] if result['total'] else 0
    return dict(cart_count=count)

# ─── RUN ─────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)