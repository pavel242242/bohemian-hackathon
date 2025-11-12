"""
SOAP-based Budget Approval Service Mock
Simulates a legacy enterprise finance system using SOAP/XML
"""

import os
from datetime import datetime
from xml.etree import ElementTree as ET
from flask import Flask
from spyne import Application, rpc, ServiceBase, Unicode, DateTime, Decimal, Integer
from spyne.protocol.soap import Soap11
from spyne.server.flask import FlaskApplication
from lxml import etree


class BudgetApproval:
    """Model for budget approval"""
    def __init__(self, approval_id, campaign_id, campaign_name, approved_amount,
                 currency, cost_center, approval_date, effective_date, approver_name,
                 approver_email, status, notes):
        self.approval_id = approval_id
        self.campaign_id = campaign_id
        self.campaign_name = campaign_name
        self.approved_amount = approved_amount
        self.currency = currency
        self.cost_center = cost_center
        self.approval_date = approval_date
        self.effective_date = effective_date
        self.approver_name = approver_name
        self.approver_email = approver_email
        self.status = status
        self.notes = notes


class BudgetApprovalService(ServiceBase):
    """SOAP service for budget approvals"""

    # Class variable to hold loaded approvals
    _approvals = []

    @classmethod
    def load_approvals(cls):
        """Load budget approvals from XML file"""
        if cls._approvals:
            return

        xml_path = os.path.join(
            os.path.dirname(__file__),
            'approvals.xml'
        )

        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"approvals.xml not found at {xml_path}")

        tree = ET.parse(xml_path)
        root = tree.getroot()

        for approval_elem in root.findall('Approval'):
            approval = BudgetApproval(
                approval_id=approval_elem.findtext('ApprovalID'),
                campaign_id=approval_elem.findtext('CampaignID'),
                campaign_name=approval_elem.findtext('CampaignName'),
                approved_amount=float(approval_elem.findtext('ApprovedAmount', '0')),
                currency=approval_elem.findtext('Currency'),
                cost_center=approval_elem.findtext('CostCenter'),
                approval_date=approval_elem.findtext('ApprovalDate'),
                effective_date=approval_elem.findtext('EffectiveDate'),
                approver_name=approval_elem.findtext('ApproverName'),
                approver_email=approval_elem.findtext('ApproverEmail'),
                status=approval_elem.findtext('Status'),
                notes=approval_elem.findtext('Notes')
            )
            cls._approvals.append(approval)

    @rpc(Unicode, Unicode, _returns=Unicode)
    def GetCampaignApprovals(ctx, date_from, date_to):
        """
        Retrieve campaign budget approvals for a date range.

        Args:
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            XML string containing filtered approvals
        """
        BudgetApprovalService.load_approvals()

        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError as e:
            return f"<Error>Invalid date format. Use YYYY-MM-DD: {str(e)}</Error>"

        # Filter approvals by approval date
        filtered_approvals = [
            approval for approval in BudgetApprovalService._approvals
            if from_date <= datetime.strptime(approval.approval_date, '%Y-%m-%d').date() <= to_date
        ]

        # Build response XML
        root = etree.Element('GetCampaignApprovalsResponse')

        # Add metadata
        metadata = etree.SubElement(root, 'Metadata')
        etree.SubElement(metadata, 'TotalRecords').text = str(len(filtered_approvals))
        etree.SubElement(metadata, 'DateFrom').text = date_from
        etree.SubElement(metadata, 'DateTo').text = date_to
        etree.SubElement(metadata, 'QueryTimestamp').text = datetime.now().isoformat()

        # Add approvals
        approvals_elem = etree.SubElement(root, 'Approvals')

        for approval in filtered_approvals:
            approval_elem = etree.SubElement(approvals_elem, 'Approval')
            etree.SubElement(approval_elem, 'ApprovalID').text = approval.approval_id
            etree.SubElement(approval_elem, 'CampaignID').text = approval.campaign_id
            etree.SubElement(approval_elem, 'CampaignName').text = approval.campaign_name
            etree.SubElement(approval_elem, 'ApprovedAmount').text = str(approval.approved_amount)
            etree.SubElement(approval_elem, 'Currency').text = approval.currency
            etree.SubElement(approval_elem, 'CostCenter').text = approval.cost_center
            etree.SubElement(approval_elem, 'ApprovalDate').text = approval.approval_date
            etree.SubElement(approval_elem, 'EffectiveDate').text = approval.effective_date
            etree.SubElement(approval_elem, 'ApproverName').text = approval.approver_name
            etree.SubElement(approval_elem, 'ApproverEmail').text = approval.approver_email
            etree.SubElement(approval_elem, 'Status').text = approval.status
            etree.SubElement(approval_elem, 'Notes').text = approval.notes

        return etree.tostring(root, pretty_print=True, xml_declaration=True,
                             encoding='UTF-8').decode('utf-8')

    @rpc(Unicode, _returns=Unicode)
    def GetApprovalByID(ctx, approval_id):
        """
        Retrieve a specific approval by ID.

        Args:
            approval_id: The approval ID to retrieve

        Returns:
            XML string containing the approval or error message
        """
        BudgetApprovalService.load_approvals()

        for approval in BudgetApprovalService._approvals:
            if approval.approval_id == approval_id:
                root = etree.Element('GetApprovalByIDResponse')

                approval_elem = etree.SubElement(root, 'Approval')
                etree.SubElement(approval_elem, 'ApprovalID').text = approval.approval_id
                etree.SubElement(approval_elem, 'CampaignID').text = approval.campaign_id
                etree.SubElement(approval_elem, 'CampaignName').text = approval.campaign_name
                etree.SubElement(approval_elem, 'ApprovedAmount').text = str(approval.approved_amount)
                etree.SubElement(approval_elem, 'Currency').text = approval.currency
                etree.SubElement(approval_elem, 'CostCenter').text = approval.cost_center
                etree.SubElement(approval_elem, 'ApprovalDate').text = approval.approval_date
                etree.SubElement(approval_elem, 'EffectiveDate').text = approval.effective_date
                etree.SubElement(approval_elem, 'ApproverName').text = approval.approver_name
                etree.SubElement(approval_elem, 'ApproverEmail').text = approval.approver_email
                etree.SubElement(approval_elem, 'Status').text = approval.status
                etree.SubElement(approval_elem, 'Notes').text = approval.notes

                return etree.tostring(root, pretty_print=True, xml_declaration=True,
                                     encoding='UTF-8').decode('utf-8')

        error_root = etree.Element('Error')
        etree.SubElement(error_root, 'Code').text = 'NOT_FOUND'
        etree.SubElement(error_root, 'Message').text = f'Approval {approval_id} not found'
        return etree.tostring(error_root, pretty_print=True, xml_declaration=True,
                             encoding='UTF-8').decode('utf-8')

    @rpc(Unicode, _returns=Unicode)
    def GetApprovalsByCostCenter(ctx, cost_center):
        """
        Retrieve all approvals for a specific cost center.

        Args:
            cost_center: The cost center code

        Returns:
            XML string containing filtered approvals
        """
        BudgetApprovalService.load_approvals()

        filtered_approvals = [
            approval for approval in BudgetApprovalService._approvals
            if approval.cost_center == cost_center
        ]

        root = etree.Element('GetApprovalsByCostCenterResponse')

        # Add metadata
        metadata = etree.SubElement(root, 'Metadata')
        etree.SubElement(metadata, 'CostCenter').text = cost_center
        etree.SubElement(metadata, 'TotalRecords').text = str(len(filtered_approvals))
        etree.SubElement(metadata, 'TotalApprovedAmount').text = str(
            sum(a.approved_amount for a in filtered_approvals)
        )

        # Add approvals
        approvals_elem = etree.SubElement(root, 'Approvals')

        for approval in filtered_approvals:
            approval_elem = etree.SubElement(approvals_elem, 'Approval')
            etree.SubElement(approval_elem, 'ApprovalID').text = approval.approval_id
            etree.SubElement(approval_elem, 'CampaignID').text = approval.campaign_id
            etree.SubElement(approval_elem, 'CampaignName').text = approval.campaign_name
            etree.SubElement(approval_elem, 'ApprovedAmount').text = str(approval.approved_amount)
            etree.SubElement(approval_elem, 'Currency').text = approval.currency
            etree.SubElement(approval_elem, 'ApprovalDate').text = approval.approval_date
            etree.SubElement(approval_elem, 'EffectiveDate').text = approval.effective_date
            etree.SubElement(approval_elem, 'ApproverName').text = approval.approver_name
            etree.SubElement(approval_elem, 'Status').text = approval.status

        return etree.tostring(root, pretty_print=True, xml_declaration=True,
                             encoding='UTF-8').decode('utf-8')


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config['SOAP_ENCODING'] = 'utf-8'

    # Create SOAP application
    soap_app = Application(
        [BudgetApprovalService],
        tns='http://company.example.com/budget/approval',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )

    # Create Flask SOAP wrapper
    FlaskApplication(soap_app, app, '/soap/BudgetService')

    # Add health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    # Add WSDL endpoint
    @app.route('/soap/BudgetService?wsdl')
    def wsdl():
        return soap_app.get_wsdl(), 200, {'Content-Type': 'application/xml'}

    return app


if __name__ == '__main__':
    app = create_app()
    print("Starting SOAP Budget Service on http://localhost:5000")
    print("WSDL available at: http://localhost:5000/soap/BudgetService?wsdl")
    app.run(debug=True, host='0.0.0.0', port=5000)
