from pydantic import BaseModel

class MetricResponse(BaseModel):
    date: str
    integration_id: str
    platform: str
    campaign_group: str
    campaign_id: str
    campaign_name: str
    impressions: int
    clicks: int
    spend: float
    currency: str
    ctr: float
    cpc: float

class MetricsListResponse(BaseModel):
    items: list[MetricResponse]
    total: int