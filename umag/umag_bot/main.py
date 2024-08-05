from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.command import Command, BotCommand
from command import menu, command_menu as menu_command, change_persona_data,\
    change_persona_register
from bot_workflows.access_flash import access_flash_router
from bot_workflows.bug import bug_router
from bot_workflows.consultation import consultation_router
from bot_workflows.document_templates import document_templates_router
from bot_workflows.getcourse import getcourse_router
from bot_workflows.ideas import ideas_router
from bot_workflows.knowledge_base import knowledge_base_router
from bot_workflows.synchronization import synchronization_router
from bot_workflows.change_data import chage_data
from bot_workflows.rate import rate_router
import logging
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from integrations.middleware import CounterMiddleware
from bot_workflows.utils import check_availability
import os
from dotenv import load_dotenv



load_dotenv()
# Bot token can be obtained via https://t.me/BotFather
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
# Webserver settings
# bind localhost only to prevent any external access
WEB_SERVER_HOST = "0.0.0.0"
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = 8080

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/webhook/bot"


# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public DNS with HTTPS support
BASE_WEBHOOK_URL = "https://jira-notifications.umag.kz"
#BASE_WEBHOOK_URL = "https://661d-185-210-139-161.ngrok-free.app"

# All handlers should be attached to the Router (or Dispatcher)
router = Router()
dp = Dispatcher()
dp.update.middleware(CounterMiddleware())


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in menu_command.items()
    ]
    await bot.set_my_commands(main_menu_commands)


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", allowed_updates=["message", "callback_query"])
    await set_main_menu(bot)






@dp.message(Command("menu"))
async def command_menu(message: types.Message, state: FSMContext):
    await state.clear()
    markup = InlineKeyboardMarkup(inline_keyboard = await menu(message.chat.id))
    await message.answer("""
Меню
Выберите вид обращения:
        """, reply_markup=markup)
    await state.clear()

@dp.message(Command("personal_data"))
async def command_menu(message: types.Message, state: FSMContext):
    await state.clear()
    result, check = await check_availability(message.chat.id)

    if check:
        html_content = '<b>Ваши персональные данные!</b>\n' \
                        "\n"\
                       f"<b>Имя</b>: <i>{result['first_name']}</i>\n" \
                       f"<b>Наименование франшизы</b>: <i>{result['franchise_name']}</i>\n" \
                       f"<b>Номер телефона</b>: <i>{result['phone_number']}</i>\n" \


        await message.answer(html_content, parse_mode=ParseMode.HTML)
        markup = InlineKeyboardMarkup(inline_keyboard=change_persona_data)
        await message.answer(
        f"""Если ваши данные неверны, измените их ✍️""", reply_markup=markup)
        return

    markup = InlineKeyboardMarkup(inline_keyboard=change_persona_register)
    await message.answer(
    f"""Заполните повторяемые данные ✍️""", reply_markup=markup)

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    "Запуск бота"
    markup = InlineKeyboardMarkup(inline_keyboard=await menu(message.chat.id))
    await message.answer(
        f"""
Здравствуйте, {hbold(message.from_user.full_name)}.  
Вы обратились в UMAG-Support! 😊
Выберите вид обращения:
        """,
        reply_markup=markup)

    await state.clear()

def main() -> None:
    # Dispatcher is a root router

    # ... and all other routers should be attached to Dispatcher

    dp.startup.register(on_startup)
    dp.include_routers(
        access_flash_router,
        chage_data,
        bug_router,
        consultation_router,
        document_templates_router,
        getcourse_router,
        ideas_router,
        knowledge_base_router,
        synchronization_router,
        rate_router,
    )






    # Initialize Bot instance with a default parse mode which will be passed to all API calls


    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,

    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()


#
# import asyncio
# import logging
# import sys
# from dotenv import load_dotenv
# from aiogram import Bot, Dispatcher, Router, F
# from aiogram.enums import ParseMode
# from aiogram.filters import CommandStart
# from aiogram.types import Message, InlineKeyboardMarkup
# from aiogram.utils.markdown import hbold
# from aiogram import types
# from aiogram.filters.command import Command, BotCommand
# from command import menu, command_menu
# from bot_workflows.access_flash import access_flash_router
# from bot_workflows.bug import bug_router
# from bot_workflows.consultation import consultation_router
# from bot_workflows.document_templates import document_templates_router
# from bot_workflows.getcourse import getcourse_router
# from bot_workflows.ideas import ideas_router
# from bot_workflows.knowledge_base import knowledge_base_router
# from bot_workflows.synchronization import synchronization_router
# import os
# load_dotenv()
# TOKEN = "2117376163:AAFNxVNaPR7cX8F3noAdOsy3RyfeeqyMQ0Q"
# dp = Dispatcher()
# main_router = Router()
#
# async def set_main_menu(bot: Bot):
#     main_menu_commands = [
#         BotCommand(
#             command=command,
#             description=description
#         ) for command, description in command_menu.items()
#     ]
#     await bot.set_my_commands(main_menu_commands)
#
#
# @dp.message(Command("menu"))
# async def command_menu(message: types.Message):
#     markup = InlineKeyboardMarkup(inline_keyboard=menu)
#     await message.answer("""
# Меню
# Выберите вид обращения:
#     """, reply_markup=markup)
#
#
#
# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     "Запуск бота"
#     markup = InlineKeyboardMarkup(inline_keyboard=menu)
#     await message.answer(
#         f"""
# Здравствуйте, {hbold(message.from_user.full_name)}.
# Вы обратились в UMAG-Support! 😊
# Выберите вид обращения:
#     """,
#         reply_markup=markup)
#
#
#
# async def main() -> None:
#     bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
#     dp.include_routers(
#         access_flash_router,
#         bug_router,
#         consultation_router,
#         document_templates_router,
#         getcourse_router,
#         ideas_router,
#         knowledge_base_router,
#         synchronization_router)
#     await dp.start_polling(bot)
#
#
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, stream=sys.stdout)
#     asyncio.run(main())
