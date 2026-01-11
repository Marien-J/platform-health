"""
Platform data models.

Defines the core Platform entity and related types used throughout
the dashboard for representing platform health status.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PlatformId(str, Enum):
    """Valid platform identifiers."""
    EDLAP = "edlap"
    SAPBW = "sapbw"
    TABLEAU = "tableau"
    ALTERYX = "alteryx"

    @classmethod
    def from_string(cls, value: str) -> "PlatformId":
        """Convert string to PlatformId, handling common aliases."""
        mapping = {
            "edlap": cls.EDLAP,
            "sap_bw": cls.SAPBW,
            "sapbw": cls.SAPBW,
            "sap bw": cls.SAPBW,
            "tableau": cls.TABLEAU,
            "alteryx": cls.ALTERYX,
        }
        normalized = value.lower().strip()
        if normalized in mapping:
            return mapping[normalized]
        raise ValueError(f"Unknown platform: {value}")


class PlatformStatus(str, Enum):
    """Platform health status levels."""
    HEALTHY = "healthy"
    ATTENTION = "attention"
    CRITICAL = "critical"

    @property
    def label(self) -> str:
        """Human-readable label for the status."""
        return self.value.capitalize()


class PlatformTrend(str, Enum):
    """Trend direction for platform metrics."""
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"


@dataclass
class PlatformMetric:
    """A single metric displayed on a platform card."""
    label: str
    value: str
    threshold: Optional[str] = None


@dataclass
class PlatformMetrics:
    """Collection of metrics for a platform card."""
    primary: PlatformMetric
    secondary: PlatformMetric
    tertiary: PlatformMetric


@dataclass
class Platform:
    """
    Represents a monitored platform with its current health status.

    This is the core entity used for displaying platform cards on the dashboard.

    Attributes:
        id: Unique platform identifier
        name: Display name
        subtitle: Short description
        status: Current health status
        metrics: Key metrics to display
        trend: Direction the platform is trending

    Example:
        platform = Platform(
            id=PlatformId.EDLAP,
            name="EDLAP",
            subtitle="Enterprise Data Lake",
            status=PlatformStatus.HEALTHY,
            metrics=PlatformMetrics(
                primary=PlatformMetric(label="Pipeline Failures", value="2", threshold="< 5"),
                secondary=PlatformMetric(label="Data Delays", value="8", threshold="< 15"),
                tertiary=PlatformMetric(label="Open Tickets", value="12"),
            ),
            trend=PlatformTrend.STABLE,
        )
    """
    id: PlatformId
    name: str
    subtitle: str
    status: PlatformStatus
    metrics: PlatformMetrics
    trend: PlatformTrend = PlatformTrend.STABLE

    @property
    def status_label(self) -> str:
        """Human-readable status label."""
        return self.status.label

    def to_dict(self) -> dict:
        """Convert to dictionary for Dash components."""
        return {
            "id": self.id.value,
            "name": self.name,
            "subtitle": self.subtitle,
            "status": self.status.value,
            "status_label": self.status_label,
            "metrics": {
                "primary": {
                    "label": self.metrics.primary.label,
                    "value": self.metrics.primary.value,
                    "threshold": self.metrics.primary.threshold,
                },
                "secondary": {
                    "label": self.metrics.secondary.label,
                    "value": self.metrics.secondary.value,
                    "threshold": self.metrics.secondary.threshold,
                },
                "tertiary": {
                    "label": self.metrics.tertiary.label,
                    "value": self.metrics.tertiary.value,
                },
            },
            "trend": self.trend.value,
        }


# Platform display information
PLATFORM_DISPLAY_NAMES = {
    PlatformId.EDLAP: "EDLAP",
    PlatformId.SAPBW: "SAP B/W",
    PlatformId.TABLEAU: "Tableau",
    PlatformId.ALTERYX: "Alteryx",
}

PLATFORM_SUBTITLES = {
    PlatformId.EDLAP: "Enterprise Data Lake",
    PlatformId.SAPBW: "Business Warehouse",
    PlatformId.TABLEAU: "Analytics & Reporting",
    PlatformId.ALTERYX: "Self-Service Analytics",
}
