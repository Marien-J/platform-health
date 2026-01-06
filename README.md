# Platform Health Dashboard

A real-time health monitoring dashboard for enterprise data platforms (EDLAP, SAP B/W, Tableau, Alteryx). Built with Python Dash.

## Overview

This dashboard provides:
- **At-a-glance health status** for all platforms (Healthy / Attention / Critical)
- **Click-to-drill-down** into platform-specific tickets
- **Configurable thresholds** for status determination
- **Integration-ready** architecture for connecting to real data sources

## Quick Start

### Local Development (Python)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
cd src
python app.py
```

Open http://localhost:8050 in your browser.

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t platform-health-dashboard .
docker run -p 8050:8050 platform-health-dashboard
```

## Project Structure

```
platform-health-dashboard/
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # CI/CD pipeline
├── assets/
│   └── styles.css           # Dashboard styling
├── src/
│   ├── __init__.py
│   ├── app.py               # Main Dash application
│   ├── components.py        # Reusable UI components
│   └── data.py              # Data fetching (mock/real)
├── tests/
│   ├── __init__.py
│   ├── test_components.py
│   └── test_data.py
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── README.md
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DASH_DEBUG` | `True` | Enable debug mode |
| `PORT` | `8050` | Application port |

### Status Thresholds

Edit `src/data.py` to configure thresholds:

```python
STATUS_THRESHOLDS = {
    'edlap': {
        'pipeline_failures': {'healthy': 5, 'attention': 10},
        'data_delays': {'healthy': 15, 'attention': 30}
    },
    # ...
}
```

## Connecting to Real Data Sources

The `src/data.py` module contains mock data. To connect to real sources:

### EDLAP (Databricks)
```python
from databricks.sdk import WorkspaceClient

def get_edlap_metrics():
    client = WorkspaceClient()
    # Fetch pipeline status, job failures, etc.
```

### SAP B/W
```python
import pyodbc

def get_sapbw_metrics():
    conn = pyodbc.connect('...')
    # Query memory usage, storage consumption
```

### Tableau Server
```python
import tableauserverclient as TSC

def get_tableau_metrics():
    server = TSC.Server('https://tableau.company.com')
    # Fetch view load times, extract refresh status
```

### ServiceNow (Tickets)
```python
import requests

def get_tickets():
    response = requests.get(
        'https://company.service-now.com/api/now/table/incident',
        auth=('user', 'pass'),
        params={'sysparm_query': 'assignment_group=Platform'}
    )
    return response.json()['result']
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_data.py -v
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) includes:

1. **Lint** - Black, Flake8, MyPy
2. **Test** - Pytest with coverage
3. **Build** - Docker image to GitHub Container Registry
4. **Deploy** - Staging (develop branch) / Production (main branch)

### Required GitHub Secrets

For deployment, configure these in your repository settings:
- `GITHUB_TOKEN` (automatic)
- Add deployment-specific secrets as needed

## Development

### Code Style

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Adding a New Platform

1. Add platform data to `get_platforms()` in `data.py`
2. Define thresholds in `STATUS_THRESHOLDS`
3. Add corresponding tickets to `get_tickets()`

## License

Internal use only - [Company Name]
