
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

import text

main_menu = [
    [
        InlineKeyboardButton(text=text.event_request_txt, callback_data="request_an_event"),
        InlineKeyboardButton(text=text.my_events_txt, callback_data="show_events")
    ],

    [
        InlineKeyboardButton(text=text.contacts_txt, callback_data="show_contacts"),
        InlineKeyboardButton(text=text.about_txt, callback_data="show_about")
    ],

    [InlineKeyboardButton(text=text.my_profile_txt, callback_data="show_user_profile")],

    [InlineKeyboardButton(text=text.help_txt, callback_data="help_to_user")],

    [InlineKeyboardButton(text=text.get_doc_txt, callback_data="get_doc_template")]
]

admin_menu = [
    [InlineKeyboardButton(text=text.show_requests, callback_data="show_all_requests")],
    [InlineKeyboardButton(text=text.stat_txt, callback_data="show_current_stat")],
    [InlineKeyboardButton(text=text.my_profile_txt, callback_data="show_user_profile")],
    [InlineKeyboardButton(text=text.support_panel, callback_data="show_complaints")]
]

choose_menu = [
    [
        InlineKeyboardButton(text="✅ Yes", callback_data="yes_fax"),
        InlineKeyboardButton(text="❌ No", callback_data="no_fax")
    ]
]

choose_menu_markup = InlineKeyboardMarkup(inline_keyboard=choose_menu)

choose_event_type = [
    [
        InlineKeyboardButton(text="🖼️ Exhibition", callback_data="exhibition"),
        InlineKeyboardButton(text="📊 Conference", callback_data="conference")
    ]
]

choose_event_type_markup = InlineKeyboardMarkup(inline_keyboard=choose_event_type)

choose_staff = [
    [
        InlineKeyboardButton(text="✅ Yes", callback_data="yes_staff"),
        InlineKeyboardButton(text="❌ No, I have my own", callback_data="no_staff")
    ]
]

choose_staff_markup = InlineKeyboardMarkup(inline_keyboard=choose_staff)

main_menu_markup = InlineKeyboardMarkup(inline_keyboard=main_menu)
admin_menu_markup = InlineKeyboardMarkup(inline_keyboard=admin_menu)

exit_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)


async def create_pagination_keyboard(requests, current_page, max_per_page=5):
    try:
        total_pages = (len(requests) + max_per_page - 1) // max_per_page
        start_idx = (current_page - 1) * max_per_page
        end_idx = start_idx + max_per_page
        page_requests = requests[start_idx:end_idx]

        keyboard = []
        row = []

        if current_page > 1:
            row.append(InlineKeyboardButton(text="⬅️", callback_data="prev_page"))
        if current_page < total_pages:
            row.append(InlineKeyboardButton(text="➡️", callback_data="next_page"))

        if row:
            keyboard.append(row)

        for idx, request in enumerate(page_requests, start=start_idx + 1):
            row = [InlineKeyboardButton(text=str(idx), callback_data=f"show_request_{request['request_id']}")]
            keyboard.append(row)

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    except Exception as e:
        print(f"⛔Something went wrong... Error:\n{e}")
