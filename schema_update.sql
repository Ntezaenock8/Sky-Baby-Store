-- ─── UPDATE PRODUCTS TABLE ─────────────────────────────────
-- Add discount and action columns to existing products table
ALTER TABLE products ADD COLUMN IF NOT EXISTS discount DECIMAL(5,2) DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS action VARCHAR(50);

-- ─── CREATE PRODUCT IMAGES TABLE ────────────────────────────
-- Store up to 3 images per product
CREATE TABLE IF NOT EXISTS product_images (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url   TEXT NOT NULL,
    image_order INTEGER DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id);

-- ─── MIGRATION: Copy existing single image_url to new table ────
-- (Only run if migrating from old schema)
INSERT INTO product_images (product_id, image_url, image_order)
SELECT id, image_url, 1 FROM products 
WHERE image_url IS NOT NULL
ON CONFLICT DO NOTHING;

-- Optional: Remove old image_url column after migration
-- ALTER TABLE products DROP COLUMN image_url;
