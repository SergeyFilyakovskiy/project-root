from pydantic import BaseModel, field_validator
from typing import Any


class RawDataMessage(BaseModel):
    integration_id: str
    date_from: str
    date_to: str
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
    
    @field_validator("date", mode="before")
    @classmethod
    def coerce_date(cls, v):
        if hasattr(v, "strftime"):
            return v.strftime("%Y-%m-%d")
        return str(v)
    
class NormalizedBatchMessage(BaseModel):
    integration_id: str
    platform: str
    date_from: str
    date_to: str
    metrics: list[NormalizedMetric]