from aiogram import F, Router
from aiogram.types import CallbackQuery

document_templates_router = Router(name="document_templates")


@document_templates_router.callback_query(F.data == 'support_document_templates')
async def document_templates_button_press(callback: CallbackQuery):
    await callback.message.answer(
        text="""Пройдите по ссылке и заполните данные
        https://drive.google.com/drive/folders/1zoAhc8G8zSAqZVFkWWDVl0V2yIROW_gX """)
