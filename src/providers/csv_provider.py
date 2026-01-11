"""
CSV file data provider.

This provider loads dashboard data from CSV files. It supports:
- Local CSV files (development)
- Mounted Azure File Share or Blob Storage (production with FUSE)
- Network file shares

The CSV files are expected to be periodically refreshed by a Databricks
job that exports the latest data.
"""

import csv
import logging
from pathlib import Path
from typing import List, Optional

from config import settings
from models import Pipeline, Ticket

from .base import DataProvider

logger = logging.getLogger(__name__)


class CSVDataProvider(DataProvider):
    """
    Data provider that loads data from CSV files.

    This provider is designed to work with CSV files that are periodically
    updated by an external process (e.g., Databricks job writing to Azure
    Blob Storage, which is mounted as a file system).

    Attributes:
        data_directory: Path to the directory containing CSV files
        tickets_file: Name of the tickets CSV file
        pipelines_file: Name of the pipelines CSV file
        bw_performance_file: Name of the B/W performance CSV file

    Example:
        # Using default settings
        provider = CSVDataProvider()
        tickets = provider.load_tickets()

        # Using custom directory
        provider = CSVDataProvider(data_directory=Path("/mnt/data"))
        tickets = provider.load_tickets()
    """

    def __init__(
        self,
        data_directory: Optional[Path] = None,
        tickets_file: Optional[str] = None,
        pipelines_file: Optional[str] = None,
        bw_performance_file: Optional[str] = None,
    ) -> None:
        """
        Initialize the CSV data provider.

        Args:
            data_directory: Path to CSV files (defaults to settings)
            tickets_file: Tickets CSV filename (defaults to settings)
            pipelines_file: Pipelines CSV filename (defaults to settings)
            bw_performance_file: B/W performance CSV filename (defaults to settings)
        """
        self.data_directory = data_directory or settings.data_source.data_directory
        self.tickets_file = tickets_file or settings.data_source.tickets_file
        self.pipelines_file = pipelines_file or settings.data_source.pipelines_file
        self.bw_performance_file = bw_performance_file or settings.data_source.bw_performance_file

        logger.info(
            "Initialized CSV data provider",
            extra={
                "data_directory": str(self.data_directory),
                "tickets_file": self.tickets_file,
                "pipelines_file": self.pipelines_file,
                "bw_performance_file": self.bw_performance_file,
            },
        )

    def _get_file_path(self, filename: str) -> Path:
        """Get the full path to a CSV file."""
        return self.data_directory / filename

    def _read_csv(self, filename: str) -> List[dict]:
        """
        Read a CSV file and return rows as dictionaries.

        Args:
            filename: Name of the CSV file

        Returns:
            List of row dictionaries, or empty list on error
        """
        file_path = self._get_file_path(filename)

        if not file_path.exists():
            logger.warning(f"CSV file not found: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                logger.debug(f"Loaded {len(rows)} rows from {filename}")
                return rows
        except csv.Error as e:
            logger.error(f"CSV parsing error in {filename}: {e}")
            return []
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error in {filename}: {e}")
            return []
        except OSError as e:
            logger.error(f"Error reading {filename}: {e}")
            return []

    def load_tickets(self) -> List[Ticket]:
        """
        Load tickets from the tickets CSV file.

        The CSV is expected to have ServiceNow export format with columns:
        - service_task_id: Ticket number
        - platform_id: Platform identifier
        - service_task_desc: Ticket description
        - service_task_type_code: INC/PRB/REQ/RITM
        - service_task_created_ts: Creation timestamp
        - service_task_state_desc: Status description
        - service_task_assignment_group_desc: Owner/group
        - is_active: Whether ticket is active
        - is_breached: Whether SLA is breached
        - snapshot_ts: Data snapshot timestamp

        Returns:
            List of Ticket objects
        """
        rows = self._read_csv(self.tickets_file)
        tickets = []

        for row in rows:
            ticket = Ticket.from_csv_row(row)
            if ticket is not None:
                tickets.append(ticket)

        if rows and not tickets:
            logger.warning(
                f"No valid tickets parsed from {len(rows)} rows in {self.tickets_file}"
            )
        elif tickets:
            logger.info(f"Loaded {len(tickets)} tickets from {self.tickets_file}")

        return tickets

    def load_pipelines(self) -> List[Pipeline]:
        """
        Load pipeline records from the pipelines CSV file.

        The CSV is expected to have columns:
        - pipeline_id: Unique pipeline identifier
        - platform_id: Platform identifier (EDLAP/SAP_BW)
        - pipeline_transformed_status: Status description
        - pipeline_original_status: Original status code
        - pipeline_delay_time_qty: Delay in seconds
        - pipeline_end_ts: Actual end timestamp
        - pipeline_expected_end_ts: Expected end timestamp
        - snapshot_ts: Data snapshot timestamp

        Returns:
            List of Pipeline objects
        """
        rows = self._read_csv(self.pipelines_file)
        pipelines = []

        for row in rows:
            pipeline = Pipeline.from_csv_row(row)
            if pipeline is not None:
                pipelines.append(pipeline)

        if rows and not pipelines:
            logger.warning(
                f"No valid pipelines parsed from {len(rows)} rows in {self.pipelines_file}"
            )
        elif pipelines:
            logger.info(f"Loaded {len(pipelines)} pipelines from {self.pipelines_file}")

        return pipelines

    def load_bw_performance(self) -> List[dict]:
        """
        Load SAP B/W performance records.

        The CSV is expected to have columns:
        - snapshot_ts: Timestamp of the snapshot
        - storage_usage_tb: Storage usage in TB
        - storage_capacity_tb: Storage capacity in TB
        - memory_usage_tb: Memory usage in TB
        - memory_capacity_tb: Memory capacity in TB
        - ymd: Date (YYYY-MM-DD)

        Returns:
            List of performance record dictionaries
        """
        rows = self._read_csv(self.bw_performance_file)
        records = []

        for row in rows:
            try:
                record = {
                    "snapshot_ts": row.get("snapshot_ts", ""),
                    "storage_usage_tb": float(row.get("storage_usage_tb", 0)),
                    "storage_capacity_tb": float(row.get("storage_capacity_tb", 0)),
                    "memory_usage_tb": float(row.get("memory_usage_tb", 0)),
                    "memory_capacity_tb": float(row.get("memory_capacity_tb", 0)),
                    "ymd": row.get("ymd", ""),
                }
                records.append(record)
            except (ValueError, TypeError) as e:
                logger.debug(f"Skipping invalid B/W performance row: {e}")
                continue

        if rows and not records:
            logger.warning(
                f"No valid B/W records parsed from {len(rows)} rows in {self.bw_performance_file}"
            )
        elif records:
            logger.info(
                f"Loaded {len(records)} B/W performance records from {self.bw_performance_file}"
            )

        return records

    def is_available(self) -> bool:
        """
        Check if the CSV data directory exists and contains expected files.

        Returns:
            True if data directory exists and has at least one expected file
        """
        if not self.data_directory.exists():
            return False

        # Check if at least one data file exists
        expected_files = [
            self.tickets_file,
            self.pipelines_file,
            self.bw_performance_file,
        ]

        for filename in expected_files:
            if self._get_file_path(filename).exists():
                return True

        return False

    def get_source_info(self) -> str:
        """
        Get a description of the CSV data source.

        Returns:
            Description string including directory path and file status
        """
        files_status = []
        for filename in [self.tickets_file, self.pipelines_file, self.bw_performance_file]:
            path = self._get_file_path(filename)
            status = "OK" if path.exists() else "MISSING"
            files_status.append(f"{filename}: {status}")

        return f"CSV Provider @ {self.data_directory}\n  " + "\n  ".join(files_status)
