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

def build_audio_card(data):
    """Constructs Native A2UI component tree for a standalone audio summary card."""
    url = data.get('audio_url') if isinstance(data, dict) else data
    if not url:
        url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        
    desc = data.get('transcript', "Executive Audio Summary") if isinstance(data, dict) else "Audio Summary"
    
    components = [
        cl.card(element_id="audio-card", child="audio-col"),
        cl.column(element_id="audio-col", children=["audio-title", "audio-player-root"]),
        cl.text(element_id="audio-title", content="Audio Summary & Insights", usage_hint="h3"),
        cl.audio_player(element_id="audio-player-root", audio_url=url, description=desc)
    ]
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="audio-card"),
        cl.surface_update(surface_id="canvas-surface", components=components)
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

def build_showcase_widgets_card(data):
    """Constructs Native A2UI 0.8 components showcase card containing Tabs, Modal, Inputs, Choices, and Buttons."""
    widgets = data.get("widgets", {})
    title = widgets.get("title", "A2UI Showcase")
    desc = widgets.get("description", "Capability Showcase")
    
    dropdown_choices = data.get("dropdown_choices", ["A", "B"])
    checkboxes = data.get("checkboxes", [])
    slider_val = data.get("slider_value", 50)
    slider_min = data.get("slider_min", 0)
    slider_max = data.get("slider_max", 100)
    modal_content = data.get("modal_content", {})
    
    # Active state rehydration values
    state = data.get("state", {})
    active_ref = state.get("tf_name_state", "Alex Carter")
    active_key = state.get("tf_key_state", "ENT-9842-XYZ")
    active_slider = float(state.get("slider_1_state", slider_val))
    active_choice = state.get("dropdown_state", dropdown_choices[0])
    
    components = []
    
    # Base wrapper card & base column
    components.append(cl.card(element_id="showcase-card", child="showcase-col"))
    components.append(cl.column(element_id="showcase-col", children=[
        "header-row", "desc-text", "div-mid", "showcase-tabs", "div-low", "action-row"
    ]))
    
    # Header Row
    components.append(cl.row(element_id="header-row", children=["header-icon", "header-title"], distribution="center"))
    components.append(cl.icon(element_id="header-icon", name="settings"))
    components.append(cl.text(element_id="header-title", content=title, usage_hint="h3"))
    components.append(cl.text(element_id="desc-text", content=desc, usage_hint="caption"))
    components.append(cl.divider(element_id="div-mid"))
    
    # Tabs section separating three sheets
    components.append(cl.tabs(
        element_id="showcase-tabs",
        titles=["Form Inputs", "Picklists & Check", "Modal Popup"],
        children=["tab-inputs-card", "tab-picks-card", "tab-overlay-card"]
    ))
    
    # Card wrappers for tabs contents
    components.append(cl.card(element_id="tab-inputs-card", child="tab-inputs-col"))
    components.append(cl.card(element_id="tab-picks-card", child="tab-picks-col"))
    components.append(cl.card(element_id="tab-overlay-card", child="tab-overlay-col"))
    
    # Tab 1: Form Inputs (TextFields + Sliders)
    components.append(cl.column(element_id="tab-inputs-col", children=[
        "tf-ref-title", "tf_name", "tf-key-title", "tf_key", "slider-title", "slider_1"
    ]))
    components.append(cl.text(element_id="tf-ref-title", content="Reference Tag", usage_hint="caption"))
    tf_name = cl.text_field(element_id="tf_name", label="Enter reference name...", value=active_ref)
    tf_name["component"]["TextField"]["text"] = {"path": "/tf_name_state", "literalString": active_ref}
    components.append(tf_name)

    components.append(cl.text(element_id="tf-key-title", content="Security ID", usage_hint="caption"))
    tf_key = cl.text_field(element_id="tf_key", label="Enter identifier...", value=active_key)
    tf_key["component"]["TextField"]["text"] = {"path": "/tf_key_state", "literalString": active_key}
    components.append(tf_key)

    components.append(cl.text(element_id="slider-title", content="Capacity Scale Limit", usage_hint="caption"))
    slider_1 = cl.slider(element_id="slider_1", min_val=slider_min, max_val=slider_max, value=active_slider)
    slider_1["component"]["Slider"]["value"] = {"path": "/slider_1_state", "literalNumber": active_slider}
    components.append(slider_1)
    
    # Tab 2: Choices & Picklists
    components.append(cl.column(element_id="tab-picks-col", children=[
        "choice-title", "dropdown", "chk-title", "chk_options"
    ]))
    components.append(cl.text(element_id="choice-title", content="Select Container Mode", usage_hint="caption"))
    
    # Premium card-wrapped MultipleChoice select dropdown
    mc = cl.multiple_choice(element_id="dropdown", options=dropdown_choices)
    # CRITICAL: Force selection properties matching A2UI 0.8 React standard
    mc["component"]["MultipleChoice"]["selections"] = {"path": "/dropdown_state"}
    mc["component"]["MultipleChoice"]["maxAllowedSelections"] = 1
    # Pre-select active choice from state
    for opt in mc["component"]["MultipleChoice"]["options"]:
        if opt["value"] == active_choice:
            mc["component"]["MultipleChoice"]["selections"]["literalString"] = active_choice
            
    components.append(mc)
    
    components.append(cl.text(element_id="chk-title", content="Enforce Infrastructure Rules", usage_hint="caption"))
    
    # Renders beautiful, native checkboxes using multiselect MultipleChoice
    mc_chk = cl.multiple_choice(element_id="chk_options", options=["Establish Sandbox VPC Boundary", "Enforce Secure SSL/TLS Channels"])
    mc_chk["component"]["MultipleChoice"]["selections"] = {"path": "/chk_options_state"}
    mc_chk["component"]["MultipleChoice"]["maxAllowedSelections"] = 5 # Enables native checkboxes list rendering!
    
    # Pre-check state values
    active_chks = state.get("chk_options_state", ["Enforce Secure SSL/TLS Channels"])
    mc_chk["component"]["MultipleChoice"]["selections"]["literalArray"] = active_chks
    components.append(mc_chk)
    
    # Tab 3: Modal Popup Container
    components.append(cl.column(element_id="tab-overlay-col", children=["modal-hint", "modal-trigger-card", "modal_showcase"]))
    components.append(cl.text(element_id="modal-hint", content="Triggers a native popup overlay modal dialog box.", usage_hint="body"))
    
    # Clickable Card serving as EntryPoint to Modal overlay (prevents redundant server actions)
    components.append(cl.card(element_id="modal-trigger-card", child="modal-trigger-txt"))
    components.append(cl.text(element_id="modal-trigger-txt", content="Launch Architecture Insight ↗", usage_hint="body"))
    
    # The Modal itself
    components.append(cl.modal(element_id="modal_showcase", entry_id="modal-trigger-card", content_id="modal-content-card"))
    
    # Modal popup content card structure
    components.append(cl.card(element_id="modal-content-card", child="modal-content-col"))
    components.append(cl.column(element_id="modal-content-col", children=["modal-content-title", "modal-content-body"]))
    components.append(cl.text(element_id="modal-content-title", content=modal_content.get("title", "Insight"), usage_hint="h4"))
    components.append(cl.text(element_id="modal-content-body", content=modal_content.get("body", ""), usage_hint="body"))
    
    components.append(cl.divider(element_id="div-low"))
    
    # Bottom Row Action Buttons
    components.append(cl.row(element_id="action-row", children=["btn_save_state", "btn_load_state"], distribution="spaceBetween"))
    
    # Save state action
    save_btn = cl.button(
        element_id="btn_save_state", 
        label="Save Active Selection", 
        action_name="save_widget_selection", 
        context=[
            {"key": "dropdown_state", "value": {"path": "/dropdown_state"}},
            {"key": "tf_name_state", "value": {"path": "/tf_name_state"}},
            {"key": "tf_key_state", "value": {"path": "/tf_key_state"}},
            {"key": "slider_1_state", "value": {"path": "/slider_1_state"}},
            {"key": "chk_options_state", "value": {"path": "/chk_options_state"}}
        ], 
        primary=True
    )
    components.extend(save_btn)
    
    # Load state action
    load_btn = cl.button(element_id="btn_load_state", label="Load Last Run", action_name="load_widget_selection", context=[], primary=False)
    components.extend(load_btn)
    
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="showcase-card"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

