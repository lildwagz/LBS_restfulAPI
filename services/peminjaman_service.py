from datetime import date


class PeminjamanService:
    def __init__(self, dao):
        self.dao = dao

    async def pinjam_buku(self, user_id, book_id):
        return await self.dao.add_peminjaman(
            user_id=user_id,
            book_id=book_id,
            tgl_pinjam=date.today().isoformat(),
            status='dipinjam'
        )

    async def get_all_peminjaman(self):
        return await self.dao.get_all_peminjaman()

    async def get_peminjaman(self, peminjaman_id):
        return await self.dao.get_peminjaman_by_id(peminjaman_id)

    async def kembalikan_buku(self, peminjaman_id):
        return await self.dao.kembalikan_buku(peminjaman_id)

    async def get_user_peminjaman(self, user_id):
        return await self.dao.get_peminjaman_by_user(user_id)

    async def get_aktif_peminjaman(self, user_id):
        return await self.dao.get_peminjaman_aktif(user_id)

    async def cek_status_peminjaman(self, user_id, book_id):
        return await self.dao.is_book_dipinjam(user_id, book_id)