"""
Platform Health Dashboard
A Dash application for monitoring platform health across EDLAP, SAP B/W, Tableau, and Alteryx.
"""

import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from datetime import datetime
import os

from data import get_platforms, get_tickets, get_summary_counts, get_performance_data
from components import (
    create_platform_card, create_ticket_table, create_summary_bar,
    create_ticket_detail_modal, get_platform_name, get_servicenow_url,
    create_performance_drilldown, STATUS_COLORS, PRIORITY_COLORS
)
ASSETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
    ],
    assets_folder=ASSETS_PATH,
    assets_url_path='/assets',
    title='Platform Health Dashboard',
    update_title='Loading...'
)

# For deployment
server = app.server

# Layout
app.layout = dbc.Container([
    # Store for selected platforms (list of platform IDs - empty list means show all tickets)
    dcc.Store(id='selected-platform', data=[], storage_type='memory'),

    # Store for selected machine (for Tableau/Alteryx filtering)
    dcc.Store(id='selected-machine', data=None, storage_type='memory'),

    # Store for card order (persisted in local storage)
    dcc.Store(id='card-order', data=['edlap', 'sapbw', 'tableau', 'alteryx'], storage_type='local'),

    # Hidden div to receive drag-drop updates from JavaScript
    html.Div(id='drag-drop-trigger', style={'display': 'none'}, **{'data-order': ''}),

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

    # Performance Drill-down Section (conditionally shown)
    html.Div(id='performance-drilldown-container', className="performance-drilldown-wrapper"),

    # Ticket Drill-down Section
    dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.Div([
                    html.H5(id='ticket-section-title', className="mb-0"),
                    html.Button(
                        "Clear All Filters",
                        id='clear-filter-btn',
                        className="btn-clear-filter",
                        style={'display': 'none'}
                    )
                ], className="ticket-header-top"),
                # Active filter badges container (shown vertically in order of selection)
                html.Div(id='active-filters-container', className="active-filters-container")
            ], className="ticket-header")
        ]),
        dbc.CardBody([
            # Filter and Sort Controls
            html.Div([
                # Text Search Filter
                html.Div([
                    dbc.Input(
                        id='ticket-search-input',
                        type='text',
                        placeholder='Search by ticket ID, title, or owner...',
                        className='ticket-search-input'
                    )
                ], className='filter-control search-control'),

                # Sort Controls
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

            # Store for sort direction (True = ascending, False = descending)
            dcc.Store(id='sort-direction', data=True),

            html.Div(id='ticket-table')
        ])
    ], className="ticket-card"),
    
    # Footer Note
    dbc.Alert([
        html.Strong("Dashboard Note: "),
        "Click any platform card to filter tickets. Status thresholds (Healthy/Attention/Critical) ",
        "are configurable based on agreed business rules."
    ], color="info", className="footer-note"),

    # Ticket Detail Modal
    create_ticket_detail_modal(),

    # Store for selected ticket data
    dcc.Store(id='selected-ticket', data=None)

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
    Input('selected-platform', 'data'),
    Input('card-order', 'data')
)
def update_platform_cards(selected_platforms, card_order):
    """Render all platform cards in the specified order."""
    platforms = get_platforms()
    platforms_dict = {p['id']: p for p in platforms}

    # Ensure selected_platforms is a list
    if selected_platforms is None:
        selected_platforms = []

    # Use stored order, falling back to default if not set
    if not card_order:
        card_order = ['edlap', 'sapbw', 'tableau', 'alteryx']

    # Ensure all platforms are included (handle any missing ones)
    all_ids = set(p['id'] for p in platforms)
    ordered_ids = [pid for pid in card_order if pid in all_ids]
    for pid in all_ids:
        if pid not in ordered_ids:
            ordered_ids.append(pid)

    cards = []
    for platform_id in ordered_ids:
        platform = platforms_dict.get(platform_id)
        if platform:
            is_selected = platform['id'] in selected_platforms
            cards.append(
                html.Div(
                    create_platform_card(platform, is_selected),
                    id={'type': 'platform-card', 'index': platform['id']},
                    n_clicks=0,
                    className="platform-card-wrapper",
                    draggable='true',
                    **{'data-platform-id': platform['id']}
                )
            )
    return cards


@callback(
    Output('performance-drilldown-container', 'children'),
    Output('performance-drilldown-container', 'style'),
    Input('selected-platform', 'data'),
    Input('selected-machine', 'data')
)
def update_performance_drilldown(selected_platforms, selected_machine):
    """Update the performance drill-down section based on selected platforms and machine."""
    # Ensure selected_platforms is a list
    if selected_platforms is None:
        selected_platforms = []

    if not selected_platforms:
        # No platform selected - hide the drill-down
        return None, {'display': 'none'}

    # Show drilldown for the first selected platform only
    selected_platform_id = selected_platforms[0]

    # Get platform info for the header
    platforms = get_platforms()
    platform = next((p for p in platforms if p['id'] == selected_platform_id), None)
    platform_name = platform['name'] if platform else 'Unknown'

    # Get performance data for the selected platform
    perf_data = get_performance_data(selected_platform_id)

    if not perf_data:
        return html.Div("No performance data available"), {'display': 'block'}

    # Create the drill-down card
    drilldown_content = dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H5([
                    html.I(className="fa fa-chart-line me-2"),
                    f"{platform_name} - System Performance"
                ], className="mb-0"),
                html.Small(
                    "Last 24 hours • 5-minute intervals",
                    className="text-muted ms-2"
                )
            ], className="d-flex align-items-center")
        ]),
        dbc.CardBody([
            create_performance_drilldown(selected_platform_id, perf_data, selected_machine)
        ])
    ], className="performance-drilldown-card")

    return drilldown_content, {'display': 'block'}


@callback(
    Output('selected-machine', 'data'),
    Input({'type': 'machine-filter-btn', 'platform': dash.ALL, 'machine': dash.ALL}, 'n_clicks'),
    Input({'type': 'machine-clear-btn', 'platform': dash.ALL}, 'n_clicks'),
    Input('selected-platform', 'data'),
    prevent_initial_call=True
)
def handle_machine_filter(machine_clicks, clear_clicks, selected_platforms):
    """Handle machine filter button clicks."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id']
    triggered_value = ctx.triggered[0]['value']

    # If platform selection changed, clear the machine filter
    if 'selected-platform' in triggered_id:
        return None

    # Handle clear button
    if 'machine-clear-btn' in triggered_id:
        return None

    # Handle machine button clicks
    if 'machine-filter-btn' in triggered_id:
        if not triggered_value or triggered_value == 0:
            return dash.no_update
        import json
        prop_id = triggered_id.rsplit('.', 1)[0]
        component_id = json.loads(prop_id)
        return component_id['machine']

    return dash.no_update


@callback(
    Output('selected-platform', 'data'),
    Input({'type': 'platform-card', 'index': dash.ALL}, 'n_clicks'),
    Input('clear-filter-btn', 'n_clicks'),
    Input({'type': 'remove-filter-btn', 'index': dash.ALL}, 'n_clicks'),
    dash.State('selected-platform', 'data'),
    prevent_initial_call=True
)
def handle_card_click(card_clicks, clear_clicks, remove_clicks, current_selection):
    """Handle platform card clicks, clear filter button, and individual filter removal."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id']
    triggered_value = ctx.triggered[0]['value']

    # Ensure current_selection is a list
    if current_selection is None:
        current_selection = []

    # Handle clear all button
    if 'clear-filter-btn' in triggered_id:
        return []

    # Handle individual filter removal
    if 'remove-filter-btn' in triggered_id:
        if not triggered_value or triggered_value == 0:
            return dash.no_update
        import json
        prop_id = triggered_id.rsplit('.', 1)[0]
        component_id = json.loads(prop_id)
        platform_to_remove = component_id['index']
        new_selection = [p for p in current_selection if p != platform_to_remove]
        return new_selection

    # Handle card clicks - toggle platform in/out of list
    if 'platform-card' in triggered_id:
        if not triggered_value or triggered_value == 0:
            return dash.no_update
        import json
        # Extract the platform id from the triggered component
        prop_id = triggered_id.rsplit('.', 1)[0]
        component_id = json.loads(prop_id)
        clicked_platform = component_id['index']

        # Toggle: if already selected, remove it; otherwise add it
        if clicked_platform in current_selection:
            new_selection = [p for p in current_selection if p != clicked_platform]
        else:
            new_selection = current_selection + [clicked_platform]

        return new_selection

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
    Output('active-filters-container', 'children'),
    Output('ticket-table', 'children'),
    Input('selected-platform', 'data'),
    Input('ticket-search-input', 'value'),
    Input('ticket-sort-field', 'value'),
    Input('sort-direction', 'data')
)
def update_ticket_section(selected_platforms, search_text, sort_field, is_ascending):
    """Update ticket section based on selected platforms, search, and sort options."""
    platforms = get_platforms()
    tickets = get_tickets()

    # Ensure selected_platforms is a list
    if selected_platforms is None:
        selected_platforms = []

    # Create active filter badges
    filter_badges = []
    if selected_platforms:
        for platform_id in selected_platforms:
            platform = next((p for p in platforms if p['id'] == platform_id), None)
            platform_name = platform['name'] if platform else platform_id
            platform_status = platform['status'] if platform else 'healthy'
            colors = STATUS_COLORS.get(platform_status, STATUS_COLORS['healthy'])

            filter_badges.append(
                html.Div([
                    html.Span(
                        platform_name,
                        className="filter-badge-label",
                        style={
                            'backgroundColor': colors['light'],
                            'color': colors['text'],
                            'borderLeft': f"3px solid {colors['bg']}"
                        }
                    ),
                    html.Button(
                        html.I(className="fa fa-times"),
                        id={'type': 'remove-filter-btn', 'index': platform_id},
                        n_clicks=0,
                        className="filter-badge-remove",
                        title=f"Remove {platform_name} filter"
                    )
                ], className="active-filter-badge")
            )

    # Filter by platforms
    if selected_platforms:
        title = "Filtered Tickets"
        btn_style = {'display': 'inline-block'}
        filtered_tickets = [t for t in tickets if t['platform'] in selected_platforms]
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

    return title, btn_style, filter_badges, create_ticket_table(filtered_tickets)


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


# Clientside callback for handling drag-drop card reordering
app.clientside_callback(
    """
    function(trigger) {
        // This callback is triggered by the drag-drop-trigger element
        // The new order is stored in the element's data-order attribute
        const triggerEl = document.getElementById('drag-drop-trigger');
        if (triggerEl && triggerEl.getAttribute('data-order')) {
            try {
                const newOrder = JSON.parse(triggerEl.getAttribute('data-order'));
                // Clear the trigger after reading
                triggerEl.setAttribute('data-order', '');
                return newOrder;
            } catch (e) {
                console.error('Error parsing card order:', e);
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('card-order', 'data'),
    Input('drag-drop-trigger', 'n_clicks'),
    prevent_initial_call=True
)


if __name__ == '__main__':
    debug_mode = os.environ.get('DASH_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=debug_mode, host='0.0.0.0', port=port)
