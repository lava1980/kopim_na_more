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
import utils



logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                    level = logging.INFO,
                    filename = 'tgbot.log'
                    )




def main():    
 

    mybot = Updater(config.TOKEN, use_context=True)
    
    # Инициализируем MessageQueue 
    mybot.bot._msg_queue = mq.MessageQueue()
    mybot.bot._is_messages_queued_default=True


    logging.info('Бот запускается.')

    dp = mybot.dispatcher

    
    initial_data = ConversationHandler(
        entry_points = [
            CommandHandler('settings', initial_data_start),
            CallbackQueryHandler(initial_data_start, pattern='new_user'), 
            CallbackQueryHandler(invited_user_conv, pattern='invited_user')
            ],
        states = {
                'purpose': [MessageHandler(Filters.text, get_purpose)],
                'purpose_date': [MessageHandler(Filters.text, get_purpose_date)], 
                'current_sum': [MessageHandler(Filters.text, get_current_sum)],
                'payday_dates': [MessageHandler(Filters.text, get_payday_dates)],
                'every_month_purp_sum': [MessageHandler(Filters.text, get_every_month_purp_sum)]                
                
                     
        },
        fallbacks = [MessageHandler(Filters.text, dontknow)]
        
    )

    
    enter_secret_key = ConversationHandler(
        entry_points = [CallbackQueryHandler(invited_user_conv, pattern='invited_user')],
        states = {
                'password': [MessageHandler(Filters.text, get_password)],              
                     
        },
        fallbacks = [MessageHandler(Filters.text, dontknow)]
        
    )






    dp.add_handler(enter_secret_key)
    dp.add_handler(initial_data)     
    dp.add_handler(CommandHandler('start', greet_user))  
    
    

   
    
    
    mybot.start_polling()  
    mybot.idle()


if __name__ == '__main__':
    main()
