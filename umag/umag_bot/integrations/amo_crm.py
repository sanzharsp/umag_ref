from aiogram.types import User, CallbackQuery
from dotenv import load_dotenv
from pytz import timezone
from datetime import datetime
import requests
import time
import os

load_dotenv()

task_api = str(os.getenv("TASK_API"))
lead_api = str(os.getenv("LEAD_API"))
customfield_id = int(os.getenv("AMOCRM_CUSTOM_FIELD"))
customfield_id_link = int(os.getenv("AMOCRM_CUSTOM_FIELD_LINK"))


def get_access_token():
    url = os.getenv("AMO_GET_ACCESS_TOKEN_URL")
    key = os.getenv("AMO_CLIENT_SECRET")
    responce = requests.post(url,
                             json={'key': key})
    if responce.status_code == 200:
        return responce.json()['access_token']
    elif responce.status_code == 400:
        pass
        print("ошибка в запросе получения токена ")
    elif responce.status_code == 401:
        print("Ключь для получения токена не правильный")


def base_request(method, endpoint, data=None):
    subdomain = os.getenv("AMO_SUBDOMAIN")
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    url = f"https://{subdomain}.amocrm.ru{endpoint}"

    if method == "get":
        return requests.get(url, headers=headers).json()
    elif method == "post":
        return requests.post(url, json=data, headers=headers).json()
def base_request_large(method, endpoint, data=None):
    subdomain = os.getenv("AMO_SUBDOMAIN")
    headers = {"Authorization": f"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjQ1ZGNkN2RlMDQ5ZmFhOTg1M2Q1NWNiYTJmOWY3MjI5ZGZlYzhhM2E5NDI2MzEwMGI1OWYxOTY2NzZkOTY5NzNmYjViZDM1Y2M4NDc5YWYyIn0.eyJhdWQiOiJjYzJiODUxMi1kNTIyLTRiYTAtODQ2ZC0wZDliZWUyMzYxNzUiLCJqdGkiOiI0NWRjZDdkZTA0OWZhYTk4NTNkNTVjYmEyZjlmNzIyOWRmZWM4YTNhOTQyNjMxMDBiNTlmMTk2Njc2ZDk2OTczZmI1YmQzNWNjODQ3OWFmMiIsImlhdCI6MTcxODYxNjk0MywibmJmIjoxNzE4NjE2OTQzLCJleHAiOjE3MTk3MDU2MDAsInN1YiI6IjExMTQ5OTIyIiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNzk2MjkwLCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiZjBjOWFmNjAtMDU2Ny00ZjE1LTlmZWUtZDJlOWJmYWZiZjMzIn0.Ck7vJp3szkIY9TplC77ZTCa-9Ts0apAL-NV5uUaYKwQgRMHpEgFphqmYoFuSAZ-J-12gHqILjBHUFWE2T_igg-LuOR6OezP4syRyrYRbjFGgnaiN--VEmwsL_qN2Tsac5xhPLCjYtr_z0B5xMrAoLobUN4f9oiEY6mInyl8rDBKZYaR_oBLBWf-OJaJKdRA70XM__vZv3jNPcZhnMjN3ahm1p6AH7bGbgdeNDwxLVjQ1r1C05uwpNPsjzlXSGaXWHjQg421AgdTASqXmaAun-wv9I6-pdzaovH7bpGZgFI5ID_4JC1ZgWqMNmlohoVAOy6iwgqAL6LPor2MGLIRdPw"}
    url = f"https://{subdomain}.amocrm.ru{endpoint}"

    if method == "get":
        return requests.get(url, headers=headers).json()
    elif method == "post":
        return requests.post(url, json=data, headers=headers).json()


def get_datetime():
    astana_timezone = timezone('Asia/Almaty')
    now_datetime = datetime.now(astana_timezone)
    due_date_timestamp = int(time.mktime(now_datetime.timetuple()))
    return due_date_timestamp


def consultation_tasks_request(user, data: dict) -> str:
    # Пример использования
    lead_response = base_request(method="post",
                                 endpoint=lead_api,
                                 data=[
                                     {
                                         "name": "Клиент просит консультцию",
                                         "custom_fields_values": [
                                             {
                                                 "field_id": customfield_id,
                                                 "values": [
                                                     {
                                                         "value":
                                                             f"""Клиент просит консультцию:\n
                                                                                        1. Имя: {data['name']}\n
                                                                                        2. Наименование франшизы: {data['franchise_name']}\n
                                                                                        3. Номер телефона: {data['phone_number']}\n
                                                                                        4. Описание проблемы:{data['problem_description']}\n
                                                                                        5. Имя пользователя в телеграм: {user.username}  
                                                                                        """
                                                     }
                                                 ]
                                             }
                                         ]
                                     }
                                 ]
                                 )
    print(lead_response)
    lead_id = lead_response['_embedded']['leads'][0]['id']

    return lead_id


def synchronization_tasks_request(user, data: dict) -> str:
    lead_response = base_request(method="post", endpoint=lead_api, data=
                                                            [
                                                                {
                                                                    "name": "Синхронизация",
                                                                    "custom_fields_values": [
                                                                        {
                                                                            "field_id": customfield_id,
                                                                            "values": [
                                                                                {
                                                                                    "value":
                                                                                        f"""
                                                                                    Синхронизация:\n
                                                                                    1. Имя: {data['name']}\n
                                                                                    2. Наименование франшизы: {data['franchise_name']}\n
                                                                                    3. Номер телефона : {data['phone_number']}\n
                                                                                    4. Название проблемы должно быть коротким, понятным и отвечать на вопросы где и в чем проблема: {data['problem_name']}\n
                                                                                    5. Название магазина: {data['shop_name']}\n
                                                                                    6. Версия кассы: {data['cash_register_version']}\n
                                                                                    7. Имя кассира: {data['cashier_name']}\n
                                                                                    8. Пароль от кассы: {data['cash_register_password']}\n
                                                                                    9. Ссылка на магазин: {data['link_to_shop']}\n
                                                                                    10. Ссылка на архив: {data['link_to_archive']}\n
                                                                                    11. Логин: {data['login']}\n
                                                                                    12. Пароль: {data['password']}\n                                                                                    
                                                                                    """
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                 )

    lead_id = lead_response['_embedded']['leads'][0]['id']


    return lead_id


def getcourse_tasks_request(user, data: dict) -> str:
    lead_response = base_request(method="post", endpoint=lead_api, data=
                                                        [
                                                            {
                                                                "name": "GetCource",
                                                                "custom_fields_values": [
                                                                    {
                                                                        "field_id": customfield_id,
                                                                        "values": [
                                                                            {
                                                                                "value":
                                                                                    f"""
                                                                                        1. Имя: {data['name']}
                                                                                        2. Наименование франшизы: {data['franchise_name']}
                                                                                        3. Номер телефона: {data['phone']}
                                                                                        4. Электронная почта: {data['email']}
                                                                                        5. Вид обучения : 
                                                                                        - {data['study_type_value']}                                                                               
                                                                                    """
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                 )

    lead_id = lead_response['_embedded']['leads'][0]['id']


    return lead_id


def bug_tasks_request(user: User, data: dict) -> str:
    url = ''
    if ("type" not in data):
        url = ''

    elif (data['type'] == 'photo'):
        telegram_file_id = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/getFile?file_id={data["photo"][0].file_id}'
        file_path = requests.get(telegram_file_id).json()
        url = f'https://api.telegram.org/file/bot{os.getenv("BOT_TOKEN")}/{file_path["result"]["file_path"]}'

    elif (data['type'] == 'document'):
        telegram_file_id = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/getFile?file_id={data["document"].file_id}'
        file_path = requests.get(telegram_file_id).json()
        url = f'https://api.telegram.org/file/bot{os.getenv("BOT_TOKEN")}/{file_path["result"]["file_path"]}'

    elif (data['type'] == 'video'):
        telegram_file_id = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/getFile?file_id={data["video"].file_id}'
        file_path = requests.get(telegram_file_id).json()
        url = f'https://api.telegram.org/file/bot{os.getenv("BOT_TOKEN")}/{file_path["result"]["file_path"]}'
    lead_response = base_request(method="post", endpoint=lead_api, data=[
                                                                            {
                                                                                "name": "Баг",
                                                                                "custom_fields_values": [
                                                                                    {
                                                                                        "field_id": customfield_id,
                                                                                        "values": [
                                                                                            {
                                                                                                "value":
                                                                                                    f"""
                                                                                                    Баг:
                                                                                                    1. Имя: {data['name']}
                                                                                                    2. Наименование франшизы: {data['franchise_name']}
                                                                                                    3. Номер телефона: {data['phone_number']}
                                                                                                    4. Название бага: {data['bug_name']}
                                                                                                    5. Описание и сценарий: {data['description_and_scenario']}
                                                                                                    6. Идентификатор телеграм: {user.id}   
                                                                                                    7. Имя пользователя в телеграм: {user.username}                                                                        
                                                                                                """
                                                                                            }
                                                                                        ]
                                                                                    },
                                                                                    {
                                                                                        "field_id": customfield_id_link,
                                                                                        "values": [
                                                                                            {
                                                                                                "value": f"{url}"
                                                                                            }
                                                                                        ]
                                                                                    }
                                                                                ],

                                                                            }
                                                                        ]
                                                                        )
    print(lead_response)
    lead_id = lead_response['_embedded']['leads'][0]['id']




    return lead_id


def new_request(user: User, data: dict) -> str:
    if data['workflow'] == 'consultation':
        #lead_id = consultation_tasks_request(user, data)
        return f"Успешно подана заявка для консультаций. ✅"
    if data['workflow'] == 'synchronization':
        #lead_id = synchronization_tasks_request(user, data)
        return f"Успешно подана заявка для синхронизаций. ✅"
    if data['workflow'] == 'getcourse':
        #lead_id = getcourse_tasks_request(user, data)
        return f"Успешно подана заявка в Getcourse ✅"
    if data['workflow'] == 'bug':
        #lead_id = bug_tasks_request(user, data)
        return f"Успешно подана заявка для выявления бага ✅"


def request_bot_answer(callback: CallbackQuery, text: str = "Здесь ничего не передано") -> None:
    from_user = callback.from_user
    message = callback.message
    #dt_now_utc = callback.message.date.replace(tzinfo=timezone.utc)
    import json
    object_amo = {
        "update_id": 958310245,
        "message": {
            "message_id": message.message_id,
            "from": {
                "id": from_user.id,
                "is_bot": False,
                "first_name": from_user.first_name,
                "username": from_user.username,
                "language_code": from_user.language_code
            },
            "chat": {
                "id": callback.message.chat.id,
                "first_name": callback.message.chat.first_name,
                "username": callback.message.chat.username,
                "type": callback.message.chat.type
            },
            "date": callback.message.date.timestamp(),
            "text": text
        }
    }
    data = json.dumps(object_amo)
    request_data=requests.post('https://amojo.amocrm.ru/~external/hooks/telegram?t=6397638357:AAEF4kljx7MgkA56vx5jTbB-lAjWkLVLVk4',
                  data=object_amo)

    print(request_data)

    # Преобразование datetime в timestamp

    print(callback)
    print(callback.message)
    print(callback.from_user.id)



def get_contacts():
    contacts_response = base_request_large(method="get", endpoint='/api/v4/leads/')
    print(contacts_response)

