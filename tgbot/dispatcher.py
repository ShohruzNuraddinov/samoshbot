"""
    Telegram event handlers
"""
from telegram.ext import (
    Dispatcher,
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
)

from dtb.settings import DEBUG
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command

from tgbot.handlers.utils import files, error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.main import bot
from tgbot import states
from tgbot.handlers.onboarding.keyboards import UZBEK, RUSSIAN
from tgbot.handlers.onboarding.static_text import CONTACT_KEYBOARD, ORDER_KEYBOARD
from tgbot.handlers.order.handlers import categories, products, product_detail, cart_save, cart_items, cart_update


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", onboarding_handlers.command_start),
            MessageHandler(Filters.regex(f"^{ORDER_KEYBOARD}$",), categories),
            CallbackQueryHandler(cart_update, pattern='^cart_'),
        ],
        states={
            states.LANGUAGE: [
                MessageHandler(
                    Filters.regex(f"^({UZBEK}|{RUSSIAN})$"),
                    onboarding_handlers.choose_language,
                ),
                MessageHandler(
                    Filters.text,
                    onboarding_handlers.choose_correct_lang,
                ),
            ],
            states.CATEGORY: [
                MessageHandler(
                    Filters.text,
                    products
                ),
                MessageHandler(Filters.regex('^(📥 Savatcha)$'), cart_items),
                CallbackQueryHandler(cart_update, pattern='^cart_')

            ],
            states.PRODUCTS: [
                MessageHandler(
                    Filters.text,
                    product_detail
                )
            ],
            states.PRODUCT_ITEM: [
                MessageHandler(
                    Filters.regex("^(1|2|3|4|5|6|7|8|9|🔙 Orqaga)$"),
                    cart_save
                )
            ]
        },
        fallbacks=[
            CommandHandler("start", onboarding_handlers.command_start),
        ],
    )
    dp.add_handler(conv)

    # admin commands
    dp.add_handler(CommandHandler("admin", admin_handlers.admin))
    dp.add_handler(CommandHandler("stats", admin_handlers.stats))
    dp.add_handler(CommandHandler("export_users", admin_handlers.export_users))

    dp.add_handler(
        MessageHandler(
            Filters.regex(f"^{CONTACT_KEYBOARD}$",),
            onboarding_handlers.contact
        ),
    )

    # dp.add_handler(MessageHandler(Filters.regex('^(📥 Savatcha)$'), cart_items))
    dp.add_handler(CallbackQueryHandler(cart_update, pattern='^cart_'))

    # broadcast message
    dp.add_handler(
        MessageHandler(
            Filters.regex(rf"^{broadcast_command}(/s)?.*"),
            broadcast_handlers.broadcast_command_with_message,
        )
    )
    dp.add_handler(
        CallbackQueryHandler(
            broadcast_handlers.broadcast_decision_handler,
            pattern=f"^{CONFIRM_DECLINE_BROADCAST}",
        )
    )

    # files
    dp.add_handler(
        MessageHandler(
            Filters.animation,
            files.show_file_id,
        )
    )

    dp.add_handler(MessageHandler(
        Filters.text, onboarding_handlers.main_handler))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    # EXAMPLES FOR HANDLERS
    # dp.add_handler(MessageHandler(Filters.text, <function_handler>))
    # dp.add_handler(MessageHandler(
    #     Filters.document, <function_handler>,
    # ))
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))

    return dp


n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(
    Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True)
)
