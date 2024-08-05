from aiogram import F, Router
from aiogram.types import CallbackQuery

access_flash_router = Router(name="access_flash")


@access_flash_router.callback_query(F.data == 'support_access_flash')
async def access_flash_button_press(callback: CallbackQuery):
    await callback.message.answer(
        text="""Пройдите по ссылке и заполните данные
https://drive.google.com/drive/folders/14I5pnfYjhLz7P6cXMYEbypl0iOG6KnG6 """)
