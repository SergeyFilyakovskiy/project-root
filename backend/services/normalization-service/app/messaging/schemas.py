from pydantic import BaseModel
from typing import Any

class RawDataMessage(BaseModel):
    integration_id: str
    platform: str
    raw_data: dict[str, Any]

class NormalizedMetric(BaseModel):
    date: str
    integration_id: str
    platform: str
    campaign_id: str
    campaign_name: str
    campaign_group: str
    impressions: int
    clicks: int
    spend: float
    currency: str
    ctr: float
    cpc: float 
