"""Agent executor for ADK agents with dynamic WebFrame template orchestration."""

import json
import logging
import os
import uuid
from a2a import types
from a2a.types import TaskState
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
        
    session_service = in_memory_session_service.InMemorySessionService()

    self._runner = runners.Runner(
        app_name=self._agent.name,
        agent=self._agent,
        session_service=session_service,
        artifact_service=in_memory_artifact_service.InMemoryArtifactService(),
        memory_service=in_memory_memory_service.InMemoryMemoryService(),
    )
    self._user_id = "remote_agent"
    self._cached_ui_payload = None
    self._last_tool_name = None
    self._last_tool_data = None
    self._executed_tool_name = None
    self._executed_tool_data = None

    wrapped_tools = []
    for t in getattr(self._agent, 'tools', []):
        t_name = getattr(t, '__name__', None) or getattr(t, 'name', None) or 'tool'
        wrapped_tools.append(self._wrap_tool(t, t_name))
    self._agent.tools = wrapped_tools

    # Load demo manifest
    manifest_path = os.path.join(os.path.dirname(__file__), 'demo_manifest.json')
    self._manifest = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r') as f:
                self._manifest = json.load(f)
            logger.info("[DEBUG] demo_manifest.json successfully loaded.")
        except Exception as e:
            logger.error("[DEBUG] Failed to parse demo_manifest.json: %s", e)

  def _wrap_tool(self, tool_func, tool_name):
      import inspect
      from functools import wraps
      if inspect.iscoroutinefunction(tool_func):
          @wraps(tool_func)
          async def async_wrapper(*args, **kwargs):
              res = await tool_func(*args, **kwargs)
              self._executed_tool_name = tool_name
              self._executed_tool_data = res
              self._last_tool_name = tool_name
              self._last_tool_data = res
              return res
          return async_wrapper
      else:
          @wraps(tool_func)
          def sync_wrapper(*args, **kwargs):
              res = tool_func(*args, **kwargs)
              self._executed_tool_name = tool_name
              self._executed_tool_data = res
              self._last_tool_name = tool_name
              self._last_tool_data = res
              return res
          return sync_wrapper


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
                  frame_height = 450
              else:
                  frame_height = 400

      return [
        {
          "beginRendering": {
            "surfaceId": "canvas-surface",
            "root": "frame-container"
          }
        },
        {
          "surfaceUpdate": {
            "surfaceId": "canvas-surface",
            "components": [
              {
                "id": "frame-container",
                "component": {
                  "WebFrameSrcdoc": {
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

  def _process_response_content(self, final_response_content: str, cached_ui_payload: list = None) -> tuple:
      """Processes the agent's response and appends any cached A2UI payload."""
      parts = []
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
          text_part = text_part.strip()
          
          match = re.search(r'(?:```(?:json)?\s*)?([\[\{][\s\S]*[\]\}])', json_string.strip())
          if match:
              json_string_cleaned = match.group(1).strip()
          else:
              json_string_cleaned = json_string.strip().lstrip("```json").rstrip("```").strip()

          if not json_string_cleaned: json_string_cleaned = "[]"
          parsed_json = json.loads(json_string_cleaned)
           
          native_keys = ["Button", "Card", "Text", "Column", "Row", "List", "Tabs", "Modal", "AudioPlayer", "Divider", "Icon", "Image", "Video"]
           
          def normalize_ast(obj, c_list=None):
              if isinstance(obj, dict):
                  if "Text" in obj and isinstance(obj["Text"], dict):
                      t_node = obj["Text"]
                      if "text" not in t_node and "literalString" in t_node:
                          t_node["text"] = {"literalString": t_node.pop("literalString")}
                  if "Button" in obj and isinstance(obj["Button"], dict):
                      b_node = obj["Button"]
                      if "action" not in b_node:
                          b_node["action"] = {"name": "button_clicked", "context": []}
                      if "child" not in b_node and "label" in b_node and c_list is not None:
                          lbl = b_node.pop("label")
                          l_str = lbl.get("literalString", "Button") if isinstance(lbl, dict) else str(lbl)
                          b_node["child"] = "btn_child_txt"
                          c_list.append({"id": "btn_child_txt", "component": {"Text": {"text": {"literalString": l_str}, "usageHint": "body"}}})
                  if any(k in obj for k in ["Select", "Dropdown", "DropdownMenu"]):
                      sel = obj.pop("Select", None) or obj.pop("Dropdown", None) or obj.pop("DropdownMenu", None)
                      opts = sel.get("options", ["Option A", "Option B"]) if isinstance(sel, dict) else ["Option A", "Option B"]
                      if isinstance(opts, dict) and "explicitList" in opts: opts = opts["explicitList"]
                      child_ids = []
                      if c_list is not None and isinstance(opts, list):
                          for idx, opt in enumerate(opts):
                              opt_str = opt.get("literalString", f"Option {idx+1}") if isinstance(opt, dict) else str(opt)
                              b_id = f"sel_btn_{idx}"
                              t_id = f"sel_txt_{idx}"
                              child_ids.append(b_id)
                              c_list.append({"id": b_id, "component": {"Button": {"child": t_id, "action": {"name": "select_option", "context": [{"id": f"opt_{idx}"}]}}}})
                              c_list.append({"id": t_id, "component": {"Text": {"text": {"literalString": opt_str}, "usageHint": "body"}}})
                      obj["Column"] = {"children": {"explicitList": child_ids}}
                  for v in list(obj.values()):
                      if isinstance(v, (dict, list)): normalize_ast(v, c_list)
              elif isinstance(obj, list):
                  for item in obj:
                      if isinstance(item, dict) and "surfaceUpdate" in item and isinstance(item["surfaceUpdate"], dict):
                          comps = item["surfaceUpdate"].get("components", [])
                          if isinstance(comps, list):
                              for c in comps: normalize_ast(c, comps)
                      else:
                          if isinstance(item, (dict, list)): normalize_ast(item, c_list)

          if isinstance(parsed_json, dict) and "component" in parsed_json and isinstance(parsed_json["component"], dict):
              parsed_json = parsed_json["component"]

          if isinstance(parsed_json, dict) and any(k in parsed_json for k in native_keys) and not any(k in parsed_json for k in ["beginRendering", "surfaceUpdate"]):
              matched_k = next(k for k in native_keys if k in parsed_json)
              comp_id = f"auto_root_{matched_k.lower()}"
              comp_wrapper = {"id": comp_id, "component": parsed_json}
              comps_list = [comp_wrapper]
              normalize_ast(comp_wrapper, comps_list)
              parsed_json = [
                  {"beginRendering": {"surfaceId": "canvas-surface", "root": comp_id}},
                  {"surfaceUpdate": {"surfaceId": "canvas-surface", "components": comps_list}}
              ]
          else:
              comps_list = []
              normalize_ast(parsed_json, comps_list)

          # Cache normalized JSON back to clean string for execution stage
          json_string_cleaned = json.dumps(parsed_json)
           
          def has_custom_view(obj):
              if isinstance(obj, dict):
                  if "CustomView" in obj:
                      return True
                  return any(has_custom_view(v) for v in obj.values())
              elif isinstance(obj, list):
                  return any(has_custom_view(item) for item in obj)
              return False

          is_custom_view = has_custom_view(parsed_json)

          if self.a2ui_schema_object and not is_custom_view and not cached_ui_payload:
              if isinstance(parsed_json, list):
                  import jsonschema
                  jsonschema.validate(instance=parsed_json, schema=self.a2ui_schema_object)

          is_valid = True
        except Exception as e:
          error_message = f"Validation failed: {str(e)}"
          logger.error(error_message)

      if is_valid:
        if text_part.strip():
          parts.append(types.Part(root=types.TextPart(text=text_part.strip())))

        processed_data = None
        active_tool = getattr(self, '_executed_tool_name', None)
        if active_tool == 'tool': active_tool = None
        active_data = getattr(self, '_executed_tool_data', None)
        
        json_data = None
        if json_string_cleaned:
            try: json_data = json.loads(json_string_cleaned)
            except: pass
            
        def find_custom_view(obj):
            if isinstance(obj, dict):
                if "CustomView" in obj: return obj["CustomView"]
                for v in obj.values():
                    res = find_custom_view(v)
                    if res: return res
            elif isinstance(obj, list):
                for item in obj:
                    res = find_custom_view(item)
                    if res: return res
            return None
            
        llm_explicit_ui = None
        if json_data:
            if active_data is None and isinstance(json_data, dict):
                active_data = json_data
                if not active_tool: active_tool = json_data.get("_source_tool")
                
            target_view = find_custom_view(json_data)
            if target_view:
                view_data = target_view.get("data", {})
                if "theme" in target_view: view_data["theme"] = target_view["theme"]
                llm_explicit_ui = self._build_webframe(view_data, target_view.get("template", "dashboard"))
            elif isinstance(json_data, (list, dict)):
                llm_explicit_ui = json_data
                
        manifest_handled = False
        if active_tool:
            steps = self._manifest.get("steps", [])
            tool_cfg = next((s for s in steps if s.get("action_tool") == active_tool), None)
            if tool_cfg:
                output_mode = tool_cfg.get("output_mode")
                if output_mode == "iframe":
                    template = tool_cfg.get("template", "dashboard")
                    injected_payload = active_data or json_data
                    if isinstance(injected_payload, dict):
                        if "theme" in tool_cfg: injected_payload["theme"] = tool_cfg["theme"]
                        if "config" in tool_cfg: injected_payload["config"] = tool_cfg["config"]
                    processed_data = self._build_webframe(injected_payload, template)
                    manifest_handled = True
                elif output_mode == "url":
                    url_str = tool_cfg.get("url") or (isinstance(active_data, dict) and active_data.get("url")) or str(active_data)
                    import component_library as cl
                    processed_data = [
                        cl.begin_rendering(surface_id="canvas-surface", root="root-url"),
                        cl.surface_update(surface_id="canvas-surface", components=[cl.web_frame_url(element_id="root-url", url=url_str)])
                    ]
                    manifest_handled = True
                elif output_mode == "native":
                    mapper_name = tool_cfg.get("native_mapper")
                    import component_mappers as cm
                    mapper_func = getattr(cm, mapper_name, None)
                    if mapper_func:
                        processed_data = mapper_func(active_data or json_data)
                        manifest_handled = True
                        
        # 2. Second Priority: If manifest didn't handle it, check if active_data is a tool-generated UI tree or llm_explicit_ui is present
        if not manifest_handled:
            ui_payload = active_data if isinstance(active_data, (list, dict)) and any(k in str(active_data) for k in ["beginRendering", "surfaceUpdate"]) else llm_explicit_ui
            if ui_payload:
                processed_data = ui_payload
                manifest_handled = True

        # Intercepted Payload Handling (Merged)
        if cached_ui_payload:
            processed_data = cached_ui_payload

        if processed_data:
            if isinstance(processed_data, list):
              for message in processed_data:
                parts.append(types.Part(root=types.DataPart(data=message, metadata={"mimeType": "application/json+a2ui"})))
            else:
              parts.append(types.Part(root=types.DataPart(data=processed_data, metadata={"mimeType": "application/json+a2ui"})))

        return parts, True
      else:
        return [], False

  async def _handle_intercepted_action(self, query: str) -> list:
      """Intercepts specific user actions and handles them deterministically."""
      steps = self._manifest.get("steps", [])
      import re
      for step in steps:
          triggers = step.get("trigger_queries", [])
          for trigger in triggers:
              clean_q = query.lower().replace('?', '').replace('.', '').replace('!', '').strip()
              clean_t = trigger.lower().replace('?', '').replace('.', '').replace('!', '').strip()
              
              match = clean_t in clean_q
              if not match:
                  stop_words = {'how', 'many', 'have', 'the', 'for', 'let', 'look', 'show', 'give', 'and', 'with'}
                  t_words = set([w.rstrip('s') for w in re.findall(r'\w+', clean_t) if len(w) > 2 and w not in stop_words])
                  q_words = set([w.rstrip('s') for w in re.findall(r'\w+', clean_q) if len(w) > 2 and w not in stop_words])
                  if t_words and len(q_words.intersection(t_words)) >= len(t_words) - 1 and len(q_words.intersection(t_words)) >= 1:
                      match = True
                      
              if match:
                  logger.info(f"[DEBUG] Intercepted query '{query}' matching trigger '{trigger}'")
                  action_tool = step.get("action_tool")
                  output_template = step.get("output_template")
                  
                  tool_func = None
                  for t in self._agent.tools:
                      name = getattr(t, '__name__', None) or getattr(t, 'name', None)
                      if name == action_tool:
                          tool_func = t
                          break
                          
                  if tool_func:
                      try:
                          import inspect
                          if inspect.iscoroutinefunction(tool_func):
                              result = await tool_func()
                          else:
                              result = tool_func()
                              
                          output_mode = step.get("output_mode")
                          processed_data = None
                          
                          if output_mode == "iframe":
                              template = step.get("template", "dashboard")
                              processed_data = self._build_webframe(result, template)
                          elif output_mode == "url":
                              url_str = step.get("url") or (isinstance(result, dict) and result.get("url")) or str(result)
                              import component_library as cl
                              processed_data = [
                                  cl.begin_rendering(surface_id="canvas-surface", root="root-url"),
                                  cl.surface_update(surface_id="canvas-surface", components=[
                                      cl.web_frame_url(element_id="root-url", url=url_str)
                                  ])
                              ]
                          elif output_mode == "native":
                              mapper_name = step.get("native_mapper")
                              import component_mappers
                              mapper_func = getattr(component_mappers, mapper_name, None)
                              if mapper_func:
                                  processed_data = mapper_func(result)
                                  
                          if processed_data:
                              parts = []
                              parts.append(types.Part(root=types.TextPart(text=f"Here is the {action_tool.replace('_', ' ')}.")))
                              
                              if isinstance(processed_data, list):
                                  for message in processed_data:
                                      parts.append(types.Part(root=types.DataPart(data=message, metadata={"mimeType": "application/json+a2ui"})))
                              else:
                                  parts.append(types.Part(root=types.DataPart(data=processed_data, metadata={"mimeType": "application/json+a2ui"})))
                                  
                              return parts
                              
                      except Exception as e:
                          logger.error(f"Failed to execute tool {action_tool}: {e}")
                          return None
      return None

  async def execute(self, context: agent_execution.RequestContext, event_queue: events.EventQueue) -> None:
    query = context.get_user_input()
    task = context.current_task
    logger.info("[DEBUG] Query: %s", query)

    if not task:
      if not context.message: return
      task = utils.new_task(context.message)
      await event_queue.enqueue_event(task)

    try:
        if context.message and hasattr(context.message, 'parts'):
            logger.warning(f"A2UI-ROOT CONTEXT DEBUG | dir(context): {dir(context)}")
            if hasattr(context, '__dict__'):
                logger.warning(f"A2UI-ROOT CONTEXT DEBUG | vars(context): {str(vars(context))[:1000]}")
            
            import base64
            for i, part in enumerate(context.message.parts):
                logger.warning(f"A2UI-MEDIA SCHEMA DEBUG | part obj: {part}")
                logger.warning(f"A2UI-MEDIA SCHEMA DEBUG | dir(part): {dir(part)}")
                try:
                    raw_b64 = None
                    if hasattr(part, 'root') and hasattr(part.root, 'file') and hasattr(part.root.file, 'bytes'):
                        raw_b64 = part.root.file.bytes
                    elif hasattr(part, 'file') and hasattr(part.file, 'bytes'):
                        raw_b64 = part.file.bytes
                        
                    if raw_b64:
                        logger.warning(f"A2UI-MEDIA-INTERCEPT | Safely extracted native base64 footprint structurally across boundary.")
                        
                        try:
                            from google.cloud import storage
                            storage_client = storage.Client(project="sandbox-426014")
                            bucket_name = "sandbox-426014-a2ui-media-cache"
                            bucket = storage_client.bucket(bucket_name)
                            
                            blob = bucket.blob("a2ui_latest_vision_bytes.bin")
                            
                            # Upload to memory-safe, globally accessible GCS storage
                            import base64
                            blob.upload_from_string(base64.b64decode(raw_b64), content_type="application/octet-stream")
                            logger.warning(f"A2UI-MEDIA-INTERCEPT | Safely pushed binary payload to globally available GCS uri: gs://{bucket_name}/a2ui_latest_vision_bytes.bin")
                        except Exception as storage_err:
                            logger.error(f"A2UI-MEDIA-INTERCEPT | Critical failure caching media to GCS: {storage_err}")
                            
                except Exception as e:
                    logger.error(f"A2UI-MEDIA-INTERCEPT | Error caching media binary: {e}")
    except Exception as e:
        logger.error(f"A2UI-MEDIA-INTERCEPT | Error mapping parts: {e}") 
        
    updater = tasks.TaskUpdater(event_queue, task.id, task.context_id)
    session_id = task.context_id
    self._current_query = query
    
    self._last_tool_name = None
    self._last_tool_data = None
    self._executed_tool_name = None
    self._executed_tool_data = None
    
    # Intercept Action Check
    intercepted_parts = await self._handle_intercepted_action(query)
    if intercepted_parts:
        await updater.start_work()
        await updater.add_artifact(intercepted_parts, name="response")
        await updater.complete()
        return

    session = await self._runner.session_service.get_session(
        app_name=self._agent.name, user_id=self._user_id, session_id=session_id
    )
    if session is None:
      session = await self._runner.session_service.create_session(
          app_name=self._agent.name, user_id=self._user_id, state={}, session_id=session_id
      )

    current_query_text = query
    if context.message and hasattr(context.message, 'parts'):
        for part in context.message.parts:
            if hasattr(part, 'root') and hasattr(part.root, 'data') and isinstance(part.root.data, dict) and "userAction" in part.root.data:
                action_data = part.root.data["userAction"]
                ui_context = action_data.get("context", {})
                action_name = action_data.get("name", "")
                # Ensure lists are unwrapped to strings for the LLM to avoid confusion
                clean_context = {k: (v[0] if isinstance(v, list) and v else v) for k, v in ui_context.items()}
                current_query_text = f"User action triggered: name={action_name}, context={json.dumps(clean_context)}"
                logger.info(f"A2UI-INJECT | Updated query text with UI event context: {current_query_text}")
    max_retries = 3
    attempt = 0

    await updater.start_work()
    
    # 1. Send an initial thought to prevent the default query echo.
    await updater.update_status(
        TaskState.working,
        utils.new_agent_text_message(f"Processing query: '{current_query_text}'"),
        metadata={"thinking_details": {"steps": [{"type": "thought", "content": f"Processing query: '{current_query_text}'"}]}}
    )

    while attempt <= max_retries:
      attempt += 1
      content = genai_types.Content(role="user", parts=[{"text": current_query_text}])
      final_response_content = None

      try:
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
          evt_str = str(event)
          if not (hasattr(event, 'is_thought') and event.is_thought()):
              logger.info(f"[STREAM EVENT] dir={dir(event)} str={evt_str[:250]}")
          for step in self._manifest.get("steps", []):
              t_name = step.get("action_tool")
              if t_name and (f"'{t_name}'" in evt_str or f'"{t_name}"' in evt_str or f"name={t_name}" in evt_str or f"tool_name={t_name}" in evt_str or f"function={t_name}" in evt_str):
                  self._last_tool_name = t_name

          # 2. Handle granular thinking updates
          thinking_steps = []
          
          if hasattr(event, 'is_thought') and event.is_thought():
              thought_text = getattr(event, 'thought', 'Thinking...')
              thinking_steps.append({"type": "thought", "content": thought_text})
          elif hasattr(event, 'is_tool_call') and event.is_tool_call():
              tool_call = getattr(event, 'tool_call', None)
              if not tool_call:
                  t_calls = getattr(event, 'tool_calls', None) or getattr(event, 'function_calls', None)
                  if t_calls and isinstance(t_calls, list) and len(t_calls) > 0:
                      tool_call = t_calls[0]
              tool_name = getattr(tool_call, 'tool_name', None) or getattr(tool_call, 'name', None) or getattr(tool_call, 'function_name', None)
              if not tool_name and isinstance(tool_call, dict):
                  tool_name = tool_call.get('name') or tool_call.get('tool_name') or tool_call.get('function_name')
              if not tool_name:
                  tool_name = getattr(event, 'tool_name', None) or getattr(event, 'name', None) or 'tool'
              self._last_tool_name = tool_name
              args = getattr(tool_call, 'args', {}) if tool_call else {}
              thinking_steps.append({
                  "type": "tool_call",
                  "content": {"name": tool_name, "args": args}
              })
          elif hasattr(event, 'is_tool_result') and event.is_tool_result():
              tool_result = getattr(event, 'tool_result', 'Result received')
              current_tool_name = getattr(event, 'tool_name', None) or getattr(event, 'name', None) or self._last_tool_name
              self._last_tool_name = current_tool_name
              if self._last_tool_name and isinstance(tool_result, dict):
                  tool_result["_source_tool"] = self._last_tool_name
              
              if self._last_tool_name:
                  steps = self._manifest.get("steps", [])
                  tool_cfg = next((s for s in steps if s.get("action_tool") == self._last_tool_name), None)
                  
                  if tool_cfg:
                      output_mode = tool_cfg.get("output_mode")
                      
                      if output_mode == "iframe":
                          template = tool_cfg.get("template", "dashboard")
                          processed_data = self._build_webframe(tool_result, template)
                          self._cached_ui_payload = processed_data
                          logger.info(f"[DEBUG] Intercepted tool result for {self._last_tool_name}, mapped to iframe with template {template}")
                          
                      elif output_mode == "url":
                          url_str = tool_cfg.get("url") or (isinstance(tool_result, dict) and tool_result.get("url")) or str(tool_result)
                          import component_library as cl
                          processed_data = [
                              cl.begin_rendering(surface_id="canvas-surface", root="root-url"),
                              cl.surface_update(surface_id="canvas-surface", components=[
                                  cl.web_frame_url(element_id="root-url", url=url_str)
                              ])
                          ]
                          self._cached_ui_payload = processed_data
                          logger.info(f"[DEBUG] Intercepted tool result for {self._last_tool_name}, mapped to url: {url_str}")
                          
                      elif output_mode == "native":
                          mapper_name = tool_cfg.get("native_mapper")
                          import component_mappers
                          mapper_func = getattr(component_mappers, mapper_name, None)
                          if mapper_func:
                              processed_data = mapper_func(tool_result)
                              self._cached_ui_payload = processed_data
                              logger.info(f"[DEBUG] Intercepted tool result for {self._last_tool_name}, mapped to native via {mapper_name}")
                          else:
                              logger.warning(f"[DEBUG] Mapper {mapper_name} not found in component_mappers")
                      
              result_text = str(tool_result)
              thinking_steps.append({"type": "tool_observation", "content": result_text})
          
          # Always check for final response as well
          if event.is_final_response():
            if event.content and event.content.parts and event.content.parts[0].text:
              final_response_content = "\n".join([p.text for p in event.content.parts if p.text])
            final_step = {"type": "thought", "content": "Formatting final UI components."}
            if final_step not in thinking_steps:
                thinking_steps.append(final_step)

          if thinking_steps:
              step_msg = "Agent is thinking..."
              for step in thinking_steps:
                  if step["type"] == "tool_call":
                      args_str = ", ".join(f"{k}={v}" for k, v in step["content"]["args"].items())
                      step_msg = f"Executing tool: {step['content']['name']}({args_str})"
                      break
                  elif step["type"] == "thought":
                      step_msg = f"Reasoning: {step['content']}"
                      break
              await updater.update_status(
                  TaskState.working,
                  utils.new_agent_text_message(step_msg),
                  metadata={"thinking_details": {"steps": thinking_steps}}
              )

      except Exception as e:
        if attempt <= max_retries:
            logger.warning(f"A2UI-EXC | Caught inference exception: {e}. Retrying {attempt}/{max_retries}...")
            import asyncio
            await asyncio.sleep(2 ** attempt)
            continue
        await updater.failed(message=utils.new_agent_text_message(f"Task failed after {max_retries} retries: {str(e)}"))
        return

      if final_response_content is None:
        if attempt <= max_retries:
            current_query_text = "I received no response. Please try again."
            continue
        await updater.failed(message=utils.new_agent_text_message("No response generated."))
        return

      parts, success = self._process_response_content(final_response_content, self._cached_ui_payload)
      
      if success:
        await updater.add_artifact(parts, name="response")
        await updater.complete()
        # Clear cache for next execution
        self._cached_ui_payload = None
        return
      else:
        error_message = "Validation failed or malformed JSON"
        if attempt <= max_retries:
          current_query_text = f"Previous invalid response: {error_message}. Retry request: '{query}'"
          continue
        else:
          await updater.add_artifact([types.Part(root=types.TextPart(text=f"UI Error: {error_message}"))], name="error")
          await updater.complete()
          self._cached_ui_payload = None
          return

  async def cancel(self, context: agent_execution.RequestContext, event_queue: events.EventQueue) -> None:
    raise a2a_errors.ServerError(error=types.UnsupportedOperationError())
