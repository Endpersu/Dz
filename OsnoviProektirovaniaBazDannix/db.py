import sqlite3
from datetime import datetime

def create_blog_database():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        print("База данных блога успешно создана!")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Ошибка при создании БД: {e}")
    finally:
        conn.close()

def get_connection():
    """Создает и возвращает соединение с базой данных"""
    conn = sqlite3.connect('blog.db')
    # Включаем поддержку внешних ключей
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def add_user(username, email):
    """
    Добавляет нового пользователя в базу данных
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (username, email)
        )
        conn.commit()
        print(f"Пользователь '{username}' успешно добавлен!")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print("Ошибка: пользователь с таким именем или email уже существует")
        return None
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Ошибка при добавлении пользователя: {e}")
        return None
    finally:
        conn.close()

def create_post(title, content, user_id, category_id):
    """
    Создает новый пост в блоге
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            print("Ошибка: пользователь не существует")
            return None
        
        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            print("Ошибка: категория не существует")
            return None
        
        cursor.execute(
            """INSERT INTO posts (title, content, user_id, category_id) 
               VALUES (?, ?, ?, ?)""",
            (title, content, user_id, category_id)
        )
        conn.commit()
        print(f"Пост '{title}' успешно создан!")
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Ошибка при создании поста: {e}")
        return None
    finally:
        conn.close()

def get_all_posts_with_authors():
    """
    Возвращает все посты с информацией об авторах и категориях
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                p.id, 
                p.title, 
                p.content, 
                p.created_at,
                u.username as author,
                c.name as category
            FROM posts p
            JOIN users u ON p.user_id = u.id
            JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
        """)
        
        posts = cursor.fetchall()
        
        if not posts:
            print("В блоге пока нет постов")
            return []
        
        print("\n=== ВСЕ ПОСТЫ В БЛОГЕ ===\n")
        for post in posts:
            post_id, title, content, created_at, author, category = post
            print(f"ID: {post_id}")
            print(f"Заголовок: {title}")
            print(f"Автор: {author}")
            print(f"Категория: {category}")
            print(f"Дата: {created_at}")
            print(f"Содержание: {content[:100]}..." if len(content) > 100 else f"Содержание: {content}")
            print("-" * 50)
        
        return posts
    except sqlite3.Error as e:
        print(f"Ошибка при получении постов: {e}")
        return []
    finally:
        conn.close()

def add_category(name):
    """Добавляет новую категорию"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Категория '{name}' успешно добавлена!")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print("Ошибка: категория с таким названием уже существует")
        return None
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Ошибка при добавлении категории: {e}")
        return None
    finally:
        conn.close()

def add_comment(text, post_id, user_id):
    """Добавляет комментарий к посту"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """INSERT INTO comments (text, post_id, user_id) 
               VALUES (?, ?, ?)""",
            (text, post_id, user_id)
        )
        conn.commit()
        print("Комментарий успешно добавлен!")
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Ошибка при добавлении комментария: {e}")
        return None
    finally:
        conn.close()

def populate_test_data():
    """Заполняет базу данных тестовыми данными"""
    print("Заполняем базу тестовыми данными...")
    
    users = [
        ('ivan_writer', 'ivan@mail.com'),
        ('maria_blogger', 'maria@ya.ru'),
        ('alex_reader', 'alex@example.org')
    ]
    
    user_ids = []
    for username, email in users:
        user_id = add_user(username, email)
        if user_id:
            user_ids.append(user_id)
    
    categories = ['Python', 'Базы данных', 'Веб-разработка']
    category_ids = []
    for category in categories:
        cat_id = add_category(category)
        if cat_id:
            category_ids.append(cat_id)
    
    posts = [
        ('Мой первый пост на Python', 'Сегодня я изучил основы Python. Это удивительный язык с простым синтаксисом и большими возможностями. Особенно понравились списки и словари!', user_ids[0], category_ids[0]),
        ('SQLite - отличная БД для старта', 'SQLite проста в использовании и не требует отдельного сервера. Идеально для небольших проектов и обучения работе с базами данных.', user_ids[1], category_ids[1]),
        ('Django vs Flask', 'Сравниваем два популярных фреймворка для веб-разработки на Python. Django - это полноценный фреймворк, а Flask - микрофреймворк с большей гибкостью.', user_ids[0], category_ids[2])
    ]
    
    for title, content, user_id, cat_id in posts:
        create_post(title, content, user_id, cat_id)
    
    print("Тестовые данные успешно добавлены!")

def get_posts_by_category(category_name):
    """Возвращает посты определенной категории"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT p.id, p.title, p.content, p.created_at, u.username
            FROM posts p
            JOIN users u ON p.user_id = u.id
            JOIN categories c ON p.category_id = c.id
            WHERE c.name = ?
            ORDER BY p.created_at DESC
        """, (category_name,))
        
        posts = cursor.fetchall()
        
        if not posts:
            print(f"В категории '{category_name}' пока нет постов")
            return []
        
        print(f"\n=== ПОСТЫ В КАТЕГОРИИ '{category_name.upper()}' ===\n")
        for post in posts:
            post_id, title, content, created_at, author = post
            print(f"Заголовок: {title}")
            print(f"Автор: {author}")
            print(f"Дата: {created_at}")
            print(f"Содержание: {content[:80]}..." if len(content) > 80 else f"Содержание: {content}")
            print("-" * 40)
        
        return posts
    except sqlite3.Error as e:
        print(f"Ошибка при получении постов: {e}")
        return []
    finally:
        conn.close()

def main():
    """Основная функция для демонстрации работы блога"""
    
    create_blog_database()
    
    populate_test_data()
    
    get_all_posts_with_authors()
    
    print("\n=== ДОБАВЛЯЕМ НОВЫЙ ПОСТ ===\n")
    new_post_id = create_post(
        "Новый пост о JOIN в SQL", 
        "JOIN операции позволяют объединять данные из нескольких таблиц. Существуют разные типы JOIN: INNER JOIN, LEFT JOIN, RIGHT JOIN и FULL OUTER JOIN. Каждый тип служит для определенных целей при работе с реляционными базами данных.", 
        1,
        1
    )
    
    if new_post_id:
        get_all_posts_with_authors()
    
    print("\n=== ПОСТЫ В КАТЕГОРИИ 'PYTHON' ===\n")
    get_posts_by_category('Python')

if __name__ == "__main__":
    main()