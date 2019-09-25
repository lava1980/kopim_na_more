import logging
import sqlite3
from telegram import ChatAction, ParseMode
from telegram.ext import ConversationHandler
import time

from utils import *

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                    level = logging.INFO,
                    filename = 'tgbot.log'
                    )
    

def greet_user(update, context):
    text_to_user = '''Привет! Я помогу вам собрать деньги на отдых. Я буду вас мотивировать, \
напоминать, пинать и т.п. Не обижайтесь на меня, ладно? Всё это для вашего же \
блага)'''
    context.bot.send_message(chat_id=update.message.chat_id, text=text_to_user)    
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    time.sleep(3)
    context.bot.send_message(
        chat_id=update.message.chat_id, 
        text='Вы новый пользователь? Или вас пригласил кто-то из вашей семьи (должен быть секретный код)?', 
        reply_markup=get_inline_keyboard()
        )

def initial_data_start(update, context):
    query = update.callback_query
    data = get_initial_data(update)
    write_initial_data_to_base(data)
    query.message.reply_text('На что копим?')
    return 'purpose'

def get_purpose(update, context):    
    write_entry_to_base('purpose', update.message.text, update.message.chat_id)
    update.message.reply_text('Когда планируете ехать?')
    return 'purpose_date'

def get_purpose_date(update, context):    
    write_entry_to_base('purpose_date', update.message.text, update.message.chat_id)
    update.message.reply_text('Сколько денег есть на данный момент?')
    return 'current_sum'

def get_current_sum(update, context):    
    write_entry_to_base('current_sum', update.message.text, update.message.chat_id)
    update.message.reply_text('В какие дни у вас приход денег?')
    return 'payday_dates'

def get_payday_dates(update, context):   
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    dates = user_entry_date_handler(update.message.text, update)
    if dates == 'payday_dates':
        return 'payday_dates'
    write_entry_to_base('payday_dates', dates, update.message.chat_id)
    update.message.reply_text('Сколько планируете откладывать в месяц?')
    return 'every_month_purp_sum'

def get_every_month_purp_sum(update, context):    
    write_entry_to_base('every_month_purp_sum', update.message.text, update.message.chat_id)
    update.message.reply_text('Спасибо, ответы принял.')
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    time.sleep(2)
    password = password_generation()
    write_entry_to_base('secret_key', password, update.message.chat_id)
    update.message.reply_text('Пароль вашей семьи: ' + password)
    update.message.reply_text('Передайте его родственнику, с которым вы вместе собираете деньги, чтобы он мог присоединиться к боту и видеть всю историю.')
    return ConversationHandler.END   

def dontknow(update, context):
    update.message.reply_text('Не понимаю, что вы имеете ввиду. Проверьте что вы написали')
 
######################################

def invited_user_conv(update, context):
    query = update.callback_query        
    query.message.reply_text('Введите секретный пароль семьи')
    return 'secret_key'

def get_password(update, context):
    pass_list = list_from_base_column('secret_key') # [('-yGIB7rf?NKU0Dk',), (None,)]
    for item in pass_list:
        if item[0] == update.message.text:            
            write_entry_to_base('secret_key', update.message.text, update.message.chat_id)
            update_invited_user_data(update.message.chat_id) # Удаляем данные, если они были
            update.message.reply_text('Отлично! Теперь вам будут приходить уведомления')
            break
        else: 
            update.message.reply_text('Пароль не найден. Уточните ещё раз')
            return 'secret_key'
    return ConversationHandler.END

# TODO Нужно доставать даты из базы и парсить -- это первое. 

# TODO Потом что? Когда у меня уже есть список из дат, дальше можно с ними работать. 
