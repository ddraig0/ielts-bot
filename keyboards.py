from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📖 Reading", callback_data="section_reading"),
            InlineKeyboardButton(text="🎧 Listening", callback_data="section_listening"),
        ],
        [
            InlineKeyboardButton(text="✍️ Writing", callback_data="section_writing"),
            InlineKeyboardButton(text="🎙️ Speaking", callback_data="section_speaking"),
        ],
        [
            InlineKeyboardButton(text="📊 Statusum", callback_data="my_status"),
            InlineKeyboardButton(text="💳 Abunəlik", callback_data="subscription_info"),
        ]
    ])

def back_to_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu")]
    ])

def reading_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Yeni Mətn", callback_data="reading_new")],
        [InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu")]
    ])

def listening_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Yeni Tapşırıq", callback_data="listening_new")],
        [InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu")]
    ])

def writing_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Task 1 (Qrafik/Cədvəl)", callback_data="writing_task1"),
            InlineKeyboardButton(text="✍️ Task 2 (Esse)", callback_data="writing_task2"),
        ],
        [InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu")]
    ])

def speaking_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Part 1 🗣️", callback_data="speaking_part1"),
            InlineKeyboardButton(text="Part 2 📋", callback_data="speaking_part2"),
            InlineKeyboardButton(text="Part 3 💬", callback_data="speaking_part3"),
        ],
        [InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu")]
    ])

def subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 1 ay — 15 AZN", callback_data="pay_1month")],
        [InlineKeyboardButton(text="💳 3 ay — 40 AZN (Sərfəli!)", callback_data="pay_3months")],
        [InlineKeyboardButton(text="💳 6 ay — 70 AZN (Ən Yaxşı!)", callback_data="pay_6months")],
        [InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu")]
    ])

def next_question_keyboard(section: str, q_index: int, total: int):
    buttons = []
    if q_index < total - 1:
        buttons.append([InlineKeyboardButton(text="➡️ Növbəti Sual", callback_data=f"{section}_q{q_index+1}")])
    else:
        buttons.append([InlineKeyboardButton(text="✅ Bitir", callback_data=f"main_menu")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 İstifadəçilər", callback_data="admin_users")],
        [InlineKeyboardButton(text="✅ Ödəniş Təsdiqlə", callback_data="admin_confirm_payment")],
        [InlineKeyboardButton(text="🚫 Ban", callback_data="admin_ban")],
    ])
