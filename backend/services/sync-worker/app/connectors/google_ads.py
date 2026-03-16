import logging
from datetime import datetime

import httpx

from app.connectors.base import BaseConnector

logger = logging.getLogger(__name__)


class GoogleAdsConnector(BaseConnector):
    """
    Коннектор для Google Ads API.
    Забирает статистику кампаний через Google Ads Query Language (GAQL).
    """

    BASE_URL = "https://googleads.googleapis.com/v16/customers/{customer_id}/googleAds:searchStream"

    async def fetch(self, date_from: datetime, date_to: datetime) -> list[dict]:
        """
        Запрашивает статистику кампаний за период через GAQL.

        Config должен содержать:
            - customer_id: ID рекламного аккаунта Google Ads
            - developer_token: токен разработчика
        """
        customer_id = self.config["customer_id"]
        developer_token = self.config["developer_token"]

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                segments.date
            FROM campaign
            WHERE segments.date BETWEEN '{date_from.strftime('%Y-%m-%d')}' 
                AND '{date_to.strftime('%Y-%m-%d')}'
        """

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.BASE_URL.format(customer_id=customer_id),
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "developer-token": developer_token,
                },
                json={"query": query},
            )
            response.raise_for_status()

        data = response.json()
        logger.info(f"GoogleAds fetched {len(data)} records")
        return data
