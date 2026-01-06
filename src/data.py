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
