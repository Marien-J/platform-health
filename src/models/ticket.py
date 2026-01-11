"""
Ticket data models.

Defines the Ticket entity and related types for ServiceNow integration.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .platform import PlatformId


class TicketPriority(str, Enum):
    """Ticket priority levels."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

    @classmethod
    def from_task_type(cls, task_type: str) -> "TicketPriority":
        """Derive priority from ServiceNow task type code."""
        mapping = {
            "INC": cls.HIGH,  # Incidents are high priority
            "PRB": cls.MEDIUM,  # Problems are medium priority
            "REQ": cls.LOW,  # Requests are low priority
            "RITM": cls.LOW,  # Request items are low priority
        }
        return mapping.get(task_type.upper()[:3], cls.LOW)


class TicketStatus(str, Enum):
    """Ticket status values."""

    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


@dataclass
class Ticket:
    """
    Represents a ServiceNow ticket.

    This model normalizes data from various ServiceNow ticket types
    (Incidents, Problems, Requests) into a consistent structure.

    Attributes:
        id: ServiceNow ticket number (e.g., INC001234)
        platform: Platform this ticket relates to
        title: Short description (truncated to 80 chars for display)
        description: Full description
        priority: Ticket priority level
        status: Current ticket status
        owner: Assignment group or individual
        requested_by: Person who requested/created the ticket
        assigned_to: Person assigned to work on the ticket
        created_date: Date ticket was created
        last_updated: Timestamp of last update
        age: Human-readable age string (e.g., "5d")
        is_active: Whether ticket is still active
        is_breached: Whether SLA has been breached
        country: Country context for the ticket
        service: Service category
    """

    id: str
    platform: PlatformId
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus = TicketStatus.OPEN
    owner: str = "Unassigned"
    requested_by: str = "Unavailable"
    assigned_to: str = "Unavailable"
    created_date: str = ""
    last_updated: str = ""
    age: str = "0d"
    is_active: bool = True
    is_breached: bool = False
    country: str = "Unknown"
    service: str = ""

    def __post_init__(self) -> None:
        """Validate and normalize fields after initialization."""
        # Ensure title is truncated for display
        if len(self.title) > 80:
            self.title = self.title[:77] + "..."

    @property
    def age_days(self) -> int:
        """Parse age string to get days as integer."""
        try:
            return int(self.age.replace("d", "").replace("?", "0"))
        except ValueError:
            return 0

    @property
    def ticket_type(self) -> str:
        """Get the ticket type from the ID prefix."""
        if self.id.startswith("INC"):
            return "Incident"
        elif self.id.startswith("PRB"):
            return "Problem"
        elif self.id.startswith("RITM"):
            return "Request Item"
        elif self.id.startswith("REQ"):
            return "Request"
        return "Unknown"

    def to_dict(self) -> dict:
        """Convert to dictionary for Dash components."""
        return {
            "id": self.id,
            "platform": self.platform.value,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "owner": self.owner,
            "requested_by": self.requested_by,
            "assigned_to": self.assigned_to,
            "created_date": self.created_date,
            "last_updated": self.last_updated,
            "age": self.age,
            "is_active": self.is_active,
            "is_breached": self.is_breached,
            "country": self.country,
            "service": self.service,
        }

    @classmethod
    def from_csv_row(cls, row: dict) -> Optional["Ticket"]:
        """
        Create a Ticket from a CSV row (ServiceNow export format).

        Args:
            row: Dictionary with CSV column values

        Returns:
            Ticket instance or None if parsing fails
        """
        from datetime import datetime

        try:
            # Map platform_id to our internal platform ids
            platform_map = {
                "EDLAP": PlatformId.EDLAP,
                "SAP_BW": PlatformId.SAPBW,
                "Tableau": PlatformId.TABLEAU,
                "Alteryx": PlatformId.ALTERYX,
            }
            platform_str = row.get("platform_id", "")
            platform = platform_map.get(
                platform_str,
                PlatformId.from_string(platform_str) if platform_str else PlatformId.EDLAP,
            )

            # Parse created timestamp
            created_ts = row.get("service_task_created_ts", "")
            created_date = created_ts[:10] if created_ts else ""

            # Calculate age in days
            age_str = "0d"
            if created_ts:
                try:
                    created_dt = datetime.fromisoformat(created_ts.replace("Z", "+00:00"))
                    age_days = (datetime.now(created_dt.tzinfo) - created_dt).days
                    age_str = f"{age_days}d"
                except (ValueError, TypeError):
                    age_str = "?d"

            # Determine priority from task type
            task_type = row.get("service_task_type_code", "REQ")
            priority = TicketPriority.from_task_type(task_type)

            # Breached tickets are always high priority
            is_breached = row.get("is_breached", "false").lower() == "true"
            if is_breached:
                priority = TicketPriority.HIGH

            # Parse status
            status_str = row.get("service_task_state_desc", "Open")
            try:
                status = TicketStatus(status_str)
            except ValueError:
                status = TicketStatus.OPEN

            # Format last updated
            snapshot_ts = row.get("snapshot_ts", "")
            last_updated = snapshot_ts[:16].replace("T", " ") if snapshot_ts else ""

            return cls(
                id=row.get("service_task_id", ""),
                platform=platform,
                title=row.get("service_task_desc", "")[:80],
                description=row.get("service_task_desc", ""),
                priority=priority,
                status=status,
                owner=row.get("service_task_assignment_group_desc", "Unassigned"),
                requested_by=row.get("requested_by", "Unavailable"),
                assigned_to=row.get("assigned_to", "Unavailable"),
                created_date=created_date,
                last_updated=last_updated,
                age=age_str,
                is_active=row.get("is_active", "true").lower() == "true",
                is_breached=is_breached,
                country=row.get("country", "Unknown"),
                service=row.get("service_task_service", ""),
            )
        except Exception:
            return None
