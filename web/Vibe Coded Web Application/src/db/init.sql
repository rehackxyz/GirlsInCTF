-- Initialize database schema and data for the CTF

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL DEFAULT 0
);

INSERT INTO products (name, price) VALUES
('Neon Fox Plush', 24.99),
('Cyber Tailcoat', 129.00),
('Photon Katana', 399.99),
('Hologram Snacks', 5.99),
('Vanta Hoodie', 69.00),
('Foxfire Keycap Set', 89.00);

CREATE TABLE IF NOT EXISTS flags (
    id SERIAL PRIMARY KEY,
    flag TEXT NOT NULL
);

INSERT INTO flags (flag) VALUES ('GCTF25{fake}');
