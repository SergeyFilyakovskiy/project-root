from datetime import datetime, date
import pytz

def to_utc(date_str, source_tz: str = "UTC") -> str:
    try:
        tz = pytz.timezone(source_tz)
        if isinstance(date_str, datetime):
            local_dt = date_str
        elif isinstance(date_str, date):
            # Google Ads может вернуть datetime.date напрямую
            local_dt = datetime(date_str.year, date_str.month, date_str.day)
        else:
            local_dt = datetime.strptime(str(date_str), "%Y-%m-%d")
        return tz.localize(local_dt).astimezone(pytz.utc).strftime("%Y-%m-%d")
    except Exception as e:
        
        return str(date_str)