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
