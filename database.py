import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        """Создание таблиц в базе данных"""
        cursor = self.conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                subscribed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица заявок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                full_name TEXT,
                phone_number TEXT,
                user_query TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Таблица для рассылок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY,
                message_text TEXT,
                sent_count INTEGER,
                total_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def add_user(self, user_id, username, first_name, last_name):
        """Добавление нового пользователя"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False

    def update_subscription(self, user_id, subscribed):
        """Обновление статуса подписки пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET subscribed = ? WHERE user_id = ?', (subscribed, user_id))
        self.conn.commit()

    def check_subscription(self, user_id):
        """Проверка подписки пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT subscribed FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else False

    def save_application(self, user_id, full_name, phone_number, user_query):
        """Сохранение заявки от пользователя"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO applications (user_id, full_name, phone_number, user_query)
                VALUES (?, ?, ?, ?)
            ''', (user_id, full_name, phone_number, user_query))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving application: {e}")
            return False

    def get_user_applications(self, user_id):
        """Получение заявок конкретного пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        return cursor.fetchall()

    def get_all_applications(self):
        """Получение всех заявок"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.*, u.username, u.first_name, u.last_name 
            FROM applications a 
            JOIN users u ON a.user_id = u.user_id 
            ORDER BY a.created_at DESC
        ''')
        return cursor.fetchall()

    def get_all_users(self):
        """Получение всех пользователей"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        return cursor.fetchall()

    def get_subscribed_users(self):
        """Получение подписанных пользователей"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE subscribed = 1 ORDER BY created_at DESC')
        return cursor.fetchall()

    def get_user_count(self):
        """Получение количества пользователей"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]

    def get_subscribed_count(self):
        """Получение количества подписанных пользователей"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE subscribed = 1')
        return cursor.fetchone()[0]

    def get_application_count(self):
        """Получение количества заявок"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM applications')
        return cursor.fetchone()[0]

    def get_user_by_id(self, user_id):
        """Получение пользователя по ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()

    def update_application_status(self, application_id, status):
        """Обновление статуса заявки"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE applications SET status = ? WHERE id = ?', (status, application_id))
        self.conn.commit()

    def save_broadcast(self, message_text, total_count):
        """Сохранение информации о рассылке"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO broadcasts (message_text, sent_count, total_count)
            VALUES (?, ?, ?)
        ''', (message_text, 0, total_count))
        self.conn.commit()
        return cursor.lastrowid

    def update_broadcast_stats(self, broadcast_id, sent_count):
        """Обновление статистики рассылки"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE broadcasts SET sent_count = ? WHERE id = ?', (sent_count, broadcast_id))
        self.conn.commit()

    def get_broadcast_history(self):
        """Получение истории рассылок"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM broadcasts ORDER BY created_at DESC LIMIT 10')
        return cursor.fetchall()

    def get_application_by_id(self, application_id):
        """Получить заявку по ID"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.*, u.username, u.first_name, u.last_name 
            FROM applications a 
            JOIN users u ON a.user_id = u.user_id 
            WHERE a.id = ?
        ''', (application_id,))
        return cursor.fetchone()

    def update_application_status(self, application_id, status):
        """Обновить статус заявки"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE applications SET status = ? WHERE id = ?', (status, application_id))
        self.conn.commit()

    def get_chat_messages(self, application_id):
        """Получить историю сообщений чата"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM chat_messages 
            WHERE application_id = ? 
            ORDER BY created_at ASC
        ''', (application_id,))
        return cursor.fetchall()

    def add_chat_message(self, application_id, user_id, message, is_admin):
        """Добавить сообщение в чат"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (application_id, user_id, message, is_admin)
            VALUES (?, ?, ?, ?)
        ''', (application_id, user_id, message, is_admin))
        self.conn.commit()

    def create_tables(self):
        """Создание таблиц (дополните существующий метод)"""
        cursor = self.conn.cursor()

        # ... существующие таблицы ...

        # Таблица сообщений чата
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY,
                application_id INTEGER,
                user_id INTEGER,
                message TEXT,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        self.conn.commit()

    def get_user_applications(self, user_id):
        """Получение заявок конкретного пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.*, u.username, u.first_name, u.last_name 
            FROM applications a 
            JOIN users u ON a.user_id = u.user_id 
            WHERE a.user_id = ? 
            ORDER BY a.created_at DESC
        ''', (user_id,))
        return cursor.fetchall()