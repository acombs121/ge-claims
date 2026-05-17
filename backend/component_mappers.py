import os
import component_library as cl

def build_benefits_card(data):
    """Constructs Native A2UI component tree for benefits summary."""
    vacation = data.get('vacation', {})
    benefits = data.get('benefits', [])
    
    components = []
    
    components.append(cl.card(element_id="benefits-card", child="benefits-col"))
    
    components.append(cl.column(element_id="benefits-col", children=["header-row", "div1", "vacation-row", "div2", "benefits-title", "benefits-list"]))
    
    components.append(cl.row(element_id="header-row", children=["icon-cal", "title-text"], distribution="center"))
    components.append(cl.icon(element_id="icon-cal", name="calendarToday"))
    components.append(cl.text(element_id="title-text", content="Employee Benefits & Time Off", usage_hint="h3"))
    
    components.append(cl.divider(element_id="div1"))
    
    components.append(cl.row(element_id="vacation-row", children=["total-col", "used-col", "rem-col"], distribution="spaceAround"))
    
    components.append(cl.column(element_id="total-col", children=["total-val", "total-lbl"]))
    components.append(cl.text(element_id="total-val", content=str(vacation.get('total', 0)), usage_hint="h2"))
    components.append(cl.text(element_id="total-lbl", content="TOTAL DAYS", usage_hint="caption"))
    
    components.append(cl.column(element_id="used-col", children=["used-val", "used-lbl"]))
    components.append(cl.text(element_id="used-val", content=str(vacation.get('used', 0)), usage_hint="h2"))
    components.append(cl.text(element_id="used-lbl", content="USED", usage_hint="caption"))
    
    components.append(cl.column(element_id="rem-col", children=["rem-val", "rem-lbl"]))
    components.append(cl.text(element_id="rem-val", content=str(vacation.get('remaining', 0)), usage_hint="h1"))
    components.append(cl.text(element_id="rem-lbl", content="REMAINING", usage_hint="caption"))
    
    components.append(cl.divider(element_id="div2"))
    
    components.append(cl.text(element_id="benefits-title", content="Active Enrollments", usage_hint="h4"))
    
    benefit_ids = [f"benefit-{i}" for i in range(len(benefits))]
    components.append(cl.list_explicit(element_id="benefits-list", children=benefit_ids, direction="vertical"))
    
    for i, benefit in enumerate(benefits):
        components.append(cl.row(element_id=f"benefit-{i}", children=[f"b-name-{i}", f"b-status-{i}"], distribution="spaceBetween"))
        components.append(cl.text(element_id=f"b-name-{i}", content=benefit.get('name', ''), usage_hint="body"))
        components.append(cl.text(element_id=f"b-status-{i}", content=benefit.get('status', ''), usage_hint="body"))
        
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="benefits-card"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def build_confirmation_card(data):
    """Constructs Native A2UI component tree for a simple confirmation message."""
    message = data.get('message', 'Action completed successfully.')
    components = [
        cl.card(element_id="success-card", child="success-text"),
        cl.text(element_id="success-text", content=message, usage_hint="body")
    ]
    return [
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def build_image_card(data):
    """Constructs Native A2UI component tree for a standalone image."""
    url = data.get('src') if isinstance(data, dict) else data
    if not url:
        url = "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/woman.jpg"
        
    components = [
        cl.image(element_id="skills-img", url=url, usage_hint="largeFeature", fit="contain")
    ]
    return [
        cl.begin_rendering(surface_id="skills-surface", root="skills-img"),
        cl.surface_update(surface_id="skills-surface", components=components)
    ]

def build_product_table(data):
    """Constructs Native A2UI component tree for a product selection table."""
    columns = data.get('columns', [
        {"key": "name", "label": "Product", "type": "string"},
        {"key": "category", "label": "Category", "type": "picklist", "editable": True, "options": ["Basic", "Premium", "Enterprise"]},
        {"key": "price", "label": "Price ($)", "type": "number", "editable": True}
    ])
    rows = data.get('rows', [
        {"name": "HR Platform License", "category": "Premium", "price": 5000},
        {"name": "Performance Module", "category": "Enterprise", "price": 2500}
    ])
    title = data.get('title', "Select Included Products")
    
    components = [
        cl.product_selection(
            element_id="product-sel-root",
            columns=columns,
            rows=rows,
            title=title,
            confirm_label="Save Selection",
            cancel_label="Reset",
            on_confirm_action="save_product_selection",
            on_cancel_action="reset_product_selection"
        )
    ]
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="product-sel-root"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]
