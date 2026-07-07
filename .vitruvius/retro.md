# Retro — Gemini Enterprise Insurance Claims Assistant Demo

> Stage 8 artifact. Reflect on the PROCESS, not the product. This is how the methodology compounds across demos.

## Rubric items that never discriminated
- **"Works at 1920x1080 resolution"**: This always passed without effort because A2UI's standard flexbox Row and Column components natively scale across widescreen resolutions. In future demos, replace general resolution checks with specific vertical viewport density rules (e.g., verifying that stacked map widgets and estimation tables do not push critical call-to-action buttons below the visible fold).

## What the pre-mortem missed
- **ADC / OAuth Credential Expiration**: The pre-mortem did not account for Google Cloud Application Default Credentials (ADC) expiring overnight or between development sessions, which caused `google.auth.exceptions.RefreshError` when initializing the Vertex AI client. For all GCP-integrated demos, token expiration and reauthentication runbooks must be treated as a primary pre-mortem risk axis.
- **LLM Tool-Chaining & Manual Formatting Loops**: The pre-mortem missed that when an LLM is equipped with sequential UI rendering tools, it may attempt to manually emit UI delimiters (`---a2ui_JSON---`) or chain multiple tools in a single turn. Adding strict anti-loop rules and delegating JSON rendering entirely to the backend executor solved this.

## Where the harness slowed us for no gain
- Generating individual evaluation artifacts for closely related sequential beats (such as Beats 3 and 5) created administrative overhead when both beats relied on the exact same underlying deterministic dataset and A2UI card generation patterns. Combining eval artifacts for lightweight beats would streamline execution in `lite` mode.

## What the rehearsal caught that phase gates should have
- End-to-end testing revealed that frontend button click payloads (`User action triggered: name=...`) require explicit instructions in the agent's system prompt to prevent the model from immediately executing subsequent tools without waiting for user confirmation. Phase gates should check for anti-loop behavioral constraints whenever conversational agents drive UI state machines.

## Carry-forward
1. **Default Anti-Loop Prompting**: Embed strict anti-loop and anti-manual-JSON instructions into all future agentic UI system prompts from day one.
2. **Credential Validation in Runbook**: Include a mandatory pre-flight token check (`gcloud auth application-default print-access-token`) in the presenter's runbook before walking into executive presentations.
3. **Universal Fallback Doctrine**: Maintain hardcoded, domain-true fallback data for every external API or LLM call (e.g., Vertex AI vision analysis, Google Maps SDK) to guarantee zero-crash live performances.
