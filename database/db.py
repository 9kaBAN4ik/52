import sqlite3
import logging
from typing import List, Tuple

class Database:
    def __init__(self, db_name: str = "bot.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        logging.info(f"Подключение к базе данных {db_name} установлено")
        self._create_tables()

    def add_user_if_not_exists(self, user_id: int, username: str = None, full_name: str = None):
        try:
            self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not self.cursor.fetchone():
                self.cursor.execute(
                    "INSERT INTO users (id, username, full_name) VALUES (?, ?, ?)",
                    (user_id, username, full_name)
                )
                self.conn.commit()
                logging.info(f"Добавлен новый пользователь: {user_id}")
        except Exception as e:
            logging.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
            raise

    def _create_tables(self):
        try:
            # Таблица для серверов/каналов
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    moderation_group_id TEXT NOT NULL
                )
            """)

            # Таблица для объявлений
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS advertisements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    server_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    photo_id TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES servers (id)
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    role TEXT DEFAULT 'user'
                )
            """)
            self.conn.commit()
            logging.info("Таблицы базы данных успешно созданы")
        except Exception as e:
            logging.error(f"Ошибка при создании таблиц: {e}")
            raise

    def add_server(self, name: str, channel_id: str, moderation_group_id: str) -> int:
        try:
            self.cursor.execute(
                "INSERT INTO servers (name, channel_id, moderation_group_id) VALUES (?, ?, ?)",
                (name, channel_id, moderation_group_id)
            )
            self.conn.commit()
            logging.info(f"Добавлен новый сервер: {name}")
            return self.cursor.lastrowid
        except Exception as e:
            logging.error(f"Ошибка при добавлении сервера: {e}")
            raise

    def get_servers(self) -> List[Tuple]:
        try:
            self.cursor.execute("SELECT id, name FROM servers")
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при получении списка серверов: {e}")
            raise

    def get_server(self, server_id: int) -> Tuple:
        try:
            self.cursor.execute("SELECT * FROM servers WHERE id = ?", (server_id,))
            return self.cursor.fetchone()
        except Exception as e:
            logging.error(f"Ошибка при получении сервера {server_id}: {e}")
            raise

    def add_advertisement(self, user_id: int, server_id: int, text: str, photo_id: str = None) -> int:
        try:
            self.cursor.execute(
                "INSERT INTO advertisements (user_id, server_id, text, photo_id) VALUES (?, ?, ?, ?)",
                (user_id, server_id, text, photo_id)
            )
            self.conn.commit()
            logging.info(f"Добавлено новое объявление от пользователя {user_id}")
            return self.cursor.lastrowid
        except Exception as e:
            logging.error(f"Ошибка при добавлении объявления: {e}")
            raise

    def update_advertisement_status(self, ad_id: int, status: str):
        try:
            self.cursor.execute(
                "UPDATE advertisements SET status = ? WHERE id = ?",
                (status, ad_id)
            )
            self.conn.commit()
            logging.info(f"Обновлен статус объявления {ad_id} на {status}")
        except Exception as e:
            logging.error(f"Ошибка при обновлении статуса объявления {ad_id}: {e}")
            raise

    def get_advertisement(self, ad_id: int) -> Tuple:
        try:
            self.cursor.execute("SELECT * FROM advertisements WHERE id = ?", (ad_id,))
            return self.cursor.fetchone()
        except Exception as e:
            logging.error(f"Ошибка при получении объявления {ad_id}: {e}")
            raise

    @staticmethod
    def is_admin(user_id: int) -> bool:
        db = Database()
        role = db.get_user_role(user_id)
        db.close()
        return role == "admin"

    def get_user_role(self, user_id: int):
        self.cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "user"


    def close(self):
        try:
            self.conn.close()
            logging.info("Соединение с базой данных закрыто")
        except Exception as e:
            logging.error(f"Ошибка при закрытии соединения с базой данных: {e}")
            raise