"""
Application settings and configuration.

This module provides a centralized configuration system that:
- Loads settings from environment variables
- Provides sensible defaults for development
- Supports Azure deployment configuration
- Defines platform thresholds and display settings

Usage:
    from config import settings

    data_dir = settings.data_source.data_directory
    threshold = settings.thresholds.edlap.pipeline_failures.healthy
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DataSourceType(str, Enum):
    """Supported data source types for the dashboard."""
    CSV = "csv"  # Local or mounted CSV files
    AZURE_BLOB = "azure_blob"  # Azure Blob Storage
    DATABRICKS = "databricks"  # Direct Databricks connection


@dataclass(frozen=True)
class ThresholdLevel:
    """Threshold configuration for a single metric."""
    healthy: float
    attention: float
    # Values above attention are considered critical


@dataclass(frozen=True)
class OutlierThreshold:
    """Outlier detection thresholds."""
    warning: float
    critical: float


@dataclass(frozen=True)
class EdlapThresholds:
    """EDLAP platform thresholds."""
    pipeline_failures: ThresholdLevel = field(
        default_factory=lambda: ThresholdLevel(healthy=5, attention=10)
    )
    data_delays: ThresholdLevel = field(
        default_factory=lambda: ThresholdLevel(healthy=15, attention=30)
    )


@dataclass(frozen=True)
class SapbwThresholds:
    """SAP B/W platform thresholds."""
    memory_tb: ThresholdLevel = field(
        default_factory=lambda: ThresholdLevel(healthy=18, attention=22)
    )
    storage_tb: ThresholdLevel = field(
        default_factory=lambda: ThresholdLevel(healthy=55, attention=60)
    )


@dataclass(frozen=True)
class TableauThresholds:
    """Tableau platform thresholds."""
    load_time_sec: ThresholdLevel = field(
        default_factory=lambda: ThresholdLevel(healthy=5, attention=8)
    )
    cpu_percent: ThresholdLevel = field(
        default_factory=lambda: ThresholdLevel(healthy=70, attention=85)
    )


@dataclass(frozen=True)
class AlteryxThresholds:
    """Alteryx platform thresholds."""
    job_failures: ThresholdLevel = field(
        default_factory=lambda: ThresholdLevel(healthy=3, attention=7)
    )
    queue_depth: ThresholdLevel = field(
        default_factory=lambda: ThresholdLevel(healthy=10, attention=20)
    )


@dataclass(frozen=True)
class PlatformThresholds:
    """All platform thresholds."""
    edlap: EdlapThresholds = field(default_factory=EdlapThresholds)
    sapbw: SapbwThresholds = field(default_factory=SapbwThresholds)
    tableau: TableauThresholds = field(default_factory=TableauThresholds)
    alteryx: AlteryxThresholds = field(default_factory=AlteryxThresholds)


@dataclass(frozen=True)
class OutlierThresholds:
    """Outlier detection thresholds for all platforms."""
    edlap_users: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=150, critical=200)
    )
    edlap_pipelines_failed: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=5, critical=10)
    )
    edlap_pipelines_delayed: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=8, critical=15)
    )
    edlap_tickets_overdue: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=5, critical=10)
    )
    sapbw_users: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=80, critical=120)
    )
    sapbw_memory_tb: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=20, critical=22)
    )
    sapbw_load_time_sec: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=8, critical=12)
    )
    sapbw_cpu_percent: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=75, critical=90)
    )
    tableau_users: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=200, critical=300)
    )
    tableau_memory_percent: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=75, critical=90)
    )
    tableau_load_time_sec: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=5, critical=8)
    )
    tableau_cpu_percent: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=70, critical=85)
    )
    alteryx_users: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=50, critical=80)
    )
    alteryx_memory_percent: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=70, critical=85)
    )
    alteryx_load_time_sec: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=120, critical=180)
    )
    alteryx_cpu_percent: OutlierThreshold = field(
        default_factory=lambda: OutlierThreshold(warning=70, critical=85)
    )

    def get_for_platform(self, platform_id: str, metric: str) -> OutlierThreshold:
        """Get outlier threshold for a platform and metric."""
        key = f"{platform_id}_{metric}"
        return getattr(self, key, OutlierThreshold(warning=float("inf"), critical=float("inf")))


@dataclass(frozen=True)
class MachineConfig:
    """Configuration for multi-machine platforms."""
    count: int
    prefix: str


@dataclass(frozen=True)
class MachineConfigs:
    """Machine configurations for all multi-machine platforms."""
    tableau: MachineConfig = field(
        default_factory=lambda: MachineConfig(count=8, prefix="TAB-SRV")
    )
    alteryx: MachineConfig = field(
        default_factory=lambda: MachineConfig(count=8, prefix="ALT-WRK")
    )


@dataclass
class DataSourceConfig:
    """Data source configuration."""
    source_type: DataSourceType = DataSourceType.CSV
    data_directory: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "sample_data")

    # Azure Blob Storage settings (for production)
    azure_storage_account: Optional[str] = None
    azure_container_name: Optional[str] = None
    azure_connection_string: Optional[str] = None

    # Databricks settings (for future use)
    databricks_host: Optional[str] = None
    databricks_token: Optional[str] = None

    # CSV file names
    tickets_file: str = "tickets.csv"
    pipelines_file: str = "pipelines.csv"
    bw_performance_file: str = "bw_system_performance.csv"

    @classmethod
    def from_environment(cls) -> "DataSourceConfig":
        """Create configuration from environment variables."""
        source_type_str = os.environ.get("DATA_SOURCE_TYPE", "csv").lower()
        source_type = DataSourceType(source_type_str) if source_type_str in [e.value for e in DataSourceType] else DataSourceType.CSV

        # Determine data directory
        data_dir_env = os.environ.get("DATA_DIRECTORY")
        if data_dir_env:
            data_directory = Path(data_dir_env)
        else:
            data_directory = Path(__file__).parent.parent.parent / "sample_data"

        return cls(
            source_type=source_type,
            data_directory=data_directory,
            azure_storage_account=os.environ.get("AZURE_STORAGE_ACCOUNT"),
            azure_container_name=os.environ.get("AZURE_CONTAINER_NAME"),
            azure_connection_string=os.environ.get("AZURE_STORAGE_CONNECTION_STRING"),
            databricks_host=os.environ.get("DATABRICKS_HOST"),
            databricks_token=os.environ.get("DATABRICKS_TOKEN"),
            tickets_file=os.environ.get("TICKETS_FILE", "tickets.csv"),
            pipelines_file=os.environ.get("PIPELINES_FILE", "pipelines.csv"),
            bw_performance_file=os.environ.get("BW_PERFORMANCE_FILE", "bw_system_performance.csv"),
        )


@dataclass
class ServiceNowConfig:
    """ServiceNow integration configuration."""
    instance: str = "aldiprod"
    base_url: str = field(init=False)

    def __post_init__(self) -> None:
        self.base_url = f"https://{self.instance}.service-now.com"

    @classmethod
    def from_environment(cls) -> "ServiceNowConfig":
        """Create configuration from environment variables."""
        return cls(
            instance=os.environ.get("SERVICENOW_INSTANCE", "aldiprod")
        )


@dataclass
class DashboardConfig:
    """Dashboard display configuration."""
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8050
    title: str = "Platform Health Dashboard"

    # Performance data generation settings
    default_hours: int = 24
    interval_minutes: int = 5

    # Random seed for reproducible demo data
    demo_random_seed: int = 42

    @classmethod
    def from_environment(cls) -> "DashboardConfig":
        """Create configuration from environment variables."""
        return cls(
            debug=os.environ.get("DASH_DEBUG", "True").lower() == "true",
            host=os.environ.get("DASH_HOST", "0.0.0.0"),
            port=int(os.environ.get("PORT", "8050")),
            title=os.environ.get("DASHBOARD_TITLE", "Platform Health Dashboard"),
        )


@dataclass
class Settings:
    """
    Main application settings container.

    This class aggregates all configuration settings for the application.
    Settings are loaded from environment variables with sensible defaults
    for development.

    Usage:
        from config import settings

        # Access data source settings
        if settings.data_source.source_type == DataSourceType.CSV:
            path = settings.data_source.data_directory / settings.data_source.tickets_file

        # Access thresholds
        if memory > settings.thresholds.sapbw.memory_tb.attention:
            status = "attention"
    """
    environment: Environment = Environment.DEVELOPMENT
    data_source: DataSourceConfig = field(default_factory=DataSourceConfig.from_environment)
    servicenow: ServiceNowConfig = field(default_factory=ServiceNowConfig.from_environment)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig.from_environment)
    thresholds: PlatformThresholds = field(default_factory=PlatformThresholds)
    outlier_thresholds: OutlierThresholds = field(default_factory=OutlierThresholds)
    machine_configs: MachineConfigs = field(default_factory=MachineConfigs)

    @classmethod
    def from_environment(cls) -> "Settings":
        """Create settings from environment variables."""
        env_str = os.environ.get("ENVIRONMENT", "development").lower()
        environment = Environment(env_str) if env_str in [e.value for e in Environment] else Environment.DEVELOPMENT

        return cls(
            environment=environment,
            data_source=DataSourceConfig.from_environment(),
            servicenow=ServiceNowConfig.from_environment(),
            dashboard=DashboardConfig.from_environment(),
        )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT


# Global settings instance - loaded once at module import
settings = Settings.from_environment()
