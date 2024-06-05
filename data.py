from aiogram import Bot
from aiogram.enums import ParseMode

TELEGRAM_BOT_TOKEN = "6886583202:AAGZC82mhveMql-RoQK0kFCPuIN7Uy9SiuQ"

db_host = "127.0.0.1"
db_username = "postgres"
db_password = "r2kVxsger"
db_port = "5432"
db_database_name = "requestModuleDB"

bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        parse_mode=ParseMode.HTML
    )
