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
                    "type": "bar",
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
    print(f"\n[AGENT_PLATFORM] Agent 'aon_hr_agent' performed action 'register_benefit' for benefit '{benefit_name}' for user '{user_name}' ({user_id}) at {timestamp}\n")
    logger.info(f"[AGENT_PLATFORM] Agent 'aon_hr_agent' performed action 'register_benefit' for benefit '{benefit_name}' for user '{user_name}' ({user_id}) at {timestamp}")
    
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
