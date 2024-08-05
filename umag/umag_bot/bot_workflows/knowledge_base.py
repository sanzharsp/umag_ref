from aiogram import F, Router
from aiogram.types import CallbackQuery

knowledge_base_router = Router(name="knowledge_base")


@knowledge_base_router.callback_query(F.data == 'support_knowledge_base')
async def knowledge_base_button_press(callback: CallbackQuery):
    await callback.message.answer(
        text="""Пройдите по ссылке - https://umag.kz/knowledge-base""")
