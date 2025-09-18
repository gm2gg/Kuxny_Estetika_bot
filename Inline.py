import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot('7585158499:AAG91_F-OhKvf0i3-zgObTmcccKGJNlAQNw')

# Массив каналов для рассылки
CHANNELS = [
    "@Estetika_Kyxni_shkafi"
]

# Массив разрешенных пользовательских ID
ALLOWED_USERS = [
    8438177540,  # Добавьте нужные ID
    7631971482,
]

def is_user_allowed(user_id):
    """Проверяет, есть ли у пользователя доступ"""
    return user_id in ALLOWED_USERS

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
        
    bot.reply_to(message, "Добро пожаловать! Отправьте мне любое сообщение (текст, фото, видео), и я перешлю его во все каналы с кнопками для связи.")

@bot.message_handler(commands=['channels'])
def show_channels(message):
    """Показывает список каналов для рассылки"""
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
        
    channels_list = "\n".join([f"• {channel}" for channel in CHANNELS])
    bot.reply_to(message, f"📢 Каналы для рассылки:\n{channels_list}\n\nВсего: {len(CHANNELS)} каналов")

def create_keyboard():
    """Создает клавиатуру с тремя кнопками"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    button1 = InlineKeyboardButton(
        text="Связаться с дизайнером",
        url="https://t.me/Estetika_kuhni_bot"
    )

    button2 = InlineKeyboardButton(
        text="Прислать проект",
        url="https://t.me/Estetika_admi?start=project_calculation"
    )

    button3 = InlineKeyboardButton(
        text="Выезд на замер",
        url="https://t.me/Estetika_admi?start=measurement_visit"
    )

    keyboard.add(button1)
    keyboard.add(button2, button3)
    return keyboard

def send_to_all_channels(content_type, content_data, caption_text):
    """Отправляет сообщение во все каналы"""
    keyboard = create_keyboard()
    success_count = 0
    failed_channels = []

    for channel in CHANNELS:
        try:
            if content_type == 'photo':
                bot.send_photo(
                    channel,
                    content_data,
                    caption=caption_text,
                    reply_markup=keyboard
                )
            elif content_type == 'video':
                bot.send_video(
                    channel,
                    content_data,
                    caption=caption_text,
                    reply_markup=keyboard
                )
            elif content_type == 'document':
                bot.send_document(
                    channel,
                    content_data,
                    caption=caption_text,
                    reply_markup=keyboard
                )
            elif content_type == 'text':
                bot.send_message(
                    channel,
                    caption_text,
                    reply_markup=keyboard
                )
            success_count += 1
            print(f"✅ Отправлено в канал: {channel}")

        except Exception as e:
            print(f"❌ Ошибка отправки в {channel}: {e}")
            failed_channels.append(f"{channel} - {str(e)}")

    return success_count, failed_channels

@bot.message_handler(content_types=['text', 'photo', 'video', 'document'])
def handle_all_messages(message):
    # Проверяем доступ пользователя
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
        
    try:
        caption_text = "Для связи используйте кнопки ниже👇"
        if message.caption:
            caption_text = f"{message.caption}\n\n{caption_text}"
        elif message.text and not (message.photo or message.video or message.document):
            caption_text = f"{message.text}\n\n{caption_text}"

        content_type = None
        content_data = None

        # Определяем тип контента и получаем данные
        if message.photo:
            content_type = 'photo'
            content_data = message.photo[-1].file_id
        elif message.video:
            content_type = 'video'
            content_data = message.video.file_id
        elif message.document:
            content_type = 'document'
            content_data = message.document.file_id
        else:
            content_type = 'text'
            content_data = None

        # Отправляем во все каналы
        success_count, failed_channels = send_to_all_channels(content_type, content_data, caption_text)

        # Формируем отчет для пользователя
        report = f"✅ Сообщение отправлено в {success_count} из {len(CHANNELS)} каналов"

        if failed_channels:
            report += f"\n\n❌ Не удалось отправить в {len(failed_channels)} каналов:"
            for i, failed in enumerate(failed_channels[:3], 1):  # Показываем первые 3 ошибки
                report += f"\n{i}. {failed}"
            if len(failed_channels) > 3:
                report += f"\n... и еще {len(failed_channels) - 3} каналов"

        bot.reply_to(message, report)

    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    print("Бот запущен...")
    print(f"Каналы для рассылки: {CHANNELS}")
    print(f"Разрешенные пользователи: {ALLOWED_USERS}")
    print("Функционал: автоматическая рассылка для разрешенных пользователей")

    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Ошибка запуска бота: {e}")
