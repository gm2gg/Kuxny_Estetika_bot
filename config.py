import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = "8377401163:AAGcgyx35JH8lOw1Xg5Jvm9slQp0hwPO724"
    CHANNEL_USERNAME = "@Estetika_Kyxni_shkafi"
    ADMIN_ID = 7631971482
    DATABASE_NAME = "bot_database.db"

    # Сообщения
    INFO_MESSAGE = "📋 Информация о нашем сервисе:\n\n• Мы предоставляем лучшие услуги\n• Работаем 24/7\n• Консультация бесплатно\n\n📞 Контакты: @ваш_контакт"
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