"""Agent executor for ADK agents with dynamic WebFrame template orchestration."""

import json
import logging
import os
import uuid
from a2a import types
from a2a import utils
from a2a.server import agent_execution
from a2a.server import events
from a2a.server import tasks
from a2a.utils import errors as a2a_errors
import a2ui_schema_full as a2ui_schema
from google.adk import runners
from google.adk.artifacts import in_memory_artifact_service
from google.adk.memory import in_memory_memory_service
from google.adk.sessions import in_memory_session_service
from google.genai import types as genai_types
import jsonschema

logger = logging.getLogger(__name__)


class AdkAgentToA2AExecutor(agent_execution.AgentExecutor):
  """An agent executor for ADK agents with dynamic layout interpolation."""

  _runner: runners.Runner

  def __init__(self, agent=None):
    # Prepare A2UI schema validator
    try:
      single_message_schema = json.loads(a2ui_schema.A2UI_SCHEMA)
      self.a2ui_schema_object = {
          "type": "array",
          "items": single_message_schema,
      }
      logger.info("[DEBUG] A2UI_SCHEMA successfully loaded.")
    except Exception as e:
      logger.error("[DEBUG] Failed to parse A2UI_SCHEMA: %s", e)
      self.a2ui_schema_object = None

    self._agent = agent
    if self._agent is None:
        from agent import root_agent
        self._agent = root_agent
        
    self._runner = runners.Runner(
        app_name=self._agent.name,
        agent=self._agent,
        session_service=in_memory_session_service.InMemorySessionService(),
        artifact_service=in_memory_artifact_service.InMemoryArtifactService(),
        memory_service=in_memory_memory_service.InMemoryMemoryService(),
    )
    self._user_id = "remote_agent"

  def _build_webframe(self, data, template_name="dashboard"):
    """Build a WebFrame component from injected data and template."""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', f'{template_name}.html')
    
    if not os.path.exists(template_path):
        logger.warning(f"Template {template_name} not found, falling back to dashboard")
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard.html')

    try:
      with open(template_path, 'r') as f:
        html_template = f.read()
      
      injected_script = f"<script>window.INJECTED_DATA = {json.dumps(data)};</script>"
      html_injected = html_template.replace('</head>', f'{injected_script}\n</head>')
      
      # Dynamically size the viewport frame height based on standalone status
      frame_height = 600
      is_standalone = not data.get('kpis') and not data.get('title') and not data.get('subtitle')
      if is_standalone:
          grid_items = data.get('grid', [])
          if len(grid_items) == 1:
              item_type = grid_items[0].get('type', '')
              if item_type == 'image':
                  frame_height = 400
              elif item_type == 'video':
                  frame_height = 350
              elif item_type in ['d3-network', 'chart', 'map-heatmap', 'table']:
                  frame_height = 320
              else:
                  frame_height = 400

      return [
        {
          "beginRendering": {
            "surfaceId": "canvas-surface",
            "root": "root-card"
          }
        },
        {
          "surfaceUpdate": {
            "surfaceId": "canvas-surface",
            "components": [
              {
                "id": "root-card",
                "component": { "Card": { "child": "frame-container" } }
              },
              {
                "id": "frame-container",
                "component": {
                  "WebFrame": {
                    "htmlContent": { "literalString": html_injected },
                    "height": frame_height
                  }
                }
              }
            ]
          }
        }
      ]
    except Exception as e:
      logger.error(f"Failed to build webframe {template_name}: %s", e)
      return [{
        "surfaceUpdate": {
            "surfaceId": "canvas-surface",
            "components": [{
                "id": "error-card",
                "component": {"Text": {"text": {"literalString": f"Viewport Error: {str(e)}"}}}
            }]
        }
      }]

  async def execute(self, context: agent_execution.RequestContext, event_queue: events.EventQueue) -> None:
    query = context.get_user_input()
    task = context.current_task
    logger.info("[DEBUG] Query: %s", query)

    if not task:
      if not context.message: return
      task = utils.new_task(context.message)
      await event_queue.enqueue_event(task)

    updater = tasks.TaskUpdater(event_queue, task.id, task.context_id)
    session_id = task.context_id

    session = await self._runner.session_service.get_session(
        app_name=self._agent.name, user_id=self._user_id, session_id=session_id
    )
    if session is None:
      session = await self._runner.session_service.create_session(
          app_name=self._agent.name, user_id=self._user_id, state={}, session_id=session_id
      )

    current_query_text = query
    max_retries = 1
    attempt = 0

    await updater.start_work()

    while attempt <= max_retries:
      attempt += 1
      content = genai_types.Content(role="user", parts=[{"text": current_query_text}])
      final_response_content = None

      try:
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
          if event.is_final_response():
            if event.content and event.content.parts and event.content.parts[0].text:
              final_response_content = "\n".join([p.text for p in event.content.parts if p.text])

      except Exception as e:
        await updater.failed(message=utils.new_agent_text_message(f"Task failed: {str(e)}"))
        return

      if final_response_content is None:
        if attempt <= max_retries:
            current_query_text = "I received no response. Please try again."
            continue
        await updater.failed(message=utils.new_agent_text_message("No response generated."))
        return

      is_valid = False
      error_message = ""
      json_string_cleaned = "[]"
      text_part = final_response_content

      if "---a2ui_JSON---" not in final_response_content:
        is_valid = True
        json_string_cleaned = None
      else:
        try:
          import re
          text_part, json_string = final_response_content.split("---a2ui_JSON---", 1)
          logger.info("=== RAW JSON FROM LLM ===")
          logger.info(json_string)
          logger.info("=========================")
          
          match = re.search(r'(?:```(?:json)?\s*)?([\[\{][\s\S]*[\]\}])', json_string.strip())
          if match:
              json_string_cleaned = match.group(1).strip()
          else:
              json_string_cleaned = json_string.strip().lstrip("```json").rstrip("```").strip()

          if not json_string_cleaned: json_string_cleaned = "[]"
          parsed_json = json.loads(json_string_cleaned)
          
          is_custom_view = False
          if isinstance(parsed_json, dict) and "CustomView" in parsed_json:
             is_custom_view = True
          elif isinstance(parsed_json, list):
             for item in parsed_json:
                 if isinstance(item, dict) and "CustomView" in item:
                     is_custom_view = True
                     break

          if self.a2ui_schema_object and not is_custom_view:
            jsonschema.validate(instance=parsed_json, schema=self.a2ui_schema_object)

          is_valid = True
        except Exception as e:
          error_message = f"Validation failed: {str(e)}"

      if is_valid:
        parts = []
        if text_part.strip():
          parts.append(types.Part(root=types.TextPart(text=text_part.strip())))

        if json_string_cleaned:
            json_data = json.loads(json_string_cleaned)
            processed_data = json_data
            
            target_view = None
            if isinstance(json_data, dict) and "CustomView" in json_data:
                target_view = json_data["CustomView"]
            elif isinstance(json_data, list):
                for item in json_data:
                    if isinstance(item, dict) and "CustomView" in item:
                        target_view = item["CustomView"]
                        break
                    elif isinstance(item, dict) and "surfaceUpdate" in item:
                        for component in item["surfaceUpdate"].get("components", []):
                            if "DataGrid" in component.get("component", {}):
                                datagrid_data = component["component"]["DataGrid"]
                                target_view = {
                                    "template": "table",
                                    "data": {
                                        "columns": datagrid_data.get("columns", []),
                                        "rows": datagrid_data.get("rows", [])
                                    }
                                }
                                break
                        if target_view:
                            break

            if target_view:
                logger.info(f"[DEBUG] CustomView intercepted triggering template {target_view.get('template')}")
                
                view_data = target_view.get("data", {})
                if "theme" in target_view:
                    view_data["theme"] = target_view["theme"]
                    
                processed_data = self._build_webframe(
                    view_data, 
                    target_view.get("template", "dashboard")
                )

            logger.info("=== PROCESSED JSON FOR FRONTEND ===")
            logger.info(json.dumps(processed_data, indent=2))
            logger.info("===================================")
            
            if isinstance(processed_data, list):
              new_surface_id = "s-" + str(uuid.uuid4())[:8]
              for message in processed_data:
                if "beginRendering" in message and "surfaceId" in message["beginRendering"]:
                  message["beginRendering"]["surfaceId"] = new_surface_id
                if "surfaceUpdate" in message and "surfaceId" in message["surfaceUpdate"]:
                  message["surfaceUpdate"]["surfaceId"] = new_surface_id

              for message in processed_data:
                parts.append(types.Part(root=types.DataPart(data=message, metadata={"mimeType": "application/json+a2ui"})))
            else:
              parts.append(types.Part(root=types.DataPart(data=processed_data, metadata={"mimeType": "application/json+a2ui"})))

        await updater.add_artifact(parts, name="response")
        await updater.complete()
        return

      else:
        if attempt <= max_retries:
          current_query_text = f"Previous invalid response: {error_message}. Retry request: '{query}'"
          continue
        else:
          await updater.add_artifact([types.Part(root=types.TextPart(text=f"UI Error: {error_message}"))], name="error")
          await updater.complete()
          return

  async def cancel(self, context: agent_execution.RequestContext, event_queue: events.EventQueue) -> None:
    raise a2a_errors.ServerError(error=types.UnsupportedOperationError())
