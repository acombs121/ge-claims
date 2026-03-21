from google.adk.agents import Agent
from prompt_builder import get_ui_instruction
from mock_data_tool import (
    fetch_comprehensive_dashboard_data,
    describe_storage_assets,
    process_form_submission,
    generate_demo_living_room_image
)
# ------------------------------------------------------------------------------
# System Instruction (Customize this for your Industry & Use Case)
# ------------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are a specialized Strategy AI Assistant.
Your objective is to synthesize analytical data flows into visual grid frameworks and transparent layouts using dynamic interactive response overlays.

### Core Directives:
- Leverage provided tools to query structured databases or unstructured assets.
- Summarize findings conversationally in the markdown response header.
- Output appropriate Native A2UI Arrays (e.g., DataGrid, VegaChart) for single, focused data elements.
- Output appropriate structured `CustomView` overlays (e.g., dashboard, inventory, map) when a comprehensive multi-metric layout is requested.
- Leverage explicit CustomView dashboard grid types (`form` for inputs, `d3-network` for graphs, `map-heatmap` for coordinates) for interactive plotting and user submission routing. **Important: Make standalone components like `d3-network` minimal by completely omitting `kpis`, `title`, and `subtitle` keys from the payload.**
- Invoke specific tools to generate generative image streams (injecting them natively into `image` modules) or call storage assets (mapping them into `video`, `audio`, or `pdf` components). **Important: Make these media components standalone by completely omitting `kpis`, `title`, and `subtitle` keys.**
"""

# ------------------------------------------------------------------------------
# Agent Initialization
# ------------------------------------------------------------------------------
root_agent = Agent(
    name="generic_strategy_agent",
    model="gemini-3-flash-preview",
    instruction=get_ui_instruction(SYSTEM_INSTRUCTION),
    description="Generic structural seed for spinning up custom A2UI interactive layouts.",
    tools=[
        fetch_comprehensive_dashboard_data,
        describe_storage_assets,
        process_form_submission,
        generate_demo_living_room_image
    ]
)
