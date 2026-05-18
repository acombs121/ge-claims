import component_library as cl

def render_ui_button(label: str = "Submit", action_name: str = "button_clicked", primary: bool = True) -> list:
    """Generates and renders a standalone interactive Button component in the UI."""
    btn_nodes = cl.button(element_id="btn_root", label=label, action_name=action_name, context=[], primary=primary)
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="btn_root"),
        cl.surface_update(surface_id="canvas-surface", components=btn_nodes)
    ]

def render_ui_dropdown(options: list[str] = ["Option A", "Option B"], title: str = "Select an Option") -> list:
    """Generates and renders a selectable dropdown/picklist menu component in the UI."""
    components = []
    components.append(cl.card(element_id="dropdown-card", child="dropdown-col"))
    
    child_ids = ["title-lbl"]
    components.append(cl.text(element_id="title-lbl", content=title, usage_hint="h4"))
    
    for idx, opt in enumerate(options):
        b_id = f"opt_btn_{idx}"
        child_ids.append(b_id)
        btn_nodes = cl.button(element_id=b_id, label=str(opt), action_name="select_option", context=[{"option": str(opt)}])
        components.extend(btn_nodes)
        
    components.append(cl.column(element_id="dropdown-col", children=child_ids))
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="dropdown-card"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def render_ui_table(title: str = "Data Overview", headers: list[str] = ["Item", "Status"], rows: list[list[str]] = [["System", "Active"]]) -> list:
    """Generates and renders a structured data table in the UI."""
    components = []
    components.append(cl.card(element_id="table-card", child="table-col"))
    
    child_ids = ["table-title"]
    components.append(cl.text(element_id="table-title", content=title, usage_hint="h3"))
    
    # Header row
    h_row_ids = []
    for idx, h in enumerate(headers):
        h_id = f"th_{idx}"
        h_row_ids.append(h_id)
        components.append(cl.text(element_id=h_id, content=str(h).upper(), usage_hint="h4"))
    
    components.append(cl.row(element_id="header-row", children=h_row_ids, distribution="spaceBetween"))
    child_ids.append("header-row")
    components.append(cl.divider(element_id="table-div"))
    child_ids.append("table-div")
    
    for r_idx, r in enumerate(rows):
        r_row_ids = []
        for c_idx, val in enumerate(r):
            cell_id = f"cell_{r_idx}_{c_idx}"
            r_row_ids.append(cell_id)
            components.append(cl.text(element_id=cell_id, content=str(val), usage_hint="body"))
        r_id = f"row_{r_idx}"
        components.append(cl.row(element_id=r_id, children=r_row_ids, distribution="spaceBetween"))
        child_ids.append(r_id)
        
    components.append(cl.column(element_id="table-col", children=child_ids))
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="table-card"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def render_ui_card(title: str = "Information Card", body_text: str = "Detailed descriptive content for the user.") -> list:
    """Generates and renders a standalone information Card component in the UI."""
    components = [
        cl.card(element_id="info-card", child="info-col"),
        cl.column(element_id="info-col", children=["info-title", "info-body"]),
        cl.text(element_id="info-title", content=title, usage_hint="h3"),
        cl.text(element_id="info-body", content=body_text, usage_hint="body")
    ]
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="info-card"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def render_ui_tabs(tab_titles: list[str] = ["Tab 1", "Tab 2"], tab_contents: list[str] = ["Content for Tab 1", "Content for Tab 2"]) -> list:
    """Generates and renders an interactive multi-view Tabs component in the UI."""
    components = []
    child_ids = []
    for idx, content_str in enumerate(tab_contents):
        c_id = f"tab_c_{idx}"
        child_ids.append(c_id)
        components.append(cl.text(element_id=c_id, content=str(content_str), usage_hint="body"))
        
    components.append(cl.tabs(element_id="tabs-root", titles=tab_titles, children=child_ids, selected=0))
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="tabs-root"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def render_ui_modal(button_label: str = "Open Details", modal_title: str = "Context Details", modal_content: str = "Full expanded breakdown of information.") -> list:
    """Generates and renders an interactive button that opens an overlay Modal dialog in the UI."""
    components = []
    
    btn_nodes = cl.button(element_id="modal-entry-btn", label=button_label, action_name="open_modal", context=[])
    components.extend(btn_nodes)
    
    components.append(cl.column(element_id="modal-content-col", children=["m-title", "m-body"]))
    components.append(cl.text(element_id="m-title", content=modal_title, usage_hint="h3"))
    components.append(cl.text(element_id="m-body", content=modal_content, usage_hint="body"))
    
    components.append(cl.modal(element_id="modal-root", entry_id="modal-entry-btn", content_id="modal-content-col"))
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="modal-root"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def render_ui_dropdown(title: str = "Select an Option", options: list[str] = ["Option A", "Option B"]) -> list:
    """Generates and renders a dropdown selection menu in the UI using MultipleChoice."""
    components = [
        cl.multiple_choice(element_id="dropdown-comp", options=options)
    ]
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="dropdown-comp"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def render_ui_checkbox(labels: list[str] = ["Option X", "Option Y"]) -> list:
    """Generates and renders a list of CheckBox components inside a vertical Column in the UI."""
    components = []
    child_ids = []
    for idx, label_str in enumerate(labels):
        c_id = f"chk_{idx}"
        child_ids.append(c_id)
        components.append(cl.checkbox(element_id=c_id, label=label_str, checked=False))
        
    components.append(cl.column(element_id="checkbox-col", children=child_ids))
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="checkbox-col"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]
