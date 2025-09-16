import sqlite3

# Подключение к базе данных (файл создается автоматически)
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

print("=== СОЗДАНИЕ БАЗЫ ДАННЫХ БИБЛИОТЕКИ ===")

# 1. Создание таблиц с PRIMARY KEY и FOREIGN KEY
print("\n1. Создание таблиц...")

# Таблица авторов
cursor.execute("""
CREATE TABLE IF NOT EXISTS Authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_year INTEGER
)
""")

# Таблица жанров
cursor.execute("""
CREATE TABLE IF NOT EXISTS Genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name TEXT NOT NULL UNIQUE
)
""")

# Таблица читателей
cursor.execute("""
CREATE TABLE IF NOT EXISTS Readers (
    reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    registration_date DATE DEFAULT CURRENT_DATE
)
""")

# Таблица книг
cursor.execute("""
CREATE TABLE IF NOT EXISTS Books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    publication_year INTEGER,
    isbn TEXT UNIQUE,
    FOREIGN KEY (author_id) REFERENCES Authors(author_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE
)
""")

# Таблица выдачи книг
cursor.execute("""
CREATE TABLE IF NOT EXISTS Book_Issues (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    reader_id INTEGER NOT NULL,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (reader_id) REFERENCES Readers(reader_id) ON DELETE CASCADE
)
""")

print("Таблицы успешно созданы!")

# 2. Наполнение таблиц тестовыми данными
print("\n2. Наполнение таблиц тестовыми данными...")

# Добавление авторов
authors_data = [
    ('Лев', 'Толстой', 1828),
    ('Фёдор', 'Достоевский', 1821),
    ('Антон', 'Чехов', 1860),
    ('Александр', 'Пушкин', 1799)
]
cursor.executemany(
    "INSERT INTO Authors (first_name, last_name, birth_year) VALUES (?, ?, ?)",
    authors_data
)

# Добавление жанров
genres_data = [
    ('Роман',),
    ('Рассказ',),
    ('Поэма',),
    ('Драма',)
]
cursor.executemany(
    "INSERT INTO Genres (genre_name) VALUES (?)",
    genres_data
)

# Добавление читателей
readers_data = [
    ('Иван', 'Иванов', 'ivanov@mail.ru'),
    ('Петр', 'Петров', 'petrov@ya.ru'),
    ('Мария', 'Сидорова', 'sidorova@gmail.com'),
    ('Анна', 'Кузнецова', 'kuznetsova@mail.ru')
]
cursor.executemany(
    "INSERT INTO Readers (first_name, last_name, email) VALUES (?, ?, ?)",
    readers_data
)

# Добавление книг
books_data = [
    ('Война и мир', 1, 1, 1869, '978-5-389-07464-0'),
    ('Анна Каренина', 1, 1, 1877, '978-5-389-05327-0'),
    ('Преступление и наказание', 2, 1, 1866, '978-5-389-06227-2'),
    ('Братья Карамазовы', 2, 1, 1880, '978-5-389-07465-7'),
    ('Вишневый сад', 3, 4, 1904, '978-5-389-05328-7'),
    ('Евгений Онегин', 4, 3, 1833, '978-5-389-06228-9')
]
cursor.executemany(
    """INSERT INTO Books (title, author_id, genre_id, publication_year, isbn) 
       VALUES (?, ?, ?, ?, ?)""",
    books_data
)

book_issues_data = [
    (1, 1, '2024-01-15', None),
    (3, 2, '2024-01-20', '2024-02-10'),
    (5, 3, '2024-02-01', None),
    (2, 1, '2024-02-05', None),
    (6, 4, '2024-01-10', '2024-01-25'),
    (4, 2, '2024-02-15', None)
]
cursor.executemany(
    """INSERT INTO Book_Issues (book_id, reader_id, issue_date, return_date) 
       VALUES (?, ?, ?, ?)""",
    book_issues_data
)

conn.commit()
print("Тестовые данные успешно добавлены!")

print("\n3. Выполнение запросов на выборку:")

print("\nа) Список всех книг с авторами и жанрами:")
cursor.execute("""
    SELECT 
        b.title AS Название_книги,
        a.first_name || ' ' || a.last_name AS Автор,
        g.genre_name AS Жанр,
        b.publication_year AS Год_издания
    FROM Books b
    JOIN Authors a ON b.author_id = a.author_id
    JOIN Genres g ON b.genre_id = g.genre_id
    ORDER BY a.last_name, b.title
""")

books = cursor.fetchall()
for book in books:
    print(f"{book[0]} | {book[1]} | {book[2]} | {book[3]}")

print("\nб) Читатели с книгами на руках:")
cursor.execute("""
    SELECT DISTINCT
        r.reader_id,
        r.first_name || ' ' || r.last_name AS Читатель,
        r.email
    FROM Readers r
    JOIN Book_Issues bi ON r.reader_id = bi.reader_id
    WHERE bi.return_date IS NULL
    ORDER BY r.last_name
""")

readers_with_books = cursor.fetchall()
for reader in readers_with_books:
    print(f"ID: {reader[0]} | {reader[1]} | Email: {reader[2]}")

print("\nв) Количество книг по авторам:")
cursor.execute("""
    SELECT 
        a.first_name || ' ' || a.last_name AS Автор,
        COUNT(b.book_id) AS Количество_книг
    FROM Authors a
    LEFT JOIN Books b ON a.author_id = b.author_id
    GROUP BY a.author_id
    ORDER BY Количество_книг DESC
""")

authors_stats = cursor.fetchall()
for author in authors_stats:
    print(f"{author[0]}: {author[1]} книг(и)")

print("\nг) Детальная информация о книгах на руках:")
cursor.execute("""
    SELECT 
        r.first_name || ' ' || r.last_name AS Читатель,
        b.title AS Книга,
        a.first_name || ' ' || a.last_name AS Автор,
        bi.issue_date AS Дата_выдачи
    FROM Book_Issues bi
    JOIN Readers r ON bi.reader_id = r.reader_id
    JOIN Books b ON bi.book_id = b.book_id
    JOIN Authors a ON b.author_id = a.author_id
    WHERE bi.return_date IS NULL
    ORDER BY r.last_name, bi.issue_date
""")

current_issues = cursor.fetchall()
for issue in current_issues:
    print(f"{issue[0]} | {issue[1]} | {issue[2]} | Выдана: {issue[3]}")

# Статистика по базе данных
print("\n=== СТАТИСТИКА БАЗЫ ДАННЫХ ===")
cursor.execute("SELECT COUNT(*) FROM Authors")
print(f"Авторов: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM Books")
print(f"Книг: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM Readers")
print(f"Читателей: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM Book_Issues WHERE return_date IS NULL")
print(f"Книг на руках: {cursor.fetchone()[0]}")

conn.close()
print("\n=== РАБОТА ЗАВЕРШЕНА ===")