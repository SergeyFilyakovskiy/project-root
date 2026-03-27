from datetime import datetime
import pytz

def to_utc(date_str: str, source_tz: str = "UTC") -> str:
    """Приводит дату к UTC. Если платформа возвращает локальное время."""
    try:
        tz = pytz.timezone(source_tz)
        local_dt = datetime.strptime(date_str, "%Y-%m-%d")
        utc_dt = tz.localize(local_dt).astimezone(pytz.utc)
        return utc_dt.strftime("%Y-%m-%d")
    except Exception:
        return date_str  # если не можем конвертировать — оставляем как есть