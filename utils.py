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

# def get_date():
#     conn = sqlite3.connect('user_base.db')
#     cursor = conn.cursor()
#     cursor.execute(f'SELECT {column} FROM users WHERE ')
#     column_list = cursor.fetchall()
#     conn.commit()
#     conn.close()    
#     return column_list # [('-yGIB7rf?NKU0Dk',), (None,)]


def password_generation():
    chars = '+-/*!&$#?=@<>abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'    
    length = 15    
    password = ''
    for i in range(length):
        password += random.choice(chars)
    return password

def user_entry_date_handler(user_entry): # Обрабатываем ввод пользователя
    
    
    # [int(s) for s in user_entry.split() if s.isdigit()]
    if ',' in user_entry:
        user_entry = user_entry.replace(',', ' ')
    if '-го' in user_entry:
        user_entry = user_entry.replace('-го', '')
    date_list = [int(s) for s in user_entry.split() if s.isdigit()]
    for date in date_list:
        if date > 31:
            print('Похоже, вы ошиблись. Дата не может быть больше 31')
            
            
    p = ''
    for s in user_entry.split():          
        if s.isdigit() == True:      # Сделать append в список                  
            if user_entry.split().index(s) == len(user_entry.split()) - 1:
                p += s 
            else: p += s + ', '
    print(p)
    print(str(date_list))

    # 23 и 11
    # 23, 11, 15
    # 23-го


    




def payday_date_handker():   # Проверяем или дата не приходится на выходной
    pass






# Сделаю автоматический забор суммы для нас, а для остальных 
# предусмотрю возможность ввести приход в день прихода. 



if __name__ == "__main__":
    # user_entry_date_handler('23, 11, 15')
    user_entry_date_handler('23-го и 15-го, и  ещё 25-го    32')



# TODO Сделать при выборе команды НАСТРОЙКИ, чтобы спрашивал: "новый пользователь" и "меня пригласили".
# Если пригласили, то предлагает ввести логин и пароль.

# TODO Сделать, чтобы люди могли редактировать свои данные (и обновлялась база)