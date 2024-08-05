from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from .utils import rate_save
rate_router = Router(name="rate")

class RateBugForm(StatesGroup):
    id = State()
    rate = State()

class RateConsultationForm(StatesGroup):
    id = State()
    rate = State()

class RateSynchronizationForm(StatesGroup):
    id = State()
    rate = State()

@rate_router.callback_query(F.data.startswith('rate_bug:'))
async def bug_button_press(callback: CallbackQuery, state: FSMContext):
    _,bug_id = callback.data.split(':')
    await state.update_data(id=bug_id)
    await callback.message.answer(f"Пожалуйста, оцените качество от 1 (очень плохо) до 5 (очень хорошо)")
    await state.set_state(RateBugForm.rate)


@rate_router.callback_query(F.data.startswith('rate_consultation:'))
async def bug_consultation_press(callback: CallbackQuery, state: FSMContext):
    _,consultation_id = callback.data.split(':')
    await state.update_data(id=consultation_id)
    await callback.message.answer(f"Пожалуйста, оцените качество от 1 (очень плохо) до 5 (очень хорошо)")
    await state.set_state(RateConsultationForm.rate)


@rate_router.callback_query(F.data.startswith('rate_synchronization:'))
async def bug_consultation_press(callback: CallbackQuery, state: FSMContext):
    _,synchronization_id = callback.data.split(':')
    await state.update_data(id=synchronization_id)
    await callback.message.answer(f"Пожалуйста, оцените качество от 1 (очень плохо) до 5 (очень хорошо)")
    await state.set_state(RateSynchronizationForm.rate)


@rate_router.message(RateBugForm.rate)
async def process_rate(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        rate = int(message.text)
        if 0 < rate <= 5:
            await state.update_data(rate=rate)
            await message.answer(f"Спасибо за вашу оценку. 😊 Чтобы подать новое обращение, нажмите «меню»")
            form_data = await state.get_data()
            await rate_save(
                {
                    "model_name": "supportbug",
                    "object_id": form_data['id'],
                    "rating": rate
                }
            )
            await state.clear()
            return
    await message.answer("Нужно ввести цифру от 1 до 5")


@rate_router.message(RateConsultationForm.rate)
async def process_rate(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        rate = int(message.text)
        if 0 < rate <= 5:
            await state.update_data(rate=rate)
            await message.answer(f"Спасибо за вашу оценку. 😊 Чтобы подать новое обращение, нажмите «меню»")
            form_data = await state.get_data()
            await rate_save(
                {
                    "model_name": "supportconsultation",
                    "object_id": form_data['id'],
                    "rating": rate
                }
            )
            await state.clear()
            return
    await message.answer("Нужно ввести цифру от 1 до 5")


@rate_router.message(RateSynchronizationForm.rate)
async def process_rate(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        rate = int(message.text)
        if 0 < rate <= 5:
            await state.update_data(rate=rate)
            await message.answer(f"Спасибо за вашу оценку. 😊 Чтобы подать новое обращение, нажмите «меню»")
            form_data = await state.get_data()
            await rate_save(
                {
                    "model_name": "supportsynchronization",
                    "object_id": form_data['id'],
                    "rating": rate
                }
            )
            await state.clear()
            return
    await message.answer("Нужно ввести цифру от 1 до 5")