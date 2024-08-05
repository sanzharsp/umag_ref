from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F, Router
from integrations.amo_crm import new_request as amo_request
from .utils import validate_phone_number, validate_email_simple, send_amocrm, check_availability, save_user_data, get_course_save


class GetCourseForm(StatesGroup):
    name = State()
    franchise_name = State()
    phone_number = State()
    email = State()
    study_type = State()


study_type_map = {
    "franchisee": "Франчайзи",
    "technical_specialist": "Технический специалист",
    "sales_manager": "Менеджер по продажам",
    "hr": "HR"
}

study_type_buttons = [
    [InlineKeyboardButton(text=value, callback_data=key)]
    for key, value in study_type_map.items()
]

getcourse_router = Router(name="getcourse")


@getcourse_router.callback_query(F.data == 'support_getcource')
async def getcourse_button_press(callback: CallbackQuery, state: FSMContext):
    result, check = await check_availability(callback.from_user.id)
    if check:
        await callback.message.answer("Электронная почта")
        await state.set_state(GetCourseForm.email)
        return
    await callback.message.answer("Ваше Имя")
    await state.set_state(GetCourseForm.name)


@getcourse_router.message(GetCourseForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer("Введите наименование франшизы")
    await state.set_state(GetCourseForm.franchise_name)


@getcourse_router.message(GetCourseForm.franchise_name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(franchise_name=message.text)
    await message.answer("Номер телефона")
    await state.set_state(GetCourseForm.phone_number)


@getcourse_router.message(GetCourseForm.phone_number)
async def process_name(message: Message, state: FSMContext) -> None:
    if validate_phone_number(message.text):
        await state.update_data(phone_number=message.text)
        await message.answer("Электронная почта")
        await state.set_state(GetCourseForm.email)
        register_data = await state.get_data()


        user_data = {
            "telegram_id": message.chat.id,
            "first_name": register_data['name'],
            "franchise_name": register_data['franchise_name'],
            "phone_number": register_data['phone_number']
        }
        await save_user_data(user_data)
    else:
        await message.answer("Номер телефона введен некорректно. Пожалуйста, введите номер в формате +7 (7xx) xxx-xx-xx.")


@getcourse_router.message(GetCourseForm.email)
async def process_name(message: Message, state: FSMContext) -> None:
    if validate_email_simple(message.text):
        await state.update_data(email=message.text)
        markup = InlineKeyboardMarkup(inline_keyboard=study_type_buttons)
        await message.answer("Вид обучения", reply_markup=markup)
        await state.set_state(GetCourseForm.study_type)
    else:
        await message.answer("Электронный адрес введен некорректно. Пожалуйста, введите адрес в формате someone@example.com.")


@getcourse_router.message(GetCourseForm.study_type)
async def process_name(message: Message, state: FSMContext) -> None:
    if message.text not in study_type_map.keys():
        await message.delete()
        return
    await state.update_data({
        "study_type_key": message.text,
        "study_type_value": study_type_map[message.text]
    })
    data = await state.get_data()
    data["workflow"] = "getcourse"
    result = amo_request(message.from_user, data)
    await message.answer(result)
    await state.set_state(None)


@getcourse_router.callback_query(GetCourseForm.study_type)
async def process_name(callback: CallbackQuery, state: FSMContext) -> None:

    await state.update_data({
        "study_type_key": callback.data,
        "study_type_value": study_type_map[callback.data]
    })
    data = await state.get_data()
    data["workflow"] = "getcourse"
    result, chek = await check_availability(callback.from_user.id)
    if chek:
        data['name'] = result['first_name']
        data['franchise_name'] = result['franchise_name']
        data['phone_number'] = result['phone_number']
    save_data = await state.get_data()
    await get_course_save({
        "telegram_id": callback.from_user.id,
        "email": save_data["email"],
        "study_type": study_type_map[callback.data]

    })
    send_object_data(callback, data)
    result = amo_request(callback.from_user, data)
    await callback.message.answer(result)
    await state.set_state(None)


def send_object_data(callback_query: CallbackQuery, data):
    message = callback_query.message
    from_user = callback_query.from_user

    object_data = {
        'message': {
            'message_id': message.message_id,
            'from': {
                'id': from_user.id,
                'is_bot': from_user.is_bot,
                'first_name': from_user.first_name,
                'username': from_user.username,
                'language_code': from_user.language_code
            },
            'chat': {
                'id': message.chat.id,
                'first_name': message.chat.first_name,
                'username': message.chat.username,
                'type': message.chat.type
            },
            'date': int(message.date.timestamp()),
            'text': f"""
                💻 Клиент выбрал запись в GetCource:

                💻 Имя: {data['name']}
                💻 Наименование франшизы: {data['franchise_name']}
                💻 Номер телефона: {data['phone_number']}
                💻 Email: {data['email']}
                💻 Вид обучения: {data['study_type_value']}
            """,
        }
    }

    send_amocrm(object_data)
    return object_data