from google.adk.tools import ToolContext

def fetch_comprehensive_dashboard_data(tool_context: ToolContext = None) -> dict:
    """Fetches a mock dataset designed to test all major A2UI components (DataGrid, VegaChart, KPIs, WebFrame maps)."""
    return {
        "title": "Comprehensive Analytics Overview",
        "description": "Mock dataset for Acme Corp testing UI widgets including DataGrid, VegaChart, Map, and basic KPIs.",
        "kpis": [
            {"title": "Total Revenue", "value": "$124,500", "status": "success"},
            {"title": "Active Users", "value": "12,430", "status": "neutral"},
            {"title": "Bounce Rate", "value": "45%", "status": "warning"}
        ],
        "sales_tabular_data": {
            "columns": [
                {"field": "id", "headerName": "ID", "width": 90},
                {"field": "region", "headerName": "Region", "width": 150},
                {"field": "sales", "headerName": "Sales ($)", "width": 150, "type": "number"},
                {"field": "status", "headerName": "Status", "width": 110}
            ],
            "rows": [
                {"id": 1, "region": "North America", "sales": 45000, "status": "Above Target"},
                {"id": 2, "region": "Europe", "sales": 32000, "status": "On Target"},
                {"id": 3, "region": "Asia Pacific", "sales": 28500, "status": "Below Target"},
                {"id": 4, "region": "South America", "sales": 19000, "status": "Below Target"}
            ]
        },
        "growth_chart_spec": {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "A simple bar chart with embedded data.",
            "data": {
                "values": [
                    {"month": "Jan", "growth": 2.5},
                    {"month": "Feb", "growth": 3.8},
                    {"month": "Mar", "growth": -1.2},
                    {"month": "Apr", "growth": 5.4},
                    {"month": "May", "growth": 6.1},
                    {"month": "Jun", "growth": 4.0}
                ]
            },
            "mark": "bar",
            "encoding": {
                "x": {"field": "month", "type": "nominal", "sort": None, "axis": {"labelAngle": 0}},
                "y": {"field": "growth", "type": "quantitative"},
                "color": {
                    "condition": {"test": "datum.growth < 0", "value": "#ef4444"},
                    "value": "#3b82f6"
                }
            }
        },
        "hq_location": {
            "lat": 37.4220,
            "lng": -122.0841,
            "name": "Acme Corp Global HQ",
            "address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043"
        }
    }

def process_form_submission(payload: dict, tool_context: ToolContext = None) -> str:
    """Mocks a backend system logging an ingested payload correctly piped via Agent-Stage `a2a.action`."""
    print(f"--- BACKEND API RECEIVED FORM PAYLOAD ---")
    print(payload)
    print(f"-----------------------------------------")
    return f"Successfully processed payload containing keys: {list(payload.keys())}!"

def clean_json_output(raw_text: str) -> str:
    """
    Utility function to strip markdown tags (like ```json) from LLM outputs.
    CRITICAL: Use this before wrapping LLM tool outputs into json.loads() to prevent A2UI parser crashes.
    """
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()
