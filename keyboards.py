from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    """Основная клавиатура для пользователей"""
    return ReplyKeyboardMarkup([
        ['📝 Оставить заявку'],
        ['ℹ️ Информация']
    ], resize_keyboard=True)

def get_subscription_keyboard(channel_username):
    """Клавиатура для подписки на канал"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Подписаться на канал", url=f"https://t.me/{channel_username[1:]}")],
        [InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")]
    ])

def get_phone_keyboard():
    """Клавиатура для отправки номера телефона"""
    return ReplyKeyboardMarkup([
        [{'text': '📱 Отправить номер телефона', 'request_contact': True}],
        ['↩️ Назад']
    ], resize_keyboard=True)

def get_back_keyboard():
    """Клавиатура с кнопкой Назад"""
    return ReplyKeyboardMarkup([
        ['↩️ Назад']
    ], resize_keyboard=True)

def get_admin_keyboard():
    """Клавиатура для администратора"""
    return ReplyKeyboardMarkup([
        ['📊 Статистика', '📨 Рассылка'],
        ['📋 Все заявки', '👥 Все пользователи']
    ], resize_keyboard=True)

def get_cancel_keyboard():
    """Клавиатура для отмены действий"""
    return ReplyKeyboardMarkup([
        ['❌ Отмена']
    ], resize_keyboard=True)
def get_info_keyboard():
    """Клавиатура для информации"""
    return ReplyKeyboardMarkup([
        ['📞 Контакты', '🕒 Часы работы'],
        ['💼 Услуги', '↩️ Назад']
    ], resize_keyboard=True)

def get_admin_order_keyboard(application_id):
    """Клавиатура для управления заявкой"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Ответить", callback_data=f"chat_{application_id}"),
         InlineKeyboardButton("✅ Завершить", callback_data=f"close_{application_id}")],
        [InlineKeyboardButton("📋 Детали", callback_data=f"details_{application_id}")]
    ])

def get_chat_keyboard(application_id):
    """Клавиатура для чата"""
    return ReplyKeyboardMarkup([
        ['❌ Завершить чат'],
        ['📋 Информация о заявке']
    ], resize_keyboard=True)