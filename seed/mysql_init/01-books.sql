CREATE DATABASE IF NOT EXISTS books_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON books_db.* TO 'example_user'@'%';

USE books_db;

-- Limpiar tablas anteriores
DROP TABLE IF EXISTS books_genres;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS genres;

-- Tabla de autores
CREATE TABLE authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Tabla de géneros
CREATE TABLE genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla de libros
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT NOT NULL,
    pages INT DEFAULT 0,
    year INT NOT NULL,
    price DECIMAL(6,2) NOT NULL DEFAULT 10.00,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

-- Relación muchos a muchos: libros ↔ géneros
CREATE TABLE books_genres (
    book_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

-- Insert autores
INSERT INTO authors (name) VALUES
    ('Robert C. Martin'),
    ('Luciano Ramalho'),
    ('Dan Bader'),
    ('Brett Slatkin'),
    ('Alan Beaulieu'),
    ('Andy Hunt'),
    ('J.K. Rowling');

-- Insert géneros
INSERT INTO genres (name) VALUES
    ('Programming'),
    ('Databases'),
    ('Fantasy'),
    ('Python');

-- Insert libros
INSERT INTO books (title, author_id, pages, year, price) VALUES
  ('Clean Code',             (SELECT id FROM authors WHERE name = 'Robert C. Martin'),    464, 2008, 35.50),
  ('Fluent Python',          (SELECT id FROM authors WHERE name = 'Luciano Ramalho'),    1014, 2015, 42.00),
  ('Python Tricks',          (SELECT id FROM authors WHERE name = 'Dan Bader'),           302, 2017, 25.00),
  ('Effective Python',       (SELECT id FROM authors WHERE name = 'Brett Slatkin'),       256, 2015, 30.00),
  ('Learning SQL',           (SELECT id FROM authors WHERE name = 'Alan Beaulieu'),       350, 2009, 22.50),
  ('The Pragmatic Programmer', (SELECT id FROM authors WHERE name = 'Andy Hunt'),         320, 1999, 40.00),
  ('Harry Potter y la piedra filosofal', (SELECT id FROM authors WHERE name = 'J.K. Rowling'), 309, 1997, 19.99),
  ('Harry Potter y la cámara secreta',   (SELECT id FROM authors WHERE name = 'J.K. Rowling'), 341, 1998, 21.50),
  ('Harry Potter y el prisionero de Azkaban', (SELECT id FROM authors WHERE name = 'J.K. Rowling'), 435, 1999, 23.00);

-- Insert relación libros ↔ géneros
INSERT INTO books_genres (book_id, genre_id)
SELECT b.id, g.id FROM books b JOIN genres g ON
    (b.title = 'Clean Code' AND g.name = 'Programming') OR
    (b.title = 'Fluent Python' AND g.name IN ('Programming', 'Python')) OR
    (b.title = 'Python Tricks' AND g.name IN ('Programming', 'Python')) OR
    (b.title = 'Effective Python' AND g.name = 'Python') OR
    (b.title = 'Learning SQL' AND g.name = 'Databases') OR
    (b.title = 'The Pragmatic Programmer' AND g.name = 'Programming') OR
    (b.title LIKE 'Harry Potter%' AND g.name = 'Fantasy');
