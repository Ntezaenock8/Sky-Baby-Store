-- Users table
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    password    TEXT NOT NULL,
    role        VARCHAR(10) DEFAULT 'customer',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    price       NUMERIC(10,2) NOT NULL,
    stock       INTEGER DEFAULT 0,
    image_url   TEXT,
    category    VARCHAR(100)
);

-- Orders table
CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id),
    total       NUMERIC(10,2) NOT NULL,
    status      VARCHAR(20) DEFAULT 'pending',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items table
CREATE TABLE order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER REFERENCES orders(id),
    product_id  INTEGER REFERENCES products(id),
    quantity    INTEGER NOT NULL,
    price       NUMERIC(10,2) NOT NULL
);

-- Cart table (persists between sessions)
CREATE TABLE cart (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id),
    product_id  INTEGER REFERENCES products(id),
    quantity    INTEGER DEFAULT 1,
    UNIQUE(user_id, product_id)
);