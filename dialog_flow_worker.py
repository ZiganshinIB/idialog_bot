import requests
import json
from dotenv import load_dotenv
import os
from google.cloud import dialogflow_v2beta1
from google.cloud import dialogflow


def get_dialog_response(text, session_id, language_code='ru'):
    session_client = dialogflow_v2beta1.SessionsClient()
    session = session_client.session_path(os.getenv('DIALOG_FLOW_PROJECT_ID'), session_id)
    text_input = dialogflow_v2beta1.types.TextInput(
        text=text,
        language_code=language_code
    )
    query_input = dialogflow_v2beta1.types.QueryInput(text=text_input)
    dialogflow_response = session_client.detect_intent(session=session, query_input=query_input)
    response = {
        'query_text': dialogflow_response.query_result.query_text,
        'intent': dialogflow_response.query_result.intent.display_name,
        'confidence': dialogflow_response.query_result.intent_detection_confidence,
        'response_text': dialogflow_response.query_result.fulfillment_text,
    }
    return response


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """ Create an intent.
    :param project_id: ID проекта в Google Cloud
    :param display_name: Тема интента
    :param training_phrases_parts: Список набора фраз, предложении и сообщений.
    :param message_texts: Ответ на training_phrases_parts.
    """
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    google_response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(google_response))


def load_intents(
        project_id,
        intents_data,
        training_phrases_parts_name='questions',
        message_texts_name='answer'
):
    """
    Загружает интенты в Google Cloud.
    :param project_id: ID проекта в Google Cloud
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
    if type(intents_data) != dict:
        raise TypeError('intents_data must be a dict')
    for display_name, intents in intents_data.items():
        if type(intents) != dict:
            raise TypeError('intents must be a dict')
        for k, v in intents.items():
            if k == training_phrases_parts_name:
                if type(v) != list:
                    raise TypeError('training_phrases_parts must be a list')
                training_phrases = v
            elif k == message_texts_name:
                if type(v) == list:
                    message_texts = v
                else:
                    message_texts = [v]
            else:
                raise Exception(f'Unknown key: {k}')

        create_intent(
            project_id,
            display_name,
            training_phrases,
            message_texts
        )


def load_url_intents(project_id, url):
    """
    Загружает интенты из JSON-файла.
    :param project_id: ID проекта в Google Cloud
    :param url: URL-адрес JSON-файла с интентами.
    """
    response = requests.get(url)
    if 200 <= response.status_code < 300:
        raise Exception(response.content)
    else:
        data_for_dialog = json.loads(response.content)
        load_intents(project_id, data_for_dialog)
