import aiomysql
from datetime import date
from utils.exceptions import (
    DatabaseError,
    RecordNotFoundError,
    InvalidDataError,
    OperationNotAllowedError
)


class PeminjamanDAO:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def _execute_query(self, query, params=None, read_only=False):
        """Utility method untuk handle operasi database"""
        async with self.db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute(query, params or ())
                    if not read_only:
                        await conn.commit()
                    return cursor
                except aiomysql.IntegrityError as e:
                    await conn.rollback()
                    if "foreign key constraint" in str(e).lower():
                        raise InvalidDataError("Referensi tidak valid", "ID user/book tidak ada") from e
                    raise DatabaseError("Gagal memproses data") from e
                except aiomysql.DataError as e:
                    await conn.rollback()
                    raise InvalidDataError("Format data salah", str(e)) from e
                except aiomysql.OperationalError as e:
                    await conn.rollback()
                    raise DatabaseError("Koneksi database gagal") from e
                except Exception as e:
                    await conn.rollback()
                    raise DatabaseError("Operasi database gagal") from e

    async def _validate_peminjaman_data(self, user_id, book_id):
        """Validasi data sebelum operasi peminjaman"""
        # Cek user exists
        user_check = await self._execute_query(
            "SELECT id FROM users WHERE id = %s",
            (user_id,),
            read_only=True
        )
        if not await user_check.fetchone():
            raise RecordNotFoundError("User", user_id)

        # Cek book exists
        book_check = await self._execute_query(
            "SELECT id, stok FROM books WHERE id = %s",
            (book_id,),
            read_only=True
        )
        book = await book_check.fetchone()
        if not book:
            raise RecordNotFoundError("Book", book_id)
        if book['stok'] < 1:
            raise OperationNotAllowedError("Stok buku habis")

    async def add_peminjaman(self, user_id, book_id, tgl_pinjam=date.today(), status='dipinjam'):
        try:
            await self._validate_peminjaman_data(user_id, book_id)

            # Cek apakah buku sudah dipinjam dan belum dikembalikan
            existing = await self._execute_query(
                """SELECT id FROM peminjaman 
                WHERE user_id = %s AND book_id = %s AND status = 'dipinjam'""",
                (user_id, book_id),
                read_only=True
            )
            if await existing.fetchone():
                raise OperationNotAllowedError("Buku sedang dipinjam")

            # Kurangi stok buku
            await self._execute_query(
                "UPDATE books SET stok = stok - 1 WHERE id = %s",
                (book_id,)
            )

            # Tambah peminjaman
            cursor = await self._execute_query(
                """INSERT INTO peminjaman 
                (user_id, book_id, tgl_pinjam, status)
                VALUES (%s, %s, %s, %s)""",
                (user_id, book_id, tgl_pinjam, status)
            )

            return cursor.lastrowid
        except DatabaseError as e:
            raise

    async def get_all_peminjaman(self, page=1, per_page=10):
        try:
            offset = (page - 1) * per_page
            cursor = await self._execute_query(
                """SELECT p.*, b.judul AS book_title, u.username AS user_name 
                FROM peminjaman p
                JOIN books b ON p.book_id = b.id
                JOIN users u ON p.user_id = u.id
                LIMIT %s OFFSET %s""",
                (per_page, offset),
                read_only=True
            )
            return await cursor.fetchall()
        except DatabaseError as e:
            raise

    async def get_peminjaman_by_id(self, peminjaman_id):
        try:
            cursor = await self._execute_query(
                """SELECT p.*, b.judul AS book_title, u.username AS user_name 
                FROM peminjaman p
                JOIN books b ON p.book_id = b.id
                JOIN users u ON p.user_id = u.id
                WHERE p.id = %s""",
                (peminjaman_id,),
                read_only=True
            )
            result = await cursor.fetchone()
            if not result:
                raise RecordNotFoundError("Peminjaman", peminjaman_id)
            return result
        except DatabaseError as e:
            raise

    async def kembalikan_buku(self, peminjaman_id):
        try:
            # Dapatkan data peminjaman
            peminjaman = await self.get_peminjaman_by_id(peminjaman_id)

            if peminjaman['status'] == 'dikembalikan':
                raise OperationNotAllowedError("Buku sudah dikembalikan")

            # Update status pengembalian
            await self._execute_query(
                """UPDATE peminjaman 
                SET tgl_kembali = CURDATE(), status = 'dikembalikan' 
                WHERE id = %s""",
                (peminjaman_id,)
            )

            # Tambah stok buku
            await self._execute_query(
                "UPDATE books SET stok = stok + 1 WHERE id = %s",
                (peminjaman['book_id'],)
            )

            return True
        except DatabaseError as e:
            raise

    async def get_peminjaman_by_user(self, user_id, page=1, per_page=10):
        try:
            offset = (page - 1) * per_page
            cursor = await self._execute_query(
                """SELECT p.*, b.judul AS book_title 
                FROM peminjaman p
                JOIN books b ON p.book_id = b.id
                WHERE p.user_id = %s
                LIMIT %s OFFSET %s""",
                (user_id, per_page, offset),
                read_only=True
            )
            return await cursor.fetchall()
        except DatabaseError as e:
            raise

    async def get_peminjaman_aktif(self, user_id):
        try:
            cursor = await self._execute_query(
                """SELECT p.*, b.judul AS book_title 
                FROM peminjaman p
                JOIN books b ON p.book_id = b.id
                WHERE p.user_id = %s AND status = 'dipinjam'""",
                (user_id,),
                read_only=True
            )
            return await cursor.fetchall()
        except DatabaseError as e:
            raise

    async def is_book_dipinjam(self, user_id, book_id):
        try:
            cursor = await self._execute_query(
                """SELECT COUNT(*) 
                FROM peminjaman 
                WHERE user_id = %s AND book_id = %s AND status = 'dipinjam'""",
                (user_id, book_id),
                read_only=True
            )
            result = await cursor.fetchone()
            return result['COUNT(*)'] > 0
        except DatabaseError as e:
            raise

    async def get_total_peminjaman(self):
        """Untuk kebutuhan paginasi"""
        try:
            cursor = await self._execute_query(
                "SELECT COUNT(*) AS total FROM peminjaman",
                read_only=True
            )
            result = await cursor.fetchone()
            return result['total']
        except DatabaseError as e:
            raise