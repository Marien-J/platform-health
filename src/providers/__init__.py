"""
Data providers for Platform Health Dashboard.

This module provides an abstraction layer for data access, allowing the
dashboard to work with different data sources:

- CSV files (development and Azure with mounted storage)
- Azure Blob Storage (production)
- Databricks (future)

Usage:
    from providers import get_data_provider

    provider = get_data_provider()
    tickets = provider.load_tickets()
    pipelines = provider.load_pipelines()
"""

from .base import DataProvider
from .csv_provider import CSVDataProvider
from .factory import get_data_provider

__all__ = [
    "DataProvider",
    "CSVDataProvider",
    "get_data_provider",
]
