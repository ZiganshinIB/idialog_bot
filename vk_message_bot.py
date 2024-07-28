import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
import os
from dotenv import load_dotenv
import logging
from logger import MyLogsHandler
from dialog_flow_worker import get_dialog_response


logger = logging.getLogger(__name__)


def git_dialog_flow_response(event, vk_api) -> None:
    """
    A function that generates a response for a dialog using the google dialog flow.

    :param event: the dialog flow event
    :param vk_api: the API for working with VKontakte

    :return: None
    """
    response = get_dialog_response(
        event.text,
        event.user_id)
    response_text = response['response_text']
    vk_api.messages.send(
            user_id=event.user_id,
            message=response_text,
            random_id=0)


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.getenv('VK_API_TOKEN')
    tg_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    tg_log_chat_id = os.getenv('TELEGRAM_BOT_LOGS_CHAT_ID')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.addHandler(MyLogsHandler(tg_bot_token, tg_log_chat_id))
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                git_dialog_flow_response(event, vk_api)
    except Exception as e:
        logger.error(
            "Бот VK перестал работать: " + str(e),
            exc_info=True)
