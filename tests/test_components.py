"""
Tests for the components module.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from components import (
    create_status_indicator,
    create_platform_card,
    create_summary_bar,
    create_ticket_table,
    STATUS_COLORS,
    PRIORITY_COLORS,
)


class TestStatusColors:
    """Tests for STATUS_COLORS configuration."""

    def test_has_all_statuses(self):
        """Should have colors for all status types."""
        assert "healthy" in STATUS_COLORS
        assert "attention" in STATUS_COLORS
        assert "critical" in STATUS_COLORS

    def test_color_structure(self):
        """Each status should have bg, light, and text colors."""
        for status, colors in STATUS_COLORS.items():
            assert "bg" in colors
            assert "light" in colors
            assert "text" in colors


class TestPriorityColors:
    """Tests for PRIORITY_COLORS configuration."""

    def test_has_all_priorities(self):
        """Should have colors for all priority levels."""
        assert "High" in PRIORITY_COLORS
        assert "Medium" in PRIORITY_COLORS
        assert "Low" in PRIORITY_COLORS


class TestCreateStatusIndicator:
    """Tests for create_status_indicator function."""

    def test_returns_div(self):
        """Should return a Dash html.Div component."""
        from dash import html

        indicator = create_status_indicator("healthy")
        assert isinstance(indicator, html.Div)

    def test_has_correct_class(self):
        """Should have status-indicator class."""
        indicator = create_status_indicator("healthy")
        assert indicator.className == "status-indicator"


class TestCreatePlatformCard:
    """Tests for create_platform_card function."""

    def test_returns_card(self):
        """Should return a Dash dbc.Card component."""
        import dash_bootstrap_components as dbc

        platform = {
            "id": "test",
            "name": "Test Platform",
            "subtitle": "Test",
            "status": "healthy",
            "status_label": "Healthy",
            "metrics": {
                "primary": {"label": "Test", "value": "1"},
                "secondary": {"label": "Test", "value": "2"},
                "tertiary": {"label": "Test", "value": "3"},
            },
        }

        card = create_platform_card(platform)
        assert isinstance(card, dbc.Card)

    def test_selected_state(self):
        """Should apply different styling when selected."""
        platform = {
            "id": "test",
            "name": "Test",
            "subtitle": "Test",
            "status": "healthy",
            "status_label": "Healthy",
            "metrics": {
                "primary": {"label": "Test", "value": "1"},
                "secondary": {"label": "Test", "value": "2"},
                "tertiary": {"label": "Test", "value": "3"},
            },
        }

        card_not_selected = create_platform_card(platform, is_selected=False)
        card_selected = create_platform_card(platform, is_selected=True)

        # Style should be different
        assert card_not_selected.style != card_selected.style


class TestCreateSummaryBar:
    """Tests for create_summary_bar function."""

    def test_returns_div(self):
        """Should return a Dash html.Div component."""
        from dash import html

        counts = {"healthy": 2, "attention": 1, "critical": 1, "total_tickets": 100}

        bar = create_summary_bar(counts)
        assert isinstance(bar, html.Div)


class TestCreateTicketTable:
    """Tests for create_ticket_table function."""

    def test_empty_tickets(self):
        """Should show 'No tickets found' when empty."""
        from dash import html

        table = create_ticket_table([])
        assert isinstance(table, html.Div)
        assert "No tickets found" in str(table)

    def test_with_tickets(self):
        """Should return a table when tickets provided."""
        import dash_bootstrap_components as dbc

        tickets = [
            {
                "id": "INC001",
                "platform": "test",
                "title": "Test ticket",
                "priority": "High",
                "age": "1d",
                "owner": "Test User",
            }
        ]

        table = create_ticket_table(tickets)
        assert isinstance(table, dbc.Table)
