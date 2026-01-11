"""
Data models for Platform Health Dashboard.

This module provides Pydantic models for type-safe data validation,
ensuring consistent data structures throughout the application.
"""

from .platform import (
    Platform,
    PlatformId,
    PlatformStatus,
    PlatformMetric,
    PlatformMetrics,
    PlatformTrend,
)
from .ticket import Ticket, TicketPriority, TicketStatus
from .performance import (
    PerformanceData,
    MetricWithOutliers,
    Outlier,
    OutlierSeverity,
    PipelineSummary,
    HistoricalStats,
    TicketHistory,
    MachineData,
    AggregatedMetrics,
    MultiMachinePerformanceData,
)
from .pipeline import Pipeline, PipelineStatus

__all__ = [
    # Platform models
    "Platform",
    "PlatformId",
    "PlatformStatus",
    "PlatformMetric",
    "PlatformMetrics",
    "PlatformTrend",
    # Ticket models
    "Ticket",
    "TicketPriority",
    "TicketStatus",
    # Performance models
    "PerformanceData",
    "MetricWithOutliers",
    "Outlier",
    "OutlierSeverity",
    "PipelineSummary",
    "HistoricalStats",
    "TicketHistory",
    "MachineData",
    "AggregatedMetrics",
    "MultiMachinePerformanceData",
    # Pipeline models
    "Pipeline",
    "PipelineStatus",
]
