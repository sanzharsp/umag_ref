from celery import shared_task
from django.shortcuts import get_object_or_404

from .models import *
from celery import shared_task
from celery.utils.log import get_task_logger
import telebot
from dotenv import load_dotenv
import os
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


load_dotenv()

logger = get_task_logger(__name__)

API_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN, parse_mode=None)

@shared_task
def delete_hook_data():
    WebhookIssueCreated.objects.all().delete()
    WebhookIssueUpdated.objects.all().delete()
    WebhookIssueDeleted.objects.all().delete()



@shared_task
def access_refresh():
    import requests
    try:
        refresh_token_instance = RefreshAccessToken.objects.first()
        settings_instance = Settings.objects.first()

        if refresh_token_instance and settings_instance:
            data = {
                "client_id": settings_instance.amo_id,
                "client_secret": settings_instance.amo_secret_key,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token_instance.refresh_token,
                "redirect_uri": settings_instance.redirect_url
            }
            response = requests.post(f"https://{settings_instance.subdomain}.amocrm.ru/oauth2/access_token", json=data)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'refresh_token' in response_data and 'access_token' in response_data:
                    refresh_token_instance.refresh_token = response_data["refresh_token"]
                    refresh_token_instance.access_token = response_data["access_token"]
                    refresh_token_instance.save()
                    print("Tokens updated successfully.")
                else:
                    # Handle the case where 'refresh_token' or 'access_token' is not in response
                    print("Expected token(s) not in response. Response:", response_data)
            else:
                # Handle non-successful status codes
                print(f"Failed to refresh token. Status code: {response.status_code}, Response: {response.text}")
        else:
            print("Refresh token instance or settings instance not found.")
    except Exception as e:
        print(f"An error occurred: {e}")




@shared_task
def send_message_consultation_telegram(support_consultation_id, telegram_id):
    support_consultation = get_object_or_404(SupportConsultation, id=support_consultation_id)

    content_type = ContentType.objects.get_for_model(SupportConsultation)
    existing_quality_control = QualityControl.objects.filter(
        content_type=content_type,
        object_id=support_consultation.id
    ).exists()

    if existing_quality_control:
        return
    else:
        menu = InlineKeyboardMarkup()
        menu.row(
        InlineKeyboardButton(text=f"Оценить качество консультаций", callback_data=f"rate_consultation:{support_consultation_id}")
        )
        bot.send_message(telegram_id, "Оцените качество обслуживания:", reply_markup=menu)


@shared_task
def send_message_synchronization_telegram(support_synchronization_id, telegram_id):
    synchronization = get_object_or_404(SupportSynchronization, id=support_synchronization_id)

    content_type = ContentType.objects.get_for_model(SupportSynchronization)
    existing_quality_control = QualityControl.objects.filter(
        content_type=content_type,
        object_id=synchronization.id
    ).exists()

    if existing_quality_control:
        return
    else:
        menu = InlineKeyboardMarkup()
        menu.row(
        InlineKeyboardButton(text=f"Оценить качество синхронизации", callback_data=f"rate_synchronization:{support_synchronization_id}")
        )
        bot.send_message(telegram_id, "Оцените качество обслуживания:", reply_markup=menu)