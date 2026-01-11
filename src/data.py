"""
Data module for Platform Health Dashboard.

This module provides the main data access layer for the dashboard,
combining data from the provider layer with business logic for
status determination and performance metrics.

In production, data is loaded from CSV files that are periodically
refreshed by a Databricks job. The CSV files can be stored locally
or in Azure Blob Storage (mounted as a file system).

Usage:
    from data import get_platforms, get_tickets, get_performance_data

    platforms = get_platforms()
    tickets = get_tickets()
    perf_data = get_performance_data("edlap")
"""

import logging
import math
import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from config import settings
from models import (
    Platform,
    PlatformId,
    PlatformMetric,
    PlatformMetrics,
    PlatformStatus,
    PlatformTrend,
)
from providers import get_data_provider

logger = logging.getLogger(__name__)


# =============================================================================
# Status Threshold Configuration
# =============================================================================
# These thresholds determine platform health status levels.
# In production, these would typically be loaded from a configuration service.

STATUS_THRESHOLDS = {
    "edlap": {
        "pipeline_failures": {
            "healthy": settings.thresholds.edlap.pipeline_failures.healthy,
            "attention": settings.thresholds.edlap.pipeline_failures.attention,
        },
        "data_delays": {
            "healthy": settings.thresholds.edlap.data_delays.healthy,
            "attention": settings.thresholds.edlap.data_delays.attention,
        },
    },
    "sapbw": {
        "memory_tb": {
            "healthy": settings.thresholds.sapbw.memory_tb.healthy,
            "attention": settings.thresholds.sapbw.memory_tb.attention,
        },
        "storage_tb": {
            "healthy": settings.thresholds.sapbw.storage_tb.healthy,
            "attention": settings.thresholds.sapbw.storage_tb.attention,
        },
    },
    "tableau": {
        "load_time_sec": {
            "healthy": settings.thresholds.tableau.load_time_sec.healthy,
            "attention": settings.thresholds.tableau.load_time_sec.attention,
        },
        "cpu_percent": {
            "healthy": settings.thresholds.tableau.cpu_percent.healthy,
            "attention": settings.thresholds.tableau.cpu_percent.attention,
        },
    },
    "alteryx": {
        "job_failures": {
            "healthy": settings.thresholds.alteryx.job_failures.healthy,
            "attention": settings.thresholds.alteryx.job_failures.attention,
        },
        "queue_depth": {
            "healthy": settings.thresholds.alteryx.queue_depth.healthy,
            "attention": settings.thresholds.alteryx.queue_depth.attention,
        },
    },
}

OUTLIER_THRESHOLDS = {
    "edlap": {
        "users": {"warning": 150, "critical": 200},
        "pipelines_failed": {"warning": 5, "critical": 10},
        "pipelines_delayed": {"warning": 8, "critical": 15},
        "tickets_overdue": {"warning": 5, "critical": 10},
    },
    "sapbw": {
        "users": {"warning": 80, "critical": 120},
        "memory_tb": {"warning": 20, "critical": 22},
        "load_time_sec": {"warning": 8, "critical": 12},
        "cpu_percent": {"warning": 75, "critical": 90},
    },
    "tableau": {
        "users": {"warning": 200, "critical": 300},
        "memory_percent": {"warning": 75, "critical": 90},
        "load_time_sec": {"warning": 5, "critical": 8},
        "cpu_percent": {"warning": 70, "critical": 85},
    },
    "alteryx": {
        "users": {"warning": 50, "critical": 80},
        "memory_percent": {"warning": 70, "critical": 85},
        "load_time_sec": {"warning": 120, "critical": 180},
        "cpu_percent": {"warning": 70, "critical": 85},
    },
}

MACHINE_CONFIG = {
    "tableau": {
        "count": settings.machine_configs.tableau.count,
        "prefix": settings.machine_configs.tableau.prefix,
    },
    "alteryx": {
        "count": settings.machine_configs.alteryx.count,
        "prefix": settings.machine_configs.alteryx.prefix,
    },
}


# =============================================================================
# Public API - Main data access functions
# =============================================================================


def get_platforms() -> List[Dict[str, Any]]:
    """
    Get platform health data for all monitored platforms.

    This function:
    1. Loads real ticket counts from the data provider
    2. Loads real SAP B/W performance metrics
    3. Loads real pipeline status data
    4. Determines health status based on configured thresholds

    Returns:
        List of platform dictionaries compatible with Dash components
    """
    provider = get_data_provider()

    # Get real ticket counts by platform
    ticket_counts = _get_ticket_counts_by_platform()

    # Get real SAP B/W performance data (latest record)
    latest_bw = provider.get_latest_bw_performance()
    if latest_bw:
        bw_memory = latest_bw["memory_usage_tb"]
        bw_storage = latest_bw["storage_usage_tb"]
        bw_memory_capacity = latest_bw["memory_capacity_tb"]
    else:
        # Fallback values for demo
        bw_memory = 18.2
        bw_storage = 54.7
        bw_memory_capacity = 24.0

    # Get real pipeline data
    pipeline_summary = get_pipeline_summary("edlap")
    edlap_failures = pipeline_summary.get("failed", 2)
    edlap_delays = pipeline_summary.get("delayed", 8)

    # Build platform objects with determined status
    platforms = [
        _build_edlap_platform(ticket_counts, edlap_failures, edlap_delays),
        _build_sapbw_platform(ticket_counts, bw_memory, bw_storage, bw_memory_capacity),
        _build_tableau_platform(ticket_counts),
        _build_alteryx_platform(ticket_counts),
    ]

    return [p.to_dict() for p in platforms]


def get_tickets() -> List[Dict[str, Any]]:
    """
    Get ticket data from the data provider.

    Loads active tickets from the configured data source, sorted by
    priority (High first) then by age (oldest first).

    Returns:
        List of ticket dictionaries compatible with Dash components
    """
    provider = get_data_provider()
    active_tickets = provider.get_active_tickets()

    # Sort by priority then age
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    active_tickets.sort(
        key=lambda t: (priority_order.get(t.priority.value, 2), -t.age_days)
    )

    return [t.to_dict() for t in active_tickets]


def get_summary_counts() -> Dict[str, int]:
    """
    Get summary counts for the dashboard header.

    Returns:
        Dictionary with counts for healthy, attention, critical platforms
        and total open tickets
    """
    platforms = get_platforms()
    tickets = get_tickets()

    return {
        "healthy": sum(1 for p in platforms if p["status"] == "healthy"),
        "attention": sum(1 for p in platforms if p["status"] == "attention"),
        "critical": sum(1 for p in platforms if p["status"] == "critical"),
        "total_tickets": len(tickets),
    }


def get_performance_data(platform_id: str, hours: int = 24) -> Dict[str, Any]:
    """
    Get performance data for a specific platform.

    Args:
        platform_id: Platform identifier (edlap, sapbw, tableau, alteryx)
        hours: Number of hours of data to return

    Returns:
        Performance data dictionary compatible with Dash graphing components
    """
    if platform_id == "edlap":
        return get_edlap_performance_data(hours)
    elif platform_id == "sapbw":
        return get_sapbw_performance_data(hours)
    elif platform_id == "tableau":
        return get_tableau_performance_data(hours)
    elif platform_id == "alteryx":
        return get_alteryx_performance_data(hours)
    return {}


def get_pipeline_summary(platform_id: str = "edlap") -> Dict[str, int]:
    """
    Get current pipeline counts for platform bar chart.

    Args:
        platform_id: Platform identifier (edlap or sapbw)

    Returns:
        Dictionary with pipeline status counts
    """
    provider = get_data_provider()
    summary = provider.get_pipeline_summary(platform_id)

    if summary.total == 0:
        # Fallback to generated data for demo
        random.seed(42 if platform_id == "edlap" else 43)
        total = 245 if platform_id == "edlap" else 150
        failed = random.randint(1, 5)
        delayed = random.randint(3, 10)
        successful = total - failed - delayed
        return {
            "successful": successful,
            "delayed": delayed,
            "failed": failed,
            "not_applicable": 0,
            "total": total,
        }

    return summary.to_dict()


def get_historical_stats(values: List[float], period: str = "month") -> Dict[str, float]:
    """
    Calculate historical statistics (average and peak) for a metric.

    For demo purposes, this simulates historical data based on current
    values with some variation. In production, this would query actual
    historical data.

    Args:
        values: Current period values to base simulation on
        period: 'month' for 30-day stats, 'week' for 7-day stats

    Returns:
        Dictionary with 'average' and 'peak' values
    """
    if not values:
        return {"average": 0, "peak": 0}

    current_avg = sum(values) / len(values)
    current_max = max(values)

    # Simulate historical variation
    random.seed(100)

    if period == "month":
        avg_factor = random.uniform(0.92, 1.08)
        peak_factor = random.uniform(1.1, 1.35)
    else:  # week
        avg_factor = random.uniform(0.95, 1.05)
        peak_factor = random.uniform(1.05, 1.2)

    return {
        "average": round(current_avg * avg_factor, 2),
        "peak": round(current_max * peak_factor, 2),
    }


def get_ticket_history(platform_id: str = None, days: int = 30) -> Dict[str, Any]:
    """
    Get ticket history data for line graphs.

    Generates a simulated history of open tickets over time based on
    current ticket data. In production, this would query historical
    snapshots from the ticketing system.

    Args:
        platform_id: Filter to specific platform or None for all
        days: Number of days of history to generate

    Returns:
        Dictionary with timestamps and ticket counts
    """
    provider = get_data_provider()
    tickets = provider.load_tickets()

    # Filter to platform if specified
    if platform_id:
        tickets = [t for t in tickets if t.platform.value == platform_id]

    # Get current counts
    active_tickets = [t for t in tickets if t.is_active]
    current_count = len(active_tickets)
    breached_count = len([t for t in active_tickets if t.is_breached])

    # Generate simulated history
    now = datetime.now()
    timestamps = []
    open_tickets = []
    overdue_tickets = []

    random.seed(hash(platform_id or "all") % 2**32)

    for i in range(days, -1, -1):
        date = now - timedelta(days=i)
        timestamps.append(date.strftime("%Y-%m-%d"))

        # Simulate ticket count history trending towards current value
        progress = (days - i) / days
        base_count = int(current_count * 0.7 + current_count * 0.6 * progress)
        daily_variation = random.randint(-3, 4)
        count = max(0, base_count + daily_variation)

        # Weekday vs weekend pattern
        if date.weekday() >= 5:
            count = int(count * 0.85)

        open_tickets.append(count)

        # Overdue is typically 15-35% of open tickets
        overdue_base = int(count * (0.15 + 0.2 * random.random()))
        overdue_variation = random.randint(-1, 1)
        overdue = max(0, min(count, overdue_base + overdue_variation))

        if i == 0:
            overdue = breached_count

        overdue_tickets.append(overdue)

    # Ensure last value matches current count
    open_tickets[-1] = current_count

    return {
        "timestamps": timestamps,
        "open_tickets": {"values": open_tickets, "outliers": []},
        "overdue_tickets": {"values": overdue_tickets, "outliers": []},
        "current_count": current_count,
        "breached_count": breached_count,
    }


def get_bw_memory_stats_30days() -> Dict[str, float]:
    """
    Get average and peak memory usage from the last 30 days of B/W data.

    Returns:
        Dictionary with 'average' and 'peak' values in TB
    """
    provider = get_data_provider()
    stats = provider.get_bw_memory_stats()
    return {"average": stats.average, "peak": stats.peak}


# Backward compatibility alias
def get_ticket_counts_by_platform() -> Dict[str, int]:
    """Get count of active tickets per platform."""
    return _get_ticket_counts_by_platform()


# =============================================================================
# Internal Helper Functions
# =============================================================================


def _get_ticket_counts_by_platform() -> Dict[str, int]:
    """Get count of active tickets per platform."""
    provider = get_data_provider()
    tickets = provider.load_tickets()
    counts = defaultdict(int)

    for ticket in tickets:
        if ticket.is_active:
            counts[ticket.platform.value] += 1

    return dict(counts)


def _build_edlap_platform(
    ticket_counts: Dict[str, int], failures: int, delays: int
) -> Platform:
    """Build EDLAP platform object with current status."""
    thresholds = STATUS_THRESHOLDS["edlap"]["pipeline_failures"]

    if failures >= thresholds["attention"]:
        status = PlatformStatus.CRITICAL
    elif failures >= thresholds["healthy"]:
        status = PlatformStatus.ATTENTION
    else:
        status = PlatformStatus.HEALTHY

    return Platform(
        id=PlatformId.EDLAP,
        name="EDLAP",
        subtitle="Enterprise Data Lake",
        status=status,
        metrics=PlatformMetrics(
            primary=PlatformMetric(
                label="Pipeline Failures", value=str(failures), threshold="< 5"
            ),
            secondary=PlatformMetric(
                label="Data Delays", value=str(delays), threshold="< 15"
            ),
            tertiary=PlatformMetric(
                label="Open Tickets", value=str(ticket_counts.get("edlap", 0))
            ),
        ),
        trend=PlatformTrend.STABLE,
    )


def _build_sapbw_platform(
    ticket_counts: Dict[str, int],
    memory: float,
    storage: float,
    memory_capacity: float,
) -> Platform:
    """Build SAP B/W platform object with current status."""
    if memory >= 22:
        status = PlatformStatus.CRITICAL
    elif memory >= 20:
        status = PlatformStatus.ATTENTION
    else:
        status = PlatformStatus.HEALTHY

    trend = PlatformTrend.RISING if memory >= 20 else PlatformTrend.STABLE

    return Platform(
        id=PlatformId.SAPBW,
        name="SAP B/W",
        subtitle="Business Warehouse",
        status=status,
        metrics=PlatformMetrics(
            primary=PlatformMetric(
                label="Memory Usage",
                value=f"{memory:.1f} TB",
                threshold=f"< {memory_capacity:.0f} TB",
            ),
            secondary=PlatformMetric(
                label="Storage", value=f"{storage:.1f} TB", threshold="< 60 TB"
            ),
            tertiary=PlatformMetric(
                label="Open Tickets", value=str(ticket_counts.get("sapbw", 0))
            ),
        ),
        trend=trend,
    )


def _build_tableau_platform(ticket_counts: Dict[str, int]) -> Platform:
    """Build Tableau platform object with current status."""
    ticket_count = ticket_counts.get("tableau", 0)
    status = PlatformStatus.ATTENTION if ticket_count > 15 else PlatformStatus.HEALTHY

    return Platform(
        id=PlatformId.TABLEAU,
        name="Tableau",
        subtitle="Analytics & Reporting",
        status=status,
        metrics=PlatformMetrics(
            primary=PlatformMetric(
                label="Avg Load Time", value="4.2s", threshold="< 5s"
            ),
            secondary=PlatformMetric(label="CPU Peak", value="72%", threshold="< 80%"),
            tertiary=PlatformMetric(label="Open Tickets", value=str(ticket_count)),
        ),
        trend=PlatformTrend.STABLE,
    )


def _build_alteryx_platform(ticket_counts: Dict[str, int]) -> Platform:
    """Build Alteryx platform object with current status."""
    return Platform(
        id=PlatformId.ALTERYX,
        name="Alteryx",
        subtitle="Self-Service Analytics",
        status=PlatformStatus.HEALTHY,
        metrics=PlatformMetrics(
            primary=PlatformMetric(
                label="Job Failures", value="1", threshold="< 5"
            ),
            secondary=PlatformMetric(
                label="Queue Depth", value="3", threshold="< 10"
            ),
            tertiary=PlatformMetric(
                label="Open Tickets", value=str(ticket_counts.get("alteryx", 0))
            ),
        ),
        trend=PlatformTrend.STABLE,
    )


# =============================================================================
# Performance Data Generation
# =============================================================================


def _generate_base_pattern(hours: int = 24, interval_minutes: int = 5) -> List[datetime]:
    """Generate timestamps for the specified duration with given interval."""
    now = datetime.now()
    minutes = (now.minute // interval_minutes) * interval_minutes
    current = now.replace(minute=minutes, second=0, microsecond=0)

    points = []
    total_points = (hours * 60) // interval_minutes
    for i in range(total_points, 0, -1):
        points.append(current - timedelta(minutes=i * interval_minutes))
    points.append(current)
    return points


def _add_daily_pattern(base_value: float, hour: int, amplitude: float = 0.3) -> float:
    """Add daily usage pattern (higher during business hours)."""
    morning_factor = math.exp(-((hour - 10.5) ** 2) / 8)
    afternoon_factor = math.exp(-((hour - 14.5) ** 2) / 10)
    pattern = morning_factor * 0.7 + afternoon_factor * 0.5
    return base_value * (1 + amplitude * pattern)


def _add_noise(value: float, noise_percent: float = 0.1) -> float:
    """Add random noise to a value."""
    noise = random.gauss(0, value * noise_percent)
    return max(0, value + noise)


def _inject_outliers(
    values: List[float],
    outlier_chance: float = 0.02,
    outlier_magnitude: float = 1.5,
) -> Tuple[List[float], List[int]]:
    """Inject outliers into a time series and return indices of outliers."""
    outlier_indices = []
    result = values.copy()
    for i in range(len(result)):
        if random.random() < outlier_chance:
            result[i] = result[i] * outlier_magnitude
            outlier_indices.append(i)
    return result, outlier_indices


def detect_outliers(values: List[float], threshold: Dict[str, float]) -> List[Dict[str, Any]]:
    """Detect outliers based on threshold configuration."""
    outliers = []
    for i, val in enumerate(values):
        if val >= threshold.get("critical", float("inf")):
            outliers.append({"index": i, "value": val, "severity": "critical"})
        elif val >= threshold.get("warning", float("inf")):
            outliers.append({"index": i, "value": val, "severity": "warning"})
    return outliers


def get_edlap_performance_data(hours: int = 24) -> Dict[str, Any]:
    """
    Generate EDLAP performance data.

    Metrics: users, pipelines (total/delayed/failed), tickets (open/overdue)
    """
    timestamps = _generate_base_pattern(hours)
    random.seed(settings.dashboard.demo_random_seed)

    # Users - typical 50-150 range with daily pattern
    users = []
    for ts in timestamps:
        base = 80
        val = _add_daily_pattern(base, ts.hour, amplitude=0.6)
        val = _add_noise(val, 0.15)
        users.append(max(5, round(val)))
    users, _ = _inject_outliers(users, 0.01, 2.0)

    # Total pipelines - relatively stable
    total_pipelines = []
    for ts in timestamps:
        base = 245
        val = base + random.randint(-5, 5)
        total_pipelines.append(val)

    # Failed pipelines - occasional spikes
    failed_pipelines = []
    for ts in timestamps:
        base = 2
        val = base + random.randint(0, 3)
        failed_pipelines.append(val)
    failed_pipelines, _ = _inject_outliers(failed_pipelines, 0.03, 3.0)

    # Delayed pipelines - more during business hours
    delayed_pipelines = []
    for ts in timestamps:
        base = 5
        val = _add_daily_pattern(base, ts.hour, amplitude=0.4)
        val = _add_noise(val, 0.2)
        delayed_pipelines.append(max(0, round(val)))
    delayed_pipelines, _ = _inject_outliers(delayed_pipelines, 0.02, 2.5)

    # Open tickets - gradual changes
    open_tickets = []
    base_tickets = 12
    for i, ts in enumerate(timestamps):
        base_tickets += random.choice([-1, 0, 0, 0, 1])
        base_tickets = max(5, min(25, base_tickets))
        open_tickets.append(base_tickets)

    # Overdue tickets - subset of open
    overdue_tickets = []
    for i, ot in enumerate(open_tickets):
        overdue = max(0, min(ot - 5, round(ot * 0.2 + random.randint(-1, 2))))
        overdue_tickets.append(overdue)

    # Detect outliers
    thresholds = OUTLIER_THRESHOLDS["edlap"]

    return {
        "timestamps": [ts.strftime("%Y-%m-%d %H:%M") for ts in timestamps],
        "users": {"values": users, "outliers": detect_outliers(users, thresholds["users"])},
        "total_pipelines": {"values": total_pipelines, "outliers": []},
        "failed_pipelines": {
            "values": [int(v) for v in failed_pipelines],
            "outliers": detect_outliers(failed_pipelines, thresholds["pipelines_failed"]),
        },
        "delayed_pipelines": {
            "values": [int(v) for v in delayed_pipelines],
            "outliers": detect_outliers(delayed_pipelines, thresholds["pipelines_delayed"]),
        },
        "open_tickets": {"values": open_tickets, "outliers": []},
        "overdue_tickets": {
            "values": overdue_tickets,
            "outliers": detect_outliers(overdue_tickets, thresholds["tickets_overdue"]),
        },
    }


def get_sapbw_performance_data(hours: int = 24) -> Dict[str, Any]:
    """
    Get SAP B/W performance data.

    Uses real memory data from bw_system_performance.csv where available.
    Metrics: users, memory (TB), avg dashboard load time, CPU
    """
    provider = get_data_provider()
    bw_records = provider.load_bw_performance()

    if bw_records:
        # Use real data - take the most recent records
        recent_records = bw_records[-min(len(bw_records), 289):]

        timestamps = []
        memory_tb = []

        for record in recent_records:
            ts_str = record.get("snapshot_ts", "")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    timestamps.append(ts.strftime("%Y-%m-%d %H:%M"))
                except (ValueError, TypeError):
                    continue
                memory_tb.append(record["memory_usage_tb"])

        memory_capacity = recent_records[-1]["memory_capacity_tb"] if recent_records else 23.25

        # Generate simulated users and other metrics
        random.seed(43)
        users = []
        for i, ts_str in enumerate(timestamps):
            try:
                hour = int(ts_str.split(" ")[1].split(":")[0])
            except (IndexError, ValueError):
                hour = 12
            base = 45
            val = _add_daily_pattern(base, hour, amplitude=0.8)
            val = _add_noise(val, 0.12)
            users.append(max(3, round(val)))

        # Dashboard load time - correlate with memory usage
        load_times = []
        for i in range(len(timestamps)):
            base = 4.5
            memory_factor = memory_tb[i] / 19 if i < len(memory_tb) else 1.0
            val = base * (0.8 + 0.4 * memory_factor)
            val = _add_noise(val, 0.2)
            load_times.append(round(val, 2))

        # CPU percent - correlate with memory
        cpu_percent = []
        for i in range(len(timestamps)):
            base = 35
            memory_factor = memory_tb[i] / 19 if i < len(memory_tb) else 1.0
            val = base * (0.7 + 0.5 * memory_factor)
            val = _add_noise(val, 0.15)
            cpu_percent.append(min(100, round(val, 1)))

    else:
        # Fallback to generated data
        generated_timestamps = _generate_base_pattern(hours)
        timestamps = [ts.strftime("%Y-%m-%d %H:%M") for ts in generated_timestamps]
        random.seed(43)
        memory_capacity = 24.0

        users = []
        for ts in generated_timestamps:
            base = 45
            val = _add_daily_pattern(base, ts.hour, amplitude=0.8)
            val = _add_noise(val, 0.12)
            users.append(max(3, round(val)))

        memory_tb = []
        for ts in generated_timestamps:
            base = 18.2
            val = _add_daily_pattern(base, ts.hour, amplitude=0.15)
            val = _add_noise(val, 0.03)
            memory_tb.append(round(val, 2))
        memory_tb, _ = _inject_outliers(memory_tb, 0.02, 1.15)

        load_times = []
        for i, ts in enumerate(generated_timestamps):
            base = 4.5
            user_factor = users[i] / 50
            val = base * (1 + 0.3 * user_factor)
            val = _add_noise(val, 0.2)
            load_times.append(round(val, 2))
        load_times, _ = _inject_outliers(load_times, 0.03, 2.0)

        cpu_percent = []
        for i, ts in enumerate(generated_timestamps):
            base = 35
            user_factor = users[i] / 50
            memory_factor = memory_tb[i] / 18
            val = base * (1 + 0.4 * user_factor + 0.3 * memory_factor)
            val = _add_noise(val, 0.15)
            cpu_percent.append(min(100, round(val, 1)))
        cpu_percent, _ = _inject_outliers(cpu_percent, 0.02, 1.4)

    # Detect outliers
    thresholds = OUTLIER_THRESHOLDS["sapbw"]

    return {
        "timestamps": timestamps,
        "users": {"values": users, "outliers": detect_outliers(users, thresholds["users"])},
        "memory_tb": {
            "values": [min(memory_capacity, v) for v in memory_tb],
            "outliers": detect_outliers(memory_tb, thresholds["memory_tb"]),
        },
        "memory_capacity": memory_capacity,
        "load_time_sec": {
            "values": load_times,
            "outliers": detect_outliers(load_times, thresholds["load_time_sec"]),
        },
        "cpu_percent": {
            "values": [min(100, v) for v in cpu_percent],
            "outliers": detect_outliers([min(100, v) for v in cpu_percent], thresholds["cpu_percent"]),
        },
    }


def _generate_multi_machine_data(
    machine_count: int,
    prefix: str,
    hours: int,
    base_users: int,
    base_memory: float,
    base_load: float,
    base_cpu: float,
) -> Tuple[List[datetime], Dict[str, Dict[str, List[float]]]]:
    """Generate performance data for multi-machine platforms."""
    timestamps = _generate_base_pattern(hours)

    machines = {}
    for m in range(machine_count):
        machine_name = f"{prefix}-{m+1:02d}"
        random.seed(44 + m)

        # Users per machine
        users = []
        for ts in timestamps:
            base = base_users / machine_count
            val = _add_daily_pattern(base, ts.hour, amplitude=0.7)
            val = _add_noise(val, 0.2)
            if m < 2:
                val *= 1.3
            users.append(max(0, round(val)))

        # Memory percent
        memory_pct = []
        for i, ts in enumerate(timestamps):
            base = base_memory
            user_factor = users[i] / (base_users / machine_count)
            val = base * (0.7 + 0.3 * user_factor)
            val = _add_noise(val, 0.1)
            memory_pct.append(min(100, round(val, 1)))
        memory_pct, _ = _inject_outliers(memory_pct, 0.02, 1.2)

        # CPU percent
        cpu_pct = []
        for i, ts in enumerate(timestamps):
            base = base_cpu
            user_factor = users[i] / (base_users / machine_count)
            val = base * (0.6 + 0.4 * user_factor)
            val = _add_noise(val, 0.15)
            cpu_pct.append(min(100, round(val, 1)))
        cpu_pct, _ = _inject_outliers(cpu_pct, 0.025, 1.3)

        machines[machine_name] = {
            "users": users,
            "memory_percent": [min(100, v) for v in memory_pct],
            "cpu_percent": [min(100, v) for v in cpu_pct],
        }

    return timestamps, machines


def get_tableau_performance_data(hours: int = 24) -> Dict[str, Any]:
    """
    Generate Tableau performance data (8 machines).

    Metrics: users, memory %, avg dashboard load time, CPU %
    """
    config = MACHINE_CONFIG["tableau"]
    timestamps, machines = _generate_multi_machine_data(
        config["count"],
        config["prefix"],
        hours,
        base_users=180,
        base_memory=55,
        base_load=3.5,
        base_cpu=45,
    )

    random.seed(48)

    # Aggregate metrics
    total_users = []
    avg_memory = []
    avg_cpu = []

    for i in range(len(timestamps)):
        users_sum = sum(m["users"][i] for m in machines.values())
        mem_avg = sum(m["memory_percent"][i] for m in machines.values()) / len(machines)
        cpu_avg = sum(m["cpu_percent"][i] for m in machines.values()) / len(machines)
        total_users.append(users_sum)
        avg_memory.append(round(mem_avg, 1))
        avg_cpu.append(round(cpu_avg, 1))

    # Dashboard load time
    load_times = []
    for i, ts in enumerate(timestamps):
        base = 3.8
        user_factor = total_users[i] / 180
        cpu_factor = avg_cpu[i] / 50
        val = base * (0.7 + 0.2 * user_factor + 0.1 * cpu_factor)
        val = _add_noise(val, 0.15)
        load_times.append(round(val, 2))
    load_times, _ = _inject_outliers(load_times, 0.04, 2.5)

    thresholds = OUTLIER_THRESHOLDS["tableau"]

    # Per-machine outliers
    machine_outliers = {}
    for name, data in machines.items():
        machine_outliers[name] = {
            "memory": detect_outliers(data["memory_percent"], thresholds["memory_percent"]),
            "cpu": detect_outliers(data["cpu_percent"], thresholds["cpu_percent"]),
        }

    return {
        "timestamps": [ts.strftime("%Y-%m-%d %H:%M") for ts in timestamps],
        "machines": machines,
        "machine_outliers": machine_outliers,
        "aggregated": {
            "users": {"values": total_users, "outliers": detect_outliers(total_users, thresholds["users"])},
            "memory_percent": {"values": avg_memory, "outliers": detect_outliers(avg_memory, thresholds["memory_percent"])},
            "load_time_sec": {"values": load_times, "outliers": detect_outliers(load_times, thresholds["load_time_sec"])},
            "cpu_percent": {"values": avg_cpu, "outliers": detect_outliers(avg_cpu, thresholds["cpu_percent"])},
        },
    }


def get_alteryx_performance_data(hours: int = 24) -> Dict[str, Any]:
    """
    Generate Alteryx performance data (8 worker machines).

    Metrics: users, memory %, avg workflow execution time, CPU %
    """
    config = MACHINE_CONFIG["alteryx"]
    timestamps, machines = _generate_multi_machine_data(
        config["count"],
        config["prefix"],
        hours,
        base_users=40,
        base_memory=50,
        base_load=90,
        base_cpu=40,
    )

    random.seed(52)

    # Aggregate metrics
    total_users = []
    avg_memory = []
    avg_cpu = []

    for i in range(len(timestamps)):
        users_sum = sum(m["users"][i] for m in machines.values())
        mem_avg = sum(m["memory_percent"][i] for m in machines.values()) / len(machines)
        cpu_avg = sum(m["cpu_percent"][i] for m in machines.values()) / len(machines)
        total_users.append(users_sum)
        avg_memory.append(round(mem_avg, 1))
        avg_cpu.append(round(cpu_avg, 1))

    # Average workflow execution time
    load_times = []
    for i, ts in enumerate(timestamps):
        base = 85
        user_factor = total_users[i] / 40
        cpu_factor = avg_cpu[i] / 45
        val = base * (0.8 + 0.15 * user_factor + 0.05 * cpu_factor)
        val = _add_noise(val, 0.2)
        load_times.append(round(val, 1))
    load_times, _ = _inject_outliers(load_times, 0.02, 1.8)

    thresholds = OUTLIER_THRESHOLDS["alteryx"]

    # Per-machine outliers
    machine_outliers = {}
    for name, data in machines.items():
        machine_outliers[name] = {
            "memory": detect_outliers(data["memory_percent"], thresholds["memory_percent"]),
            "cpu": detect_outliers(data["cpu_percent"], thresholds["cpu_percent"]),
        }

    return {
        "timestamps": [ts.strftime("%Y-%m-%d %H:%M") for ts in timestamps],
        "machines": machines,
        "machine_outliers": machine_outliers,
        "aggregated": {
            "users": {"values": total_users, "outliers": detect_outliers(total_users, thresholds["users"])},
            "memory_percent": {"values": avg_memory, "outliers": detect_outliers(avg_memory, thresholds["memory_percent"])},
            "load_time_sec": {"values": load_times, "outliers": detect_outliers(load_times, thresholds["load_time_sec"])},
            "cpu_percent": {"values": avg_cpu, "outliers": detect_outliers(avg_cpu, thresholds["cpu_percent"])},
        },
    }
