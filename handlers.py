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
    query.message.reply_text('На что копим? Пример: Отдых в Сочи')
    return 'purpose'

def get_purpose(update, context):
    write_entry_to_base('purpose', update.message.text, update.message.chat_id)
    update.message.reply_text(
        'Какую сумму хотите собрать? Например, 1000 долларов... или 2000 белорусских рублей 🤔')    
    return 'purpose_sum'

def get_purpose_sum(update, context):          
    if check_user_sum_entry(update.message.text, update.message.chat_id, context) == True:        
        write_entry_to_base(
                    'purpose_sum', 
                    int(update.message.text.split()[0]), 
                    update.message.chat_id
                    )            
    else: 
        update.message.reply_text('''Извините, не понимаю... \
Напишите сумму, которую хотите накопить. Например, 1000 долларов. Цифру пишите без пробелов''')
        return 'purpose_sum'    
    update.message.reply_text('Когда планируете ехать? Например, 1 августа')
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
    update.message.reply_text('В какой валюте получаете зарплату?', reply_markup=inline_keyboard_currency())
    return 'salary_currency'

def get_salary_currency(update, context):  
    query = update.callback_query
    write_entry_to_base('salary_currency', query.data, query.message.chat_id)  
    query.message.reply_text('Спасибо, ответы принял.')
    context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.TYPING)    
    password = password_generation()
    write_entry_to_base('secret_key', password, query.message.chat_id)
    query.message.reply_text('Пароль вашей семьи: ' + password)
    query.message.reply_text('Передайте его родственнику, с которым вы вместе собираете деньги, чтобы он мог присоединиться к боту и видеть всю историю.')
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
    unset(update, context)
    query = update.callback_query
    query.message.reply_text('Введите общую сумму прихода за сегодня')
    return 'payed_summ'

def get_payed_summ(update, context):
    left_days_to_purp = day_to_purp(update.message.chat_id)
    context.user_data['left_days_to_purp'] = str(left_days_to_purp)

    purp_sum = get_data_cell('purpose_sum', update.message.chat_id)
    context.user_data['purpose_sum'] = str(purp_sum)
    
    current_sum = get_data_cell('current_sum', update.message.chat_id)   # int 
    context.user_data['current_sum'] = str(current_sum)

    every_month_purp_sum = (purp_sum - current_sum) / left_days_to_purp * 30
    every_month_purp_sum = int(round(every_month_purp_sum/5.0)*5) 
    context.user_data['every_month_purp_sum'] = str(every_month_purp_sum)
    
    payed_summ = update.message.text    
    currency = get_data_cell('purp_currency', update.message.chat_id)
    context.user_data['currency'] = currency    
    charges = get_data_cell('charges', update.message.chat_id)
    cashflow = int(payed_summ) - charges
    if cashflow < 100:
        little_sum = get_little_sum(cashflow)
        text = f'''В этом месяце небольшой приход. Комфортно вы можете отложить \
{str(little_sum)}{currency}. Если поднапрячься, можно выкроить и {str(every_month_purp_sum)} {currency}. \
Какую сумму отложим?'''
        update.message.reply_text(
            text, 
            reply_markup=pay_day_inline_keyboard3(str(little_sum), str(every_month_purp_sum), currency)
            )
        context.user_data.update({'little_sum': little_sum})
    else:        
        update.message.reply_text(
            f'Вы можете отложить {str(every_month_purp_sum)} {currency} или больше. \
Сколько откладываем?', 
            reply_markup=pay_day_inline_keyboard2(str(every_month_purp_sum), currency))
    return 'how_much_saving'

def get_saving_sum(update, context):    
    query = update.callback_query
    every_month_purp_sum = context.user_data['every_month_purp_sum']
    if query.data == every_month_purp_sum or query.data == '2':    
        current_sum = int(context.user_data['current_sum'])
        current_sum = current_sum + int(every_month_purp_sum)         
    if query.data == '1':        
        little_sum = context.user_data['little_sum']
        current_sum = int(context.user_data['current_sum'])
        current_sum = current_sum + int(little_sum)        

    write_entry_to_base('current_sum', current_sum, query.message.chat_id) 
    context.user_data['current_sum'] = str(current_sum)
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
    # TODO Проверить этот вариант, чтобы было корректное значение current_sum
    # current_sum = get_data_cell('current_sum', update.message.chat_id)   # int   
    current_sum = context.user_data['current_sum']

    current_sum = int(current_sum) + int(saving_sum)
    write_entry_to_base('current_sum', current_sum, update.message.chat_id)     
    context.user_data['current_sum'] = str(current_sum)
    update.message.reply_text('Отлично, информацию принял!')    
    
    resume(update, context)
    return ConversationHandler.END
    
###########################################################

def pass_current_month(update, context):
    query = update.callback_query
    # TODO И здесь проверить, чтобы были корректные данные        
    query.message.reply_text('Информацию принял!')
    resume(update, context)
    return ConversationHandler.END    


# TODO Сделать возможность выбирать валюту накоплений


def set_delay(update, context): 
    query = update.callback_query
    chat_id = query.message.chat_id    
    # new_job = context.job_queue.run_repeating(ask_question, 10, context=chat_id)        
    new_job = context.job_queue.run_once(ask_question, datetime.timedelta(seconds=10.0), context=chat_id)        
    context.chat_data['job'] = new_job
    query.message.reply_text('Ок, спрошу позже')    
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
        text='Вы получили зарплату?', 
        reply_markup=pay_day_inline_keyboard1()
        )

# Как это должно быть? ВКак мне быть с валютами? 
# Что мне делать? Как мне быть? Как определиться? Как мне быть с валютами? 

# TODO Сделать, когда вначале пользователь вводит дату, чтобы 
# она обрабатывалась в формат базы данных.


# Что мне надо сделать? 

# В какой момент мне надо эта информация? Инфа о том, сколько отложить в месяц?
# в момент формирования кнопока. 


# Т.е. 