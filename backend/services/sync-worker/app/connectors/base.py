from abc import ABC, abstractmethod
from datetime import datetime


class BaseConnector(ABC):
    """
    Абстрактный базовый класс для всех коннекторов рекламных платформ.
    Каждый коннектор получает токен и конфиг, умеет забирать данные за период.
    """

    def __init__(self, access_token: str, config: dict):
        """
        Args:
            access_token: Актуальный OAuth токен платформы.
            config: Платформо-специфичный конфиг (account_id и т.д.).
        """
        self.access_token = access_token
        self.config = config

    @abstractmethod
    async def fetch(self, date_from: datetime, date_to: datetime) -> list[dict]:
        """
        Забирает данные с платформы за указанный период.

        Args:
            date_from: Начало периода.
            date_to: Конец периода.

        Returns:
            Список сырых записей для передачи в normalization-service.
        """
        ...
