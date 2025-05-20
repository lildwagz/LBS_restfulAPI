class BookService:
    def __init__(self, dao):
        self.dao = dao

    async def get_all_books(self, page=1, per_page=10):
        return await self.dao.get_all_books(page, per_page)

    async def get_book(self, book_id):
        return await self.dao.get_book_by_id(book_id)

    async def create_book(self, data):
        return await self.dao.add_book(
            judul=data['judul'],
            pengarang=data['pengarang'],
            stok=data['stok'],
            tahun_terbit=data['tahun_terbit']
        )

    async def update_book(self, book_id, data):
        return await self.dao.update_book(
            book_id=book_id,
            **{k: v for k, v in data.items() if k in ['judul', 'pengarang', 'stok', 'tahun_terbit']}
        )

    async def delete_book(self, book_id):
        return await self.dao.delete_book(book_id)

    async def search_books(self, keyword, search_fields=['judul', 'pengarang']):
        return await self.dao.search_books(
            keyword=keyword,
            search_fields=search_fields
        )

    async def adjust_stock(self, book_id, quantity):
        return await self.dao.adjust_stock(
            book_id=book_id,
            quantity=quantity
        )

    async def get_book_by_id(self, book_id):
        return await self.dao.get_book_by_id(book_id)

    async def add_book(self, param, param1, param2, param3):
        return await self.dao.add_book(param, param1, param2, param3)
    