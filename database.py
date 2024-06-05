import datetime

import asyncpg
import data
from datetime import datetime


async def connect_to_db():
    connection = await asyncpg.connect(
        host=data.db_host,
        port=data.db_port,
        user=data.db_username,
        password=data.db_password,
        database=data.db_database_name
    )

    return connection


async def check_user_in_db(telegram_id: str):
    conn = await connect_to_db()

    try:
        sql_query = "SELECT * FROM users WHERE telegram_id = $1"
        result = await conn.fetch(sql_query, telegram_id)
        return result
    except Exception as e:
        print(f"⛔Something went wrong... Error:\n{e}")
        return False


async def check_user_status(telegram_id: str):
    conn = await connect_to_db()

    try:
        sql_query = "SELECT * FROM users WHERE telegram_id = $1 AND user_status = 'admin';"
        result = await conn.fetch(sql_query, telegram_id)
        print(f"Result is {result}")

        return result
    except Exception as e:
        print(f"⛔Something went wrong... Error:\n{e}")
        await conn.close()
        return False


async def add_new_user(telegram_id: str, telegram_username: str, username: str):
    conn = await connect_to_db()

    try:
        sql_query = "INSERT INTO users(user_status, username, telegram_username, telegram_id, registration_date) " \
                    "VALUES('client', $1, $2, $3, $4);"
        result = await conn.fetch(
            sql_query,
            username,
            telegram_username,
            telegram_id,
            datetime.utcnow()
        )
        return result
    except Exception as e:
        await conn.close()
        print(f"Error:\n{e}")
        return False


async def fetch_requests_by_user_id(telegram_id: str):
    conn = await connect_to_db()
    sql_query = "SELECT * FROM requests WHERE user_id = (SELECT user_id FROM users WHERE telegram_id = $1);"

    try:
        result = await conn.fetch(sql_query, telegram_id)
        return result
    except Exception as e:
        print(f"⛔Something went wrong... Error:\n{e}")
        await conn.close()


async def fetch_user_id_by_telegram_id(telegram_id: str) -> int:
    conn = await connect_to_db()
    sql_query = "SELECT user_id FROM users WHERE telegram_id = $1;"

    try:
        result = await conn.fetch(sql_query, telegram_id)
        return result[0]
    finally:
        await conn.close()


async def add_new_request(req: dict, telegram_id) -> str:
    conn = await connect_to_db()
    try:
        sql_query = "INSERT INTO requests(request_status, user_id, request_timestamp, " \
                    "customer_full_name, customer_tin, customer_phone, customer_email, " \
                    "fax_address, event_type, event_name, event_timestamp, desired_event_venue, " \
                    "estimated_number_of_guests, availability_of_technical_staff, event_duration) " \
                    "VALUES ($1, (SELECT user_id FROM users WHERE telegram_id = $2), " \
                    "$3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15);"

        await conn.fetch(
            sql_query, 'new', str(telegram_id), datetime.utcnow(),
            req['provided_fullname'], req['provided_tin'], req['provided_phone'], req['provided_email'],
            req['provided_fax'], req['provided_event_type'], req['provided_event_name'],
            datetime.strptime(req['provided_timestamp'], "%H:%M %d:%m:%Y"), req['provided_event_venue'],
            int(req['provided_amount_of_guests']),
            req['provided_staff'],
            datetime.strptime(req['provided_event_duration'], "%H:%M")
        )
        return "✅ Your request successfully added!"
    except Exception as e:
        print(f"⛔Something went wrong... Error:\n{e}")
        return f"❌ Something went wrong... Please, try later.\n<code>{e}</code>"
    finally:
        await conn.close()
