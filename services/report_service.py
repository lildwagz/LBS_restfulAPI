from collections import defaultdict
from datetime import datetime

class ReportService:
    def __init__(self, dao):
        self.dao = dao

    async def generate_report(self, **filters):
        raw_data = await self.dao.get_filtered_report(**filters)
        return {
            "data": raw_data,
            "stats": {
                "monthly_trend": self._calculate_monthly_trend(raw_data),
                "status_distribution": self._calculate_status_distribution(raw_data)
            }
        }

    async def get_filter_options(self):
        return {
            "book_titles": await self.dao.get_all_book_titles(),
            "usernames": await self.dao.get_all_usernames()
        }

    def _calculate_monthly_trend(self, data):
        trend = defaultdict(int)
        for item in data:
            date = datetime.fromisoformat(item['tgl_pinjam'])
            key = f"{date.year}-{date.month:02d}"
            trend[key] += 1
        return dict(sorted(trend.items()))

    def _calculate_status_distribution(self, data):
        distribution = defaultdict(int)
        for item in data:
            distribution[item['status']] += 1
        return dict(distribution)