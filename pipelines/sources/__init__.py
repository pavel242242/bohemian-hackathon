"""
Nike Campaigns Data Sources
All dlthub sources for extracting Nike campaign data from various advertising platforms
"""

from .meta_ads import meta_ads_source, transform_meta_campaign
from .google_ads import google_ads_source, transform_google_campaign
from .tiktok_ads import tiktok_ads_source, transform_tiktok_campaign
from .budget_approvals import budget_approvals_source, transform_budget_approval

__all__ = [
    "meta_ads_source",
    "google_ads_source",
    "tiktok_ads_source",
    "budget_approvals_source",
    "transform_meta_campaign",
    "transform_google_campaign",
    "transform_tiktok_campaign",
    "transform_budget_approval",
]
