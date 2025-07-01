-- books_simple_drf_init.sql
-- Crea una BD simplificada que convive con `books_db`

/* 1. Base de datos y permisos */
CREATE DATABASE IF NOT EXISTS books_simple_drf_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'example_user'@'%'
IDENTIFIED BY 'example_password';

GRANT ALL PRIVILEGES ON books_simple_drf_db.* TO 'example_user'@'%';
FLUSH PRIVILEGES;

/* 2. Esquema compatible con el modelo FastAPI */
USE books_simple_drf_db;

DROP TABLE IF EXISTS books;

CREATE TABLE books (
    id     CHAR(24)      PRIMARY KEY,
    title  VARCHAR(255)  NOT NULL,
    author VARCHAR(255)  NOT NULL,
    pages  INT           NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* 3. Semilla opcional */
INSERT INTO books (id, title, author, pages) VALUES
  (LPAD(HEX(RANDOM_BYTES(12)),24,'0'), 'Clean Code',               'Robert C. Martin',      464),
  (LPAD(HEX(RANDOM_BYTES(12)),24,'0'), 'Fluent Python',            'Luciano Ramalho',       1014),
  (LPAD(HEX(RANDOM_BYTES(12)),24,'0'), 'Effective Python',         'Brett Slatkin',         256),
  (LPAD(HEX(RANDOM_BYTES(12)),24,'0'), 'The Pragmatic Programmer', 'Andrew Hunt',           320);
