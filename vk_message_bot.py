import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
import os
from dotenv import load_dotenv
from google.cloud import dialogflow_v2beta1 as dialogflow
import logging
from logger import MyLogsHandler
from dialog_flow_worker import get_dialog_response
logger = logging.getLogger(__name__)


def dialog_flow_response(event, vk_api) -> None:
    """Echo the user message."""
    try:
        response_text = get_dialog_response(event.text, event.user_id)['response_text']
        vk_api.messages.send(user_id=event.user_id, message=response_text, random_id=0)
    except Exception as e:
        logger.error("VK: " + str(e), exc_info=True)


def main() -> None:
    """Start the bot."""
    load_dotenv()
    vk_session = vk.VkApi(token=os.getenv('VK_API_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.addHandler(MyLogsHandler())
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                dialog_flow_response(event, vk_api)
    except Exception as e:
        logger.error("Бот VK перестала работать: " + str(e), exc_info=True)
 

if __name__ == "__main__":
    main()

