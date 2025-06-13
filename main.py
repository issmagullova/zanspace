import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_lang = {}
user_role = {}

# Запуск
@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Қазақша 🇰🇿", callback_data="lang_kz"),
        InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")
    )
    bot.send_message(message.chat.id, "Тілді таңдаңыз / Выберите язык / Choose a language:", reply_markup=markup)

# Выбор языка
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_language(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang

    markup = InlineKeyboardMarkup()
    if lang == "ru":
        msg = "Вы выбрали русский язык. Кто вы?"
        markup.add(
            InlineKeyboardButton("Создатель проекта", callback_data="role_creator"),
            InlineKeyboardButton("Преподаватель", callback_data="role_teacher"),
            InlineKeyboardButton("Жюри", callback_data="role_jury")
        )
    else:
        msg = "Сіз қазақ тілін таңдадыңыз. Сіз кімсіз?"
        markup.add(
            InlineKeyboardButton("Жоба авторы", callback_data="role_creator"),
            InlineKeyboardButton("Мұғалім", callback_data="role_teacher"),
            InlineKeyboardButton("Қазылар", callback_data="role_jury")
        )
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup)

# Выбор роли
@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def handle_role(call):
    role = call.data.split("_")[1]
    lang = user_lang.get(call.from_user.id, "ru")
    user_role[call.from_user.id] = role

    prompt = generate_prompt(lang, role)
    reply = ask_openrouter(prompt)
    bot.send_message(call.message.chat.id, reply)

def generate_prompt(lang, role):
    if lang == "ru":
        if role == "creator":
            return "Ты — ИИ-юрист. Определи юридические риски проекта, подскажи документы и этапы легализации."
        elif role == "teacher":
            return "Ты — помощник преподавателя по бизнес-праву. Помоги адаптировать материал под школьный формат, дай задания и правовые кейсы."
        elif role == "jury":
            return "Ты — эксперт по стартапам. Быстро оцени легальность проекта и предложи вопросы участникам."
    else:
        if role == "creator":
            return "Сіз — жасанды интеллект заңгерісіз. Жобадағы заңды қауіптерді анықтаңыз, қажетті құжаттар мен тіркеу жолын түсіндіріңіз."
        elif role == "teacher":
            return "Сіз — бизнес құқығы пәнінің мұғаліміне көмекші ИИ. Мазмұнды бейімдеңіз, тапсырмалар мен құқықтық кейстер ұсыныңыз."
        elif role == "jury":
            return "Сіз — стартап сарапшысы. Жобаның заңдылығын бағалаңыз және қатысушыларға сұрақтар ұсыныңыз."
    return "Помоги с правовой оценкой проекта."

def generate_prompt(lang, role):
    # ... твой код генерации промпта ...
    return "Помоги с правовой оценкой проекта."


def ask_openrouter(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openchat/openchat-7b",
        "messages": [
            {"role": "system", "content": "Ты юридический помощник, эксперт в праве РК."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "❌ Ошибка при обращении к OpenRouter."

# Обработка текстовых сообщений от пользователя
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "ru")
    role = user_role.get(user_id)

    if role == "creator":
        prompt = generate_prompt(lang, role) + "\n\n" + message.text
        reply = ask_openrouter(prompt)
        bot.send_message(message.chat.id, reply)
    else:
        bot.send_message(message.chat.id, "⚠️ Эта функция сейчас доступна только для создателей проекта.")

# Запрос к OpenRouter
def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://openrouter.ai",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        response = r.json()
        print("DEBUG:", response)  # ← вот сюда вставь
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Ошибка при подключении к ИИ: {e}"

# Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Flask run
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))