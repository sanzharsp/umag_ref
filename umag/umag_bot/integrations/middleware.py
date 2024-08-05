from aiogram import BaseMiddleware
from aiogram.types import Message
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from bot_workflows.utils import validate_phone_number, validate_email_simple

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


class CounterMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0

    async def SendAmoCrm(self, object_data: object) -> None:
        requests.post(
            f'https://amojo.amocrm.ru/~external/hooks/telegram?t={TOKEN}',
            json=object_data)

    async def __call__(
            self,
            handler,
            event: Message,
            data,
    ):
        # event_data = event.model_dump_json(indent=2)
        # print(event_data)
        # for k, v in data.items():
        #     print(k)
        #     print(k, v)
        # print("event -------------------------------------------------------")
        #
        # print(event)
        #
        # print("handler -------------------------------------------------------")
        #
        # print(handler)
        #
        # print("-------------------------------------------------------")
        #
        # print(data['raw_state'] == 'ConsultationForm:name')
        # print(event.update_id)
        # print(event.message.message_id)
        # print(event.message.date)
        # print(event.message.chat.id)
        # print(event.message.chat.type)
        # print(event.message.chat.username)
        # print(event.message.chat.first_name)
        if event.message is not None:
            await self.handle_message(data, event)


        return await handler(event, data)



    async def handle_message(self, data, event):
        if data["raw_state"] == None:
            message = event.message
            text = str(message.text)

            if message.text not in no_text:  # Только если текст сообщения не в no_text
                text = text.replace('None', '')
                object_data = {
                    'update_id': event.update_id,
                    'message': {
                        'message_id': message.message_id,
                        'from': {
                            'id': message.chat.id,
                            'is_bot': data['event_from_user'].is_bot,
                            'first_name': data['event_from_user'].first_name,
                            'username': data['event_from_user'].username,
                            'language_code': data['event_from_user'].language_code
                        },
                        'chat': {
                            'id': message.chat.id,
                            'first_name': message.chat.first_name,
                            'username': message.chat.username,
                            'type': message.chat.type
                        },
                        'date': int(message.date.timestamp()),
                        'text': text,

                    }
                }
                if message.photo is not None:
                    best_photo = message.photo[-1]
                    photo_info = {
                        'file_id': best_photo.file_id,
                        'file_unique_id': best_photo.file_unique_id,
                        'file_size': best_photo.file_size,
                        'width': best_photo.width,
                        'height': best_photo.height
                    }
                    object_data['message']['photo'] = [photo_info]
                    object_data['message']['text'] += "\nКлиент отправил фото\n"

                if message.document is not None:
                    document = message.document

                    document_info = {
                        'file_id': document.file_id,
                        'file_unique_id': document.file_unique_id,
                        'file_name': document.file_name,
                        'mime_type': document.mime_type,
                        'file_size': document.file_size

                    }

                    object_data['message']['document'] = document_info
                    object_data['message']['text'] += "\nКлиент отправил документ\n"

                if message.voice is not None:
                    voice = message.voice
                    voice_info = {
                        'file_id': voice.file_id,
                        'file_unique_id': voice.file_unique_id,
                        'duration': voice.duration,
                        'mime_type': voice.mime_type,
                        'file_size': voice.file_size
                    }
                    object_data['message']['voice'] = voice_info
                    object_data['message']['text'] += "\nКлиент отправил голосовое сообщение\n"

                if message.video is not None:
                    video = message.video
                    video_info = {
                        'file_id': video.file_id,
                        'file_unique_id': video.file_unique_id,
                        'width': video.width,
                        'height': video.height,
                        'duration': video.duration,
                        'thumb': {
                            'file_id': video.thumb.get('file_id', ''),
                            'file_unique_id': video.thumb.get('file_unique_id', ''),
                            'width': video.thumb.get('width', ''),
                            'height': video.thumb.get('height', '')
                        },
                        'mime_type': video.mime_type,
                        'file_size': video.file_size
                    }
                    object_data['message']['video'] = video_info
                    object_data['message']['text'] += "\nКлиент отправил видео\n"
                if message.audio is not None:
                    audio = message.audio
                    audio_info = {
                        'file_id': audio.file_id,
                        'file_unique_id': audio.file_unique_id,
                        'duration': audio.duration,
                        'performer': audio.performer,
                        'title': audio.title,
                        'mime_type': audio.mime_type,
                        'file_size': audio.file_size
                    }
                    object_data['message']['audio'] = audio_info
                    object_data['message']['text'] += "\nКлиент отправил аудио\n"
                if message.video_note is not None:
                    video_note_main = message.video_note
                    video_note_info = {
                        'file_id': video_note_main.file_id,
                        'file_unique_id': video_note_main.file_unique_id,
                        'length': video_note_main.length,
                        'duration': video_note_main.duration,
                        'thumb': {
                            'file_id': video_note_main.thumb.get('file_id', ''),
                            'file_unique_id': video_note_main.thumb.get('file_unique_id', ''),
                            'file_size': video_note_main.thumb.get('file_size', ''),
                            'width': video_note_main.thumb.get('width', ''),
                            'height': video_note_main.thumb.get('height', '')
                        },
                        'file_size': video_note_main.file_size
                    }
                    object_data['message']['video_note'] = video_note_info
                    object_data['message']['text'] += "\nКлиент отправил видео-заметку\n"

                if message.sticker is not None:
                    sticker = message.sticker
                    sticker_info = {
                        'file_id': sticker.file_id,
                        'file_unique_id': sticker.file_unique_id,
                        'width': sticker.width,
                        'height': sticker.height,
                        'is_animated': sticker.is_animated,
                        'thumb': {
                            'file_id': sticker.thumb.get('file_id', ''),
                            'file_unique_id': sticker.thumb.get('file_unique_id', ''),
                            'width': sticker.thumb.get('width', ''),
                            'height': sticker.thumb.get('height', ''),
                            'file_size': sticker.thumb.get('file_size', '')
                        },
                        'emoji': sticker.emoji,
                        'set_name': sticker.set_name,
                        'file_size': sticker.file_size
                    }
                    object_data['message']['sticker'] = sticker_info
                    object_data['message']['text'] += "\nКлиент отправил стикер\n"
                if message.caption:
                    object_data['message']['caption'] = message.caption

                await self.SendAmoCrm(object_data)


no_text = [
    '/personal_data',
    '/start',
    '/menu',
    'support_consultation',
    'support_bug',
    'support_synchronization',
    'support_access_flash',
    'support_knowledge_base',
    'support_getcource',
    'support_document_templates',
    'support_ideas',
    'change_persona_data_button',
    'change_persona_data_name',
    'change_persona_data_register_button',
    'change_persona_data_franchise_name',
    'change_persona_data_phone_number'

]
translations = {
    None: "",
    'ConsultationForm:name': "🖊️ Клиент выбрал консультацию и ввел имя: ",
    'ConsultationForm:franchise_name': "🖊️ Клиент ввел наименование франшизы: ",
    'ConsultationForm:phone_number': "🖊️ Клиент ввел номер телефона: ",
    'ConsultationForm:problem_description': "🖊️ Клиент ввел описание проблемы: ",

    'BugForm:name': "🚫 Клиент хочет сообщить о баге и ввел свое имя: ",
    'BugForm:franchise_name': "🚫 Клиент ввел наименование франшизы: ",
    'BugForm:phone_number': "🚫 Клиент ввел номер телефона: ",
    'BugForm:bug_name': "🚫 Клиент ввел название бага: ",
    'BugForm:description_and_scenario': "🚫 Клиент ввел описание и сценарий: ",
    'BugForm:additional_information': "🚫 Клиент ввел дополнительную информацию: ",

    'SynchronizationForm:name': "🔄 Клиент выбрал синхронизацию и ввел имя: ",
    'SynchronizationForm:franchise_name': "🔄 Клиент ввел наименование франшизы ",
    'SynchronizationForm:phone_number': "🔄 Клиент ввел номер телефона: ",
    'SynchronizationForm:problem_name': "🔄 Клиент ввел название проблемы: ",
    'SynchronizationForm:shop_name': "🔄 Клиент ввел название магазина: ",
    'SynchronizationForm:cash_register_version': "🔄 Клиент ввел версию кассы: ",
    'SynchronizationForm:cashier_name': "🔄 Клиент ввел имя кассира: ",
    'SynchronizationForm:cash_register_password': "🔄 Клиент ввел пароль от кассы: ",
    'SynchronizationForm:link_to_shop': "🔄 Клиент ввел ссылку на магазин: ",
    'SynchronizationForm:link_to_archive': "🔄 Клиент имя ссылку на архив: ",
    'SynchronizationForm:login': "🔄 Клиент ввел Логин: ",
    'SynchronizationForm:password': "🔄 Клиент ввел пароль: ",
    'GetCourseForm:name': " 💻 Клиент выбрал запись в GetCource и ввел свое имя: ",
    'GetCourseForm:franchise_name': " 💻 Клиент ввел наименование франшизы: ",
    'GetCourseForm:phone_number': " 💻 Клиент ввел номер телефона: ",
    'GetCourseForm:email': " 💻 Клиент ввел email: ",
    'GetCourseForm:study_type': " 💻 Клиент ввел вид обучения: ",

}
button_translations = {
    "change_persona_data_button": "Изменить",
    'change_persona_data_name': "Имя",
    'change_persona_data_franchise_name': "Наименование франшизы",
    'change_persona_data_phone_number': "Номер телефона",
    'change_persona_data_register_button': "Заполнить",
    "franchisee": "Франчайзи",
    "technical_specialist": "Технический специалист",
    "sales_manager": "Менеджер по продажам",
    "hr": "HR",
    "support_consultation": "Консультация",
    "support_bug": "Баг",
    "support_synchronization": "Синхронизация",
    "support_access_flash": "Доступ на идеальную флешку",
    "support_knowledge_base": "База знаний",
    "support_getcource": "Доступ на обучение в GetCource",
    "support_document_templates": "Шаблоны документов",
    "support_ideas": "Ваши идеи по улучшению ПО",
}
