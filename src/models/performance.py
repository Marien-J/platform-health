"""
Performance data models.

Defines models for time-series performance data, metrics, and statistics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class OutlierSeverity(str, Enum):
    """Severity levels for outlier detection."""

    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Outlier:
    """
    Represents a detected outlier in a time series.

    Attributes:
        index: Position in the time series
        value: The outlier value
        severity: How severe the outlier is
    """

    index: int
    value: float
    severity: OutlierSeverity

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "value": self.value,
            "severity": self.severity.value,
        }


@dataclass
class MetricWithOutliers:
    """
    A metric time series with detected outliers.

    Attributes:
        values: List of metric values
        outliers: List of detected outliers
    """

    values: List[float] = field(default_factory=list)
    outliers: List[Outlier] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for Dash components."""
        return {
            "values": self.values,
            "outliers": [o.to_dict() for o in self.outliers],
        }


@dataclass
class HistoricalStats:
    """
    Historical statistics for a metric.

    Attributes:
        average: Average value over the period
        peak: Maximum value over the period
    """

    average: float
    peak: float

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "average": self.average,
            "peak": self.peak,
        }


@dataclass
class PipelineSummary:
    """
    Summary of pipeline statuses for a platform.

    Attributes:
        successful: Number of successful pipelines
        delayed: Number of delayed pipelines
        failed: Number of failed pipelines
        not_applicable: Number of not applicable pipelines
        total: Total number of pipelines
    """

    successful: int = 0
    delayed: int = 0
    failed: int = 0
    not_applicable: int = 0

    @property
    def total(self) -> int:
        """Calculate total pipelines."""
        return self.successful + self.delayed + self.failed + self.not_applicable

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "successful": self.successful,
            "delayed": self.delayed,
            "failed": self.failed,
            "not_applicable": self.not_applicable,
            "total": self.total,
        }


@dataclass
class TicketHistory:
    """
    Historical ticket data for line graphs.

    Attributes:
        timestamps: List of date strings
        open_tickets: Time series of open ticket counts
        overdue_tickets: Time series of overdue ticket counts
        current_count: Current open ticket count
        breached_count: Current breached ticket count
    """

    timestamps: List[str] = field(default_factory=list)
    open_tickets: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    overdue_tickets: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    current_count: int = 0
    breached_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for Dash components."""
        return {
            "timestamps": self.timestamps,
            "open_tickets": self.open_tickets.to_dict(),
            "overdue_tickets": self.overdue_tickets.to_dict(),
            "current_count": self.current_count,
            "breached_count": self.breached_count,
        }


@dataclass
class PerformanceData:
    """
    Base class for platform performance data.

    This contains common fields shared across all platforms.
    """

    timestamps: List[str] = field(default_factory=list)
    users: MetricWithOutliers = field(default_factory=MetricWithOutliers)

    def to_dict(self) -> dict:
        """Convert to dictionary for Dash components."""
        return {
            "timestamps": self.timestamps,
            "users": self.users.to_dict(),
        }


@dataclass
class EdlapPerformanceData(PerformanceData):
    """
    EDLAP-specific performance data.

    Additional metrics:
        total_pipelines: Total pipeline count over time
        failed_pipelines: Failed pipeline count over time
        delayed_pipelines: Delayed pipeline count over time
        open_tickets: Open ticket count over time
        overdue_tickets: Overdue ticket count over time
    """

    total_pipelines: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    failed_pipelines: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    delayed_pipelines: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    open_tickets: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    overdue_tickets: MetricWithOutliers = field(default_factory=MetricWithOutliers)

    def to_dict(self) -> dict:
        """Convert to dictionary for Dash components."""
        base = super().to_dict()
        base.update(
            {
                "total_pipelines": self.total_pipelines.to_dict(),
                "failed_pipelines": self.failed_pipelines.to_dict(),
                "delayed_pipelines": self.delayed_pipelines.to_dict(),
                "open_tickets": self.open_tickets.to_dict(),
                "overdue_tickets": self.overdue_tickets.to_dict(),
            }
        )
        return base


@dataclass
class SapbwPerformanceData(PerformanceData):
    """
    SAP B/W-specific performance data.

    Additional metrics:
        memory_tb: Memory usage in TB
        memory_capacity: Maximum memory capacity in TB
        load_time_sec: Dashboard load time in seconds
        cpu_percent: CPU utilization percentage
    """

    memory_tb: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    memory_capacity: float = 24.0
    load_time_sec: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    cpu_percent: MetricWithOutliers = field(default_factory=MetricWithOutliers)

    def to_dict(self) -> dict:
        """Convert to dictionary for Dash components."""
        base = super().to_dict()
        base.update(
            {
                "memory_tb": self.memory_tb.to_dict(),
                "memory_capacity": self.memory_capacity,
                "load_time_sec": self.load_time_sec.to_dict(),
                "cpu_percent": self.cpu_percent.to_dict(),
            }
        )
        return base


@dataclass
class MachineData:
    """
    Performance data for a single machine.

    Used for multi-machine platforms (Tableau, Alteryx).
    """

    users: List[float] = field(default_factory=list)
    memory_percent: List[float] = field(default_factory=list)
    cpu_percent: List[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "users": self.users,
            "memory_percent": self.memory_percent,
            "cpu_percent": self.cpu_percent,
        }


@dataclass
class MachineOutliers:
    """Outliers detected for a single machine."""

    memory: List[Outlier] = field(default_factory=list)
    cpu: List[Outlier] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "memory": [o.to_dict() for o in self.memory],
            "cpu": [o.to_dict() for o in self.cpu],
        }


@dataclass
class AggregatedMetrics:
    """
    Aggregated metrics across all machines.

    Used for multi-machine platform summaries.
    """

    users: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    memory_percent: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    load_time_sec: MetricWithOutliers = field(default_factory=MetricWithOutliers)
    cpu_percent: MetricWithOutliers = field(default_factory=MetricWithOutliers)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "users": self.users.to_dict(),
            "memory_percent": self.memory_percent.to_dict(),
            "load_time_sec": self.load_time_sec.to_dict(),
            "cpu_percent": self.cpu_percent.to_dict(),
        }


@dataclass
class MultiMachinePerformanceData:
    """
    Performance data for multi-machine platforms (Tableau, Alteryx).

    Attributes:
        timestamps: List of timestamp strings
        machines: Per-machine data
        machine_outliers: Outliers detected per machine
        aggregated: Aggregated metrics across all machines
    """

    timestamps: List[str] = field(default_factory=list)
    machines: Dict[str, MachineData] = field(default_factory=dict)
    machine_outliers: Dict[str, MachineOutliers] = field(default_factory=dict)
    aggregated: AggregatedMetrics = field(default_factory=AggregatedMetrics)

    def to_dict(self) -> dict:
        """Convert to dictionary for Dash components."""
        return {
            "timestamps": self.timestamps,
            "machines": {k: v.to_dict() for k, v in self.machines.items()},
            "machine_outliers": {k: v.to_dict() for k, v in self.machine_outliers.items()},
            "aggregated": self.aggregated.to_dict(),
        }
