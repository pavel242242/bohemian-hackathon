"""
Source Templates for Dynamic dlthub Source Generation

This module contains templates for generating dlthub sources dynamically
based on user queries and requirements.
"""

from typing import Dict, Any, List

# Template for REST API sources (most common)
REST_API_TEMPLATE = '''"""
{source_name} Source - Dynamically Generated
{description}
"""

import dlt
from dlt.sources.rest_api import rest_api_source

def {function_name}(
    base_url: str = "{default_base_url}",
    api_key: str = dlt.secrets.value,
) -> Any:
    """
    Load data from {source_name}

    Args:
        base_url: Base URL for the API
        api_key: API key for authentication

    Returns:
        dlt source with configured resources
    """

    config = {{
        "client": {{
            "base_url": base_url,
            {auth_config}
        }},
        "resource_defaults": {{
            "primary_key": "{primary_key}",
            "write_disposition": "merge",
        }},
        "resources": [
            {{
                "name": "{resource_name}",
                "endpoint": {{
                    "path": "{endpoint_path}",
                    {endpoint_params}
                    "data_selector": "$",
                }},
            }}
        ]
    }}

    return rest_api_source(config)
'''

# Template for SOAP sources
SOAP_TEMPLATE = '''"""
{source_name} SOAP Source - Dynamically Generated
{description}
"""

import dlt
from dlt.sources.helpers import requests
import xmltodict

@dlt.resource(
    name="{resource_name}",
    write_disposition="merge",
    primary_key="{primary_key}"
)
def {function_name}(
    wsdl_url: str = "{default_wsdl_url}",
):
    """
    Load data from {source_name} SOAP service

    Args:
        wsdl_url: WSDL URL for the SOAP service

    Yields:
        Records from the SOAP service
    """

    # SOAP envelope
    envelope = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            {soap_action}
        </soap:Body>
    </soap:Envelope>"""

    headers = {{
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': '"{soap_action_header}"'
    }}

    response = requests.post(wsdl_url, data=envelope, headers=headers)
    response.raise_for_status()

    # Parse XML response
    data = xmltodict.parse(response.content)

    # Extract data from response
    records = data.get('{response_path}', [])
    if not isinstance(records, list):
        records = [records]

    yield from records
'''

# Template for GraphQL sources
GRAPHQL_TEMPLATE = '''"""
{source_name} GraphQL Source - Dynamically Generated
{description}
"""

import dlt
from dlt.sources.helpers import requests

@dlt.resource(
    name="{resource_name}",
    write_disposition="merge",
    primary_key="{primary_key}"
)
def {function_name}(
    graphql_url: str = "{default_graphql_url}",
    api_key: str = dlt.secrets.value,
):
    """
    Load data from {source_name} GraphQL API

    Args:
        graphql_url: GraphQL endpoint URL
        api_key: API key for authentication

    Yields:
        Records from the GraphQL API
    """

    query = """
    {graphql_query}
    """

    headers = {{
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {{api_key}}'
    }}

    payload = {{
        'query': query
    }}

    response = requests.post(graphql_url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    records = data.get('data', {{}}).get('{data_path}', [])

    yield from records
'''


class SourceTemplate:
    """Represents a source template with its configuration"""

    def __init__(
        self,
        name: str,
        template: str,
        required_params: List[str],
        optional_params: Dict[str, Any] = None
    ):
        self.name = name
        self.template = template
        self.required_params = required_params
        self.optional_params = optional_params or {}

    def generate(self, params: Dict[str, Any]) -> str:
        """
        Generate source code from template with given parameters

        Args:
            params: Parameters to fill in the template

        Returns:
            Generated Python source code
        """
        # Merge with defaults
        all_params = {**self.optional_params, **params}

        # Validate required params
        missing = set(self.required_params) - set(all_params.keys())
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")

        # Generate source code
        return self.template.format(**all_params)


# Available templates
TEMPLATES = {
    'rest_api': SourceTemplate(
        name='REST API',
        template=REST_API_TEMPLATE,
        required_params=[
            'source_name',
            'function_name',
            'resource_name',
            'endpoint_path',
            'primary_key'
        ],
        optional_params={
            'description': 'REST API data source',
            'default_base_url': 'http://localhost:8000',
            'auth_config': '"auth": {"type": "bearer", "token": api_key},',
            'endpoint_params': '"params": {},\n                    ',
        }
    ),

    'soap': SourceTemplate(
        name='SOAP',
        template=SOAP_TEMPLATE,
        required_params=[
            'source_name',
            'function_name',
            'resource_name',
            'soap_action',
            'soap_action_header',
            'response_path',
            'primary_key'
        ],
        optional_params={
            'description': 'SOAP web service data source',
            'default_wsdl_url': 'http://localhost:5001/soap',
        }
    ),

    'graphql': SourceTemplate(
        name='GraphQL',
        template=GRAPHQL_TEMPLATE,
        required_params=[
            'source_name',
            'function_name',
            'resource_name',
            'graphql_query',
            'data_path',
            'primary_key'
        ],
        optional_params={
            'description': 'GraphQL API data source',
            'default_graphql_url': 'http://localhost:4000/graphql',
        }
    ),
}


def get_template(template_type: str) -> SourceTemplate:
    """
    Get a source template by type

    Args:
        template_type: Type of template ('rest_api', 'soap', 'graphql')

    Returns:
        SourceTemplate instance

    Raises:
        ValueError: If template type not found
    """
    if template_type not in TEMPLATES:
        raise ValueError(f"Unknown template type: {template_type}. Available: {list(TEMPLATES.keys())}")

    return TEMPLATES[template_type]


def list_templates() -> List[str]:
    """List available template types"""
    return list(TEMPLATES.keys())
