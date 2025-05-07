import sys
from os import environ

import psycopg2

from errors.errors import ConnectionParamsError


class DBController:
    cursor = None
    conn = None

    @classmethod
    def start_db_control(cls):
        try:
            # подключение к БД
            POSTGRES_DB = environ.get("POSTGRES_DB")
            POSTGRES_USER = environ.get("POSTGRES_USER")
            POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")
            POSTGRES_HOST = environ.get("POSTGRES_HOST")

            if not all([POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD]):
                raise ConnectionParamsError()

            cls.conn = psycopg2.connect(dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD,
                                        host=POSTGRES_HOST)
            cls.cursor = cls.conn.cursor()
            # cls.extra_functionality()
        except ConnectionParamsError as e:
            print(e.message, file=sys.stderr)

    # @classmethod
    # def start_db_control(cls, db_path):
    #     db_dir = os.path.dirname(db_path)
    #     os.makedirs(db_dir, exist_ok=True)
    #     # подключение к БД
    #     cls.conn = sqlite3.connect(db_path, check_same_thread=False)
    #     cls.cursor = cls.conn.cursor()
    #
    #     cls.init_tables_if_not_exists()
    #     cls.extra_functionality()

    @classmethod
    def init_tables_if_not_exists(cls):
        # создание таблицы в БД при первом включении
        cls.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {environ.get("USERS_TABLE")} (
            user_id INTEGER PRIMARY KEY,
            course INTEGER,
            group_num INTEGER,
            subgroup INTEGER
        );
        """)

        # Создаем таблицу, где ключ - это название переменной
        cls.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {environ.get("CONFIG_TABLE")} (
                key TEXT PRIMARY KEY,  
                value TEXT
            );
        """)

        cls.cursor.execute(f"""
               INSERT OR IGNORE INTO {environ.get("CONFIG_TABLE")} (key, value) VALUES (%s, %s);
           """, ("week_type", "0"))
        cls.cursor.execute(f"""
               INSERT OR IGNORE INTO {environ.get("CONFIG_TABLE")} (key, value) VALUES (%s, %s);
           """, ("users_per_day", "0"))
        cls.conn.commit()

    @classmethod
    def end_db_control(cls):
        """Закрывает соединение с БД."""
        if cls.conn:
            cls.conn.close()
            cls.conn = None
            cls.cursor = None

    @classmethod
    def user_exists(cls, user_id: int) -> bool:
        """
        Проверяет существование пользователя в БД.

        Args:
            user_id: tg id пользователя.

        Returns:
            bool: факт существования данного пользователя в БД.
        """
        cls.cursor.execute(f"SELECT EXISTS(SELECT 1 FROM {environ.get("USERS_TABLE")} WHERE user_id=%s)", (user_id,))
        return cls.cursor.fetchone()[0]

    @classmethod
    def add_user(cls, user_id):
        """
        Добавляет в БД запись с pk = user_id.

        Args:
            user_id: tg id пользователя.
        """
        cls.cursor.execute(f"INSERT INTO {environ.get("USERS_TABLE")} (user_id) VALUES (%s)", (user_id,))
        cls.conn.commit()

    @classmethod
    def update_user(cls, user_id, column, value):
        """
        Обновляет значение определенного поля зарегестрированного пользователя

        Args:
            user_id: tg id пользователя.
            column: поле, которое нужно изменить.
            value: новое значение изменяемого поля.
        """
        cls.cursor.execute(f"UPDATE {environ.get("USERS_TABLE")} SET {column} = %s WHERE user_id = %s", (value, user_id))
        cls.conn.commit()

    @classmethod
    def get_user_data(cls, user_id):
        """
        Получает данные пользователя из БД.

        Args:
            user_id: tg id пользователя.

        Returns:
            tuple: номер курса, группы и подгруппы пользователя.
        """
        cls.cursor.execute(f"SELECT course, group_num, subgroup FROM {environ.get("USERS_TABLE")} WHERE user_id = %s",
                           (user_id,))
        return cls.cursor.fetchone()

    @classmethod
    def get_current_week_type(cls):
        cls.cursor.execute(f"SELECT value FROM {environ.get("CONFIG_TABLE")} WHERE key = %s", ("week_type",))
        return int(cls.cursor.fetchone()[0])

    @classmethod
    def update_current_week_type(cls, new_week_type):
        cls.cursor.execute("UPDATE config SET value = %s WHERE key = %s", (str(new_week_type), "week_type"))
        cls.conn.commit()

    @classmethod
    def get_users_per_day(cls):
        cls.cursor.execute(f"SELECT value FROM {environ.get("CONFIG_TABLE")} WHERE key = %s", ("users_per_day",))
        return int(cls.cursor.fetchone()[0])

    @classmethod
    def increment_users_per_day_cnt(cls):
        cls.cursor.execute(f"UPDATE {environ.get("CONFIG_TABLE")} SET value = %s WHERE key = %s",
                           (cls.get_users_per_day() + 1, "users_per_day"))
        cls.conn.commit()

    @classmethod
    def set_users_per_day(cls, new_value):
        cls.cursor.execute(f"UPDATE {environ.get("CONFIG_TABLE")} SET value = %s WHERE key = %s",
                           (new_value, "users_per_day"))
        cls.conn.commit()

    @classmethod
    def extra_functionality(cls):
        pass
