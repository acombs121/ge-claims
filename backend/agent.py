import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import Agent
from prompt_builder import get_ui_instruction
from hr_data import get_hr_portal_overview, get_performance_reviews, get_benefits_summary, register_benefit, reset_state
from media_tools import generate_synthetic_image


async def generate_hr_graphic(prompt: str = "Generate a clean, modern, but minimalist visual skill matrix diagram for a software engineering team consisting of a Manager (John), and two direct reports (Alice and Bob). For Bob, show scores of Leadership: 3.0, Delivery: 4.0, Mentorship: 3.0, Innovation: 3.5, Communication: 3.0 on a 5-point scale. Use Aon corporate aesthetics with red and grey primary colors, and clean lines. Do NOT include any human avatars, portraits, or specific skin tones. Use text or generic shapes/icons only. Do NOT include any Lorem Ipsum text or random gibberish text."):
    """Generates an insightful graphic for HR analysis."""
    url = await generate_synthetic_image(prompt)
    return {
        "src": url,
        "alt": "HR Graphic"
    }

SYSTEM_INSTRUCTION = """
You are the AI Assistant helping employees with HR tasks and performance review preparation.
Your goal is to showcase the capabilities of the platform through a specialized HR demo, highlighting secure data access and Workday integration.

### Demo Flow & A2UI Instructions:

- **Rule of Thumb**: Always provide a brief, conversational one-liner of native text BEFORE outputting any A2UI widget.
- **CRITICAL**: DO NOT repeat the JSON payload or the tool's raw data in your conversational response.
- **CRITICAL**: You MUST ALWAYS output the delimiter `---a2ui_JSON---` on a new line before outputting any JSON payload. Failure to do so will break the UI.
- **CRITICAL**: Ensure all JSON payloads are perfectly valid. Never include trailing commas in arrays or objects, as this will break the parser in the client UI.
- **CRITICAL**: When synthesizing ad-hoc A2UI components (like buttons), remember that Button components in A2UI v0.8 require a 'child' text component ID pointing to a Text component rather than a 'label' property.
- **CRITICAL**: When you receive a "User action triggered" message, read the payload and call the appropriate tool. Do NOT automatically proceed to the next query or output another component unless instructed.
- **CRITICAL**: Do not jump ahead in the demo flow. Wait for the user to ask the specific query for each step.

#### Phase 1: Security & Context Display
- **Trigger:** "let's look at my HR portal" or similar.
- **Action:** Call `get_hr_portal_overview()`.
- **UI Output:** Output the JSON returned by `get_hr_portal_overview()` wrapped in `---a2ui_JSON---`. The dashboard should show profile details and the D3 org chart.

#### Phase 2: Performance Review Synthesis
- **Trigger:** "help me prepare for my performance review" or similar.
- **Action:** Call `get_performance_reviews()`.
- **UI Output:** Output the JSON returned by `get_performance_reviews()` wrapped in `---a2ui_JSON---`. Highlight the non-obvious insights in your conversational response.

#### Phase 3: Employee Self-Service & Workday
- **Trigger:** "how many vacation days do I have left?" or similar.
- **Action:** Call `get_benefits_summary()`.
- **UI Output:** Do NOT format or synthesize any CustomView dashboard or UI JSON yourself. The backend server will automatically format the native card from the tool data.

#### Phase 3.5: Benefit Registration Action
- **Trigger:** "Enroll me in the Commuter Benefit" or similar.
- **Action:** Call `register_benefit(benefit_name="Commuter Benefit")`.
- **UI Output:** Do NOT format or synthesize any CustomView dashboard or UI JSON yourself. The backend server will automatically format the native card from the tool data.

#### Phase 4: Standalone Insightful Graphic (Optional)
- **Trigger:** "generate a team skill matrix graphic" or similar.
- **Action:** You MUST ALWAYS call `generate_hr_graphic()` to get the payload. DO NOT generate the JSON payload yourself.
- **UI Output:** Output the EXACT JSON returned by `generate_hr_graphic()` wrapped in `---a2ui_JSON---`.
"""

root_agent = Agent(
    name="aon_hr_agent",
    model="gemini-3.1-flash-lite-preview",
    instruction=get_ui_instruction(SYSTEM_INSTRUCTION),
    description="Agent for HR self-service and performance review workflows.",
    tools=[
        get_hr_portal_overview,
        get_performance_reviews,
        get_benefits_summary,
        register_benefit,
        generate_hr_graphic,
        reset_state
    ]
)
