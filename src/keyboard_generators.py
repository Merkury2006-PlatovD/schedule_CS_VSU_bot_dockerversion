from telebot import types


def get_persistent_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("📅 Понедельник"),
        types.KeyboardButton("📅 Вторник"),
        types.KeyboardButton("📅 Среда"),
        types.KeyboardButton("📅 Четверг"),
        types.KeyboardButton("📅 Пятница"),
        types.KeyboardButton("📅 Суббота")
    )
    return keyboard


def get_course_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for i in range(1, 5):
        keyboard.add(types.InlineKeyboardButton(text=str(i), callback_data=f"course_{i}"))
    return keyboard


def get_group_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for i in range(1, 18, 3):
        keyboard.add(types.InlineKeyboardButton(text=str(i), callback_data=f"group_{i}"),
                     types.InlineKeyboardButton(text=str(i + 1), callback_data=f"group_{i + 1}"),
                     types.InlineKeyboardButton(text=str(i + 2), callback_data=f"group_{i + 2}"))
    return keyboard


def get_mistake_report_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Подтверждаю", callback_data="mistake_1"),
                 types.InlineKeyboardButton(text="Не подтверждаю", callback_data="mistake_0"))
    return keyboard


def get_subgroup_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="1", callback_data="subgroup_1"))
    keyboard.add(types.InlineKeyboardButton(text="2", callback_data="subgroup_2"))
    return keyboard
