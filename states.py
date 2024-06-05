
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup

router = Router()


class GetCredentials(StatesGroup):
    get_email_address_state = State()
    get_fullname_state = State()


class ShowRequestsState(StatesGroup):
    showing_requests = State()


class GetRequest(StatesGroup):
    get_customer_fullname = State()
    get_customer_tin = State()
    get_customer_phone = State()
    get_customer_email = State()
    choosing_fax = State()
    get_customer_fax = State()  # User can pass this point
    get_event_type = State()
    get_event_name = State()
    get_event_timestamp = State()
    get_desired_venue = State()
    get_estimated_amount_of_guests = State()
    get_availability_of_tech_staff = State()  # Reply keyboard with 'yes' and 'no'
    get_event_duration = State()  # For example: hh:mm:ss
