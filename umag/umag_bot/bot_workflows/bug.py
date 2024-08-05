from aiogram.enums import ContentType, ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from integrations.amo_crm import new_request as amo_request
from .utils import validate_phone_number, send_amocrm, check_availability, save_user_data,bug_save,check_any_unrated
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class BugForm(StatesGroup):
    name = State()
    franchise_name = State()
    phone_number = State()
    bug_name = State()
    description_and_scenario = State()
    app_version = State()
    personal_account_access = State()
    additional_information = State()


bug_router = Router(name="bug")


@bug_router.callback_query(F.data == 'support_bug')
async def bug_button_press(callback: CallbackQuery, state: FSMContext):

    if await check_any_unrated(callback.from_user.id, callback) == False:
        result, check = await check_availability(callback.from_user.id)
        if check:
            await callback.message.answer("Название бага")
            await state.set_state(BugForm.bug_name)
            return

        await callback.message.answer("Ваше Имя")
        await state.set_state(BugForm.name)
    else:
        return

@bug_router.message(BugForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer("Введите наименование франшизы")
    await state.set_state(BugForm.franchise_name)


@bug_router.message(BugForm.franchise_name)
async def process_franchise_name(message: Message, state: FSMContext) -> None:
    await state.update_data(franchise_name=message.text)
    await message.answer("Номер телефона")
    await state.set_state(BugForm.phone_number)



@bug_router.message(BugForm.phone_number)
async def process_phone_number(message: Message, state: FSMContext) -> None:
    if validate_phone_number(message.text):
        await state.update_data(phone_number=message.text)
        await message.answer("Название бага")
        await state.set_state(BugForm.bug_name)
        register_data = await state.get_data()


        user_data = {
            "telegram_id": message.chat.id,
            "first_name": register_data['name'],
            "franchise_name": register_data['franchise_name'],
            "phone_number": register_data['phone_number']
        }
        await save_user_data(user_data)

    else:
        await message.answer(
            "Номер телефона введен некорректно. Пожалуйста, введите номер в формате +7 (7xx) xxx-xx-xx."
        )


@bug_router.message(BugForm.bug_name)
async def process_bug_name(message: Message, state: FSMContext) -> None:
    await state.update_data(bug_name=message.text)
    await message.answer("Описание и сценарий. Подробное описание бага и сценарий воспроизведения (последовательные действия), которые нужно совершить, чтобы воспроизвести баг:")
    await state.set_state(BugForm.description_and_scenario)


@bug_router.message(BugForm.description_and_scenario)
async def process_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description_and_scenario=message.text)
    await message.answer("Версия приложения:")
    await state.set_state(BugForm.app_version)

@bug_router.message(BugForm.app_version)
async def process_app_version(message: Message, state: FSMContext) -> None:
    await state.update_data(app_version=message.text)
    await message.answer("Доступ от личного кабинета:")
    await state.set_state(BugForm.personal_account_access)

@bug_router.message(BugForm.personal_account_access)
async def process_description(message: Message, state: FSMContext) -> None:
    await state.update_data(personal_account_access=message.text)
    await message.answer("Видео, фото, видеозаметки, аудио или файлы")
    await state.set_state(BugForm.additional_information)

@bug_router.message(BugForm.additional_information)
async def process_additional_information(message: Message, state: FSMContext) -> None:
    content_type = message.content_type
    data = {"type": content_type.value}
    result = {ctype: False for ctype in ContentType.__members__.keys()}

    if content_type == ContentType.PHOTO:
        best_photo = message.photo[-1]
        result['photo'] = best_photo
        data[ContentType.PHOTO.value] = best_photo
    elif content_type == ContentType.VIDEO:
        result['video'] = message.video
        data[ContentType.VIDEO.value] = message.video
    elif content_type == ContentType.DOCUMENT:
        result['document'] = message.document
        data[ContentType.DOCUMENT.value] = message.document
    elif content_type == ContentType.VOICE:
        result['voice'] = message.voice
        data[ContentType.VOICE.value] = message.voice
    elif content_type == ContentType.AUDIO:
        result['audio'] = message.audio
        data[ContentType.AUDIO.value] = message.audio
    elif content_type == ContentType.VIDEO_NOTE:
        result['video_note'] = message.video_note
        data[ContentType.VIDEO_NOTE.value] = message.video_note
    elif content_type == ContentType.STICKER:
        result['sticker'] = message.sticker
        #data[ContentType.STICKER.value] = message.sticker
        await message.answer("Пожалуйста, отправляйте только видео, фото, видеозаметки, аудио и файлы.🙌")
        return
    elif content_type == ContentType.TEXT:
        result['text'] = message.text
        #data[ContentType.TEXT.value] = message.text
        await message.answer("Пожалуйста, отправляйте только видео, фото, видеозаметки, аудио и файлы.🙌")
        return


    await state.update_data(additional_information=result)
    await state.update_data(data)

    data = await state.get_data()
    data["workflow"] = "bug"
    save_data = await state.get_data()
    await state.set_state(None)
    await state.clear()
    bug_save_result = await bug_save({
        "telegram_id": message.chat.id,
        "bug_name": save_data['bug_name'],
        "app_version": save_data['app_version'],
        "personal_account_access": save_data['personal_account_access'],
        "description_and_scenario": save_data['description_and_scenario'],
        "additional_information": str(result)
    })

    result, chek = await check_availability(message.chat.id)

    if chek:
        data['name']=result['first_name']
        data['franchise_name']=result['franchise_name']
        data['phone_number']=result['phone_number']
    send_object_data(message, data)
    result = amo_request(message.from_user, data)

    # Создаем кнопку и клавиатуру
    # button = InlineKeyboardButton(text="Оценить качество обращения в (Баг)",
    #                               callback_data=f"rate_bug:{bug_save_result['id']}")
    # keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    # Отправляем сообщение
    await message.answer(result)



def send_object_data(message, data):
    additional_info = data.get('additional_information', {})
    text = additional_info.get('text', False)
    additional_text = f"🚫Дополнительная информация: {text}" if text else ""

    object_data = {
        'message': {
            'message_id': message.message_id,
            'from': {
                'id': message.chat.id,
                'is_bot': message.from_user.is_bot,
                'first_name': message.from_user.first_name,
                'username': message.from_user.username,
                'language_code': message.from_user.language_code
            },
            'chat': {
                'id': message.chat.id,
                'first_name': message.chat.first_name,
                'username': message.chat.username,
                'type': message.chat.type
            },
            'date': int(message.date.timestamp()),
            'text': f"""
                Клиент хочет сообщить о баге

                🚫 Имя: {data['name']}
                🚫 Наименование франшизы: {data['franchise_name']}
                🚫 Номер телефона: {data['phone_number']}
                🚫 Название бага: {data['bug_name']}
                🚫 Описание и сценарий: {data['description_and_scenario']}
                🚫 Версия приложения: {data['app_version']}
                🚫 Доступ от личного кабинета:{data['personal_account_access']}
                {additional_text}
            """,
        }
    }

    if additional_info:
        for key, value in additional_info.items():
            if value:
                if key == 'photo':
                    photo_info = {
                        'file_id': value.file_id,
                        'file_unique_id': value.file_unique_id,
                        'file_size': value.file_size,
                        'width': value.width,
                        'height': value.height
                    }
                    object_data['message']['photo'] = [photo_info]

                    object_data['message']['text'] += "🚫Дополнительная информация: Клиент прикрепил фото \n"
                    if message.caption:
                        object_data['message']['text'] += f"✍️ Описание фото: {message.caption}"
                elif key == 'document':
                    document_info = {
                        'file_id': value.file_id,
                        'file_unique_id': value.file_unique_id,
                        'file_name': value.file_name,
                        'mime_type': value.mime_type,
                        'file_size': value.file_size
                    }
                    object_data['message']['document'] = document_info
                    object_data['message']['text'] += "🚫Дополнительная информация: Клиент прикрепил документ \n"
                    if message.caption:
                        object_data['message']['text'] += f"✍️ Описание документа: {message.caption}"
                elif key == 'voice':
                    voice_info = {
                        'file_id': value.file_id,
                        'file_unique_id': value.file_unique_id,
                        'duration': value.duration,
                        'mime_type': value.mime_type,
                        'file_size': value.file_size
                    }
                    object_data['message']['voice'] = voice_info
                    object_data['message'][
                        'text'] += "🚫Дополнительная информация: Клиент отправил голосовое сообщение \n"
                    if message.caption:
                        object_data['message']['text'] += f"✍️ Описание голосового сообщения: {message.caption}"
                elif key == 'video':

                    video_info = {
                        'file_id': value.file_id,
                        'file_unique_id': value.file_unique_id,
                        'width': value.width,
                        'height': value.height,
                        'duration': value.duration,
                        'thumb': {
                            'file_id': value.thumb['file_id'],
                            'file_unique_id': value.thumb['file_unique_id'],
                            'width': value.thumb['width'],
                            'height': value.thumb['height']
                        },
                        'mime_type': value.mime_type,
                        'file_size': value.file_size
                    }
                    object_data['message']['video'] = video_info
                    object_data['message']['text'] += "🚫Дополнительная информация: Клиент отправил видео \n"
                    if message.caption:
                        object_data['message']['text'] += f"✍️ Описание видео: {message.caption}"
                elif key == 'audio':
                    audio_info = {
                        'file_id': value.file_id,
                        'file_unique_id': value.file_unique_id,
                        'duration': value.duration,
                        'performer': value.performer,
                        'title': value.title,
                        'mime_type': value.mime_type,
                        'file_size': value.file_size
                    }
                    object_data['message']['audio'] = audio_info
                    object_data['message']['text'] += "🚫Дополнительная информация: Клиент отправил аудио \n"
                    if message.caption:
                        object_data['message']['text'] += f"✍️ Описание аудио: {message.caption}"
                elif key == 'video_note':
                    video_note_info = {
                        'file_id': value.file_id,
                        'file_unique_id': value.file_unique_id,
                        'length': value.length,
                        'duration': value.duration,
                        'thumb': {
                            'file_id': value.thumb['file_id'],
                            'file_unique_id': value.thumb['file_unique_id'],
                            'width': value.thumb['width'],
                            'height': value.thumb['height']
                        },
                        'file_size': value.file_size
                    }
                    object_data['message']['video_note'] = video_note_info
                    object_data['message']['text'] += "🚫Дополнительная информация: Клиент отправил видео-заметку \n"
                    if message.caption:
                        object_data['message']['text'] += f"✍️ Описание видео-заметки: {message.caption}"
                elif key == 'sticker':
                    sticker_info = {
                        'file_id': value.file_id,
                        'file_unique_id': value.file_unique_id,
                        'width': value.width,
                        'height': value.height,
                        'is_animated': value.is_animated,
                        'thumb': {
                            'file_id': value.thumb['file_id'],
                            'file_unique_id': value.thumb['file_unique_id'],
                            'width': value.thumb['width'],
                            'height': value.thumb['height'],
                            'file_size': value.thumb['file_size']
                        },
                        'emoji': value.emoji,
                        'set_name': value.set_name,
                        'file_size': value.file_size
                    }
                    object_data['message']['sticker'] = sticker_info
                    object_data['message']['text'] += "🚫Дополнительная информация: Клиент отправил стикер \n"
                    if message.caption:
                        object_data['message']['text'] += f"✍️ Описание стикера: {message.caption}"
                elif key == 'text':
                    object_data['message']['text'] += f"🚫Дополнительная информация: {value} \n"
    object_data['message']['text']+= f"Идентификатор telegram: {message.chat.id}"
    send_amocrm(object_data)
    return object_data
