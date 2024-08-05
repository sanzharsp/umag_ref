from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot_workflows.utils import fetch_unrated_bugs, fetch_unrated_consultation, fetch_unrated_synchronization


async def menu(telegram_id):
    menu = [
        [InlineKeyboardButton(text="Консультация", callback_data="support_consultation"), ],
        [InlineKeyboardButton(text="Баг", callback_data="support_bug"), ],
        [InlineKeyboardButton(text="Синхронизация", callback_data="support_synchronization"), ],
        [InlineKeyboardButton(text="Доступ на идеальную флешку", callback_data="support_access_flash"), ],
        [InlineKeyboardButton(text="База знаний", callback_data="support_knowledge_base"), ],
        [InlineKeyboardButton(text="Доступ на обучение в GetCource", callback_data="support_getcource"), ],
        [InlineKeyboardButton(text="Шаблоны документов", callback_data="support_document_templates"), ],
        [InlineKeyboardButton(text="Ваши идеи по улучшению ПО", callback_data="support_ideas")]
    ]

    bugs = await fetch_unrated_bugs(telegram_id)
    consultation = await fetch_unrated_consultation(telegram_id)
    synchronization = await fetch_unrated_synchronization(telegram_id)

    for bug in bugs:
        menu.append([InlineKeyboardButton(text=f"Оцените качество техподдержки (Баг)",
                                          callback_data=f"rate_bug:{bug['id']}")])
    for consult in consultation:
        menu.append([InlineKeyboardButton(text=f"Оцените качество техподдержки (Консультация)",
                                          callback_data=f"rate_consultation:{consult['id']}")])
    for sync in synchronization:
        menu.append([InlineKeyboardButton(text=f"Оцените качество техподдержки (Синхранизация)",
                                          callback_data=f"rate_synchronization:{sync['id']}")])

    return menu


# Пример использования:
# telegram_id = 123456789  # Замените на реальный telegram_id пользователя
# keyboard = await update_menu_with_bugs(telegram_id)


# menu = [
#     [InlineKeyboardButton(text="Консультация ", callback_data="support_consultation"),
#      InlineKeyboardButton(text="Баг", callback_data="support_bug")],
#     [InlineKeyboardButton(text="Синхронизация ", callback_data="support_synchronization"),
#      InlineKeyboardButton(text="Доступ на идеальную флешку", callback_data="support_access_flash")],
#     [InlineKeyboardButton(text="База знаний", callback_data="support_knowledge_base"),
#      InlineKeyboardButton(text="Доступ на обучение в GetCource", callback_data="support_getcource")],
#     [InlineKeyboardButton(text="Шаблоны документов", callback_data="support_document_templates"),
#      InlineKeyboardButton(text="Ваши идеи по улучшению ПО", callback_data="support_ideas")
#      ]
# ]

change_persona_data = [
    [InlineKeyboardButton(text="Изменить ", callback_data="change_persona_data_button"), ],
]
change_persona_register = [
    [InlineKeyboardButton(text="Заполнить ", callback_data="change_persona_data_register_button"), ],
]

command_menu: dict[str, str] = {
    '/start': 'Запуск бота',
    '/menu': 'Меню',
    '/personal_data': 'Личные данные'
}
