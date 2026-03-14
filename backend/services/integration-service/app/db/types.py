from typing import Any

from cryptography.fernet import Fernet
from sqlalchemy import Dialect, String, TypeDecorator
from app.core.config import settings

class EncryptedString(TypeDecorator):

    impl = String(2048)

    cache_ok = True

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._fernet = Fernet(settings.db_encryption_key.get_secret_value().encode())

    def process_bind_param(self, value, dialect)-> str | None:
        if value is None: 
            return None
        return self._fernet.encrypt(value.encode()).decode()
    
    def process_result_value(self, value: Any | None, dialect: Dialect) -> Any | None:
        if value is None:
            return None
        return  self._fernet.decrypt(value.encode()).decode()
    