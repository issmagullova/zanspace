import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Токен бота
TOKEN = os.getenv("BOT_TOKEN") 
bot = telebot.TeleBot(TOKEN)

# Храним язык пользователя
user_lang = {}

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("Қазақша 🇰🇿", callback_data="lang_kz")
    btn2 = InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Тілді таңдаңыз / Выберите язык / Choose a language:", reply_markup=markup)

# Обработка выбора языка
@bot.callback_query_handler(func=lambda call: call.data in ["lang_kz", "lang_ru"])
def handle_language_selection(call):
    lang = call.data.split("_")[1]  # "kz" или "ru"
    user_lang[call.message.chat.id] = lang

    if lang == "ru":
        bot.send_message(call.message.chat.id, "Вы выбрали русский язык. Кто вы?", reply_markup=role_keyboard("ru"))
    else:
        bot.send_message(call.message.chat.id, "Сіз қазақ тілін таңдадыңыз. Сіз кімсіз?", reply_markup=role_keyboard("kz"))

# Клавиатура с ролями
def role_keyboard(lang):
    markup = InlineKeyboardMarkup(row_width=1)
    if lang == "ru":
        markup.add(
            InlineKeyboardButton("Создатель проекта", callback_data="role_creator"),
            InlineKeyboardButton("Преподаватель", callback_data="role_teacher"),
            InlineKeyboardButton("Жюри", callback_data="role_jury")
        )
    else:
        markup.add(
            InlineKeyboardButton("Жоба авторы", callback_data="role_creator"),
            InlineKeyboardButton("Мұғалім", callback_data="role_teacher"),
            InlineKeyboardButton("Қазылар", callback_data="role_jury")
        )
    return markup

# Обработка выбора роли
@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def handle_role_selection(call):
    role = call.data.split("_")[1]
    lang = user_lang.get(call.message.chat.id, "ru")

    if lang == "ru":
        if role == "creator":
            bot.send_message(call.message.chat.id, "🔍 Введите описание проекта, я проанализирую его на юридические риски.")
        elif role == "teacher":
            bot.send_message(call.message.chat.id, "📚 Я помогу вам ориентироваться в Кодексах РК для преподавания.")
        elif role == "jury":
            bot.send_message(call.message.chat.id, "🧑‍⚖️ Я подскажу, какие юридические вопросы можно задать участникам.")
    else:
        if role == "creator":
            bot.send_message(call.message.chat.id, "🔍 Жобаны сипаттаңыз, мен оны құқықтық тәуекелдерге талдаймын.")
        elif role == "teacher":
            bot.send_message(call.message.chat.id, "📚 Мен ҚР кодекстерімен жұмыс істеуге көмектесемін.")
        elif role == "jury":
            bot.send_message(call.message.chat.id, "🧑‍⚖️ Мен жобаларға қоятын құқықтық сұрақтарды ұсынамын.")

# Запуск бота
bot.polling()