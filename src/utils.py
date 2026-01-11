"""
Utility functions for Platform Health Dashboard.
"""


def generate_servicenow_link(ticket_number: str, instance: str = "aldiprod") -> str:
    """
    Generate ServiceNow link based on ticket prefix.

    Args:
        ticket_number: The ticket number (e.g., INC001234, RITM001234, PRB001234)
        instance: ServiceNow instance name (default: aldisued)

    Returns:
        Full ServiceNow URL for the ticket
    """
    base_url = f"https://{instance}.service-now.com"

    if ticket_number.startswith("INC"):
        return f"{base_url}/incident.do?sysparm_query=number={ticket_number}"
    elif ticket_number.startswith("RITM"):
        return f"{base_url}/sc_req_item.do?sysparm_query=number={ticket_number}"
    elif ticket_number.startswith("PRB"):
        return f"{base_url}/problem.do?sysparm_query=number={ticket_number}"
    else:
        search_uri = "%2F$sn_global_search_results.do%3Fsysparm_search%3D"
        return f"{base_url}/nav_to.do?uri={search_uri}{ticket_number}"
