
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

INSERT INTO products (name, price) VALUES
('Cyber Katana', 199.99),
('Neon Goggles', 79.50),
('Quantum Jacket', 149.95),
('Holo-Gloves', 59.00),
('AI Companion Chip', 999.99),
('Synthwave Sneakers', 129.49),
('Cyberdeck Mk-II', 599.00),
('Augmented Cola', 4.20),
('Retro Cassette', 14.99),
('Drone Buddy', 349.99);


CREATE TABLE secret_flags (
    id SERIAL PRIMARY KEY,
    flag TEXT NOT NULL
);


INSERT INTO secret_flags (flag) VALUES ('GCTF25{fake}');
