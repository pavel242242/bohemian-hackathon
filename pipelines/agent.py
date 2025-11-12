"""
Intelligent Agent for Nike Campaigns Query System

This agent:
1. Understands natural language queries
2. Checks if data exists and is fresh
3. Decides to query DB or build new pipeline
4. Generates dlthub sources dynamically
5. Uses Stagehand for web scraping when needed
"""

import os
import sys
import json
import duckdb
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re

# Import dynamic driver generation
from driver_manager import DriverManager

# Known API endpoints for different sources
API_CONFIGS = {
    'meta': {
        'base_url': 'http://localhost:3001',
        'endpoint': '/ads_archive',
        'headers': {}
    },
    'google': {
        'base_url': 'http://localhost:8000',
        'endpoint': '/api/v1/campaigns',
        'headers': {}
    },
    'tiktok': {
        'base_url': 'http://localhost:3003',
        'endpoint': '/api/v1/campaigns',
        'headers': {}
    },
    'seznam': {
        'base_url': 'http://localhost:3004',
        'endpoint': '/api/v2/campaigns',
        'headers': {'X-Seznam-Api-Key': 'demo_api_key_12345'}
    },
    'soap': {
        'base_url': 'http://localhost:5001',
        'endpoint': '/BudgetApproval/Service',
        'headers': {'Content-Type': 'text/xml'}
    }
}

class NikeCampaignsAgent:
    def __init__(self, db_path: str = "nike_campaigns.duckdb"):
        self.db_path = db_path
        self.logs = []
        self.pipelines_dir = Path(__file__).parent
        self.driver_manager = DriverManager(self.pipelines_dir)

    def log(self, message: str):
        """Add log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def parse_query(self, query_text: str) -> Dict[str, Any]:
        """
        Parse natural language query to extract intent and requirements

        Returns:
            {
                'intent': 'query' | 'refresh' | 'new_source',
                'sources': ['meta', 'google', 'tiktok', 'soap'],
                'filters': {'date_range': ..., 'budget_min': ..., etc},
                'limit': int,
                'needs_fresh_data': bool
            }
        """
        query_lower = query_text.lower()

        intent = {
            'intent': 'query',
            'sources': [],
            'filters': {},
            'limit': 20,
            'needs_fresh_data': False,
            'scrape_web': False
        }

        # Detect data sources
        if 'meta' in query_lower or 'facebook' in query_lower:
            intent['sources'].append('meta')
        if 'google' in query_lower or 'adwords' in query_lower:
            intent['sources'].append('google')
        if 'tiktok' in query_lower or 'tik tok' in query_lower:
            intent['sources'].append('tiktok')
        if 'seznam' in query_lower or 'czech' in query_lower or 'cz' in query_lower:
            intent['sources'].append('seznam')
        if 'budget' in query_lower or 'soap' in query_lower or 'approval' in query_lower:
            intent['sources'].append('soap')

        # If no specific source mentioned, use all
        if not intent['sources']:
            intent['sources'] = ['meta', 'google', 'tiktok', 'seznam', 'soap']

        # Detect freshness requirements
        if any(word in query_lower for word in ['latest', 'recent', 'fresh', 'new', 'update', 'refresh']):
            intent['needs_fresh_data'] = True

        # Detect web scraping needs
        if any(word in query_lower for word in ['scrape', 'crawl', 'website', 'web']):
            intent['scrape_web'] = True
            intent['intent'] = 'scrape'

        # Extract limit
        limit_match = re.search(r'top\s+(\d+)|(\d+)\s+campaigns?', query_lower)
        if limit_match:
            intent['limit'] = int(limit_match.group(1) or limit_match.group(2))

        # Extract date filters
        if 'december' in query_lower or 'dec' in query_lower:
            intent['filters']['month'] = 12
        if '2024' in query_lower:
            intent['filters']['year'] = 2024
        if '2025' in query_lower:
            intent['filters']['year'] = 2025

        # Extract budget filters
        budget_match = re.search(r'budget\s*[>>=]\s*\$?([\d,]+)', query_lower)
        if budget_match:
            budget_str = budget_match.group(1).replace(',', '')
            intent['filters']['budget_min'] = float(budget_str)

        # Detect sorting
        if any(word in query_lower for word in ['highest', 'largest', 'biggest', 'most expensive']):
            intent['filters']['sort_by'] = 'budget_desc'
        elif any(word in query_lower for word in ['recent', 'newest', 'latest']):
            intent['filters']['sort_by'] = 'date_desc'

        return intent

    def check_data_status(self) -> Dict[str, Any]:
        """
        Check if data exists and when it was last updated

        Returns:
            {
                'exists': bool,
                'tables': list,
                'row_counts': dict,
                'last_updated': datetime | None,
                'is_fresh': bool (< 1 hour old)
            }
        """
        if not os.path.exists(self.db_path):
            return {
                'exists': False,
                'tables': [],
                'row_counts': {},
                'last_updated': None,
                'is_fresh': False
            }

        try:
            conn = duckdb.connect(self.db_path, read_only=True)

            # Get campaign tables from marketing_data schema
            tables = conn.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'marketing_data'
                AND table_name LIKE '%campaigns'
            """).fetchall()

            table_names = [t[0] for t in tables]

            # Get row counts
            row_counts = {}
            for table in table_names:
                count = conn.execute(f"SELECT COUNT(*) FROM marketing_data.{table}").fetchone()[0]
                row_counts[table] = count

            # Check file modification time as proxy for last update
            file_mtime = datetime.fromtimestamp(os.path.getmtime(self.db_path))
            is_fresh = (datetime.now() - file_mtime) < timedelta(hours=1)

            conn.close()

            return {
                'exists': True,
                'tables': table_names,
                'row_counts': row_counts,
                'last_updated': file_mtime,
                'is_fresh': is_fresh
            }

        except Exception as e:
            self.log(f"Error checking data status: {e}")
            return {
                'exists': False,
                'tables': [],
                'row_counts': {},
                'last_updated': None,
                'is_fresh': False
            }

    def check_and_build_drivers(self, sources: List[str]) -> Dict[str, bool]:
        """
        Check if drivers exist for requested sources, build them if missing

        Args:
            sources: List of source names (e.g., ['seznam', 'meta'])

        Returns:
            Dict mapping source name to whether driver exists/was built
        """
        driver_status = {}

        for source in sources:
            # Skip sources we already have hardcoded
            if source in ['meta', 'google', 'tiktok', 'soap']:
                driver_status[source] = True
                continue

            # Check if driver exists
            if self.driver_manager.driver_exists(source):
                self.log(f"✅ Driver for {source} already exists")
                driver_status[source] = True
                continue

            # Try to build driver if API config is known
            if source in API_CONFIGS:
                self.log(f"🔧 Building driver for {source}...")
                config = API_CONFIGS[source]

                success, driver_path, error = self.driver_manager.build_driver(
                    source_name=source,
                    base_url=config['base_url'],
                    endpoint=config['endpoint'],
                    headers=config.get('headers')
                )

                # Log driver manager logs
                for log_msg in self.driver_manager.logs:
                    self.log(log_msg)

                if success:
                    self.log(f"✅ Driver for {source} built successfully: {driver_path}")
                    driver_status[source] = True
                else:
                    self.log(f"❌ Failed to build driver for {source}: {error}")
                    driver_status[source] = False
            else:
                self.log(f"⚠️ No API configuration for {source}")
                driver_status[source] = False

        return driver_status

    def decide_action(self, intent: Dict[str, Any], data_status: Dict[str, Any]) -> str:
        """
        Decide whether to query existing data or build new pipeline

        Returns: 'query' | 'refresh' | 'new_pipeline' | 'scrape'
        """
        # If web scraping is needed
        if intent.get('scrape_web'):
            self.log("🕷️ Query requires web scraping")
            return 'scrape'

        # If no data exists, build pipeline
        if not data_status['exists']:
            self.log("📦 No data found - need to build pipeline")
            return 'refresh'

        # If fresh data explicitly requested and data is stale
        if intent['needs_fresh_data'] and not data_status['is_fresh']:
            self.log("🔄 Fresh data requested and current data is stale")
            return 'refresh'

        # If data exists and is acceptable, query it
        self.log("✅ Data exists and is acceptable - will query")
        return 'query'

    def query_database(self, intent: Dict[str, Any]) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Query the DuckDB database based on intent

        Returns: (results, summary)
        """
        conn = duckdb.connect(self.db_path, read_only=True)

        # Build unified campaigns view with UNION
        union_query = """
            SELECT
                id as campaign_id,
                page_name as campaign_name,
                'meta' as source,
                'Facebook/Instagram' as channel,
                CAST(spend__upper_bound AS DOUBLE) as budget,
                CAST(impressions__upper_bound AS INTEGER) as impressions,
                ad_delivery_start_time as start_date,
                ad_delivery_stop_time as end_date
            FROM marketing_data.meta_campaigns

            UNION ALL

            SELECT
                CAST(id AS VARCHAR) as campaign_id,
                name as campaign_name,
                'google' as source,
                channel,
                budget_micros / 1000000.0 as budget,
                metrics__impressions as impressions,
                start_date,
                end_date
            FROM marketing_data.google_campaigns

            UNION ALL

            SELECT
                campaign_id,
                campaign_name,
                'tiktok' as source,
                'TikTok' as channel,
                CAST(budget AS DOUBLE) as budget,
                COALESCE(TRY_CAST(metrics__impressions AS INTEGER), 0) as impressions,
                start_time as start_date,
                end_time as end_date
            FROM marketing_data.tiktok_campaigns

            UNION ALL

            SELECT
                campaign_id,
                name as campaign_name,
                'seznam' as source,
                channel,
                budget_czk / 25.0 as budget,  -- Convert CZK to USD (~25 CZK/USD)
                COALESCE(total_impressions, 0) as impressions,
                TRY_CAST(created AS TIMESTAMP) as start_date,
                TRY_CAST(updated AS TIMESTAMP) as end_date
            FROM marketing_data.seznam_campaigns

            UNION ALL

            SELECT
                approval_id as campaign_id,
                campaign_name,
                'soap' as source,
                'Budget System' as channel,
                approved_amount as budget,
                0 as impressions,
                TRY_CAST(approval_date AS TIMESTAMP) as start_date,
                NULL as end_date
            FROM marketing_data.budget_approvals
        """

        # Build WHERE clauses
        where_clauses = []

        # Source filtering (fixed: < 5 instead of < 4 to properly detect "all sources")
        if intent['sources'] and len(intent['sources']) < 5:
            sources_str = "', '".join(intent['sources'])
            where_clauses.append(f"source IN ('{sources_str}')")

        # Budget filtering
        if 'budget_min' in intent['filters']:
            where_clauses.append(f"budget >= {intent['filters']['budget_min']}")

        # Date filtering
        if 'month' in intent['filters']:
            where_clauses.append(f"EXTRACT(MONTH FROM start_date) = {intent['filters']['month']}")
        if 'year' in intent['filters']:
            where_clauses.append(f"EXTRACT(YEAR FROM start_date) = {intent['filters']['year']}")

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Sorting
        sort_by = intent['filters'].get('sort_by', 'budget_desc')
        if sort_by == 'budget_desc':
            order_sql = "budget DESC"
        elif sort_by == 'date_desc':
            order_sql = "start_date DESC"
        else:
            order_sql = "budget DESC"

        # Build full query
        query = f"""
            SELECT
                campaign_name,
                source,
                channel,
                budget,
                impressions,
                start_date,
                end_date
            FROM ({union_query})
            WHERE {where_sql}
            ORDER BY {order_sql}
            LIMIT {intent['limit']}
        """

        self.log(f"🔍 Executing SQL query...")
        results = conn.execute(query).fetchdf()

        # Generate summary
        summary_query = f"""
            SELECT
                COUNT(*) as total,
                STRING_AGG(DISTINCT source, ', ' ORDER BY source) as sources,
                STRING_AGG(DISTINCT channel, ', ' ORDER BY channel) as channels,
                SUM(budget) as total_budget,
                SUM(impressions) as total_impressions
            FROM ({union_query})
            WHERE {where_sql}
        """

        summary_row = conn.execute(summary_query).fetchone()
        summary = {
            'total': summary_row[0],
            'sources': summary_row[1].split(', ') if summary_row[1] else [],
            'channels': summary_row[2].split(', ') if summary_row[2] else [],
            'total_budget': float(summary_row[3]) if summary_row[3] else 0,
            'total_impressions': int(summary_row[4]) if summary_row[4] else 0
        }

        conn.close()

        # Convert results to list of dicts
        results_list = results.to_dict('records')

        return results_list, summary

    def refresh_pipeline(self) -> bool:
        """
        Run the data extraction pipeline to refresh data
        """
        import subprocess

        self.log("🔄 Starting data pipeline refresh...")

        try:
            # Activate venv and run pipeline
            venv_python = self.pipelines_dir / "venv" / "bin" / "python"
            pipeline_script = self.pipelines_dir / "nike_campaigns_pipeline.py"

            result = subprocess.run(
                [str(venv_python), str(pipeline_script)],
                cwd=str(self.pipelines_dir),
                capture_output=True,
                text=True,
                timeout=60
            )

            # Log output
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.log(line)

            if result.returncode == 0:
                self.log("✅ Pipeline refresh complete")
                return True
            else:
                self.log(f"❌ Pipeline failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.log("⏱️ Pipeline timed out")
            return False
        except Exception as e:
            self.log(f"❌ Pipeline error: {e}")
            return False

    def execute_query(self, query_text: str) -> Dict[str, Any]:
        """
        Main entry point: execute a natural language query

        Returns:
            {
                'success': bool,
                'action': 'query' | 'refresh' | 'scrape',
                'results': list,
                'summary': dict,
                'logs': list,
                'raw_output': str
            }
        """
        self.logs = []
        self.log(f"📝 Received query: {query_text}")

        # Step 1: Parse query
        intent = self.parse_query(query_text)
        self.log(f"🧠 Parsed intent: {intent['intent']}")
        self.log(f"📊 Data sources: {', '.join(intent['sources'])}")

        # Step 2: Check and build drivers if needed
        self.log(f"🔍 Checking drivers for {len(intent['sources'])} source(s)...")
        driver_status = self.check_and_build_drivers(intent['sources'])

        # If any driver failed to build, warn user
        failed_drivers = [source for source, status in driver_status.items() if not status]
        if failed_drivers:
            self.log(f"⚠️ Could not build drivers for: {', '.join(failed_drivers)}")

        # Step 3: Check data status
        data_status = self.check_data_status()
        if data_status['exists']:
            self.log(f"💾 Found {sum(data_status['row_counts'].values())} total rows")
            self.log(f"⏰ Last updated: {data_status['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.log("⚠️ No data found in database")

        # Step 4: Decide action
        action = self.decide_action(intent, data_status)

        # Step 4: Execute action
        results = []
        summary = {}
        success = True

        if action == 'refresh':
            success = self.refresh_pipeline()
            if success:
                # After refresh, query the data
                results, summary = self.query_database(intent)
                self.log(f"📊 Found {len(results)} campaigns")
            else:
                self.log("❌ Failed to refresh data")

        elif action == 'query':
            results, summary = self.query_database(intent)
            self.log(f"📊 Found {len(results)} campaigns")

        elif action == 'scrape':
            self.log("🕷️ Web scraping not yet implemented - using existing data")
            # TODO: Implement Stagehand scraping
            results, summary = self.query_database(intent)

        # Format output
        raw_output = self._format_results(results, summary)

        return {
            'success': success,
            'action': action,
            'results': results,
            'summary': summary,
            'logs': self.logs,
            'raw_output': raw_output
        }

    def _format_results(self, results: List[Dict], summary: Dict) -> str:
        """Format results as human-readable text"""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("RESULTS:")
        lines.append("="*80)

        if not results:
            lines.append("No campaigns found.")
        else:
            for i, row in enumerate(results, 1):
                lines.append(f"\n{i}. {row.get('campaign_name', 'N/A')}")
                lines.append(f"   Source: {row.get('source', 'N/A')}")
                lines.append(f"   Channel: {row.get('channel', 'N/A')}")
                lines.append(f"   Budget: ${row.get('budget', 0):,.2f}")
                lines.append(f"   Impressions: {row.get('impressions', 0):,}")
                lines.append(f"   Period: {row.get('start_date', 'N/A')} to {row.get('end_date', 'N/A')}")

        lines.append("\n" + "="*80)
        lines.append("SUMMARY:")
        lines.append("="*80)
        lines.append(f"Total: {summary.get('total', 0)} campaigns")
        lines.append(f"Sources: {', '.join(summary.get('sources', []))}")
        lines.append(f"Channels: {', '.join(summary.get('channels', []))}")
        lines.append(f"Total Budget: ${summary.get('total_budget', 0):,.2f}")
        lines.append(f"Total Impressions: {summary.get('total_impressions', 0):,}")
        lines.append("="*80)

        return "\n".join(lines)


def main():
    """CLI interface for testing"""
    if len(sys.argv) < 2:
        print("Usage: python agent.py 'your query here'")
        sys.exit(1)

    query = sys.argv[1]
    agent = NikeCampaignsAgent()
    result = agent.execute_query(query)

    # Print logs
    for log in result['logs']:
        print(log)

    # Print results
    print(result['raw_output'])

    # Exit with status
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
