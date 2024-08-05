import phonenumbers
from aiogram.enums import ParseMode
from phonenumbers import NumberParseException
from email_validator import validate_email, EmailNotValidError
import requests
import os
from dotenv import load_dotenv
import aiohttp
import asyncio
load_dotenv()

headers = {
    "Authorization": str(os.getenv("PERMISSION_KEY"))
}


TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")

def validate_phone_number(phone_number: str) -> bool:
    try:
        number = phonenumbers.parse(phone_number, None)  # Используйте 'KZ' для номеров Казахстана
        return phonenumbers.is_valid_number(number)
    except NumberParseException:
        return False


def validate_email_simple(email: str) -> bool:
    try:
        # Попытка валидации электронной почты
        validate_email(email)
        return True
    except EmailNotValidError:
        # В случае ошибки валидации
        return False


def send_amocrm(object_data):
    requests.post(
        f'https://amojo.amocrm.ru/~external/hooks/telegram?t={TOKEN}',
        json=object_data)

async def check_availability(telegram_id: str) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + f'/api/personaldata/check/{telegram_id}', headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return result, True
            return False, False


async def save_user_data(user_data: dict) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/api/register', json=user_data, headers=headers) as response:
            return response.status == 201

async def update_user_data(telegram_id: str, updated_data: dict) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.patch(BASE_URL + f'/api/personaldata/update/{telegram_id}', json=updated_data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return result, True
            return False, False


async def consultation_save(main_data: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/api/consultation/create', json=main_data, headers=headers) as response:
            return await response.json()

async def bug_save(main_data: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/api/bug/create', json=main_data, headers=headers) as response:
            return await response.json()


async def synchronization_save(main_data: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/api/synchronization/create', json=main_data, headers=headers) as response:
            return await response.json()

async def get_course_save(main_data: dict) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/api/get_course/create', json=main_data, headers=headers) as response:
            return response.status == 201


async def rate_save(main_data: dict) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/api/quality-control/', json=main_data, headers=headers) as response:
            return response.status == 201




# Проверка оценка качеества
async def fetch_unrated_bugs(telegram_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL+f'/api/unrated-bugs/{telegram_id}/', headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []

async def fetch_unrated_consultation(telegram_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL+f'/api/unrated-consultation/{telegram_id}/', headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []

async def fetch_unrated_synchronization(telegram_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL+f'/api/unrated-synchronization/{telegram_id}/', headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []


async def consultation_period_message(main_data: dict) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/api/quality-control-period/consultation', json=main_data, headers=headers) as response:
            return response.status == 201

async def synchronization_period_message(main_data: dict) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL + '/api/quality-control-period/synchronization', json=main_data, headers=headers) as response:
            return response.status == 201


async def check_any_unrated(telegram_id, callback):
    results = await asyncio.gather(
        fetch_unrated_bugs(telegram_id),
        fetch_unrated_consultation(telegram_id),
        fetch_unrated_synchronization(telegram_id)
    )

    for res in results[2]:
        await callback.message.answer(
            f"Пожалуйста, оцените качество ответа на ваше предыдущее обращение "
            f"<b>«Синхронизация от {res['creation_date']}»</b> "
            f"перед подачей нового запроса.",
            parse_mode=ParseMode.HTML
        )

    for res in results[1]:
        await callback.message.answer(
            f"Пожалуйста, оцените качество ответа на ваше предыдущее обращение "
            f"<b>«Консультация от {res['creation_date']}»</b> "
            f"перед подачей нового запроса.",
            parse_mode=ParseMode.HTML
        )

    for res in results[0]:
        await callback.message.answer(
            f"Пожалуйста, оцените качество ответа на ваше предыдущее обращение "
            f"<b>«Баг от {res['creation_date']}»</b> "
            f"перед подачей нового запроса.",
            parse_mode=ParseMode.HTML
        )

    # Проверяем, не пусты ли результаты хотя бы одного из запросов
    for result in results:
        if result:
            return True

    return False
# Проверка что клиент оценил все обслуживания

