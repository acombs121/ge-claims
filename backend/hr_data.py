import json
import os
import logging

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
STATE_FILE = os.path.join(DATA_DIR, 'hr_state.json')

def _read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def _read_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def _write_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def reset_state():
    """Resets the session state."""
    _write_state({})
    return {"status": "State reset successfully"}

def get_hr_portal_overview():
    """Returns a high-fidelity Workday-like portal overview without Skills."""
    profile = _read_json('employee_profile.json')
    org_chart = _read_json('org_chart.json')
    
    emp_details = profile.get('employment_details', {})
    team_details = profile.get('team_details', {})
    
    return {
        "title": "HR Portal Overview",
        "agent_url": os.environ.get("AGENT_URL", ""),
        "grid": [
            {
                "type": "table",
                "title": "Employment Profile",
                "data": {
                    "headers": ["Field", "Value"],
                    "rows": [
                        ["Name", profile.get('name', 'N/A')],
                        ["Role", profile.get('role', 'N/A')],
                        ["Department", profile.get('department', 'N/A')],
                        ["Location", emp_details.get('location', 'N/A')],
                        ["Hire Date", emp_details.get('hire_date', 'N/A')]
                    ]
                }
            },
            {
                "type": "d3-network",
                "title": "Organization Hierarchy",
                "data": org_chart
            },
            {
                "type": "table",
                "title": "Team & Security",
                "data": {
                    "headers": ["Field", "Value"],
                    "rows": [
                        ["Team Name", team_details.get('team_name', 'N/A')],
                        ["Direct Reports", str(team_details.get('direct_reports', 0))],
                        ["Security Level", profile.get('security_context', {}).get('level', 'N/A')],
                        ["Access Rule", profile.get('security_context', {}).get('rule', 'N/A')]
                    ]
                }
            },
            {
                "type": "table",
                "title": "Recent Actions",
                "data": {
                    "headers": ["Action"],
                    "rows": [[action] for action in profile.get('recent_actions', [])]
                }
            }
        ]
    }

def get_employee_profile():
    """Returns A2UI payload for employee profile."""
    data = _read_json('employee_profile.json')
    components = [
        {
            "id": "profile-card",
            "component": { "Card": { "child": "profile-col" } }
        },
        {
            "id": "profile-col",
            "component": { "Column": { "children": { "explicitList": ["name-text", "role-text", "dept-text"] } } }
        },
        {
            "id": "name-text",
            "component": { "Text": { "text": { "literalString": f"Name: {data.get('name', 'N/A')}" }, "usageHint": "h3" } }
        },
        {
            "id": "role-text",
            "component": { "Text": { "text": { "literalString": f"Role: {data.get('role', 'N/A')}" }, "usageHint": "body" } }
        },
        {
            "id": "dept-text",
            "component": { "Text": { "text": { "literalString": f"Department: {data.get('department', 'N/A')}" }, "usageHint": "body" } }
        }
    ]
    return [
        {
            "beginRendering": { "surfaceId": "canvas-surface", "root": "profile-card" }
        },
        {
            "surfaceUpdate": { "surfaceId": "canvas-surface", "components": components }
        }
    ]

def get_performance_reviews():
    """Returns CustomView payload for performance reviews with Radar chart and Skills."""
    data = _read_json('performance_reviews.json').get('EMP003', {})
    comps = data.get('competencies', {})
    details = data.get('feedback_details', {})
    
    profile = _read_json('employee_profile.json')
    skills = profile.get('skills', [])
    
    return {
        "title": "Performance Evaluation",
        "agent_url": os.environ.get("AGENT_URL", ""),
        "grid": [
            {
                "type": "table",
                "title": "Feedback Summary",
                "data": {
                    "headers": ["Period", "Rating", "Summary"],
                    "rows": [[data.get('review_period', 'N/A'), data.get('overall_rating', 'N/A'), data.get('feedback_summary', 'N/A')]]
                }
            },
            {
                "type": "chart",
                "title": "Competency Matrix",
                "data": {
                    "type": "radar",
                    "label": "Score",
                    "labels": comps.get('labels', []),
                    "data": comps.get('data', [])
                }
            },
            {
                "type": "table",
                "title": "Skills & Competencies",
                "data": {
                    "headers": ["Skill", "Proficiency"],
                    "rows": [[s.get('name', 'N/A'), s.get('level', 'N/A')] for s in skills]
                }
            },
            {
                "type": "table",
                "title": "Strengths & Growth Areas",
                "data": {
                    "headers": ["Category", "Items"],
                    "rows": [
                        ["Strengths", ", ".join(details.get('strengths', []))],
                        ["Growth Areas", ", ".join(details.get('areas_for_growth', []))]
                    ]
                }
            }
        ]
    }

def get_org_chart():
    """Returns CustomView payload for org chart D3 graph."""
    data = _read_json('org_chart.json')
    return [
        {
            "CustomView": {
                "template": "dashboard",
                "data": {
                    "title": "Organization Chart",
                    "subtitle": "Security Boundary: Manager Level",
                    "grid": [
                        {
                            "type": "d3-network",
                            "title": "Org Hierarchy",
                            "data": data
                        }
                    ]
                }
            }
        }
    ]

def get_benefits_summary():
    """Returns pure data for benefits summary."""
    data = _read_json('benefits_summary.json').get('EMP001', {})
    vacation = data.get('vacation', {})
    benefits = data.get('benefits', [])
    
    return {
        "vacation": vacation,
        "benefits": benefits
    }

def register_benefit(benefit_name: str):
    """Simulates registering a benefit in Workday."""
    profile = _read_json('employee_profile.json')
    user_id = profile.get('id', 'Unknown')
    user_name = profile.get('name', 'Unknown')
    
    import datetime
    timestamp = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
    print(f"\n[AGENT_PLATFORM] Agent 'a2ui_seed_agent' performed action 'register_benefit' for benefit '{benefit_name}' for user '{user_name}' ({user_id}) at {timestamp}\n")
    logger.info(f"[AGENT_PLATFORM] Agent 'a2ui_seed_agent' performed action 'register_benefit' for benefit '{benefit_name}' for user '{user_name}' ({user_id}) at {timestamp}")
    
    state = _read_state()
    pending = state.get('pending_registrations', [])
    pending.append(benefit_name)
    state['pending_registrations'] = pending
    _write_state(state)
    
    return {
        "success": True,
        "benefit_name": benefit_name,
        "message": f"Successfully requested registration for: {benefit_name}"
    }

def get_standard_widgets_overview():
    """Loads and returns pre-wired dummy data for A2UI 0.8 Standard Components showcase. Throws FileNotFoundError if configuration is missing."""
    path = os.path.join(DATA_DIR, "showcase_widgets.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Critical seed widgets configuration missing: {path}")
    
    with open(path, "r") as f:
        return json.load(f)

def get_map_visualization(intent: str = "interactive", route_type: str = "shortest_distance", location: str = "Boston Common, Boston, MA"):
    """Calculates and returns optimized map parameters. Uses public URL search query embeds or Leaflet road network overlays. Queries Google Directions API at runtime for Leaflet routes if key is available."""
    # Re-read maps API key which is loaded dynamically from .env
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY") or ""
    
    if intent == "simple" or intent == "url":
        import urllib.parse
        encoded_q = urllib.parse.quote(location)
        # Secure, standard key-free Google Maps sharing iframe search mode
        # Devoid of key parameters (never throws 403 API not activated) and 100% allowlisted globally (never blocked by frame CSP)
        return {
            "url": f"https://www.google.com/maps?q={encoded_q}&output=embed"
        }
    
    # High-fidelity Leaflet custom map rendering coordinates and config
    path = os.path.join(DATA_DIR, "map_showcase.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Critical geographic mapping dataset missing: {path}")
    
    with open(path, "r") as f:
        map_data = json.load(f)
        
    # Dynamically calculate high-fidelity street direction paths using live Directions API
    from route_tools import get_accurate_route_google
    
    # Route 1: Downtown Boston Node A to Back Bay Node B
    r1 = get_accurate_route_google(origin_str="42.3620,-71.0570", destination_str="42.3590,-71.0600")
    # Route 2: Downtown Boston Node A to North End Node C
    r2 = get_accurate_route_google(origin_str="42.3620,-71.0570", destination_str="42.3650,-71.0520")
    
    if r1 and "coordinates" in r1:
        map_data["routes"]["shortest_distance"] = r1
    if r2 and "coordinates" in r2:
        map_data["routes"]["account_priority"] = r2
        

    # Fetch local POIs (restaurants, cafes, shops) using official, secure Google Places Nearby Search (100% allowlisted in GCP Cloud Run!)
    map_data["local_pois"] = []
    try:
        import requests
        lat, lng = map_data.get("center", [42.3601, -71.0589])
        if api_key:
            places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 2000,
                "type": "restaurant|cafe|store",
                "key": api_key
            }
            r_pois = requests.get(places_url, params=params, timeout=3.5)
            if r_pois.status_code == 200:
                places_data = r_pois.json()
                for place in places_data.get("results", [])[:15]:
                    loc = place.get("geometry", {}).get("location", {})
                    types_list = place.get("types", [])
                    p_type = "shop"
                    if "restaurant" in types_list or "food" in types_list:
                        p_type = "restaurant"
                    elif "cafe" in types_list or "bakery" in types_list:
                        p_type = "cafe"
                    poi = {
                        "lat": loc.get("lat"),
                        "lng": loc.get("lng"),
                        "name": place.get("name", "Local Business"),
                        "type": p_type,
                        "cuisine": ""
                    }
                    map_data["local_pois"].append(poi)
        else:
            # Local runs without Maps API key fallback immediately to default mock list
            raise ValueError("GOOGLE_MAPS_API_KEY not set in server environment.")
    except Exception as poi_err:
        # Bubble up exception for custom queries, only use fallback for default Boston Common demo (avoids silent fails!)
        if "boston" in location.lower():
            logger.warning(f"Google Places API query encountered an error, falling back to Boston mocks: {poi_err}")
            lat, lng = map_data.get("center", [42.3601, -71.0589])
            map_data["local_pois"] = [
                {"lat": lat + 0.0025, "lng": lng + 0.003, "name": "The Daily Grind Cafe", "type": "cafe", "cuisine": "Coffee"},
                {"lat": lat - 0.003, "lng": lng - 0.0025, "name": "Green Garden Restaurant", "type": "restaurant", "cuisine": "Italian"},
                {"lat": lat + 0.004, "lng": lng - 0.0015, "name": "Beacon Boutique", "type": "shop", "cuisine": ""}
            ]
        else:
            logger.error(f"Google Places API nearbysearch failed for custom location '{location}': {poi_err}")
            raise poi_err
            
    return map_data

def get_universal_dashboard_data():
    """Returns elaborate Pfizer-style metrics data for the universal_dashboard template."""
    return {
        "title": "Seed Analytics Dashboard",
        "subtitle": "Executive Resource Projections, KPI counter targets & Live Simulations",
        "theme": "dark",
        "kpis": [
            {
                "title": "Showcase Requests",
                "value": "1,482 instances",
                "sub": "+14.2% vs last session",
                "status": "success"
            },
            {
                "title": "Response Latency",
                "value": "38 ms",
                "sub": "99.8th percentile",
                "status": "success"
            },
            {
                "title": "Service Availability",
                "value": "99.98%",
                "sub": "Secure VPC Sandboxed",
                "status": "success"
            }
        ],
        "grid": [
            {
                "type": "chart",
                "title": "Monthly System Resource Allocation Limits",
                "fullWidth": True,
                "data": {
                    "type": "bar",
                    "labels": ["Tier 1 Exact", "Tier 2 Jaccard", "Tier 3 LLM Fallback", "Tier 4 UI Card", "Tier 5 Audio WAV"],
                    "label": "Compute Units Allocated (Standard vs Custom)",
                    "data": [85, 65, 115, 90, 140]
                }
            },
            {
                "type": "simulator",
                "title": "Capacity Simulation Engine",
                "fullWidth": True,
                "data": {
                    "controls": [
                        {"label": "User Traffic Load (x100)", "min": 5, "max": 100, "value": 45, "step": 5},
                        {"label": "System Resource Limit (GB)", "min": 16, "max": 128, "value": 64, "step": 16}
                    ],
                    "chartConfig": {
                        "type": "bar",
                        "data": {
                            "labels": ["Risk Index", "Attainment Target"],
                            "datasets": [{
                                "label": "Simulation Index Value",
                                "data": [30, 85],
                                "backgroundColor": ["rgba(239, 68, 68, 0.85)", "rgba(37, 99, 235, 0.85)"]
                            }]
                        }
                    },
                    "onUpdateBody": "const load = params[0]; const limit = params[1]; const risk = Math.min(100, Math.max(10, parseInt((load / limit) * 100))); const target = Math.max(15, 100 - parseInt(risk * 0.4)); chart.data.datasets[0].data = [risk, target];"
                }
            },
            {
                "type": "table",
                "title": "Dynamic Showcase Transaction Logs",
                "fullWidth": True,
                "data": {
                    "headers": ["Transaction ID", "Component Type", "State Scope", "Status"],
                    "rows": [
                        ["TX-9842", "Tabs Showcase Panel", "Session Sandbox", "Synchronized"],
                        ["TX-9843", "Leaflet Map Overlay", "Dynamic Street Route", "Completed"],
                        ["TX-9844", "TTS Audio WAV Player", "WAV Transcoded 45s", "Ready"],
                        ["TX-9845", "D3 Network Graph", "Interactive Drag/Zoom", "Rendered"]
                    ]
                }
            }
        ]
    }

def get_d3_network_data():
    """Returns elaborate org relationship tree network graph data for the dashboard template."""
    return {
        "title": "Seed Topology Network Graph",
        "subtitle": "D3 Directed Graph representing Boston nodes connections and peer dependencies",
        "theme": "dark",
        "kpis": [
            {
                "title": "Total Network Nodes",
                "value": "5 Anchors",
                "sub": "Active Hubs",
                "status": "success"
            },
            {
                "title": "Total Topology Edges",
                "value": "5 Connections",
                "sub": "Optimum Directions",
                "status": "success"
            }
        ],
        "grid": [
            {
                "type": "d3-network",
                "title": "Enterprise Connections Hierarchy Map",
                "data": {
                    "nodes": [
                        {"id": "Downtown Node A", "label": "Downtown Node A", "radius": 15, "color": "#ef4444", "level": 1, "detail_info": "Downtown Boston HUB Core"},
                        {"id": "Back Bay Node B", "label": "Back Bay Node B", "radius": 12, "color": "#f97316", "level": 2, "detail_info": "Back Bay Regional Branch"},
                        {"id": "North End Node C", "label": "North End Node C", "radius": 12, "color": "#facc15", "level": 2, "detail_info": "North End Logistics Relay"},
                        {"id": "MIT Node D", "label": "MIT Campus Node D", "radius": 10, "color": "#38bdf8", "level": 3, "detail_info": "MIT Advanced Research Lab"},
                        {"id": "Harvard Node E", "label": "Harvard Node E", "radius": 10, "color": "#38bdf8", "level": 3, "detail_info": "Harvard Analytics Center"}
                    ],
                    "edges": [
                        {"source": "Downtown Node A", "target": "Back Bay Node B", "value": "Core Connect"},
                        {"source": "Downtown Node A", "target": "North End Node C", "value": "Relay Link"},
                        {"source": "Back Bay Node B", "target": "MIT Node D", "value": "Research Pipeline"},
                        {"source": "North End Node C", "target": "Harvard Node E", "value": "Analytics Link"},
                        {"source": "MIT Node D", "target": "Harvard Node E", "value": "University Bridge"}
                    ]
                }
            },
            {
                "type": "table",
                "title": "Topology Nodes Metadata Breakdown",
                "data": {
                    "headers": ["Node ID", "Classification", "Color Tag", "Visual Ring Type"],
                    "rows": [
                        ["Downtown Node A", "Downtown HUB Core", "Red", "Severity Pulsing High"],
                        ["Back Bay Node B", "Back Bay Regional Branch", "Orange", "Severity Pulsing Medium"],
                        ["North End Node C", "North End Logistics Relay", "Yellow", "Severity Pulsing Low"],
                        ["MIT Campus Node D", "MIT Advanced Research Lab", "Cyan Blue", "Anchor Connect"],
                        ["Harvard Node E", "Harvard Analytics Center", "Cyan Blue", "Anchor Connect"]
                    ]
                }
            }
        ]
    }


