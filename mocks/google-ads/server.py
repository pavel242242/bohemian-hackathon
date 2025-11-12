"""
Google Ads API v16 Mock Server
Provides realistic mock responses for Google Ads API endpoints
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import uvicorn


# Load fixtures
FIXTURES_PATH = Path(__file__).parent / "fixtures.json"

with open(FIXTURES_PATH, "r") as f:
    FIXTURES = json.load(f)


app = FastAPI(
    title="Google Ads API Mock Server",
    description="Mock server for Google Ads API v16 endpoints",
    version="1.0.0",
)


def parse_date_string(date_str: str) -> datetime:
    """Parse date string in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format. Expected YYYY-MM-DD, got {date_str}")


def format_date_string(dt: datetime) -> str:
    """Format datetime to YYYY-MM-DD string"""
    return dt.strftime("%Y-%m-%d")


def build_google_ads_row(campaign: Dict[str, Any], custom_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Build a Google Ads API response row matching the actual API structure.

    The Google Ads API returns results with camelCase field names and specific structure.
    """

    # Use custom date if provided, otherwise use the campaign's end date
    date_str = custom_date or campaign["end_date"]

    row = {
        "campaign": {
            "resourceName": f"customers/1234567890/campaigns/{campaign['id']}",
            "id": campaign["id"],
            "name": campaign["name"],
            "status": campaign["status"],
            "biddingStrategyType": "TARGET_CPA",
            "budgetReferenceResourceName": f"customers/1234567890/campaignBudgets/{campaign['id']}",
            "startDate": campaign["start_date"].replace("-", ""),
            "endDate": campaign["end_date"].replace("-", "") if campaign["end_date"] else "20991231",
            "advertisingChannelType": {
                "YouTube": "VIDEO",
                "Google Display": "DISPLAY",
                "Search": "SEARCH",
            }.get(campaign["channel"], "UNKNOWN"),
        },
        "metrics": {
            "impressions": str(campaign["metrics"]["impressions"]),
            "clicks": str(campaign["metrics"]["clicks"]),
            "costMicros": str(campaign["metrics"]["cost_micros"]),
            "conversions": f"{campaign['metrics']['conversions']:.1f}",
            "conversionValueMicros": str(campaign["metrics"]["conversion_value_micros"]),
            "allConversionValueMicros": str(campaign["metrics"]["conversion_value_micros"]),
            "segments": {
                "date": date_str.replace("-", ""),
            },
        },
        "campaignBudget": {
            "resourceName": f"customers/1234567890/campaignBudgets/{campaign['id']}",
            "id": campaign["id"],
            "amountMicros": str(campaign["budget_micros"]),
            "explicitlySharedBudgetReferenceResourceName": None,
            "implicitlySharedBudgetReferenceResourceName": None,
        },
    }

    return row


def filter_campaigns_by_date(
    campaigns: List[Dict[str, Any]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Filter campaigns by date range"""

    filtered = campaigns.copy()

    if start_date:
        try:
            start = parse_date_string(start_date)
            filtered = [
                c for c in filtered
                if parse_date_string(c["end_date"]) >= start
            ]
        except ValueError as e:
            raise ValueError(f"Invalid start_date: {e}")

    if end_date:
        try:
            end = parse_date_string(end_date)
            filtered = [
                c for c in filtered
                if parse_date_string(c["start_date"]) <= end
            ]
        except ValueError as e:
            raise ValueError(f"Invalid end_date: {e}")

    return filtered


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "google-ads-api-mock"}


@app.post("/googleads/v16/customers/{customer_id}/googleAds:searchStream")
async def search_stream(
    customer_id: str,
    start_date: Optional[str] = Query(None, description="Filter campaigns starting from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter campaigns ending before this date (YYYY-MM-DD)"),
    body: Optional[Dict[str, Any]] = None,
):
    """
    Mock implementation of Google Ads API v16 searchStream endpoint.

    Returns campaign data in Google Ads API format.
    Query parameters:
    - start_date: Filter campaigns by start date (YYYY-MM-DD)
    - end_date: Filter campaigns by end date (YYYY-MM-DD)
    """

    try:
        # Filter campaigns based on date parameters
        filtered_campaigns = filter_campaigns_by_date(
            FIXTURES["campaigns"],
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Build response in Google Ads API format
    # The API returns an array of response objects, each containing a results array
    response_data = []

    for campaign in filtered_campaigns:
        row = build_google_ads_row(campaign, custom_date=end_date or campaign["end_date"])

        response_object = {
            "results": [row],
            "fieldMask": "campaign.id,campaign.name,campaign.status,metrics.impressions,metrics.clicks,metrics.costMicros,campaignBudget.amountMicros",
            "requestId": f"req_{customer_id}_{campaign['id']}",
        }

        response_data.append(response_object)

    # Return as JSON
    return response_data


@app.post("/googleads/v16/customers/{customer_id}/googleAds:search")
async def search(
    customer_id: str,
    start_date: Optional[str] = Query(None, description="Filter campaigns starting from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter campaigns ending before this date (YYYY-MM-DD)"),
):
    """
    Mock implementation of Google Ads API v16 search endpoint (non-streaming).

    Returns all campaign data in a single response.
    """

    try:
        # Filter campaigns based on date parameters
        filtered_campaigns = filter_campaigns_by_date(
            FIXTURES["campaigns"],
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Build response
    results = []
    for campaign in filtered_campaigns:
        row = build_google_ads_row(campaign, custom_date=end_date or campaign["end_date"])
        results.append(row)

    return {
        "results": results,
        "fieldMask": "campaign.id,campaign.name,campaign.status,metrics.impressions,metrics.clicks,metrics.costMicros,campaignBudget.amountMicros",
        "totalResultsCount": str(len(results)),
        "requestId": f"req_{customer_id}_search",
    }


@app.get("/campaigns")
async def list_campaigns(
    status: Optional[str] = Query(None, description="Filter by status (ENABLED, PAUSED)"),
    channel: Optional[str] = Query(None, description="Filter by channel (YouTube, Google Display, Search)"),
):
    """
    Convenience endpoint to list available campaigns with filters.
    """

    campaigns = FIXTURES["campaigns"].copy()

    if status:
        campaigns = [c for c in campaigns if c["status"] == status.upper()]

    if channel:
        campaigns = [c for c in campaigns if c["channel"] == channel]

    return {
        "campaigns": campaigns,
        "count": len(campaigns),
    }


@app.get("/fixtures")
async def get_fixtures():
    """Return all fixture data"""
    return FIXTURES


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "service": "Google Ads API Mock Server",
        "version": "v16",
        "endpoints": {
            "health": "GET /health",
            "list_campaigns": "GET /campaigns",
            "search": "POST /googleads/v16/customers/{customer_id}/googleAds:search",
            "search_stream": "POST /googleads/v16/customers/{customer_id}/googleAds:searchStream",
            "fixtures": "GET /fixtures",
        },
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
