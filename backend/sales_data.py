"""
This file contains legacy sales data handling functions, cloned from the ge-sales-agent project.
It is preserved here as a starting point for future pivots back to sales use cases.
The functions in this file follow the new paradigm of deterministic JSON generation (returning 
structured A2UI payloads or CustomView dicts directly from Python) to avoid LLM hallucination overhead.
"""
import json
import os
import logging
from config import get_parameter_default
from route_tools import get_accurate_route_google
from map_services import build_map_payload

logger = logging.getLogger(__name__)



DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
STATE_FILE = os.path.join(DATA_DIR, 'sales_state.json')

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

def save_trip_params(industry: str = None, prioritization: str = None) -> dict:
    """Saves the selected industry and prioritization to session state."""
    print(f"DEBUG: save_trip_params called with industry={industry}, prioritization={prioritization}")
    
    if not industry:
        industry = get_parameter_default("industry", "Tech")
    if not prioritization:
        prioritization = get_parameter_default("prioritization", "Account Size")

    state = _read_state()
    state['industry'] = industry
    state['prioritization'] = prioritization
    _write_state(state)
    return {"status": f"Trip parameters saved: {industry}, {prioritization}"}

def get_recommendations(industry: str = None, prioritization: str = None) -> list:
    """Saves params and gets the recommended accounts, returning A2UI components."""
    print(f"DEBUG: get_recommendations called with industry={industry}, prioritization={prioritization}")

    
    # Handle list inputs from MultipleChoice
    if isinstance(industry, list) and industry:
        industry = industry[0]
    if isinstance(prioritization, list) and prioritization:
        prioritization = prioritization[0]

    if not industry:
        industry = get_parameter_default("industry", "Tech")
    if not prioritization:
        prioritization = get_parameter_default("prioritization", "Account Size")

    state = _read_state()
    state['industry'] = industry
    state['prioritization'] = prioritization
    _write_state(state)
    key = f"{industry}_{prioritization}"
    
    try:
        recs = _read_json('recommendations.json')
        selected = recs.get(key, [])
    except Exception as e:
        print(f"Error reading recommendations: {e}")
        selected = []
        
    if not selected:
        return [
            {
                "id": "error-text",
                "component": { "Text": { "text": { "literalString": f"No recommendations found for industry '{industry}' and prioritization '{prioritization}'." } } }
            }
        ]

        
    components = [
        {
            "id": "recs-column",
            "component": {
                "Column": {
                    "children": { "explicitList": ["title-text", "unified-card", "ok-btn"] },
                    "distribution": "start",
                    "alignment": "stretch"
                }
            }
        },
        {
            "id": "title-text",
            "component": { "Text": { "text": { "literalString": "Here's your recommended accounts for this sales trip:" } } }
        },
        {
            "id": "unified-card",
            "component": { "Card": { "child": "card-column" } }
        }
    ]
    
    card_children = []
    
    for i, acc in enumerate(selected):
        col_id = f"col-{i}"
        card_children.append(col_id)
        
        # Add divider between accounts
        if i > 0:
            div_id = f"account-divider-{i}"
            card_children.insert(len(card_children)-1, div_id)
            components.append({
                "id": div_id,
                "component": { "Divider": {} }
            })

        components.extend([
            {
                "id": col_id,
                "component": {
                    "Column": {
                        "children": { "explicitList": [
                            f"logo-{i}",
                            f"ind-field-{i}",
                            f"reg-field-{i}",
                            f"div1-{i}",
                            f"rat-row-{i}",
                            f"div2-{i}",
                            f"metrics-row-{i}"
                        ] },
                        "alignment": "stretch"
                    }
                }
            },
            {
                "id": f"logo-{i}",
                "component": {
                    "Row": {
                        "children": { "explicitList": [f"img-{i}", f"title-{i}"] },
                        "alignment": "center"
                    }
                }
            },
            {
                "id": f"img-{i}",
                "component": { "Image": { "url": { "literalString": f"https://placehold.co/32x32?text={acc.get('id', 'AC001')}" if not os.environ.get("K_SERVICE") else f"https://storage.cloud.google.com/sandbox-426014-logos/{acc.get('id', 'AC001')}.svg?v=4" }, "usageHint": "icon" } }
            },
            {
                "id": f"title-{i}",
                "component": { "Text": { "text": { "literalString": acc.get("name", "Account") }, "usageHint": "h3" } }
            },
            {
                "id": f"ind-field-{i}",
                "component": { "Text": { "text": { "literalString": f"INDUSTRY: {acc.get('industry', 'Tech')}" }, "usageHint": "body" } }
            },
            {
                "id": f"reg-field-{i}",
                "component": { "Text": { "text": { "literalString": f"REGION: {acc.get('territory', 'Northeast')} ({acc.get('sub_region', 'Boston Metro')})" }, "usageHint": "body" } }
            },
            {
                "id": f"div1-{i}",
                "component": { "Divider": {} }
            },
            {
                "id": f"rat-row-{i}",
                "component": {
                    "Row": {
                        "children": { "explicitList": [f"star-{i}", f"rat-text-{i}"] },
                        "alignment": "center"
                    }
                }
            },
            {
                "id": f"star-{i}",
                "component": { "Icon": { "name": { "literalString": "star" } } }
            },
            {
                "id": f"rat-text-{i}",
                "component": { "Text": { "text": { "literalString": acc.get('rationale', '') }, "usageHint": "h4" } }
            },
            {
                "id": f"div2-{i}",
                "component": { "Divider": {} }
            },
            {
                "id": f"metrics-row-{i}",
                "component": {
                    "Row": {
                        "children": { "explicitList": [f"arr-col-{i}", f"lv-col-{i}", f"stat-col-{i}"] },
                        "alignment": "stretch",
                        "justify": "spaceAround",
                        "width": "100%"
                    }
                }
            },
            {
                "id": f"arr-col-{i}",
                "component": {
                    "Column": {
                        "children": { "explicitList": [f"arr-val-{i}", f"arr-lbl-{i}"] },
                        "alignment": "center"
                    }
                }
            },
            {
                "id": f"arr-val-{i}",
                "component": { "Text": { "text": { "literalString": f"${acc.get('arr', 0):,}" }, "usageHint": "h3" } }
            },
            {
                "id": f"arr-lbl-{i}",
                "component": { "Text": { "text": { "literalString": "ARR" }, "usageHint": "caption" } }
            },
            {
                "id": f"lv-col-{i}",
                "component": {
                    "Column": {
                        "children": { "explicitList": [f"lv-val-{i}", f"lv-lbl-{i}"] },
                        "alignment": "center"
                    }
                }
            },
            {
                "id": f"lv-val-{i}",
                "component": { "Text": { "text": { "literalString": acc.get('last_visited', 'Never') }, "usageHint": "h3" } }
            },
            {
                "id": f"lv-lbl-{i}",
                "component": { "Text": { "text": { "literalString": "LAST VISITED" }, "usageHint": "caption" } }
            },
            {
                "id": f"stat-col-{i}",
                "component": {
                    "Column": {
                        "children": { "explicitList": [f"stat-val-{i}", f"stat-lbl-{i}"] },
                        "alignment": "center"
                    }
                }
            },
            {
                "id": f"stat-val-{i}",
                "component": { "Text": { "text": { "literalString": acc.get('status', 'Active') }, "usageHint": "h3" } }
            },
            {
                "id": f"stat-lbl-{i}",
                "component": { "Text": { "text": { "literalString": "STATUS" }, "usageHint": "caption" } }
            }
        ])
        
    # Insert card-column containing all account columns
    components.append({
        "id": "card-column",
        "component": {
            "Column": {
                "children": { "explicitList": card_children },
                "alignment": "stretch"
            }
        }
    })

    components.extend([
        {
            "id": "ok-btn",
            "component": { "Button": { "child": "ok-btn-text", "action": { "name": "confirm_recs" } } }
        },
        {
            "id": "ok-btn-text",
            "component": { "Text": { "text": { "literalString": "See Recommended Route" } } }
        }
    ])

    
    return [
        {
            "beginRendering": {
                "surfaceId": "canvas-surface",
                "root": "recs-column"
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "canvas-surface",
                "components": components
            }
        }
    ]


def save_selected_accounts(accounts):
    """Saves the selected accounts to session state."""
    state = _read_state()
    state['selected_accounts'] = accounts
    _write_state(state)
    return {"status": f"Saved {len(accounts)} accounts to plan"}

def get_client_visit_parameters():
    """Returns default parameters for client visit intake."""
    return {
        "travel_window": "2026-04-15 to 2026-04-20",
        "min_arr": 100000,
        "industry_options": [
            {"label": {"literalString": "Finance"}, "value": "Finance"},
            {"label": {"literalString": "Tech"}, "value": "Tech"},
            {"label": {"literalString": "Healthcare"}, "value": "Healthcare"},
            {"label": {"literalString": "Retail"}, "value": "Retail"}
        ]
    }

def filter_accounts(churn_risk=None, support_tickets_spike=None, industry=None):
    """Filters accounts based on criteria and returns full A2UI DataGrid JSON."""
    accounts = _read_json('accounts.json')
    if not isinstance(accounts, list):
        return []
        
    # Read industry from state if not provided
    state = _read_state()
    if not industry:
        industry = state.get('industry')
        
    if isinstance(support_tickets_spike, str):
        if support_tickets_spike.lower() == 'true':
            support_tickets_spike = True
        elif support_tickets_spike.lower() == 'false':
            support_tickets_spike = False
    
    filtered = []
    for acc in accounts:
        match = True
        if churn_risk and acc.get("churn_risk") != churn_risk:
            match = False
        if support_tickets_spike is not None and acc.get("support_tickets_spike") != support_tickets_spike:
            match = False
        if industry and acc.get("industry") != industry:
            match = False
        if match:
            filtered.append(acc)
            
    # Limit to top 6 to allow selecting 4 out of 6
    filtered = filtered[:6]
            
    # Construct components list for Native A2UI (Strict Schema)
    components = [
        {
            "id": "customize-column",
            "component": {
                "Column": {
                    "children": { "explicitList": ["title-text", "account-choices", "submit-btn"] },
                    "distribution": "start",
                    "alignment": "stretch"
                }
            }
        },
        {
            "id": "title-text",
            "component": {
                "Text": {
                    "text": {"literalString": "Customize Trip Plan - Select Accounts"},
                    "usageHint": "h3"
                }
            }
        },
        {
            "id": "account-choices",
            "component": {
                "MultipleChoice": {
                    "options": [
                        {
                            "label": {"literalString": f"{acc['name']} (Risk: {acc['risk_score']})"},
                            "value": acc['id']
                        } for acc in filtered
                    ],
                    "selections": {"path": "/selected_accounts"},
                    "maxAllowedSelections": 5
                }
            }
        },
        {
            "id": "submit-btn",
            "component": {
                "Button": {
                    "child": "submit-text",
                    "primary": True,
                    "action": {
                        "name": "save_plan",
                        "context": ["/selected_accounts"]
                    }
                }
            }
        },
        {
            "id": "submit-text",
            "component": {
                "Text": {
                    "text": {"literalString": "Confirm Selection"}
                }
            }
        }
    ]
        
    # Construct full A2UI payload
    a2ui_payload = [
        {
            "beginRendering": {
                "surfaceId": "canvas-surface",
                "root": "customize-column"
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "canvas-surface",
                "components": components
            }
        }
    ]
    
    # Log what's coming out of the function
    print(f"DEBUG: filter_accounts returning: {json.dumps(a2ui_payload)}")
    
    return a2ui_payload

def get_initial_form():
    """Returns the initial quarterly planning UI form as full A2UI JSON schema.
    Call this tool exactly when the user asks to plan their sales visits for the day."""
    print("DEBUG: get_initial_form called")
    
    industry_options_raw = get_parameter_default("industry_options", [
        {"label": "Finance", "value": "Finance"},
        {"label": "Healthcare", "value": "Healthcare"},
        {"label": "Tech", "value": "Tech"},
        {"label": "Retail", "value": "Retail"}
    ])
    
    prioritization_options_raw = get_parameter_default("prioritization_options", [
        {"label": "Account Size", "value": "Account Size"},
        {"label": "Churn Risk", "value": "Churn Risk"},
        {"label": "Upsell Potential", "value": "Upsell Potential"}
    ])

    industry_options = [
        {"label": {"literalString": opt["label"]}, "value": opt["value"]}
        if isinstance(opt["label"], str) else opt
        for opt in industry_options_raw
    ]

    prioritization_options = [
        {"label": {"literalString": opt["label"]}, "value": opt["value"]}
        if isinstance(opt["label"], str) else opt
        for opt in prioritization_options_raw
    ]

    return [
        {
            "dataModelUpdate": {
                "surfaceId": "canvas-surface",
                "contents": [
                    {"key": "selected_industry", "valueString": "Finance"},
                    {"key": "selected_prioritization", "valueString": "Account Size"}
                ]
            }
        },
        {
            "beginRendering": {
                "surfaceId": "canvas-surface",
                "root": "form-column"
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "canvas-surface",
                "components": [
                    {
                        "id": "form-column",
                        "component": { "Column": { "children": { "explicitList": ["title-text", "ind-label", "ind-select", "prio-label", "prio-select", "submit-btn"] } } }
                    },
                    {
                        "id": "title-text",
                        "component": { "Text": { "text": { "literalString": "Plan your sales visits:" }, "usageHint": "h2" } }
                    },
                    {
                        "id": "ind-label",
                        "component": { "Text": { "text": { "literalString": "Target Industry" }, "usageHint": "caption" } }
                    },
                    {
                        "id": "prio-label",
                        "component": { "Text": { "text": { "literalString": "Customer Prioritization Dimensions" }, "usageHint": "caption" } }
                    },
                    {
                        "id": "ind-select",
                        "component": {
                            "MultipleChoice": {
                                "options": industry_options,
                                "selections": {"path": "/selected_industry"},
                                "maxAllowedSelections": 1
                            }
                        }
                    },
                    {
                        "id": "prio-select",
                        "component": {
                            "MultipleChoice": {
                                "options": prioritization_options,
                                "selections": {"path": "/selected_prioritization"},
                                "maxAllowedSelections": 1
                            }
                        }
                    },
                    {
                        "id": "submit-btn",
                        "component": { 
                            "Button": { 
                                "child": "submit-text", 
                                "action": { 
                                    "name": "submit_params",
                                    "context": [
                                        {"key": "selected_industry", "value": {"path": "/selected_industry"}},
                                        {"key": "selected_prioritization", "value": {"path": "/selected_prioritization"}}
                                    ]
                                } 
                            } 
                        }
                    },
                    {
                        "id": "submit-text",
                        "component": { "Text": { "text": { "literalString": "Submit" } } }
                    }
                ]
            }
        }
    ]


def map_boston_route(route_type: str = None) -> dict:
    """Returns route data for Boston trip as full CustomView JSON.
    CRITICAL PRECONDITION: You are strictly prohibited from calling this tool until AFTER the user has clicked the confirmation button on the recommendation cards. Do not call this tool during the initial submission phase."""
    state = _read_state()
    print(f"DEBUG: map_boston_route called with state={state}")
    routes = _read_json('routes.json')
    
    # Read industry and prioritization dynamically with context-aware fallbacks
    state = _read_state()
    industry = state.get('industry')
    prioritization = state.get('prioritization')
    
    # Resolve any nested lists from multiple-choice inputs dynamically
    if isinstance(industry, list) and industry:
        industry = industry[0]
    if isinstance(prioritization, list) and prioritization:
        prioritization = prioritization[0]
        
    # Explicit error handling: inform the user precisely what is missing instead of failing silently
    if not industry or not prioritization:
        return {
            "CustomView": {
                "template": "dashboard",
                "data": {
                    "title": "Route Generation Error",
                    "subtitle": "Missing Required Session Data",
                    "kpis": [
                        { "title": "Status", "value": "Failed", "status": "warning", "sub": "State hydration incomplete" }
                    ],
                    "grid": [
                        {
                            "type": "metric",
                            "title": "Error Detail",
                            "value": "Missing Target Industry or Prioritization parameter.",
                            "status": "warning"
                        }
                    ]
                }
            }
        }
    
    try:
        recs = _read_json('recommendations.json')
        selected = recs.get(f"{industry}_{prioritization}", [])



    except Exception as e:
        print(f"Error reading recommendations: {e}")
        selected = []
        
    print(f"DEBUG: map_boston_route selected {len(selected)} accounts for key {industry}_{prioritization}: {[acc.get('name') for acc in selected]}")
        
    # Construct points for heatmap based on selection
    heatmap_points = []
    markers = []
    for acc in selected:
        heatmap_points.append([acc.get('lat'), acc.get('lng'), acc.get('intensity', 0.5)])
        markers.append([
            acc.get('lat'), 
            acc.get('lng'), 
            acc.get('intensity', 0.5),
            acc.get('name', 'Account'),
            acc.get('status', 'Active'),
            acc.get('priority', 'Medium')
        ])
            
    # Fallback to defaults if none found
    if not heatmap_points:
        heatmap_points = [
            [42.3554, -71.0664, 0.9],
            [42.3600, -71.0560, 0.95],
            [42.3662, -71.0621, 0.88],
            [42.3526, -71.0550, 0.92]
        ]
    
    mapped_routes = {}
    
    if len(selected) >= 2:
        origin = f"{selected[0]['lat']},{selected[0]['lng']}"
        destination = f"{selected[-1]['lat']},{selected[-1]['lng']}"
        waypoints = [f"{acc['lat']},{acc['lng']}" for acc in selected[1:-1]]
        
        google_route_shortest = get_accurate_route_google(origin, destination, waypoints, optimize=True)
        google_route_priority = get_accurate_route_google(origin, destination, waypoints, optimize=False)
        mapped_routes["shortest_distance"] = google_route_shortest
        mapped_routes["account_priority"] = google_route_priority

    else:
        # Fallback to static hardcoded routes if insufficient accounts selected
        key_base = f"{industry}_{prioritization}"
        shortest_key = f"{key_base}_shortest"
        priority_key = f"{key_base}_priority"
        
        if shortest_key in routes:
            mapped_routes["shortest_distance"] = routes[shortest_key]
        if priority_key in routes:
            mapped_routes["account_priority"] = routes[priority_key]


        
    config = {"enableHeatmap": True, "enableWeatherStub": True}
    a2ui_payload = build_map_payload(
        center=[42.3601, -71.0589],
        zoom=14,
        heatmap_points=heatmap_points,
        markers=markers,
        routes=mapped_routes,
        config=config
    )

    
    return a2ui_payload

def forecast_trip_arr(scenario: str = "conservative", image_url: str = None) -> dict:
    """Returns forecast data for trip as full CustomView JSON."""
    print(f"DEBUG: forecast_trip_arr called with scenario={scenario}")
    forecasts = _read_json('forecasts.json')
    print(f"DEBUG: Available scenarios: {list(forecasts.keys())}")
    scenario_data = forecasts.get(scenario, {})
    print(f"DEBUG: Scenario data found: {bool(scenario_data)}")
    
    # Read state for cascading results
    state = _read_state()
    selected_ids = state.get('selected_accounts', [])
    industry = state.get('industry', 'Northeast')
    
    # Calculate sum of ARR for selected accounts
    accounts_data = _read_json('accounts.json')
    total_arr = 0
    if isinstance(accounts_data, list):
        for acc in accounts_data:
            if acc.get('id') in selected_ids:
                total_arr += acc.get('arr', 0)
                
    # Fallback to forecast default if no accounts selected or sum is 0
    if total_arr == 0:
        arr_data = scenario_data.get("arr", [])
        total_arr = arr_data[-1] if arr_data else 450000
        
    display_arr = f"${total_arr:,}"
    
    if not image_url or image_url.startswith("Error") or "failed" in image_url.lower():
        logger.warning(f"Media generation failed or returned invalid URL: {image_url}. Falling back to default public image.")
        image_url = "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/woman.jpg"
        
    # Construct full CustomView payload
    a2ui_payload = {
        "CustomView": {
            "template": "dashboard",
            "data": {
                "title": f"{industry} Trip Forecast",
                "subtitle": f"Scenario: {scenario.capitalize()}",
                "kpis": [
                    { "title": "Projected ARR", "value": display_arr, "status": "success", "sub": "At Month 6" },
                    { "title": "Target Gap", "value": "$5,000", "status": "warning", "sub": "To Goal" }
                ],
                "grid": [
                    {
                        "type": "image",
                        "title": "Client Briefing Cover",
                        "data": {
                            "src": image_url,
                            "alt": "Client Briefing Cover"
                        }
                    },
                    {
                        "type": "metric",
                        "title": "Projected Final ARR",
                        "value": display_arr,
                        "status": "success"
                    },
                    {
                        "type": "chart",
                        "title": "ARR Growth Projection",
                        "data": {
                            "type": "line",
                            "label": "ARR ($)",
                            "labels": scenario_data.get("labels", []),
                            "data": scenario_data.get("arr", [])
                        }
                    }
                ]
            }
        }
    }
    
    return a2ui_payload
