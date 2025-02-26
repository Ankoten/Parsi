import os
import telebot
import requests
from telebot import types
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

region_id = None
name = None
salary_to = 2147483647
salary_from = 0
time_day = None
data = None
k = 1


def send_vacancy(vac):
    salary = 'Цена не указана\n'
    if int(vac['salaryFrom']) != 0 and int(vac['salaryTo']) != 0:
        salary = f"от {vac['salaryFrom']} до {vac['salaryTo']}\n"
    elif int(vac['salaryFrom']) != 0 and int(vac['salaryTo']) == 0:
        salary = f"от {vac['salaryFrom']}\n"
    elif int(vac['salaryFrom']) == '0' and int(vac['salaryTo']) != 0:
        salary = f"до {vac['salaryTo']}\n"
    mes = f"{vac['vacancy']}\n" \
          f"Компания: {vac['employer']}\n" + salary +\
          f"Адреc: {vac['address']} \n" \
          f"Требования: {vac['requirement']}\n" \
          f"Описание: {vac['requirement']}\n" \
          f"{vac['timeDay']}\n" \
          f"Дата публикации: {vac['time']}\n" \
          f"Ссылка: {vac['alternate_url']}"
    return mes


@bot.message_handler(commands=['start', 'menu'])
def start(message):
    global k
    k = 1
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton("Найти вакансию")
    markup.add(btn)
    bot.send_message(message.chat.id, "HI,это бот для поиска вакансий, начнём?",
                     reply_markup=markup)
    bot.register_next_step_handler(message, open_search)


def open_search(message):
    if message.text == "Найти вакансию":
        bot.send_message(message.chat.id, "Введите регион, в котором ищите вакансию",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_id_region)
    else:
        bot.send_message(message.chat.id, "Ошибочка",
                         reply_markup=types.ReplyKeyboardRemove())


def get_id_region(message):
    url = f"http://Mainapp:5000/region/{message.text}"
    data = requests.get(url).json()
    global region_id
    if data.get('id') is not None:
        region_id = data["id"]
        bot.send_message(message.chat.id, "Введите название профессии")
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(message.chat.id, "Ошибка,этого региона не существует")
        bot.register_next_step_handler(message, get_id_region)


def get_name(message):
    global name
    name = message.text.replace(" ", "+")
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton("Пропустить")
    markup.add(btn)
    bot.send_message(message.chat.id, "Введите нижнюю граниу ЗП",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_salary_from)


def get_salary_from(message):
    global salary_from
    if message.text != "Пропустить":
        salary_from = message.text
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton("Пропустить")
    markup.add(btn)
    bot.send_message(message.chat.id, "Введите верхнюю граниу ЗП",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_salary_to)


def get_salary_to(message):
    global salary_to
    if message.text != "Пропустить":
        salary_to = message.text
    markup = types.ReplyKeyboardMarkup()
    td1 = types.KeyboardButton("Полная занятость")
    td2 = types.KeyboardButton("Частичная занятость")
    markup.row(td1, td2)
    btn = types.KeyboardButton("Пропустить")
    markup.row(btn)
    bot.send_message(message.chat.id, "Выберете график",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_time_day)


def get_time_day(message):
    global time_day
    if message.text != "Пропустить":
        time_day = message.text
    url = f"http://Mainapp:5000/vacancy?vacancy={name}&salaryFrom={salary_from}&salaryTo={salary_to}&" \
          f"timeDay={time_day}&area={region_id}"
    global data
    data = requests.get(url).json()
    if not data:
        bot.send_message(message.chat.id, "Вакансий по запросу не найдено", reply_markup=types.ReplyKeyboardRemove())
    else:
        vac = data[0]
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton("Следующая")
        btn2 = types.KeyboardButton("Меню")
        markup.row(btn1,btn2)
        bot.send_message(message.chat.id, send_vacancy(vac), reply_markup=markup)
        bot.register_next_step_handler(message, next_vacancy)


def next_vacancy(message):
    global k
    if message.text == 'Следующая' and k < len(data)-1:
        vac = data[k]
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton("Следующая")
        btn2 = types.KeyboardButton("Меню")
        markup.row(btn1, btn2)
        bot.send_message(message.chat.id, send_vacancy(vac), reply_markup=markup)
        k += 1
        bot.register_next_step_handler(message, next_vacancy)
    elif message.text == 'Следующая' and k == len(data)-1:
        vac = data[k]
        markup = types.ReplyKeyboardMarkup()
        btn = types.KeyboardButton("Меню")
        markup.add(btn)
        bot.send_message(message.chat.id, send_vacancy(vac), reply_markup=markup)
        bot.register_next_step_handler(message, start)
    elif message.text == 'Меню':
        bot.send_message(message.chat.id, "Напишите /menu", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Команда не распознана",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, next_vacancy)


bot.polling(none_stop=True)