import datetime
import locale
import logging
import random
import sqlite3
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import time

import config

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

def pay_day_inline_keyboard2(every_month_purp_sum, currency):
    inlinekeyboard = [
        [InlineKeyboardButton(str(every_month_purp_sum) + ' ' + currency, callback_data=str(every_month_purp_sum)),        
        InlineKeyboardButton('Другая', callback_data='other')],
        [InlineKeyboardButton('Пропустить', callback_data='pass_current_month')]                        ]
    kbd_markup = InlineKeyboardMarkup(inlinekeyboard)
    return kbd_markup

def purp_type_inline_keyboard():
    inlinekeyboard = [[InlineKeyboardButton('Отдых', callback_data='vacation'),
                        InlineKeyboardButton('Покупка', callback_data='purchase'), 
                        InlineKeyboardButton('Долг', callback_data='debt')], 
                        [InlineKeyboardButton('Другой тип', callback_data='other-type')]                        
                        ]
    kbd_markup = InlineKeyboardMarkup(inlinekeyboard)
    return kbd_markup

def handle_var_inside_text(dictionary, key):
    text_list = dictionary[key]
    text = random.choice(text_list)
    return text
  

def create_user_base():
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                    (chat_id text PRIMARY KEY, first_name text, purpose text, purpose_type text,
                    purpose_sum integer, purpose_date text, current_sum integer, 
                    charges integer, payday_dates text, secret_key text, 
                    purp_currency text, salary_currency text, save_in_this_month integer, 
                    sum_to_save_in_this_month integer)''' # secret_key для приглашения членов семьи
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

def update_invited_user_data(chatid, user_data_list):


    purpose, purpose_type, purpose_sum, purpose_date, \
        current_sum, payday_dates, secret_key, purp_currency, save_in_this_month, \
        sum_to_save_in_this_month = user_data_list
    
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE users SET purpose=?, purpose_type=?, purpose_sum=?, purpose_date=?, 
        current_sum=?, payday_dates=?, secret_key=?, purp_currency=?, save_in_this_month=?, 
        sum_to_save_in_this_month=? WHERE chat_id=?''', 
        (purpose, purpose_type, purpose_sum, purpose_date,
        current_sum, payday_dates, secret_key, purp_currency, save_in_this_month,
        sum_to_save_in_this_month, chatid)
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

def get_data_cell(column, chat_id):
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT {column} FROM users WHERE chat_id=?', (chat_id,))
    date_list = cursor.fetchone()
    conn.commit()
    conn.close()               
    return date_list[0]

def select_family_list(password):
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT chat_id, secret_key, role FROM users WHERE secret_key=?', (password,))
    date_list = cursor.fetchall()
    conn.commit()
    conn.close()            
    return date_list

def select_user_data(chat_id):
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute(
        f'SELECT purpose, purpose_type, purpose_sum, purpose_date, current_sum, \
payday_dates, secret_key, purp_currency, save_in_this_month, \
sum_to_save_in_this_month FROM users WHERE chat_id=?', 
        (chat_id,))
    date_list = cursor.fetchall()
    conn.commit()
    conn.close()        
    print(date_list[0])   
    return date_list[0]


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
    # chars = '+-/*!&$#?=@<>abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'    
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'    
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

def day_to_purp(chat_id, purpose_date):    
    purp_date = datetime.datetime.strptime(purpose_date, '%Y-%m-%d')
    today = datetime.datetime.today()
    delta = purp_date - today    
    return delta.days

def get_resume_text(context):
    left_days_to_purp = int(context.user_data['left_days_to_purp'])
    current_sum = int(context.user_data['current_sum'])
    purp_sum = int(context.user_data['purpose_sum'])
    left_to_collect = purp_sum - current_sum
    # save_per_month = left_to_collect / left_days_to_purp * 30
    save_per_month = left_to_collect / round(left_days_to_purp / 30)
    save_per_month = int(round(save_per_month/5.0)*5)   
    progres = int(round(current_sum / purp_sum * 100))
    currency = context.user_data['purp_currency']
    
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    date_str = datetime.datetime.strptime(context.user_data['purpose_date'], '%Y-%m-%d')
    date_str = date_str.strftime('%d %B %Y')

    text = f'''{config.EMOJI['megaphone']} <b>Ситуация на текущий момент:</b> 

{config.EMOJI['target']} Цель: {context.user_data['purpose']}
{config.EMOJI['calendar']} Дата цели: {date_str}
----------
{config.EMOJI['foot']} Осталось: {str(left_days_to_purp)} дней
{config.EMOJI['money_bag']} На сегодня собрали: {str(current_sum)} {currency}
{config.EMOJI['hand_right']} Осталось собрать: {str(left_to_collect)} {currency}

{config.EMOJI['bar_chart']} Цель выполнена на {str(progres)}%

{config.EMOJI['double_exclamation_mark']} План: ежемесячно откладывать <b>не менее {str(save_per_month)} {currency}</b>
'''     
    return text

# Что мне надо сделать? Мне надо:



# 1. Вытянуть из базы всех юзеров, у которых такой же пароль (chat_id).
# 2. Разослать им сообщение резюме

# Он нажал на кнопку получения инфы. И что? 

# Надо тчобы при нажатии на кнопку:
# 1. Определить кто это -- админ или член семьи, чтобы понимать, кому слать. А какая
# разница? Мне надо иметь чат-айди. Чтобы я мог слать сообщения. Мне надо просто понимать, 
# кому слать. 

# Если это человек, то у него уже есть чат-айди, мне надо просто ... и у него уже есть запись в базе.
# Мне просто надо её прочитать. Вот и всё, и не надо изобретать велосипед. 



def send_resume_to_family(update, context):
    if update.callback_query != None:
        update = update.callback_query
    password = context.user_data['secret_key']
    family_list = select_family_list(password)
    for family in family_list:
        chat_id, passw = family
        # assert chat_id == update.message.chat_id, 'chat_id не равен update.message.chat_id'
        if chat_id == str(update.message.chat_id):
            continue
        else:
            resume(chat_id, context)

    
        
def get_family_admin_id(password):
    family_list = select_family_list(password)  
    for family in family_list:
        chat_id, passw, role = family
        if role == 'admin':
            return chat_id   



def send_resume(update, context):
    if update.callback_query != None:
        update = update.callback_query
    if context.user_data.get('left_days_to_purp') == None:
        get_user_data_befor_conv(update, context)
    resume(update.message.chat_id, context)
    send_resume_to_family(update, context)



def resume(chat_id, context):
    text = get_resume_text(context)
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    time.sleep(2)    
    context.bot.send_message(
        chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)




'''ПАРСИМ ДАННЫЕ, КОТОРЫЕ ВВЁЛ ЧЕЛОВЕК'''

def check_user_sum_entry(text, chat_id, context):
    text = text.lower()
    if len(text.split()) == 2 or len(text.split()) == 3:
        if text.split()[0].isdigit() == True and text.split()[1].isdigit() == False:
            for item in config.USD_SYNONIM_LIST:
                if item in text:
                    write_entry_to_base('purp_currency', 'USD', chat_id)
                    context.user_data['purp_currency'] = 'USD'
                    return True
            for item in config.UAH_SYNONIM_LIST:
                if item in text:
                    write_entry_to_base('purp_currency', 'UAH', chat_id)
                    context.user_data['purp_currency'] = 'UAH'
                    return True
            for item in config.BYN_SYNONIM_LIST:
                if item in text:
                    write_entry_to_base('purp_currency', 'BYN', chat_id)
                    context.user_data['purp_currency'] = 'BYN'
                    return True
            for item in config.RUB_SYNONIM_LIST:
                if item in text:
                    write_entry_to_base('purp_currency', 'RUB', chat_id)
                    context.user_data['purp_currency'] = 'RUB'
                    return True
                return False
        else: return False
    else: return False

def date_to_sql_format(word_list, month_list):
    day, month, year = word_list
    for month_item in month_list:
        if month_item in month:
            month = str(month_list.index(month_item) + 1)
    purp_date = datetime.datetime.strptime(f'{year}-{month}-{day}', '%Y-%m-%d').date()    
    return purp_date    

def parse_purp_date(date_str):
    date_str = date_str.lower()
    month_list = ['январ', 'феврал', 'март', 'апрел', 'мая', 'июн', 'июл', 'август', 'сентяб', 'октябр', 'ноябр', 'декабр']
    word_list = date_str.split()
    if len(word_list) > 1 and word_list[0].isdigit() == True and int(word_list[0]) < 32 and word_list[1].isdigit() == False:
        if len(word_list) == 3:
            purp_date = date_to_sql_format(word_list, month_list)
            return purp_date
        elif len(word_list) == 4:
            del word_list[-1]
            purp_date = date_to_sql_format(word_list, month_list)
            return purp_date
        elif len(word_list) == 2:
            year = str(datetime.datetime.today().year)
            word_list.append(year)
            purp_date = date_to_sql_format(word_list, month_list)
            delta = purp_date - datetime.date.today()
            if delta.days < 0:
                year = str(datetime.datetime.today().year + 1)
                del word_list[-1]
                word_list.append(year)
                purp_date = date_to_sql_format(word_list, month_list)
                print(purp_date)
                return purp_date
            else: return purp_date    
        else: return -1
    else: return -1

def parse_current_sum(summ, context):
    if len(summ.split()) == 1:
        if summ.isdigit() == True:
            return summ
        else: return -1
    elif len(summ.split()) == 2:
        if summ.split()[0].isdigit() == True and summ.split()[1].isdigit() == False:            
            if context.user_data['purp_currency'] == 'USD':
                synonim_list = config.USD_SYNONIM_LIST
            if context.user_data['purp_currency'] == 'UAH':
                synonim_list = config.UAH_SYNONIM_LIST
            if context.user_data['purp_currency'] == 'RUB':
                synonim_list = config.RUB_SYNONIM_LIST
            if context.user_data['purp_currency'] == 'BYN':
                synonim_list = config.BYN_SYNONIM_LIST
            for word in synonim_list:
                if word in summ:
                    return summ.split()[0]
            else: return -1
    else: return -1
        

def get_user_data_befor_conv(update, context):
    purpose, purpose_type, purp_sum, purpose_date, current_sum, payed_dates, \
        secret_key, currency, save_in_this_month, \
        sum_to_save_in_this_month = select_user_data(update.message.chat_id)
    context.user_data['purpose'] = purpose
    context.user_data['purpose_type'] = purpose_type
    context.user_data['purpose_date'] = purpose_date

    left_days_to_purp = day_to_purp(update.message.chat_id, purpose_date)
    context.user_data['left_days_to_purp'] = str(left_days_to_purp)

    context.user_data['purpose_sum'] = str(purp_sum)    
    context.user_data['current_sum'] = str(current_sum)    
    context.user_data['payed_dates'] = payed_dates
    # payed_dates = payed_dates.split(', ')

    context.user_data['save_in_this_month'] = str(save_in_this_month)
    context.user_data['secret_key'] = secret_key
    context.user_data['purp_currency'] = currency        

    today = str(datetime.datetime.now().day)        
    
    for date in payed_dates:        
        if today == date:            
            index = payed_dates.index(date)
            if index == 0: # Если первая дата в месяце, то задаётся цель на месяц
                sum_to_save_in_this_month = (purp_sum - current_sum) / left_days_to_purp * 30
                sum_to_save_in_this_month = int(round(sum_to_save_in_this_month/5.0)*5) 
                context.user_data['sum_to_save_in_this_month'] = sum_to_save_in_this_month
                write_entry_to_base(
                    'sum_to_save_in_this_month', sum_to_save_in_this_month, update.message.chat_id)  
                save_in_this_month = 0
                context.user_data['save_in_this_month'] = str(save_in_this_month)            

            every_month_purp_sum = (sum_to_save_in_this_month - save_in_this_month)/ (len(payed_dates) - index)
            every_month_purp_sum = int(round(every_month_purp_sum/5.0)*5) 
            context.user_data['every_month_purp_sum'] = str(every_month_purp_sum)
        else:
            every_month_purp_sum = '0'
            context.user_data['every_month_purp_sum'] = str(every_month_purp_sum)    

    user_data_list = [purpose, purpose_type, purp_sum, purpose_date, current_sum, payed_dates, \
        secret_key, currency, save_in_this_month, \
            sum_to_save_in_this_month]

    return user_data_list










if __name__ == '__main__':
    # parse_purp_date('32 октября')            
    # payday_date_handler('30')
    # get_subscribers_send_to('3')
    # select_family_list('$DDMsf!cIzpyehr')
    # day_to_purp('529133148')
    # parse_purpose_sum('50 ДОЛЛАРОВ')
    # print(check_user_sum_entry('50 000 jkjkjk'))
    select_user_data('529133148')