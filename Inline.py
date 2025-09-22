import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
import time
import threading

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
    keyboard = InlineKeyboardMarkup(row_width=1)  # 1 кнопка в строке

    button1 = InlineKeyboardButton(
        text="👨‍💻 Связаться с дизайнером",
        url="https://t.me/Estetika_kuhni_bot"
    )

    button2 = InlineKeyboardButton(
        text="📐 Прислать проект",
        url="https://t.me/Estetika_admi?start=project_calculation"
    )

    button3 = InlineKeyboardButton(
        text="📏 Выезд на замер",
        url="https://t.me/Estetika_admi?start=measurement_visit"
    )

    button4 = InlineKeyboardButton(
        text="⭐ Отзывы",
        url="https://t.me/Etetika_prorkti"
    )

    button5 = InlineKeyboardButton(
        text="🏠 Реализованные проекты",
        url="https://t.me/Etetika_prorkti"
    )

    # Все кнопки в один столбец
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    keyboard.add(button4)
    keyboard.add(button5)
    
    return keyboard


def send_media_group_with_caption(channel, media_list, caption_text):
    """Отправляет медиагруппу с подписью и кнопками в одном сообщении"""
    try:
        # Добавляем подпись к первому медиа
        if media_list and len(media_list) > 0:
            # Создаем копию первого медиа с подписью
            first_media = media_list[0]

            # В зависимости от типа медиа создаем новый объект с подписью
            if isinstance(first_media, InputMediaPhoto):
                media_list[0] = InputMediaPhoto(
                    first_media.media,
                    caption=caption_text,
                    parse_mode='HTML'
                )
            elif isinstance(first_media, InputMediaVideo):
                media_list[0] = InputMediaVideo(
                    first_media.media,
                    caption=caption_text,
                    parse_mode='HTML'
                )

        # Отправляем медиагруппу с подписью
        bot.send_media_group(channel, media_list)

        # Отправляем кнопки ОТДЕЛЬНЫМ сообщением после медиагруппы
        keyboard = create_keyboard()
        bot.send_message(channel, "Для связи используйте кнопки ниже👇", reply_markup=keyboard)

        return True
    except Exception as e:
        print(f"❌ Ошибка отправки медиагруппы в {channel}: {e}")
        return False


def process_media_group(group_id):
    """Обрабатывает собранную медиагруппу"""
    if group_id not in media_groups:
        return

    group_data = media_groups[group_id]

    # Ждем немного, чтобы все медиа успели прийти
    time.sleep(1.5)

    if len(group_data['media']) == 0:
        return

    # Формируем окончательный текст
    caption_text = group_data['caption'] if group_data['caption'] else ""

    # Отправляем во все каналы
    success_count = 0
    failed_channels = []

    for channel in CHANNELS:
        try:
            if send_media_group_with_caption(channel, group_data['media'].copy(), caption_text):
                success_count += 1
                print(f"✅ Медиагруппа отправлена в канал: {channel}")
            else:
                failed_channels.append(f"{channel} - ошибка отправки")
        except Exception as e:
            print(f"❌ Ошибка отправки в {channel}: {e}")
            failed_channels.append(f"{channel} - {str(e)}")

    # Отправляем отчет пользователю
    report = f"✅ Медиагруппа ({len(group_data['media'])} фото/видео) отправлена в {success_count} из {len(CHANNELS)} каналов"
    if failed_channels:
        report += f"\n\n❌ Не удалось отправить в {len(failed_channels)} каналов:"
        for i, failed in enumerate(failed_channels[:3], 1):
            report += f"\n{i}. {failed}"
        if len(failed_channels) > 3:
            report += f"\n... и еще {len(failed_channels) - 3} каналов"

    bot.send_message(group_data['user_id'], report)

    # Удаляем обработанную группу
    if group_id in media_groups:
        del media_groups[group_id]


@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    """Обрабатывает медиа (фото/видео) с группировкой"""
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
                    'user_id': message.from_user.id,
                    'last_update': time.time(),
                    'timer': None
                }

            # Добавляем медиа в группу
            if message.photo:
                media_item = InputMediaPhoto(message.photo[-1].file_id)
                media_groups[group_id]['media'].append(media_item)
            elif message.video:
                media_item = InputMediaVideo(message.video.file_id)
                media_groups[group_id]['media'].append(media_item)

            # Обновляем подпись (берем из последнего сообщения с подписью)
            if message.caption:
                media_groups[group_id]['caption'] = message.caption

            # Обновляем время последнего добавления
            media_groups[group_id]['last_update'] = time.time()

            # Отменяем предыдущий таймер и запускаем новый
            if media_groups[group_id]['timer']:
                media_groups[group_id]['timer'].cancel()

            # Запускаем обработку группы через 2 секунды (ждем все медиа)
            timer = threading.Timer(2.0, process_media_group, [group_id])
            media_groups[group_id]['timer'] = timer
            timer.start()

        else:
            # Одиночное медиа - обрабатываем сразу
            handle_single_media(message)

    except Exception as e:
        print(f"Ошибка при обработке медиа: {e}")
        bot.reply_to(message, f"❌ Ошибка обработки медиа: {str(e)}")


def handle_single_media(message):
    """Обрабатывает одиночное медиа (фото/видео)"""
    try:
        caption_text = "Для связи используйте кнопки ниже👇"
        if message.caption:
            caption_text = f"{message.caption}\n\n{caption_text}"
        else:
            caption_text = f"{caption_text}"

        content_type = None
        content_data = None

        # Определяем тип контента
        if message.photo:
            content_type = 'photo'
            content_data = message.photo[-1].file_id
        elif message.video:
            content_type = 'video'
            content_data = message.video.file_id

        # Отправляем во все каналы
        success_count = 0
        failed_channels = []

        for channel in CHANNELS:
            try:
                if content_type == 'photo':
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

                print(f"✅ Отправлено в канал: {channel}")

            except Exception as e:
                print(f"❌ Ошибка отправки в {channel}: {e}")
                failed_channels.append(f"{channel} - {str(e)}")

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
        print(f"Ошибка при обработке одиночного медиа: {e}")
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")


@bot.message_handler(content_types=['text', 'document'])
def handle_text_and_documents(message):
    """Обрабатывает текст и документы"""
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return

    try:
        caption_text = "Для связи используйте кнопки ниже👇"
        if message.text:
            caption_text = f"{message.text}\n\n{caption_text}"
        elif message.caption:
            caption_text = f"{message.caption}\n\n{caption_text}"

        content_type = 'text'
        content_data = None

        if message.document:
            content_type = 'document'
            content_data = message.document.file_id

        # Отправляем во все каналы
        success_count = 0
        failed_channels = []

        for channel in CHANNELS:
            try:
                if content_type == 'document':
                    bot.send_document(
                        channel,
                        content_data,
                        caption=caption_text,
                        reply_markup=create_keyboard()
                    )
                else:
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

        # Формируем отчет
        report = f"✅ Сообщение отправлено в {success_count} из {len(CHANNELS)} каналов"

        if failed_channels:
            report += f"\n\n❌ Не удалось отправить в {len(failed_channels)} каналов:"
            for i, failed in enumerate(failed_channels[:3], 1):
                report += f"\n{i}. {failed}"
            if len(failed_channels) > 3:
                report += f"\n... и еще {len(failed_channels) - 3} каналов"

        bot.reply_to(message, report)

    except Exception as e:
        print(f"Ошибка при обработке текста/документа: {e}")
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")


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


