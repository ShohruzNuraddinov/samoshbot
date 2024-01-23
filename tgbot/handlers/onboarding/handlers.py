import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import User, Settings
from tgbot.handlers.onboarding.keyboards import (
    UZBEK,
    RUSSIAN,
    main_keyboard,
    language_keyboard,
)
from tgbot import states


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if not u.language:
        text = "Tilni tanlang / Выберите язык"
        update.message.reply_text(text, reply_markup=language_keyboard())
        return states.LANGUAGE
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)
        update.message.reply_text(text=text, reply_markup=main_keyboard())
        # return states.MAIN


def choose_correct_lang(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    text = "Tilni tanlang / Выберите язык Quyidagilardan birini kiriting."
    update.message.reply_text(text, reply_markup=language_keyboard())
    return states.LANGUAGE


def choose_language(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if update.message.text == UZBEK:
        u.language = "uz"
    elif update.message.text == RUSSIAN:
        u.language = "ru"
    u.save()
    text = static_text.start_not_created.format(first_name=u.first_name)
    update.message.reply_text(text=text, reply_markup=main_keyboard())
    return ConversationHandler.END


def contact(update: Update, context: CallbackContext) -> None:
    settings = Settings.objects.first()

    text = f"<b>{settings.description}</b>\n\n📞 Telefon: {settings.contact}"
    update.message.reply_text(
        text, reply_markup=main_keyboard(), parse_mode='HTML')
    # return states.CONTACT


def review(update: Update, context: CallbackContext) -> None:
    text = """
SamOshni tanlaganingiz uchun rahmat.

Agar siz bizning xizmat sifatimizni yaxshilashimizga yordam bersangiz hursand bulardik.
Buning uchun 5 ball tizim asosida baholang"""

    update.message.reply_text(
        text, reply_markup=main_keyboard(), parse_mode='HTML')
    # return states.REVIEW


def main_handler(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Bosh menu", reply_markup=main_keyboard()
    )
