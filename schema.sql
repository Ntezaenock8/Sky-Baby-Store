-- Sky Baby Store - Full Database Schema
-- Reflects the current live PostgreSQL database structure.
-- Run this on a fresh database to recreate everything from scratch.

-- USERS
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100)        NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    password    TEXT                NOT NULL,
    role        VARCHAR(10)         DEFAULT 'customer',
    created_at  TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
);

-- PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200)        NOT NULL,
    description TEXT,
    price       NUMERIC(10,2)       NOT NULL,
    stock       INTEGER             DEFAULT 0,
    image_url   TEXT,
    category    VARCHAR(100),
    discount    DECIMAL(5,2)        DEFAULT 0,
    action      VARCHAR(50)
);

-- PRODUCT IMAGES
CREATE TABLE IF NOT EXISTS product_images (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url   TEXT    NOT NULL,
    image_order INTEGER DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id);

-- ORDERS
CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER       REFERENCES users(id),
    total       NUMERIC(10,2) NOT NULL,
    status      VARCHAR(20)   DEFAULT 'pending',
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- ORDER ITEMS
CREATE TABLE IF NOT EXISTS order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER       REFERENCES orders(id),
    product_id  INTEGER       REFERENCES products(id),
    quantity    INTEGER       NOT NULL,
    price       NUMERIC(10,2) NOT NULL
);

-- CART
CREATE TABLE IF NOT EXISTS cart (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id),
    product_id  INTEGER REFERENCES products(id),
    quantity    INTEGER DEFAULT 1,
    UNIQUE(user_id, product_id)
);

-- AUDIT LOG
CREATE TABLE IF NOT EXISTS audit_log (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER   REFERENCES users(id),
    action     TEXT      NOT NULL,
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
