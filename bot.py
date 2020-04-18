'''
Создать чат-бот для оформления заявки на потребительский кредит.
Цель – минимизировать объем полей, заполняемых клиентом.
Максимальное количество полей должно быть заполнено из открытых источников без нарушения Федерального закона  № 152-ФЗ «О персональных данных»
'''

import config
import telebot
from telebot import types  # кнопки
from string import Template
import telebot

bot = telebot.TeleBot(config.token)

user_dict = {}

class User:
    def __init__(self, city):
        self.city = city

        keys = ['fullname', 'phone', 'driverSeria',
                'driverNumber', 'driverDate']

        for key in keys:
            self.key = None


# если /help, /start
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn1 = types.KeyboardButton('/about')
    itembtn2 = types.KeyboardButton('/registation')

    markup.add(itembtn1, itembtn2)

    bot.send_message(message.chat.id, "Здравствуйте "
                     + message.from_user.first_name
                     + ", я бот, чтобы вы хотели узнать?", reply_markup=markup)


# /about
@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(message.chat.id, "В боте вы можете ввести свои данные для оформления завки на потре")


# /reg
@bot.message_handler(commands=["reg"])
def credit_period(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('1 год')
    itembtn2 = types.KeyboardButton('2 года')
    itembtn3 = types.KeyboardButton('3 года')
    itembtn4 = types.KeyboardButton('4 года')
    itembtn5 = types.KeyboardButton('5 лет')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)

    msg = bot.send_message(message.chat.id, 'Срок кредита', reply_markup=markup)
    bot.register_next_step_handler(msg, process_period_step)


def process_period_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = User(message.text)

        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, 'Фамилия Имя Отчество', reply_markup=markup)
        bot.register_next_step_handler(msg, process_fullname_step)

    except Exception as e:
        bot.reply_to(message, 'ooops!!')


def process_fullname_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.fullname = message.text

        msg = bot.send_message(chat_id, 'Ваш номер телефона')
        bot.register_next_step_handler(msg, process_phone_step)

    except Exception as e:
        bot.reply_to(message, 'ooops!!')


def process_phone_step(message):
    try:
        int(message.text)

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.phone = message.text

        msg = bot.send_message(chat_id, 'Сумма кредита')
        bot.register_next_step_handler(msg, process_driverSeria_step)

    except Exception as e:
        msg = bot.reply_to(message, 'Вы ввели что то другое. Пожалуйста введите номер телефона.')
        bot.register_next_step_handler(msg, process_phone_step)


def process_driverSeria_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.driverSeria = message.text

        msg = bot.send_message(chat_id, 'Введите e-mail')
        bot.register_next_step_handler(msg, process_driverNumber_step)

    except Exception as e:
        bot.reply_to(message, 'ooops!!')


def process_driverNumber_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.driverNumber = message.text

        msg = bot.send_message(chat_id, 'День рождения\nВ формате: День.Месяц.Год')
        bot.register_next_step_handler(msg, process_carDate_step)

    except Exception as e:
        bot.reply_to(message, 'ooops!!')

def process_carDate_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.carDate = message.text

        # ваша заявка "Имя пользователя"
        bot.send_message(chat_id, getRegData(user, 'Ваша заявка', message.from_user.first_name), parse_mode="Markdown")
        # отправить в группу
        #bot.send_message(config.chat_id, getRegData(user, 'Заявка от бота', bot.get_me().username), parse_mode="Markdown")
        # print(config.chat_id)
    except Exception as e:
        bot.reply_to(message, 'ooops!!')


# формирует вид заявки регистрации
# нельзя делать перенос строки Template
# в send_message должно стоять parse_mode="Markdown"
def getRegData(user, title, name):
    t = Template(
        '$title *$name* \n Срок кредита: *$userCity* \n ФИО: *$fullname* \n Телефон: *$phone* \n Сумма: *$driverSeria* \n Дата рождения: *$driverNumber* \n ')

    return t.substitute({
        'title': title,
        'name': name,
        'userCity': user.city,
        'fullname': user.fullname,
        'phone': user.phone,
        'driverSeria': user.driverSeria,
        'driverNumber': user.driverNumber,
        #'driverDate': user.driverDate,
    })


# произвольный текст
@bot.message_handler(content_types=["text"])
def send_help(message):
    bot.send_message(message.chat.id, 'О нас - /about\nРегистрация - /reg\nПомощь - /help')


# произвольное фото
@bot.message_handler(content_types=["photo"])
def send_help_text(message):
    bot.send_message(message.chat.id, 'Напишите текст')


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)
