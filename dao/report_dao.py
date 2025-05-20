import aiomysql
from datetime import date
from utils.exceptions import DatabaseError


class ReportDAO:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def _execute_query(self, query, params=None):
        """Utility method untuk handle operasi database"""
        async with self.db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute(query, params or ())
                    return await cursor.fetchall()
                except aiomysql.Error as e:
                    raise DatabaseError(f"Database error: {str(e)}") from e

    async def generate_report(self, **filters):
        """Generate laporan peminjaman dengan filter"""
        try:
            base_query = """
                SELECT 
                    p.id AS peminjaman_id,
                    u.username,
                    b.judul AS book_title,
                    p.tgl_pinjam,
                    p.tgl_kembali,
                    p.status,
                    DATEDIFF(p.tgl_kembali, p.tgl_pinjam) AS lama_peminjaman
                FROM peminjaman p
                JOIN users u ON p.user_id = u.id
                JOIN books b ON p.book_id = b.id
            """

            where_clauses = []
            params = []

            # Handle date filters
            if filters.get('start_date'):
                where_clauses.append("p.tgl_pinjam >= %s")
                params.append(filters['start_date'])
            if filters.get('end_date'):
                where_clauses.append("p.tgl_pinjam <= %s")
                params.append(filters['end_date'])

            # Handle other filters
            if filters.get('status'):
                where_clauses.append("p.status = %s")
                params.append(filters['status'])
            if filters.get('book_title'):
                where_clauses.append("b.judul LIKE %s")
                params.append(f"%{filters['book_title']}%")
            if filters.get('username'):
                where_clauses.append("u.username LIKE %s")
                params.append(f"%{filters['username']}%")

            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)

            return await self._execute_query(base_query, params)

        except Exception as e:
            raise DatabaseError(f"Failed to generate report: {str(e)}")

    async def get_filter_options(self):
        """Mendapatkan opsi filter yang tersedia"""
        try:
            options = {
                'status': [],
                'book_titles': [],
                'usernames': []
            }

            # Get status options
            status_query = "SELECT DISTINCT status FROM peminjaman"
            status_result = await self._execute_query(status_query)
            options['status'] = [row['status'] for row in status_result]

            # Get book title options
            book_query = "SELECT DISTINCT judul FROM books"
            book_result = await self._execute_query(book_query)
            options['book_titles'] = [row['judul'] for row in book_result]

            # Get username options
            user_query = "SELECT DISTINCT username FROM users"
            user_result = await self._execute_query(user_query)
            options['usernames'] = [row['username'] for row in user_result]

            return options
        except Exception as e:
            raise DatabaseError(f"Failed to get filter options: {str(e)}")