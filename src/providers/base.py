"""
Abstract base class for data providers.

This module defines the interface that all data providers must implement,
ensuring consistent data access patterns regardless of the underlying
data source.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from models import Pipeline, Ticket
from models.performance import HistoricalStats, PipelineSummary


class DataProvider(ABC):
    """
    Abstract base class for data providers.

    All data providers must implement these methods to ensure consistent
    data access across different storage backends (CSV, Azure Blob, Databricks).

    The provider is responsible for:
    - Loading raw data from the source
    - Parsing data into model objects
    - Handling errors gracefully
    - Logging operations for debugging

    Example implementation:
        class AzureBlobProvider(DataProvider):
            def __init__(self, connection_string: str, container: str):
                self.client = BlobServiceClient.from_connection_string(connection_string)
                self.container = container

            def load_tickets(self) -> List[Ticket]:
                blob = self.client.get_blob_client(self.container, "tickets.csv")
                content = blob.download_blob().readall()
                return self._parse_tickets(content)
    """

    @abstractmethod
    def load_tickets(self) -> List[Ticket]:
        """
        Load all tickets from the data source.

        Returns:
            List of Ticket objects, or empty list if no data available

        Raises:
            Should not raise exceptions - log errors and return empty list
        """
        pass

    @abstractmethod
    def load_pipelines(self) -> List[Pipeline]:
        """
        Load all pipeline records from the data source.

        Returns:
            List of Pipeline objects, or empty list if no data available

        Raises:
            Should not raise exceptions - log errors and return empty list
        """
        pass

    @abstractmethod
    def load_bw_performance(self) -> List[dict]:
        """
        Load SAP B/W performance records from the data source.

        Returns:
            List of performance record dictionaries with keys:
                - snapshot_ts: Timestamp string
                - storage_usage_tb: Storage usage in TB
                - storage_capacity_tb: Storage capacity in TB
                - memory_usage_tb: Memory usage in TB
                - memory_capacity_tb: Memory capacity in TB
                - ymd: Date string (YYYY-MM-DD)

        Raises:
            Should not raise exceptions - log errors and return empty list
        """
        pass

    def get_active_tickets(self) -> List[Ticket]:
        """
        Load and filter to only active tickets.

        Returns:
            List of active Ticket objects
        """
        tickets = self.load_tickets()
        return [t for t in tickets if t.is_active]

    def get_tickets_by_platform(self, platform_id: str) -> List[Ticket]:
        """
        Load tickets filtered to a specific platform.

        Args:
            platform_id: Platform ID to filter by

        Returns:
            List of Ticket objects for the platform
        """
        tickets = self.load_tickets()
        return [t for t in tickets if t.platform.value == platform_id]

    def get_pipeline_summary(self, platform_id: str) -> PipelineSummary:
        """
        Get pipeline status summary for a platform.

        Uses the shown_status property which applies platform-specific logic:
        - EDLAP: Failed if original_status='Failed', Delayed if Succeeded with delay>0
        - SAP_BW: Uses pipeline_transformed_status directly

        Args:
            platform_id: Platform ID to summarize

        Returns:
            PipelineSummary with counts by status
        """
        pipelines = self.load_pipelines()
        platform_pipelines = [p for p in pipelines if p.platform.value == platform_id]

        if not platform_pipelines:
            return PipelineSummary()

        # Use shown_status for counting (applies platform-specific logic)
        return PipelineSummary(
            successful=sum(1 for p in platform_pipelines if p.shown_status == 'Succeeded'),
            delayed=sum(1 for p in platform_pipelines if p.shown_status == 'Delayed'),
            failed=sum(1 for p in platform_pipelines if p.shown_status == 'Failed'),
            not_applicable=sum(1 for p in platform_pipelines if p.shown_status == 'Not Applicable'),
        )

    def get_bw_memory_stats(self) -> HistoricalStats:
        """
        Get average and peak memory usage from B/W performance data.

        Returns:
            HistoricalStats with average and peak values in TB
        """
        records = self.load_bw_performance()

        if not records:
            # Fallback if no data available
            return HistoricalStats(average=19.5, peak=21.9)

        memory_values = [r["memory_usage_tb"] for r in records if r.get("memory_usage_tb")]

        if not memory_values:
            return HistoricalStats(average=19.5, peak=21.9)

        avg_memory = sum(memory_values) / len(memory_values)
        peak_memory = max(memory_values)

        return HistoricalStats(
            average=round(avg_memory, 2),
            peak=round(peak_memory, 2),
        )

    def get_latest_bw_performance(self) -> Optional[dict]:
        """
        Get the most recent B/W performance record.

        Returns:
            Latest performance record or None
        """
        records = self.load_bw_performance()
        return records[-1] if records else None

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the data source is available and accessible.

        Returns:
            True if data source is accessible, False otherwise
        """
        pass

    @abstractmethod
    def get_source_info(self) -> str:
        """
        Get a description of the data source for logging/debugging.

        Returns:
            Human-readable description of the data source
        """
        pass
