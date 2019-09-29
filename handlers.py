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
    update.message.reply_text('Какую сумму хотите собрать?')    
    return 'purpose_sum'

def get_purpose_sum(update, context):    
    write_entry_to_base('purpose_sum', update.message.text, update.message.chat_id)
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
    password = password_generation()
    write_entry_to_base('secret_key', password, update.message.chat_id)
    update.message.reply_text('Пароль вашей семьи: ' + password)
    update.message.reply_text('Передайте его родственнику, с которым вы вместе собираете деньги, чтобы он мог присоединиться к боту и видеть всю историю.')
    return ConversationHandler.END   

def dontknow(update, context):
    update.message.reply_text('Не понимаю, что вы имеете ввиду. Проверьте что вы написали')
 
##################################################

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

##################################################

def start_enter_pay_sum(update, context):
    query = update.callback_query
    query.message.reply_text('Введите общую сумму прихода за сегодня')
    return 'payed_summ'

def get_payed_summ(update, context):
    payed_summ = update.message.text    
    every_month_purp_sum = get_data_cell('every_month_purp_sum', update.message.chat_id)
    charges = get_data_cell('charges', update.message.chat_id)
    cashflow = int(payed_summ) - charges
    if cashflow < 100:
        little_sum = get_little_sum(cashflow)
        text = f'''В этом месяце небольшой приход. Комфортно вы можете отложить \
{str(little_sum)}. Если поднапрячься, можно выкроить и {every_month_purp_sum} долларов. \
Какую сумму отложим?'''
        update.message.reply_text(
            text, 
            reply_markup=pay_day_inline_keyboard3(str(little_sum), every_month_purp_sum)
            )
        context.user_data.update({'little_sum': little_sum})
    else:        
        update.message.reply_text(
            f'Вы можете отложить {every_month_purp_sum} долларов или больше. \
Сколько откладываем?', 
            reply_markup=pay_day_inline_keyboard2(every_month_purp_sum))
    return 'how_much_saving'

def get_saving_sum(update, context):    
    query = update.callback_query
    every_month_purp_sum = get_data_cell('every_month_purp_sum', query.message.chat_id)  # str
    if query.data == every_month_purp_sum or query.data == '2':    
        current_sum = get_data_cell('current_sum', query.message.chat_id)   # int   
        current_sum = current_sum + int(every_month_purp_sum)        
    if query.data == '1':        
        little_sum = context.user_data['little_sum']
        current_sum = get_data_cell('current_sum', query.message.chat_id)   # int   
        current_sum = current_sum + int(little_sum)


    write_entry_to_base('current_sum', current_sum, query.message.chat_id) 
    context.user_data.update({'current_sum': current_sum})   
    query.message.reply_text('Отлично, информацию принял!')

    resume(update, context)
    return ConversationHandler.END
    
 
    
#########################################################

def get_other_sum(update, context):
    query = update.callback_query        
    query.message.reply_text('Введите сумму, которую отложите')    
    return 'enter_sum'

def get_other_saving_sum(update, context):   
    saving_sum = update.message.text
    current_sum = get_data_cell('current_sum', update.message.chat_id)   # int   
    current_sum = current_sum + int(saving_sum)
    write_entry_to_base('current_sum', current_sum, update.message.chat_id) 
    context.user_data.update({'current_sum': current_sum})      
    update.message.reply_text('Отлично, информацию принял!')    
    
    resume(update, context)
    return ConversationHandler.END
    
###########################################################

def pass_current_month(update, context):
    query = update.callback_query
    current_sum = get_data_cell('current_sum', query.message.chat_id)   # int   
    context.user_data.update({'current_sum': current_sum})      
    query.message.reply_text('Информацию принял!')
    resume(update, context)
    return ConversationHandler.END    


# TODO Сделать возможность выбирать валюту накоплений



