"""
Data module for Platform Health Dashboard.
In production, this would connect to your actual data sources (ServiceNow, monitoring APIs, etc.)
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import random
import math
import os
import csv
from collections import defaultdict

# Path to sample data directory
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data')


def _load_tickets_from_csv() -> List[Dict[str, Any]]:
    """Load tickets from the sample_data/tickets.csv file."""
    tickets = []
    csv_path = os.path.join(SAMPLE_DATA_DIR, 'tickets.csv')

    if not os.path.exists(csv_path):
        return []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Map platform_id to our internal platform ids
            platform_map = {
                'EDLAP': 'edlap',
                'SAP_BW': 'sapbw',
                'Tableau': 'tableau',
                'Alteryx': 'alteryx'
            }

            platform = platform_map.get(row['platform_id'], row['platform_id'].lower())

            # Parse dates
            created_ts = row.get('service_task_created_ts', '')
            created_date = created_ts[:10] if created_ts else ''

            # Calculate age in days
            age_str = '0d'
            if created_ts:
                try:
                    created_dt = datetime.fromisoformat(created_ts.replace('Z', '+00:00'))
                    age_days = (datetime.now(created_dt.tzinfo) - created_dt).days
                    age_str = f"{age_days}d"
                except:
                    age_str = '?d'

            # Map service_task_type_code to priority (heuristic)
            task_type = row.get('service_task_type_code', 'REQ')
            priority_map = {'INC': 'High', 'PRB': 'Medium', 'REQ': 'Low'}
            priority = priority_map.get(task_type, 'Low')

            # Determine if breached affects priority
            if row.get('is_breached', 'false').lower() == 'true':
                priority = 'High'

            # Build ticket object
            ticket = {
                'id': row.get('service_task_id', ''),
                'platform': platform,
                'title': row.get('service_task_desc', '')[:80] + ('...' if len(row.get('service_task_desc', '')) > 80 else ''),
                'priority': priority,
                'age': age_str,
                'created_date': created_date,
                'owner': row.get('service_task_assignment_group_desc', 'Unassigned'),
                'description': row.get('service_task_desc', ''),
                'last_updated': row.get('snapshot_ts', '')[:16].replace('T', ' ') if row.get('snapshot_ts') else '',
                'status': row.get('service_task_state_desc', 'Open'),
                'is_active': row.get('is_active', 'true').lower() == 'true',
                'is_breached': row.get('is_breached', 'false').lower() == 'true',
                'country': row.get('country', 'Unknown'),
                'service': row.get('service_task_service', '')
            }
            tickets.append(ticket)

    return tickets


def _load_pipelines_from_csv() -> List[Dict[str, Any]]:
    """Load pipeline data from sample_data/pipelines.csv."""
    pipelines = []
    csv_path = os.path.join(SAMPLE_DATA_DIR, 'pipelines.csv')

    if not os.path.exists(csv_path):
        return []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Map platform_id
            platform_map = {
                'EDLAP': 'edlap',
                'SAP_BW': 'sapbw'
            }
            platform = platform_map.get(row.get('platform_id', ''), row.get('platform_id', '').lower())

            # Parse delay time
            delay_qty = row.get('pipeline_delay_time_qty', '')
            try:
                delay_seconds = float(delay_qty) if delay_qty and delay_qty != 'null' else 0
            except:
                delay_seconds = 0

            pipeline = {
                'platform': platform,
                'pipeline_id': row.get('pipeline_id', ''),
                'snapshot_ts': row.get('snapshot_ts', ''),
                'end_ts': row.get('pipeline_end_ts', ''),
                'expected_end_ts': row.get('pipeline_expected_end_ts', ''),
                'delay_seconds': delay_seconds,
                'original_status': row.get('pipeline_original_status', ''),
                'status': row.get('pipeline_transformed_status', '')
            }
            pipelines.append(pipeline)

    return pipelines


def _load_bw_performance_from_csv() -> List[Dict[str, Any]]:
    """Load SAP B/W system performance data from sample_data/bw_system_performance.csv."""
    records = []
    csv_path = os.path.join(SAMPLE_DATA_DIR, 'bw_system_performance.csv')

    if not os.path.exists(csv_path):
        return []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                record = {
                    'snapshot_ts': row.get('snapshot_ts', ''),
                    'storage_usage_tb': float(row.get('storage_usage_tb', 0)),
                    'storage_capacity_tb': float(row.get('storage_capacity_tb', 0)),
                    'memory_usage_tb': float(row.get('memory_usage_tb', 0)),
                    'memory_capacity_tb': float(row.get('memory_capacity_tb', 0)),
                    'ymd': row.get('ymd', '')
                }
                records.append(record)
            except:
                continue

    return records


def get_ticket_counts_by_platform() -> Dict[str, int]:
    """Get count of active tickets per platform from CSV data."""
    tickets = _load_tickets_from_csv()
    counts = defaultdict(int)

    for ticket in tickets:
        if ticket.get('is_active', True):
            counts[ticket['platform']] += 1

    return dict(counts)


def get_platforms() -> List[Dict[str, Any]]:
    """
    Get platform health data.

    Uses real data from CSV files where available:
    - Ticket counts from tickets.csv
    - SAP B/W memory/storage from bw_system_performance.csv
    - Pipeline data from pipelines.csv
    """
    # Get real ticket counts
    ticket_counts = get_ticket_counts_by_platform()

    # Get real SAP B/W performance data (latest record)
    bw_records = _load_bw_performance_from_csv()
    if bw_records:
        latest_bw = bw_records[-1]
        bw_memory = latest_bw['memory_usage_tb']
        bw_storage = latest_bw['storage_usage_tb']
        bw_memory_capacity = latest_bw['memory_capacity_tb']
    else:
        bw_memory = 18.2
        bw_storage = 54.7
        bw_memory_capacity = 24.0

    # Get real pipeline data
    pipeline_summary = get_pipeline_summary('edlap')
    edlap_failures = pipeline_summary.get('failed', 2)
    edlap_delays = pipeline_summary.get('delayed', 8)

    # Determine SAP B/W status based on memory usage
    if bw_memory >= 22:
        bw_status = 'critical'
        bw_status_label = 'Critical'
    elif bw_memory >= 20:
        bw_status = 'attention'
        bw_status_label = 'Attention'
    else:
        bw_status = 'healthy'
        bw_status_label = 'Healthy'

    # Determine EDLAP status based on pipeline failures
    if edlap_failures >= 10:
        edlap_status = 'critical'
        edlap_status_label = 'Critical'
    elif edlap_failures >= 5:
        edlap_status = 'attention'
        edlap_status_label = 'Attention'
    else:
        edlap_status = 'healthy'
        edlap_status_label = 'Healthy'

    return [
        {
            'id': 'edlap',
            'name': 'EDLAP',
            'subtitle': 'Enterprise Data Lake',
            'status': edlap_status,
            'status_label': edlap_status_label,
            'metrics': {
                'primary': {'label': 'Pipeline Failures', 'value': str(edlap_failures), 'threshold': '< 5'},
                'secondary': {'label': 'Data Delays', 'value': str(edlap_delays), 'threshold': '< 15'},
                'tertiary': {'label': 'Open Tickets', 'value': str(ticket_counts.get('edlap', 0))}
            },
            'trend': 'stable'
        },
        {
            'id': 'sapbw',
            'name': 'SAP B/W',
            'subtitle': 'Business Warehouse',
            'status': bw_status,
            'status_label': bw_status_label,
            'metrics': {
                'primary': {'label': 'Memory Usage', 'value': f'{bw_memory:.1f} TB', 'threshold': f'< {bw_memory_capacity:.0f} TB'},
                'secondary': {'label': 'Storage', 'value': f'{bw_storage:.1f} TB', 'threshold': '< 60 TB'},
                'tertiary': {'label': 'Open Tickets', 'value': str(ticket_counts.get('sapbw', 0))}
            },
            'trend': 'rising' if bw_memory >= 20 else 'stable'
        },
        {
            'id': 'tableau',
            'name': 'Tableau',
            'subtitle': 'Analytics & Reporting',
            'status': 'attention' if ticket_counts.get('tableau', 0) > 15 else 'healthy',
            'status_label': 'Attention' if ticket_counts.get('tableau', 0) > 15 else 'Healthy',
            'metrics': {
                'primary': {'label': 'Avg Load Time', 'value': '4.2s', 'threshold': '< 5s'},
                'secondary': {'label': 'CPU Peak', 'value': '72%', 'threshold': '< 80%'},
                'tertiary': {'label': 'Open Tickets', 'value': str(ticket_counts.get('tableau', 0))}
            },
            'trend': 'stable'
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
                'tertiary': {'label': 'Open Tickets', 'value': str(ticket_counts.get('alteryx', 0))}
            },
            'trend': 'stable'
        }
    ]


def get_tickets() -> List[Dict[str, Any]]:
    """
    Get ticket data from CSV file.

    Loads data from sample_data/tickets.csv with real ServiceNow ticket data.
    Ticket prefixes:
    - INC: Incident
    - RITM: Request Item
    - PRB: Problem
    """
    tickets = _load_tickets_from_csv()

    # Filter to only active tickets and return
    active_tickets = [t for t in tickets if t.get('is_active', True)]

    # Sort by priority (High first) then by age (oldest first)
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    active_tickets.sort(key=lambda t: (priority_order.get(t['priority'], 2), -int(t['age'].replace('d', '').replace('?', '0'))))

    return active_tickets


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
    Get SAP B/W performance data.
    Uses real memory data from bw_system_performance.csv where available.
    Metrics: users, memory (TB), avg dashboard load time, CPU
    """
    # Load real BW performance data
    bw_records = _load_bw_performance_from_csv()

    if bw_records:
        # Use real data - take the most recent records
        # The CSV has hourly snapshots, we'll use the last N records
        recent_records = bw_records[-min(len(bw_records), 289):]  # Up to ~12 days of hourly data

        timestamps = []
        memory_tb = []

        for record in recent_records:
            ts_str = record.get('snapshot_ts', '')
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    timestamps.append(ts.strftime('%Y-%m-%d %H:%M'))
                except:
                    continue
                memory_tb.append(record['memory_usage_tb'])

        # Get memory capacity from last record
        memory_capacity = recent_records[-1]['memory_capacity_tb'] if recent_records else 23.25

        # Generate simulated users and other metrics based on timestamps
        random.seed(43)
        users = []
        for i, ts_str in enumerate(timestamps):
            try:
                hour = int(ts_str.split(' ')[1].split(':')[0])
            except:
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
        timestamps = [ts.strftime('%Y-%m-%d %H:%M') for ts in generated_timestamps]
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
    thresholds = OUTLIER_THRESHOLDS['sapbw']
    users_outliers = detect_outliers(users, thresholds['users'])
    memory_outliers = detect_outliers(memory_tb, thresholds['memory_tb'])
    load_outliers = detect_outliers(load_times, thresholds['load_time_sec'])
    cpu_outliers = detect_outliers([min(100, v) for v in cpu_percent], thresholds['cpu_percent'])

    return {
        'timestamps': timestamps,
        'users': {'values': users, 'outliers': users_outliers},
        'memory_tb': {'values': [min(memory_capacity, v) for v in memory_tb], 'outliers': memory_outliers},
        'memory_capacity': memory_capacity,
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


def get_historical_stats(values: List[float], period: str = 'month') -> Dict[str, float]:
    """
    Calculate historical statistics (average and peak) for a metric.
    Simulates historical data based on current values with some variation.

    Args:
        values: Current period values to base simulation on
        period: 'month' for 30-day stats, 'week' for 7-day stats

    Returns:
        Dict with 'average' and 'peak' values
    """
    if not values:
        return {'average': 0, 'peak': 0}

    # Calculate base stats from current data
    current_avg = sum(values) / len(values)
    current_max = max(values)

    # Simulate historical variation
    random.seed(100)  # Consistent simulation

    if period == 'month':
        # Monthly stats: typically average is similar, peak is higher
        avg_factor = random.uniform(0.92, 1.08)
        peak_factor = random.uniform(1.1, 1.35)
    else:  # week
        # Weekly stats: closer to current values
        avg_factor = random.uniform(0.95, 1.05)
        peak_factor = random.uniform(1.05, 1.2)

    return {
        'average': round(current_avg * avg_factor, 2),
        'peak': round(current_max * peak_factor, 2)
    }


def get_ticket_history(platform_id: str = None, days: int = 30) -> Dict[str, Any]:
    """
    Get ticket history data for line graphs.

    Generates a simulated history of open tickets over time based on current ticket data.
    In production, this would query historical snapshots from the ticketing system.

    Args:
        platform_id: Filter to specific platform ('edlap', 'sapbw', 'tableau', 'alteryx') or None for all
        days: Number of days of history to generate

    Returns:
        Dict with timestamps and ticket counts (open and overdue/breached)
    """
    tickets = _load_tickets_from_csv()

    # Filter to platform if specified
    if platform_id:
        tickets = [t for t in tickets if t['platform'] == platform_id]

    # Get current count of active tickets
    active_tickets = [t for t in tickets if t.get('is_active', True)]
    current_count = len(active_tickets)

    # Count breached tickets as "overdue"
    breached_count = len([t for t in active_tickets if t.get('is_breached', False)])

    # Generate timestamps for the past N days (one point per day)
    now = datetime.now()
    timestamps = []
    open_tickets = []
    overdue_tickets = []

    random.seed(hash(platform_id or 'all') % 2**32)

    for i in range(days, -1, -1):
        date = now - timedelta(days=i)
        timestamps.append(date.strftime('%Y-%m-%d'))

        # Simulate ticket count history with some variation
        # Trend towards current value
        progress = (days - i) / days
        base_count = int(current_count * 0.7 + current_count * 0.6 * progress)

        # Add daily variation
        daily_variation = random.randint(-3, 4)
        count = max(0, base_count + daily_variation)

        # Weekday vs weekend pattern (fewer tickets opened on weekends)
        if date.weekday() >= 5:
            count = int(count * 0.85)

        open_tickets.append(count)

        # Overdue/breached count is typically 15-35% of open tickets
        overdue_base = int(count * (0.15 + 0.2 * random.random()))
        overdue_variation = random.randint(-1, 1)
        overdue = max(0, min(count, overdue_base + overdue_variation))

        # Make sure the last value matches actual data
        if i == 0:
            overdue = breached_count

        overdue_tickets.append(overdue)

    # Make sure the last value matches actual current count
    open_tickets[-1] = current_count

    return {
        'timestamps': timestamps,
        'open_tickets': {'values': open_tickets, 'outliers': []},
        'overdue_tickets': {'values': overdue_tickets, 'outliers': []},
        'current_count': current_count,
        'breached_count': breached_count
    }


def get_bw_memory_stats_30days() -> Dict[str, float]:
    """
    Get average and peak memory usage from the last 30 days of B/W data.

    Calculates actual statistics from the bw_system_performance.csv file.

    Returns:
        Dict with 'average' and 'peak' values in TB
    """
    records = _load_bw_performance_from_csv()

    if not records:
        # Fallback if no data available
        return {'average': 19.5, 'peak': 21.9}

    # Get memory values from all available records (CSV should have ~30 days)
    memory_values = [r['memory_usage_tb'] for r in records if r.get('memory_usage_tb')]

    if not memory_values:
        return {'average': 19.5, 'peak': 21.9}

    avg_memory = sum(memory_values) / len(memory_values)
    peak_memory = max(memory_values)

    return {
        'average': round(avg_memory, 2),
        'peak': round(peak_memory, 2)
    }


def get_pipeline_summary(platform_id: str = 'edlap') -> Dict[str, int]:
    """
    Get current pipeline counts for platform bar chart.

    Args:
        platform_id: 'edlap' or 'sapbw'

    Returns pipeline status counts from real CSV data.
    """
    pipelines = _load_pipelines_from_csv()

    # Filter to requested platform
    platform_pipelines = [p for p in pipelines if p['platform'] == platform_id]

    if not platform_pipelines:
        # Fallback to generated data
        random.seed(42 if platform_id == 'edlap' else 43)
        total = 245 if platform_id == 'edlap' else 150
        failed = random.randint(1, 5)
        delayed = random.randint(3, 10)
        successful = total - failed - delayed
        return {
            'successful': successful,
            'delayed': delayed,
            'failed': failed,
            'total': total
        }

    # Count by status
    successful = 0
    delayed = 0
    failed = 0
    not_applicable = 0

    for p in platform_pipelines:
        status = p.get('status', '').lower()
        orig_status = p.get('original_status', '').lower()

        if 'failed' in status or orig_status == 'r' or 'failed' in orig_status:
            failed += 1
        elif 'delayed' in status:
            delayed += 1
        elif 'not applicable' in status:
            not_applicable += 1
        elif 'within expected' in status or orig_status == 'g' or 'succeeded' in orig_status:
            successful += 1
        else:
            successful += 1  # Default to successful if status unclear

    total = successful + delayed + failed + not_applicable

    return {
        'successful': successful,
        'delayed': delayed,
        'failed': failed,
        'not_applicable': not_applicable,
        'total': total
    }
