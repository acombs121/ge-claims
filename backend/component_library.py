"""Helper functions to build A2UI components cleanly.

Based on documentation for A2UI 0.8 compatibility.
"""

from collections.abc import Sequence
from typing import Any

def text(
    *, element_id: str, content: str, usage_hint: str = "body"
) -> dict[str, Any]:
  """Generates a Text component."""
  return {
      "id": element_id,
      "component": {
          "Text": {
              "text": {"literalString": content},
              "usageHint": usage_hint,
          }
      },
  }

def column(*, element_id: str, children: list[str]) -> dict[str, Any]:
  """Generates a Column component."""
  return {
      "id": element_id,
      "component": {"Column": {"children": {"explicitList": children}}},
  }

def card(*, element_id: str, child: str) -> dict[str, Any]:
  """Generates a Card component."""
  return {
      "id": element_id,
      "component": {"Card": {"child": child}},
  }

def button(
    *,
    element_id: str,
    label: str,
    action_name: str,
    context: Sequence[dict[str, Any]],
    primary: bool = False,
) -> list[dict[str, Any]]:
  """Generates a Button component and its required Text child component."""
  text_id = f"txt_{element_id}"
  return [
      {
          "id": element_id,
          "component": {
              "Button": {
                  "child": text_id,
                  "primary": primary,
                  "action": {
                      "name": action_name,
                      "context": context,
                  },
              }
          },
      },
      {
          "id": text_id,
          "component": {
              "Text": {
                  "text": {"literalString": label},
                  "usageHint": "body",
              }
          },
      },
  ]

def row(
    *, element_id: str, children: list[str], distribution: str = ""
) -> dict[str, Any]:
  """Generates a Row component."""
  row_component = {"children": {"explicitList": children}}
  if distribution:
    row_component["distribution"] = distribution
  return {
      "id": element_id,
      "component": {"Row": row_component},
  }

def icon(
    *, element_id: str, name: str
) -> dict[str, Any]:
  """Generates an Icon component."""
  return {
      "id": element_id,
      "component": {
          "Icon": {
              "name": {"literalString": name},
          }
      },
  }

def image(
    *,
    element_id: str,
    url: str = "",
    url_path: str = "",
    usage_hint: str = "mediumFeature",
    fit: str = "contain",
) -> dict[str, Any]:
  """Generates an Image component."""
  image_url = {"path": url_path} if url_path else {"literalString": url}
  return {
      "id": element_id,
      "component": {
          "Image": {
              "url": image_url,
              "usageHint": usage_hint,
              "fit": fit,
          }
      },
  }

def divider(*, element_id: str) -> dict[str, Any]:
  """Generates a Divider component."""
  return {
      "id": element_id,
      "component": {"Divider": {}},
  }

def list_explicit(
    *, element_id: str, children: list[str], direction: str = "vertical"
) -> dict[str, Any]:
  """Generates a List component with explicit children."""
  return {
      "id": element_id,
      "component": {
          "List": {
              "children": {"explicitList": children},
              "direction": direction,
          }
      },
  }

def mime_type() -> dict[str, str]:
  """Returns the standard A2UI MIME type metadata."""
  return {"mimeType": "application/json+a2ui"}

def surface_update(
    *, surface_id: str, components: list[dict[str, Any]]
) -> dict[str, Any]:
  """Generates a surfaceUpdate payload."""
  return {
      "surfaceUpdate": {
          "surfaceId": surface_id,
          "components": components,
      }
  }

def begin_rendering(
    *, surface_id: str, root: str = "root"
) -> dict[str, Any]:
  """Generates a beginRendering payload."""
  return {
      "beginRendering": {
          "surfaceId": surface_id,
          "root": root,
      }
  }

def web_frame_url(
    *, element_id: str, url: str, height: int = 450
) -> dict[str, Any]:
  """Generates a WebFrameUrl component for allowlisted external iframes."""
  return {
      "id": element_id,
      "component": {
          "WebFrameUrl": {
              "url": {"literalString": url},
              "height": height,
          }
      },
  }

def product_selection(
    *,
    element_id: str,
    columns: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    title: str = "Product Selection",
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    on_confirm_action: str = "",
    on_cancel_action: str = "",
) -> dict[str, Any]:
  """Generates a ProductSelection custom native component for editable tables/picklists."""
  component_data: dict[str, Any] = {
      "columns": columns,
      "rows": rows,
      "productTableTitle": title,
      "confirmLabel": confirm_label,
      "cancelLabel": cancel_label,
  }
  if on_confirm_action:
    component_data["onConfirm"] = {"name": on_confirm_action, "context": []}
  if on_cancel_action:
    component_data["onCancel"] = {"name": on_cancel_action, "context": []}
    
  return {
      "id": element_id,
      "component": {
          "ProductSelection": component_data
      }
  }

def audio_player(
    *, element_id: str, audio_url: str, description: str = "Audio Summary"
) -> dict[str, Any]:
  """Generates an AudioPlayer component."""
  return {
      "id": element_id,
      "component": {
          "AudioPlayer": {
              "url": {"literalString": audio_url},
              "description": {"literalString": description},
          }
      },
  }

def tabs(*, element_id: str, titles: list[str], children: list[str], selected: int = 0) -> dict[str, Any]:
  """Generates a Tabs component conforming to A2UI schema."""
  tab_items = []
  for t, child_id in zip(titles, children):
      tab_items.append({
          "title": {"literalString": str(t)},
          "child": child_id
      })
  return {
      "id": element_id,
      "component": {
          "Tabs": {
              "tabItems": tab_items
          }
      },
  }

def modal(*, element_id: str, entry_id: str, content_id: str) -> dict[str, Any]:
  """Generates a Modal component conforming to A2UI schema."""
  return {
      "id": element_id,
      "component": {
          "Modal": {
              "entryPointChild": entry_id,
              "contentChild": content_id,
          }
      },
  }

def multiple_choice(*, element_id: str, options: list[str], selected: list[str] = None) -> dict[str, Any]:
  """Generates a MultipleChoice component conforming to A2UI schema."""
  return {
      "id": element_id,
      "component": {
          "MultipleChoice": {
              "options": [
                  {
                      "label": {"literalString": str(opt)},
                      "value": str(opt)
                  } for idx, opt in enumerate(options)
              ],
              "selections": {"path": f"/{element_id}_state"},
              "maxAllowedSelections": 1
          }
      },
  }

def checkbox(*, element_id: str, label: str, checked: bool = False, path: str = "") -> dict[str, Any]:
  """Generates a CheckBox component conforming to A2UI schema."""
  val_node = {"path": path} if path else {"literalBoolean": checked}
  return {
      "id": element_id,
      "component": {
          "CheckBox": {
              "label": {"literalString": label},
              "value": val_node,
          }
      },
  }

def text_field(*, element_id: str, label: str = "", value: str = "", text_field_type: str = "shortText") -> dict[str, Any]:
  """Generates a TextField component conforming to A2UI schema."""
  tf_data = {
      "label": {"literalString": label or "Input"},
  }
  if value:
      tf_data["text"] = {"literalString": value}
  if text_field_type:
      tf_data["textFieldType"] = text_field_type
  return {
      "id": element_id,
      "component": {
          "TextField": tf_data
      }
  }

def slider(*, element_id: str, min_val: float = 0, max_val: float = 100, value: float = 50) -> dict[str, Any]:
  """Generates a Slider component conforming to A2UI schema."""
  return {
      "id": element_id,
      "component": {
          "Slider": {
              "value": {"literalNumber": value},
              "minValue": min_val,
              "maxValue": max_val,
          }
      },
  }

