import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot('')

# Массив каналов и групп для отслеживания
TRACKED_CHATS = [
    "@Estetika_Kyxni_shkafi",
    "@Etetika_prorkti"
]

# Массив разрешенных пользовательских ID (админы бота)
ALLOWED_USERS = [
    7631971482,
    8438177540,
    804870556,
]

# Словарь для хранения настроек пользователей
user_settings = {}


def is_user_allowed(user_id):
    """Проверяет, есть ли у пользователя доступ к боту"""
    return user_id in ALLOWED_USERS


def create_keyboard():
    """Создает клавиатуру с кнопками в один столбец"""
    keyboard = InlineKeyboardMarkup(row_width=1)

    button1 = InlineKeyboardButton(
        text="👨‍💻 Связаться с дизайнером",
        url="https://t.me/Estetika_kuhni_bot"
    )
    button2 = InlineKeyboardButton(
        text="⭐ Отзывы",
        url="https://t.me/Estetika_otziv"
    )
    button3 = InlineKeyboardButton(
        text="🏠 Реализованные проекты",
        url="https://t.me/Etetika_prorkti"
    )

    keyboard.add(button1, button2, button3)
    return keyboard


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
    
    welcome_text = """
🤖 Бот для добавления кнопок в каналах и группах

Доступные команды:
/start - показать эту справку
/true - прикреплять кнопки к сообщениям (по умолчанию)
/false - не прикреплять кнопки к сообщениям

Бот автоматически добавляет кнопки под сообщениями в отслеживаемых каналах и группах.
"""
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=['true'])
def set_true(message):
    """Включает прикрепление кнопок"""
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
    
    user_id = message.from_user.id
    user_settings[user_id] = True
    bot.reply_to(message, "✅ Теперь к сообщениям будут прикрепляться кнопки")


@bot.message_handler(commands=['false'])
def set_false(message):
    """Отключает прикрепление кнопок"""
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
    
    user_id = message.from_user.id
    user_settings[user_id] = False
    bot.reply_to(message, "❌ Теперь к сообщениям НЕ будут прикрепляться кнопки")


def should_add_buttons(user_id):
    """Проверяет, нужно ли прикреплять кнопки для пользователя"""
    return user_settings.get(user_id, True)


def is_tracked_chat(chat_id, chat_username):
    """Проверяет, отслеживается ли чат"""
    for chat in TRACKED_CHATS:
        if chat.startswith('@'):
            if chat_username and chat_username.lower() == chat.lower():
                return True, chat
        else:
            if str(chat_id) == chat:
                return True, chat
    return False, ""


def handle_chat_message(message, is_channel=False):
    """Обрабатывает сообщения из чатов (каналов и групп)"""
    chat_id = message.chat.id
    chat_username = f"@{message.chat.username}" if message.chat.username else None
    
    # Проверяем, что сообщение пришло из отслеживаемого чата
    is_tracked, chat_name = is_tracked_chat(chat_id, chat_username)
    
    if not is_tracked:
        return
    
    # Для каналов - всегда обрабатываем
    # Для групп - проверяем, что сообщение от админа бота
    if not is_channel:
        if not hasattr(message, 'from_user') or not message.from_user or message.from_user.id not in ALLOWED_USERS:
            print(f"❌ Сообщение в группе {chat_name} от обычного пользователя, игнорируем")
            return
    
    # Определяем ID для настроек
    if is_channel:
        # Для каналов используем первого админа
        user_id = ALLOWED_USERS[0] if ALLOWED_USERS else None
    else:
        # Для групп используем ID отправителя
        user_id = message.from_user.id
    
    add_buttons = should_add_buttons(user_id) if user_id else True
    
    if add_buttons:
        keyboard = create_keyboard()
        
        try:
            # Отправляем просто следующим сообщением без ответа
            bot.send_message(
                chat_id, 
                "Для связи используйте кнопки ниже 👇", 
                reply_markup=keyboard
            )
            
            sender_type = "канала" if is_channel else "админа"
            print(f"✅ Добавлены кнопки к сообщению {sender_type} в {chat_name}")
            
        except Exception as e:
            print(f"❌ Ошибка при добавлении кнопок в {chat_name}: {e}")
    else:
        print(f"✅ Режим /false - кнопки не добавлены к сообщению в {chat_name}")


# Обработчик для сообщений из каналов
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation'])
def handle_channel_post(message):
    """Обрабатывает сообщения из каналов"""
    handle_chat_message(message, is_channel=True)


# Обработчик для сообщений из групп и супергрупп
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation'], 
                    chat_types=['group', 'supergroup'])
def handle_group_message(message):
    """Обрабатывает сообщения из групп"""
    handle_chat_message(message, is_channel=False)


@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def block_other_messages(message):
    """Блокирует все сообщения кроме команд"""
    if message.text and message.text.startswith('/'):
        # Это команда, пропускаем обработку другими хендлерами
        return
    
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
    
    # Для разрешенных пользователей показываем подсказку
    bot.reply_to(message, "❌ Бот принимает только команды. Используйте /start для просмотра доступных команд.")


if __name__ == "__main__":
    print("Бот запущен...")
    print(f"Отслеживаем чаты: {', '.join(TRACKED_CHATS)}")
    print(f"Админы бота: {', '.join(map(str, ALLOWED_USERS))}")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
