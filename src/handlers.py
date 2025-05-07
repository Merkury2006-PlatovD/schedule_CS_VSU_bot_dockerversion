import os

import telebot
from telebot import TeleBot

from db_controller import DBController
from errors.errors import ScheduleParserFindError
from parser.excell_converter import ScheduleParser
from keyboard_generators import get_subgroup_keyboard, get_group_keyboard, get_course_keyboard, get_persistent_keyboard, \
    get_mistake_report_keyboard
import config


def register_handlers(bot: TeleBot, sch_parser: ScheduleParser):
    def set_bot_commands_menu():
        bot.set_my_commands([
            telebot.types.BotCommand("start", "Начать работу с ботом"),
            telebot.types.BotCommand("help", "Получить помощь"),
            telebot.types.BotCommand("info", "Узнать информацию о себе"),
            telebot.types.BotCommand("updateinfo", "Поменять информацию о себе"),
            telebot.types.BotCommand("mistake", "Сообщить об ошибке в расписании"),
            telebot.types.BotCommand("znam", "Посмотреть расписание на знаменатель"),
            telebot.types.BotCommand("chis", "Посмотреть расписание на числитель")
        ])

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        """
        Слушает команду "/start" и выполняет действия в зависимости от результата user_exists(user_id). Начинает работу всего бота.

        Args:
            message: экземпляр telebot.types.Message.
        """
        set_bot_commands_menu()
        user_id = message.from_user.id
        bot.send_message(user_id,
                         f"Неделя сейчас: {'числитель' if DBController.get_current_week_type() == 0 else 'знаменатель'}")
        if not DBController.user_exists(user_id):
            DBController.add_user(user_id)
            bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())
        else:
            bot.send_message(user_id, "Ты уже зарегистрирован!")
            bot.send_message(user_id, "На какой день тебе нужно расписание?", reply_markup=get_persistent_keyboard())

    @bot.message_handler(commands=['updateinfo'])
    def handle_profile_update(message):
        """
        Слушает команду "/updateinfo" и регистрирует/изменяет данные о пользователе в БД.

        Args:
            message: экземпляр telebot.types.Message.
        """
        user_id = message.from_user.id
        if not DBController.user_exists(user_id):
            DBController.add_user(user_id)
        bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())

    @bot.message_handler(commands=['help'])
    def handle_help(message):
        """
        Слушает команду "/help" и выводит пользователю справочную информацию.

        Args:
            message: экземпляр telebot.types.Message.
        """
        bot.send_message(message.from_user.id, "Привет! Я помогу тебе с расписанием: \n"
                                               "•  Напиши команду /start, чтобы я узнал информацию о тебе и твоем расписании\n"
                                               "•  Напиши команду /updateinfo, чтобы изменить информацию о тебе\n"
                                               "•  Напиши команду /info, чтобы узнать краткую информацию о тебе\n"
                                               "•  Напиши команду /mistake, чтобы отправить отчет о неправильном расписании\n"
                                               "•  Напиши команду /znam, чтобы посмотреть расписание на знаменатель\n"
                                               "•  Напиши команду /chis, чтобы посмотреть расписание на числитель")

    @bot.message_handler(commands=['info'])
    def handle_info(message):
        user_id = message.from_user.id
        course, group, subgroup = DBController.get_user_data(user_id)
        bot.send_message(message.from_user.id, "Информация о тебе: \n"
                                               f"Твой курс: {course}\n"
                                               f"Твоя группа: {group}\n"
                                               f"Твоя подгруппа: {subgroup}")

    @bot.message_handler(commands=['mistake'])
    def handle_mistake_report(message):
        bot.send_message(message.from_user.id,
                         "Подтвердите факт ошибки в расписании. Если ошибок нет, просим вас не создавать нам лишней работы!",
                         reply_markup=get_mistake_report_keyboard())

    # специальные хэндлеры для использования администратором
    @bot.message_handler(commands=['getDB'])
    def handle_database_request(message):
        if str(message.from_user.id) in [os.getenv("ADMIN_TG_ID1"), os.getenv("ADMIN_TG_ID2")]:
            try:
                with open(config.db_path, "rb") as db_file:
                    bot.send_document(message.from_user.id, db_file, caption="Вот твоя база данных 📂")
            except FileNotFoundError:
                bot.reply_to(message, "Файл базы данных не найден! ❌")

    @bot.message_handler(commands=['getUsersPerDay'])
    def handle_users_per_day_request(message):
        bot.send_message(message.from_user.id, f"Запросов за текущий день {DBController.get_users_per_day()}")

    @bot.message_handler(commands=['sendMessage'])
    def handle_send_message(message):
        if str(message.from_user.id) in [os.getenv("ADMIN_TG_ID1"), os.getenv("ADMIN_TG_ID2")]:
            args = message.text.split(maxsplit=2)
            if len(args) < 3:
                bot.reply_to(message, "⚠ Использование: /sendMessage [id пользователя] \"сообщение\"")
                return

            user_id = int(args[1])
            user_message = args[2]

            bot.send_message(user_id, user_message)
            bot.reply_to(message, f"✅ Сообщение отправлено пользователю {user_id}")

    @bot.message_handler(commands=['chis', 'znam'])
    def handle_chis_znam_shedule(message):
        user_id = message.from_user.id
        print(f"Запрос от {user_id}: {message.from_user.username}")
        DBController.increment_users_per_day_cnt()

        if not DBController.user_exists(user_id):
            DBController.add_user(user_id)
            bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())
        else:
            try:
                out_data_formated = f"Твое расписание на {"числитель" if message.text == '/chis' else 'знаменатель'}:\n\n"
                days_map = {"📅 Понедельник": 0, "📅 Вторник": 1, "📅 Среда": 2, "📅 Четверг": 3, "📅 Пятница": 4,
                            "📅 Суббота": 5}
                course, group, subgroup = DBController.get_user_data(user_id)

                for key, val in days_map.items():
                    schedule = sch_parser.get_lessons_on_day(sch_parser.find_required_col(course, group, subgroup),
                                                             val, 0 if message.text == '/chis' else 1)
                    out_data_formated += f"📅 *Расписание занятий на {key.split(' ')[-1]}:*\n\n"
                    for key_day, val_day in schedule.items():
                        if val_day is None or val_day.strip() == "":
                            val_day = "— Нет пары —"
                        out_data_formated += f"🕒 *{key_day}*\n📖 {val_day}\n\n"

                bot.send_message(user_id, out_data_formated, parse_mode="Markdown")
            except (ScheduleParserFindError, TypeError, ValueError) as e:
                handle_error(user_id, e,
                             "Возможно ошибка связана с обновлением на сервере. В таком случае просим Вас просто заново ввести данные. Мы сделам все возможное, чтобы это не повторилось.\n\n❌ Мы не смогли найти учебную группу с вашими данными.\n🔍 Убедитесь, что вы правильно ввели все данные.\n💡 Попробуйте ввести их еще раз.")
                handle_profile_update(message)

    @bot.message_handler(
        func=lambda message: message.text not in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница",
                                                  "📅 Суббота"])
    def handle_error_message(message):
        user_id = message.from_user.id
        bot.send_message(user_id, "Привет! Напиши /start для запуска бота или /help для более подробной информации")

    @bot.message_handler(
        func=lambda message: message.text in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница",
                                              "📅 Суббота"])
    def handle_schedule_request(message):
        days_map = {"📅 Понедельник": 0, "📅 Вторник": 1, "📅 Среда": 2, "📅 Четверг": 3, "📅 Пятница": 4, "📅 Суббота": 5}
        user_id = message.from_user.id
        print(f"Запрос от {user_id}: {message.from_user.username}")
        DBController.increment_users_per_day_cnt()
        day = days_map[message.text]
        try:
            week_type = DBController.get_current_week_type()
            course, group, subgroup = DBController.get_user_data(user_id)
            schedule = sch_parser.get_lessons_on_day(sch_parser.find_required_col(course, group, subgroup),
                                                     day, week_type)
            out_data_formated = f"📅 *Расписание занятий на {message.text.split(' ')[-1]}/{'числ' if week_type == 0 else 'знам'}:*\n\n"

            for key, val in schedule.items():
                if val is None or val.strip() == "":
                    val = "— Нет пары —"

                out_data_formated += f"🕒 *{key}*\n📖 {val}\n\n"

            bot.send_message(user_id, out_data_formated, parse_mode="Markdown")
        except (ScheduleParserFindError, TypeError, ValueError) as e:
            handle_error(user_id, e,
                         "Возможно ошибка связана с обновлением на сервере. В таком случае просим Вас просто заново ввести данные. Мы сделам все возможное, чтобы это не повторилось.\n\n❌ Мы не смогли найти учебную группу с вашими данными.\n🔍 Убедитесь, что вы правильно ввели все данные.\n💡 Попробуйте ввести их еще раз.")
            handle_profile_update(message)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
    def handle_course(call):
        user_id = call.from_user.id
        course = int(call.data.split("_")[1])

        DBController.update_user(user_id, "course", course)
        keyboard = get_group_keyboard()
        bot.send_message(user_id, "Теперь выбери свою группу:", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
    def handle_group(call):
        user_id = call.from_user.id
        group = int(call.data.split("_")[1])

        DBController.update_user(user_id, "group_num", group)
        keyboard = get_subgroup_keyboard()
        bot.send_message(user_id, "Теперь выбери свою подгруппу:", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("subgroup_"))
    def handle_subgroup(call):
        user_id = call.from_user.id
        subgroup = int(call.data.split("_")[-1])

        DBController.update_user(user_id, "subgroup", subgroup)
        bot.send_message(user_id, "Отлично! Данные сохранены.")
        bot.send_message(user_id, "На какой день тебе нужно расписание?", reply_markup=get_persistent_keyboard())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("mistake"))
    def handle_report_send(call):
        if call.data.split("_")[-1] == "1":
            course, group, subgroup = DBController.get_user_data(call.from_user.id)
            bot.send_message(5109041126,
                             f"Ошибка в расписании у курс: {course}, группа: {group}, подгруппа: {subgroup} от {call.from_user.username} c id {call.from_user.id}")
            print(
                f"Ошибка в расписании у курс: {course}, группа: {group}, подгруппа: {subgroup} от {call.from_user.username} c id {call.from_user.id}")
            bot.send_message(call.from_user.id,
                             "Спасибо! Ваша жалоба успешно отправлена, и мои разработчики рассмотрят её в ближайшее время.")
        else:
            bot.send_message(call.from_user.id, "Рады, что все работает хорошо)")

    def handle_error(user_id, error_log, error_text=""):
        error_text = f"⚠️Ошибка⚠️\n\n{error_text}\n\n{error_log}"
        bot.send_message(user_id, error_text)
