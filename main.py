import os
import requests
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_lang = {}
user_role = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Қазақша 🇰🇿", callback_data="lang_kz"),
        InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")
    )
    bot.send_message(message.chat.id, "Тілді таңдаңыз / Выберите язык:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_language(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang

    if lang == "ru":
        msg = "Вы выбрали русский язык. Кто вы?"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Создатель проекта", callback_data="role_creator"),
            InlineKeyboardButton("Преподаватель", callback_data="role_teacher"),
            InlineKeyboardButton("Жюри", callback_data="role_jury")
        )
    else:
        msg = "Сіз қазақ тілін таңдадыңыз. Сіз кімсіз?"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Жоба авторы", callback_data="role_creator"),
            InlineKeyboardButton("Мұғалім", callback_data="role_teacher"),
            InlineKeyboardButton("Қазылар", callback_data="role_jury")
        )
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def handle_role(call):
    role = call.data.split("_")[1]
    lang = user_lang.get(call.from_user.id, "ru")
    user_role[call.from_user.id] = role

    if lang == "ru":
        if role == "creator":
            bot.send_message(call.message.chat.id, "🧠 Расскажи о своём проекте, и я подскажу правовые риски!")
        elif role == "teacher":
            bot.send_message(call.message.chat.id, "📚 Я помогу вам сориентироваться в Кодексах РК для преподавания.")
        elif role == "jury":
            bot.send_message(call.message.chat.id, "⚖️ Я помогу задать юридические вопросы участникам.")
    else:
        if role == "creator":
            bot.send_message(call.message.chat.id, "🧠 Жобаңызды сипаттаңыз, мен заңдық тәуекелдерді айтамын!")
        elif role == "teacher":
            bot.send_message(call.message.chat.id, "📚 Мен оқыту үшін ҚР кодекстерін түсіндіруге көмектесемін.")
        elif role == "jury":
            bot.send_message(call.message.chat.id, "⚖️ Мен қатысушыларға қоятын заң сұрақтарын ұсынамын.")

def generate_prompt(lang, role):
    if lang == "ru":
        if role == "creator":
            return (
                "Ты — ИИ-юрист. Обрати внимание: этот ответ не является юридической консультацией, а только рекомендацией. "
                "Оцени проект ниже по законодательству Казахстана, определи риски, пробелы в документах и рекомендации:\n\n"
            )
    else:
        if role == "creator":
            return (
                "Сіз — заңгер ретінде әрекет ететін жасанды интеллектсіз. Назар аударыңыз: бұл жауап тек кеңес, заңдық күшке ие емес. "
                "Қазақстан заңнамасына сәйкес жобаны бағалап, тәуекелдерді анықтаңыз:\n\n"
            )
    return "Оцени проект на основе законодательства Казахстана."

@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_message(message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "ru")
    role = user_role.get(user_id)

    if role == "creator":
        bot.send_message(message.chat.id, "⏳ Проект в обработке, подождите 20–30 секунд...")
        prompt = generate_prompt(lang, role) + message.text
        reply = ask_openrouter(prompt)
        bot.send_message(message.chat.id, reply)
    else:
        bot.send_message(message.chat.id, "⚠️ Эта функция сейчас доступна только для создателей проекта.")

def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://openrouter.ai",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-ai/deepseek-r1-0528:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        response = r.json()
        print("DEBUG:", response)
        if "choices" in response:
            return response["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Ошибка: модель не вернула ответ. Ответ API: {response}"
    except Exception as e:
        return f"⚠️ Ошибка при подключении к ИИ: {e}"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))