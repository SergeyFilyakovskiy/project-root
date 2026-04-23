from app.messaging.schemas import RawDataMessage, NormalizedMetric

def normalize(message: RawDataMessage) -> list[NormalizedMetric]: # type: ignore
    platform = message.platform
    if platform == "google_ads":
        return _normalize_google(message)
    elif platform == "yandex_ads":
        return _normalize_yandex(message)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

def _normalize_google(message: RawDataMessage)-> list[NormalizedMetric]:
    results = []
    rows = message.raw_data.get("rows", [])
    for row in rows:
        impressions = int(row.get("impressions", 0))
        clicks = int(row.get("clicks", 0))
        spend = float(row.get("costMicros", 0)) / 1_000_000
        results.append(NormalizedMetric(
            date=row["date"],
            integration_id=message.integration_id,
            platform=message.platform,
            campaign_group=row.get("adGroupName", ""),
            campaign_id=str(row.get("campaignId", "")),
            campaign_name=row.get("campaignName", ""),
            impressions=impressions,
            clicks=clicks,
            spend=spend,
            currency=row.get("currency", "USD"),
            ctr=round(clicks / impressions * 100, 4) if impressions > 0 else 0.0,
            cpc=round(spend / clicks, 4) if clicks > 0 else 0.0,
        ))
    return results

def _normalize_yandex(message: RawDataMessage)-> list[NormalizedMetric]:
    results = []
    rows = message.raw_data.get("data", {}).get("rows", [])
    for row in rows:
        impressions = int(row.get("Impressions", 0))
        clicks = int(row.get("Clicks", 0))
        spend = float(row.get("Cost", 0))
        results.append(NormalizedMetric(
            date=row["Date"],
            integration_id=message.integration_id,
            platform=message.platform,
            campaign_group=row.get("AdGroupName", ""),
            campaign_id=str(row.get("CampaignId", "")),
            campaign_name=row.get("CampaignName", ""),
            impressions=impressions,
            clicks=clicks,
            spend=spend,
            currency=row.get("Currency", "RUB"),
            ctr=round(clicks / impressions * 100, 4) if impressions > 0 else 0.0,
            cpc=round(spend / clicks, 4) if clicks > 0 else 0.0,
        ))
    return results
