import os
import time

import telebot

import config
from botcontroller import BotController
from db_controller import DBController
from parser.excell_loader import download_and_update
from updaters import start_week_updating, start_users_monitoring, start_excell_update

# токен бота
bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))

# подключение бд
DBController.start_db_control()


def main():
    while True:
        try:
            BotController.set_bot(bot)
            download_and_update()
            BotController.refresh_bot()

            # старт обновления основных данных
            start_week_updating()
            start_users_monitoring()
            start_excell_update()

            print("Бот запущен")
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
