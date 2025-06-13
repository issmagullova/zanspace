import os
import telebot
from Flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_lang = {}  # Словарь для хранения выбранного языка по user_id

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton("Русский"), telebot.types.KeyboardButton("Қазақша"))
    bot.send_message(message.chat.id, "Выберите язык / Тілді таңдаңыз:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Русский", "Қазақша"])
def choose_language(message):
    lang = message.text
    user_lang[message.chat.id] = lang
    if lang == "Русский":
        bot.send_message(message.chat.id, "Вы выбрали русский язык. Кто вы?",
                         reply_markup=role_keyboard("ru"))
    else:
        bot.send_message(message.chat.id, "Сіз қазақ тілін таңдадыңыз. Сіз кімсіз?",
                         reply_markup=role_keyboard("kz"))

def role_keyboard(lang):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if lang == "ru":
        markup.add("Создатель проекта", "Преподаватель", "Жюри")
    else:
        markup.add("Жоба авторы", "Мұғалім", "Қазылар")
    return markup

# 📡 Webhook route
@app.route('/' + TOKEN, methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# 🌐 Ping route
@app.route('/')
def index():
    return "Bot is running via webhook"

if name == '__main__':
    # 🔗 Установка webhook
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))