#!/usr/bin/env python3
"""
Simple SOAP Budget Approval Mock Server
Returns XML budget approval data without complex dependencies
"""

from flask import Flask, request, Response
import xml.etree.ElementTree as ET
from datetime import datetime
import os

app = Flask(__name__)

# Load approvals XML
approvals_file = os.path.join(os.path.dirname(__file__), 'approvals.xml')
approvals_tree = ET.parse(approvals_file)
approvals_root = approvals_tree.getroot()

@app.route('/health', methods=['GET'])
def health():
    return {"status": "OK", "service": "soap-budget-mock", "timestamp": datetime.utcnow().isoformat()}

@app.route('/soap/BudgetService', methods=['POST'])
def budget_service():
    """SOAP endpoint for budget approvals"""
    try:
        # Parse incoming SOAP request
        request_data = request.data.decode('utf-8')

        # Extract date range from request (simple parsing)
        date_from = None
        date_to = None

        if 'date_from' in request_data:
            # Simple extraction - in production would use proper SOAP parsing
            import re
            date_from_match = re.search(r'<.*?date_from>(.*?)</', request_data)
            date_to_match = re.search(r'<.*?date_to>(.*?)</', request_data)

            if date_from_match:
                date_from = date_from_match.group(1)
            if date_to_match:
                date_to = date_to_match.group(1)

        # Build response
        response_root = ET.Element('GetCampaignApprovalsResponse')

        # Metadata
        metadata = ET.SubElement(response_root, 'Metadata')
        ET.SubElement(metadata, 'QueryTimestamp').text = datetime.utcnow().isoformat()
        if date_from:
            ET.SubElement(metadata, 'DateFrom').text = date_from
        if date_to:
            ET.SubElement(metadata, 'DateTo').text = date_to

        # Approvals
        approvals_elem = ET.SubElement(response_root, 'Approvals')

        # Filter approvals by date if provided
        count = 0
        for approval in approvals_root.findall('Approval'):
            approval_date_elem = approval.find('ApprovalDate')
            if approval_date_elem is not None:
                approval_date = approval_date_elem.text

                # Simple date filtering
                include = True
                if date_from and approval_date < date_from:
                    include = False
                if date_to and approval_date > date_to:
                    include = False

                if include:
                    approvals_elem.append(approval)
                    count += 1

        ET.SubElement(metadata, 'TotalRecords').text = str(count)

        # Convert to string
        xml_str = ET.tostring(response_root, encoding='utf-8', method='xml')

        return Response(xml_str, mimetype='text/xml')

    except Exception as e:
        # Error response
        error_root = ET.Element('Error')
        ET.SubElement(error_root, 'Message').text = str(e)
        ET.SubElement(error_root, 'Timestamp').text = datetime.utcnow().isoformat()
        xml_str = ET.tostring(error_root, encoding='utf-8', method='xml')
        return Response(xml_str, mimetype='text/xml', status=500)

@app.route('/approvals', methods=['GET'])
def get_approvals():
    """Simple GET endpoint for testing - returns all approvals as XML"""
    xml_str = ET.tostring(approvals_root, encoding='utf-8', method='xml')
    return Response(xml_str, mimetype='text/xml')

@app.route('/approvals/json', methods=['GET'])
def get_approvals_json():
    """JSON endpoint for easier testing"""
    approvals = []
    for approval in approvals_root.findall('Approval'):
        approval_dict = {}
        for child in approval:
            approval_dict[child.tag] = child.text
        approvals.append(approval_dict)

    return {"approvals": approvals, "count": len(approvals)}

if __name__ == '__main__':
    print("Simple SOAP Budget Mock Server")
    print("Running on http://localhost:5001")
    print("")
    print("Endpoints:")
    print("  GET  /health              - Health check")
    print("  POST /soap/BudgetService  - SOAP endpoint")
    print("  GET  /approvals           - All approvals (XML)")
    print("  GET  /approvals/json      - All approvals (JSON)")
    print("")

    app.run(host='0.0.0.0', port=5001, debug=False)
