import logging
import sqlite3

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                    level = logging.INFO,
                    filename = 'tgbot.log'
                    )


def create_user_base():
    conn = sqlite3.connect('user_base.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                    (chat_id text PRIMARY KEY, first_name text, purpose text, 
                    purpose_date text, current_sum integer, payday_dates text, 
                    every_month_purp_sum text)'''
                    )
    conn.commit()
    conn.close()

def get_initial_data(update):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
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






# Сделаю автоматический забор суммы для нас, а для остальных 
# предусмотрю возможность ввести приход в день прихода. 





if __name__ == "__main__":
    write_entry_to_base('purpose', 'лёля', '121212313')




# payday_dates - даты прихода. Можно в одну строку несколько дат. потом их просто парсить.

# TODO Сделать, чтобы люди могли редактировать свои данные (и обновлялась база)
# TODO Человек указал, и сразу записалось в базу. 

# TODO Как добавлять членов семьи в одну группу. Например, как добавить Таню?