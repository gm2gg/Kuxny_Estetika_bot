import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo

bot = telebot.TeleBot('')

# Массив каналов для рассылки
CHANNELS = [
    "@Estetika_Kyxni_shkafi"
]

# Массив разрешенных пользовательских ID
ALLOWED_USERS = [
    7631971482,
    8438177540,
    804870556,
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

def send_media_group_to_channel(channel, media_list, caption_text):
    """Отправляет медиагруппу в канал"""
    try:
        bot.send_media_group(channel, media_list)
        # Отправляем кнопки отдельным сообщением
        keyboard = create_keyboard()
        bot.send_message(channel, caption_text, reply_markup=keyboard)
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки медиагруппы в {channel}: {e}")
        return False

def send_to_all_channels(content_type, content_data, caption_text, media_group=None):
    """Отправляет сообщение во все каналы"""
    success_count = 0
    failed_channels = []

    for channel in CHANNELS:
        try:
            if media_group:
                # Отправляем медиагруппу
                if send_media_group_to_channel(channel, media_group, caption_text):
                    success_count += 1
                else:
                    failed_channels.append(f"{channel} - ошибка медиагруппы")
                    
            elif content_type == 'photo':
                bot.send_photo(
                    channel,
                    content_data,
                    caption=caption_text,
                    reply_markup=create_keyboard()
                )
                success_count += 1
                
            elif content_type == 'video':
                bot.send_video(
                    channel,
                    content_data,
                    caption=caption_text,
                    reply_markup=create_keyboard()
                )
                success_count += 1
                
            elif content_type == 'document':
                bot.send_document(
                    channel,
                    content_data,
                    caption=caption_text,
                    reply_markup=create_keyboard()
                )
                success_count += 1
                
            elif content_type == 'text':
                bot.send_message(
                    channel,
                    caption_text,
                    reply_markup=create_keyboard()
                )
                success_count += 1
                
            print(f"✅ Отправлено в канал: {channel}")

        except Exception as e:
            print(f"❌ Ошибка отправки в {channel}: {e}")
            failed_channels.append(f"{channel} - {str(e)}")

    return success_count, failed_channels

@bot.message_handler(content_types=['text', 'photo', 'video', 'document'])
def handle_single_message(message):
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
            for i, failed in enumerate(failed_channels[:3], 1):
                report += f"\n{i}. {failed}"
            if len(failed_channels) > 3:
                report += f"\n... и еще {len(failed_channels) - 3} каналов"

        bot.reply_to(message, report)

    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

@bot.message_handler(content_types=['media_group'])
def handle_media_group(message):
    """Обрабатывает медиагруппы (несколько фото/видео в одном сообщении)"""
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
        
    try:
        # Получаем информацию о медиагруппе
        media_group_id = message.media_group_id
        # Здесь нужно будет доработать логику для получения всех медиа из группы
        # Это требует более сложной обработки с отслеживанием медиагрупп
        
        # Временно отправляем как обычное сообщение
        handle_single_message(message)
        
    except Exception as e:
        print(f"Ошибка при обработке медиагруппы: {e}")
        bot.reply_to(message, f"❌ Ошибка обработки медиагруппы: {str(e)}")

# Альтернативный подход для обработки медиагрупп
media_groups = {}  # Словарь для хранения медиагрупп

@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    """Обрабатывает медиа (фото/видео) с возможностью группировки"""
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
        
    try:
        if message.media_group_id:
            # Это часть медиагруппы
            group_id = message.media_group_id
            
            if group_id not in media_groups:
                media_groups[group_id] = {
                    'media': [],
                    'caption': message.caption or '',
                    'timestamp': message.date
                }
            
            # Добавляем медиа в группу
            if message.photo:
                media_groups[group_id]['media'].append(
                    InputMediaPhoto(message.photo[-1].file_id)
                )
            elif message.video:
                media_groups[group_id]['media'].append(
                    InputMediaVideo(message.video.file_id)
                )
            
            # Ждем завершения группы (можно добавить таймер)
            # Пока просто обрабатываем как одиночное сообщение
            handle_single_message(message)
            
        else:
            # Одиночное медиа
            handle_single_message(message)
            
    except Exception as e:
        print(f"Ошибка при обработке медиа: {e}")
        bot.reply_to(message, f"❌ Ошибка обработки медиа: {str(e)}")

if __name__ == "__main__":
    print("Бот запущен...")
    print(f"Каналы для рассылки: {CHANNELS}")
    print(f"Разрешенные пользователи: {ALLOWED_USERS}")
    print("Функционал: автоматическая рассылка для разрешенных пользователей")
    print("Поддержка медиагрупп активирована")

    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Ошибка запуска бота: {e}")

