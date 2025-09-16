import sqlite3
from datetime import datetime

# Вспомогательная функция для подключения к БД
def get_connection():
    """Создает и возвращает соединение с базой данных"""
    conn = sqlite3.connect('blog.db')
    # Включаем поддержку внешних ключей
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# 1. Функция для добавления нового пользователя
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
        return cursor.lastrowid  # Возвращаем ID нового пользователя
    except sqlite3.IntegrityError:
        print("Ошибка: пользователь с таким именем или email уже существует")
        return None
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Ошибка при добавлении пользователя: {e}")
        return None
    finally:
        conn.close()

# 2. Функция для создания поста
def create_post(title, content, user_id, category_id):
    """
    Создает новый пост в блоге
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            print("Ошибка: пользователь не существует")
            return None
        
        # Проверяем, существует ли категория
        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            print("Ошибка: категория не существует")
            return None
        
        # Создаем пост
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

# 3. Функция для вывода всех постов с именами авторов (с использованием JOIN)
def get_all_posts_with_authors():
    """
    Возвращает все посты с информацией об авторах и категориях
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # JOIN трех таблиц для получения полной информации
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

# 4. Дополнительная функция: добавление категории
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

# 5. Дополнительная функция: добавление комментария
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

# 6. Функция для заполнения тестовыми данными
def populate_test_data():
    """Заполняет базу данных тестовыми данными"""
    print("Заполняем базу тестовыми данными...")
    
    # Добавляем пользователей
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
    
    # Добавляем категории
    categories = ['Python', 'Базы данных', 'Веб-разработка']
    category_ids = []
    for category in categories:
        cat_id = add_category(category)
        if cat_id:
            category_ids.append(cat_id)
    
    # Добавляем посты
    posts = [
        ('Мой первый пост на Python', 'Сегодня я изучил основы Python...', user_ids[0], category_ids[0]),
        ('SQLite - отличная БД для старта', 'SQLite проста в использовании...', user_ids[1], category_ids[1]),
        ('Django vs Flask', 'Сравниваем два популярных фреймворка...', user_ids[0], category_ids[2])
    ]
    
    for title, content, user_id, cat_id in posts:
        create_post(title, content, user_id, cat_id)
    
    print("Тестовые данные успешно добавлены!")

# Основная функция для демонстрации
def main():
    """Основная функция для демонстрации работы блога"""
    
    # Сначала создаем структуру БД
    create_blog_database()
    
    # Заполняем тестовыми данными
    populate_test_data()
    
    # Получаем и выводим все посты
    get_all_posts_with_authors()
    
    # Пример добавления нового поста
    print("\n=== ДОБАВЛЯЕМ НОВЫЙ ПОСТ ===\n")
    new_post_id = create_post(
        "Новый пост о JOIN в SQL", 
        "JOIN операции позволяют объединять данные из нескольких таблиц...", 
        1,  # user_id 
        1   # category_id
    )
    
    # Снова выводим все посты
    if new_post_id:
        get_all_posts_with_authors()

if __name__ == "__main__":
    main()