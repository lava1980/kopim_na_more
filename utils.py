import datetime
import logging
import random
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                    level = logging.INFO,
                    filename = 'tgbot.log'
                    )


def get_inline_keyboard():
    inlinekeyboard = [[InlineKeyboardButton('Новый пользователь', callback_data='new_user'),
                        InlineKeyboardButton('Меня пригласили', callback_data='invited_user')]]
    kbd_markup = InlineKeyboardMarkup(inlinekeyboard)
    return kbd_markup

def pay_day_inline_keyboard1():
    inlinekeyboard = [[InlineKeyboardButton('Да', callback_data='yes'),
                        InlineKeyboardButton('Нет', callback_data='no')]]
    kbd_markup = InlineKeyboardMarkup(inlinekeyboard)
    return kbd_markup

def create_user_base():
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                    (family_id text PRIMARY KEY, chat_id text, first_name text, purpose text, 
                    purpose_date text, current_sum integer, payday_dates text, 
                    every_month_purp_sum text, secret_key text)''' # secret_key для приглашения членов семьи
                    )
    conn.commit()
    conn.close()

def get_initial_data(update):    
    query = update.callback_query
    chat_id = query.message.chat_id
    first_name = query.message.chat.first_name
    initial_user_data = (chat_id, first_name)
    return initial_user_data

def write_initial_data_to_base(data):
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (chat_id, first_name) VALUES (?, ?)', data)
    conn.commit()
    conn.close()

def write_entry_to_base(stage, entry, id):
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET {stage}=? WHERE chat_id=?', (entry, id))
    conn.commit()
    conn.close()    

def list_from_base_column(column): # Возвращает список значений столбца
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT {column} FROM users')
    column_list = cursor.fetchall()
    conn.commit()
    conn.close()    
    return column_list # [('-yGIB7rf?NKU0Dk',), (None,)]

def update_invited_user_data(chatid):
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE users SET purpose=Null, purpose_date=Null, 
        current_sum=Null, payday_dates=Null, every_month_purp_sum=Null WHERE chat_id=?''', 
        (chatid,)
        )
    conn.commit()
    conn.close()

def get_date_string(column, chat_id):
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT {column} FROM users WHERE chat_id=?', (chat_id,))
    date_list = cursor.fetchone()
    conn.commit()
    conn.close()    
    date_list = date_list[0].split(', ') 
    print(date_list)   
    return date_list

def select_family_list(password):
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT chat_id, secret_key FROM users WHERE secret_key=?', (password,))
    date_list = cursor.fetchall()
    conn.commit()
    conn.close()        
    print(date_list)   
    return date_list


def select_subscribers():    
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT chat_id, payday_dates, secret_key FROM users'
        )
    subscribers_list = cursor.fetchall()
    conn.commit()
    conn.close()          
    return subscribers_list

def get_subscribers_send_to(date_str): # '11'
    subs_list = select_subscribers()
    subs_list_send_to = []
    for subscriber in subs_list:
        date_list = subscriber[1].split(', ')
        if date_str in date_list:
            subs_list_send_to.append(subscriber)
    print(list(subs_list_send_to))
    return subs_list_send_to # [('891850606', '2, 1, 13', '-yGIB7rf?NKU0Dk')]


    






def password_generation():
    chars = '+-/*!&$#?=@<>abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'    
    length = 15    
    password = ''
    for i in range(length):
        password += random.choice(chars)
    return password

def user_entry_date_handler(user_entry, update): # Обрабатываем ввод пользователя
    if ',' in user_entry:
        user_entry = user_entry.replace(',', ' ')
    if '-го' in user_entry:
        user_entry = user_entry.replace('-го', '')           
    date_list = []
    for s in user_entry.split():          
        if s.isdigit() == True:                 
            date_list.append(s)
    for date in date_list:
        if int(date) > 31:
            update.message.reply_text(
                'Похоже, вы ввели неверное число. Дата не может быть больше 31. Введите правильные даты прихода. Например, 11 и 23')            
            return 'payday_dates'    
    date_list.sort()
    dates_str_to_base = ', '.join(date_list)
    return dates_str_to_base
        
def payday_date_handler(date_from_base):   # Число в строке '15'
    today_date = datetime.datetime.now().day
    if int(date_from_base) == today_date:
        print(date_from_base)
        return date_from_base
           
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_date = tomorrow.day # 27
    day_of_week_tomorr = tomorrow.isoweekday() # 5
    if int(date_from_base) == tomorrow_date:
        if day_of_week_tomorr == 6:
            print(today_date)
            return today_date

    after_tomorrow = datetime.date.today() + datetime.timedelta(days=2)
    after_tomorrow_date = after_tomorrow.day # 28
    day_of_week_after_tomorr = after_tomorrow.isoweekday() # 6
    if int(date_from_base) == after_tomorrow_date:
        if day_of_week_after_tomorr == 7:
            print(today_date)
            return today_date
    
    print(date_from_base)
    return date_from_base

# Сделать, чтобы когда зарплата приходится на выходной, чтобы челу потом и в выходной не 
# приходило уведомление

# def is_weekend(delta, date_from_base):
#     date = datetime.date.today() + datetime.timedelta(days=delta)
#     date_day = date.day # 27
#     day_of_week = date.isoweekday() # 5
#     if int(date_from_base) == date_day:
#         if day_of_week == 6:
#             print('День выдачи з/п приходится на выходной.')
#             return True






# Сделаю автоматический забор суммы для нас, а для остальных 
# предусмотрю возможность ввести приход в день прихода. 



if __name__ == "__main__":        
    payday_date_handler('30')
    # get_subscribers_send_to('3')
    # select_family_list('$DDMsf!cIzpyehr')



# TODO Сделать при выборе команды НАСТРОЙКИ, чтобы спрашивал: "новый пользователь" и "меня пригласили".
# Если пригласили, то предлагает ввести логин и пароль.

# TODO Сделать, чтобы люди могли редактировать свои данные (и обновлялась база)