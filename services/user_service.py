class UserService:
    def __init__(self, dao):
        self.dao = dao

    async def get_user(self, user_id):
        return await self.dao.get_by_id(user_id)

    async def get_user_by_username(self, username):
        return await self.dao.get_by_username(username)

    async def create_user(self, username, password, role='user'):
        return await self.dao.create_user(username, password, role)

    async def update_user(self, user_id, username, password, role):
        return await self.dao.update_user(user_id, username, password, role)

    async def delete_user(self, user_id):
        return await self.dao.delete_user(user_id)

    async def get_all_users(self):
        return await self.dao.get_all_users()

    async def search_users(self, keyword):
        return await self.dao.search_users(keyword)