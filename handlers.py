import logging
import sqlite3
from telegram import ChatAction, ParseMode
from telegram.ext import ConversationHandler
import time

from config import EMOJI, PURPOSE_TEXT, PURPOSE_DATE_TEXT
from utils import *


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                    level = logging.INFO,
                    filename = 'tgbot.log'
                    )
    

def greet_user(update, context):
    text_to_user = f'''Привет {EMOJI["waving_hand"]} Я помогу вам собрать \
деньги на отдых, покупку чего-либо и другие цели {EMOJI["money_bag"]} Основная моя задача — сделать так, чтобы вы не забывали про цель... \
чтобы постоянно к ней возвращались, думали про неё, мечтали и т.п.'''
    context.bot.send_message(chat_id=update.message.chat_id, text=text_to_user)      
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    context.bot.send_message(
        chat_id=update.message.chat_id, 
        text=f'{EMOJI["trophy"]} Поэтому я буду вам напоминать откладывать деньги, мотивировать и т.п.')    
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    time.sleep(2)
    context.bot.send_message(
        chat_id=update.message.chat_id, 
        text='Вы новый пользователь? Или вас пригласил кто-то из вашей семьи (должен быть секретный код)?', 
        reply_markup=get_inline_keyboard()
        )



def initial_data_start(update, context):
    query = update.callback_query
    data = get_initial_data(update)
    write_initial_data_to_base(data)

    query.message.reply_text('Укажите тип цели', reply_markup=purp_type_inline_keyboard())    
    return 'purpose_type'

def get_purpose_type(update, context):
    query = update.callback_query
    purpose_type = query.data
    write_entry_to_base('purpose_type', purpose_type, query.message.chat_id)       
    context.user_data['purpose_type'] = purpose_type

    query.message.reply_text(
        f'{EMOJI["target"]} {handle_var_inside_text(PURPOSE_TEXT, purpose_type)}')
    return 'purpose'


def get_purpose(update, context):      
    write_entry_to_base('purpose', update.message.text, update.message.chat_id)
    update.message.reply_text(
        f'Какую сумму хотите собрать? Например, 1000 долларов... или 2000 белорусских рублей {EMOJI["winking_face"]}')            
    return 'purpose_sum'

def get_purpose_sum(update, context):          
    if check_user_sum_entry(update.message.text, update.message.chat_id, context) == True:        
        write_entry_to_base(
                    'purpose_sum', 
                    int(update.message.text.split()[0]), 
                    update.message.chat_id
                    )            
    else: 
        update.message.reply_text(f'''Извините, не понимаю... {EMOJI["thinking_face"]} \
Напишите сумму, которую хотите накопить. Например, 1000 долларов. Цифру пишите без пробелов''')
        return 'purpose_sum'  
    purpose_type = context.user_data['purpose_type']  
    update.message.reply_text(f'{EMOJI["calendar"]} {handle_var_inside_text(PURPOSE_DATE_TEXT, purpose_type)} Например, 1 августа')
    return 'purpose_date'

def get_purpose_date(update, context):       
    purpose_date = parse_purp_date(update.message.text) 
    if purpose_date != -1:
        write_entry_to_base('purpose_date', purpose_date, update.message.chat_id)
        purp_currency = context.user_data['purp_currency']
        update.message.reply_text(f'Сколько денег есть на данный момент (в {purp_currency})?')
        return 'current_sum'
    else: 
        update.message.reply_text('Введите дату в правильном формате, например, 1 августа... или 1 августа 2022 года')
        return 'purpose_date'

def get_current_sum(update, context):  
    current_summ = parse_current_sum(update.message.text, context)
    if current_summ != -1:
        write_entry_to_base('current_sum', current_summ, update.message.chat_id)
        update.message.reply_text('В какие дни у вас приход денег?')
        return 'payday_dates'
    else:
        purp_currency = context.user_data['purp_currency']
        update.message.reply_text(
            f'Введите или цифру, или цифру и валюту, например, 50 долларов. Обратите внимание, что валюта должна совпадать с валютой цели (в вашем случае {purp_currency}).'
            )
        return 'current_sum'

def get_payday_dates(update, context):   
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    dates = user_entry_date_handler(update.message.text, update)
    if dates == 'payday_dates':
        return 'payday_dates'
    write_entry_to_base('payday_dates', dates, update.message.chat_id) 
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
    data = get_initial_data(update)
    write_initial_data_to_base(data)         
    query.message.reply_text('Введите секретный пароль семьи')
    return 'secret_key'

def get_password(update, context):
    pass_list = list_from_base_column('secret_key') # [('-yGIB7rf?NKU0Dk',), (None,)]
    for item in pass_list:
        if item[0] == update.message.text:  
            admin_id = get_family_admin_id(update.message.text)                     
            user_data_list = select_user_data(admin_id)
            update_invited_user_data(update.message.chat_id, user_data_list)

            update.message.reply_text('Отлично! Теперь вам будут приходить уведомления')
            break
        else: 
            update.message.reply_text('Пароль не найден. Уточните ещё раз')
            return 'secret_key'
    return ConversationHandler.END

##################################################


def start_get_payed_summ(update, context):   
    unset(update, context)
    update = update.callback_query

    purpose, purpose_type, purp_sum, purpose_date, current_sum, payed_dates, \
    secret_key, currency, save_in_this_month, \
    sum_to_save_in_this_month, role \
                = get_user_data_befor_conv(update, context)    
    
    every_month_purp_sum = int(context.user_data['every_month_purp_sum'])
    payed_summ = update.message.text    
    update.message.reply_text(f'Отлично! {EMOJI["money_mouth_face"]}')
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    if save_in_this_month == 0:
        how_much_saving_text = ''
    else: how_much_saving_text = f'Вы отложили {save_in_this_month} {currency}.'     
    update.message.reply_text(
        f'{EMOJI["target"]} В этом месяце по графику вам нужно сохранить {sum_to_save_in_this_month} {currency}. \
{how_much_saving_text} Сейчас нужно отложить {str(every_month_purp_sum)} {currency} или больше. \
Сколько откладываем?', 
        reply_markup=pay_day_inline_keyboard2(every_month_purp_sum, currency))
    return 'how_much_saving'

def get_saving_sum(update, context):    
    query = update.callback_query
    every_month_purp_sum = context.user_data['every_month_purp_sum']
    save_in_this_month = int(context.user_data['save_in_this_month'])
    if query.data == every_month_purp_sum:    
        current_sum = int(context.user_data['current_sum'])
        current_sum = current_sum + int(every_month_purp_sum)             
        save_in_this_month = save_in_this_month + int(every_month_purp_sum)

    write_entry_to_base('current_sum', current_sum, query.message.chat_id) 
    write_entry_to_base('save_in_this_month', save_in_this_month, query.message.chat_id)
    context.user_data['current_sum'] = str(current_sum)
    query.message.reply_text(f'Отлично, информацию принял {EMOJI["ok_hand"]}')
    clone_admin_data(update, context)

    send_resume(update, context)
    send_resume_to_family_in_payday(update, context)
    return ConversationHandler.END
    
 
    
#########################################################

def get_other_sum(update, context):    
    query = update.callback_query  
    if query != None:      # Через инлайн клавиатуру, user_data подгружены
        query.message.reply_text(
            f'Введите сумму, которую отложите {EMOJI["hand_pointing_down"]}')    
    else:
        get_user_data_befor_conv(update, context) # Вызов через команду, подгружаем user_data
        update.message.reply_text(
            f'Введите сумму, которую отложите {EMOJI["hand_pointing_down"]}')
    return 'enter_sum'

def get_other_saving_sum(update, context):   
    saving_sum = int(update.message.text)
    current_sum = context.user_data['current_sum']
    current_sum = int(current_sum) + int(saving_sum)
    
    save_in_this_month = int(context.user_data['save_in_this_month'])
    save_in_this_month = save_in_this_month + saving_sum

    write_entry_to_base('current_sum', current_sum, update.message.chat_id)     
    write_entry_to_base('save_in_this_month', save_in_this_month, update.message.chat_id)
    context.user_data['current_sum'] = str(current_sum)
    update.message.reply_text(f'Отлично, информацию принял {EMOJI["ok_hand"]}')  
    clone_admin_data(update, context)  
    
    send_resume_to_family_in_payday(update, context)
    send_resume(update, context)
    return ConversationHandler.END
    
###########################################################

def pass_current_month(update, context):
    query = update.callback_query    
    query.message.reply_text(f'Информацию принял {EMOJI["thumbs_up"]}')
    resume(update, context)
    return ConversationHandler.END    

###########################################################   

def set_delay(update, context): 
    query = update.callback_query
    chat_id = query.message.chat_id    
    # new_job = context.job_queue.run_repeating(ask_question, 10, context=chat_id)        
    new_job = context.job_queue.run_once(ask_question, datetime.timedelta(seconds=10.0), context=chat_id)        
    context.chat_data['job'] = new_job
    query.message.reply_text(f'странно... {EMOJI["thinking_face"]} ок, спрошу позже')    
    print(context.user_data)

def unset(update, context):
    # query = update.callback_query
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        # query.message.reply_text('You have no active timer')
        return

    job = context.chat_data['job']
    print(job)
    job.schedule_removal()
    del context.chat_data['job']
    # query.message.reply_text('Timer successfully unset!')

def ask_question(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(
        job.context, 
        text=f'Вы получили зарплату? {EMOJI["purse"]}', 
        reply_markup=pay_day_inline_keyboard1()
        )



# TODO Сделать, чтобы уведомления приходили не админам.

# TODO Сделать поздравления, когда месячная цель достигнута. Т.е. 
# sum_to_save_in_this_month == save_in_this_month.

# TODO Сделать, чтобы люди могли редактировать свои данные (и обновлялась база)

# TODO Сделать, чтобы когда зарплата приходится на выходной, чтобы челу потом и в выходной не 
# приходило уведомление

# TODO В начале объяснить, что для того, чтобы бот нормально работал, его нужно 
# настроить. И спрашивать: вы готовы настроить сейчас?

