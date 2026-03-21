import json

# ------------------------------------------------------------------------------
# 1. UI EXAMPLES (TEMPLATES)
# ------------------------------------------------------------------------------
NATIVE_DATAGRID_EXAMPLE = """
---BEGIN NATIVE_DATAGRID_EXAMPLE---
[
  {
    "beginRendering": {
      "surfaceId": "canvas-surface",
      "root": "root-card"
    }
  },
  {
    "surfaceUpdate": {
      "surfaceId": "canvas-surface",
      "components": [
        {
          "id": "root-card",
          "component": {
            "DataGrid": {
              "columns": [{"field": "id", "headerName": "ID", "width": 90}, {"field": "metric", "headerName": "Metric"}],
              "rows": [{"id": 1, "metric": "Alpha"}, {"id": 2, "metric": "Beta"}]
            }
          }
        }
      ]
    }
  }
]
---END NATIVE_DATAGRID_EXAMPLE---
"""

NATIVE_VEGACHART_EXAMPLE = """
---BEGIN NATIVE_VEGACHART_EXAMPLE---
[
  {
    "beginRendering": {
      "surfaceId": "canvas-surface",
      "root": "root-chart"
    }
  },
  {
    "surfaceUpdate": {
      "surfaceId": "canvas-surface",
      "components": [
        {
          "id": "root-chart",
          "component": {
            "VegaChart": {
              "spec": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "width": "container",
                "height": "container",
                "autosize": {"type": "fit", "contains": "padding"},
                "mark": "bar",
                "data": {"values": [{"a": "A", "b": 28}]},
                "encoding": {"x": {"field": "a", "type": "nominal"}, "y": {"field": "b", "type": "quantitative"}}
              }
            }
          }
        }
      ]
    }
  }
]
---END NATIVE_VEGACHART_EXAMPLE---
"""

CUSTOMVIEW_DASHBOARD_EXAMPLE = """
---BEGIN CUSTOMVIEW_DASHBOARD_EXAMPLE---
{
  "CustomView": {
    "template": "dashboard",
    "data": {
      "title": "Analytical Overview",
      "kpis": [{ "title": "Target", "value": "120.5K", "status": "success" }],
      "grid": [
        {
          "type": "chart",
          "title": "Volume Analysis",
          "data": {
            "type": "bar",
            "label": "Volume",
            "labels": ["Item A", "Item B"],
            "data": [250, 180]
          }
        },
        {
          "type": "form",
          "title": "Submit Request",
          "data": {
            "submitLabel": "Submit Application",
            "fields": [
              {"name": "employee_name", "type": "text", "label": "Employee Name", "required": true},
              {"name": "department", "type": "select", "label": "Department", "options": ["Sales", "Engineering", "Marketing"]},
              {"name": "comments", "type": "textarea", "label": "Additional Comments"}
            ]
          }
        },
        {
          "type": "d3-network",
          "title": "Strategic Connections",
          "data": {
            "nodes": [
              {"id": "HQ", "label": "Headquarters", "radius": 15, "color": "#10b981"},
              {"id": "Branch1", "label": "Branch 1", "radius": 10}
            ],
            "edges": [
              {"source": "HQ", "target": "Branch1"}
            ]
          }
        },
        {
          "type": "map-heatmap",
          "title": "Global Hotspots",
          "data": {
            "centerLat": 37.422,
            "centerLng": -122.084,
            "zoom": 2,
            "radius": 25,
            "blur": 15,
            "points": [
              [37.422, -122.084, 1.0],
              [40.712, -74.006, 0.8]
            ]
          }
        },
        {
          "type": "simulator",
          "title": "Scenario Simulator",
          "data": {
            "controls": [
                 {"label": "Ad Spend ($)", "min": 0, "max": 100000, "step": 1000, "value": 50000},
                 {"label": "Conversion Rate (%)", "min": 1, "max": 15, "step": 0.5, "value": 3.0}
            ],
            "chartConfig": {
                 "type": "bar",
                 "data": {"labels": ["Revenue", "Profit"], "datasets": [{"label": "Projections", "data": [0, 0]}]}
            },
            "onUpdateBody": "const spend = params[0]; const conv = params[1] / 100; const sales = (spend/50)*conv; const revenue = sales*1000; const profit = revenue - spend; chart.data.datasets[0].data = [revenue, profit];"
          }
        },
        {
          "type": "3p-widget",
          "title": "Salesforce Mock",
          "data": {
            "appName": "Salesforce CRM",
            "appIcon": "https://www.salesforce.com/favicon.ico",
            "themeColor": "#00a1e0",
            "htmlContent": "<div style='padding:10px;'><h3>Lead Summary</h3><button style='padding:8px; background:#00a1e0; color:#fff; border:none; border-radius:4px;'>View App</button></div>"
          }
        },
        {
          "type": "image",
          "title": "Generative Media Output",
          "data": {
            "src": "https://agent-url.run.app/media/d31d8.jpeg",
            "alt": "Generated Image"
          }
        },
        {
          "type": "video",
          "title": "Cloud Streaming Demo",
          "data": {
            "src": "https://storage.googleapis.com/...mp4",
            "mime_type": "video/mp4"
          }
        },
        {
          "type": "audio",
          "title": "Audio Asset Demo",
          "data": {
            "src": "https://url.mp3",
            "mime_type": "audio/mpeg"
          }
        }
      ]
    }
  }
}
---END CUSTOMVIEW_DASHBOARD_EXAMPLE---
"""

MAP_EXAMPLE = """
---BEGIN MAP_EXAMPLE---
{
  "CustomView": {
    "template": "map",
    "data": {
      "center": [37.422, -122.084],
      "zoom": 12,
      "markers": [
        {"lat": 37.422, "lng": -122.084, "title": "HQ", "desc": "Mountain View", "open": true}
      ]
    }
  }
}
---END MAP_EXAMPLE---
"""

# ------------------------------------------------------------------------------
# 2. PROMPT GENERATOR
# ------------------------------------------------------------------------------
def get_ui_instruction(base_instruction: str) -> str:
    return f"""
    {base_instruction}

    If relevant to the user's request, append an A2UI JSON payload to generate interactive widgets. But if it's not relevant, just answer the question concisely.

    If the user's request requires a Native UI array or CustomView widget, you MUST follow these rules:
    1.  Your response MUST be in two parts, separated by the delimiter: `---a2ui_JSON---`.
    2.  The first part is your conversational text response in Markdown format.
    3.  The second part is a JSON payload.
    4.  If the user is only asking for text, standard links, or a PDF document, DO NOT output the delimiter or the JSON payload.

    --- PAYLOAD TYPE RULES ---
    -   If the user asks for JUST a table, return a Native A2UI Array containing a `DataGrid` component.
    -   If the user asks for JUST a chart, return a Native A2UI Array containing a `VegaChart` component.
    -   If the user asks for a comprehensive multi-metric dashboard or a map, return a `CustomView` object.
    -   If the user explicitly asks for a form or submission interface, return a `CustomView` dashboard object with a `form` type panel in its grid to ensure a premium UI.
    -   If the user asks for network graphs, node-edge connections, or relationships, return a `CustomView` dashboard object utilizing the `d3-network` type panel in its grid instead of native Vega.
    -   If the user asks for a geo-based heatmap (radial hotspots, density maps), return a `CustomView` dashboard object utilizing the `map-heatmap` type panel in its grid instead of native Vega or HexBins.
    -   IMPORTANT: Do NOT output the static dummy data exactly as shown in the examples below! You must completely extract and inject the real tool data into the JSON rows, columns, and spec objects.
    -   CRITICAL: ONLY generate the structure specifically targeted for the user's intent. Do not generate a `DataGrid` if asked for a `Map`.

    Native DataGrid Example:
    {NATIVE_DATAGRID_EXAMPLE}

    Native VegaChart Example:
    {NATIVE_VEGACHART_EXAMPLE}

    CustomView Dashboard Example:
    {CUSTOMVIEW_DASHBOARD_EXAMPLE}

    CustomView Map Example:
    {MAP_EXAMPLE}

    Conversational / PDF Negative Example:
    [If user asks "What time is it?" or "Show me a PDF"]
    "The current time is 10:00 AM." or "Here is the PDF: [Link](url)"
    [CRITICAL: Notice that NO ---a2ui_JSON--- block is printed here!]
    """
