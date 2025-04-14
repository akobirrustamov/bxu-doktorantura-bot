from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config
from data.config import DB_PORT


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=DB_PORT,
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users_telegram (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            username VARCHAR(255),
            telegram_id BIGINT NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO users_telegram (full_name, username, telegram_id) VALUES ($1, $2, $3) RETURNING *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM users_telegram"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users_telegram WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users_telegram"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE users_telegram SET username = $1 WHERE telegram_id = $2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM users_telegram WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE users_telegram", execute=True)




    async def create_table_applications(self):
        sql = """
        CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL REFERENCES users_telegram(telegram_id) ON DELETE CASCADE,
        full_name TEXT,
        phone TEXT,
        schedule_file TEXT,   -- store path like /public/{telegram_id}/schedule.docx
        diploma_file TEXT,
        passport_file TEXT,
        reference_word TEXT,
        reference_pdf TEXT,
        status INTEGER DEFAULT 0,
        is_accepted BOOLEAN DEFAULT FALSE
        );

        """
        await self.execute(sql, execute=True)

    async def create_application(self, telegram_id):
        sql = "INSERT INTO applications (telegram_id) VALUES ($1) RETURNING *"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def update_application_step(self, telegram_id, field_name, field_value, status):
        sql = f"UPDATE applications SET {field_name} = $1, status = $2 WHERE telegram_id = $3"
        return await self.execute(sql, field_value, status, telegram_id, execute=True)

    async def get_application(self, telegram_id):
        sql = "SELECT * FROM applications WHERE telegram_id = $1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def accept_application(self, telegram_id):
        sql = "UPDATE applications SET is_accepted = TRUE WHERE telegram_id = $1"
        return await self.execute(sql, telegram_id, execute=True)
    async def create_application(self, telegram_id):
        sql = "INSERT INTO applications (telegram_id) VALUES ($1) RETURNING *"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def update_application_step(self, telegram_id, field_name, field_value, status):
        sql = f"UPDATE applications SET {field_name} = $1, status = $2 WHERE telegram_id = $3"
        return await self.execute(sql, field_value, status, telegram_id, execute=True)
