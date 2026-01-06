"""
Data module for Platform Health Dashboard.
In production, this would connect to your actual data sources (ServiceNow, monitoring APIs, etc.)
"""

from typing import List, Dict, Any


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
            'owner': 'M. Schmidt'
        },
        {
            'id': 'INC001198',
            'platform': 'tableau',
            'title': 'Slow refresh on Executive KPIs',
            'priority': 'High',
            'age': '5d',
            'owner': 'K. Weber'
        },
        {
            'id': 'INC001201',
            'platform': 'sapbw',
            'title': 'Memory spike during month-end',
            'priority': 'Medium',
            'age': '2d',
            'owner': 'SAP Team'
        },
        {
            'id': 'INC001189',
            'platform': 'edlap',
            'title': 'Pipeline delay - Finance feed',
            'priority': 'Low',
            'age': '4d',
            'owner': 'Data Ops'
        },
        {
            'id': 'INC001156',
            'platform': 'tableau',
            'title': 'Report export failing for GBIE',
            'priority': 'Medium',
            'age': '7d',
            'owner': 'K. Weber'
        },
        {
            'id': 'INC001145',
            'platform': 'sapbw',
            'title': 'BW query performance degradation',
            'priority': 'High',
            'age': '6d',
            'owner': 'SAP Team'
        },
        {
            'id': 'INC001132',
            'platform': 'alteryx',
            'title': 'Scheduled workflow failed - HR extract',
            'priority': 'Low',
            'age': '1d',
            'owner': 'Data Ops'
        },
        {
            'id': 'INC001128',
            'platform': 'edlap',
            'title': 'Data quality issue in customer dimension',
            'priority': 'Medium',
            'age': '8d',
            'owner': 'Data Ops'
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
