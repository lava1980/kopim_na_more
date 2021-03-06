import datetime
import logging
import random
import sqlite3

from telegram import InlineQuery
from telegram.ext import Updater, CallbackQueryHandler, ConversationHandler, CommandHandler, \
        MessageHandler, RegexHandler, Filters, CallbackQueryHandler
from telegram.ext import messagequeue as mq

import config
from handlers import *
from messages import *
import utils



logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                    level = logging.INFO,
                    filename = 'tgbot.log'
                    )


def send_updates(context):    
    today_date = datetime.datetime.now().day
    subs_list = get_subscribers_send_to(str(today_date)) # [('891850606', '2, 1, 13', '-yGIB7rf?NKU0Dk')]
    if len(subs_list) == 0:
        return False
    for subs in subs_list:
        chat_id, dates, role = subs         
        date_list = dates.split(', ')
    
        for date_from_base in date_list:
            # date_from_base = payday_date_handler(date_from_base) # Проверяем или з/п не приходится на выходной
            if today_date == int(date_from_base) and role == 'admin': # Только админам
                # Основной код, который должен выполняться в день выдачи зарплаты                
                context.bot.send_message(
                    chat_id=chat_id, 
                    text=f'Привет {config.EMOJI["waving_hand"]} Сегодня классный день — день зарплаты) Вы получили деньги?',
                    reply_markup=pay_day_inline_keyboard1()
                    )
    






mybot = Updater(config.TOKEN, use_context=True)

def main():    
 

    
    
    # Инициализируем MessageQueue 
    mybot.bot._msg_queue = mq.MessageQueue()
    mybot.bot._is_messages_queued_default=True


    logging.info('Бот запускается.')

    dp = mybot.dispatcher
    
    # mybot.job_queue.run_daily(send_updates, datetime.time(16, 0, 0))        
    mybot.job_queue.run_repeating(send_updates, interval=30, first=1)        

    
    initial_data = ConversationHandler(
        entry_points = [
            CommandHandler('settings', initial_data_start),
            CallbackQueryHandler(initial_data_start, pattern='new_user'), 
            CallbackQueryHandler(invited_user_conv, pattern='invited_user')
            ],
        states = {             
                'purpose_type': [CallbackQueryHandler(get_purpose_type)],
                'purpose': [MessageHandler(Filters.text, get_purpose)],
                'purpose_sum': [MessageHandler(Filters.text, get_purpose_sum)],
                'purpose_date': [MessageHandler(Filters.text, get_purpose_date)], 
                'current_sum': [MessageHandler(Filters.text, get_current_sum)],
                'payday_dates': [MessageHandler(Filters.text, get_payday_dates)]                                                            
                    
        },
        fallbacks = [MessageHandler(Filters.text, dontknow)]
        
    )

    
    enter_secret_key = ConversationHandler(
        entry_points = [CallbackQueryHandler(invited_user_conv, pattern='invited_user')],
        states = {
                'secret_key': [MessageHandler(Filters.text, get_password)],              
                     
        },
        fallbacks = [MessageHandler(Filters.text, dontknow)]
        
    )

    enter_pay_sum = ConversationHandler(
        entry_points = [CallbackQueryHandler(start_get_payed_summ, pattern='yes'), 
                        CommandHandler('add', get_other_sum)
        ],
        states = {            
            'how_much_saving': [CallbackQueryHandler(get_other_sum, pattern='other'),
                                CallbackQueryHandler(pass_current_month, pattern='pass_current_month'),
                                CallbackQueryHandler(pass_current_month, pattern='pass_current_month_2'),
                                CallbackQueryHandler(get_saving_sum, pattern='every_month_purp_sum')],
            'enter_sum': [MessageHandler(Filters.text, get_other_saving_sum)] 
        }, 
        fallbacks = [MessageHandler(Filters.text, dontknow)]
    )

  
    dp.add_handler(enter_pay_sum)    
    dp.add_handler(enter_secret_key)
    dp.add_handler(initial_data) 
    dp.add_handler(CallbackQueryHandler(set_delay, pattern='no'))   
    dp.add_handler(CommandHandler('start', check_if_is_subscriber))      
    dp.add_handler(CommandHandler('now', send_resume))    
    dp.add_handler(CallbackQueryHandler(callback_other_handler))   
    
    # webhook_domain = 'https://python-developer.ru'    
    # PORT = 5000

    # mybot.start_webhook(listen='127.0.0.1',
    #                 port=PORT,
    #                 url_path=config.TOKEN,
    #                 webhook_url=f'{webhook_domain}/{config.TOKEN}'                    
    #                 )


    # mybot.bot.set_webhook(f'{webhook_domain}/{config.TOKEN}')
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()

# TODO Когда дата отпуска достигнута, выдать сообщение -- похвалить или утешить. 
# И обнулить данные в базе

