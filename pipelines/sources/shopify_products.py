"""
Shopify Products Source - Dynamically Generated
Shopify Products API
"""

import dlt
from dlt.sources.rest_api import rest_api_source

def shopify_products(
    base_url: str = "https://myshop.myshopify.com/admin/api/2024-01",
    api_key: str = dlt.secrets.value,
) -> Any:
    """
    Load data from Shopify Products

    Args:
        base_url: Base URL for the API
        api_key: API key for authentication

    Returns:
        dlt source with configured resources
    """

    config = {
        "client": {
            "base_url": base_url,
            "auth": {"type": "bearer", "token": api_key},
        },
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "merge",
        },
        "resources": [
            {
                "name": "shopify_products_data",
                "endpoint": {
                    "path": "/data",
                    "params": {},
                    
                    "data_selector": "$",
                },
            }
        ]
    }

    return rest_api_source(config)
