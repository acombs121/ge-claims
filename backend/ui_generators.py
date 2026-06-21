import component_library as cl

def render_ui_button(label: str = "Submit", action_name: str = "button_clicked", primary: bool = True) -> list:
    """Generates and renders a standalone interactive Button component in the UI."""
    btn_nodes = cl.button(element_id="btn_root", label=label, action_name=action_name, context=[], primary=primary)
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="btn_root"),
        cl.surface_update(surface_id="canvas-surface", components=btn_nodes)
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
    """Generates and renders an interactive overlay Modal dialog in the UI without triggering server actions."""
    components = []
    
    # Clickable Card serving as EntryPoint to Modal overlay (prevents redundant server actions)
    components.append(cl.card(element_id="modal-entry-card", child="modal-entry-txt"))
    components.append(cl.text(element_id="modal-entry-txt", content=button_label, usage_hint="body"))
    
    components.append(cl.column(element_id="modal-content-col", children=["m-title", "m-body"]))
    components.append(cl.text(element_id="m-title", content=modal_title, usage_hint="h3"))
    components.append(cl.text(element_id="m-body", content=modal_content, usage_hint="body"))
    
    components.append(cl.modal(element_id="modal-root", entry_id="modal-entry-card", content_id="modal-content-col"))
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="modal-root"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def render_ui_dropdown(title: str = "Select an Option", options: list[str] = ["Option A", "Option B"]) -> list:
    """Generates and renders a dropdown selection menu in the UI wrapped in a Card and Column, complete with a state-bound Submit Button."""
    components = []
    components.append(cl.card(element_id="dropdown-card", child="dropdown-col"))
    components.append(cl.column(element_id="dropdown-col", children=["dropdown-title", "dropdown-comp", "dropdown-submit-btn"]))
    components.append(cl.text(element_id="dropdown-title", content=title, usage_hint="h4"))
    dropdown_comp = cl.multiple_choice(element_id="dropdown-comp", options=options)
    dropdown_comp["component"]["MultipleChoice"]["selections"] = {"path": "/dropdown-comp_state"}
    dropdown_comp["component"]["MultipleChoice"]["maxAllowedSelections"] = 1
    components.append(dropdown_comp)
    
    # Add State-Bound Submit Button conforming to A2UI schema
    components.append({
        "id": "dropdown-submit-btn",
        "component": {
            "Button": {
                "child": "dropdown-submit-txt",
                "primary": True,
                "action": {
                    "name": "select_option",
                    "context": [
                        {
                            "key": "selection",
                            "value": {"path": "/dropdown-comp_state"}
                        }
                    ]
                }
            }
        }
    })
    components.append(cl.text(element_id="dropdown-submit-txt", content="Confirm Selection", usage_hint="body"))
    
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="dropdown-card"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]

def render_ui_checkbox(labels: list[str] = ["Option X", "Option Y"], title: str = "Select Options") -> list:
    """Generates and renders a list of CheckBox components wrapped inside a Card complete with a Submit Button."""
    components = []
    components.append(cl.card(element_id="checkbox-card", child="checkbox-col"))
    
    child_ids = ["checkbox-title"]
    components.append(cl.text(element_id="checkbox-title", content=title, usage_hint="h4"))
    
    for idx, label_str in enumerate(labels):
        c_id = f"chk_{idx}"
        child_ids.append(c_id)
        chk_comp = cl.checkbox(element_id=c_id, label=label_str, checked=False)
        chk_comp["component"]["CheckBox"]["checked"] = {"path": f"/chk_{idx}_state"}
        components.append(chk_comp)
        
    # Add Submit Button
    btn_id = "checkbox-submit-btn"
    txt_id = "checkbox-submit-txt"
    child_ids.append(btn_id)
    
    context_list = []
    for idx, label_str in enumerate(labels):
        context_list.append({
            "key": f"chk_{idx}_selected",
            "value": {"path": f"/chk_{idx}_state"}
        })
        
    components.append({
        "id": btn_id,
        "component": {
            "Button": {
                "child": txt_id,
                "primary": True,
                "action": {
                    "name": "submit_selections",
                    "context": context_list
                }
            }
        }
    })
    components.append(cl.text(element_id=txt_id, content="Confirm Selections", usage_hint="body"))
    
    components.append(cl.column(element_id="checkbox-col", children=child_ids))
    return [
        cl.begin_rendering(surface_id="canvas-surface", root="checkbox-card"),
        cl.surface_update(surface_id="canvas-surface", components=components)
    ]
