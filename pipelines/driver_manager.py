"""
Driver Manager Module

Manages dynamic driver generation with iterative refinement:
1. Generates driver code
2. Tests it
3. Analyzes errors
4. Refines code
5. Retries until it works
"""

import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import traceback
import re

from api_explorer import explore_api
from source_generator import generate_source_file


class DriverManager:
    def __init__(self, pipelines_dir: Path):
        self.pipelines_dir = pipelines_dir
        self.sources_dir = pipelines_dir / "sources"
        self.max_attempts = 3
        self.logs = []

    def log(self, message: str):
        """Log a message"""
        self.logs.append(message)
        print(message)

    def build_driver(
        self,
        source_name: str,
        base_url: str,
        endpoint: str,
        headers: Optional[Dict] = None
    ) -> Tuple[bool, Optional[Path], str]:
        """
        Build a working driver through iterative refinement

        Args:
            source_name: Name of the source
            base_url: Base URL of the API
            endpoint: Main endpoint
            headers: Optional headers

        Returns:
            (success, driver_path, error_message)
        """
        self.logs = []
        self.log(f"🔧 Building driver for {source_name}...")

        # Step 1: Explore API
        self.log("🔍 Exploring API...")
        try:
            api_patterns = explore_api(base_url, endpoint, headers)
            self.log(f"✅ API exploration complete")
            self.log(f"  - Pagination: {api_patterns.get('pagination', {}).get('type', 'none')}")
            self.log(f"  - Response format: {api_patterns.get('response_format', {}).get('type', 'standard')}")
            self.log(f"  - Rate limiting: {'Yes' if api_patterns.get('rate_limiting') else 'No'}")
            self.log(f"  - Data path: {api_patterns.get('data_path', 'unknown')}")
            self.log(f"  - Primary key: {api_patterns.get('primary_key', 'id')}")
        except Exception as e:
            error = f"Failed to explore API: {e}"
            self.log(f"❌ {error}")
            return False, None, error

        # Step 2: Generate driver iteratively
        for attempt in range(1, self.max_attempts + 1):
            self.log(f"\n📝 Attempt {attempt}/{self.max_attempts}: Generating driver...")

            try:
                # Generate source file
                driver_path = self.sources_dir / f"{source_name}_ads.py"
                generate_source_file(
                    source_name=source_name,
                    base_url=base_url,
                    endpoint=endpoint,
                    api_patterns=api_patterns,
                    output_path=driver_path,
                    headers=headers
                )

                self.log(f"✅ Driver generated: {driver_path}")

                # Step 3: Test the driver
                self.log("🧪 Testing driver...")
                success, error = self._test_driver(source_name, driver_path)

                if success:
                    self.log(f"✅ Driver works! Extracted data successfully")
                    return True, driver_path, None

                # Step 4: Analyze error and refine
                self.log(f"⚠️ Driver failed: {error}")

                if attempt < self.max_attempts:
                    self.log(f"🔄 Refining driver based on error...")
                    api_patterns = self._refine_patterns(api_patterns, error)
                else:
                    self.log(f"❌ Max attempts reached")
                    return False, driver_path, error

            except Exception as e:
                error = f"Driver generation failed: {e}\n{traceback.format_exc()}"
                self.log(f"❌ {error}")

                if attempt >= self.max_attempts:
                    return False, None, error

        return False, None, "Max attempts reached without success"

    def _test_driver(self, source_name: str, driver_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Test the generated driver by importing and running it

        Returns:
            (success, error_message)
        """
        try:
            # Import the module dynamically
            spec = importlib.util.spec_from_file_location(f"sources.{source_name}_ads", driver_path)
            if not spec or not spec.loader:
                return False, "Could not load module spec"

            module = importlib.util.module_from_spec(spec)
            sys.modules[f"sources.{source_name}_ads"] = module
            spec.loader.exec_module(module)

            # Get the resource function
            resource_func = getattr(module, f"{source_name}_campaigns", None)
            if not resource_func:
                return False, f"Could not find {source_name}_campaigns function"

            # Try to call it and get first few items
            self.log("  - Calling resource function...")
            resource = resource_func()

            items_count = 0
            for item in resource:
                items_count += 1
                if items_count >= 3:  # Test with first 3 items
                    break

            if items_count == 0:
                return False, "No items returned from resource"

            self.log(f"  - Successfully extracted {items_count} items")
            return True, None

        except Exception as e:
            error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return False, error

    def _refine_patterns(self, api_patterns: Dict[str, Any], error: str) -> Dict[str, Any]:
        """
        Refine API patterns based on error

        This implements self-healing by adjusting patterns when errors occur
        """
        refined = api_patterns.copy()

        # Common error patterns and fixes
        if "KeyError" in error or "not found" in error.lower():
            # Try to extract the missing key from error
            key_match = re.search(r"['\"]([\w_]+)['\"]", error)
            if key_match:
                missing_key = key_match.group(1)
                self.log(f"  - Detected missing key: {missing_key}")

                # Adjust data path if key is missing
                if refined.get('data_path'):
                    # Try alternative paths
                    alternatives = ['data', 'results', 'items', 'records', '$']
                    current_path = refined['data_path']
                    for alt in alternatives:
                        if alt != current_path:
                            refined['data_path'] = alt
                            self.log(f"  - Trying alternative data path: {alt}")
                            break

        if "AttributeError" in error or "object has no attribute" in error:
            # Response structure is different than expected
            self.log("  - Detected structure mismatch")

            # Try simpler response format
            if refined.get('response_format', {}).get('type') == 'wrapped':
                refined['response_format'] = {'type': 'standard'}
                self.log("  - Simplified response format to standard")

        if "401" in error or "403" in error or "Unauthorized" in error:
            self.log("  - Detected authentication issue")
            refined['auth'] = 'required'

        if "pagination" in error.lower() or "cursor" in error.lower():
            self.log("  - Detected pagination issue")

            # Try simpler pagination
            if refined.get('pagination', {}).get('type') == 'cursor':
                refined['pagination'] = {'type': 'none'}
                self.log("  - Disabled pagination for simpler extraction")

        return refined

    def load_driver(self, source_name: str) -> Optional[Any]:
        """
        Load an existing driver module

        Returns:
            The resource function or None
        """
        driver_path = self.sources_dir / f"{source_name}_ads.py"

        if not driver_path.exists():
            return None

        try:
            spec = importlib.util.spec_from_file_location(f"sources.{source_name}_ads", driver_path)
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[f"sources.{source_name}_ads"] = module
            spec.loader.exec_module(module)

            resource_func = getattr(module, f"{source_name}_campaigns", None)
            return resource_func

        except Exception as e:
            self.log(f"Failed to load driver: {e}")
            return None

    def driver_exists(self, source_name: str) -> bool:
        """Check if driver already exists"""
        driver_path = self.sources_dir / f"{source_name}_ads.py"
        return driver_path.exists()


def build_and_test_driver(
    source_name: str,
    base_url: str,
    endpoint: str,
    headers: Optional[Dict] = None,
    pipelines_dir: Path = Path(__file__).parent
) -> Tuple[bool, Optional[Path], str]:
    """
    Convenience function to build and test a driver

    Returns:
        (success, driver_path, logs)
    """
    manager = DriverManager(pipelines_dir)
    success, driver_path, error = manager.build_driver(source_name, base_url, endpoint, headers)

    logs = "\n".join(manager.logs)

    if success:
        return True, driver_path, logs
    else:
        return False, driver_path, logs + f"\n\nError: {error}"
