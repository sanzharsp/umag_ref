from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from .utils import update_user_data, validate_phone_number, save_user_data, check_availability

change_persona_edit = [
    [InlineKeyboardButton(text="Номер телефона", callback_data="change_persona_data_phone_number"),
     InlineKeyboardButton(text="Наименование франшизы", callback_data="change_persona_data_franchise_name")],
    [InlineKeyboardButton(text="Имя", callback_data="change_persona_data_name"),
     ],
]



def updated_persona_data(result):
    html_content = '<b>Ваши персональные данные!</b>\n' \
                   "\n" \
                   f"<b>Имя</b>: <i>{result['first_name']}</i>\n" \
                   f"<b>Наименование франшизы</b>: <i>{result['franchise_name']}</i>\n" \
                   f"<b>Номер телефона</b>: <i>{result['phone_number']}</i>\n"
    return html_content


class ChangeData(StatesGroup):
    name = State()
    franchise_name = State()
    phone_number = State()

    name_register=State()
    franchise_name_register=State()
    phone_number_register=State()


chage_data = Router(name="chage_data")


@chage_data.callback_query(F.data == 'change_persona_data_button')
async def getcourse_button_press(callback: CallbackQuery, state: FSMContext):
    print(callback)
    markup = InlineKeyboardMarkup(inline_keyboard=change_persona_edit)
    await callback.message.answer(
        f"""Список изменяемых данных""", reply_markup=markup)





@chage_data.callback_query(F.data == 'change_persona_data_phone_number')
async def getcourse_button_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        f"""Введите номер телефона""")
    await state.set_state(ChangeData.phone_number)

@chage_data.callback_query(F.data == 'change_persona_data_franchise_name')
async def getcourse_button_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        f"""Введите наименование франшизы""")
    await state.set_state(ChangeData.franchise_name)

@chage_data.callback_query(F.data == 'change_persona_data_name')
async def getcourse_button_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        f"""Введите свое имя""")
    await state.set_state(ChangeData.name)


@chage_data.message(ChangeData.phone_number)
async def process_franchise_name(message: Message, state: FSMContext) -> None:
    if validate_phone_number(message.text):
        result, check = await update_user_data(message.chat.id, {"phone_number": message.text})
        if check:
            await message.answer(
                f"""Данные успешно изменены""")
            await state.clear()
            await message.answer(updated_persona_data(result), parse_mode=ParseMode.HTML)
        else:
            await message.answer(
                "Произошла ошибка при сохранении данных")

    else:
        await message.answer(
            "Номер телефона введен некорректно. Пожалуйста, введите номер в формате +7 (7xx) xxx-xx-xx.")

@chage_data.message(ChangeData.franchise_name)
async def process_franchise_name(message: Message, state: FSMContext) -> None:
    result, check = await update_user_data(message.chat.id, {"franchise_name": message.text})
    if check:
        await message.answer(
                f"""Данные успешно изменены""")
        await state.clear()
        await message.answer(updated_persona_data(result), parse_mode=ParseMode.HTML)
    else:
        await message.answer(
                "Произошла ошибка при сохранении данных")

@chage_data.message(ChangeData.name)
async def process_franchise_name(message: Message, state: FSMContext) -> None:
    result, check = await update_user_data(message.chat.id, {"first_name": message.text})
    if check:
        await message.answer(
                f"""Данные успешно изменены""")
        await state.clear()
        await message.answer(updated_persona_data(result), parse_mode=ParseMode.HTML)
    else:
        await message.answer(
                "Произошла ошибка при сохранении данных")



@chage_data.callback_query(F.data == 'change_persona_data_register_button')
async def getcourse_button_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Ваше Имя")
    await state.set_state(ChangeData.name_register)

@chage_data.message(ChangeData.name_register)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name_register=message.text)
    await message.answer("Введите наименование франшизы")
    await state.set_state(ChangeData.franchise_name_register)

@chage_data.message(ChangeData.franchise_name_register)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(franchise_name_register=message.text)
    await message.answer("Введите номер телефона")
    await state.set_state(ChangeData.phone_number_register)


@chage_data.message(ChangeData.phone_number_register)
async def process_name(message: Message, state: FSMContext) -> None:
    if validate_phone_number(message.text):
        await state.update_data(phone_number_register=message.text)
        data = await state.get_data()
        print(data)
        await save_user_data({
  "telegram_id": message.chat.id,
  "first_name": data['name_register'],
  "franchise_name": data['franchise_name_register'],
  "phone_number": data['phone_number_register']
})
        result, chek = await check_availability(message.chat.id)
        await message.answer(updated_persona_data(result), parse_mode=ParseMode.HTML)
    else:
        await message.answer(
            "Номер телефона введен некорректно. Пожалуйста, введите номер в формате +7 (7xx) xxx-xx-xx.")
