import logging
import sqlite3
from telegram.ext import ConversationHandler

from utils import *

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                    level = logging.INFO,
                    filename = 'tgbot.log'
                    )


def greet_user(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Привет! Этот бот поможет тебе собрать деньги на отдых.')


def initial_data_start(update, context):
    data = get_initial_data(update)
    write_initial_data_to_base(data)
    update.message.reply_text('На что копим?')
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
    write_entry_to_base('payday_dates', update.message.text, update.message.chat_id)
    update.message.reply_text('Сколько планируете откладывать в месяц?')
    return 'every_month_purp_sum'

def get_every_month_purp_sum(update, context):
    write_entry_to_base('every_month_purp_sum', update.message.text, update.message.chat_id)
    update.message.reply_text('Спасибо, ответы принял.')
    return ConversationHandler.END

def dontknow(update, context):
    update.message.reply_text('Чё-то я не втыкаю. За тобой косяк, командир, проверь ещё разок, что ты накарябал')
 