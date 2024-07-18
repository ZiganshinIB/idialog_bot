import logging
import argparse
import os

import requests
import json

from dotenv import load_dotenv
from google.cloud import dialogflow_v2beta1
from google.cloud import dialogflow


PROJECT_ID = os.getenv('DIALOG_FLOW_PROJECT_ID')


def get_dialog_response( text, session_id, language_code='ru'):
    session_client = dialogflow_v2beta1.SessionsClient()
    session = session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow_v2beta1.types.TextInput(
        text=text,
        language_code=language_code
    )
    query_input = dialogflow_v2beta1.types.QueryInput(text=text_input)
    dialogflow_response = session_client.detect_intent(
        session=session,
        query_input=query_input)
    response = {
        'is_fallback': dialogflow_response.query_result.is_fallback,
        'query_text': dialogflow_response.query_result.query_text,
        'intent': dialogflow_response.query_result.intent.display_name,
        'confidence':
            dialogflow_response.query_result.intent_detection_confidence,
        'response_text': dialogflow_response.query_result.fulfillment_text,
    }
    return response


def create_intent(
        display_name,
        training_phrases_parts,
        message_texts
):
    """ Create an intent.
    :param display_name: Тема интента
    :param training_phrases_parts: Список набора фраз, предложении и сообщений.
    :param message_texts: Ответы на training_phrases_parts.
    """
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(PROJECT_ID)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part
        )
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)
    messages = []
    for message_text in message_texts:
        message = dialogflow.Intent.Message.Text(text=[message_text])
        message = dialogflow.Intent.Message(text=message)
        messages.append(message)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=messages
    )

    google_response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(google_response))


def load_intents(
        intents_data,
        training_phrases_parts_name='questions',
        message_texts_name='answer'
):
    """
    Загружает интенты в Google Cloud.
    :param intents_data: Словарь с названиями интентов и списком наборов фраз.
    :param training_phrases_parts_name: Название словаря с наборами фраз.
    :param message_texts_name: Название словаря с сообщениями.
    Example intents_data = {
        display_name: {
            training_phrases_parts_name: [
                phrase1,
                phrase2,
                ...
            ],
            message_texts_name: [
                message1,
                message2,
                ...
        },
        ...
    }
    """
    if type(intents_data) is not dict:
        raise TypeError('intents_data must be a dict')
    for display_name, intents in intents_data.items():
        if type(intents) is not dict:
            raise TypeError('intents must be a dict')
        if type(intents[training_phrases_parts_name]) is not list:
            raise TypeError('training_phrases_parts must be a list')
        training_phrases = intents[training_phrases_parts_name]
        if type(intents[message_texts_name]) is list:
            message_texts = intents[message_texts_name]
        else:
            message_texts = [intents[message_texts_name]]
        create_intent(
            display_name,
            training_phrases,
            message_texts
        )


def load_url_intents(url):
    """
    Загружает интенты из JSON-файла.
    :param url: URL-адрес JSON-файла с интентами.
    """
    response = requests.get(url)
    response.raise_for_status()
    data_for_dialog = json.loads(response.content)
    load_intents(data_for_dialog)


# Более подробнее читать:
# https://github.com/ZiganshinIB/idialog_bot/tree/main?tab=readme-ov-file#%D0%B4%D0%BE%D0%BF%D0%BE%D0%BB%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5-%D1%84%D0%B8%D1%87%D0%B8
if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(
        description='Описание что делает программа'
    )
    parser.add_argument('-u', '--url',
                        help='URL-адрес JSON-файла с интентами',
                        default="https://dvmn.org/media/filer_public/a7/db/a7db66c0-1259-4dac-9726-2d1fa9c44f20/questions.json")
    parser.add_argument('-p', '--project_id',
                        help='ID проекта в Google Cloud',
                        default=PROJECT_ID)
    args = parser.parse_args()
    url = args.url
    PROJECT_ID = args.project_id
    logger = logging.getLogger(__name__)
    try:
        response = requests.get(url, timeout=4)
        response.raise_for_status()
        data_for_dialog = json.loads(response.content)
        for display_name, intent in data_for_dialog.items():
            training_phrases = intent['questions']
            message_texts = intent['answer']
            create_intent(display_name, training_phrases,
                          [message_texts])
    except Exception as e:
        logger.error(
            "Произошла ошибка при загрузке интентов из JSON-файла: " + str(e),
        )

