#!/usr/bin/env python3
"""
Главный и единственный скрипт для запуска Telegram-бота на pyTelegramBotAPI
"""
import re
import telebot
import logging
import sqlite3
from datetime import datetime
from telebot import types
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


# Конфигурация, переменные
class Config:
    BOT_TOKEN = "8377401163:AAGcgyx35JH8lOw1Xg5Jvm9slQp0hwPO724"
    CHANNEL_USERNAME = "@Estetika_Kyxni_shkafi"
    ADMIN_ID = [7631971482, 8438177540]
    DATABASE_NAME = "bot_database.db"

    # Сообщения
    WELCOME_MESSAGE = "Добро пожаловать! Для доступа к чату подпишитесь на наш канал."
    SUBSCRIPTION_REQUIRED = "❌ Для доступа к боту необходимо подписаться на канал: {}"
    SUBSCRIPTION_SUCCESS = "Спасибо, чтобы связаться с дизайнером оставьте заявку"
    REQUEST_NAME = "📝 Пожалуйста, введите ваше ФИО:"
    REQUEST_PHONE = "📞 Теперь введите ваш номер телефона:"
    REQUEST_QUERY = "💬 Расскажите, чем мы можем вам помочь? \nКакую мебель подбираете? \nКухня, шкаф, гардеробная? \n_____________________________________\n\nEсть ли у вас уже проект мебели, или нужно спроектировать?"
    DATA_SAVED = "✅ Ваши данные сохранены! С вами свяжутся в ближайшее время."
    INFO_MESSAGE = "📋 Информация о нашем сервисе:\n\n• Мы предоставляем лучшие услуги\n• Работаем с 9:00 до 20:00 по МСК\n• Консультация бесплатно\n\n📞 Контакты: @Estetika_admi"
    BACK_MESSAGE = "↩️ Возврат в главное меню"
    INVALID_NAME = "❌ ФИО должно содержать минимум 2 слова (Имя и Фамилия)"
    INVALID_PHONE = "❌ Неверный формат телефона. Пример: +7 (912) 345 67 89"
    PHONE_EXAMPLE = "+7 (000) 000 00 00"
    CHAT_STARTED = "💬 Чат по заявке #{}\nАдминистратор подключился к диалогу."
    CHAT_MESSAGE_FROM_USER = "👤 Сообщение от пользователя:"
    CHAT_MESSAGE_FROM_ADMIN = "👨‍💼 Сообщение от администратора:"
    ORDER_NOT_FOUND = "❌ Заявка с номером {} не найдена"
    ORDER_CLOSED = "✅ Заявка #{} закрыта"
    ORDER_REOPENED = "✅ Заявка #{} reopened"
    ORDER_DELETED = "✅ Заявка #{} успешно удалена"
    ORDER_DELETE_CONFIRM = "⚠️ Вы уверены, что хотите удалить заявку #{}?\n\n📛 ФИО: {}\n📞 Телефон: {}\n💬 Запрос: {}"
    ORDER_DELETE_CANCELLED = "❌ Удаление заявки #{} отменено"
    DELETE_CONFIRM_YES = "✅ Да, удалить"
    DELETE_CONFIRM_NO = "❌ Нет, отменить"


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# База данных
class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
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

    def add_user(self, user_id, username, first_name, last_name):
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
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET subscribed = ? WHERE user_id = ?', (subscribed, user_id))
        self.conn.commit()

    def check_subscription(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT subscribed FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return bool(result[0]) if result else False

    def save_application(self, user_id, full_name, phone_number, user_query):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO applications (user_id, full_name, phone_number, user_query)
                VALUES (?, ?, ?, ?)
            ''', (user_id, full_name, phone_number, user_query))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving application: {e}")
            return False

    def get_all_applications(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.*, u.username, u.first_name, u.last_name
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            ORDER BY a.created_at DESC
        ''')
        return cursor.fetchall()

    def get_application_by_id(self, application_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.*, u.username, u.first_name, u.last_name
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.id = ?
        ''', (application_id,))
        return cursor.fetchone()

    def update_application_status(self, application_id, status):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE applications SET status = ? WHERE id = ?', (status, application_id))
        self.conn.commit()

    def delete_application(self, application_id):
        try:
            cursor = self.conn.cursor()
            # Сначала удаляем связанные сообщения чата
            cursor.execute('DELETE FROM chat_messages WHERE application_id = ?', (application_id,))
            # Затем удаляем заявку
            cursor.execute('DELETE FROM applications WHERE id = ?', (application_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting application: {e}")
            return False

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        return cursor.fetchall()

    def get_user_count(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]

    def get_application_count(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM applications')
        return cursor.fetchone()[0]

    def get_subscribed_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE subscribed = 1 ORDER BY created_at DESC')
        return cursor.fetchall()

    def add_chat_message(self, application_id, user_id, message, is_admin):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (application_id, user_id, message, is_admin)
            VALUES (?, ?, ?, ?)
        ''', (application_id, user_id, message, is_admin))
        self.conn.commit()

    def get_chat_messages(self, application_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM chat_messages
            WHERE application_id = ?
            ORDER BY created_at ASC
        ''', (application_id,))
        return cursor.fetchall()


# Клавиатуры
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('📝 Оставить заявку'))
    markup.add(types.KeyboardButton('ℹ️ Информация'))
    return markup


def get_subscription_keyboard(channel_username):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Подписаться на канал", url=f"https://t.me/{channel_username[1:]}"))
    markup.add(types.InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription"))
    return markup


def get_phone_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('📱 Отправить номер телефона', request_contact=True))
    markup.add(types.KeyboardButton('↩️ Назад'))
    return markup


def get_back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('↩️ Назад'))
    return markup


def get_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('📊 Статистика'), types.KeyboardButton('📨 Рассылка'))
    markup.add(types.KeyboardButton('📋 Все заявки'), types.KeyboardButton('👥 Все пользователи'))
    markup.add(types.KeyboardButton('🗑️ Удалить заявку'))
    return markup


def get_info_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('📞 Контакты'))
    markup.add(types.KeyboardButton('💼 Услуги'), types.KeyboardButton('↩️ Назад'))
    return markup


def get_admin_order_keyboard(application_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💬 Ответить", callback_data=f"chat_{application_id}"),
        types.InlineKeyboardButton("✅ Завершить", callback_data=f"close_{application_id}")
    )
    markup.add(
        types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{application_id}")
    )
    return markup


def get_chat_keyboard(application_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('❌ Завершить чат'))
    markup.add(types.KeyboardButton('📋 Информация о заявке'))
    return markup


def get_delete_confirmation_keyboard(application_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(Config.DELETE_CONFIRM_YES, callback_data=f"confirm_delete_{application_id}"),
        types.InlineKeyboardButton(Config.DELETE_CONFIRM_NO, callback_data=f"cancel_delete_{application_id}")
    )
    return markup


# Утилиты
def validate_name(full_name):
    """Проверка ФИО - минимум 2 слова"""
    words = full_name.strip().split()
    return len(words) >= 2


def validate_phone(phone_number):
    """Проверка формата телефона"""
    pattern = r'^\+7\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}$'
    return re.match(pattern, phone_number) is not None


def format_phone(phone):
    """Форматирование телефона в нужный вид"""
    digits = re.sub(r'\D', '', phone)

    if digits.startswith('8'):
        digits = '7' + digits[1:]
    elif not digits.startswith('7'):
        digits = '7' + digits

    if len(digits) == 11:
        return f"+7 ({digits[1:4]}) {digits[4:7]} {digits[7:9]} {digits[9:11]}"
    return None


def format_application(application):
    app_id, user_id, full_name, phone_number, user_query, status, created_at, username, first_name, last_name = application
    return f"""
📋 Заявка #{app_id}
👤 Пользователь: {first_name} {last_name} (@{username})
📛 ФИО: {full_name}
📞 Телефон: {phone_number}
💬 Запрос: {user_query}
🕒 Дата: {created_at}
📊 Статус: {status}
""".strip()


def format_user(user):
    user_id, tg_user_id, username, first_name, last_name, subscribed, created_at = user
    return f"""
👤 User ID: {tg_user_id}
📛 Имя: {first_name} {last_name}
📱 Username: @{username}
✅ Подписка: {'Да' if subscribed else 'Нет'}
🕒 Дата регистрации: {created_at}
""".strip()


# Основной класс бота
class TelegramBot:
    def __init__(self):
        self.config = Config()
        self.db = Database(self.config.DATABASE_NAME)
        self.bot = telebot.TeleBot(self.config.BOT_TOKEN)
        self.user_states = {}  # Для хранения состояний пользователей

        self.setup_handlers()




def setup_handlers(self):
    # Обработчики команд
    @self.bot.message_handler(func=lambda message: message.text in ['📞 Контакты', '💼 Услуги'])
    def info_buttons_handler(message):
        self.info_buttons_handler(message)

    @self.bot.message_handler(commands=['start'])
    def start_handler(message):
        user = message.from_user

        # Проверяем, есть ли пользователь уже в базе
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT subscribed FROM users WHERE user_id = ?', (user.id,))
        existing_user = cursor.fetchone()

        # Добавляем/обновляем пользователя
        self.db.add_user(user.id, user.username, user.first_name, user.last_name)

        # Проверка подписки (синхронно)
        try:
            chat_member = self.bot.get_chat_member(self.config.CHANNEL_USERNAME, user.id)
            is_subscribed = chat_member.status in ['member', 'administrator', 'creator']
        except:
            is_subscribed = False

        if is_subscribed:
            # Обновляем подписку
            self.db.update_subscription(user.id, 1)

            # Отправляем уведомление только если пользователь был неподписан или это новый пользователь
            if not existing_user or (existing_user and not existing_user[0]):
                for admin_id in self.config.ADMIN_ID:
                    self.bot.send_message(admin_id,f"🎉 Новый подписчик: {user.first_name} {user.last_name} (@{user.username})")

            self.bot.send_message(message.chat.id, self.config.WELCOME_MESSAGE, reply_markup=get_main_keyboard())
        else:
            self.db.update_subscription(user.id, 0)
            self.bot.send_message(
                message.chat.id,
                self.config.SUBSCRIPTION_REQUIRED.format(self.config.CHANNEL_USERNAME),
                reply_markup=get_subscription_keyboard(self.config.CHANNEL_USERNAME)
            )

    @self.bot.message_handler(commands=['admin'])
    def admin_handler(message):
        self.admin_handler(message)

    @self.bot.message_handler(commands=['chat'])
    def chat_command(message):
        self.chat_command(message)

    @self.bot.message_handler(commands=['delete'])
    def delete_command(message):
        self.delete_command(message)

    # Обработчик callback запросов
    @self.bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        self.callback_handler(call)

    # Обработчики текстовых сообщений
    @self.bot.message_handler(func=lambda message: message.text == '📝 Оставить заявку')
    def start_application_handler(message):
        user_id = message.from_user.id
        
        # Проверяем актуальную подписку через Telegram API
        try:
            chat_member = self.bot.get_chat_member(self.config.CHANNEL_USERNAME, user_id)
            is_subscribed = chat_member.status in ['member', 'administrator', 'creator']
        except:
            is_subscribed = False
        
        if not is_subscribed:
            self.bot.send_message(
                message.chat.id,
                self.config.SUBSCRIPTION_REQUIRED.format(self.config.CHANNEL_USERNAME),
                reply_markup=get_subscription_keyboard(self.config.CHANNEL_USERNAME)
            )
            return
        
        # Обновляем статус подписки в базе
        self.db.update_subscription(user_id, 1)
        
        self.user_states[user_id] = {'state': 'NAME'}
        self.bot.send_message(message.chat.id, self.config.REQUEST_NAME, reply_markup=get_back_keyboard())

    @self.bot.message_handler(func=lambda message: message.text == 'ℹ️ Информация')
    def info_handler(message):
        self.info_handler(message)

    @self.bot.message_handler(func=lambda message: message.text == '↩️ Назад')
    def back_handler(message):
        self.back_handler(message)

    @self.bot.message_handler(
        func=lambda message: message.text in ['📊 Статистика', '📋 Все заявки', '👥 Все пользователи', '📨 Рассылка',
                                              '🗑️ Удалить заявку'])
    def admin_buttons_handler(message):
        self.admin_buttons_handler(message)

    # Обработчик всех текстовых сообщений
    @self.bot.message_handler(content_types=['text'])
    def text_message_handler(message):
        user_id = message.from_user.id

        # Обработка кнопок чата для админа
        if user_id in self.config.ADMIN_ID and user_id in self.user_states and 'current_chat' in self.user_states[user_id]:
            if message.text == '❌ Завершить чат':
                self.end_chat(message)
                return
            elif message.text == '📋 Информация о заявке':
                self.show_application_info(message)
                return

        self.text_message_handler(message)

    # Обработчик контактов
    @self.bot.message_handler(content_types=['contact'])
    def contact_handler(message):
        self.contact_handler(message)

        # Обработка кнопок чата для админа
        if user_id in self.config.ADMIN_ID and user_id in self.user_states and 'current_chat' in self.user_states[user_id]:
            if message.text == '❌ Завершить чат':
                self.end_chat(message)
                return
            elif message.text == '📋 Информация о заявке':
                self.show_application_info(message)
                return

        self.text_message_handler(message)

    def back_handler(self, message):
        user_id = message.from_user.id
        if user_id in self.user_states:
            del self.user_states[user_id]

        self.bot.send_message(
            message.chat.id,
            self.config.BACK_MESSAGE,
            reply_markup=get_main_keyboard()
        )

    def admin_buttons_handler(self, message):
        if message.from_user.id not in self.config.ADMIN_ID:
            return

        if message.text == '📊 Статистика':
            self.stats_handler(message)
        elif message.text == '📋 Все заявки':
            self.applications_handler(message)
        elif message.text == '👥 Все пользователи':
            self.users_handler(message)
        elif message.text == '📨 Рассылка':
            self.broadcast_handler(message)
        elif message.text == '🗑️ Удалить заявку':
            self.delete_handler(message)

    def stats_handler(self, message):
        user_count = self.db.get_user_count()
        app_count = self.db.get_application_count()
        self.bot.send_message(message.chat.id, f"📊 Статистика:\n\n👥 Пользователей: {user_count}\n📋 Заявок: {app_count}")

    def applications_handler(self, message):
        applications = self.db.get_all_applications()
        if not applications:
            self.bot.send_message(message.chat.id, "📭 Заявок пока нет")
            return

        for app in applications:
            self.bot.send_message(message.chat.id, format_application(app))

    def users_handler(self, message):
        users = self.db.get_all_users()
        if not users:
            self.bot.send_message(message.chat.id, "👥 Пользователей пока нет")
            return

        for user in users:
            self.bot.send_message(message.chat.id, format_user(user))

    def broadcast_handler(self, message):
        self.user_states[message.from_user.id] = {'awaiting_broadcast': True}
        self.bot.send_message(message.chat.id, "Введите сообщение для рассылки:",
                              reply_markup=types.ReplyKeyboardRemove())

    def delete_handler(self, message):
        """Обработчик кнопки удаления заявки"""
        self.user_states[message.from_user.id] = {'awaiting_delete': True}
        self.bot.send_message(message.chat.id, "Введите номер заявки для удаления:")

    def delete_command(self, message):
        """Команда /delete для удаления заявки"""
        if message.from_user.id not in self.config.ADMIN_ID:
            self.bot.send_message(message.chat.id, "❌ Доступ запрещен")
            return

        if not message.text.split():
            self.bot.send_message(message.chat.id, "Использование: /delete <номер_заявки>")
            return

        try:
            application_id = int(message.text.split()[1])
            application = self.db.get_application_by_id(application_id)

            if not application:
                self.bot.send_message(message.chat.id, self.config.ORDER_NOT_FOUND.format(application_id))
                return

            # Показываем подтверждение удаления
            app_id, user_id, full_name, phone_number, user_query, status, created_at, username, first_name, last_name = application
            self.bot.send_message(
                message.chat.id,
                self.config.ORDER_DELETE_CONFIRM.format(application_id, full_name, phone_number, user_query),
                reply_markup=get_delete_confirmation_keyboard(application_id)
            )

        except (ValueError, IndexError):
            self.bot.send_message(message.chat.id, "Номер заявки должен быть числом")

    def text_message_handler(self, message):
        user_id = message.from_user.id

        # Проверяем, ожидаем ли мы рассылку от админа
        if user_id in self.config.ADMIN_ID and self.user_states.get(user_id, {}).get('awaiting_broadcast'):
            self.process_broadcast(message)
            return

        # Проверяем, ожидаем ли мы номер заявки для удаления
        if user_id in self.config.ADMIN_ID and self.user_states.get(user_id, {}).get('awaiting_delete'):
            self.process_delete_request(message)
            return

        # Проверяем состояние пользователя
        user_state = self.user_states.get(user_id, {}).get('state')

        if user_state == 'NAME':
            self.get_name(message)
        elif user_state == 'PHONE':
            self.get_phone(message)
        elif user_state == 'QUERY':
            self.get_query(message)
        elif user_id in self.user_states and 'current_chat' in self.user_states[user_id]:
            self.process_chat_message(message)

    def process_delete_request(self, message):
        """Обработка ввода номера заявки для удаления"""
        user_id = message.from_user.id
        try:
            application_id = int(message.text)
            application = self.db.get_application_by_id(application_id)

            if not application:
                self.bot.send_message(message.chat.id, self.config.ORDER_NOT_FOUND.format(application_id))
                return

            # Показываем подтверждение удаления
            app_id, user_id, full_name, phone_number, user_query, status, created_at, username, first_name, last_name = application
            self.bot.send_message(
                message.chat.id,
                self.config.ORDER_DELETE_CONFIRM.format(application_id, full_name, phone_number, user_query),
                reply_markup=get_delete_confirmation_keyboard(application_id)
            )

            # Очищаем состояние
            if user_id in self.user_states and 'awaiting_delete' in self.user_states[user_id]:
                del self.user_states[user_id]['awaiting_delete']

        except ValueError:
            self.bot.send_message(message.chat.id, "Номер заявки должен быть числом")

    def contact_handler(self, message):
        user_id = message.from_user.id
        user_state = self.user_states.get(user_id, {}).get('state')

        if user_state == 'PHONE':
            self.get_phone(message, is_contact=True)

    def process_broadcast(self, message):
        user_id = message.from_user.id
        broadcast_message = message.text
        users = self.db.get_subscribed_users()

        success_count = 0
        for user in users:
            try:
                self.bot.send_message(user[1], broadcast_message)  # user[1] = user_id
                success_count += 1
            except Exception as e:
                logger.error(f"Error sending broadcast to user {user[1]}: {e}")

        # Очищаем состояние
        if user_id in self.user_states and 'awaiting_broadcast' in self.user_states[user_id]:
            del self.user_states[user_id]['awaiting_broadcast']

        self.bot.send_message(
            message.chat.id,
            f"✅ Рассылка завершена\nОтправлено: {success_count}/{len(users)}",
            reply_markup=get_admin_keyboard()
        )

    def chat_command(self, message):
        if message.from_user.id not in self.config.ADMIN_ID:
            return

        if not message.text.split():
            self.bot.send_message(message.chat.id, "Использование: /chat <номер_заявки>")
            return

        try:
            application_id = int(message.text.split()[1])
            application = self.db.get_application_by_id(application_id)

            if not application:
                self.bot.send_message(message.chat.id, self.config.ORDER_NOT_FOUND.format(application_id))
                return

            self.user_states[message.from_user.id] = {'current_chat': application_id}
            self.bot.send_message(
                message.chat.id,
                self.config.CHAT_STARTED.format(application_id),
                reply_markup=get_chat_keyboard(application_id)
            )

        except (ValueError, IndexError):
            self.bot.send_message(message.chat.id, "Номер заявки должен быть числом")

    def process_chat_message(self, message):
        user_id = message.from_user.id

        # Пропускаем служебные команды чата
        if message.text in ['❌ Завершить чат', '📋 Информация о заявке']:
            return

        message_text = message.text
        application_id = self.user_states[user_id]['current_chat']
        is_admin = (user_id in self.config.ADMIN_ID)

        # Сохраняем сообщение
        self.db.add_chat_message(application_id, user_id, message_text, is_admin)

        # Пересылаем сообщение
        application = self.db.get_application_by_id(application_id)
        if application:
            target_id = self.config.ADMIN_ID if not is_admin else application[1]  # application[1] = user_id

            prefix = self.config.CHAT_MESSAGE_FROM_ADMIN if is_admin else self.config.CHAT_MESSAGE_FROM_USER
            self.bot.send_message(
                target_id,
                f"{prefix}\n{message_text}\n\n(Заявка #{application_id})",
                reply_markup=get_chat_keyboard(application_id) if not is_admin else None
            )

    def admin_order_callback(self, call):
        user_id = call.from_user.id
        data = call.data

        if user_id not in self.config.ADMIN_ID:
            self.bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return

        if data.startswith('chat_'):
            application_id = int(data.split('_')[1])
            self.user_states[user_id] = {'current_chat': application_id}

            # Вместо редактирования сообщения отправляем новое с правильной клавиатурой
            self.bot.send_message(
                call.message.chat.id,
                self.config.CHAT_STARTED.format(application_id),
                reply_markup=get_chat_keyboard(application_id)
            )
            self.bot.answer_callback_query(call.id)  # Закрываем callback

        elif data.startswith('close_'):
            application_id = int(data.split('_')[1])
            self.db.update_application_status(application_id, 'closed')
            self.bot.edit_message_text(
                self.config.ORDER_CLOSED.format(application_id),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=None  # Убираем клавиатуру при закрытии
            )

        elif data.startswith('details_'):
            application_id = int(data.split('_')[1])
            application = self.db.get_application_by_id(application_id)
            if application:
                self.bot.edit_message_text(
                    format_application(application),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=get_admin_order_keyboard(application_id)  # Возвращаем ту же клавиатуру
                )

        elif data.startswith('delete_'):
            application_id = int(data.split('_')[1])
            application = self.db.get_application_by_id(application_id)
            if application:
                app_id, user_id, full_name, phone_number, user_query, status, created_at, username, first_name, last_name = application
                self.bot.edit_message_text(
                    self.config.ORDER_DELETE_CONFIRM.format(application_id, full_name, phone_number, user_query),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=get_delete_confirmation_keyboard(application_id)
                )

        elif data.startswith('confirm_delete_'):
            application_id = int(data.split('_')[2])
            if self.db.delete_application(application_id):
                self.bot.edit_message_text(
                    self.config.ORDER_DELETED.format(application_id),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=None  # Убираем клавиатуру после удаления
                )
            else:
                self.bot.answer_callback_query(call.id, "❌ Ошибка при удалении заявки")

        elif data.startswith('cancel_delete_'):
            application_id = int(data.split('_')[2])
            application = self.db.get_application_by_id(application_id)
            if application:
                self.bot.edit_message_text(
                    format_application(application),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=get_admin_order_keyboard(application_id)
                )

    def run(self):
        """Запуск бота"""
        logger.info("Бот запущен...")
        self.bot.infinity_polling()


# Точка входа
if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()

