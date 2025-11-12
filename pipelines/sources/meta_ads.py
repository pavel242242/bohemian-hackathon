"""
Meta Ad Library API Source
Extracts Nike campaign data from Meta (Facebook/Instagram) Ad Library mock
"""

import dlt
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source
def meta_ads_source(base_url: str = "http://localhost:3001"):
    """
    Source for Meta Ad Library API

    Args:
        base_url: Base URL for the Meta Ad Library mock server

    Yields:
        DLT resources with Meta ad campaign data
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
                "name": "meta_campaigns",
                "endpoint": {
                    "path": "ads_archive",
                    "params": {
                        "search_terms": "Nike",
                    },
                    # Meta returns array directly
                    "data_selector": "$",
                },
            }
        ],
    }

    yield from rest_api_resources(config)


def transform_meta_campaign(item: dict) -> dict:
    """
    Transform Meta Ad Library response to unified campaign format

    Args:
        item: Raw Meta ad item

    Returns:
        Transformed campaign dict
    """
    return {
        "campaign_id": item["id"],
        "campaign_name": item.get("ad_creative_bodies", [""])[0][:100],  # Use first 100 chars of creative as name
        "source": "meta",
        "channel": ", ".join(item.get("publisher_platforms", [])),
        "budget": float(item.get("spend", {}).get("upper_bound", 0)),
        "spend": float(item.get("spend", {}).get("lower_bound", 0)),
        "start_date": item.get("ad_delivery_start_time"),
        "end_date": item.get("ad_delivery_stop_time"),
        "impressions_min": int(item.get("impressions", {}).get("lower_bound", 0)),
        "impressions_max": int(item.get("impressions", {}).get("upper_bound", 0)),
        "currency": item.get("currency", "USD"),
        "raw_data": item,  # Store full response for reference
    }


if __name__ == "__main__":
    # Quick test
    pipeline = dlt.pipeline(
        pipeline_name="meta_ads_test",
        destination="duckdb",
        dataset_name="nike_campaigns"
    )

    load_info = pipeline.run(meta_ads_source())
    print(f"✅ Meta Ads loaded: {load_info}")
