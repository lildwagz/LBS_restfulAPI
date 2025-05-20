import aiomysql
import bcrypt
from aiomysql import IntegrityError, DataError
from utils.exceptions import (
    DatabaseError,
    DuplicateEntryError,
    RecordNotFoundError,
    InvalidDataError,
    TransactionError
)



class UserDAO:
    def __init__(self, db_pool):
        self.db_pool = db_pool


    async def _execute_query(self, query, params=None):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute(query, params or ())
                    return cursor
                except DataError as e:
                    raise ValueError("Invalid data format") from e
                except IntegrityError as e:
                    if "Duplicate entry" in str(e):
                        raise ValueError("Username already exists") from e
                    raise
                except Exception as e:
                    raise RuntimeError("Database operation failed") from e

    async def get_by_username(self, username):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await self._handle_db_operation(
                    cursor.execute,
                    "SELECT id, username, password, role FROM users WHERE username = %s",
                    (username,)
                )
                result = await cursor.fetchone()
                if not result:
                    raise RecordNotFoundError("User", f"username={username}")
                return result

    async def create_user(self, username, password, role='user'):
        if len(username) < 3 or len(username) > 20:
            raise InvalidDataError("username", username)

        if len(password) < 8:
            raise InvalidDataError("password", "too short")

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        async with self.db_pool.acquire() as conn:
            try:
                async with conn.cursor() as cursor:
                    await self._handle_db_operation(
                        cursor.execute,
                        """INSERT INTO users (username, password, role)
                        VALUES (%s, %s, %s)""",
                        (username, hashed, role)
                    )
                    await conn.commit()
                    return cursor.lastrowid
            except Exception as e:
                await conn.rollback()
                raise TransactionError("user creation") from e

    async def verify_password(self, username, password):
        user = await self.get_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        return None

    async def update_user(self, user_id, username, password, role):
        # Validasi sebelum update
        existing_user = await self.get_by_id(user_id)
        if not existing_user:
            raise ValueError("User not found")

        if username != existing_user['username']:
            existing = await self.get_by_username(username)
            if existing:
                raise ValueError("Username already exists")

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor = await self._execute_query(
            """UPDATE users SET
            username = %s, password = %s, role = %s
            WHERE id = %s""",
            (username, hashed, role, user_id)
        )

        async with self.db_pool.acquire() as conn:
            await conn.commit()

        return cursor.rowcount > 0

    async def delete_user(self, user_id):
        cursor = await self._execute_query(
            "DELETE FROM users WHERE id = %s",
            (user_id,)
        )

        async with self.db_pool.acquire() as conn:
            await conn.commit()

        return cursor.rowcount > 0

    async def get_by_id(self, user_id):
        cursor = await self._execute_query(
            "SELECT id, username, password, role FROM users WHERE id = %s",
            (user_id,)
        )
        return await cursor.fetchone()

    async def get_all_users(self):
        cursor = await self._execute_query(
            "SELECT id, username, role FROM users"
        )
        return await cursor.fetchall()

    async def search_users(self, keyword):
        cursor = await self._execute_query(
            "SELECT id, username, role FROM users WHERE username LIKE %s",
            (f"%{keyword}%",)
        )
        return await cursor.fetchall()

    async def _handle_db_operation(self, func, *args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except aiomysql.IntegrityError as e:
            if "Duplicate entry" in str(e):
                field = str(e).split("'")[1]
                raise DuplicateEntryError(field) from e
            raise DatabaseError("Database integrity error") from e
        except aiomysql.DataError as e:
            field = str(e).split("'")[1] if "'" in str(e) else "unknown"
            raise InvalidDataError(field, "invalid value") from e
        except aiomysql.OperationalError as e:
            raise DatabaseError("Database connection error") from e
        except Exception as e:
            raise DatabaseError("Unexpected database error") from e