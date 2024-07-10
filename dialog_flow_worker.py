import requests
import json
from google.cloud import dialogflow_v2beta1
from google.cloud import dialogflow


def get_dialog_response(project_id, text, session_id, language_code='ru'):
    session_client = dialogflow_v2beta1.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow_v2beta1.types.TextInput(
        text=text,
        language_code=language_code
    )
    query_input = dialogflow_v2beta1.types.QueryInput(text=text_input)
    dialogflow_response = session_client.detect_intent(
        session=session,
        query_input=query_input)
    response = {
        'query_text': dialogflow_response.query_result.query_text,
        'intent': dialogflow_response.query_result.intent.display_name,
        'confidence':
            dialogflow_response.query_result.intent_detection_confidence,
        'response_text': dialogflow_response.query_result.fulfillment_text,
    }
    return response


def create_intent(
        project_id,
        display_name,
        training_phrases_parts,
        message_texts
):
    """ Create an intent.
    :param project_id: ID проекта в Google Cloud
    :param display_name: Тема интента
    :param training_phrases_parts: Список набора фраз, предложении и сообщений.
    :param message_texts: Ответы на training_phrases_parts.
    """
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
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
    response.raise_for_status()
    data_for_dialog = json.loads(response.content)
    load_intents(project_id, data_for_dialog)
