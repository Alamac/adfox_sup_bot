import logging

from daemon import daemon
from emoji import emojize
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
import telegram

import settings
from utils import get_tickets_from_emails

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

def ticket_handler(bot, job):

    ticket_list = get_tickets_from_emails(settings.IMAP, settings.LOGIN, settings.PASS, settings.FOLDER, settings.DEL_FOLDER)

    if len(ticket_list) > 0:
        
        for ticket in ticket_list:
            nmb = ticket['ticket']
            theme = ticket['theme']
            theme = theme.replace('[', '\[')
            url = ticket['url']
            action = ticket['action']
            if action == 'Task created':
                sign = emojize(':white_check_mark:', use_aliases=True)
                reply = f'*Новая задача*{sign}\n{nmb}\n{theme}\n{url}'

            elif action == 'SLA expiring':
                sign = emojize(':warning:', use_aliases=True)
                reply = f'*Истекает SLA*{sign}\n{nmb}\n{theme}\n{url}'

            elif action == 'SLA expired':
                sign = emojize(':bangbang:', use_aliases=True)
                reply = f'*Истёк SLA*{sign}\n{nmb}\n{theme}\n{url}'
        
            bot.send_message(chat_id='-1001361799205', text=reply, parse_mode=telegram.ParseMode.MARKDOWN)

def set_support_duty(bot, update):
    pass

if __name__ == '__main__':

    bot = Updater(token=settings.TELEGRAM_API_KEY)
    jobs = bot.job_queue
    job_minute = jobs.run_repeating(ticket_handler, interval=10, first=0)
    dp = bot.dispatcher
    bot.start_polling()
    bot.idle()