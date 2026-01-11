"""
Data provider factory.

This module provides a factory function to create the appropriate
data provider based on configuration settings.
"""

import logging

from config import settings, DataSourceType

from .base import DataProvider
from .csv_provider import CSVDataProvider

logger = logging.getLogger(__name__)

# Cached provider instance for reuse
_provider_instance: DataProvider | None = None


def get_data_provider(force_new: bool = False) -> DataProvider:
    """
    Get a data provider instance based on current configuration.

    This factory function creates the appropriate data provider based on
    the DATA_SOURCE_TYPE environment variable. It caches the provider
    instance for efficiency.

    Args:
        force_new: If True, create a new instance even if one is cached

    Returns:
        A DataProvider instance appropriate for the current configuration

    Raises:
        ValueError: If the configured data source type is not supported

    Example:
        # Get the default provider
        provider = get_data_provider()
        tickets = provider.load_tickets()

        # Force a new provider instance
        provider = get_data_provider(force_new=True)
    """
    global _provider_instance

    if _provider_instance is not None and not force_new:
        return _provider_instance

    source_type = settings.data_source.source_type

    if source_type == DataSourceType.CSV:
        _provider_instance = CSVDataProvider()
        logger.info("Created CSV data provider")

    elif source_type == DataSourceType.AZURE_BLOB:
        # For Azure Blob Storage, we can still use CSV provider with a
        # mounted blob container. The blob is mounted via FUSE or similar.
        # For direct blob access, implement AzureBlobProvider in the future.
        logger.info(
            "Azure Blob configured - using CSV provider with mounted storage"
        )
        _provider_instance = CSVDataProvider()

    elif source_type == DataSourceType.DATABRICKS:
        # Future: Implement DatabricksProvider for direct connection
        logger.warning(
            "Databricks provider not yet implemented, falling back to CSV"
        )
        _provider_instance = CSVDataProvider()

    else:
        raise ValueError(f"Unsupported data source type: {source_type}")

    # Log provider info
    logger.info(f"Data provider initialized:\n{_provider_instance.get_source_info()}")

    return _provider_instance


def reset_provider() -> None:
    """
    Reset the cached provider instance.

    Use this to force re-initialization of the provider, for example
    after configuration changes or for testing.
    """
    global _provider_instance
    _provider_instance = None
    logger.debug("Data provider cache reset")
