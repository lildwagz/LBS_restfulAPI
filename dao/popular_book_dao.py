import aiomysql
from datetime import date
from utils.exceptions import DatabaseError, InvalidDataError


class PopularBookDAO:
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

    async def get_popular_books(self, year: int, limit: int = 10):
        """Mendapatkan buku populer berdasarkan tahun"""
        try:
            # Validasi parameter
            if not year or year < 1900 or year > 2100:
                raise InvalidDataError('year', year, 'Tahun harus antara 1900-2100')

            if limit < 1 or limit > 100:
                raise InvalidDataError('limit', limit, 'Limit harus antara 1-100')

            query = """
                SELECT 
                    b.id AS book_id,
                    b.judul,
                    b.pengarang,
                    COUNT(p.id) AS total_pinjam,
                    ROUND(AVG(DATEDIFF(p.tgl_kembali, p.tgl_pinjam)), 1) AS avg_durasi,
                    MAX(p.tgl_pinjam) AS terakhir_pinjam,
                    ROUND((COUNT(p.id) * 100.0) / (
                        SELECT COUNT(*) 
                        FROM peminjaman 
                        WHERE YEAR(tgl_pinjam) = %s
                    ), 2) AS persentase
                FROM peminjaman p
                JOIN books b ON p.book_id = b.id
                WHERE YEAR(p.tgl_pinjam) = %s
                GROUP BY b.id, b.judul, b.pengarang
                ORDER BY total_pinjam DESC
                LIMIT %s
            """

            result = await self._execute_query(query, (year, year, limit))

            # Konversi tipe data
            for row in result:
                row['avg_durasi'] = float(row['avg_durasi']) if row['avg_durasi'] else 0.0
                row['persentase'] = float(row['persentase']) if row['persentase'] else 0.0
                if row['terakhir_pinjam']:
                    row['terakhir_pinjam'] = row['terakhir_pinjam'].isoformat()

            return result
        except Exception as e:
            raise DatabaseError(f"Gagal mendapatkan buku populer: {str(e)}")

    async def get_available_years(self):
        """Mendapatkan tahun-tahun tersedia untuk analisis"""
        try:
            query = """
                SELECT DISTINCT YEAR(tgl_pinjam) AS year 
                FROM peminjaman 
                ORDER BY year DESC
            """
            result = await self._execute_query(query)
            return [row['year'] for row in result if row['year'] is not None]
        except Exception as e:
            raise DatabaseError(f"Gagal mendapatkan tahun tersedia: {str(e)}")