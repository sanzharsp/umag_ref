from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from integrations.amo_crm import new_request as amo_request
from .utils import validate_phone_number, send_amocrm, check_availability, save_user_data, synchronization_save, \
    check_any_unrated, synchronization_period_message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class SynchronizationForm(StatesGroup):
    name = State()
    franchise_name = State()
    phone_number = State()
    problem_name = State()
    shop_name = State()
    cash_register_version = State()
    cashier_name = State()
    cash_register_password = State()
    link_to_shop = State()
    link_to_archive = State()
    login = State()
    password = State()


synchronization_router = Router(name="synchronization")


@synchronization_router.callback_query(F.data == 'support_synchronization')
async def synchronization_button_press(callback: CallbackQuery, state: FSMContext):
    if await check_any_unrated(callback.from_user.id, callback) == False:
        result, check = await check_availability(callback.from_user.id)
        if check:
            await callback.message.answer(
            """Название проблемы должно быть коротким, понятным и отвечать на вопросы где и в чем проблема"""
        )
            await state.set_state(SynchronizationForm.problem_name)
            return

        await callback.message.answer("Ваше Имя")
        await state.set_state(SynchronizationForm.name)
    else:
        return


@synchronization_router.message(SynchronizationForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer("Введите наименование франшизы")
    await state.set_state(SynchronizationForm.franchise_name)


@synchronization_router.message(SynchronizationForm.franchise_name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(franchise_name=message.text)
    await message.answer("Номер телефона")
    await state.set_state(SynchronizationForm.phone_number)


@synchronization_router.message(SynchronizationForm.phone_number)
async def process_name(message: Message, state: FSMContext) -> None:
    if validate_phone_number(message.text):
        await state.update_data(phone_number=message.text)
        await message.answer(
            """Название проблемы должно быть коротким, понятным и отвечать на вопросы где и в чем проблема"""
        )
        await state.set_state(SynchronizationForm.problem_name)
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




@synchronization_router.message(SynchronizationForm.problem_name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(problem_name=message.text)
    await message.answer("Название магазина")
    await state.set_state(SynchronizationForm.shop_name)


@synchronization_router.message(SynchronizationForm.shop_name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(shop_name=message.text)
    await message.answer("Версия кассы")
    await state.set_state(SynchronizationForm.cash_register_version)


@synchronization_router.message(SynchronizationForm.cash_register_version)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(cash_register_version=message.text)
    await message.answer("Имя кассира")
    await state.set_state(SynchronizationForm.cashier_name)


@synchronization_router.message(SynchronizationForm.cashier_name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(cashier_name=message.text)
    await message.answer("Пароль от кассы")
    await state.set_state(SynchronizationForm.cash_register_password)


@synchronization_router.message(SynchronizationForm.cash_register_password)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(cash_register_password=message.text)
    await message.answer("Ссылка на магазин")
    await state.set_state(SynchronizationForm.link_to_shop)


@synchronization_router.message(SynchronizationForm.link_to_shop)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(link_to_shop=message.text)
    await message.answer("Ссылка на архив")
    await state.set_state(SynchronizationForm.link_to_archive)


@synchronization_router.message(SynchronizationForm.link_to_archive)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(link_to_archive=message.text)
    await message.answer("Логин")
    await state.set_state(SynchronizationForm.login)


@synchronization_router.message(SynchronizationForm.login)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(login=message.text)
    await message.answer("Пароль")
    await state.set_state(SynchronizationForm.password)

@synchronization_router.message(SynchronizationForm.password)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(password=message.text)
    state_data = await state.get_data()
    data ={}
    data["workflow"] = "synchronization"
    result, chek = await check_availability(message.chat.id)
    if chek:
        data['name'] = result['first_name']
        data['franchise_name'] = result['franchise_name']
        data['phone_number'] = result['phone_number']
        data['problem_name'] =state_data['problem_name']
        data['cash_register_version'] = state_data['cash_register_version']
        data['cashier_name'] = state_data['cashier_name']
        data['cash_register_password'] = state_data['cash_register_password']
        data['link_to_shop'] = state_data['link_to_shop']
        data['link_to_archive'] = state_data['link_to_archive']
        data['login'] = state_data['login']
        data['password'] = message.text

    send_object_data(message, data)
    result = amo_request(message.from_user, data)
    await message.answer(result)
    synchronization_save_result = await synchronization_save({
        "telegram_id": message.chat.id,
       "all_messages": f"""
                    \n1. Название проблемы должно быть коротким, понятным и отвечать на вопросы где и в чем проблема.: {state_data['problem_name']}
                \n2. Название магазина: {state_data['cash_register_version']}
                \n3. Версия кассы: {state_data['cash_register_version']}
                \n4. Имя кассира: {state_data['cashier_name']}
                \n5. Пароль от кассы: {state_data['cash_register_password']}
                \n6. Ссылка на магазин: {state_data['link_to_shop']}
                \n7. Ссылка на архив: {state_data['link_to_archive']}
                \n8. Логин: {state_data['login']}
                \n9. Пароль: {state_data['password']}
       
       """
    })
    await synchronization_period_message({
        "telegram_id": message.chat.id,
        "support_synchronization_id": synchronization_save_result['id']
    })

    await state.set_state(None)


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
                🔄 Клиент выбрал синхронизацию:

                🔄 Имя: {data['name']}
                🔄 Наименование франшизы: {data['franchise_name']}
                🔄 Номер телефона: {data['phone_number']}
                \n1. Название проблемы должно быть коротким, понятным и отвечать на вопросы где и в чем проблема.: {data['problem_name']}
                \n2. Название магазина: {data['cash_register_version']}
                \n3. Версия кассы: {data['cash_register_version']}
                \n4. Имя кассира: {data['cashier_name']}
                \n5. Пароль от кассы: {data['cash_register_password']}
                \n6. Ссылка на магазин: {data['link_to_shop']}
                \n7. Ссылка на архив: {data['link_to_archive']}
                \n8. Логин: {data['login']}
                \n9. Пароль: {data['password']}
            """,
        }
    }
    send_amocrm(object_data)
    return object_data