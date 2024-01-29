from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler


from product.models import Product, Category, Cart
from users.models import User

from tgbot.handlers.onboarding.keyboards import main_keyboard
from tgbot.handlers.order.keyboards import (
    make_category_btn,
    make_products_btn,
    make_cart_quantity_btn,
    cart_items_keyboard,
)

from tgbot import states
from django.db.models import Sum


def categories(update: Update, context: CallbackContext):
    u, created = User.get_user_and_created(update, context)
    cart = Cart.objects.filter(user=u)

    categories = Category.objects.filter(parent=None)

    if not categories:
        update.message.reply_text("Kategoriya topilmadi", reply_markup=main_keyboard())
        return ConversationHandler.END

    update.message.reply_text("Categories", reply_markup=make_category_btn(cart))
    return states.CATEGORY


def products(update: Update, context: CallbackContext):
    u, created = User.get_user_and_created(update, context)
    cart = Cart.objects.filter(user=u)

    if update.message.text == "📥 Savatcha":
        cart_items(update, context)
        # return ConversationHandler.END
        return states.CATEGORY

    if update.message.text == "🔙 Orqaga":
        update.message.reply_text("Bosh Menu", reply_markup=main_keyboard())
        return ConversationHandler.END

    category = Category.objects.get(title=update.message.text)
    products = Product.objects.filter(category=category)

    if not products:
        update.message.reply_text(
            "Mahsulot topilmadi", reply_markup=make_category_btn(cart)
        )
        return states.CATEGORY

    update.message.reply_text(
        update.message.text, reply_markup=make_products_btn(products)
    )
    return states.PRODUCTS


def product_detail(update: Update, context: CallbackContext):
    u, created = User.get_user_and_created(update, context)
    cart = Cart.objects.filter(user=u)

    if update.message.text == "🔙 Orqaga":
        update.message.reply_text("Kategoriya", reply_markup=make_category_btn(cart))
        return states.CATEGORY

    product = Product.objects.get(title=update.message.text)

    if not product:
        update.message.reply_text("Mahsulot topilmadi", reply_markup=main_keyboard())
        return states.PRODUCTS

    text = f"Mahsulot: <b>{product.title}</b>\nHaqida: <b>{product.description}</b>\n\nNarx: <b>{product.price}</b>so'm"

    Cart.objects.create(user=u, product=product)

    if product.image:
        update.message.reply_photo(
            photo=product.image,
            caption=text,
            reply_markup=make_cart_quantity_btn(),
            parse_mode="HTML",
        )
    else:
        update.message.reply_text(
            text, reply_markup=make_cart_quantity_btn(), parse_mode="HTML"
        )

    return states.PRODUCT_ITEM


def cart_save(update: Update, context: CallbackContext):
    u, created = User.get_user_and_created(update, context)
    cart = Cart.objects.filter(user=u).last()
    if update.message.text == "🔙 Orqaga":
        cart.delete()
        update.message.reply_text(
            "Kategoriyalar", reply_markup=make_category_btn(Cart.objects.filter(user=u))
        )
        return ConversationHandler.END

    cart.quantity = int(update.message.text)
    cart.total_price = cart.quantity * cart.product.price
    cart.save()

    update.message.reply_text(
        "Mahsulotni savatchaga saqlandi", reply_markup=main_keyboard()
    )
    return ConversationHandler.END


def cart_items(update: Update, context: CallbackContext):
    u, created = User.get_user_and_created(update, context)
    cart = Cart.objects.filter(user=u)
    btn = cart_items_keyboard(cart)
    text = "<b>Sizning savatchangizda:</b>\n\n"
    total_price = cart.aggregate(total=Sum("total_price"))["total"]
    for item in cart:
        calc_price = item.quantity * item.product.price
        text += f"<b>{item.product.title}</b>\n{item.quantity} x {item.product.price} so'm = <b>{calc_price} so'm</b>\n\n"

    text += f"Umumiy summa: {total_price} so'm"
    update.message.reply_text(text, reply_markup=btn, parse_mode="HTML")


def cart_update(update: Update, context: CallbackContext):
    u, created = User.get_user_and_created(update, context)
    call_data = update.callback_query.data.split("_")

    cart = Cart.objects.get(id=int(call_data[2]))

    if call_data[1] == "plus":
        cart.quantity += 1
        cart.total_price = cart.quantity * cart.product.price
        cart.save()

    if call_data[1] == "minus":
        if int(call_data[3]) == 0:
            cart.delete()
            if Cart.objects.filter(user=u).count() == 0:
                update.callback_query.message.delete()
                update.callback_query.message.reply_text(
                    "Afsuski sizning savatchangiz bo'm-bo'sh.\n"
                    "Keling davom ettiramiz.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                update.callback_query.message.reply_text(
                    text="Kategoriyalar",
                    reply_markup=make_category_btn(Cart.objects.filter(user=u)),
                )
                return states.CATEGORY
        elif int(call_data[3]) > 0:
            cart.quantity -= 1
            cart.total_price = cart.quantity * cart.product.price
            cart.save()

    if call_data[1] == "delete":
        cart.delete()
        if not Cart.objects.filter(user=u).exists():
            update.callback_query.message.delete()
            update.callback_query.message.reply_text(
                "Afsuski sizning savatchangiz bo'm-bo'sh.\n" "Keling davom ettiramiz.",
                reply_markup=ReplyKeyboardRemove(),
            )
            update.callback_query.message.reply_text(
                text="Kategoriyalar",
                reply_markup=make_category_btn(Cart.objects.filter(user=u)),
            )
            return states.CATEGORY

        # return ConversationHandler.END

    carts = Cart.objects.filter(user=u)

    btn = cart_items_keyboard(carts)
    text = "<b>Sizning savatchangizda:</b>\n\n"
    total_price = carts.aggregate(total=Sum("total_price"))["total"]
    for item in carts:
        calc_price = item.quantity * item.product.price
        text += f"<b>{item.product.title}</b>\n{item.quantity} x {item.product.price} so'm = <b>{calc_price} so'm</b>\n\n"

    text += f"Umumiy summa: {total_price} so'm"
    update.callback_query.message.edit_text(text, reply_markup=btn, parse_mode="HTML")
