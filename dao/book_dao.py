from aiomysql import IntegrityError, DataError, OperationalError, DictCursor
from utils.exceptions import (
    DatabaseError,
    RecordNotFoundError,
    DuplicateEntryError,
    InvalidDataError
)


class BookDAO:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def _execute_query(self, query, params=None, read_only=False):
        """Utility method to handle database operations"""
        async with self.db_pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cursor:
                try:
                    await cursor.execute(query, params or ())
                    if not read_only:
                        await conn.commit()
                    return cursor
                except IntegrityError as e:
                    await conn.rollback()
                    if "Duplicate entry" in str(e):
                        field = str(e).split("'")[1]
                        raise DuplicateEntryError(field)
                    raise DatabaseError("Database integrity error") from e
                except DataError as e:
                    await conn.rollback()
                    raise InvalidDataError("Invalid data format", str(e)) from e
                except OperationalError as e:
                    await conn.rollback()
                    raise DatabaseError("Database connection error") from e
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError("Database operation failed") from e

    async def get_all_books(self, page=1, per_page=10):
        """Get paginated list of books"""
        try:
            offset = (page - 1) * per_page
            cursor = await self._execute_query(
                "SELECT * FROM books LIMIT %s OFFSET %s",
                (per_page, offset),
                read_only=True
            )
            result = await cursor.fetchall()
            return [self._row_to_dict(row) for row in result]
        except DatabaseError as e:
            raise DatabaseError(f"Failed to fetch books: {str(e)}")

    async def get_book_by_id(self, book_id):
        """Get single book by ID"""
        try:
            cursor = await self._execute_query(
                "SELECT * FROM books WHERE id = %s",
                (book_id,),
                read_only=True
            )
            row = await cursor.fetchone()
            if not row:
                raise RecordNotFoundError("Book", book_id)
            return self._row_to_dict(row)
        except DatabaseError as e:
            raise DatabaseError(f"Failed to fetch book: {str(e)}")

    async def add_book(self, judul, pengarang, stok, tahun_terbit):
        """Add new book to database"""
        try:
            # Validasi dasar sebelum insert
            if len(judul) < 2 or len(judul) > 200:
                raise InvalidDataError("judul", judul, "2-200 karakter")

            if stok < 0:
                raise InvalidDataError("stok", stok, "Harus >= 0")

            cursor = await self._execute_query(
                """INSERT INTO books 
                (judul, pengarang, stok, tahun_terbit)
                VALUES (%s, %s, %s, %s)""",
                (judul, pengarang, stok, tahun_terbit)
            )
            return cursor.lastrowid
        except DatabaseError as e:
            raise DatabaseError(f"Failed to add book: {str(e)}")

    async def update_book(self, book_id, **kwargs):
        """Update book with partial data"""
        try:
            # Validasi input
            valid_fields = {'judul', 'pengarang', 'stok', 'tahun_terbit'}
            update_data = {k: v for k, v in kwargs.items() if k in valid_fields}

            if not update_data:
                raise InvalidDataError("update_data", None, "No valid fields provided")

            # Build dynamic update query
            set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
            values = list(update_data.values()) + [book_id]

            cursor = await self._execute_query(
                f"""UPDATE books SET 
                {set_clause}
                WHERE id = %s""",
                tuple(values)
            )

            if cursor.rowcount == 0:
                raise RecordNotFoundError("Book", book_id)

            return True
        except DatabaseError as e:
            raise DatabaseError(f"Failed to update book: {str(e)}")

    async def delete_book(self, book_id):
        """Delete book from database"""
        try:
            cursor = await self._execute_query(
                "DELETE FROM books WHERE id = %s",
                (book_id,)
            )

            if cursor.rowcount == 0:
                raise RecordNotFoundError("Book", book_id)

            return True
        except DatabaseError as e:
            raise DatabaseError(f"Failed to delete book: {str(e)}")

    async def search_books(self, keyword, search_fields=['judul', 'pengarang']):
        """Search books with keyword in specified fields"""
        try:
            if not keyword or len(keyword.strip()) < 2:
                raise InvalidDataError("keyword", keyword, "Minimal 2 karakter")

            # Build dynamic search query
            search_conditions = " OR ".join(
                [f"{field} LIKE %s" for field in search_fields]
            )
            params = tuple([f"%{keyword}%" for _ in search_fields])

            cursor = await self._execute_query(
                f"""SELECT * FROM books 
                WHERE {search_conditions}""",
                params,
                read_only=True
            )
            result = await cursor.fetchall()
            return [self._row_to_dict(row) for row in result]
        except DatabaseError as e:
            raise DatabaseError(f"Failed to search books: {str(e)}")

    async def adjust_stock(self, book_id, quantity):
        """Adjust book stock atomically"""
        try:
            if not isinstance(quantity, int):
                raise InvalidDataError("quantity", quantity, "Harus bilangan bulat")

            cursor = await self._execute_query(
                "UPDATE books SET stok = stok + %s WHERE id = %s",
                (quantity, book_id)
            )

            if cursor.rowcount == 0:
                raise RecordNotFoundError("Book", book_id)

            return True
        except DatabaseError as e:
            raise DatabaseError(f"Failed to adjust stock: {str(e)}")


    def _row_to_dict(self, row):
        """Convert database row to dictionary menggunakan nama kolom"""
        return {
            "id": row['id'],
            "judul": row['judul'],
            "pengarang": row['pengarang'],
            "stok": row['stok'],
            "tahun_terbit": row['tahun_terbit']
        }