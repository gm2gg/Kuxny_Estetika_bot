import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
import time
import threading

bot = telebot.TeleBot('YOUR_BOT_TOKEN')

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

# Глобальный словарь для хранения медиагрупп
media_groups = {}


def is_user_allowed(user_id):
    """Проверяет, есть ли у пользователя доступ"""
    return user_id in ALLOWED_USERS


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
    bot.reply_to(message,
                 "Добро пожаловать! Отправьте мне любое сообщение (текст, фото, видео), и я перешлю его во все каналы с кнопками для связи.")


@bot.message_handler(commands=['channels'])
def show_channels(message):
    """Показывает список каналов для рассылки"""
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
    channels_list = "\n".join([f"• {channel}" for channel in CHANNELS])
    bot.reply_to(message, f"📢 Каналы для рассылки:\n{channels_list}\n\nВсего: {len(CHANNELS)} каналов")


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


def send_media_group_with_caption(channel, media_list, caption_text):
    """Отправляет медиагруппу с подписью и кнопками"""
    try:
        # Ограничиваем длину подписи (1024 символа - лимит Telegram)
        if caption_text and len(caption_text) > 1024:
            caption_text = caption_text[:1020] + "..."

        # Добавляем подпись только к первому медиа
        if media_list and len(media_list) > 0:
            first_media = media_list[0]
            if isinstance(first_media, InputMediaPhoto):
                media_list[0] = InputMediaPhoto(first_media.media, caption=caption_text)
            elif isinstance(first_media, InputMediaVideo):
                media_list[0] = InputMediaVideo(first_media.media, caption=caption_text)

        # Отправляем медиагруппу
        bot.send_media_group(channel, media_list)

        # Отправляем кнопки одним сообщением
        keyboard = create_keyboard()
        bot.send_message(channel, "Для связи используйте кнопки ниже 👇", reply_markup=keyboard)

        return True
    except Exception as e:
        print(f"❌ Ошибка отправки в {channel}: {e}")
        return False


def send_single_media(channel, content_type, content_data, caption_text):
    """Отправляет одиночное медиа"""
    try:
        # Ограничиваем длину подписи
        if caption_text and len(caption_text) > 1024:
            caption_text = caption_text[:1020] + "..."

        keyboard = create_keyboard()

        if content_type == 'photo':
            bot.send_photo(channel, content_data, caption=caption_text, reply_markup=keyboard)
        elif content_type == 'video':
            bot.send_video(channel, content_data, caption=caption_text, reply_markup=keyboard)
        elif content_type == 'document':
            bot.send_document(channel, content_data, caption=caption_text, reply_markup=keyboard)
        else:  # text
            bot.send_message(channel, caption_text, reply_markup=keyboard)

        return True
    except Exception as e:
        print(f"❌ Ошибка отправки в {channel}: {e}")
        return False


def process_media_group(group_id):
    """Обрабатывает собранную медиагруппу"""
    if group_id not in media_groups:
        return

    group_data = media_groups[group_id]
    time.sleep(2)  # Ждем сбор всех медиа

    if len(group_data['media']) == 0:
        return

    user_id = group_data['user_id']
    caption_text = group_data['caption'] or ""

    # Добавляем стандартный текст только если есть место
    if caption_text and len(caption_text) < 900:
        caption_text += "\n\nДля связи используйте кнопки ниже 👇"

    success_count = 0
    failed_channels = []

    for channel in CHANNELS:
        try:
            if send_media_group_with_caption(channel, group_data['media'].copy(), caption_text):
                success_count += 1
                print(f"✅ Медиагруппа отправлена в {channel}")
            else:
                failed_channels.append(channel)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            failed_channels.append(channel)

    # Отчет пользователю
    report = f"✅ Медиагруппа ({len(group_data['media'])} медиа) отправлена в {success_count}/{len(CHANNELS)} каналов"
    if failed_channels:
        report += f"\n❌ Ошибки: {', '.join(failed_channels)}"

    bot.send_message(user_id, report)

    # Удаляем группу
    try:
        del media_groups[group_id]
    except:
        pass


@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    """Обрабатывает медиа"""
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ Нет доступа.")
        return

    try:
        if message.media_group_id:
            # Медиагруппа
            group_id = message.media_group_id

            if group_id not in media_groups:
                media_groups[group_id] = {
                    'media': [],
                    'caption': message.caption or "",
                    'user_id': message.from_user.id,
                    'timer': None
                }

            # Добавляем медиа
            if message.photo:
                media_item = InputMediaPhoto(message.photo[-1].file_id)
                media_groups[group_id]['media'].append(media_item)
            elif message.video:
                media_item = InputMediaVideo(message.video.file_id)
                media_groups[group_id]['media'].append(media_item)

            # Обновляем подпись
            if message.caption:
                media_groups[group_id]['caption'] = message.caption

            # Запускаем/перезапускаем таймер
            if media_groups[group_id]['timer']:
                media_groups[group_id]['timer'].cancel()

            timer = threading.Timer(2.0, process_media_group, [group_id])
            media_groups[group_id]['timer'] = timer
            timer.start()

        else:
            # Одиночное медиа
            handle_single_message(message)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(content_types=['text', 'document'])
def handle_single_message(message):
    """Обрабатывает одиночные сообщения"""
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ Нет доступа.")
        return

    try:
        # Формируем текст
        main_text = ""
        if message.text:
            main_text = message.text
        elif message.caption:
            main_text = message.caption

        caption_text = main_text
        if main_text and len(main_text) < 900:
            caption_text += "\n\nДля связи используйте кнопки ниже 👇"

        # Определяем тип контента
        content_type = 'text'
        content_data = None

        if message.photo:
            content_type = 'photo'
            content_data = message.photo[-1].file_id
        elif message.video:
            content_type = 'video'
            content_data = message.video.file_id
        elif message.document:
            content_type = 'document'
            content_data = message.document.file_id

        # Отправляем
        success_count = 0
        failed_channels = []

        for channel in CHANNELS:
            if send_single_media(channel, content_type, content_data, caption_text):
                success_count += 1
            else:
                failed_channels.append(channel)

        # Отчет
        report = f"✅ Сообщение отправлено в {success_count}/{len(CHANNELS)} каналов"
        if failed_channels:
            report += f"\n❌ Ошибки: {', '.join(failed_channels)}"

        bot.reply_to(message, report)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


if __name__ == "__main__":
    print("Бот запущен...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")