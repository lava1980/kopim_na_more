import logging
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

def get_all_cashflow():
    pass



# Первый чел получает логин и пароль. Передаёт второму. Тот их вводит -- и попадает в базу с 
# айди их общей группы с первым челом. А обновления приходят по айди этой общей группы (не по
# айди пользователя или чат-айди). 

# У второго чела должна быть возможность выбрать "Мне прислали пароль" или "Меня пригласили". 
# Чтобы ему не надо было заполнять все данные с нуля. 






# Сделаю автоматический забор суммы для нас, а для остальных 
# предусмотрю возможность ввести приход в день прихода. 





if __name__ == "__main__":
    write_entry_to_base('purpose', 'лёля', '121212313')




# payday_dates - даты прихода. Можно в одну строку несколько дат. потом их просто парсить.

# TODO Сделать при выборе команды НАСТРОЙКИ, чтобы спрашивал: "новый пользователь" и "меня пригласили".
# Если пригласили, то предлагает ввести логин и пароль.

# TODO Сделать, чтобы люди могли редактировать свои данные (и обновлялась база)