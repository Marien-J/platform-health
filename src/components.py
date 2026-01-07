"""
UI Components for Platform Health Dashboard.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Optional

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


# Graph color palette for multiple series
GRAPH_COLORS = [
    '#2563EB',  # Blue
    '#9CA3AF',  # Gray
    '#10B981',  # Green
    '#F59E0B',  # Amber
    '#EC4899',  # Pink
    '#8B5CF6',  # Purple
    '#06B6D4',  # Cyan
    '#EF4444',  # Red
]

# Graph layout configuration for consistent sizing
GRAPH_LAYOUT_CONFIG = {
    'margin': dict(l=50, r=20, t=40, b=50),
    'font': dict(family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size=11),
    'paper_bgcolor': 'white',
    'plot_bgcolor': 'white',
    'hovermode': 'x unified',
}


def create_server_status_card(
    server_id: str,
    alert_count: int,
    status: str,
    is_selected: bool = False
) -> html.Div:
    """Create a clickable server status card."""
    colors = STATUS_COLORS.get(status, STATUS_COLORS['healthy'])

    card_style = {
        'padding': '12px 16px',
        'borderRadius': '8px',
        'border': f"2px solid {colors['bg'] if is_selected else '#E5E7EB'}",
        'backgroundColor': colors['light'] if status != 'healthy' else '#FFFFFF',
        'cursor': 'pointer',
        'transition': 'all 0.2s ease',
        'textAlign': 'center',
        'minWidth': '100px',
        'flex': '1 1 100px',
    }

    if is_selected:
        card_style['boxShadow'] = f"0 2px 8px {colors['bg']}40"

    return html.Div([
        html.Div(
            className="status-indicator",
            style={
                'width': '8px',
                'height': '8px',
                'borderRadius': '50%',
                'backgroundColor': colors['bg'],
                'display': 'inline-block',
                'marginBottom': '4px'
            }
        ),
        html.Div(server_id, style={'fontWeight': '600', 'fontSize': '13px', 'color': '#111827'}),
        html.Div(f"{alert_count} alerts", style={'fontSize': '11px', 'color': '#6B7280'})
    ], style=card_style, className="server-status-card")


def create_server_status_section(
    title: str,
    servers: List[str],
    alert_counts: Dict[str, int],
    server_statuses: Dict[str, str],
    selected_servers: Optional[List[str]] = None,
    card_id_prefix: str = "server"
) -> html.Div:
    """Create a row of server status cards."""
    if selected_servers is None:
        selected_servers = []

    cards = []
    for server in servers:
        is_selected = server in selected_servers
        cards.append(
            html.Div(
                create_server_status_card(
                    server,
                    alert_counts.get(server, 0),
                    server_statuses.get(server, 'healthy'),
                    is_selected
                ),
                id={'type': f'{card_id_prefix}-card', 'index': server},
                n_clicks=0,
                className="server-card-wrapper"
            )
        )

    return html.Div([
        html.H6(title, className="server-section-title"),
        html.Div(cards, className="server-cards-row")
    ], className="server-status-section")


def create_active_users_graph(
    timestamps: List,
    values: List[int],
    avg_month: int,
    peak_month: int,
    title: str = "Total Active Users"
) -> dcc.Graph:
    """Create active users time series graph with average and peak lines (no warning/critical)."""
    fig = go.Figure()

    # Main data line with area fill
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=values,
        mode='lines',
        name='Total Users',
        line=dict(color='#2563EB', width=2),
        fill='tozeroy',
        fillcolor='rgba(37, 99, 235, 0.1)',
        hovertemplate='%{y} users<extra></extra>'
    ))

    # Average line (last month)
    fig.add_hline(
        y=avg_month,
        line=dict(color='#059669', width=2, dash='dash'),
        annotation_text=f"Average: {avg_month}",
        annotation_position="right",
        annotation_font=dict(color='#059669', size=10)
    )

    # Peak line (last month)
    fig.add_hline(
        y=peak_month,
        line=dict(color='#7C3AED', width=2, dash='dot'),
        annotation_text=f"Peak: {peak_month}",
        annotation_position="right",
        annotation_font=dict(color='#7C3AED', size=10)
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#111827')),
        xaxis=dict(
            showgrid=True,
            gridcolor='#F3F4F6',
            tickformat='%H:%M\n%b %d',
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#F3F4F6',
            title='Users',
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10)
        ),
        **GRAPH_LAYOUT_CONFIG
    )

    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False, 'responsive': True},
        className='dashboard-graph'
    )


def create_memory_usage_graph(
    timestamps: List,
    servers_data: Dict[str, Dict],
    server_list: List[str],
    selected_servers: Optional[List[str]] = None,
    thresholds: Optional[Dict] = None,
    title: str = "Memory Usage (%)"
) -> dcc.Graph:
    """Create memory usage graph for multiple servers with hover-based legend."""
    fig = go.Figure()

    # Determine which servers to show
    visible_servers = selected_servers if selected_servers else server_list

    for i, server in enumerate(server_list):
        visible = server in visible_servers
        memory_data = servers_data[server]['memory']

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=memory_data,
            mode='lines',
            name=server,
            line=dict(color=GRAPH_COLORS[i % len(GRAPH_COLORS)], width=1.5),
            visible=True if visible else 'legendonly',
            hovertemplate=f'{server}: %{{y:.1f}}%<extra></extra>'
        ))

    # Add average line
    if visible_servers:
        avg_values = []
        for i in range(len(timestamps)):
            avg = sum(servers_data[s]['memory'][i] for s in visible_servers) / len(visible_servers)
            avg_values.append(avg)

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=avg_values,
            mode='lines',
            name='Average',
            line=dict(color='#7C3AED', width=2.5),
            hovertemplate='Average: %{y:.1f}%<extra></extra>'
        ))

    # Add threshold lines
    if thresholds:
        fig.add_hline(
            y=thresholds.get('memory_warning', 75),
            line=dict(color='#F59E0B', width=1.5, dash='dash'),
            annotation_text="Warning",
            annotation_position="right",
            annotation_font=dict(color='#F59E0B', size=9)
        )
        fig.add_hline(
            y=thresholds.get('memory_critical', 90),
            line=dict(color='#EF4444', width=1.5, dash='dash'),
            annotation_text="Critical",
            annotation_position="right",
            annotation_font=dict(color='#EF4444', size=9)
        )

    fig.update_layout(
        title=dict(text=f"{title} - {len(server_list)} Machines", font=dict(size=14, color='#111827')),
        xaxis=dict(showgrid=True, gridcolor='#F3F4F6', tickformat='%H:%M\n%b %d'),
        yaxis=dict(showgrid=True, gridcolor='#F3F4F6', title='%', range=[0, 105]),
        showlegend=False,  # Hide legend - use tooltip
        **GRAPH_LAYOUT_CONFIG
    )

    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False, 'responsive': True},
        className='dashboard-graph'
    )


def create_load_time_graph(
    timestamps: List,
    load_times: List[float],
    load_time_spikes: List[bool],
    avg_week: float,
    peak_week: float,
    title: str = "Avg Dashboard Load Time (sec)"
) -> dcc.Graph:
    """Create load time graph with spikes marked (orange when exceeds average, no red markers)."""
    fig = go.Figure()

    # Main line with area fill
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=load_times,
        mode='lines',
        name='Load Time',
        line=dict(color='#06B6D4', width=2),
        fill='tozeroy',
        fillcolor='rgba(6, 182, 212, 0.1)',
        hovertemplate='%{y:.1f}s<extra></extra>'
    ))

    # Add orange markers for values exceeding average
    spike_x = []
    spike_y = []
    for i, (ts, lt) in enumerate(zip(timestamps, load_times)):
        if lt > avg_week:
            spike_x.append(ts)
            spike_y.append(lt)

    if spike_x:
        fig.add_trace(go.Scatter(
            x=spike_x,
            y=spike_y,
            mode='markers',
            name='Above Average',
            marker=dict(
                color='#F59E0B',
                size=8,
                symbol='diamond',
                line=dict(color='#92400E', width=1)
            ),
            hovertemplate='%{y:.1f}s (above avg)<extra></extra>'
        ))

    # Average line
    fig.add_hline(
        y=avg_week,
        line=dict(color='#059669', width=2, dash='dash'),
        annotation_text=f"Avg: {avg_week}s",
        annotation_position="right",
        annotation_font=dict(color='#059669', size=10)
    )

    # Peak line
    fig.add_hline(
        y=peak_week,
        line=dict(color='#7C3AED', width=2, dash='dot'),
        annotation_text=f"Peak: {peak_week}s",
        annotation_position="right",
        annotation_font=dict(color='#7C3AED', size=10)
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#111827')),
        xaxis=dict(showgrid=True, gridcolor='#F3F4F6', tickformat='%H:%M\n%b %d'),
        yaxis=dict(showgrid=True, gridcolor='#F3F4F6', title='Load Time (s)'),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10)
        ),
        **GRAPH_LAYOUT_CONFIG
    )

    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False, 'responsive': True},
        className='dashboard-graph'
    )


def create_cpu_usage_graph(
    timestamps: List,
    servers_data: Dict[str, Dict],
    server_list: List[str],
    avg_cpu: List[float],
    avg_week: float,
    peak_week: float,
    selected_servers: Optional[List[str]] = None,
    title: str = "CPU Usage (%)"
) -> dcc.Graph:
    """Create CPU usage graph with average and peak lines (no threshold lines)."""
    fig = go.Figure()

    visible_servers = selected_servers if selected_servers else server_list

    for i, server in enumerate(server_list):
        visible = server in visible_servers
        cpu_data = servers_data[server]['cpu']

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=cpu_data,
            mode='lines',
            name=server,
            line=dict(color=GRAPH_COLORS[i % len(GRAPH_COLORS)], width=1.5),
            visible=True if visible else 'legendonly',
            hovertemplate=f'{server}: %{{y:.1f}}%<extra></extra>'
        ))

    # Add overall average line
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=avg_cpu,
        mode='lines',
        name='Average',
        line=dict(color='#059669', width=2.5),
        hovertemplate='Average: %{y:.1f}%<extra></extra>'
    ))

    # Add historical average and peak lines
    fig.add_hline(
        y=avg_week,
        line=dict(color='#059669', width=1.5, dash='dash'),
        annotation_text=f"Week Avg: {avg_week}%",
        annotation_position="right",
        annotation_font=dict(color='#059669', size=10)
    )

    fig.add_hline(
        y=peak_week,
        line=dict(color='#7C3AED', width=1.5, dash='dot'),
        annotation_text=f"Week Peak: {peak_week}%",
        annotation_position="right",
        annotation_font=dict(color='#7C3AED', size=10)
    )

    fig.update_layout(
        title=dict(text=f"{title} - {len(server_list)} Machines", font=dict(size=14, color='#111827')),
        xaxis=dict(showgrid=True, gridcolor='#F3F4F6', tickformat='%H:%M\n%b %d'),
        yaxis=dict(showgrid=True, gridcolor='#F3F4F6', title='%', range=[0, 105]),
        showlegend=False,  # Hide legend - use tooltip
        **GRAPH_LAYOUT_CONFIG
    )

    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False, 'responsive': True},
        className='dashboard-graph'
    )


def create_pipeline_status_bar_chart(
    pipeline_status: Dict[str, int],
    title: str = "Pipeline Status"
) -> dcc.Graph:
    """Create a bar chart showing pipeline status counts (successful, delayed, failed)."""
    categories = ['Successful', 'Delayed', 'Failed']
    values = [
        pipeline_status.get('successful', 0),
        pipeline_status.get('delayed', 0),
        pipeline_status.get('failed', 0)
    ]
    colors = ['#059669', '#F59E0B', '#EF4444']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=values,
        textposition='outside',
        hovertemplate='%{x}: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#111827')),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#F3F4F6', title='Count'),
        showlegend=False,
        **GRAPH_LAYOUT_CONFIG
    )

    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False, 'responsive': True},
        className='dashboard-graph'
    )


def create_tickets_time_series_graph(
    timestamps: List,
    open_tickets: List[int],
    avg_month: float,
    peak_month: int,
    title: str = "Open Tickets (Last 30 Days)"
) -> dcc.Graph:
    """Create tickets time series with average and peak lines (no warning/critical)."""
    fig = go.Figure()

    # Main line with area fill
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=open_tickets,
        mode='lines+markers',
        name='Open Tickets',
        line=dict(color='#2563EB', width=2),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(37, 99, 235, 0.1)',
        hovertemplate='%{y} tickets<extra></extra>'
    ))

    # Average line
    fig.add_hline(
        y=avg_month,
        line=dict(color='#059669', width=2, dash='dash'),
        annotation_text=f"Avg: {avg_month:.0f}",
        annotation_position="right",
        annotation_font=dict(color='#059669', size=10)
    )

    # Peak line
    fig.add_hline(
        y=peak_month,
        line=dict(color='#7C3AED', width=2, dash='dot'),
        annotation_text=f"Peak: {peak_month}",
        annotation_position="right",
        annotation_font=dict(color='#7C3AED', size=10)
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#111827')),
        xaxis=dict(showgrid=True, gridcolor='#F3F4F6', tickformat='%b %d'),
        yaxis=dict(showgrid=True, gridcolor='#F3F4F6', title='Tickets'),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10)
        ),
        **GRAPH_LAYOUT_CONFIG
    )

    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False, 'responsive': True},
        className='dashboard-graph'
    )


def create_platform_performance_section(
    platform_name: str,
    platform_icon: str = "📊"
) -> html.Div:
    """Create a section header for platform performance."""
    return html.Div([
        html.Span(platform_icon, style={'marginRight': '8px'}),
        html.Span(f"{platform_name} - System Performance", style={'fontWeight': '600'}),
        html.Span(" Last 24 hours • 5-minute intervals", style={'color': '#6B7280', 'fontSize': '13px', 'marginLeft': '12px'})
    ], className="platform-section-header")
