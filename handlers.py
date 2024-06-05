from aiogram import Router, types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import keyboards
import text
import database
from states import GetCredentials, GetRequest, ShowRequestsState

router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    telegram_id = str(msg.from_user.id)
    telegram_username = msg.from_user.username
    username = msg.from_user.full_name

    if not await database.check_user_in_db(telegram_id):
        res = await database.add_new_user(
            telegram_id,
            telegram_username,
            username
        )
        if res:
            await msg.answer("✅ You've been registered successfully!")
        else:
            await msg.answer("❌ Sorry, the database currently is unreachable. Try it later...")
    else:
        request = await database.check_user_status(telegram_id)

        if request:
            await msg.answer(
                text.admin_greeting.format(username=msg.from_user.full_name),
                reply_markup=keyboards.admin_menu_markup
            )
        else:
            await msg.answer(text.greeting.format(
                username=msg.from_user.full_name
            ), reply_markup=keyboards.main_menu_markup)


@router.message(Command("set_credentials"))
async def get_credentials(msg: Message, state: FSMContext):
    await msg.answer(
        text="Please, type in your email address"
    )
    await state.set_state(GetCredentials.get_email_address_state)


@router.message(GetCredentials.get_email_address_state)
async def get_email(msg: Message, state: FSMContext):
    await state.update_data(provided_email=msg.text)
    await msg.answer(text=f"Thank you, now your fullname")
    await state.set_state(GetCredentials.get_fullname_state)


@router.message(GetCredentials.get_fullname_state)
async def get_fullname(msg: Message, state: FSMContext):
    await state.update_data(provided_fullname=msg.text)
    user_data = await state.get_data()
    await msg.answer(text=f"Alright, I get it:\nEMAIL: {user_data['provided_email']}"
                          f"\nFULLNAME: {user_data['provided_fullname']}")
    await state.clear()


@router.message(Command("menu"))
@router.message(F.text == "menu")
@router.message(F.text == "home")
async def main_menu(msg: Message):
    await msg.answer(text.main_menu, reply_markup=keyboards.main_menu_markup)


@router.message(lambda message: message.text in ['help', 'HELP'])
@router.message(Command('help'))
async def get_help_banner(msg: Message):
    await msg.answer(text=text.help_banner_txt)


@router.callback_query(lambda query: query.data == 'request_an_event')
async def process_client_request(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Let's start filling in the form step by step. "
                                        "First of all, provide with your full name if you're an individual, "
                                        "or your full company name if you're legal entity")
    await state.set_state(GetRequest.get_customer_fullname)


@router.message(GetRequest.get_customer_fullname)
async def process_client_fullname(msg: Message, state: FSMContext):
    await state.update_data(provided_fullname=msg.text.title())
    await msg.answer(text="Alright, next you TIN code")
    await state.set_state(GetRequest.get_customer_tin)


@router.message(GetRequest.get_customer_tin)
async def process_client_tin(msg: Message, state: FSMContext):
    await state.update_data(provided_tin=msg.text.strip())
    await msg.answer(text="Alright, next step is your phone")
    await state.set_state(GetRequest.get_customer_phone)


@router.message(GetRequest.get_customer_phone)
async def process_client_phone(msg: Message, state: FSMContext):
    await state.update_data(provided_phone=msg.text.strip())
    await msg.answer(text="Alright, next step is your email address")
    await state.set_state(GetRequest.get_customer_email)


@router.message(GetRequest.get_customer_email)
async def process_client_email(msg: Message, state: FSMContext):
    await state.update_data(provided_email=msg.text.strip())
    await msg.answer(
        text="Alright, next step is your fax. It's unnecessary, but would you like to provide us your fax address?",
        reply_markup=keyboards.choose_menu_markup
    )
    await state.set_state(GetRequest.choosing_fax)


@router.callback_query(GetRequest.choosing_fax, lambda c: c.data in ["yes_fax", "no_fax"])
async def process_fax_choice(callback: CallbackQuery, state: FSMContext):
    fax_choice = callback.data
    if fax_choice == "yes_fax":
        await callback.message.answer("Ok, just type in your fax address below")
        await state.set_state(GetRequest.get_customer_fax)
    elif fax_choice == "no_fax":
        await callback.answer()  # Подтверждаем получение callback
        await state.update_data(provided_fax="")
        await callback.message.answer(
            text="Well, as you wish, next step is event type. Just choose right one",
            reply_markup=keyboards.choose_event_type_markup
        )
        await state.set_state(GetRequest.get_event_type)
    await callback.answer()  # Подтверждаем получение callback


@router.message(GetRequest.get_customer_fax)
async def process_client_fax(msg: Message, state: FSMContext):
    await state.update_data(provided_fax=msg.text.strip())
    await msg.answer(
        text="Ok, I've got your fax address. Next step is event type. Just choose right one",
        reply_markup=keyboards.choose_event_type_markup
    )
    await state.set_state(GetRequest.get_event_type)


@router.callback_query(lambda query: query.data in ['exhibition', 'conference'])
async def process_event_type(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(provided_event_type=callback_query.data)
    await callback_query.message.answer(
        text="Ok, next step is event name. Just type in it below"
    )
    await state.set_state(GetRequest.get_event_name)


@router.message(GetRequest.get_event_name)
async def process_event_name(msg: Message, state: FSMContext):
    await state.update_data(provided_event_name=msg.text.strip())
    await msg.answer(
        text="Ok, next step is event timestamp. Just type in right time in this format - <code>hh:mm dd:mm:yyyy</code>"
    )
    await state.set_state(GetRequest.get_event_timestamp)


@router.message(GetRequest.get_event_timestamp)
async def process_event_timestamp(msg: Message, state: FSMContext):
    await state.update_data(provided_timestamp=msg.text.strip())
    db = await state.get_data()
    article = 'an' if db['provided_event_type'] == 'exhibition' else 'a'
    await msg.answer(
        text=f"Alright, next step is desired venue. "
             f"Just type in desired venue to hold <code>{article} {db['provided_event_type']}</code>"
    )
    await state.set_state(GetRequest.get_desired_venue)


@router.message(GetRequest.get_desired_venue)
async def process_event_venue(msg: Message, state: FSMContext):
    await state.update_data(provided_event_venue=msg.text.strip())
    await msg.answer(
        text="I've got it. Also we need to know the estimated amount of guests invited. "
             "Just type in estimated amount below"
    )
    await state.set_state(GetRequest.get_estimated_amount_of_guests)


@router.message(GetRequest.get_estimated_amount_of_guests)
async def process_estimated_amount_of_guests(msg: Message, state: FSMContext):
    await state.update_data(provided_amount_of_guests=msg.text.strip())
    await msg.answer(
        text="🕐 And how long will the event last? Just type in the estimated time - <code>hh:mm</code>"
    )
    await state.set_state(GetRequest.get_event_duration)


@router.message(GetRequest.get_event_duration)
async def process_event_duration(msg: Message, state: FSMContext):
    await state.update_data(provided_event_duration=msg.text.strip())
    await msg.answer(
        text="Last question - do you need technical staff?",
        reply_markup=keyboards.choose_staff_markup
    )


@router.callback_query(lambda query: query.data in ['yes_staff', 'no_staff'])
async def process_tech_staff(callback_query: CallbackQuery, state: FSMContext):
    ans: bool = True if callback_query.data == 'yes_staff' else False
    await state.update_data(provided_staff=ans)
    db = await state.get_data()
    await callback_query.message.answer(
        text=text.result_banner.format(
            username=callback_query.from_user.full_name,
            provided_fullname=db['provided_fullname'],
            provided_tin=db['provided_tin'],
            provided_phone=db['provided_phone'],
            provided_email=db['provided_email'],
            provided_fax=db['provided_fax'],
            provided_event_type=db['provided_event_type'],
            provided_event_name=db['provided_event_name'],
            provided_timestamp=db['provided_timestamp'],
            provided_event_venue=db['provided_event_venue'],
            provided_amount_of_guests=db['provided_amount_of_guests'],
            provided_event_duration=db['provided_event_duration'],
            provided_staff=db['provided_staff']
        )
    )
    res = await database.add_new_request(db, callback_query.from_user.id)
    await callback_query.answer(res)
    await state.clear()


@router.callback_query(lambda query: query.data == 'show_events')
async def process_show_events(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = str(callback_query.from_user.id)
    requests = await database.fetch_requests_by_user_id(telegram_id)

    try:
        if not requests:
            await callback_query.message.answer(
                text=text.no_requests.format(username=callback_query.from_user.full_name)
            )
            await state.clear()
        else:
            await state.set_state(ShowRequestsState.showing_requests)
            await state.update_data(requests=requests, current_page=1)
            keyboard = await keyboards.create_pagination_keyboard(requests, 1)

            message_text = "📃 Your requests: \n\n"
            for idx, request in enumerate(requests, start=1):
                message_text += f"[{idx}] Request type: <code>{request['event_type']}</code>\n"
                message_text += f"   Event name: <code>{request['event_name']}</code>\n"
                message_text += f"   Request status: <code>{request['request_status']}</code>\n\n"

            await callback_query.message.answer(
                text=message_text,
                reply_markup=keyboard
            )
    except Exception as e:
        await callback_query.message.answer(text=f"⛔Something went wrong... Error:\n{e}")


@router.callback_query(lambda c: c.data in ['prev_page', 'next_page'], ShowRequestsState.showing_requests)
async def process_pagination(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    requests = data['requests']
    current_page = data['current_page']
    max_per_page = 5
    print(f"Current page: {current_page}, Requests: {requests}")

    if callback_query.data == 'prev_page':
        current_page -= 1
    else:
        current_page += 1

    keyboard = await keyboards.create_pagination_keyboard(requests, current_page, max_per_page)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    await state.update_data(current_page=current_page)


@router.callback_query(lambda c: c.data.startswith("show_request_"), ShowRequestsState.showing_requests)
async def show_request_details(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    requests = data['requests']
    request_id = int(callback_query.data.split('_')[-1])
    request = next((r for r in requests if r['request_id'] == request_id), None)

    if request:
        message = f"🔎 Detailed information about request №<code>{request_id}</code>:\n\n"
        message += text.detailed_info_banner.format(
            event_type=request['event_type'],
            provided_event_name=request['event_name'],
            provided_status=request['request_status'],
            provided_timestamp=request['request_timestamp'],
            provided_name=request['customer_full_name'],
            provided_tin=request['customer_tin'],
            provided_phone=request['customer_phone'],
            provided_email=request['customer_email'],
            provided_fax=request['fax_address'],
            event_timestamp=request['event_timestamp'],
            event_venue=request['desired_event_venue'],
            provided_staff=request['availability_of_technical_staff'],
            event_duration=request['event_duration'],
            amount_guests=request['estimated_number_of_guests']
        )

        await callback_query.message.answer(
            text=message,
            disable_web_page_preview=True
        )
    else:
        await callback_query.message.answer(f"❌ Request №<code>{request_id}</code> not found...")


@router.callback_query(lambda query: query.data == 'get_doc_template')
async def process_send_doc(callback_query: CallbackQuery):
    await callback_query.message.answer("📝 You can use this sample to fill out the application:")
    await callback_query.message.answer_document(
        document='./template.odt',
        caption='📝 Just Sample'
    )


@router.message(F.document)
async def process_received_doc(msg: Message):
    doc = msg.document

    file_id = doc.file_id
    file_name = doc.file_name
    file_size = doc.file_size

    if doc.mime_type in ('application/vnd.oasis.opendocument.text', 'application/msword'):
        await msg.reply(
            text=f"FILE ID: <code>{file_id}</code>\n"
                 f"FILE NAME: <code>{file_name}</code>\n"
                 f"FILE SIZE: <code>{file_size}</code>"
        )
        await msg.answer(text="✅ Processing the document... wait ⌛")
    else:
        await msg.answer(
            text=f"❌ Files of this format are not allowed!"
        )


@router.callback_query(lambda query: query.data == 'show_contacts')
async def process_show_contacts(callback_query: CallbackQuery):
    await callback_query.message.answer(text=text.contacts_banner_txt)


@router.callback_query(lambda query: query.data == 'show_about')
async def process_show_about(callback_query: CallbackQuery):
    await callback_query.message.answer('About page will be added soon...')


@router.callback_query(lambda query: query.data == 'main_menu')
async def process_main_menu(callback_query: CallbackQuery):
    await callback_query.message.answer(text.main_menu, reply_markup=keyboards.main_menu_markup)


@router.callback_query(lambda query: query.data == 'show_user_profile')
async def process_show_user_profile(callback_query: CallbackQuery):
    await callback_query.message.answer("Your profile will be added soon...")


@router.callback_query(lambda query: query.data == 'help_to_user')
async def process_help_to_user(callback_query: CallbackQuery):
    await callback_query.message.answer("We can't help you right now...")


@router.callback_query(lambda query: query.data == 'show_all_requests')
async def process_show_all_requests(callback_query: CallbackQuery):
    await callback_query.message.answer("Will be soon...")
    # TODO: have to set a request list to admins


@router.callback_query(lambda query: query.data == 'show_current_stat')
async def process_show_current_stat(callback_query: CallbackQuery):
    await callback_query.message.answer("Stat function will be available soon...")
    # TODO: have to set statistics to admins


@router.callback_query(lambda query: query.data == 'show_complaints')
async def process_show_complaints(callback_query: CallbackQuery):
    await callback_query.message.answer("Complaints will be available soon...")
    # TODO: need to create an opportunity to show complaints to admins
