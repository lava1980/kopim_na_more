import datetime
import logging
import random
import sqlite3

from telegram.ext import Updater, CallbackQueryHandler, ConversationHandler, CommandHandler, \
        MessageHandler, RegexHandler, Filters
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
        entry_points = [CommandHandler('settings', initial_data_start)], 
        states = {
                'purpose': [MessageHandler(Filters.text, get_purpose)],
                'purpose_date': [MessageHandler(Filters.text, get_purpose_date)], 
                'curent_sum': [MessageHandler(Filters.text, get_current_sum)],
                'payday_dates': [MessageHandler(Filters.text, get_payday_dates)],
                'every_month_purp_sum': [MessageHandler(Filters.text, get_every_month_purp_sum)]                
                
                     
        },
        fallbacks = [MessageHandler(Filters.text, dontknow)]
    )
    # dp.add_handler(CallbackQueryHandler(handlers.func))
    dp.add_handler(initial_data)   
    # dp.add_handler(CommandHandler('start', handlers.subscribe))
    # dp.add_handler(CommandHandler('unsubscribe', handlers.unsubscribe))  
    
    
    
    mybot.start_polling()  
    mybot.idle()


if __name__ == '__main__':
    main()
