"""
TikTok Ads API Source
Extracts Nike campaign data from TikTok Ads API mock
"""

import dlt
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source
def tiktok_ads_source(base_url: str = "http://localhost:3003"):
    """
    Source for TikTok Ads API

    Args:
        base_url: Base URL for the TikTok Ads mock server

    Yields:
        DLT resources with TikTok Ads campaign data
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resource_defaults": {
            "primary_key": "campaign_id",
            "write_disposition": "merge",
        },
        "resources": [
            {
                "name": "tiktok_campaigns",
                "endpoint": {
                    "path": "open_api/v1.3/campaign/get/",
                    "params": {
                        "advertiser_id": "1700000000000001",  # Nike advertiser ID
                    },
                    # TikTok returns {data: {campaigns: [...]}}
                    "data_selector": "data.campaigns",
                },
            }
        ],
    }

    yield from rest_api_resources(config)


def transform_tiktok_campaign(item: dict) -> dict:
    """
    Transform TikTok Ads response to unified campaign format

    Args:
        item: Raw TikTok Ads campaign item

    Returns:
        Transformed campaign dict
    """
    metrics = item.get("metrics", {})

    return {
        "campaign_id": item["campaign_id"],
        "campaign_name": item.get("campaign_name", ""),
        "source": "tiktok",
        "channel": item.get("channel", "TikTok"),
        "budget": float(item.get("budget", 0)),
        "spend": float(metrics.get("spend", 0)),
        "start_date": None,  # TikTok uses Unix timestamps - would need conversion
        "end_date": None,
        "impressions_min": int(metrics.get("impressions", 0)),
        "impressions_max": int(metrics.get("impressions", 0)),
        "clicks": int(metrics.get("clicks", 0)),
        "conversions": int(metrics.get("conversions", 0)),
        "conversion_rate": float(metrics.get("conversion_rate", 0)),
        "cpc": float(metrics.get("cpc", 0)),
        "currency": "USD",
        "raw_data": item,
    }


if __name__ == "__main__":
    # Quick test
    pipeline = dlt.pipeline(
        pipeline_name="tiktok_ads_test",
        destination="duckdb",
        dataset_name="nike_campaigns"
    )

    load_info = pipeline.run(tiktok_ads_source())
    print(f"✅ TikTok Ads loaded: {load_info}")
