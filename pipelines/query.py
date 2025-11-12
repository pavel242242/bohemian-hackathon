#!/usr/bin/env python3
"""
Simple CLI to query Nike campaigns data
Run the pipeline and answer questions about campaigns
"""

import sys
import dlt
import duckdb
from datetime import datetime
from sources import (
    meta_ads_source,
    google_ads_source,
    tiktok_ads_source,
    budget_approvals_source,
)


def print_header(text):
    """Print a formatted header"""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)
    print()


def run_pipeline():
    """Run the data extraction pipeline"""
    print_header("EXTRACTING NIKE CAMPAIGNS DATA")

    pipeline = dlt.pipeline(
        pipeline_name="nike_campaigns",
        destination="duckdb",
        dataset_name="marketing_data",
        dev_mode=False,
    )

    sources = [
        ("Meta (Facebook/Instagram)", meta_ads_source),
        ("Google Ads", google_ads_source),
        ("TikTok Ads", tiktok_ads_source),
        ("Budget Approvals", budget_approvals_source),
    ]

    for name, source in sources:
        print(f"📊 Extracting from {name}...", end=" ")
        try:
            pipeline.run(source())
            print("✅")
        except Exception as e:
            print(f"❌ Error: {e}")

    return pipeline


def query_campaigns(query_text, limit=20):
    """Query campaigns from DuckDB"""
    conn = duckdb.connect("nike_campaigns.duckdb")

    # Parse query for filters (simple approach)
    query_lower = query_text.lower()

    # Determine what to show based on query
    show_top = "top" in query_lower
    show_recent = "recent" in query_lower or "last" in query_lower
    show_channel = any(word in query_lower for word in ["channel", "platform", "where"])
    show_budget = "budget" in query_lower or "spend" in query_lower or "cost" in query_lower

    # Build query
    query = f"""
    WITH all_campaigns AS (
        SELECT
            id as campaign_id,
            page_name as campaign_name,
            'Meta' as source,
            'Facebook/Instagram' as channel,
            CAST(spend__upper_bound AS DOUBLE) as budget,
            CAST(impressions__upper_bound AS BIGINT) as impressions,
            ad_delivery_start_time as start_date,
            ad_delivery_stop_time as end_date
        FROM marketing_data.meta_campaigns

        UNION ALL

        SELECT
            id as campaign_id,
            name as campaign_name,
            'Google' as source,
            channel,
            CAST(budget_micros AS DOUBLE) / 1000000 as budget,
            CAST(metrics__impressions AS BIGINT) as impressions,
            start_date::TIMESTAMP as start_date,
            end_date::TIMESTAMP as end_date
        FROM marketing_data.google_campaigns

        UNION ALL

        SELECT
            campaign_id,
            campaign_name,
            'TikTok' as source,
            channel,
            CAST(budget AS DOUBLE) as budget,
            CAST(metrics__impressions AS BIGINT) as impressions,
            NULL as start_date,
            NULL as end_date
        FROM marketing_data.tiktok_campaigns
    )
    SELECT
        campaign_name,
        source,
        channel,
        '$' || ROUND(budget / 1000, 1) || 'K' as budget,
        impressions,
        start_date,
        end_date
    FROM all_campaigns
    WHERE budget IS NOT NULL
    ORDER BY {"start_date DESC" if show_recent else "budget DESC"}
    LIMIT {limit}
    """

    result = conn.execute(query).fetchdf()
    conn.close()

    return result


def format_results(df, query_text):
    """Format and display results"""
    print_header(f"RESULTS: {query_text}")

    if len(df) == 0:
        print("No campaigns found.")
        return

    # Display as a nice table
    print(df.to_string(index=False))
    print()
    print(f"📊 Total: {len(df)} campaigns")
    print()

    # Show summary stats
    print("💰 SUMMARY:")
    print(f"   Sources: {', '.join(df['source'].unique())}")
    print(f"   Channels: {', '.join(df['channel'].unique())}")
    print()


def interactive_mode():
    """Run in interactive mode"""
    print_header("NIKE CAMPAIGNS QUERY INTERFACE")
    print("Ask questions about Nike campaigns!")
    print("Examples:")
    print("  - Show me the top 20 Nike campaigns")
    print("  - What are the recent campaigns?")
    print("  - Show campaigns with budgets")
    print()
    print("Type 'refresh' to re-extract data")
    print("Type 'quit' or 'exit' to quit")
    print()

    while True:
        try:
            query = input("🔍 Your question: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if query.lower() == 'refresh':
                run_pipeline()
                continue

            # Query the database
            print()
            print("⏳ Querying database...")
            results = query_campaigns(query)
            format_results(results, query)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command mode: query.py "your question"
        query_text = " ".join(sys.argv[1:])

        print_header("NIKE CAMPAIGNS QUERY")
        print(f"Question: {query_text}")

        # Check if database exists, if not run pipeline
        import os
        if not os.path.exists("nike_campaigns.duckdb"):
            print("\n📂 Database not found. Running pipeline first...")
            run_pipeline()

        # Query
        results = query_campaigns(query_text)
        format_results(results, query_text)

    else:
        # Interactive mode
        # Check if database exists
        import os
        if not os.path.exists("nike_campaigns.duckdb"):
            print("\n📂 Database not found. Running pipeline first...")
            run_pipeline()

        interactive_mode()


if __name__ == "__main__":
    main()
