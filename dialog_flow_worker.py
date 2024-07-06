import requests
import json
from dotenv import load_dotenv
import os
from google.cloud import dialogflow_v2beta1 as dialogflow


def get_dialog_response(text, session_id, language_code='ru'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(os.getenv('DIALOG_FLOW_PROJECT_ID'), session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
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
    from google.cloud import dialogflow

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

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(response))


if __name__ == "__main__":
    load_dotenv()
    response = requests.get('https://dvmn.org/media/filer_public/a7/db/a7db66c0-1259-4dac-9726-2d1fa9c44f20/questions.json')
    data_for_dialog = json.loads(response.content)
    for display_name in data_for_dialog:
        training_phrases = data_for_dialog[display_name]['questions']
        message_texts = data_for_dialog[display_name]['answer']
        project_id = os.getenv('DIALOG_FLOW_PROJECT_ID')
        create_intent(project_id, display_name, training_phrases,
                      [message_texts])
