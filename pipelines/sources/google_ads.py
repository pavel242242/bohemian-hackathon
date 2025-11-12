"""
Google Ads API Source
Extracts Nike campaign data from Google Ads API mock
"""

import dlt
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source
def google_ads_source(base_url: str = "http://localhost:8000"):
    """
    Source for Google Ads API

    Args:
        base_url: Base URL for the Google Ads mock server

    Yields:
        DLT resources with Google Ads campaign data
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "merge",
        },
        "resources": [
            {
                "name": "google_campaigns",
                "endpoint": {
                    "path": "campaigns",
                    "params": {
                        "advertiser_name": "Nike",
                    },
                    # Google mock returns {campaigns: [...]}
                    "data_selector": "campaigns",
                },
            }
        ],
    }

    yield from rest_api_resources(config)


def transform_google_campaign(item: dict) -> dict:
    """
    Transform Google Ads response to unified campaign format

    Args:
        item: Raw Google Ads campaign item

    Returns:
        Transformed campaign dict
    """
    # Google Ads uses micros (1 dollar = 1,000,000 micros)
    budget_micros = item.get("budget_amount_micros", 0)
    cost_micros = item.get("cost_micros", 0)

    return {
        "campaign_id": item["campaign_id"],
        "campaign_name": item.get("campaign_name", ""),
        "source": "google",
        "channel": item.get("channel", "Google"),
        "budget": budget_micros / 1_000_000,  # Convert micros to dollars
        "spend": cost_micros / 1_000_000,
        "start_date": item.get("start_date"),
        "end_date": item.get("end_date"),
        "impressions_min": item.get("impressions", 0),
        "impressions_max": item.get("impressions", 0),  # Google doesn't provide range
        "clicks": item.get("clicks", 0),
        "currency": "USD",
        "raw_data": item,
    }


if __name__ == "__main__":
    # Quick test
    pipeline = dlt.pipeline(
        pipeline_name="google_ads_test",
        destination="duckdb",
        dataset_name="nike_campaigns"
    )

    load_info = pipeline.run(google_ads_source())
    print(f"✅ Google Ads loaded: {load_info}")
