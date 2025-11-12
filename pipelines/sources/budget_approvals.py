"""
SOAP Budget Approval Source
Extracts budget approval data from enterprise SOAP service mock
"""

import dlt
import requests
import xml.etree.ElementTree as ET
from typing import Iterator, Dict, Any


@dlt.resource(
    name="budget_approvals",
    primary_key="ApprovalID",
    write_disposition="merge"
)
def budget_approvals_resource(base_url: str = "http://localhost:5001") -> Iterator[Dict[str, Any]]:
    """
    DLT resource for budget approvals from SOAP service

    Args:
        base_url: Base URL for the SOAP Budget mock server

    Yields:
        Budget approval records
    """
    # For simplicity, use the JSON endpoint instead of parsing SOAP XML
    # In production, would use proper SOAP client
    response = requests.get(f"{base_url}/approvals/json")
    response.raise_for_status()

    data = response.json()
    approvals = data.get("approvals", [])

    for approval in approvals:
        # Transform XML-style field names to snake_case
        yield {
            "approval_id": approval.get("ApprovalID"),
            "campaign_id": approval.get("CampaignID"),
            "campaign_name": approval.get("CampaignName"),
            "approved_amount": float(approval.get("ApprovedAmount", 0)),
            "currency": approval.get("Currency", "USD"),
            "cost_center": approval.get("CostCenter"),
            "approval_date": approval.get("ApprovalDate"),
            "effective_date": approval.get("EffectiveDate"),
            "approver_name": approval.get("ApproverName"),
            "approver_email": approval.get("ApproverEmail"),
            "status": approval.get("Status"),
            "notes": approval.get("Notes"),
        }


@dlt.source
def budget_approvals_source(base_url: str = "http://localhost:5001"):
    """
    Source for budget approvals from SOAP service

    Args:
        base_url: Base URL for the SOAP Budget mock server

    Yields:
        DLT resources with budget approval data
    """
    return budget_approvals_resource(base_url=base_url)


def transform_budget_approval(item: dict) -> dict:
    """
    Transform budget approval to unified format

    Args:
        item: Raw budget approval item

    Returns:
        Transformed approval dict
    """
    return {
        "approval_id": item["approval_id"],
        "campaign_id": item["campaign_id"],
        "source": "soap_budget",
        "approved_budget": item["approved_amount"],
        "approval_date": item["approval_date"],
        "cost_center": item["cost_center"],
        "approver": item["approver_name"],
        "currency": item["currency"],
        "raw_data": item,
    }


if __name__ == "__main__":
    # Quick test
    pipeline = dlt.pipeline(
        pipeline_name="budget_approvals_test",
        destination="duckdb",
        dataset_name="nike_campaigns"
    )

    load_info = pipeline.run(budget_approvals_source())
    print(f"✅ Budget Approvals loaded: {load_info}")
