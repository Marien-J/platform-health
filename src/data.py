"""
Data module for Platform Health Dashboard.
In production, this would connect to your actual data sources (ServiceNow, monitoring APIs, etc.)
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import math


def get_platforms() -> List[Dict[str, Any]]:
    """
    Get platform health data.
    
    In production, this would fetch from:
    - EDLAP: Databricks API / monitoring
    - SAP B/W: SAP monitoring endpoints
    - Tableau: Tableau Server API
    - Alteryx: Alteryx Server API
    """
    return [
        {
            'id': 'edlap',
            'name': 'EDLAP',
            'subtitle': 'Enterprise Data Lake',
            'status': 'healthy',
            'status_label': 'Healthy',
            'metrics': {
                'primary': {'label': 'Pipeline Failures', 'value': '2', 'threshold': '< 5'},
                'secondary': {'label': 'Data Delays', 'value': '8', 'threshold': '< 15'},
                'tertiary': {'label': 'Open Tickets', 'value': '12'}
            },
            'trend': 'stable'
        },
        {
            'id': 'sapbw',
            'name': 'SAP B/W',
            'subtitle': 'Business Warehouse',
            'status': 'attention',
            'status_label': 'Attention',
            'metrics': {
                'primary': {'label': 'Memory Usage', 'value': '18.2 TB', 'threshold': '< 20 TB'},
                'secondary': {'label': 'Storage', 'value': '54.7 TB', 'threshold': '< 60 TB'},
                'tertiary': {'label': 'Open Tickets', 'value': '34'}
            },
            'trend': 'rising'
        },
        {
            'id': 'tableau',
            'name': 'Tableau',
            'subtitle': 'Analytics & Reporting',
            'status': 'critical',
            'status_label': 'Critical',
            'metrics': {
                'primary': {'label': 'Avg Load Time', 'value': '12.4s', 'threshold': '< 5s'},
                'secondary': {'label': 'CPU Peak', 'value': '94%', 'threshold': '< 80%'},
                'tertiary': {'label': 'Open Tickets', 'value': '47'}
            },
            'trend': 'degrading'
        },
        {
            'id': 'alteryx',
            'name': 'Alteryx',
            'subtitle': 'Self-Service Analytics',
            'status': 'healthy',
            'status_label': 'Healthy',
            'metrics': {
                'primary': {'label': 'Job Failures', 'value': '1', 'threshold': '< 5'},
                'secondary': {'label': 'Queue Depth', 'value': '3', 'threshold': '< 10'},
                'tertiary': {'label': 'Open Tickets', 'value': '8'}
            },
            'trend': 'stable'
        }
    ]


def get_tickets() -> List[Dict[str, Any]]:
    """
    Get ticket data.

    In production, this would fetch from ServiceNow or your ticketing system.
    """
    return [
        {
            'id': 'INC001234',
            'platform': 'tableau',
            'title': 'Dashboard timeout on Sales Overview',
            'priority': 'High',
            'age': '3d',
            'created_date': '2026-01-03',
            'owner': 'M. Schmidt',
            'description': 'The Sales Overview dashboard is timing out after approximately 30 seconds when users attempt to load it. This affects the entire sales team during their morning standup meetings. Initial investigation suggests the issue may be related to a recent data source change.',
            'last_updated': '2026-01-06 09:45'
        },
        {
            'id': 'INC001198',
            'platform': 'tableau',
            'title': 'Slow refresh on Executive KPIs',
            'priority': 'High',
            'age': '5d',
            'created_date': '2026-01-01',
            'owner': 'K. Weber',
            'description': 'Executive KPI dashboard refresh time has increased from 5 seconds to over 45 seconds. This is impacting leadership meetings and decision-making processes. The slowdown started after the latest data model update.',
            'last_updated': '2026-01-05 14:30'
        },
        {
            'id': 'INC001201',
            'platform': 'sapbw',
            'title': 'Memory spike during month-end',
            'priority': 'Medium',
            'age': '2d',
            'created_date': '2026-01-04',
            'owner': 'SAP Team',
            'description': 'Memory usage spikes to 22TB during month-end processing, approaching the 24TB limit. This causes query slowdowns and potential system instability. Need to investigate query optimization or consider scheduling changes.',
            'last_updated': '2026-01-06 08:15'
        },
        {
            'id': 'INC001189',
            'platform': 'edlap',
            'title': 'Pipeline delay - Finance feed',
            'priority': 'Low',
            'age': '4d',
            'created_date': '2026-01-02',
            'owner': 'Data Ops',
            'description': 'The Finance department data feed is arriving 2-3 hours later than expected. This is due to upstream system maintenance windows being extended. Working with Finance IT to resolve the scheduling conflict.',
            'last_updated': '2026-01-04 16:20'
        },
        {
            'id': 'INC001156',
            'platform': 'tableau',
            'title': 'Report export failing for GBIE',
            'priority': 'Medium',
            'age': '7d',
            'created_date': '2025-12-30',
            'owner': 'K. Weber',
            'description': 'GBIE team reports that PDF exports of their regional sales reports are failing with a timeout error. The exports work fine for smaller datasets but fail when the full region is selected. May need to implement pagination or optimize the underlying query.',
            'last_updated': '2026-01-03 11:00'
        },
        {
            'id': 'INC001145',
            'platform': 'sapbw',
            'title': 'BW query performance degradation',
            'priority': 'High',
            'age': '6d',
            'created_date': '2025-12-31',
            'owner': 'SAP Team',
            'description': 'Several key BW queries have experienced 3x slower performance over the past week. This affects multiple downstream reports and analytics. Root cause analysis points to index fragmentation and statistics that need updating.',
            'last_updated': '2026-01-05 17:45'
        },
        {
            'id': 'INC001132',
            'platform': 'alteryx',
            'title': 'Scheduled workflow failed - HR extract',
            'priority': 'Low',
            'age': '1d',
            'created_date': '2026-01-05',
            'owner': 'Data Ops',
            'description': 'The daily HR data extract workflow failed due to a connection timeout to the source system. This is a transient issue that has been resolved by rerunning the workflow manually. Monitoring for recurrence.',
            'last_updated': '2026-01-06 07:30'
        },
        {
            'id': 'INC001128',
            'platform': 'edlap',
            'title': 'Data quality issue in customer dimension',
            'priority': 'Medium',
            'age': '8d',
            'created_date': '2025-12-29',
            'owner': 'Data Ops',
            'description': 'Duplicate customer records identified in the customer dimension table affecting approximately 2% of records. This is causing discrepancies in customer count reports. Data stewardship team is working on a deduplication strategy.',
            'last_updated': '2026-01-02 13:15'
        }
    ]


def get_summary_counts() -> Dict[str, int]:
    """Get summary counts for the dashboard header."""
    platforms = get_platforms()
    tickets = get_tickets()
    
    counts = {
        'healthy': sum(1 for p in platforms if p['status'] == 'healthy'),
        'attention': sum(1 for p in platforms if p['status'] == 'attention'),
        'critical': sum(1 for p in platforms if p['status'] == 'critical'),
        'total_tickets': len(tickets)
    }
    return counts


# Status thresholds configuration
# In production, these would be loaded from a config file or database
STATUS_THRESHOLDS = {
    'edlap': {
        'pipeline_failures': {'healthy': 5, 'attention': 10},  # critical if > 10
        'data_delays': {'healthy': 15, 'attention': 30}
    },
    'sapbw': {
        'memory_tb': {'healthy': 18, 'attention': 22},  # out of 24 TB
        'storage_tb': {'healthy': 55, 'attention': 60}
    },
    'tableau': {
        'load_time_sec': {'healthy': 5, 'attention': 8},
        'cpu_percent': {'healthy': 70, 'attention': 85}
    },
    'alteryx': {
        'job_failures': {'healthy': 3, 'attention': 7},
        'queue_depth': {'healthy': 10, 'attention': 20}
    }
}


# Server configurations
TABLEAU_SERVERS = [f"TAB-SRV-{i:02d}" for i in range(1, 9)]
ALTERYX_WORKERS = [f"ALT-WRK-{i:02d}" for i in range(1, 9)]


def _generate_time_series(hours: int = 24, interval_minutes: int = 5) -> List[datetime]:
    """Generate time series timestamps for the last N hours."""
    now = datetime.now().replace(second=0, microsecond=0)
    # Round to nearest interval
    now = now.replace(minute=(now.minute // interval_minutes) * interval_minutes)
    points = hours * 60 // interval_minutes
    return [now - timedelta(minutes=i * interval_minutes) for i in range(points - 1, -1, -1)]


def _generate_metric_data(
    base: float,
    variance: float,
    spike_probability: float = 0.02,
    spike_multiplier: float = 1.5,
    hours: int = 24
) -> List[float]:
    """Generate realistic metric data with occasional spikes."""
    timestamps = _generate_time_series(hours)
    data = []

    for i, ts in enumerate(timestamps):
        # Add time-of-day pattern (higher during business hours)
        hour = ts.hour
        time_factor = 1.0 + 0.3 * math.sin((hour - 6) * math.pi / 12) if 6 <= hour <= 18 else 0.7

        # Base value with variance
        value = base * time_factor + random.uniform(-variance, variance)

        # Occasional spikes
        if random.random() < spike_probability:
            value *= spike_multiplier

        data.append(max(0, min(100, value)))  # Clamp between 0 and 100

    return data


def get_tableau_server_data() -> Dict[str, Any]:
    """Get Tableau server performance data for the last 24 hours."""
    timestamps = _generate_time_series(24)

    # Generate data for each server with slightly different characteristics
    servers_data = {}
    alert_counts = {}
    server_statuses = {}

    for i, server in enumerate(TABLEAU_SERVERS):
        # Each server has slightly different baseline metrics
        base_cpu = 45 + i * 3 + random.uniform(-5, 5)
        base_memory = 55 + i * 2 + random.uniform(-5, 5)

        cpu_data = _generate_metric_data(base_cpu, 15, spike_probability=0.03)
        memory_data = _generate_metric_data(base_memory, 10, spike_probability=0.02)

        servers_data[server] = {
            'cpu': cpu_data,
            'memory': memory_data
        }

        # Count alerts (values exceeding thresholds)
        critical_count = sum(1 for v in cpu_data + memory_data if v > 90)
        warning_count = sum(1 for v in cpu_data + memory_data if 75 < v <= 90)
        alert_counts[server] = critical_count + warning_count

        # Determine server status
        if critical_count > 5:
            server_statuses[server] = 'critical'
        elif warning_count > 10 or critical_count > 0:
            server_statuses[server] = 'attention'
        else:
            server_statuses[server] = 'healthy'

    # Generate active users (aggregate)
    active_users = []
    for i, ts in enumerate(timestamps):
        hour = ts.hour
        # Business hours pattern
        if 8 <= hour <= 18:
            base_users = 250 + random.uniform(-50, 50)
        else:
            base_users = 100 + random.uniform(-30, 30)

        # Occasional spikes
        if random.random() < 0.05:
            base_users *= 1.3

        active_users.append(int(base_users))

    # Generate load times (in seconds) with spikes
    load_times = []
    load_time_spikes = []  # Track which points are spikes

    for i in range(len(timestamps)):
        base_load = 4 + random.uniform(-1, 1)
        is_spike = random.random() < 0.03

        if is_spike:
            load_time = base_load * random.uniform(2, 4)
            load_time_spikes.append(True)
        else:
            load_time = base_load
            load_time_spikes.append(False)

        load_times.append(round(load_time, 1))

    # Calculate historical averages (simulating "last month" data)
    avg_users_month = int(sum(active_users) / len(active_users) * 0.95)
    peak_users_month = int(max(active_users) * 1.1)

    # Calculate weekly averages for load times and CPU
    avg_load_week = round(sum(load_times) / len(load_times), 1)
    peak_load_week = round(max(load_times) * 0.9, 1)

    # CPU averages across all servers
    all_cpu = []
    for server_data in servers_data.values():
        all_cpu.extend(server_data['cpu'])
    avg_cpu = [sum(servers_data[s]['cpu'][i] for s in TABLEAU_SERVERS) / len(TABLEAU_SERVERS)
               for i in range(len(timestamps))]
    avg_cpu_week = round(sum(avg_cpu) / len(avg_cpu), 1)
    peak_cpu_week = round(max(avg_cpu), 1)

    return {
        'timestamps': timestamps,
        'servers': servers_data,
        'alert_counts': alert_counts,
        'server_statuses': server_statuses,
        'active_users': active_users,
        'load_times': load_times,
        'load_time_spikes': load_time_spikes,
        'avg_cpu': avg_cpu,
        'thresholds': {
            'cpu_warning': 75,
            'cpu_critical': 90,
            'memory_warning': 75,
            'memory_critical': 90,
        },
        'historical': {
            'avg_users_month': avg_users_month,
            'peak_users_month': peak_users_month,
            'avg_load_week': avg_load_week,
            'peak_load_week': peak_load_week,
            'avg_cpu_week': avg_cpu_week,
            'peak_cpu_week': peak_cpu_week,
        }
    }


def get_alteryx_server_data() -> Dict[str, Any]:
    """Get Alteryx worker performance data for the last 24 hours."""
    timestamps = _generate_time_series(24)

    workers_data = {}
    alert_counts = {}
    worker_statuses = {}

    for i, worker in enumerate(ALTERYX_WORKERS):
        base_cpu = 40 + i * 4 + random.uniform(-5, 5)
        base_memory = 50 + i * 3 + random.uniform(-5, 5)

        cpu_data = _generate_metric_data(base_cpu, 12, spike_probability=0.02)
        memory_data = _generate_metric_data(base_memory, 8, spike_probability=0.02)

        workers_data[worker] = {
            'cpu': cpu_data,
            'memory': memory_data
        }

        critical_count = sum(1 for v in cpu_data + memory_data if v > 90)
        warning_count = sum(1 for v in cpu_data + memory_data if 75 < v <= 90)
        alert_counts[worker] = critical_count + warning_count

        if critical_count > 5:
            worker_statuses[worker] = 'critical'
        elif warning_count > 10 or critical_count > 0:
            worker_statuses[worker] = 'attention'
        else:
            worker_statuses[worker] = 'healthy'

    # Active users
    active_users = []
    for ts in timestamps:
        hour = ts.hour
        if 9 <= hour <= 17:
            base_users = 150 + random.uniform(-30, 30)
        else:
            base_users = 50 + random.uniform(-20, 20)

        if random.random() < 0.04:
            base_users *= 1.4

        active_users.append(int(base_users))

    # Load times
    load_times = []
    load_time_spikes = []

    for i in range(len(timestamps)):
        base_load = 6 + random.uniform(-2, 2)
        is_spike = random.random() < 0.04

        if is_spike:
            load_time = base_load * random.uniform(2, 3)
            load_time_spikes.append(True)
        else:
            load_time = base_load
            load_time_spikes.append(False)

        load_times.append(round(load_time, 1))

    avg_users_month = int(sum(active_users) / len(active_users) * 0.9)
    peak_users_month = int(max(active_users) * 1.05)

    avg_load_week = round(sum(load_times) / len(load_times), 1)
    peak_load_week = round(max(load_times) * 0.85, 1)

    avg_cpu = [sum(workers_data[w]['cpu'][i] for w in ALTERYX_WORKERS) / len(ALTERYX_WORKERS)
               for i in range(len(timestamps))]
    avg_cpu_week = round(sum(avg_cpu) / len(avg_cpu), 1)
    peak_cpu_week = round(max(avg_cpu), 1)

    return {
        'timestamps': timestamps,
        'workers': workers_data,
        'alert_counts': alert_counts,
        'worker_statuses': worker_statuses,
        'active_users': active_users,
        'load_times': load_times,
        'load_time_spikes': load_time_spikes,
        'avg_cpu': avg_cpu,
        'thresholds': {
            'cpu_warning': 75,
            'cpu_critical': 90,
            'memory_warning': 75,
            'memory_critical': 90,
        },
        'historical': {
            'avg_users_month': avg_users_month,
            'peak_users_month': peak_users_month,
            'avg_load_week': avg_load_week,
            'peak_load_week': peak_load_week,
            'avg_cpu_week': avg_cpu_week,
            'peak_cpu_week': peak_cpu_week,
        }
    }


def get_edlap_data() -> Dict[str, Any]:
    """Get EDLAP platform data including pipeline status and tickets."""
    timestamps = _generate_time_series(24)

    # Pipeline status counts (for bar chart)
    pipeline_status = {
        'successful': random.randint(85, 120),
        'delayed': random.randint(5, 15),
        'failed': random.randint(1, 5)
    }

    # Open tickets time series (last 30 days, daily)
    ticket_days = 30
    ticket_timestamps = [datetime.now() - timedelta(days=i) for i in range(ticket_days - 1, -1, -1)]

    open_tickets = []
    base_tickets = 12
    for i in range(ticket_days):
        # Add some trend and variance
        tickets = base_tickets + random.randint(-3, 4)
        # Occasional spikes (e.g., after incidents)
        if random.random() < 0.1:
            tickets += random.randint(3, 8)
        open_tickets.append(max(0, tickets))

    avg_tickets_month = round(sum(open_tickets) / len(open_tickets), 1)
    peak_tickets_month = max(open_tickets)

    return {
        'timestamps': timestamps,
        'ticket_timestamps': ticket_timestamps,
        'pipeline_status': pipeline_status,
        'open_tickets': open_tickets,
        'historical': {
            'avg_tickets_month': avg_tickets_month,
            'peak_tickets_month': peak_tickets_month,
        }
    }
