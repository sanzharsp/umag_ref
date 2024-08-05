from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from integrations.amo_crm import new_request as amo_request
from .utils import validate_phone_number, send_amocrm, check_availability, save_user_data, consultation_save, consultation_period_message,check_any_unrated
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class ConsultationForm(StatesGroup):
    name = State()
    franchise_name = State()
    phone_number = State()
    problem_description = State()


consultation_router = Router(name="consultation")


@consultation_router.callback_query(F.data == 'support_consultation')
async def consultation_button_press(callback: CallbackQuery, state: FSMContext):
    if await check_any_unrated(callback.from_user.id, callback) == False:
        result, check = await check_availability(callback.from_user.id)
        if check:
            await callback.message.answer("Описание проблемы")
            await state.set_state(ConsultationForm.problem_description)
            return
        await callback.message.answer("Ваше Имя")
        await state.set_state(ConsultationForm.name)
    else:
        return


@consultation_router.message(ConsultationForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer("Введите наименование франшизы")
    await state.set_state(ConsultationForm.franchise_name)


@consultation_router.message(ConsultationForm.franchise_name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(franchise_name=message.text)
    await message.answer("Номер телефона")
    await state.set_state(ConsultationForm.phone_number)


@consultation_router.message(ConsultationForm.phone_number)
async def process_name(message: Message, state: FSMContext) -> None:
    if validate_phone_number(message.text):
        await state.update_data(phone_number=message.text)
        await message.answer("Описание проблемы")
        await state.set_state(ConsultationForm.problem_description)
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
            "Номер телефона введен некорректно. Пожалуйста, введите номер в формате +7 (7xx) xxx-xx-xx.")


@consultation_router.message(ConsultationForm.problem_description)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(problem_description=message.text)
    data = await state.get_data()
    data["workflow"] = "consultation"
    result, chek = await check_availability(message.chat.id)
    if chek:
        data['name'] = result['first_name']
        data['franchise_name'] = result['franchise_name']
        data['phone_number'] = result['phone_number']

    send_object_data(message, data)
    await state.set_state(None)
    await state.clear()
    result = amo_request(message.from_user, data)

    await message.answer(result)
    result_save_user= await consultation_save({
        "telegram_id": message.chat.id,
        "description_problem": message.text
    })
    await consultation_period_message({
        "telegram_id": message.chat.id,
        "support_consultation_id": result_save_user['id']
    })



def send_object_data(message, data):
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
                🖊️ Клиент хочет консультацию:

                🖊️ Имя: {data['name']}
                🖊️ Наименование франшизы: {data['franchise_name']}
                🖊️ Номер телефона: {data['phone_number']}
                🖊️ Описание проблемы: {data['problem_description']}
             
            """,
        }
    }
    send_amocrm(object_data)
    return object_data
