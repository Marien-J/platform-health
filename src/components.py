"""
UI Components for Platform Health Dashboard.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any

# Color schemes for status indicators (ALDI colors)
STATUS_COLORS = {
    'healthy': {'bg': '#439539', 'light': '#E8F5E6', 'text': '#2D6427'},
    'attention': {'bg': '#FF7800', 'light': '#FFF3E6', 'text': '#B35500'},
    'critical': {'bg': '#D70000', 'light': '#FDEDED', 'text': '#990000'}
}

PRIORITY_COLORS = {
    'High': {'bg': '#FDEDED', 'text': '#990000'},      # ALDI red
    'Medium': {'bg': '#FFF3E6', 'text': '#B35500'},    # ALDI orange
    'Low': {'bg': '#F5F4F0', 'text': '#393A34'}        # ALDI beige/charcoal
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
        'border': f"2px solid {colors['bg'] if is_selected else '#E5E7EB'}",
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
    """Generate ServiceNow URL for a ticket based on its prefix."""
    from utils import generate_servicenow_link
    return generate_servicenow_link(ticket_id)


def create_ticket_detail_modal() -> dbc.Modal:
    """Create the ticket detail modal component."""
    return dbc.Modal([
        dbc.ModalHeader([
            html.Div([
                html.Span(id='modal-header-ticket-id', className="modal-header-ticket-id"),
                html.Span(id='modal-status-badge', className="modal-status-badge")
            ], className="modal-header-content"),
            html.Button(
                html.I(className="fa fa-times"),
                className="btn-close-modal-navy",
                id='modal-close-btn',
                n_clicks=0
            )
        ], close_button=False, className="modal-header-navy"),
        dbc.ModalBody([
            # Title (bold)
            html.Div([
                html.H5(id='modal-ticket-title', className="modal-ticket-title-text")
            ], className="modal-title-section"),

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

            # Owner
            html.Div([
                html.Span("Assigned To: ", className="modal-label"),
                html.Span(id='modal-owner')
            ], className="modal-field"),

            # Created Date
            html.Div([
                html.Span("Created: ", className="modal-label"),
                html.Span(id='modal-created-date')
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
                html.Div(id='modal-description', className="ticket-description-box")
            ], className="modal-description-section")
        ]),
        dbc.ModalFooter([
            dbc.Button(
                [html.I(className="fa fa-external-link-alt me-2"), "Open in ServiceNow"],
                id='modal-servicenow-btn',
                href="#",
                target="_blank",
                color="primary",
                className="modal-servicenow-btn",
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


# Graph colors for consistent theming (ALDI colors)
GRAPH_COLORS = {
    'primary': '#00005F',      # ALDI Navy
    'secondary': '#55C3F0',    # ALDI Light Blue
    'success': '#439539',      # ALDI Green
    'warning': '#FF7800',      # ALDI Orange
    'danger': '#D70000',       # ALDI Red
    'info': '#55C3F0',         # ALDI Light Blue
    'neutral': '#393A34',      # ALDI Charcoal
    'machines': [
        '#00005F', '#55C3F0', '#439539', '#FF7800',
        '#D70000', '#95C11F', '#FFC800', '#D1CAB4'
    ]
}


def _create_base_figure(title: str = None) -> go.Figure:
    """Create a base figure with consistent ALDI styling."""
    fig = go.Figure()
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=14, color='#00005F'),  # ALDI Navy
            x=0,
            xanchor='left'
        ) if title else None,
        font=dict(family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=20, t=50 if title else 20, b=40),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='top',
            y=1.12,
            xanchor='right',
            x=1,
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.8)'
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#D1CAB4',  # ALDI Beige
            linecolor='#D1CAB4',  # ALDI Beige
            tickfont=dict(size=10, color='#393A34')  # ALDI Charcoal
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#D1CAB4',  # ALDI Beige
            linecolor='#D1CAB4',  # ALDI Beige
            tickfont=dict(size=10, color='#393A34'),  # ALDI Charcoal
            zeroline=False
        )
    )
    return fig


def _add_threshold_lines(fig: go.Figure, thresholds: Dict[str, float], y_max: float) -> go.Figure:
    """Add warning and critical threshold lines to a figure."""
    if 'warning' in thresholds:
        fig.add_hline(
            y=thresholds['warning'],
            line_dash='dot',
            line_color=GRAPH_COLORS['warning'],
            line_width=1.5,
            annotation_text=f"Warning: {thresholds['warning']}",
            annotation_position='top left',
            annotation_font_size=9,
            annotation_font_color=GRAPH_COLORS['warning'],
            annotation_bgcolor='rgba(255,255,255,0.8)'
        )
    if 'critical' in thresholds:
        fig.add_hline(
            y=thresholds['critical'],
            line_dash='dash',
            line_color=GRAPH_COLORS['danger'],
            line_width=1.5,
            annotation_text=f"Critical: {thresholds['critical']}",
            annotation_position='top left',
            annotation_font_size=9,
            annotation_font_color=GRAPH_COLORS['danger'],
            annotation_bgcolor='rgba(255,255,255,0.8)'
        )
    return fig


def _add_avg_peak_lines(fig: go.Figure, avg_value: float, peak_value: float,
                        period_label: str = 'month') -> go.Figure:
    """Add average and peak reference lines to a figure."""
    fig.add_hline(
        y=avg_value,
        line_dash='dash',
        line_color='#393A34',  # ALDI Charcoal
        line_width=1.5,
        annotation_text=f'Avg ({period_label}): {avg_value:.1f}',
        annotation_position='top left',
        annotation_font_size=9,
        annotation_font_color='#393A34',  # ALDI Charcoal
        annotation_bgcolor='rgba(255,255,255,0.8)'
    )
    fig.add_hline(
        y=peak_value,
        line_dash='dot',
        line_color='#55C3F0',  # ALDI Light Blue
        line_width=1.5,
        annotation_text=f'Peak ({period_label}): {peak_value:.1f}',
        annotation_position='top left',
        annotation_font_size=9,
        annotation_font_color='#55C3F0',  # ALDI Light Blue
        annotation_bgcolor='rgba(255,255,255,0.8)'
    )
    return fig


def _add_above_avg_markers(fig: go.Figure, timestamps: List[str], values: List[float],
                           avg_value: float) -> go.Figure:
    """Add orange markers for values exceeding the average."""
    above_avg_x, above_avg_y = [], []

    for i, val in enumerate(values):
        if val > avg_value:
            above_avg_x.append(timestamps[i])
            above_avg_y.append(val)

    if above_avg_x:
        fig.add_trace(go.Scatter(
            x=above_avg_x, y=above_avg_y,
            mode='markers',
            marker=dict(size=8, color=GRAPH_COLORS['warning'], symbol='diamond'),
            name='Above Avg',
            hoverinfo='skip',
            showlegend=False
        ))

    return fig


def create_edlap_drilldown(data: Dict[str, Any]) -> html.Div:
    """Create EDLAP-specific drill-down graphs."""
    from data import get_historical_stats, get_pipeline_summary, get_ticket_history

    timestamps = data['timestamps']

    # Graph 1: Active Users - with avg/peak of last month, no warning/critical
    fig_users = _create_base_figure('Active Users')
    users_data = data['users']
    fig_users.add_trace(go.Scatter(
        x=timestamps, y=users_data['values'],
        mode='lines',
        name='Users',
        line=dict(color=GRAPH_COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 0, 95, 0.1)'  # ALDI Navy with opacity
    ))
    # Add avg/peak lines instead of warning/critical
    user_stats = get_historical_stats(users_data['values'], 'month')
    _add_avg_peak_lines(fig_users, user_stats['average'], user_stats['peak'], 'month')

    # Graph 2: Pipelines - BAR CHART showing successful/delayed/failed (from real CSV data)
    pipeline_summary = get_pipeline_summary('edlap')
    fig_pipelines = _create_base_figure('Pipeline Status (Current)')
    fig_pipelines.add_trace(go.Bar(
        x=['Successful', 'Delayed', 'Failed'],
        y=[pipeline_summary['successful'], pipeline_summary['delayed'], pipeline_summary['failed']],
        marker_color=[GRAPH_COLORS['success'], GRAPH_COLORS['warning'], GRAPH_COLORS['danger']],
        text=[pipeline_summary['successful'], pipeline_summary['delayed'], pipeline_summary['failed']],
        textposition='outside',
        textfont=dict(size=14, color='#374151')
    ))
    fig_pipelines.update_layout(
        showlegend=False,
        yaxis=dict(title='Count', range=[0, max(pipeline_summary['successful'], 50) * 1.15]),
        xaxis=dict(title='')
    )

    # Graph 3: Open Tickets History (from real CSV data) - with avg/peak of last month
    ticket_history = get_ticket_history('edlap', days=30)
    fig_tickets = _create_base_figure('Open Tickets (30 days)')
    fig_tickets.add_trace(go.Scatter(
        x=ticket_history['timestamps'], y=ticket_history['open_tickets']['values'],
        mode='lines',
        name='Open Tickets',
        line=dict(color=GRAPH_COLORS['info'], width=2),
        fill='tozeroy',
        fillcolor='rgba(85, 195, 240, 0.1)'  # ALDI Light Blue with opacity
    ))
    fig_tickets.add_trace(go.Scatter(
        x=ticket_history['timestamps'], y=ticket_history['overdue_tickets']['values'],
        mode='lines',
        name='Breached',
        line=dict(color=GRAPH_COLORS['danger'], width=2)
    ))
    # Add avg/peak lines for open tickets instead of thresholds
    ticket_stats = get_historical_stats(ticket_history['open_tickets']['values'], 'month')
    _add_avg_peak_lines(fig_tickets, ticket_stats['average'], ticket_stats['peak'], 'month')

    return html.Div([
        html.Div([
            dcc.Graph(figure=fig_users, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container'),
        html.Div([
            dcc.Graph(figure=fig_pipelines, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container'),
        html.Div([
            dcc.Graph(figure=fig_tickets, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container')
    ], className='drilldown-graphs-grid')


def create_sapbw_drilldown(data: Dict[str, Any]) -> html.Div:
    """Create SAP B/W-specific drill-down graphs."""
    from data import get_historical_stats, get_pipeline_summary, get_ticket_history, get_bw_memory_stats_30days

    timestamps = data['timestamps']

    # Get memory capacity from data (real from CSV)
    memory_capacity = data.get('memory_capacity', 23.25)

    # Graph 1: Active Users - with avg/peak of last month, no warning/critical
    fig_users = _create_base_figure('Active Users')
    users_data = data['users']
    fig_users.add_trace(go.Scatter(
        x=timestamps, y=users_data['values'],
        mode='lines',
        name='Users',
        line=dict(color=GRAPH_COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 0, 95, 0.1)'  # ALDI Navy with opacity
    ))
    user_stats = get_historical_stats(users_data['values'], 'month')
    _add_avg_peak_lines(fig_users, user_stats['average'], user_stats['peak'], 'month')

    # Graph 2: Memory (TB) with actual capacity reference - keep thresholds (hardware limit)
    fig_memory = _create_base_figure('Memory Usage (TB)')
    memory_data = data['memory_tb']
    fig_memory.add_trace(go.Scatter(
        x=timestamps, y=memory_data['values'],
        mode='lines',
        name='Memory (TB)',
        line=dict(color=GRAPH_COLORS['secondary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(85, 195, 240, 0.1)'  # ALDI Light Blue with opacity
    ))
    fig_memory.add_hline(y=memory_capacity, line_dash='solid', line_color='#393A34', line_width=1,
                         annotation_text=f'Max: {memory_capacity:.1f}TB', annotation_position='top left',
                         annotation_font_size=9, annotation_bgcolor='rgba(255,255,255,0.8)')
    # Use actual 30-day avg/peak from CSV data instead of hardcoded thresholds
    memory_stats = get_bw_memory_stats_30days()
    _add_avg_peak_lines(fig_memory, memory_stats['average'], memory_stats['peak'], '30d')
    fig_memory.update_layout(yaxis=dict(range=[0, memory_capacity + 2]))

    # Graph 3: Pipeline Status - BAR CHART (like EDLAP)
    pipeline_summary = get_pipeline_summary('sapbw')
    fig_pipelines = _create_base_figure('Pipeline Status (Current)')
    fig_pipelines.add_trace(go.Bar(
        x=['Successful', 'Delayed', 'Failed'],
        y=[pipeline_summary['successful'], pipeline_summary['delayed'], pipeline_summary['failed']],
        marker_color=[GRAPH_COLORS['success'], GRAPH_COLORS['warning'], GRAPH_COLORS['danger']],
        text=[pipeline_summary['successful'], pipeline_summary['delayed'], pipeline_summary['failed']],
        textposition='outside',
        textfont=dict(size=14, color='#374151')
    ))
    fig_pipelines.update_layout(
        showlegend=False,
        yaxis=dict(title='Count', range=[0, max(pipeline_summary['successful'], 50) * 1.15]),
        xaxis=dict(title='')
    )

    # Graph 4: Open Tickets History - line chart with avg/peak
    ticket_history = get_ticket_history('sapbw', days=30)
    fig_tickets = _create_base_figure('Open Tickets (30 days)')
    fig_tickets.add_trace(go.Scatter(
        x=ticket_history['timestamps'], y=ticket_history['open_tickets']['values'],
        mode='lines',
        name='Open Tickets',
        line=dict(color=GRAPH_COLORS['info'], width=2),
        fill='tozeroy',
        fillcolor='rgba(85, 195, 240, 0.1)'
    ))
    fig_tickets.add_trace(go.Scatter(
        x=ticket_history['timestamps'], y=ticket_history['overdue_tickets']['values'],
        mode='lines',
        name='Breached',
        line=dict(color=GRAPH_COLORS['danger'], width=2)
    ))
    ticket_stats = get_historical_stats(ticket_history['open_tickets']['values'], 'month')
    _add_avg_peak_lines(fig_tickets, ticket_stats['average'], ticket_stats['peak'], 'month')

    # Graph 5: Dashboard Load Time - with avg/peak of last week, orange when above avg
    fig_load = _create_base_figure('Avg Dashboard Load Time (sec)')
    load_data = data['load_time_sec']
    fig_load.add_trace(go.Scatter(
        x=timestamps, y=load_data['values'],
        mode='lines',
        name='Load Time (s)',
        line=dict(color=GRAPH_COLORS['info'], width=2),
        fill='tozeroy',
        fillcolor='rgba(85, 195, 240, 0.1)'  # ALDI Light Blue with opacity
    ))
    load_stats = get_historical_stats(load_data['values'], 'week')
    _add_avg_peak_lines(fig_load, load_stats['average'], load_stats['peak'], 'week')
    _add_above_avg_markers(fig_load, timestamps, load_data['values'], load_stats['average'])

    # Graph 6: CPU Usage - with avg/peak of last week, orange when above avg
    fig_cpu = _create_base_figure('CPU Utilization (%)')
    cpu_data = data['cpu_percent']
    fig_cpu.add_trace(go.Scatter(
        x=timestamps, y=cpu_data['values'],
        mode='lines',
        name='CPU %',
        line=dict(color=GRAPH_COLORS['success'], width=2),
        fill='tozeroy',
        fillcolor='rgba(67, 149, 57, 0.1)'  # ALDI Green with opacity
    ))
    cpu_stats = get_historical_stats(cpu_data['values'], 'week')
    _add_avg_peak_lines(fig_cpu, cpu_stats['average'], cpu_stats['peak'], 'week')
    _add_above_avg_markers(fig_cpu, timestamps, cpu_data['values'], cpu_stats['average'])
    fig_cpu.update_layout(yaxis=dict(range=[0, 105]))

    return html.Div([
        html.Div([
            dcc.Graph(figure=fig_users, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container'),
        html.Div([
            dcc.Graph(figure=fig_memory, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container'),
        html.Div([
            dcc.Graph(figure=fig_pipelines, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container'),
        html.Div([
            dcc.Graph(figure=fig_tickets, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container'),
        html.Div([
            dcc.Graph(figure=fig_load, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container'),
        html.Div([
            dcc.Graph(figure=fig_cpu, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container')
    ], className='drilldown-graphs-grid six-cols')


def create_multi_machine_drilldown(data: Dict[str, Any], platform_name: str,
                                   load_time_label: str = 'Avg Dashboard Load Time (sec)',
                                   selected_machine: str = None) -> html.Div:
    """Create drill-down graphs for multi-machine platforms (Tableau/Alteryx)."""
    from data import get_historical_stats, get_ticket_history

    timestamps = data['timestamps']
    machines = data['machines']
    aggregated = data['aggregated']
    platform_id = 'tableau' if 'TAB' in list(machines.keys())[0] else 'alteryx'

    # Graph 1: Total Users (aggregated) - with avg/peak of last month
    fig_users = _create_base_figure('Total Active Users')
    users_data = aggregated['users']
    fig_users.add_trace(go.Scatter(
        x=timestamps, y=users_data['values'],
        mode='lines',
        name='Total Users',
        line=dict(color=GRAPH_COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 0, 95, 0.1)'  # ALDI Navy with opacity
    ))
    user_stats = get_historical_stats(users_data['values'], 'month')
    _add_avg_peak_lines(fig_users, user_stats['average'], user_stats['peak'], 'month')

    # Graph 2: Memory Usage - simplified legend, show per-machine only if one selected
    fig_memory = _create_base_figure(f'Memory Usage (%) - {len(machines)} Machines')

    if selected_machine and selected_machine in machines:
        # Show only selected machine
        machine_data = machines[selected_machine]
        fig_memory.add_trace(go.Scatter(
            x=timestamps, y=machine_data['memory_percent'],
            mode='lines',
            name=selected_machine,
            line=dict(color=GRAPH_COLORS['primary'], width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 0, 95, 0.1)'  # ALDI Navy with opacity
        ))
    else:
        # Show per-machine lines (lighter, no legend to avoid clutter)
        for i, (machine_name, machine_data) in enumerate(machines.items()):
            fig_memory.add_trace(go.Scatter(
                x=timestamps, y=machine_data['memory_percent'],
                mode='lines',
                name=machine_name,
                line=dict(color=GRAPH_COLORS['machines'][i % len(GRAPH_COLORS['machines'])], width=1),
                opacity=0.35,
                showlegend=False
            ))
        # Add average line (bold, with legend)
        memory_data = aggregated['memory_percent']
        fig_memory.add_trace(go.Scatter(
            x=timestamps, y=memory_data['values'],
            mode='lines',
            name='Average',
            line=dict(color=GRAPH_COLORS['secondary'], width=3),
        ))

    mem_stats = get_historical_stats(aggregated['memory_percent']['values'], 'week')
    _add_avg_peak_lines(fig_memory, mem_stats['average'], mem_stats['peak'], 'week')
    fig_memory.update_layout(yaxis=dict(range=[0, 105]))

    # Graph 3: Load Time (aggregated) - with avg/peak of last week, orange when above avg
    fig_load = _create_base_figure(load_time_label)
    load_data = aggregated['load_time_sec']
    fig_load.add_trace(go.Scatter(
        x=timestamps, y=load_data['values'],
        mode='lines',
        name='Load Time',
        line=dict(color=GRAPH_COLORS['info'], width=2),
        fill='tozeroy',
        fillcolor='rgba(85, 195, 240, 0.1)'  # ALDI Light Blue with opacity
    ))
    load_stats = get_historical_stats(load_data['values'], 'week')
    _add_avg_peak_lines(fig_load, load_stats['average'], load_stats['peak'], 'week')
    _add_above_avg_markers(fig_load, timestamps, load_data['values'], load_stats['average'])

    # Graph 4: CPU Utilization - simplified legend, show per-machine only if one selected
    fig_cpu = _create_base_figure(f'CPU Utilization (%) - {len(machines)} Machines')

    if selected_machine and selected_machine in machines:
        # Show only selected machine
        machine_data = machines[selected_machine]
        fig_cpu.add_trace(go.Scatter(
            x=timestamps, y=machine_data['cpu_percent'],
            mode='lines',
            name=selected_machine,
            line=dict(color=GRAPH_COLORS['success'], width=2),
            fill='tozeroy',
            fillcolor='rgba(67, 149, 57, 0.1)'  # ALDI Green with opacity
        ))
    else:
        # Show per-machine lines (lighter, no legend)
        for i, (machine_name, machine_data) in enumerate(machines.items()):
            fig_cpu.add_trace(go.Scatter(
                x=timestamps, y=machine_data['cpu_percent'],
                mode='lines',
                name=machine_name,
                line=dict(color=GRAPH_COLORS['machines'][i % len(GRAPH_COLORS['machines'])], width=1),
                opacity=0.35,
                showlegend=False
            ))
        # Add average line (bold, with legend)
        cpu_data = aggregated['cpu_percent']
        fig_cpu.add_trace(go.Scatter(
            x=timestamps, y=cpu_data['values'],
            mode='lines',
            name='Average',
            line=dict(color=GRAPH_COLORS['success'], width=3),
        ))

    cpu_stats = get_historical_stats(aggregated['cpu_percent']['values'], 'week')
    _add_avg_peak_lines(fig_cpu, cpu_stats['average'], cpu_stats['peak'], 'week')
    _add_above_avg_markers(fig_cpu, timestamps, aggregated['cpu_percent']['values'], cpu_stats['average'])
    fig_cpu.update_layout(yaxis=dict(range=[0, 105]))

    # Graph 5: Open Tickets History - line chart with avg/peak
    ticket_history = get_ticket_history(platform_id, days=30)
    fig_tickets = _create_base_figure('Open Tickets (30 days)')
    fig_tickets.add_trace(go.Scatter(
        x=ticket_history['timestamps'], y=ticket_history['open_tickets']['values'],
        mode='lines',
        name='Open Tickets',
        line=dict(color=GRAPH_COLORS['info'], width=2),
        fill='tozeroy',
        fillcolor='rgba(85, 195, 240, 0.1)'
    ))
    fig_tickets.add_trace(go.Scatter(
        x=ticket_history['timestamps'], y=ticket_history['overdue_tickets']['values'],
        mode='lines',
        name='Breached',
        line=dict(color=GRAPH_COLORS['danger'], width=2)
    ))
    ticket_stats = get_historical_stats(ticket_history['open_tickets']['values'], 'month')
    _add_avg_peak_lines(fig_tickets, ticket_stats['average'], ticket_stats['peak'], 'month')

    # Create machine status summary with clickable buttons
    machine_status_items = []
    for machine_name, machine_data in machines.items():
        # Calculate recent metrics (last 12 data points = 1 hour)
        recent_cpu = machine_data['cpu_percent'][-12:]
        recent_mem = machine_data['memory_percent'][-12:]
        avg_cpu = sum(recent_cpu) / len(recent_cpu)
        avg_mem = sum(recent_mem) / len(recent_mem)
        max_cpu = max(recent_cpu)
        max_mem = max(recent_mem)

        # Determine load status based on recent averages
        combined_load = (avg_cpu + avg_mem) / 2

        # Check for notable events
        had_cpu_spike = max_cpu >= 95
        had_mem_spike = max_mem >= 95
        cpu_above_daily_avg = avg_cpu > sum(machine_data['cpu_percent']) / len(machine_data['cpu_percent']) * 1.1

        # Determine status and color
        if combined_load >= 75 or had_cpu_spike or had_mem_spike:
            status_color = GRAPH_COLORS['danger']
            status_class = 'machine-status-critical'
            if had_cpu_spike or had_mem_spike:
                status_text = 'Spike ↑'
            else:
                status_text = 'High load'
        elif combined_load >= 55 or cpu_above_daily_avg:
            status_color = GRAPH_COLORS['warning']
            status_class = 'machine-status-warning'
            if cpu_above_daily_avg:
                status_text = 'Above avg'
            else:
                status_text = 'Busy'
        elif combined_load >= 35:
            status_color = GRAPH_COLORS['success']
            status_class = 'machine-status-healthy'
            status_text = 'Normal'
        else:
            status_color = GRAPH_COLORS['info']
            status_class = 'machine-status-light'
            status_text = 'Light'

        # Add selected class if this machine is selected
        if selected_machine == machine_name:
            status_class += ' selected'

        machine_status_items.append(
            html.Div([
                html.Span(className='machine-status-dot', style={'backgroundColor': status_color}),
                html.Span(machine_name, className='machine-name'),
                html.Span(status_text, className='machine-alert-count')
            ],
            id={'type': 'machine-filter-btn', 'platform': platform_id, 'machine': machine_name},
            n_clicks=0,
            className=f'machine-status-item {status_class}')
        )

    return html.Div([
        # Machine status overview
        html.Div([
            html.Div([
                html.H6(f'{platform_name} Server Status', className='machine-status-title'),
                html.Button(
                    'Clear Filter',
                    id={'type': 'machine-clear-btn', 'platform': platform_id},
                    n_clicks=0,
                    className='btn-clear-machine-filter',
                    style={'display': 'inline-block' if selected_machine else 'none'}
                )
            ], className='machine-status-header'),
            html.Div(machine_status_items, className='machine-status-grid')
        ], className='machine-status-container'),
        # Graphs
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_users, config={'displayModeBar': False}, className='drilldown-graph')
            ], className='drilldown-graph-container'),
            html.Div([
                dcc.Graph(figure=fig_memory, config={'displayModeBar': False}, className='drilldown-graph')
            ], className='drilldown-graph-container'),
            html.Div([
                dcc.Graph(figure=fig_load, config={'displayModeBar': False}, className='drilldown-graph')
            ], className='drilldown-graph-container'),
            html.Div([
                dcc.Graph(figure=fig_cpu, config={'displayModeBar': False}, className='drilldown-graph')
            ], className='drilldown-graph-container'),
            html.Div([
                dcc.Graph(figure=fig_tickets, config={'displayModeBar': False}, className='drilldown-graph')
            ], className='drilldown-graph-container')
        ], className='drilldown-graphs-grid five-cols')
    ])


def create_performance_drilldown(platform_id: str, data: Dict[str, Any],
                                  selected_machine: str = None) -> html.Div:
    """Create the appropriate drill-down view based on platform."""
    if platform_id == 'edlap':
        return create_edlap_drilldown(data)
    elif platform_id == 'sapbw':
        return create_sapbw_drilldown(data)
    elif platform_id == 'tableau':
        return create_multi_machine_drilldown(data, 'Tableau', 'Avg Dashboard Load Time (sec)', selected_machine)
    elif platform_id == 'alteryx':
        return create_multi_machine_drilldown(data, 'Alteryx', 'Avg Workflow Execution Time (sec)', selected_machine)
    return html.Div("No performance data available")
