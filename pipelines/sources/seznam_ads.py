"""
Seznam Ads Source - Dynamically Generated for Complex API

Handles:
- Nested cursor-based pagination
- Non-standard response format (wrapped in responseMetadata)
- Multiple endpoint calls to enrich data (campaigns + ads + stats)
- Rate limiting headers
"""

import dlt
from dlt.sources.helpers import requests
import time

@dlt.resource(
    name="seznam_campaigns",
    write_disposition="merge",
    primary_key="campaignId"
)
def seznam_campaigns(
    base_url: str = "http://localhost:3004",
    api_key: str = "demo_api_key_12345"
):
    """
    Load Nike campaigns from Seznam Ads with full enrichment

    This handles the complex Seznam API structure:
    1. Paginate through campaigns with cursor tokens
    2. For each campaign, call /ads and /stats endpoints
    3. Unwrap non-standard response format
    4. Combine all data into enriched campaign records
    """

    headers = {
        'X-Seznam-Api-Key': api_key,
        'Content-Type': 'application/json'
    }

    # Track rate limiting
    def check_rate_limit(response):
        """Check rate limit headers"""
        remaining = response.headers.get('X-RateLimit-Remaining')
        if remaining and int(remaining) < 10:
            print(f"⚠️ Rate limit warning: {remaining} requests remaining")
            time.sleep(1)  # Be conservative

    # Pagination state
    cursor = None
    page = 1

    while True:
        # Build pagination parameters
        params = {'page': page, 'pageSize': 10}
        if cursor:
            params['cursor'] = cursor

        # Fetch campaigns page
        response = requests.get(
            f"{base_url}/api/v2/campaigns",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        check_rate_limit(response)

        data = response.json()

        # Extract from non-standard response format
        if data.get('responseMetadata', {}).get('status') != 'SUCCESS':
            error = data.get('responseMetadata', {}).get('message', 'Unknown error')
            raise Exception(f"Seznam API error: {error}")

        campaigns = data.get('data', {}).get('campaigns', [])

        if not campaigns:
            break

        # Enrich each campaign with ads and stats
        for campaign in campaigns:
            campaign_id = campaign['campaignId']

            # Fetch ads for this campaign
            try:
                ads_response = requests.get(
                    f"{base_url}/api/v2/campaigns/{campaign_id}/ads",
                    headers=headers
                )
                ads_response.raise_for_status()
                check_rate_limit(ads_response)

                ads_data = ads_response.json()
                if ads_data.get('responseMetadata', {}).get('status') == 'SUCCESS':
                    ads = ads_data.get('data', {}).get('ads', [])
                    campaign['ads'] = ads
                    campaign['adCount'] = len(ads)

                    # Calculate aggregate ad metrics
                    if ads:
                        campaign['totalClicks'] = sum(ad.get('clicks', 0) for ad in ads)
                        campaign['totalImpressions'] = sum(ad.get('impressions', 0) for ad in ads)
                        campaign['avgCTR'] = sum(ad.get('ctr', 0) for ad in ads) / len(ads)
            except Exception as e:
                print(f"Warning: Could not fetch ads for campaign {campaign_id}: {e}")
                campaign['ads'] = []
                campaign['adCount'] = 0

            # Fetch stats for this campaign
            try:
                stats_response = requests.get(
                    f"{base_url}/api/v2/campaigns/{campaign_id}/stats",
                    headers=headers
                )
                stats_response.raise_for_status()
                check_rate_limit(stats_response)

                stats_data = stats_response.json()
                if stats_data.get('responseMetadata', {}).get('status') == 'SUCCESS':
                    stats = stats_data.get('data', {}).get('statistics', {})
                    if stats:
                        campaign['totalSpend'] = stats.get('totalSpend', 0)
                        campaign['avgCPC'] = stats.get('avgCPC', 0)
                        campaign['conversions'] = stats.get('conversions', 0)
                        campaign['conversionRate'] = stats.get('conversionRate', 0)
                        campaign['currency'] = stats_data.get('data', {}).get('currency', 'CZK')
            except Exception as e:
                print(f"Warning: Could not fetch stats for campaign {campaign_id}: {e}")

            # Add source metadata
            campaign['source'] = 'seznam'
            campaign['channel'] = 'Seznam.cz'

            # Convert daily budget to total budget estimate (30 days)
            campaign['budgetCZK'] = campaign.get('dailyBudgetCZK', 0)
            campaign['estimatedMonthlyBudget'] = campaign.get('dailyBudgetCZK', 0) * 30

            yield campaign

        # Check for next page
        pagination = data.get('pagination', {}).get('navigation', {})
        if not pagination.get('hasNext'):
            break

        cursor = pagination.get('nextCursor')
        page += 1

        # Be nice to the API
        time.sleep(0.1)

    print(f"✅ Seznam Ads: Extracted {page} pages of campaigns")
