import requests
import json
import telebot
from telebot import types
import datetime
import time
from threading import Thread
from datetime import datetime, timedelta

#курсы валют
URL = 'https://www.cbr-xml-daily.ru/daily_json.js'

#коронавирус
URLc = 'https://api.thevirustracker.com/free-api?countryTotal=RU'

#собственно бот
# apihelper.proxy = {'https': 'https://31.14.131.70:8080',
#                    'http': 'http://31.14.131.70:8080',}

URLtime = 'https://api.thevirustracker.com/free-api?countryTimeline=RU'
data = json.loads(requests.get(URLtime).text)

def get_dates():
    date_format = '%d.%m.%Y'
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    return {'today': today.strftime("%m/%d/%y"),
            'yesterday': yesterday.strftime("%m/%d/%y"),}

yesterdayDate = str(get_dates()['yesterday'])

if(yesterdayDate[0] == '0'):
    yesterdayDate = yesterdayDate[1:8]

yesterdayCases = data['timelineitems'][0][yesterdayDate]['new_daily_cases']

bot = telebot.TeleBot("1133417779:AAEpat31ypweSvo843n8FfkWzvDmkazGiBY");

print('start')
isAuto = 0
userTime = ''

def covidInfo(call):
    covidData = json.loads(requests.get(URLc).text)
    curCovid = covidData['countrydata'][0]['total_cases']
    newCovid = covidData['countrydata'][0]['total_new_cases_today']
    msg = "Статистика по вирусу:\n" + "Всего в РФ: " + str(curCovid) + "\n" + "Новых за день +" + str(
        newCovid) + '\n' + "За вчерашний день было +" + str(yesterdayCases)
    bot.send_message(call.message.chat.id, msg)

def valuteInfo(call):
    moneyData = json.loads(requests.get(URL).text)
    curEur = round(moneyData['Valute']['EUR']['Value'], 2)
    curUsd = round(moneyData['Valute']['USD']['Value'], 2)
    prevEur = round(moneyData['Valute']['EUR']['Previous'], 2)
    prevUsd = round(moneyData['Valute']['USD']['Previous'], 2)
    difE = round(curEur - prevEur, 2)
    difU = round(curUsd - prevUsd, 2)
    if (curEur > prevEur):
        statusE = 'вырос'
    else:
        statusE = 'упал'
    if (curUsd > prevUsd):
        statusU = 'вырос'
    else:
        statusU = 'упал'
    msg = "Курсы валют на сейчас:\n" + "Евро: " + str(curEur) + ", " + statusE + "  (" + str(difE) + "), был " + str(
        prevEur) + "\n" + "Доллар: " + str(curUsd) + ", " + statusU + "  (" + str(difU) + "), был " + str(prevUsd)
    bot.send_message(call.message.chat.id, msg)

def mainPart():

    #метод получения текстовых сообщений
    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        if message.text == "/help":
            bot.send_message(message.from_user.id, "Введи /exchange чтобы получить курсы валют.\nВведи /covid чтобы получить статистику по коронавирусу. Или жми кнопки.")
            #bot.reply_to(message, "Введи /exchange для подписки на курсы валют.\n Введи /covid для подписки на статистику по коронавирусу.")
            if(isAuto == 1):
                bot.send_message(message.from_user.id, "Рассылка включена.")
            else:
                bot.send_message(message.from_user.id, "Рассылка отключена.")
        else: bot.send_message(message.from_user.id, "Введи /help для помощи.")

        keyboard = types.InlineKeyboardMarkup()
        key_covid = types.InlineKeyboardButton(text='Covid', callback_data='covid')
        keyboard.add(key_covid)
        key_valute = types.InlineKeyboardButton(text='Валюты', callback_data='valute')
        keyboard.add(key_valute)
        key_everyday = types.InlineKeyboardButton(text='Присылать автоматически', callback_data='everyday')
        keyboard.add(key_everyday)
        key_everydayOff = types.InlineKeyboardButton(text='Больше не присылать', callback_data='everydayTurnoff')
        keyboard.add(key_everydayOff)
    #кнопка отладки
        # key_everydayOff = types.InlineKeyboardButton(text='отладка', callback_data='TESTKEY')
        # keyboard.add(key_everydayOff)
        bot.send_message(message.from_user.id, text='Выбери функцию', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):

        if call.data == "covid":
            covidInfo(call)

        if call.data == "valute":
            valuteInfo(call)

        if call.data == "everyday":
            bot.send_message(call.message.chat.id, "Автоматическая рассылка включена. Новости каждый день в 12:00.")
            global isAuto
            isAuto = 1
            global callTemp
            callTemp = call

        if call.data =="everydayTurnoff":
            isAuto = 0
            bot.send_message(call.message.chat.id, "Автоматическая рассылка отключена.")

        if call.data == "TESTKEY":
            bot.send_message(call.message.chat.id, "Я не завис.")
    bot.polling()

def timerPart():
    while True:
        if isAuto == 1:
            now = datetime.datetime.now()
            if str(now.strftime("%H:%M")) == "12:00":
                bot.send_message(callTemp.message.chat.id, "Актуальная информация на сегодня:")
                covidInfo(callTemp)
                valuteInfo(callTemp)
        time.sleep(60)

th_1, th_2 = Thread(target=mainPart), Thread(target = timerPart)

if __name__ == '__main__':
    th_1.start(), th_2.start()
    th_1.join(), th_2.join()
