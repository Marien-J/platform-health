"""
Platform Health Dashboard
A Dash application for monitoring platform health across EDLAP, SAP B/W, Tableau, and Alteryx.
"""

import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from datetime import datetime
import os

from data import (
    get_platforms, get_tickets, get_summary_counts,
    get_tableau_server_data, get_alteryx_server_data, get_edlap_data,
    TABLEAU_SERVERS, ALTERYX_WORKERS
)
from components import (
    create_platform_card, create_ticket_table, create_summary_bar,
    create_ticket_detail_modal, get_platform_name, get_servicenow_url,
    create_server_status_section, create_active_users_graph,
    create_memory_usage_graph, create_load_time_graph, create_cpu_usage_graph,
    create_pipeline_status_bar_chart, create_tickets_time_series_graph,
    create_platform_performance_section,
    STATUS_COLORS, PRIORITY_COLORS
)

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
    ],
    assets_folder='../assets',
    title='Platform Health Dashboard',
    update_title='Loading...'
)

# For deployment
server = app.server

# Layout
app.layout = dbc.Container([
    # Stores for selected items
    dcc.Store(id='selected-platform', data=None, storage_type='memory'),
    dcc.Store(id='selected-tableau-servers', data=[], storage_type='memory'),
    dcc.Store(id='selected-alteryx-workers', data=[], storage_type='memory'),
    dcc.Store(id='sort-direction', data=True),
    dcc.Store(id='selected-ticket', data=None),

    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Platform Health Dashboard", className="dashboard-title"),
            html.P(
                f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} CET",
                className="last-updated"
            )
        ])
    ], className="header-row"),

    # Summary Bar
    html.Div(id='summary-bar', className="summary-bar"),

    # Platform Cards
    html.Div(id='platform-cards', className="platform-cards-container"),

    # Tableau Performance Section
    dbc.Card([
        dbc.CardHeader([
            create_platform_performance_section("Tableau", "📊")
        ], className="performance-card-header"),
        dbc.CardBody([
            # Server Status Cards
            html.Div(id='tableau-server-cards', className="server-status-container"),

            # Graphs Grid
            html.Div([
                html.Div([
                    html.Div(id='tableau-users-graph', className="graph-cell"),
                    html.Div(id='tableau-memory-graph', className="graph-cell"),
                ], className="graph-row"),
                html.Div([
                    html.Div(id='tableau-load-time-graph', className="graph-cell"),
                    html.Div(id='tableau-cpu-graph', className="graph-cell"),
                ], className="graph-row"),
            ], className="graphs-grid")
        ])
    ], className="performance-card"),

    # Alteryx Performance Section
    dbc.Card([
        dbc.CardHeader([
            create_platform_performance_section("Alteryx", "⚙️")
        ], className="performance-card-header"),
        dbc.CardBody([
            # Worker Status Cards
            html.Div(id='alteryx-worker-cards', className="server-status-container"),

            # Graphs Grid
            html.Div([
                html.Div([
                    html.Div(id='alteryx-memory-graph', className="graph-cell"),
                    html.Div(id='alteryx-users-graph', className="graph-cell"),
                ], className="graph-row"),
                html.Div([
                    html.Div(id='alteryx-load-time-graph', className="graph-cell"),
                ], className="graph-row"),
            ], className="graphs-grid")
        ])
    ], className="performance-card"),

    # EDLAP Section
    dbc.Card([
        dbc.CardHeader([
            create_platform_performance_section("EDLAP", "🗄️")
        ], className="performance-card-header"),
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.Div(id='edlap-pipeline-graph', className="graph-cell"),
                    html.Div(id='edlap-tickets-graph', className="graph-cell"),
                ], className="graph-row"),
            ], className="graphs-grid")
        ])
    ], className="performance-card"),

    # Ticket Drill-down Section
    dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H5(id='ticket-section-title', className="mb-0"),
                html.Button(
                    "Clear Filter",
                    id='clear-filter-btn',
                    className="btn-clear-filter",
                    style={'display': 'none'}
                )
            ], className="ticket-header")
        ]),
        dbc.CardBody([
            # Filter and Sort Controls
            html.Div([
                html.Div([
                    dbc.Input(
                        id='ticket-search-input',
                        type='text',
                        placeholder='Search by ticket ID, title, or owner...',
                        className='ticket-search-input'
                    )
                ], className='filter-control search-control'),
                html.Div([
                    html.Label('Sort by:', className='sort-label'),
                    dbc.Select(
                        id='ticket-sort-field',
                        options=[
                            {'label': 'Ticket ID', 'value': 'id'},
                            {'label': 'Title', 'value': 'title'},
                            {'label': 'Priority', 'value': 'priority'},
                            {'label': 'Owner', 'value': 'owner'}
                        ],
                        value='id',
                        className='sort-select'
                    ),
                    dbc.Button(
                        html.I(className='fa fa-sort-amount-down', id='sort-icon'),
                        id='sort-direction-btn',
                        color='light',
                        className='sort-direction-btn',
                        n_clicks=0
                    )
                ], className='filter-control sort-control')
            ], className='ticket-filter-bar'),
            html.Div(id='ticket-table')
        ])
    ], className="ticket-card"),

    # Footer Note
    dbc.Alert([
        html.Strong("Dashboard Note: "),
        "Click any platform card to filter tickets. Click server cards to filter graphs. ",
        "Status thresholds are configurable based on agreed business rules."
    ], color="info", className="footer-note"),

    # Ticket Detail Modal
    create_ticket_detail_modal(),

], fluid=True, className="dashboard-container")


@callback(
    Output('summary-bar', 'children'),
    Input('selected-platform', 'data')
)
def update_summary_bar(_):
    """Update the summary bar with current counts and platform statuses."""
    counts = get_summary_counts()
    platforms = get_platforms()
    return create_summary_bar(counts, platforms)


@callback(
    Output('platform-cards', 'children'),
    Input('selected-platform', 'data')
)
def update_platform_cards(selected_platform_id):
    """Render all platform cards."""
    platforms = get_platforms()
    cards = []
    for platform in platforms:
        is_selected = platform['id'] == selected_platform_id
        cards.append(
            html.Div(
                create_platform_card(platform, is_selected),
                id={'type': 'platform-card', 'index': platform['id']},
                n_clicks=0,
                className="platform-card-wrapper"
            )
        )
    return cards


@callback(
    Output('selected-platform', 'data'),
    Input({'type': 'platform-card', 'index': dash.ALL}, 'n_clicks'),
    Input('clear-filter-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_card_click(card_clicks, clear_clicks):
    """Handle platform card clicks and clear filter button."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id']
    triggered_value = ctx.triggered[0]['value']

    # Handle clear button
    if 'clear-filter-btn' in triggered_id:
        return None

    # Handle card clicks - only respond to actual clicks (value > 0)
    if 'platform-card' in triggered_id:
        if not triggered_value or triggered_value == 0:
            return dash.no_update
        import json
        # Extract the platform id from the triggered component
        prop_id = triggered_id.rsplit('.', 1)[0]
        component_id = json.loads(prop_id)
        return component_id['index']

    return dash.no_update


@callback(
    Output('sort-direction', 'data'),
    Output('sort-icon', 'className'),
    Input('sort-direction-btn', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_sort_direction(n_clicks):
    """Toggle sort direction between ascending and descending."""
    # Odd clicks = descending, even clicks = ascending
    is_ascending = n_clicks % 2 == 0
    icon_class = 'fa fa-sort-amount-up' if is_ascending else 'fa fa-sort-amount-down'
    return is_ascending, icon_class


@callback(
    Output('ticket-section-title', 'children'),
    Output('clear-filter-btn', 'style'),
    Output('ticket-table', 'children'),
    Input('selected-platform', 'data'),
    Input('ticket-search-input', 'value'),
    Input('ticket-sort-field', 'value'),
    Input('sort-direction', 'data')
)
def update_ticket_section(selected_platform_id, search_text, sort_field, is_ascending):
    """Update ticket section based on selected platform, search, and sort options."""
    platforms = get_platforms()
    tickets = get_tickets()

    # Filter by platform
    if selected_platform_id:
        platform = next((p for p in platforms if p['id'] == selected_platform_id), None)
        platform_name = platform['name'] if platform else 'Unknown'
        title = f"{platform_name} - Open Tickets"
        btn_style = {'display': 'inline-block'}
        filtered_tickets = [t for t in tickets if t['platform'] == selected_platform_id]
    else:
        title = "All Open Tickets"
        btn_style = {'display': 'none'}
        filtered_tickets = tickets

    # Apply text search filter
    if search_text:
        search_lower = search_text.lower()
        filtered_tickets = [
            t for t in filtered_tickets
            if search_lower in t['id'].lower()
            or search_lower in t['title'].lower()
            or search_lower in t['owner'].lower()
        ]

    # Apply sorting
    if sort_field:
        # Special handling for priority to sort by severity rather than alphabetically
        if sort_field == 'priority':
            priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
            filtered_tickets = sorted(
                filtered_tickets,
                key=lambda t: priority_order.get(t['priority'], 99),
                reverse=not is_ascending
            )
        else:
            filtered_tickets = sorted(
                filtered_tickets,
                key=lambda t: t.get(sort_field, '').lower() if isinstance(t.get(sort_field), str) else t.get(sort_field, ''),
                reverse=not is_ascending
            )

    return title, btn_style, create_ticket_table(filtered_tickets)


@callback(
    Output('selected-ticket', 'data'),
    Input({'type': 'ticket-row', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def handle_ticket_click(row_clicks):
    """Handle ticket row clicks to select a ticket."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id']
    triggered_value = ctx.triggered[0]['value']

    # Only respond to actual clicks (value > 0), not table re-renders
    if not triggered_value or triggered_value == 0:
        return dash.no_update

    # Check if any row was actually clicked
    if 'ticket-row' in triggered_id:
        import json
        prop_id = triggered_id.rsplit('.', 1)[0]
        component_id = json.loads(prop_id)
        ticket_id = component_id['index']

        # Find the ticket data
        tickets = get_tickets()
        ticket = next((t for t in tickets if t['id'] == ticket_id), None)
        if ticket:
            return ticket

    return dash.no_update


@callback(
    Output('ticket-detail-modal', 'is_open'),
    Output('modal-ticket-title', 'children'),
    Output('modal-ticket-id', 'children'),
    Output('modal-ticket-id', 'href'),
    Output('modal-platform-badge', 'children'),
    Output('modal-platform-badge', 'style'),
    Output('modal-priority-badge', 'children'),
    Output('modal-priority-badge', 'style'),
    Output('modal-age', 'children'),
    Output('modal-created-date', 'children'),
    Output('modal-owner', 'children'),
    Output('modal-last-updated', 'children'),
    Output('modal-description', 'children'),
    Output('modal-servicenow-btn', 'href'),
    Input('selected-ticket', 'data'),
    Input('modal-close-btn', 'n_clicks'),
    Input('modal-footer-close-btn', 'n_clicks'),
    prevent_initial_call=True
)
def update_modal(ticket_data, close_btn, footer_close_btn):
    """Update modal content and visibility based on selected ticket."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return (False, "", "", "#", "", {}, "", {}, "", "", "", "", "", "#")

    triggered_id = ctx.triggered[0]['prop_id']

    # Handle close buttons
    if 'close-btn' in triggered_id:
        return (False, "", "", "#", "", {}, "", {}, "", "", "", "", "", "#")

    # Handle ticket selection
    if ticket_data:
        ticket_id = ticket_data['id']
        servicenow_url = get_servicenow_url(ticket_id)

        # Get platform info
        platforms = get_platforms()
        platform = next((p for p in platforms if p['id'] == ticket_data['platform']), None)
        platform_name = get_platform_name(ticket_data['platform'])
        platform_status = platform['status'] if platform else 'healthy'
        platform_colors = STATUS_COLORS.get(platform_status, STATUS_COLORS['healthy'])

        platform_badge_style = {
            'backgroundColor': platform_colors['light'],
            'color': platform_colors['text'],
            'padding': '4px 12px',
            'borderRadius': '20px',
            'fontSize': '13px',
            'fontWeight': '600'
        }

        # Priority styling
        priority_colors = PRIORITY_COLORS.get(ticket_data['priority'], PRIORITY_COLORS['Low'])
        priority_style = {
            'backgroundColor': priority_colors['bg'],
            'color': priority_colors['text']
        }

        return (
            True,  # is_open
            ticket_data['title'],  # modal-ticket-title
            ticket_id,  # modal-ticket-id children
            servicenow_url,  # modal-ticket-id href
            platform_name,  # modal-platform-badge children
            platform_badge_style,  # modal-platform-badge style
            ticket_data['priority'],  # modal-priority-badge children
            priority_style,  # modal-priority-badge style
            ticket_data['age'],  # modal-age
            ticket_data.get('created_date', 'N/A'),  # modal-created-date
            ticket_data['owner'],  # modal-owner
            ticket_data.get('last_updated', 'N/A'),  # modal-last-updated
            ticket_data.get('description', 'No description available.'),  # modal-description
            servicenow_url  # modal-servicenow-btn href
        )

    return (False, "", "", "#", "", {}, "", {}, "", "", "", "", "", "#")


# ==================== Tableau Section Callbacks ====================

@callback(
    Output('selected-tableau-servers', 'data'),
    Input({'type': 'tableau-server-card', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def handle_tableau_server_click(clicks):
    """Handle Tableau server card clicks for filtering."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id']
    triggered_value = ctx.triggered[0]['value']

    if not triggered_value or triggered_value == 0:
        return dash.no_update

    if 'tableau-server-card' in triggered_id:
        import json
        prop_id = triggered_id.rsplit('.', 1)[0]
        component_id = json.loads(prop_id)
        server_id = component_id['index']

        # Get current selection from inputs (toggle behavior)
        # For simplicity, we'll just return the clicked server as the only selected one
        # Click again to deselect (empty list shows all)
        return [server_id]

    return dash.no_update


@callback(
    Output('tableau-server-cards', 'children'),
    Input('selected-tableau-servers', 'data')
)
def update_tableau_server_cards(selected_servers):
    """Update Tableau server status cards."""
    data = get_tableau_server_data()
    return create_server_status_section(
        "Tableau Server Status",
        TABLEAU_SERVERS,
        data['alert_counts'],
        data['server_statuses'],
        selected_servers or [],
        card_id_prefix='tableau-server'
    )


@callback(
    Output('tableau-users-graph', 'children'),
    Output('tableau-memory-graph', 'children'),
    Output('tableau-load-time-graph', 'children'),
    Output('tableau-cpu-graph', 'children'),
    Input('selected-tableau-servers', 'data')
)
def update_tableau_graphs(selected_servers):
    """Update all Tableau performance graphs."""
    data = get_tableau_server_data()
    ts = data['timestamps']
    hist = data['historical']

    # Active users graph (no filtering by server - aggregate metric)
    users_graph = create_active_users_graph(
        ts,
        data['active_users'],
        hist['avg_users_month'],
        hist['peak_users_month'],
        "Total Active Users"
    )

    # Memory usage graph (filterable by server)
    memory_graph = create_memory_usage_graph(
        ts,
        data['servers'],
        TABLEAU_SERVERS,
        selected_servers if selected_servers else None,
        data['thresholds'],
        "Memory Usage (%)"
    )

    # Load time graph
    load_graph = create_load_time_graph(
        ts,
        data['load_times'],
        data['load_time_spikes'],
        hist['avg_load_week'],
        hist['peak_load_week'],
        "Avg Dashboard Load Time (sec)"
    )

    # CPU usage graph (filterable by server)
    cpu_graph = create_cpu_usage_graph(
        ts,
        data['servers'],
        TABLEAU_SERVERS,
        data['avg_cpu'],
        hist['avg_cpu_week'],
        hist['peak_cpu_week'],
        selected_servers if selected_servers else None,
        "CPU Usage (%)"
    )

    return users_graph, memory_graph, load_graph, cpu_graph


# ==================== Alteryx Section Callbacks ====================

@callback(
    Output('selected-alteryx-workers', 'data'),
    Input({'type': 'alteryx-worker-card', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def handle_alteryx_worker_click(clicks):
    """Handle Alteryx worker card clicks for filtering."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id']
    triggered_value = ctx.triggered[0]['value']

    if not triggered_value or triggered_value == 0:
        return dash.no_update

    if 'alteryx-worker-card' in triggered_id:
        import json
        prop_id = triggered_id.rsplit('.', 1)[0]
        component_id = json.loads(prop_id)
        worker_id = component_id['index']
        return [worker_id]

    return dash.no_update


@callback(
    Output('alteryx-worker-cards', 'children'),
    Input('selected-alteryx-workers', 'data')
)
def update_alteryx_worker_cards(selected_workers):
    """Update Alteryx worker status cards."""
    data = get_alteryx_server_data()
    return create_server_status_section(
        "Alteryx Server Status",
        ALTERYX_WORKERS,
        data['alert_counts'],
        data['worker_statuses'],
        selected_workers or [],
        card_id_prefix='alteryx-worker'
    )


@callback(
    Output('alteryx-memory-graph', 'children'),
    Output('alteryx-users-graph', 'children'),
    Output('alteryx-load-time-graph', 'children'),
    Input('selected-alteryx-workers', 'data')
)
def update_alteryx_graphs(selected_workers):
    """Update all Alteryx performance graphs."""
    data = get_alteryx_server_data()
    ts = data['timestamps']
    hist = data['historical']

    # Memory usage graph
    memory_graph = create_memory_usage_graph(
        ts,
        data['workers'],
        ALTERYX_WORKERS,
        selected_workers if selected_workers else None,
        data['thresholds'],
        "Memory Usage (%)"
    )

    # Active users graph
    users_graph = create_active_users_graph(
        ts,
        data['active_users'],
        hist['avg_users_month'],
        hist['peak_users_month'],
        "Active Users"
    )

    # Load time graph
    load_graph = create_load_time_graph(
        ts,
        data['load_times'],
        data['load_time_spikes'],
        hist['avg_load_week'],
        hist['peak_load_week'],
        "Avg Dashboard Load Time (sec)"
    )

    return memory_graph, users_graph, load_graph


# ==================== EDLAP Section Callbacks ====================

@callback(
    Output('edlap-pipeline-graph', 'children'),
    Output('edlap-tickets-graph', 'children'),
    Input('selected-platform', 'data')  # Trigger on any platform selection change
)
def update_edlap_graphs(_):
    """Update EDLAP graphs."""
    data = get_edlap_data()
    hist = data['historical']

    # Pipeline status bar chart
    pipeline_graph = create_pipeline_status_bar_chart(
        data['pipeline_status'],
        "Pipeline Status (Today)"
    )

    # Open tickets time series
    tickets_graph = create_tickets_time_series_graph(
        data['ticket_timestamps'],
        data['open_tickets'],
        hist['avg_tickets_month'],
        hist['peak_tickets_month'],
        "Open Tickets (Last 30 Days)"
    )

    return pipeline_graph, tickets_graph


if __name__ == '__main__':
    debug_mode = os.environ.get('DASH_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=debug_mode, host='0.0.0.0', port=port)
