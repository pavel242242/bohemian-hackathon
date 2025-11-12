#!/usr/bin/env python3
"""
Test script for SOAP Budget Service
Demonstrates how to make SOAP requests and parse responses
"""

import requests
from lxml import etree
import json
from datetime import datetime

# SOAP service URL
SOAP_URL = 'http://localhost:5000/soap/BudgetService'


def pretty_print_xml(xml_string):
    """Pretty print XML string"""
    root = etree.fromstring(xml_string.encode())
    return etree.tostring(root, pretty_print=True, encoding='unicode')


def test_get_campaign_approvals(date_from, date_to):
    """Test GetCampaignApprovals SOAP method"""
    print("\n" + "="*80)
    print(f"TEST: GetCampaignApprovals ({date_from} to {date_to})")
    print("="*80)

    request_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetCampaignApprovals>
            <ns0:date_from>{date_from}</ns0:date_from>
            <ns0:date_to>{date_to}</ns0:date_to>
        </ns0:GetCampaignApprovals>
    </soap-env:Body>
</soap-env:Envelope>"""

    print("\nRequest XML:")
    print(pretty_print_xml(request_xml))

    try:
        response = requests.post(
            SOAP_URL,
            data=request_xml,
            headers={'Content-Type': 'text/xml'},
            timeout=5
        )

        print(f"Response Status: {response.status_code}")
        print("\nResponse XML:")
        print(pretty_print_xml(response.text))

        # Parse response to extract metadata
        root = etree.fromstring(response.content)
        metadata = root.find('.//Metadata')
        if metadata is not None:
            total_records = metadata.findtext('TotalRecords', 'N/A')
            print(f"\nMetadata:")
            print(f"  Total Records: {total_records}")

        return True
    except requests.ConnectionError:
        print("ERROR: Could not connect to SOAP service")
        print("Make sure the service is running: python soap_server.py")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def test_get_approval_by_id(approval_id):
    """Test GetApprovalByID SOAP method"""
    print("\n" + "="*80)
    print(f"TEST: GetApprovalByID ({approval_id})")
    print("="*80)

    request_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalByID>
            <ns0:approval_id>{approval_id}</ns0:approval_id>
        </ns0:GetApprovalByID>
    </soap-env:Body>
</soap-env:Envelope>"""

    print("\nRequest XML:")
    print(pretty_print_xml(request_xml))

    try:
        response = requests.post(
            SOAP_URL,
            data=request_xml,
            headers={'Content-Type': 'text/xml'},
            timeout=5
        )

        print(f"Response Status: {response.status_code}")
        print("\nResponse XML:")
        print(pretty_print_xml(response.text))

        return True
    except requests.ConnectionError:
        print("ERROR: Could not connect to SOAP service")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def test_get_approvals_by_cost_center(cost_center):
    """Test GetApprovalsByCostCenter SOAP method"""
    print("\n" + "="*80)
    print(f"TEST: GetApprovalsByCostCenter ({cost_center})")
    print("="*80)

    request_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalsByCostCenter>
            <ns0:cost_center>{cost_center}</ns0:cost_center>
        </ns0:GetApprovalsByCostCenter>
    </soap-env:Body>
</soap-env:Envelope>"""

    print("\nRequest XML:")
    print(pretty_print_xml(request_xml))

    try:
        response = requests.post(
            SOAP_URL,
            data=request_xml,
            headers={'Content-Type': 'text/xml'},
            timeout=5
        )

        print(f"Response Status: {response.status_code}")
        print("\nResponse XML:")
        print(pretty_print_xml(response.text))

        # Parse response to extract metadata
        root = etree.fromstring(response.content)
        metadata = root.find('.//Metadata')
        if metadata is not None:
            cost_center = metadata.findtext('CostCenter', 'N/A')
            total_records = metadata.findtext('TotalRecords', 'N/A')
            total_amount = metadata.findtext('TotalApprovedAmount', 'N/A')
            print(f"\nMetadata:")
            print(f"  Cost Center: {cost_center}")
            print(f"  Total Records: {total_records}")
            print(f"  Total Approved Amount: {total_amount}")

        return True
    except requests.ConnectionError:
        print("ERROR: Could not connect to SOAP service")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*80)
    print("TEST: Health Check")
    print("="*80)

    try:
        response = requests.get(
            'http://localhost:5000/health',
            timeout=5
        )
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        return True
    except requests.ConnectionError:
        print("ERROR: Could not connect to health check endpoint")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("SOAP Budget Service - Integration Tests")
    print("="*80)
    print(f"Service URL: {SOAP_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")

    # Test 1: Health check
    print("\n[1/4] Testing health check...")
    if not test_health_check():
        print("\nERROR: Service is not running. Start it with: python soap_server.py")
        return

    # Test 2: Get approvals by date range
    print("\n[2/4] Testing GetCampaignApprovals...")
    test_get_campaign_approvals('2025-09-01', '2025-09-30')

    # Test 3: Get approval by ID
    print("\n[3/4] Testing GetApprovalByID...")
    test_get_approval_by_id('APR-006')

    # Test 4: Get approvals by cost center
    print("\n[4/4] Testing GetApprovalsByCostCenter...")
    test_get_approvals_by_cost_center('US-MARKETING-DIGITAL')

    print("\n" + "="*80)
    print("All tests completed!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
