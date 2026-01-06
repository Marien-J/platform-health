"""
Platform Health Dashboard
A Dash application for monitoring platform health across EDLAP, SAP B/W, Tableau, and Alteryx.
"""

import dash
from dash import html, dcc, callback, Output, Input, State, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
from datetime import datetime
import os

from data import get_platforms, get_tickets, get_summary_counts
from components import (
    create_platform_card, create_ticket_table, create_summary_bar,
    create_ticket_detail_modal, get_platform_name, get_servicenow_url,
    STATUS_COLORS, PRIORITY_COLORS
)

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
    ],
    external_scripts=[
        "https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"
    ],
    assets_folder='../assets',
    title='Platform Health Dashboard',
    update_title='Loading...',
    suppress_callback_exceptions=True
)

# For deployment
server = app.server

# Layout
app.layout = dbc.Container([
    # Store for selected platform (no default filter - show all tickets)
    dcc.Store(id='selected-platform', data=None, storage_type='memory'),

    # Store for card order (persists across page reloads)
    dcc.Store(id='card-order', data=['edlap', 'sapbw', 'tableau', 'alteryx'], storage_type='local'),
    
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
    
    # Platform Cards (sortable container) - populated by callback
    html.Div(
        id='platform-cards',
        className="platform-cards-container",
        children=[
            html.Div(
                create_platform_card(p, False),
                id={'type': 'platform-card', 'index': p['id']},
                n_clicks=0,
                className="platform-card-wrapper",
                **{'data-platform-id': p['id']}
            ) for p in get_platforms()
        ]
    ),

    # Hidden div to trigger sortable initialization
    html.Div(id='sortable-init', style={'display': 'none'}),
    
    # Drill-down Section
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
    Output('sortable-init', 'children'),
    Input('selected-platform', 'data'),
    State('card-order', 'data')
)
def update_platform_cards(selected_platform_id, card_order):
    """Render all platform cards."""
    platforms = get_platforms()
    platform_dict = {p['id']: p for p in platforms}

    # Use stored order, falling back to default if order is invalid
    if not card_order:
        card_order = ['edlap', 'sapbw', 'tableau', 'alteryx']

    # Build cards based on order
    cards = []
    for platform_id in card_order:
        if platform_id in platform_dict:
            platform = platform_dict[platform_id]
            is_selected = platform['id'] == selected_platform_id
            cards.append(
                html.Div(
                    create_platform_card(platform, is_selected),
                    id={'type': 'platform-card', 'index': platform['id']},
                    n_clicks=0,
                    className="platform-card-wrapper",
                    **{'data-platform-id': platform['id']}
                )
            )

    # Return cards and a timestamp to trigger sortable re-init
    import time
    return cards, str(time.time())


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
    Output('ticket-section-title', 'children'),
    Output('clear-filter-btn', 'style'),
    Output('ticket-table', 'children'),
    Input('selected-platform', 'data')
)
def update_ticket_section(selected_platform_id):
    """Update ticket section based on selected platform."""
    platforms = get_platforms()
    tickets = get_tickets()
    
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


if __name__ == '__main__':
    debug_mode = os.environ.get('DASH_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=debug_mode, host='0.0.0.0', port=port)
