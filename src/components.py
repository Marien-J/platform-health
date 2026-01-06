"""
UI Components for Platform Health Dashboard.
"""

from dash import html
import dash_bootstrap_components as dbc
from typing import List, Dict, Any

# ALDI colour schemes for status indicators
STATUS_COLORS = {
    'healthy': {'bg': '#439539', 'light': '#E8F5E6', 'text': '#2D6626'},
    'attention': {'bg': '#FF7800', 'light': '#FFF3E6', 'text': '#B35500'},
    'critical': {'bg': '#D70000', 'light': '#FDEDED', 'text': '#990000'}
}

PRIORITY_COLORS = {
    'High': {'bg': '#FDEDED', 'text': '#D70000'},
    'Medium': {'bg': '#FFF3E6', 'text': '#FF7800'},
    'Low': {'bg': '#E5E7EB', 'text': '#393A34'}
}


def create_status_indicator(status: str) -> html.Div:
    """Create a status dot indicator."""
    colors = STATUS_COLORS.get(status, STATUS_COLORS['healthy'])
    
    style = {
        'width': '12px',
        'height': '12px',
        'borderRadius': '50%',
        'backgroundColor': colors['bg'],
        'display': 'inline-block'
    }
    
    if status == 'critical':
        style['boxShadow'] = f"0 0 8px {colors['bg']}"
        style['animation'] = 'pulse 2s infinite'
    
    return html.Div(className='status-indicator', style=style)


def create_platform_card(platform: Dict[str, Any], is_selected: bool = False) -> dbc.Card:
    """Create a platform health card."""
    status = platform['status']
    colors = STATUS_COLORS.get(status, STATUS_COLORS['healthy'])
    metrics = platform['metrics']
    
    card_style = {
        'cursor': 'pointer',
        'transition': 'all 0.2s ease',
        'border': f"2px solid {colors['bg'] if is_selected else '#D1CAB4'}",
        'backgroundColor': colors['light'] if is_selected else '#FFFFFF'
    }
    
    if is_selected:
        card_style['boxShadow'] = f"0 4px 12px {colors['bg']}25"
    
    return dbc.Card([
        dbc.CardBody([
            # Header with name and status
            html.Div([
                html.Div([
                    html.H5(platform['name'], className="card-title mb-0"),
                    html.Small(platform['subtitle'], className="text-muted")
                ]),
                create_status_indicator(status)
            ], className="d-flex justify-content-between align-items-start mb-2"),
            
            # Status badge
            html.Span(
                platform['status_label'],
                className="status-badge",
                style={
                    'backgroundColor': colors['light'],
                    'color': colors['text'],
                    'padding': '4px 12px',
                    'borderRadius': '20px',
                    'fontSize': '13px',
                    'fontWeight': '600',
                    'display': 'inline-block',
                    'marginBottom': '12px'
                }
            ),
            
            # Metrics
            html.Div([
                html.Div([
                    html.Span(metrics['primary']['label'], className="metric-label"),
                    html.Span(metrics['primary']['value'], className="metric-value")
                ], className="metric-row"),
                html.Div([
                    html.Span(metrics['secondary']['label'], className="metric-label"),
                    html.Span(metrics['secondary']['value'], className="metric-value")
                ], className="metric-row"),
                html.Div([
                    html.Span(metrics['tertiary']['label'], className="metric-label text-muted"),
                    html.Span(metrics['tertiary']['value'], className="metric-value text-muted")
                ], className="metric-row")
            ], className="metrics-container"),
            
            # Footer
            html.Div(
                "Click to drill down →",
                className="card-footer-hint"
            )
        ])
    ], className="platform-card", style=card_style)


def create_summary_bar(counts: Dict[str, int], platforms: List[Dict[str, Any]] = None) -> html.Div:
    """Create the summary bar showing overall counts and individual platform statuses."""
    items = []

    # Add overall counts
    items.extend([
        html.Div([
            html.Div(className="summary-dot", style={'backgroundColor': STATUS_COLORS['healthy']['bg']}),
            html.Span([html.Strong(str(counts['healthy'])), " Healthy"])
        ], className="summary-item"),

        html.Div([
            html.Div(className="summary-dot", style={'backgroundColor': STATUS_COLORS['attention']['bg']}),
            html.Span([html.Strong(str(counts['attention'])), " Attention"])
        ], className="summary-item"),

        html.Div([
            html.Div(className="summary-dot", style={'backgroundColor': STATUS_COLORS['critical']['bg']}),
            html.Span([html.Strong(str(counts['critical'])), " Critical"])
        ], className="summary-item")
    ])

    # Add separator
    if platforms:
        items.append(html.Div(className="summary-separator"))

    # Add individual platform statuses
    if platforms:
        for platform in platforms:
            status = platform['status']
            colors = STATUS_COLORS.get(status, STATUS_COLORS['healthy'])
            items.append(
                html.Div([
                    html.Div(className="summary-dot", style={'backgroundColor': colors['bg']}),
                    html.Span([
                        html.Strong(platform['name']),
                        f" - {platform['status_label']}"
                    ])
                ], className="summary-item platform-status")
            )

    # Add total tickets at the end
    items.append(
        html.Div([
            html.Span(["Total Open Tickets: ", html.Strong(str(counts['total_tickets']))])
        ], className="summary-item ms-auto")
    )

    return html.Div(items, className="summary-bar-inner")


def create_ticket_table(tickets: List[Dict[str, Any]]) -> html.Div:
    """Create the ticket table."""
    if not tickets:
        return html.Div(
            "No tickets found",
            className="text-center text-muted py-5"
        )
    
    # Table header
    header = html.Thead(
        html.Tr([
            html.Th("Ticket ID"),
            html.Th("Title"),
            html.Th("Priority"),
            html.Th("Age"),
            html.Th("Owner")
        ])
    )
    
    # Table rows
    rows = []
    for ticket in tickets:
        priority_colors = PRIORITY_COLORS.get(ticket['priority'], PRIORITY_COLORS['Low'])

        rows.append(
            html.Tr([
                html.Td(
                    html.Span(
                        ticket['id'],
                        className="ticket-link"
                    )
                ),
                html.Td(ticket['title']),
                html.Td(
                    html.Span(
                        ticket['priority'],
                        className="priority-badge",
                        style={
                            'backgroundColor': priority_colors['bg'],
                            'color': priority_colors['text']
                        }
                    )
                ),
                html.Td(ticket['age'], className="text-muted"),
                html.Td(ticket['owner'])
            ],
            id={'type': 'ticket-row', 'index': ticket['id']},
            className="ticket-row-clickable",
            n_clicks=0
            )
        )
    
    body = html.Tbody(rows, id='ticket-table-body')

    return dbc.Table(
        [header, body],
        striped=False,
        hover=True,
        responsive=True,
        className="ticket-table"
    )


def get_platform_name(platform_id: str) -> str:
    """Get the display name for a platform ID."""
    platform_names = {
        'edlap': 'EDLAP',
        'sapbw': 'SAP B/W',
        'tableau': 'Tableau',
        'alteryx': 'Alteryx'
    }
    return platform_names.get(platform_id, platform_id)


def get_servicenow_url(ticket_id: str) -> str:
    """Generate ServiceNow URL for a ticket."""
    return f"https://company.service-now.com/nav_to.do?uri=incident.do?sys_id={ticket_id}"


def create_ticket_detail_modal() -> dbc.Modal:
    """Create the ticket detail modal component."""
    return dbc.Modal([
        dbc.ModalHeader([
            dbc.ModalTitle(id='modal-ticket-title'),
            html.Button(
                html.I(className="fa fa-times"),
                className="btn-close-modal",
                id='modal-close-btn',
                n_clicks=0
            )
        ], close_button=False, className="modal-header-custom"),
        dbc.ModalBody([
            # Ticket ID with ServiceNow link
            html.Div([
                html.Span("Ticket ID: ", className="modal-label"),
                html.A(
                    id='modal-ticket-id',
                    href="#",
                    target="_blank",
                    className="modal-ticket-link"
                )
            ], className="modal-field"),

            # Platform with status badge
            html.Div([
                html.Span("Platform: ", className="modal-label"),
                html.Span(id='modal-platform-badge', className="modal-platform-badge")
            ], className="modal-field"),

            # Priority
            html.Div([
                html.Span("Priority: ", className="modal-label"),
                html.Span(id='modal-priority-badge', className="priority-badge")
            ], className="modal-field"),

            # Age / Created Date
            html.Div([
                html.Span("Age: ", className="modal-label"),
                html.Span(id='modal-age')
            ], className="modal-field"),

            html.Div([
                html.Span("Created: ", className="modal-label"),
                html.Span(id='modal-created-date')
            ], className="modal-field"),

            # Owner
            html.Div([
                html.Span("Assigned To: ", className="modal-label"),
                html.Span(id='modal-owner')
            ], className="modal-field"),

            # Last Updated
            html.Div([
                html.Span("Last Updated: ", className="modal-label"),
                html.Span(id='modal-last-updated')
            ], className="modal-field"),

            # Description
            html.Hr(className="modal-divider"),
            html.Div([
                html.H6("Description", className="modal-section-title"),
                html.P(id='modal-description', className="modal-description")
            ], className="modal-description-section")
        ]),
        dbc.ModalFooter([
            dbc.Button(
                [html.I(className="fa fa-external-link-alt me-2"), "Open in ServiceNow"],
                id='modal-servicenow-btn',
                href="#",
                target="_blank",
                color="primary",
                className="btn-servicenow",
                external_link=True
            ),
            dbc.Button(
                "Close",
                id='modal-footer-close-btn',
                className="btn-modal-close",
                color="secondary",
                outline=True
            )
        ])
    ], id='ticket-detail-modal', is_open=False, centered=True, size="lg", className="ticket-modal")
