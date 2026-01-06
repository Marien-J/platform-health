"""
Platform Health Dashboard
A Dash application for monitoring platform health across EDLAP, SAP B/W, Tableau, and Alteryx.
"""

import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from datetime import datetime
import os

from data import get_platforms, get_tickets, get_summary_counts
from components import create_platform_card, create_ticket_table, create_summary_bar

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder='../assets',
    title='Platform Health Dashboard',
    update_title='Loading...'
)

# For deployment
server = app.server

# Layout
app.layout = dbc.Container([
    # Store for selected platform
    dcc.Store(id='selected-platform', data=None),
    
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
    ], color="info", className="footer-note")
    
], fluid=True, className="dashboard-container")


@callback(
    Output('summary-bar', 'children'),
    Input('selected-platform', 'data')
)
def update_summary_bar(_):
    """Update the summary bar with current counts."""
    counts = get_summary_counts()
    return create_summary_bar(counts)


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
        return None
    
    triggered_id = ctx.triggered[0]['prop_id']
    
    # Handle clear button
    if 'clear-filter-btn' in triggered_id:
        return None
    
    # Handle card clicks
    if 'platform-card' in triggered_id:
        import json
        # Extract the platform id from the triggered component
        prop_id = triggered_id.rsplit('.', 1)[0]
        component_id = json.loads(prop_id)
        return component_id['index']
    
    return None


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


if __name__ == '__main__':
    debug_mode = os.environ.get('DASH_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=debug_mode, host='0.0.0.0', port=port)
