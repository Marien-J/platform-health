"""
Data module for Platform Health Dashboard.
In production, this would connect to your actual data sources (ServiceNow, monitoring APIs, etc.)
"""

from typing import List, Dict, Any, Tuple
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

# Outlier thresholds for performance metrics
OUTLIER_THRESHOLDS = {
    'edlap': {
        'users': {'warning': 150, 'critical': 200},
        'pipelines_failed': {'warning': 5, 'critical': 10},
        'pipelines_delayed': {'warning': 8, 'critical': 15},
        'tickets_overdue': {'warning': 5, 'critical': 10}
    },
    'sapbw': {
        'users': {'warning': 80, 'critical': 120},
        'memory_tb': {'warning': 20, 'critical': 22},
        'load_time_sec': {'warning': 8, 'critical': 12},
        'cpu_percent': {'warning': 75, 'critical': 90}
    },
    'tableau': {
        'users': {'warning': 200, 'critical': 300},
        'memory_percent': {'warning': 75, 'critical': 90},
        'load_time_sec': {'warning': 5, 'critical': 8},
        'cpu_percent': {'warning': 70, 'critical': 85}
    },
    'alteryx': {
        'users': {'warning': 50, 'critical': 80},
        'memory_percent': {'warning': 70, 'critical': 85},
        'load_time_sec': {'warning': 120, 'critical': 180},
        'cpu_percent': {'warning': 70, 'critical': 85}
    }
}

# Machine configuration for multi-server platforms
MACHINE_CONFIG = {
    'tableau': {'count': 8, 'prefix': 'TAB-SRV'},
    'alteryx': {'count': 8, 'prefix': 'ALT-WRK'}
}


def _generate_base_pattern(hours: int = 24, interval_minutes: int = 5) -> List[datetime]:
    """Generate timestamps for the specified duration with given interval."""
    now = datetime.now()
    # Round down to nearest interval
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
    # Peak at 10-11 AM and 2-3 PM
    morning_factor = math.exp(-((hour - 10.5) ** 2) / 8)
    afternoon_factor = math.exp(-((hour - 14.5) ** 2) / 10)
    pattern = morning_factor * 0.7 + afternoon_factor * 0.5
    return base_value * (1 + amplitude * pattern)


def _add_noise(value: float, noise_percent: float = 0.1) -> float:
    """Add random noise to a value."""
    noise = random.gauss(0, value * noise_percent)
    return max(0, value + noise)


def _inject_outliers(values: List[float], outlier_chance: float = 0.02,
                     outlier_magnitude: float = 1.5) -> Tuple[List[float], List[int]]:
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
        if val >= threshold.get('critical', float('inf')):
            outliers.append({'index': i, 'value': val, 'severity': 'critical'})
        elif val >= threshold.get('warning', float('inf')):
            outliers.append({'index': i, 'value': val, 'severity': 'warning'})
    return outliers


def get_edlap_performance_data(hours: int = 24) -> Dict[str, Any]:
    """
    Generate EDLAP performance data.
    Metrics: users, pipelines (total/delayed/failed), tickets (open/overdue)
    """
    timestamps = _generate_base_pattern(hours)
    random.seed(42)  # For reproducible demo data

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
        # Slowly varying
        base_tickets += random.choice([-1, 0, 0, 0, 1])
        base_tickets = max(5, min(25, base_tickets))
        open_tickets.append(base_tickets)

    # Overdue tickets - subset of open
    overdue_tickets = []
    for i, ot in enumerate(open_tickets):
        overdue = max(0, min(ot - 5, round(ot * 0.2 + random.randint(-1, 2))))
        overdue_tickets.append(overdue)

    # Detect outliers
    thresholds = OUTLIER_THRESHOLDS['edlap']
    users_outliers = detect_outliers(users, thresholds['users'])
    failed_outliers = detect_outliers(failed_pipelines, thresholds['pipelines_failed'])
    delayed_outliers = detect_outliers(delayed_pipelines, thresholds['pipelines_delayed'])
    overdue_outliers = detect_outliers(overdue_tickets, thresholds['tickets_overdue'])

    return {
        'timestamps': [ts.strftime('%Y-%m-%d %H:%M') for ts in timestamps],
        'users': {'values': users, 'outliers': users_outliers},
        'total_pipelines': {'values': total_pipelines, 'outliers': []},
        'failed_pipelines': {'values': [int(v) for v in failed_pipelines], 'outliers': failed_outliers},
        'delayed_pipelines': {'values': [int(v) for v in delayed_pipelines], 'outliers': delayed_outliers},
        'open_tickets': {'values': open_tickets, 'outliers': []},
        'overdue_tickets': {'values': overdue_tickets, 'outliers': overdue_outliers}
    }


def get_sapbw_performance_data(hours: int = 24) -> Dict[str, Any]:
    """
    Generate SAP B/W performance data.
    Metrics: users, memory (TB), avg dashboard load time, CPU
    """
    timestamps = _generate_base_pattern(hours)
    random.seed(43)

    # Users - business hours pattern, max around 100
    users = []
    for ts in timestamps:
        base = 45
        val = _add_daily_pattern(base, ts.hour, amplitude=0.8)
        val = _add_noise(val, 0.12)
        users.append(max(3, round(val)))

    # Memory TB - high baseline (machine has 24TB), stays 16-22 typically
    memory_tb = []
    for ts in timestamps:
        base = 18.2
        # Higher during business hours due to caching
        val = _add_daily_pattern(base, ts.hour, amplitude=0.15)
        val = _add_noise(val, 0.03)
        memory_tb.append(round(val, 2))
    memory_tb, _ = _inject_outliers(memory_tb, 0.02, 1.15)  # Occasional spikes to ~21TB

    # Dashboard load time - varies with load
    load_times = []
    for i, ts in enumerate(timestamps):
        base = 4.5
        # Correlate with users
        user_factor = users[i] / 50
        val = base * (1 + 0.3 * user_factor)
        val = _add_noise(val, 0.2)
        load_times.append(round(val, 2))
    load_times, _ = _inject_outliers(load_times, 0.03, 2.0)

    # CPU percent - correlates with memory and users
    cpu_percent = []
    for i, ts in enumerate(timestamps):
        base = 35
        user_factor = users[i] / 50
        memory_factor = memory_tb[i] / 18
        val = base * (1 + 0.4 * user_factor + 0.3 * memory_factor)
        val = _add_noise(val, 0.15)
        cpu_percent.append(min(100, round(val, 1)))
    cpu_percent, _ = _inject_outliers(cpu_percent, 0.02, 1.4)

    # Detect outliers
    thresholds = OUTLIER_THRESHOLDS['sapbw']
    users_outliers = detect_outliers(users, thresholds['users'])
    memory_outliers = detect_outliers(memory_tb, thresholds['memory_tb'])
    load_outliers = detect_outliers(load_times, thresholds['load_time_sec'])
    cpu_outliers = detect_outliers([min(100, v) for v in cpu_percent], thresholds['cpu_percent'])

    return {
        'timestamps': [ts.strftime('%Y-%m-%d %H:%M') for ts in timestamps],
        'users': {'values': users, 'outliers': users_outliers},
        'memory_tb': {'values': [min(24, v) for v in memory_tb], 'outliers': memory_outliers},
        'load_time_sec': {'values': load_times, 'outliers': load_outliers},
        'cpu_percent': {'values': [min(100, v) for v in cpu_percent], 'outliers': cpu_outliers}
    }


def _generate_multi_machine_data(machine_count: int, prefix: str, hours: int,
                                  base_users: int, base_memory: float,
                                  base_load: float, base_cpu: float) -> Dict[str, Any]:
    """Generate performance data for multi-machine platforms."""
    timestamps = _generate_base_pattern(hours)

    machines = {}
    for m in range(machine_count):
        machine_name = f"{prefix}-{m+1:02d}"
        random.seed(44 + m)  # Different seed per machine

        # Users per machine
        users = []
        for ts in timestamps:
            base = base_users / machine_count
            val = _add_daily_pattern(base, ts.hour, amplitude=0.7)
            val = _add_noise(val, 0.2)
            # Some machines handle more load
            if m < 2:  # First 2 machines are primary
                val *= 1.3
            users.append(max(0, round(val)))

        # Memory percent (not TB for these systems)
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
            'users': users,
            'memory_percent': [min(100, v) for v in memory_pct],
            'cpu_percent': [min(100, v) for v in cpu_pct]
        }

    return timestamps, machines


def get_tableau_performance_data(hours: int = 24) -> Dict[str, Any]:
    """
    Generate Tableau performance data (8 machines).
    Metrics: users, memory %, avg dashboard load time, CPU %
    """
    config = MACHINE_CONFIG['tableau']
    timestamps, machines = _generate_multi_machine_data(
        config['count'], config['prefix'], hours,
        base_users=180, base_memory=55, base_load=3.5, base_cpu=45
    )

    random.seed(48)

    # Aggregate metrics
    total_users = []
    avg_memory = []
    avg_cpu = []

    for i in range(len(timestamps)):
        users_sum = sum(m['users'][i] for m in machines.values())
        mem_avg = sum(m['memory_percent'][i] for m in machines.values()) / len(machines)
        cpu_avg = sum(m['cpu_percent'][i] for m in machines.values()) / len(machines)
        total_users.append(users_sum)
        avg_memory.append(round(mem_avg, 1))
        avg_cpu.append(round(cpu_avg, 1))

    # Dashboard load time - aggregate metric
    load_times = []
    for i, ts in enumerate(timestamps):
        base = 3.8
        user_factor = total_users[i] / 180
        cpu_factor = avg_cpu[i] / 50
        val = base * (0.7 + 0.2 * user_factor + 0.1 * cpu_factor)
        val = _add_noise(val, 0.15)
        load_times.append(round(val, 2))
    load_times, _ = _inject_outliers(load_times, 0.04, 2.5)  # Tableau has load issues

    # Detect outliers
    thresholds = OUTLIER_THRESHOLDS['tableau']
    users_outliers = detect_outliers(total_users, thresholds['users'])
    memory_outliers = detect_outliers(avg_memory, thresholds['memory_percent'])
    load_outliers = detect_outliers(load_times, thresholds['load_time_sec'])
    cpu_outliers = detect_outliers(avg_cpu, thresholds['cpu_percent'])

    # Per-machine outliers
    machine_outliers = {}
    for name, data in machines.items():
        machine_outliers[name] = {
            'memory': detect_outliers(data['memory_percent'], thresholds['memory_percent']),
            'cpu': detect_outliers(data['cpu_percent'], thresholds['cpu_percent'])
        }

    return {
        'timestamps': [ts.strftime('%Y-%m-%d %H:%M') for ts in timestamps],
        'machines': machines,
        'machine_outliers': machine_outliers,
        'aggregated': {
            'users': {'values': total_users, 'outliers': users_outliers},
            'memory_percent': {'values': avg_memory, 'outliers': memory_outliers},
            'load_time_sec': {'values': load_times, 'outliers': load_outliers},
            'cpu_percent': {'values': avg_cpu, 'outliers': cpu_outliers}
        }
    }


def get_alteryx_performance_data(hours: int = 24) -> Dict[str, Any]:
    """
    Generate Alteryx performance data (8 worker machines).
    Metrics: users, memory %, avg workflow execution time, CPU %
    """
    config = MACHINE_CONFIG['alteryx']
    timestamps, machines = _generate_multi_machine_data(
        config['count'], config['prefix'], hours,
        base_users=40, base_memory=50, base_load=90, base_cpu=40
    )

    random.seed(52)

    # Aggregate metrics
    total_users = []
    avg_memory = []
    avg_cpu = []

    for i in range(len(timestamps)):
        users_sum = sum(m['users'][i] for m in machines.values())
        mem_avg = sum(m['memory_percent'][i] for m in machines.values()) / len(machines)
        cpu_avg = sum(m['cpu_percent'][i] for m in machines.values()) / len(machines)
        total_users.append(users_sum)
        avg_memory.append(round(mem_avg, 1))
        avg_cpu.append(round(cpu_avg, 1))

    # Average workflow execution time (seconds) - longer than dashboard loads
    load_times = []
    for i, ts in enumerate(timestamps):
        base = 85  # Alteryx workflows take longer
        user_factor = total_users[i] / 40
        cpu_factor = avg_cpu[i] / 45
        val = base * (0.8 + 0.15 * user_factor + 0.05 * cpu_factor)
        val = _add_noise(val, 0.2)
        load_times.append(round(val, 1))
    load_times, _ = _inject_outliers(load_times, 0.02, 1.8)

    # Detect outliers
    thresholds = OUTLIER_THRESHOLDS['alteryx']
    users_outliers = detect_outliers(total_users, thresholds['users'])
    memory_outliers = detect_outliers(avg_memory, thresholds['memory_percent'])
    load_outliers = detect_outliers(load_times, thresholds['load_time_sec'])
    cpu_outliers = detect_outliers(avg_cpu, thresholds['cpu_percent'])

    # Per-machine outliers
    machine_outliers = {}
    for name, data in machines.items():
        machine_outliers[name] = {
            'memory': detect_outliers(data['memory_percent'], thresholds['memory_percent']),
            'cpu': detect_outliers(data['cpu_percent'], thresholds['cpu_percent'])
        }

    return {
        'timestamps': [ts.strftime('%Y-%m-%d %H:%M') for ts in timestamps],
        'machines': machines,
        'machine_outliers': machine_outliers,
        'aggregated': {
            'users': {'values': total_users, 'outliers': users_outliers},
            'memory_percent': {'values': avg_memory, 'outliers': memory_outliers},
            'load_time_sec': {'values': load_times, 'outliers': load_outliers},
            'cpu_percent': {'values': avg_cpu, 'outliers': cpu_outliers}
        }
    }


def get_performance_data(platform_id: str, hours: int = 24) -> Dict[str, Any]:
    """Get performance data for a specific platform."""
    if platform_id == 'edlap':
        return get_edlap_performance_data(hours)
    elif platform_id == 'sapbw':
        return get_sapbw_performance_data(hours)
    elif platform_id == 'tableau':
        return get_tableau_performance_data(hours)
    elif platform_id == 'alteryx':
        return get_alteryx_performance_data(hours)
    return {}
