"""
Source Generator Module

Generates dlthub source code from API patterns discovered by APIExplorer.
Supports multiple pagination patterns, authentication, rate limiting, etc.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json


class SourceGenerator:
    def __init__(self, source_name: str, api_patterns: Dict[str, Any]):
        self.source_name = source_name
        self.patterns = api_patterns
        self.resource_name = f"{source_name}_campaigns"

    def generate(self, base_url: str, endpoint: str, headers: Optional[Dict] = None) -> str:
        """
        Generate complete dlthub source code

        Args:
            base_url: Base URL of the API
            endpoint: Main endpoint to extract from
            headers: Optional headers

        Returns:
            Python source code as string
        """
        # Build imports
        imports = self._generate_imports()

        # Build resource decorator
        decorator = self._generate_decorator()

        # Build function signature
        signature = self._generate_signature(base_url, headers)

        # Build function body
        body = self._generate_body(endpoint, headers)

        # Combine all parts
        code = f"""{imports}

{decorator}
{signature}
{body}
"""
        return code

    def _generate_imports(self) -> str:
        """Generate import statements"""
        imports = [
            "import dlt",
            "from dlt.sources.helpers import requests",
            "import time"
        ]

        # Add json import if needed for response unwrapping
        if self.patterns.get('response_format', {}).get('type') == 'wrapped':
            imports.append("import json")

        return "\n".join(imports)

    def _generate_decorator(self) -> str:
        """Generate @dlt.resource decorator"""
        primary_key = self.patterns.get('primary_key', 'id')

        return f'''@dlt.resource(
    name="{self.resource_name}",
    write_disposition="merge",
    primary_key="{primary_key}"
)'''

    def _generate_signature(self, base_url: str, headers: Optional[Dict]) -> str:
        """Generate function signature with parameters"""
        params = [f'base_url: str = "{base_url}"']

        # Add auth parameter if needed
        if headers:
            for key, value in headers.items():
                param_name = key.lower().replace('-', '_').replace('x_', '')
                params.append(f'{param_name}: str = "{value}"')

        params_str = ",\n    ".join(params)

        return f'''def {self.resource_name}(
    {params_str}
):
    """
    Auto-generated dlthub source for {self.source_name}

    Handles:
    - Pagination: {self.patterns.get('pagination', {}).get('type', 'none')}
    - Response format: {self.patterns.get('response_format', {}).get('type', 'standard')}
    - Rate limiting: {'Yes' if self.patterns.get('rate_limiting') else 'No'}
    """'''

    def _generate_body(self, endpoint: str, headers: Optional[Dict]) -> str:
        """Generate function body"""
        lines = []

        # Build headers
        lines.append(self._generate_headers(headers))

        # Add rate limit checking if needed
        if self.patterns.get('rate_limiting'):
            lines.append(self._generate_rate_limit_check())

        # Add pagination loop
        lines.append(self._generate_pagination_loop(endpoint))

        return "\n".join(lines)

    def _generate_headers(self, headers: Optional[Dict]) -> str:
        """Generate headers setup"""
        if not headers:
            return "    headers = {}"

        lines = ["    headers = {"]
        for key, value in headers.items():
            param_name = key.lower().replace('-', '_').replace('x_', '')
            lines.append(f"        '{key}': {param_name},")
        lines.append("    }")

        return "\n".join(lines)

    def _generate_rate_limit_check(self) -> str:
        """Generate rate limit checking function"""
        rl = self.patterns.get('rate_limiting', {})
        remaining_header = rl.get('remaining_header', 'X-RateLimit-Remaining')

        return f'''
    def check_rate_limit(response):
        """Check rate limit headers and sleep if needed"""
        remaining = response.headers.get('{remaining_header}')
        if remaining and int(remaining) < 10:
            print(f"⚠️ Rate limit warning: {{remaining}} requests remaining")
            time.sleep(1)
'''

    def _generate_pagination_loop(self, endpoint: str) -> str:
        """Generate pagination loop based on detected pattern"""
        pagination = self.patterns.get('pagination', {})
        pag_type = pagination.get('type', 'none')

        if pag_type == 'cursor':
            return self._generate_cursor_pagination(endpoint, pagination)
        elif pag_type == 'offset':
            return self._generate_offset_pagination(endpoint, pagination)
        elif pag_type == 'page':
            return self._generate_page_pagination(endpoint, pagination)
        else:
            return self._generate_no_pagination(endpoint)

    def _generate_cursor_pagination(self, endpoint: str, pagination: Dict) -> str:
        """Generate cursor-based pagination"""
        cursor_path = pagination.get('cursor_path', 'cursor')
        has_next_path = pagination.get('has_next_path', 'hasNext')
        data_path = self.patterns.get('data_path', 'data')

        # Handle nested paths
        cursor_get = self._generate_nested_get(cursor_path)
        has_next_get = self._generate_nested_get(has_next_path)
        data_get = self._generate_nested_get(data_path)

        response_check = self._generate_response_check()

        return f'''
    cursor = None
    page = 1

    while True:
        # Build pagination parameters
        params = {{'page': page, 'pageSize': 10}}
        if cursor:
            params['cursor'] = cursor

        # Fetch data
        response = requests.get(
            f"{{base_url}}{endpoint}",
            headers=headers,
            params=params
        )
        response.raise_for_status()
{self._indent(self._generate_rate_limit_call() if self.patterns.get('rate_limiting') else '', 8)}

        data = response.json()

{self._indent(response_check, 8)}

        items = {data_get}

        if not items:
            break

        # Yield each item
        for item in items:
            item['source'] = '{self.source_name}'
            yield item

        # Check for next page
        has_next = {has_next_get}
        if not has_next:
            break

        cursor = {cursor_get}
        page += 1
        time.sleep(0.1)

    print(f"✅ {self.source_name}: Extracted {{page}} pages")
'''

    def _generate_offset_pagination(self, endpoint: str, pagination: Dict) -> str:
        """Generate offset-based pagination"""
        data_path = self.patterns.get('data_path', 'data')
        data_get = self._generate_nested_get(data_path)

        return f'''
    offset = 0
    limit = 100

    while True:
        params = {{'offset': offset, 'limit': limit}}

        response = requests.get(
            f"{{base_url}}{endpoint}",
            headers=headers,
            params=params
        )
        response.raise_for_status()
{self._indent(self._generate_rate_limit_call() if self.patterns.get('rate_limiting') else '', 8)}

        data = response.json()
        items = {data_get}

        if not items:
            break

        for item in items:
            item['source'] = '{self.source_name}'
            yield item

        offset += limit
        time.sleep(0.1)
'''

    def _generate_page_pagination(self, endpoint: str, pagination: Dict) -> str:
        """Generate page-based pagination"""
        next_key = pagination.get('next_key', 'nextPage')
        data_path = self.patterns.get('data_path', 'data')
        data_get = self._generate_nested_get(data_path)

        return f'''
    page = 1

    while True:
        params = {{'page': page, 'per_page': 100}}

        response = requests.get(
            f"{{base_url}}{endpoint}",
            headers=headers,
            params=params
        )
        response.raise_for_status()

        data = response.json()
        items = {data_get}

        if not items:
            break

        for item in items:
            item['source'] = '{self.source_name}'
            yield item

        if not data.get('{next_key}'):
            break

        page += 1
        time.sleep(0.1)
'''

    def _generate_no_pagination(self, endpoint: str) -> str:
        """Generate simple non-paginated extraction"""
        data_path = self.patterns.get('data_path', 'data')
        data_get = self._generate_nested_get(data_path)

        return f'''
    response = requests.get(
        f"{{base_url}}{endpoint}",
        headers=headers
    )
    response.raise_for_status()

    data = response.json()
    items = {data_get}

    for item in items:
        item['source'] = '{self.source_name}'
        yield item
'''

    def _generate_response_check(self) -> str:
        """Generate response validation code"""
        response_format = self.patterns.get('response_format', {})

        if response_format.get('type') == 'wrapped':
            status_path = response_format.get('status_path', 'status')
            status_get = self._generate_nested_get(status_path)

            return f'''# Check response status
        status = {status_get}
        if status != 'SUCCESS':
            error = data.get('responseMetadata', {{}}).get('message', 'Unknown error')
            raise Exception(f"API error: {{error}}")'''

        return ""

    def _generate_rate_limit_call(self) -> str:
        """Generate call to rate limit check"""
        return "check_rate_limit(response)"

    def _generate_nested_get(self, path: str) -> str:
        """Generate nested .get() calls for path like 'data.campaigns'"""
        if path == '$':
            return "data"

        parts = path.split('.')
        result = "data"

        for part in parts:
            result += f".get('{part}', {{}})"

        return result

    def _indent(self, text: str, spaces: int) -> str:
        """Indent text by N spaces"""
        if not text:
            return ""
        indent = " " * spaces
        return "\n".join(indent + line if line.strip() else line for line in text.split('\n'))


def generate_source_file(
    source_name: str,
    base_url: str,
    endpoint: str,
    api_patterns: Dict[str, Any],
    output_path: Path,
    headers: Optional[Dict] = None
) -> Path:
    """
    Generate a complete dlthub source file

    Args:
        source_name: Name of the source (e.g., 'seznam')
        base_url: Base URL of the API
        endpoint: Main endpoint to extract from
        api_patterns: Patterns discovered by APIExplorer
        output_path: Path to write the source file
        headers: Optional headers

    Returns:
        Path to generated file
    """
    generator = SourceGenerator(source_name, api_patterns)
    code = generator.generate(base_url, endpoint, headers)

    output_path.write_text(code)
    print(f"✅ Generated source file: {output_path}")

    return output_path
