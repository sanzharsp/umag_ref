from main import dp, bot, WEBHOOK_PATH, BASE_WEBHOOK_URL

from aiogram import Bot
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from bot_workflows.access_flash import access_flash_router
from bot_workflows.bug import bug_router
from bot_workflows.consultation import consultation_router
from bot_workflows.document_templates import document_templates_router
from bot_workflows.getcourse import getcourse_router
from bot_workflows.ideas import ideas_router
from bot_workflows.knowledge_base import knowledge_base_router
from bot_workflows.synchronization import synchronization_router






async def on_startup() -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", allowed_updates=['message', 'callback_query'])


async def create_app():
    dp.startup.register(on_startup)
    dp.include_routers(
        access_flash_router,
        bug_router,
        consultation_router,
        document_templates_router,
        getcourse_router,
        ideas_router,
        knowledge_base_router,
        synchronization_router,
    )

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,

    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host='0.0.0.0', port=8080)
