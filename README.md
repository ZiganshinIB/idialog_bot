# Бот для общение 
Бот который может понимать речь и отвечать на вопросы
## Задачи, которые выполняет
* Общение в телеграм 
* Интеграция с Google DialogFlow
## Требования 
* рекомендуется Python 3.9(можно З.7, 3.8, 3.10) 
* требуется создать приложение [dialog flow в google cloud](https://cloud.google.com/dialogflow/es/docs/quick/setup)
## Запуск проекта
### 1. Загрузка на локальное устройство 
```shell
git clone https://github.com/ZiganshinIB/idialog_bot
cd idialog_bot
```
### 2. Создание витруального окружение
```shell
python -m venv .venv
```
#### 2.1 Активация витруального окружение
```shell
source .venv/bin/activate
```
### 3. Установка зависимостей
```shell
pip install -r requirements.txt
```
### 4. Создание переменых сред
В проекте используются токены (ключи и пароли), которые не должны хранится в открытом доступе. По этому такие данные храним в системной переменных среде, следующим образом:
В директории с проектом создается файл `.env`
```shell
nano .env
```
Заполняется следующим способом
```text
TELEGRAM_BOT_TOKEN='Токен_для_телеграм_бота'
TELEGRAM_BOT_LOGS_CHAT_ID=1
DIALOG_FLOW_PROJECT_ID='название вашего проекта'
GOOGLE_API_KEY='Google api ключ'
GOOGLE_APPLICATION_CREDENTIALS='/home/ziganshinib/.config/gcloud/application_default_credentials.json'
DIALOGFLOW_SESSION_ID='me'
VK_API_TOKEN=''
```
* Как получить токен для телеграм бота описана [тут](https://core.telegram.org/bots#how-do-i-create-a-bot)
* TELEGRAM_BOT_LOGS_CHAT_ID - идентификатор чата куда будуть логи работы программы. [Узнать чат id](https://docs.leadconverter.su/faq/populyarnye-voprosy/telegram/kak-uznat-id-telegram-gruppy-chata)
* DIALOG_FLOW_PROJECT_ID - название проекта
* GOOGLE_API_KEY - личный ключ. [Инструкция](https://cloud.google.com/docs/authentication/api-keys)
* VK_API_TOKEN инструкция по получению токена [тут](https://vk.com/@vksoftred-kak-poluchit-token-soobschestva-vkontakte)


### 5. Запуск проектов
```shell
python tg_message_bot.py
python vk_message_bot.py
```