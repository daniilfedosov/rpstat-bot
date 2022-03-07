from base64 import encode
import datetime
from datetime import datetime
from dis import show_code
from re import I
import sqlite3
import time
import telebot
import os
import yaml
import sys
import metacheck
import requests
import numpy as np
import schedule

def metabase_env():
    config = yaml.safe_load(open(sys.path[0] + '/env.yml'))
    return config['environment']


def metabase(env, session=None):
    session_id = metacheck.Base(env=env, session=session, project=PROJECT).session
    print(session_id)
    base = metacheck.Base(session=session_id, env=env, project=PROJECT)
    return base

PROJECT = 'realdeposits'

TOKEN='5089328788:AAFJDC5ofQ7EVDN4GPHld_Ws228TXbD3OOA'
bot = telebot.TeleBot(TOKEN)



@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == "/check":
        bot.send_message(message.chat.id,'approved (past 24h): 100')
        save_history(message.text, message)

    if message.text == "/history":
        bot.send_message(message.chat.id, show_history())
        print("show_history:")
        print()

    if message.text == "/payments":
        print("main")
        bot.send_message(message.chat.id, main())  
    
    if message.text == "/percent":
        print("job")
        bot.send_message(message.chat.id, job())



def job() :
    print(main())
    schedule.every(2).minutes.do(job)
    while True :
        schedule.run_pending()
        time.sleep(1)




def show_history():

    connect = sqlite3.connect('rp-stat-bot.db')

    
    cursor = connect.cursor()

     
    cursor.execute("SELECT TelegramID, created_at, command_text FROM input_history")

   
    res = cursor.fetchall()

    mes = ""
    
    i = 0

  
    for r in res:
        print(mes)

        mes = "%s\n%s" % (str(r), mes)
        i = 1 + i 

    print(i)

    return mes

    
    

def save_history(command_text, message):
    connect = sqlite3.connect('rp-stat-bot.db')
    cursor = connect.cursor()

    uid = message.from_user.id  
    now = datetime.now()
    currenttime = now.strftime("%H:%M:%S")

    cursor.execute("INSERT INTO input_history (TelegramID, created_at, command_text) VALUES(?,?,?)", (uid, currenttime, command_text))
     
    connect.commit()

    connect.close()


def parse():

    env = metabase_env()
    base = metabase(env)

    # print(env) 

    count = (base.post('/card/%s/query/json' % env['realdeposits']['QUESTION_NUMBER_IN_URL']))
    print(count)

    return(count[1][0]['Count'])
    

def db_save(cnt_current, ts):

    # тут должен быть код который добавляет cnt_count в базу
    connect = sqlite3.connect('rp-stat-bot.db')
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS payments(
        numbers INTEGER, date TIMESTAMP
    )""")
                                            
    if (cnt_current != None):
        cursor.execute('INSERT INTO payments (numbers,date) VALUES (:numbers,:date)', {"numbers": cnt_current, "date": ts })
    
    

    connect.commit() 
    connect.close 

def db_fetch_prev():
    # тут должен быть SELECT последнего по ДАТЕ значения из базы
    connect = sqlite3.connect('rp-stat-bot.db')
    cursor = connect.cursor()
    cursor.execute("SELECT numbers FROM payments ORDER BY date DESC LIMIT 2")

    cursor_res = cursor.fetchall()
    cursor.close()
    return(cursor_res)

def percentage(part, whole):
  percentage = 100 * float(part)/float(whole)
  return str(percentage) + "%"
    


def main():

    number_approved = parse()

    ts = time.time()
    print(ts)
    
    print(number_approved)

    db_save(number_approved, ts)

    # cnt_prev = db_fetch_prev()
    print("Current approved count: %s" % number_approved)
    
    numbers = db_fetch_prev()


   
    n1 = numbers[0][0]
    n2 = numbers[1][0]
    print(n1,n2)


    if (n2 > 0):
        calc = float(n1)/float(n2)*100-100
    else:
        print("n2 is zero")
    
    
    print(calc)

    return(calc)


# main()
bot.polling(none_stop=True,interval=0)