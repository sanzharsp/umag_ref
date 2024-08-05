from dotenv import load_dotenv
import os
import telebot
from .models import *
from django.shortcuts import get_object_or_404
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


load_dotenv()
bot_token = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(bot_token, parse_mode=None)

def send_telegram_message(chat_id, message):
    try:
        bot.send_message(chat_id, message, parse_mode="Markdown")

    except Exception as e:
        print(e)


def send_telegram_bug(chat_id):
    personal_data = PersonalData.objects.get(telegram_id=chat_id)
    support_bug_id = SupportBug.objects.filter(personal_data=personal_data).latest('id')
    support_bug = get_object_or_404(SupportBug, id=support_bug_id.id)

    content_type = ContentType.objects.get_for_model(SupportConsultation)
    existing_quality_control = QualityControl.objects.filter(
        content_type=content_type,
        object_id=support_bug.id
    ).exists()

    if existing_quality_control:
        return
    else:
        menu = InlineKeyboardMarkup()
        menu.row(
        InlineKeyboardButton(text=f"Оценить качество бага", callback_data=f"rate_bug:{support_bug_id.id}")
        )
        bot.send_message(chat_id, "Оцените качество бага:", reply_markup=menu)

