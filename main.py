import os
import telebot
from telebot import types

TOKEN = "8084945590:AAFpLPZes86ClO1NLNOUakPlM6OFZJFNxAo"
bot = telebot.TeleBot(TOKEN)

user_lang = {}  # Словарь для хранения выбранного языка по user_id

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Русский")
    btn2 = types.KeyboardButton("Қазақша")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Выберите язык / Тілді таңдаңыз:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Русский", "Қазақша"])
def set_language(message):
    user_lang[message.chat.id] = message.text
    lang = message.text

    if lang == "Русский":
        bot.send_message(message.chat.id, "Вы выбрали русский язык. Кто вы?",
                         reply_markup=role_keyboard("ru"))
    else:
        bot.send_message(message.chat.id, "Сіз қазақ тілін таңдадыңыз. Сіз кімсіз?",
                         reply_markup=role_keyboard("kz"))

def role_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if lang == "ru":
        markup.add("Создатель проекта", "Преподаватель", "Жюри")
    else:
        markup.add("Жоба авторы", "Мұғалім", "Қазылар")
    return markup

bot.polling()