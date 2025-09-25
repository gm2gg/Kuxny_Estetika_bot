import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot('YOUR_BOT_TOKEN')

# Массив каналов и групп для отслеживания
TRACKED_CHANNELS = [
    "@Estetika_Kyxni_shkafi",
    "@Etetika_prorkti"
]

# Массив разрешенных пользовательских ID
ALLOWED_USERS = [
    7631971482,
    8438177540,
    804870556,
]

# Словарь для хранения настроек пользователей
user_settings = {}


def is_user_allowed(user_id):
    """Проверяет, есть ли у пользователя доступ"""
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
🤖 Бот для добавления кнопок в каналах

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


@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation'])
def handle_channel_post(message):
    """Обрабатывает сообщения из каналов"""
    chat_id = message.chat.id
    chat_username = f"@{message.chat.username}" if message.chat.username else None
    
    # Проверяем, что сообщение пришло из отслеживаемого канала/группы
    is_tracked = False
    channel_name = ""
    
    for channel in TRACKED_CHANNELS:
        if channel.startswith('@'):
            if chat_username and chat_username.lower() == channel.lower():
                is_tracked = True
                channel_name = channel
                break
        else:
            if str(chat_id) == channel:
                is_tracked = True
                channel_name = channel
                break
    
    if is_tracked:
        # Получаем настройки для администратора (первого пользователя из ALLOWED_USERS)
        admin_id = ALLOWED_USERS[0] if ALLOWED_USERS else None
        add_buttons = should_add_buttons(admin_id) if admin_id else True
        
        if add_buttons:
            keyboard = create_keyboard()
            
            try:
                # Отправляем только текст с кнопками под сообщением
                bot.send_message(
                    chat_id, 
                    "Для связи используйте кнопки ниже 👇", 
                    reply_markup=keyboard,
                    reply_to_message_id=message.message_id  # Ответ на конкретное сообщение
                )
                
                print(f"✅ Добавлены кнопки к сообщению в {channel_name}")
                
            except Exception as e:
                print(f"❌ Ошибка при добавлении кнопок в {channel_name}: {e}")


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
    print(f"Отслеживаем каналы/группы: {', '.join(TRACKED_CHANNELS)}")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
