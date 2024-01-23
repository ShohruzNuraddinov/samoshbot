from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from product.models import Category, Product


def make_category_btn(cart=None):

    categories = Category.objects.filter(parent=None)

    keyboard = []

    if cart:
        keyboard.append(
            [
                '📥 Savatcha'
            ]
        )

    for index in range(0, len(categories), 2):
        if len(categories) - index == 1:
            keyboard.append([categories[index].title])
        else:
            keyboard.append(
                [
                    categories[index].title, categories[index + 1].title
                ]
            )

    keyboard.append(
        [
            "🔙 Orqaga"
        ]
    )
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def make_products_btn(products):

    keyboard = []

    for index in range(0, len(products), 2):
        if len(products) - index == 1:
            keyboard.append([products[index].title])
        else:

            keyboard.append(
                [
                    products[index].title, products[index + 1].title
                ]
            )

    keyboard.append(
        [
            "🔙 Orqaga"
        ]
    )

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def make_cart_quantity_btn():
    keyboard = [
        [
            '1',
            '2',
            '3',
        ],
        [
            '4',
            '5',
            '6',
        ],
        [
            '7',
            '8',
            '9',
        ],
        [
            "🔙 Orqaga"
        ]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def cart_items_keyboard(items):
    keyboard = []

    for item in items:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{item.product.title}", callback_data=f"{item.id}"),
            ],
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    "➖", callback_data=f'cart_minus_{item.id}_{item.quantity - 1}'
                ),
                InlineKeyboardButton(
                    " ❌", callback_data=f'cart_delete_{item.id}_{item.quantity}'
                ),
                InlineKeyboardButton(
                    "➕", callback_data=f'cart_plus_{item.id}_{item.quantity + 1}'
                ),
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton("🛍 Buyurtma berish", callback_data='order')
        ]
    )
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)
