from aiogram import F, Router
from aiogram.types import CallbackQuery

ideas_router = Router(name="ideas")


@ideas_router.callback_query(F.data == 'support_ideas')
async def ideas_button_press(callback: CallbackQuery):
    await callback.message.answer(
        text="""Пройдите по ссылке и заполните данные
        https://docs.google.com/forms/d/1sFV7A9ZT45cO2JIFHnuf_hIK0AFaak6eJPnsYoTedp0/edit""")
