"""
API Explorer Module

Discovers API patterns by calling endpoints and analyzing responses:
- Authentication methods
- Pagination patterns
- Response structure
- Rate limiting
- Data nesting
"""

import requests
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin


class APIExplorer:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.findings = {
            'auth': None,
            'pagination': None,
            'response_format': None,
            'rate_limiting': None,
            'endpoints': []
        }

    def explore(self, initial_endpoint: str = "/", headers: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main exploration method

        Args:
            initial_endpoint: Starting endpoint to explore
            headers: Optional headers (e.g., auth headers)

        Returns:
            Dictionary with API patterns discovered
        """
        self.findings['endpoints'] = []

        # Try initial endpoint
        response = self._try_endpoint(initial_endpoint, headers)

        if response:
            # Detect response format
            self.findings['response_format'] = self._detect_response_format(response)

            # Detect pagination
            self.findings['pagination'] = self._detect_pagination(response)

            # Detect rate limiting
            self.findings['rate_limiting'] = self._detect_rate_limiting(response)

            # Extract data path
            self.findings['data_path'] = self._find_data_path(response)

            # Detect primary key
            self.findings['primary_key'] = self._detect_primary_key(response)

        return self.findings

    def _try_endpoint(self, endpoint: str, headers: Optional[Dict] = None) -> Optional[requests.Response]:
        """Try calling an endpoint"""
        url = urljoin(self.base_url, endpoint)

        try:
            response = requests.get(url, headers=headers or {}, timeout=10)

            self.findings['endpoints'].append({
                'path': endpoint,
                'status': response.status_code,
                'success': response.status_code == 200
            })

            if response.status_code == 200:
                return response
            elif response.status_code == 401:
                self.findings['auth'] = 'required'

            return None
        except Exception as e:
            print(f"Error trying {url}: {e}")
            return None

    def _detect_response_format(self, response: requests.Response) -> Dict[str, Any]:
        """Detect non-standard response wrapping"""
        try:
            data = response.json()

            # Check for common wrapper patterns
            if isinstance(data, dict):
                # Pattern: { responseMetadata: {...}, data: {...} }
                if 'responseMetadata' in data or 'response_metadata' in data:
                    return {
                        'type': 'wrapped',
                        'wrapper_keys': ['responseMetadata', 'data'],
                        'status_path': 'responseMetadata.status'
                    }

                # Pattern: { meta: {...}, data: {...} }
                if 'meta' in data and 'data' in data:
                    return {
                        'type': 'wrapped',
                        'wrapper_keys': ['meta', 'data'],
                        'status_path': 'meta.status'
                    }

                # Pattern: { success: bool, result: {...} }
                if 'success' in data and 'result' in data:
                    return {
                        'type': 'wrapped',
                        'wrapper_keys': ['success', 'result'],
                        'status_path': 'success'
                    }

                # Standard format
                return {'type': 'standard'}

            return {'type': 'standard'}
        except:
            return {'type': 'unknown'}

    def _detect_pagination(self, response: requests.Response) -> Dict[str, Any]:
        """Detect pagination pattern"""
        try:
            data = response.json()

            if isinstance(data, dict):
                # Cursor-based pagination
                if 'cursor' in data or 'nextCursor' in data:
                    return {
                        'type': 'cursor',
                        'cursor_key': 'nextCursor' if 'nextCursor' in data else 'cursor'
                    }

                # Check nested pagination
                if 'pagination' in data:
                    pag = data['pagination']
                    if 'navigation' in pag and 'nextCursor' in pag['navigation']:
                        return {
                            'type': 'cursor',
                            'cursor_path': 'pagination.navigation.nextCursor',
                            'has_next_path': 'pagination.navigation.hasNext'
                        }

                # Offset-based pagination
                if 'offset' in data or 'page' in data:
                    return {
                        'type': 'offset',
                        'offset_key': 'offset' if 'offset' in data else 'page'
                    }

                # Page-based pagination
                if 'next_page' in data or 'nextPage' in data:
                    return {
                        'type': 'page',
                        'next_key': 'nextPage' if 'nextPage' in data else 'next_page'
                    }

            return {'type': 'none'}
        except:
            return {'type': 'unknown'}

    def _detect_rate_limiting(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """Detect rate limiting headers"""
        headers = response.headers

        rate_limit_headers = {}

        # Check for common rate limit headers
        if 'X-RateLimit-Limit' in headers:
            rate_limit_headers['limit_header'] = 'X-RateLimit-Limit'
            rate_limit_headers['remaining_header'] = 'X-RateLimit-Remaining'
            rate_limit_headers['reset_header'] = 'X-RateLimit-Reset'
            return rate_limit_headers

        if 'RateLimit-Limit' in headers:
            rate_limit_headers['limit_header'] = 'RateLimit-Limit'
            rate_limit_headers['remaining_header'] = 'RateLimit-Remaining'
            return rate_limit_headers

        return None

    def _find_data_path(self, response: requests.Response) -> Optional[str]:
        """Find where the actual data array/list is in the response"""
        try:
            data = response.json()

            if isinstance(data, list):
                return '$'  # Root is the data

            if isinstance(data, dict):
                # Check common data keys
                for key in ['data', 'results', 'items', 'records']:
                    if key in data:
                        # Check if it's nested further
                        inner = data[key]
                        if isinstance(inner, list):
                            return key
                        elif isinstance(inner, dict):
                            # Check for nested data
                            for inner_key in ['campaigns', 'items', 'results']:
                                if inner_key in inner and isinstance(inner[inner_key], list):
                                    return f"{key}.{inner_key}"
                            return key

                # If no standard key, look for any list
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        return key
                    elif isinstance(value, dict):
                        for inner_key, inner_value in value.items():
                            if isinstance(inner_value, list) and len(inner_value) > 0:
                                return f"{key}.{inner_key}"

            return None
        except:
            return None

    def _detect_primary_key(self, response: requests.Response) -> Optional[str]:
        """Detect likely primary key field"""
        try:
            data = response.json()

            # Navigate to data items
            items = self._extract_items(data)

            if items and len(items) > 0:
                first_item = items[0]

                # Check for common ID patterns
                for key in ['id', 'ID', '_id', 'uuid', 'campaignId', 'campaign_id']:
                    if key in first_item:
                        return key

                # Look for any field with 'id' in name
                for key in first_item.keys():
                    if 'id' in key.lower():
                        return key

            return 'id'  # Default
        except:
            return 'id'

    def _extract_items(self, data: Any) -> Optional[List]:
        """Extract list of items from response"""
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in ['data', 'results', 'items', 'records']:
                if key in data:
                    inner = data[key]
                    if isinstance(inner, list):
                        return inner
                    elif isinstance(inner, dict):
                        for inner_key in ['campaigns', 'items', 'results']:
                            if inner_key in inner and isinstance(inner[inner_key], list):
                                return inner[inner_key]

            # Look for any list
            for value in data.values():
                if isinstance(value, list) and len(value) > 0:
                    return value

        return None


def explore_api(base_url: str, endpoint: str = "/", headers: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Convenience function to explore an API

    Args:
        base_url: Base URL of the API
        endpoint: Starting endpoint
        headers: Optional headers

    Returns:
        API patterns discovered
    """
    explorer = APIExplorer(base_url)
    return explorer.explore(endpoint, headers)
