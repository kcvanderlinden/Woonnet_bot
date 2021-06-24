import Rijnmond_overzicht, Rijnland_overzicht, Woonbron_overzicht, Haaglanden_overzicht
import logging
import sys
import traceback
import datetime, pytz


from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.helpers import mention_html

# plaats hier je eigen gegevens tussen de haakjes
TELEGRAM_TOKEN = ''
TELEGRAM_DEV_ID = ''

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def error_callback(update, context):
    # We want to notify the user of this problem. This will always work,
    # but not notify users if the update is callback or inline query, or a poll update.
    # In case you want this, keep in mind that sending the message could fail.
    if update.effective_message:
        text = "Hallo. Er is helaas een fout opgetreden bij het verwerken van uw verzoek. " \
               "Mijn ontwikkelaar wordt op de hoogte gesteld."
        update.effective_message.reply_text(text)
    # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
    # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
    # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
    # empty string works fine.
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    # lets try to get as much information from the telegram update as possible
    payload = ""
    # normally, we always have an user. If not, its either a channel or a poll update.
    if update.effective_user:
        payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
    # there are more situations when you don't get a chat
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    # but only one where you have an empty payload by now: A poll (buuuh)
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    # lets put this in a "well" formatted text
    text = f"Hey.\nThe error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}</code>"
    # and send it to the dev
    context.bot.send_message(TELEGRAM_DEV_ID, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it. If you don't use the logger module, use it.
    raise

def start_callback(update, context):
    update.message.reply_text(f'Leuk je weer te zien {update.effective_user.first_name}.')

def rijnmond_aanbod_bericht(update, context):
    msg = context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Het woningaanbod van woonnet Rijnmond wordt opgehaald',
                                   parse_mode=ParseMode.HTML)
    context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=Rijnmond_overzicht.aanbod_message(), parse_mode=ParseMode.HTML)

def rijnmond_update_bericht(context: CallbackContext):
    Rijnmond_overzicht.rijnmond_aanbod()
    current_time = datetime.datetime.now()
    if current_time.hour >= 18 and current_time.hour < 20:
        context.bot.send_message(chat_id=TELEGRAM_DEV_ID, text=Rijnmond_overzicht.aanbod_message(), parse_mode=ParseMode.HTML)
    else:
        message = 'Helaas, deze functie werkt alleen automatisch en tussen 18:00 en 20:00'
        context.bot.send_message(chat_id=TELEGRAM_DEV_ID,
                                 text=message,
                                 parse_mode=ParseMode.HTML)
def updater_aanbod():
    Rijnland_overzicht.rijnland_aanbod()
    Woonbron_overzicht.woonbron_aanbod()
    Haaglanden_overzicht.haaglanden_aanbod()
    return

def automated_updater(context: CallbackContext):
    updater_aanbod()
    context.bot.send_message(chat_id='150602383', text='update doorgevoerd voor Rijnland, Haaglanden en Woonbron', parse_mode=ParseMode.HTML)

def rijnland_aanbod_bericht(update, context):
    msg = context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Het woningaanbod van Woonnet Rijnland wordt opgehaald',
                                   parse_mode=ParseMode.HTML)
    context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=Rijnland_overzicht.aanbod_message(), parse_mode=ParseMode.HTML)

def haaglanden_aanbod_bericht(update, context):
    msg = context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Het woningaanbod van Woonnet Haaglanden wordt opgehaald',
                                   parse_mode=ParseMode.HTML)
    context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id,
                                  text=Haaglanden_overzicht.aanbod_message(), parse_mode=ParseMode.HTML)

def woonbron_aanbod_bericht(update, context):
    msg = context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Het woningaanbod van Woonbron Direct huren wordt opgehaald',
                                   parse_mode=ParseMode.HTML)
    context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=Woonbron_overzicht.aanbod_message(), parse_mode=ParseMode.HTML)

def woonbron_oud_aanbod_bericht(update, context):
    msg = context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Het oud woningaanbod van Woonbron Direct huren wordt opgehaald',
                                   parse_mode=ParseMode.HTML)
    context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=Woonbron_overzicht.oud_aanbod_message(), parse_mode=ParseMode.HTML)

def unknown_callback(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, dat commando begreep ik niet.")

start_handler = CommandHandler('start', start_callback)
unknown_handler = MessageHandler(Filters.command, unknown_callback)
rijnland_aanbod_handler = CommandHandler('rijnland', rijnland_aanbod_bericht)
rijnmond_aanbod_handler = CommandHandler('rijnmond', rijnmond_aanbod_bericht)
woonbron_aanbod_handler = CommandHandler('woonbron', woonbron_aanbod_bericht)
woonbron_oud_aanbod_handler = CommandHandler('woonbron_oud', woonbron_oud_aanbod_bericht)
haaglanden_aanbod_handler = CommandHandler('haaglanden', haaglanden_aanbod_bericht)

dispatcher.add_error_handler(error_callback)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(rijnmond_aanbod_handler)
dispatcher.add_handler(rijnland_aanbod_handler)
dispatcher.add_handler(woonbron_aanbod_handler)
dispatcher.add_handler(woonbron_oud_aanbod_handler)
dispatcher.add_handler(haaglanden_aanbod_handler)
# The unknown_handler must be added last.
dispatcher.add_handler(unknown_handler)


job_queue.run_daily(automated_updater, datetime.time(hour=8, minute=0, tzinfo=pytz.timezone('Europe/Amsterdam')))
job_queue.run_daily(automated_updater, datetime.time(hour=12, minute=30, tzinfo=pytz.timezone('Europe/Amsterdam')))
job_queue.run_daily(automated_updater, datetime.time(hour=20, minute=30, tzinfo=pytz.timezone('Europe/Amsterdam')))
job_queue.run_daily(rijnmond_update_bericht, datetime.time(hour=18, minute=38, tzinfo=pytz.timezone('Europe/Amsterdam')))

updater.start_polling()
updater.idle()