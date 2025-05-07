import os

users_per_week = {}
volume_path = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "/src/database")
db_path = os.path.join(volume_path, "bot_data.sql")  # путь к volume
