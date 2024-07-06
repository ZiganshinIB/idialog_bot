import logging
import os
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dialog_flow_worker import get_dialog_response

from logger import MyLogsHandler

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def dialog_flow_response(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    try:
        response_text = get_dialog_response(update.message.text, update.message.chat_id)['response_text']
        update.message.reply_text(response_text)
    except Exception as e:
        response_text = "Не совсем понял тебя"
        update.message.reply_text(response_text)


def main() -> None:
    """Start the bot."""
    load_dotenv()
    tg_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    tg_log_chat_id = os.getenv('TELEGRAM_BOT_LOGS_CHAT_ID')
    logger.addHandler(MyLogsHandler(tg_bot_token, tg_log_chat_id))
    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, dialog_flow_response))
    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()