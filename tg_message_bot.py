import logging
import os
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext)
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


def get_dialog_flow_response(update: Update, context: CallbackContext) -> None:
    """
    A function that generates a response for a dialog using the google dialog flow.

    :param update: The incoming update from the user.
    :param context: The context for the current callback.
    :return: None
    """
    response_text = get_dialog_response(
        project_id,
        update.message.text,
        update.message.chat_id)['response_text']
    update.message.reply_text(response_text)


def main() -> None:
    """Start the bot."""
    tg_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    tg_log_chat_id = os.getenv('TELEGRAM_BOT_LOGS_CHAT_ID')
    logger.addHandler(MyLogsHandler(tg_bot_token, tg_log_chat_id))
    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command, get_dialog_flow_response))
    # Start the Bot
    try:
        updater.start_polling()
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
    except Exception as e:
        logger.error(
            "Бот Telegram перестал работать: " + str(e),
            exc_info=True)


if __name__ == '__main__':
    load_dotenv()
    project_id = os.getenv('DIALOG_FLOW_PROJECT_ID')
    main()
