"""
Configuration module for Platform Health Dashboard.

This module provides centralized configuration management with support for:
- Environment-specific settings (development, production)
- Data source configuration (CSV, Azure Blob Storage, Databricks)
- Platform thresholds and display settings

Usage:
    from config import settings, DataSourceType

    if settings.data_source.source_type == DataSourceType.CSV:
        path = settings.data_source.data_directory / settings.data_source.tickets_file
"""

from .settings import (
    DataSourceConfig,
    DataSourceType,
    DashboardConfig,
    Environment,
    MachineConfig,
    MachineConfigs,
    OutlierThreshold,
    OutlierThresholds,
    PlatformThresholds,
    ServiceNowConfig,
    Settings,
    ThresholdLevel,
    settings,
)

__all__ = [
    "DataSourceConfig",
    "DataSourceType",
    "DashboardConfig",
    "Environment",
    "MachineConfig",
    "MachineConfigs",
    "OutlierThreshold",
    "OutlierThresholds",
    "PlatformThresholds",
    "ServiceNowConfig",
    "Settings",
    "ThresholdLevel",
    "settings",
]
