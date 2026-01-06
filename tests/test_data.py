"""
Tests for the data module.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data import get_platforms, get_tickets, get_summary_counts


class TestGetPlatforms:
    """Tests for get_platforms function."""
    
    def test_returns_list(self):
        """Should return a list of platforms."""
        platforms = get_platforms()
        assert isinstance(platforms, list)
    
    def test_has_four_platforms(self):
        """Should return exactly 4 platforms."""
        platforms = get_platforms()
        assert len(platforms) == 4
    
    def test_platform_has_required_fields(self):
        """Each platform should have required fields."""
        platforms = get_platforms()
        required_fields = ['id', 'name', 'subtitle', 'status', 'status_label', 'metrics']
        
        for platform in platforms:
            for field in required_fields:
                assert field in platform, f"Platform missing field: {field}"
    
    def test_platform_status_valid(self):
        """Platform status should be one of healthy, attention, critical."""
        platforms = get_platforms()
        valid_statuses = ['healthy', 'attention', 'critical']
        
        for platform in platforms:
            assert platform['status'] in valid_statuses
    
    def test_metrics_structure(self):
        """Platform metrics should have primary, secondary, tertiary."""
        platforms = get_platforms()
        
        for platform in platforms:
            metrics = platform['metrics']
            assert 'primary' in metrics
            assert 'secondary' in metrics
            assert 'tertiary' in metrics
            
            # Each metric should have label and value
            for key in ['primary', 'secondary', 'tertiary']:
                assert 'label' in metrics[key]
                assert 'value' in metrics[key]


class TestGetTickets:
    """Tests for get_tickets function."""
    
    def test_returns_list(self):
        """Should return a list of tickets."""
        tickets = get_tickets()
        assert isinstance(tickets, list)
    
    def test_tickets_not_empty(self):
        """Should return at least one ticket."""
        tickets = get_tickets()
        assert len(tickets) > 0
    
    def test_ticket_has_required_fields(self):
        """Each ticket should have required fields."""
        tickets = get_tickets()
        required_fields = ['id', 'platform', 'title', 'priority', 'age', 'owner']
        
        for ticket in tickets:
            for field in required_fields:
                assert field in ticket, f"Ticket missing field: {field}"
    
    def test_ticket_priority_valid(self):
        """Ticket priority should be High, Medium, or Low."""
        tickets = get_tickets()
        valid_priorities = ['High', 'Medium', 'Low']
        
        for ticket in tickets:
            assert ticket['priority'] in valid_priorities
    
    def test_ticket_platform_exists(self):
        """Ticket platform should match a valid platform id."""
        tickets = get_tickets()
        platforms = get_platforms()
        valid_platform_ids = [p['id'] for p in platforms]
        
        for ticket in tickets:
            assert ticket['platform'] in valid_platform_ids


class TestGetSummaryCounts:
    """Tests for get_summary_counts function."""
    
    def test_returns_dict(self):
        """Should return a dictionary."""
        counts = get_summary_counts()
        assert isinstance(counts, dict)
    
    def test_has_required_keys(self):
        """Should have healthy, attention, critical, total_tickets keys."""
        counts = get_summary_counts()
        required_keys = ['healthy', 'attention', 'critical', 'total_tickets']
        
        for key in required_keys:
            assert key in counts
    
    def test_counts_are_integers(self):
        """All counts should be integers."""
        counts = get_summary_counts()
        
        for key, value in counts.items():
            assert isinstance(value, int)
    
    def test_counts_match_data(self):
        """Counts should match actual platform data."""
        counts = get_summary_counts()
        platforms = get_platforms()
        tickets = get_tickets()
        
        healthy_count = sum(1 for p in platforms if p['status'] == 'healthy')
        attention_count = sum(1 for p in platforms if p['status'] == 'attention')
        critical_count = sum(1 for p in platforms if p['status'] == 'critical')
        
        assert counts['healthy'] == healthy_count
        assert counts['attention'] == attention_count
        assert counts['critical'] == critical_count
        assert counts['total_tickets'] == len(tickets)
