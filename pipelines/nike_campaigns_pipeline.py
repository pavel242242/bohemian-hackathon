#!/usr/bin/env python3
"""
Nike Campaigns Unified Pipeline
Extracts campaign data from all advertising platforms and creates unified view in DuckDB
"""

import dlt
from sources import (
    meta_ads_source,
    google_ads_source,
    tiktok_ads_source,
    budget_approvals_source,
)
from sources.seznam_ads import seznam_campaigns


def load_all_campaigns():
    """
    Load Nike campaigns from all sources into DuckDB

    Returns:
        Pipeline load info
    """
    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name="nike_campaigns",
        destination="duckdb",
        dataset_name="marketing_data",
        dev_mode=False,  # Use stable schema name
    )

    print("=" * 60)
    print("NIKE CAMPAIGNS DATA PIPELINE")
    print("=" * 60)
    print()

    # Load Meta Ads
    print("📊 Loading Meta Ad Library campaigns...")
    try:
        meta_info = pipeline.run(
            meta_ads_source(),
            table_name="meta_campaigns",
        )
        print(f"✅ Meta: {meta_info}")
    except Exception as e:
        print(f"❌ Meta failed: {e}")

    print()

    # Load Google Ads
    print("📊 Loading Google Ads campaigns...")
    try:
        google_info = pipeline.run(
            google_ads_source(),
            table_name="google_campaigns",
        )
        print(f"✅ Google: {google_info}")
    except Exception as e:
        print(f"❌ Google failed: {e}")

    print()

    # Load TikTok Ads
    print("📊 Loading TikTok Ads campaigns...")
    try:
        tiktok_info = pipeline.run(
            tiktok_ads_source(),
            table_name="tiktok_campaigns",
        )
        print(f"✅ TikTok: {tiktok_info}")
    except Exception as e:
        print(f"❌ TikTok failed: {e}")

    print()

    # Load Budget Approvals
    print("📊 Loading budget approvals...")
    try:
        budget_info = pipeline.run(
            budget_approvals_source(),
            table_name="budget_approvals",
        )
        print(f"✅ Budget: {budget_info}")
    except Exception as e:
        print(f"❌ Budget failed: {e}")

    print()

    # Load Seznam Ads (Complex API)
    print("📊 Loading Seznam Ads campaigns...")
    try:
        seznam_info = pipeline.run(
            seznam_campaigns(),
            table_name="seznam_campaigns",
        )
        print(f"✅ Seznam: {seznam_info}")
    except Exception as e:
        print(f"❌ Seznam failed: {e}")

    print()
    print("=" * 60)
    print("✅ PIPELINE COMPLETE")
    print("=" * 60)

    return pipeline


def query_top_campaigns(pipeline, limit: int = 20):
    """
    Query top campaigns across all sources

    Args:
        pipeline: DLT pipeline instance
        limit: Number of top campaigns to return
    """
    import duckdb

    print()
    print("=" * 60)
    print(f"TOP {limit} NIKE CAMPAIGNS")
    print("=" * 60)
    print()

    # Get pipeline database path - use the default DuckDB path
    db_path = "nike_campaigns.duckdb"

    # Connect to DuckDB
    conn = duckdb.connect(db_path)

    # Query across all campaign tables
    query = f"""
    WITH all_campaigns AS (
        -- Meta campaigns (no campaign name, use page_name)
        SELECT
            id as campaign_id,
            page_name as campaign_name,
            'Meta' as source,
            'Facebook/Instagram' as channel,
            CAST(spend__upper_bound AS DOUBLE) as budget,
            ad_delivery_start_time as start_date,
            ad_delivery_stop_time as end_date
        FROM marketing_data.meta_campaigns

        UNION ALL

        -- Google campaigns
        SELECT
            id as campaign_id,
            name as campaign_name,
            'Google' as source,
            channel,
            CAST(budget_micros AS DOUBLE) / 1000000 as budget,
            start_date::TIMESTAMP as start_date,
            end_date::TIMESTAMP as end_date
        FROM marketing_data.google_campaigns

        UNION ALL

        -- TikTok campaigns
        SELECT
            campaign_id,
            campaign_name,
            'TikTok' as source,
            channel,
            CAST(budget AS DOUBLE) as budget,
            NULL as start_date,
            NULL as end_date
        FROM marketing_data.tiktok_campaigns
    )
    SELECT
        campaign_id,
        campaign_name,
        source,
        channel,
        budget,
        start_date,
        end_date
    FROM all_campaigns
    WHERE budget IS NOT NULL
    ORDER BY budget DESC
    LIMIT {limit}
    """

    result = conn.execute(query).fetchdf()

    print(result.to_string(index=False))
    print()
    print(f"Total campaigns: {len(result)}")

    conn.close()

    return result


if __name__ == "__main__":
    # Run pipeline
    pipeline = load_all_campaigns()

    # Query results
    top_campaigns = query_top_campaigns(pipeline, limit=20)

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Loaded {len(top_campaigns)} campaigns")
    print(f"📂 Database: nike_campaigns.duckdb")
    print()
    print("To explore data:")
    print("  duckdb nike_campaigns.duckdb")
    print()
