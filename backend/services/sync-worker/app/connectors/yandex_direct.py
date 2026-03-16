import logging
from datetime import datetime

import httpx

from app.connectors.base import BaseConnector

logger = logging.getLogger(__name__)


class YandexDirectConnector(BaseConnector):
    """
    Коннектор для Яндекс.Директ API.
    Забирает статистику через Reports API.
    """

    REPORTS_URL = "https://api.direct.yandex.com/json/v5/reports"

    async def fetch(self, date_from: datetime, date_to: datetime) -> list[dict]:
        """
        Запрашивает отчёт по кампаниям за период.

        Config должен содержать:
            - client_login: логин рекламного аккаунта
        """
        client_login = self.config["client_login"]

        body = {
            "params": {
                "SelectionCriteria": {
                    "DateFrom": date_from.strftime("%Y-%m-%d"),
                    "DateTo": date_to.strftime("%Y-%m-%d"),
                },
                "FieldNames": ["CampaignId", "CampaignName", "Clicks", "Impressions", "Cost"],
                "ReportName": f"report_{date_from.date()}_{date_to.date()}",
                "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
                "DateRangeType": "CUSTOM_DATE",
                "Format": "TSV",
                "IncludeVAT": "NO",
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.REPORTS_URL,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Client-Login": client_login,
                    "Accept-Language": "ru",
                    "processingMode": "auto",
                },
                json=body,
            )
            response.raise_for_status()

        logger.info(f"YandexDirect fetched data for {client_login}")
        return [{"raw": response.text}]
