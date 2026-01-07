"""
UI Components for Platform Health Dashboard.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any

# Color schemes for status indicators
STATUS_COLORS = {
    'healthy': {'bg': '#059669', 'light': '#D1FAE5', 'text': '#065F46'},
    'attention': {'bg': '#D97706', 'light': '#FEF3C7', 'text': '#92400E'},
    'critical': {'bg': '#DC2626', 'light': '#FEE2E2', 'text': '#991B1B'}
}

PRIORITY_COLORS = {
    'High': {'bg': '#FEE2E2', 'text': '#991B1B'},
    'Medium': {'bg': '#FEF3C7', 'text': '#92400E'},
    'Low': {'bg': '#E5E7EB', 'text': '#374151'}
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


# Graph colors for consistent theming
GRAPH_COLORS = {
    'primary': '#2563EB',      # Blue
    'secondary': '#7C3AED',    # Purple
    'success': '#059669',      # Green
    'warning': '#D97706',      # Orange/Amber
    'danger': '#DC2626',       # Red
    'info': '#0891B2',         # Cyan
    'neutral': '#6B7280',      # Gray
    'machines': [
        '#2563EB', '#7C3AED', '#059669', '#D97706',
        '#DC2626', '#0891B2', '#EC4899', '#F59E0B'
    ]
}


def _create_base_figure(title: str = None) -> go.Figure:
    """Create a base figure with consistent styling."""
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#374151')) if title else None,
        font=dict(family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=30, t=40 if title else 20, b=40),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5E7EB',
            linecolor='#D1D5DB',
            tickfont=dict(size=10, color='#6B7280')
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5E7EB',
            linecolor='#D1D5DB',
            tickfont=dict(size=10, color='#6B7280'),
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
            annotation_text='Warning',
            annotation_position='right',
            annotation_font_size=10,
            annotation_font_color=GRAPH_COLORS['warning']
        )
    if 'critical' in thresholds:
        fig.add_hline(
            y=thresholds['critical'],
            line_dash='dash',
            line_color=GRAPH_COLORS['danger'],
            line_width=1.5,
            annotation_text='Critical',
            annotation_position='right',
            annotation_font_size=10,
            annotation_font_color=GRAPH_COLORS['danger']
        )
    return fig


def _add_avg_peak_lines(fig: go.Figure, avg_value: float, peak_value: float,
                        period_label: str = 'month') -> go.Figure:
    """Add average and peak reference lines to a figure."""
    fig.add_hline(
        y=avg_value,
        line_dash='dash',
        line_color='#6B7280',
        line_width=1.5,
        annotation_text=f'Avg ({period_label})',
        annotation_position='right',
        annotation_font_size=10,
        annotation_font_color='#6B7280'
    )
    fig.add_hline(
        y=peak_value,
        line_dash='dot',
        line_color='#9333EA',
        line_width=1.5,
        annotation_text=f'Peak ({period_label})',
        annotation_position='right',
        annotation_font_size=10,
        annotation_font_color='#9333EA'
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
    from data import get_historical_stats, get_pipeline_summary

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
        fillcolor='rgba(37, 99, 235, 0.1)'
    ))
    # Add avg/peak lines instead of warning/critical
    user_stats = get_historical_stats(users_data['values'], 'month')
    _add_avg_peak_lines(fig_users, user_stats['average'], user_stats['peak'], 'month')

    # Graph 2: Pipelines - BAR CHART showing successful/delayed/failed
    pipeline_summary = get_pipeline_summary()
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

    # Graph 3: Tickets (open and overdue) - with avg/peak of last month
    fig_tickets = _create_base_figure('Tickets')
    fig_tickets.add_trace(go.Scatter(
        x=timestamps, y=data['open_tickets']['values'],
        mode='lines',
        name='Open Tickets',
        line=dict(color=GRAPH_COLORS['info'], width=2),
        fill='tozeroy',
        fillcolor='rgba(8, 145, 178, 0.1)'
    ))
    fig_tickets.add_trace(go.Scatter(
        x=timestamps, y=data['overdue_tickets']['values'],
        mode='lines',
        name='Overdue',
        line=dict(color=GRAPH_COLORS['danger'], width=2)
    ))
    # Add avg/peak lines for open tickets instead of thresholds
    ticket_stats = get_historical_stats(data['open_tickets']['values'], 'month')
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
    from data import get_historical_stats

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
        fillcolor='rgba(37, 99, 235, 0.1)'
    ))
    user_stats = get_historical_stats(users_data['values'], 'month')
    _add_avg_peak_lines(fig_users, user_stats['average'], user_stats['peak'], 'month')

    # Graph 2: Memory (TB) with 24TB max reference - keep thresholds (hardware limit)
    fig_memory = _create_base_figure('Memory Usage (TB)')
    memory_data = data['memory_tb']
    fig_memory.add_trace(go.Scatter(
        x=timestamps, y=memory_data['values'],
        mode='lines',
        name='Memory (TB)',
        line=dict(color=GRAPH_COLORS['secondary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(124, 58, 237, 0.1)'
    ))
    fig_memory.add_hline(y=24, line_dash='solid', line_color='#374151', line_width=1,
                         annotation_text='Max (24TB)', annotation_position='right',
                         annotation_font_size=10)
    _add_threshold_lines(fig_memory, {'warning': 20, 'critical': 22}, 24)
    fig_memory.update_layout(yaxis=dict(range=[0, 26]))

    # Graph 3: Dashboard Load Time - with avg/peak of last week, orange when above avg
    fig_load = _create_base_figure('Avg Dashboard Load Time (sec)')
    load_data = data['load_time_sec']
    fig_load.add_trace(go.Scatter(
        x=timestamps, y=load_data['values'],
        mode='lines',
        name='Load Time (s)',
        line=dict(color=GRAPH_COLORS['info'], width=2),
        fill='tozeroy',
        fillcolor='rgba(8, 145, 178, 0.1)'
    ))
    load_stats = get_historical_stats(load_data['values'], 'week')
    _add_avg_peak_lines(fig_load, load_stats['average'], load_stats['peak'], 'week')
    _add_above_avg_markers(fig_load, timestamps, load_data['values'], load_stats['average'])

    # Graph 4: CPU Usage - with avg/peak of last week, orange when above avg
    fig_cpu = _create_base_figure('CPU Utilization (%)')
    cpu_data = data['cpu_percent']
    fig_cpu.add_trace(go.Scatter(
        x=timestamps, y=cpu_data['values'],
        mode='lines',
        name='CPU %',
        line=dict(color=GRAPH_COLORS['success'], width=2),
        fill='tozeroy',
        fillcolor='rgba(5, 150, 105, 0.1)'
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
            dcc.Graph(figure=fig_load, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container'),
        html.Div([
            dcc.Graph(figure=fig_cpu, config={'displayModeBar': False}, className='drilldown-graph')
        ], className='drilldown-graph-container')
    ], className='drilldown-graphs-grid four-cols')


def create_multi_machine_drilldown(data: Dict[str, Any], platform_name: str,
                                   load_time_label: str = 'Avg Dashboard Load Time (sec)',
                                   selected_machine: str = None) -> html.Div:
    """Create drill-down graphs for multi-machine platforms (Tableau/Alteryx)."""
    from data import get_historical_stats

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
        fillcolor='rgba(37, 99, 235, 0.1)'
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
            fillcolor='rgba(37, 99, 235, 0.1)'
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
        fillcolor='rgba(8, 145, 178, 0.1)'
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
            fillcolor='rgba(5, 150, 105, 0.1)'
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

    # Create machine status summary with clickable buttons
    machine_outliers = data.get('machine_outliers', {})
    machine_status_items = []
    for machine_name in machines.keys():
        outliers = machine_outliers.get(machine_name, {})
        mem_outliers = len(outliers.get('memory', []))
        cpu_outliers = len(outliers.get('cpu', []))
        total_outliers = mem_outliers + cpu_outliers

        if total_outliers > 5:
            status_color = GRAPH_COLORS['danger']
            status_class = 'machine-status-critical'
        elif total_outliers > 0:
            status_color = GRAPH_COLORS['warning']
            status_class = 'machine-status-warning'
        else:
            status_color = GRAPH_COLORS['success']
            status_class = 'machine-status-healthy'

        # Add selected class if this machine is selected
        if selected_machine == machine_name:
            status_class += ' selected'

        machine_status_items.append(
            html.Div([
                html.Span(className='machine-status-dot', style={'backgroundColor': status_color}),
                html.Span(machine_name, className='machine-name'),
                html.Span(f'{total_outliers} alerts' if total_outliers else 'OK',
                         className='machine-alert-count')
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
            ], className='drilldown-graph-container')
        ], className='drilldown-graphs-grid four-cols')
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
