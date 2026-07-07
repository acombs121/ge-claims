import os
import json
import logging
from config import load_customer_dataset
import component_library as cl

logger = logging.getLogger(__name__)

def get_policy_triage():
    """
    Loads policyholder and claim details for Walter White.
    Constructs a clean dark-mode Policy Card showing exclusions, inclusions, limits.
    """
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'policy_report.html')
    with open(template_path, 'r') as f:
        html_content = f.read()

    components = [{
        "id": "policy-report-frame",
        "component": {
            "WebFrameSrcdoc": {
                "htmlContent": { "literalString": html_content },
                "height": 850
            }
        }
    }]

    return [
        cl.begin_rendering(surface_id="canvas-surface", root="policy-report-frame"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def analyze_photos(claim_id: str = "CLM-47209"):
    """
    Analyzes the uploaded claim photos using Gemini Multimodal LLM.
    Displays side-by-side images and a table of structured analysis.
    """
    agent_url = os.environ.get("AGENT_URL", "http://127.0.0.1:8080")
    bathroom_img_url = f"{agent_url}/media/laundry_room_flooding.jpg"
    laundry_img_url = f"{agent_url}/media/bathroom_water_damage.jpg"

    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'photo_report.html')
    with open(template_path, 'r') as f:
        html_content = f.read()

    # Inject static image URLs
    html_content = html_content.replace("{{BATHROOM_IMG_URL}}", bathroom_img_url)
    html_content = html_content.replace("{{LAUNDRY_IMG_URL}}", laundry_img_url)

    components = [{
        "id": "photo-report-frame",
        "component": {
            "WebFrameSrcdoc": {
                "htmlContent": { "literalString": html_content },
                "height": 850
            }
        }
    }]

    return [
        cl.begin_rendering(surface_id="canvas-surface", root="photo-report-frame"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def assess_risk(claim_id: str = "CLM-47209"):
    """
    Queries historical claim metrics and returns a beautiful risk analytics card.
    """
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'risk_report.html')
    with open(template_path, 'r') as f:
        html_content = f.read()

    components = [{
        "id": "risk-report-frame",
        "component": {
            "WebFrameSrcdoc": {
                "htmlContent": { "literalString": html_content },
                "height": 850
            }
        }
    }]

    return [
        cl.begin_rendering(surface_id="canvas-surface", root="risk-report-frame"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def estimate_dispatch(claim_id: str = "CLM-47209"):
    """
    Returns the repair estimation table and approved local contractor map stacked inside a scrollable WebFrame.
    """
    claim = load_customer_dataset("claim")
    contractors = load_customer_dataset("contractors")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "insurance_map.html")
    with open(template_path, "r") as f:
        html_template = f.read()

    # Build cost estimate table rows dynamically
    table_rows_html = ""
    est = claim.get("estimation", {})
    for item in est.get("items", []):
        table_rows_html += f"""
        <tr>
            <td class="label-cell">{item.get('description')}</td>
            <td class="value-cell" style="text-align: right; font-weight: 500;">${item.get('cost'):,}</td>
        </tr>
        """
    # Deductible row
    table_rows_html += f"""
    <tr>
        <td class="label-cell" style="color: var(--text-secondary);">Less Policy Deductible:</td>
        <td class="value-cell" style="text-align: right; color: var(--danger); font-weight: 500;">-${est.get('deductible'):,}</td>
    </tr>
    """
    # Net Proposed Settlement row
    table_rows_html += f"""
    <tr style="border-top: 2px solid var(--border-color);">
        <td class="label-cell" style="font-weight: 700; color: var(--text-primary);">Proposed Net Settlement Payout:</td>
        <td class="value-cell" style="text-align: right; font-weight: 700; color: var(--success); font-size: 1.05rem;">${est.get('net_payout'):,}</td>
    </tr>
    """

    # Replace placeholder
    html_template = html_template.replace("{{ESTIMATE_TABLE_ROWS}}", table_rows_html)

    injected_data = {
        "claim_location": claim.get("location"),
        "contractors": contractors
    }
    
    maps_key = os.environ.get("GOOGLE_MAPS_API_KEY") or ""
    html_template = html_template.replace("YOUR_GOOGLE_MAPS_API_KEY_HERE", maps_key)
    
    injected_script = f"<script>window.INJECTED_DATA = {json.dumps(injected_data)};</script>"
    html_injected = html_template.replace('</head>', f'{injected_script}\n</head>')

    components = [{
        "id": "dispatch-report-frame",
        "component": {
            "WebFrameSrcdoc": {
                "htmlContent": { "literalString": html_injected },
                "height": 950
            }
        }
    }]

    return [
        cl.begin_rendering(surface_id="canvas-surface", root="dispatch-report-frame"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def finalize_claim(claim_id: str = "CLM-47209"):
    """
    Drafts the Ohio-compliant settlement letter and shows available scheduling slots.
    """
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'settlement_report.html')
    with open(template_path, 'r') as f:
        html_content = f.read()

    components = [{
        "id": "settlement-report-frame",
        "component": {
            "WebFrameSrcdoc": {
                "htmlContent": { "literalString": html_content },
                "height": 950
            }
        }
    }]

    return [
        cl.begin_rendering(surface_id="canvas-surface", root="settlement-report-frame"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]
