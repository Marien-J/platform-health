"""
Pipeline data models.

Defines the Pipeline entity for tracking data pipeline status.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .platform import PlatformId


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    SUCCESSFUL = "successful"
    DELAYED = "delayed"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"
    RUNNING = "running"
    PENDING = "pending"

    @classmethod
    def from_string(cls, status: str, original_status: str = "") -> "PipelineStatus":
        """
        Parse status from CSV data.

        Args:
            status: Transformed status string
            original_status: Original status code (G=green, R=red, etc.)

        Returns:
            Parsed PipelineStatus
        """
        status_lower = status.lower()
        original_lower = original_status.lower()

        if "failed" in status_lower or original_lower == "r" or "failed" in original_lower:
            return cls.FAILED
        elif "delayed" in status_lower:
            return cls.DELAYED
        elif "not applicable" in status_lower:
            return cls.NOT_APPLICABLE
        elif "running" in status_lower:
            return cls.RUNNING
        elif "pending" in status_lower or "scheduled" in status_lower:
            return cls.PENDING
        elif "within expected" in status_lower or original_lower == "g" or "succeeded" in original_lower:
            return cls.SUCCESSFUL
        else:
            # Default to successful if status is unclear
            return cls.SUCCESSFUL


@dataclass
class Pipeline:
    """
    Represents a data pipeline execution record.

    This model captures the status of pipeline executions for
    EDLAP and SAP B/W platforms.

    Attributes:
        platform: Platform this pipeline belongs to
        pipeline_id: Unique pipeline identifier
        status: Current execution status
        original_status: Raw status from source system
        snapshot_ts: Timestamp of this status snapshot
        end_ts: Actual end timestamp
        expected_end_ts: Expected end timestamp
        delay_seconds: Delay in seconds (0 if on time or early)
    """
    platform: PlatformId
    pipeline_id: str
    status: PipelineStatus
    original_status: str = ""
    snapshot_ts: str = ""
    end_ts: str = ""
    expected_end_ts: str = ""
    delay_seconds: float = 0.0

    @property
    def is_delayed(self) -> bool:
        """Check if pipeline is delayed."""
        return self.status == PipelineStatus.DELAYED or self.delay_seconds > 0

    @property
    def is_failed(self) -> bool:
        """Check if pipeline failed."""
        return self.status == PipelineStatus.FAILED

    @property
    def is_successful(self) -> bool:
        """Check if pipeline completed successfully."""
        return self.status == PipelineStatus.SUCCESSFUL

    def to_dict(self) -> dict:
        """Convert to dictionary for data processing."""
        return {
            "platform": self.platform.value,
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "original_status": self.original_status,
            "snapshot_ts": self.snapshot_ts,
            "end_ts": self.end_ts,
            "expected_end_ts": self.expected_end_ts,
            "delay_seconds": self.delay_seconds,
        }

    @classmethod
    def from_csv_row(cls, row: dict) -> Optional["Pipeline"]:
        """
        Create a Pipeline from a CSV row.

        Args:
            row: Dictionary with CSV column values

        Returns:
            Pipeline instance or None if parsing fails
        """
        try:
            # Map platform_id
            platform_map = {
                "EDLAP": PlatformId.EDLAP,
                "SAP_BW": PlatformId.SAPBW,
            }
            platform_str = row.get("platform_id", "")
            platform = platform_map.get(platform_str)
            if platform is None:
                try:
                    platform = PlatformId.from_string(platform_str)
                except ValueError:
                    platform = PlatformId.EDLAP

            # Parse delay time
            delay_qty = row.get("pipeline_delay_time_qty", "")
            try:
                delay_seconds = float(delay_qty) if delay_qty and delay_qty != "null" else 0.0
            except (ValueError, TypeError):
                delay_seconds = 0.0

            # Parse status
            transformed_status = row.get("pipeline_transformed_status", "")
            original_status = row.get("pipeline_original_status", "")
            status = PipelineStatus.from_string(transformed_status, original_status)

            return cls(
                platform=platform,
                pipeline_id=row.get("pipeline_id", ""),
                status=status,
                original_status=original_status,
                snapshot_ts=row.get("snapshot_ts", ""),
                end_ts=row.get("pipeline_end_ts", ""),
                expected_end_ts=row.get("pipeline_expected_end_ts", ""),
                delay_seconds=delay_seconds,
            )
        except Exception:
            return None
