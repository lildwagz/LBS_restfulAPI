from datetime import date


class PopularBookService:
    def __init__(self, dao):
        self.dao = dao

    async def get_popular_books(self, year=None, limit=10):
        # Default ke tahun berjalan jika tidak ada input
        current_year = date.today().year
        year = year or current_year
        return await self.dao.get_popular_books(year, limit)