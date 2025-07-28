from utils import call_bedrock_llm
from datetime import datetime
class ScopingAgent:
    def generate_scope(self, pm_brief):
        import json
        prompt = f"""Human: You are a product scoping assistant. Given this minimal PM input:
                    {pm_brief}
                    todays date is {datetime.now().strftime("%Y-%m-%d")}, use this to calculate target dates for milestones.
                    Generate a comprehensive scope document in STRICT JSON format. You MUST reply with a JSON object conforming to the following JSON schema. Do not include any commentary, markdown, or extra text—ONLY valid JSON.

                    JSON Schema (use as reference):
                    {{
                    "agent": "ScopingAgent",
                    "sections": {{
                        "problem_statement": "string (detailed, 3-5 sentences)",
                        "goals_and_success_metrics": [
                        {{ "goal": "string", "success_metric": "string" }}
                        ],
                        "user_stories": [
                        {{ "role": "string", "story": "string" }}
                        ],
                        "constraints": ["string", ...],
                        "milestones": [
                        {{ "milestone": "string", "target_date": "string (month/year or Qx YYYY)" }}
                        ],
                    }}
                    }}

                    Section requirements:
                    - problem_statement: What is the core problem and context?
                    - goals_and_success_metrics: List of goals with a measurable success metric for each.
                    - user_stories: List of user stories, each with a role and story.
                    - constraints: List of key constraints (technical, regulatory, etc).
                    - milestones: List of major milestones and target dates.
                    Reply with ONLY valid JSON matching the schema above.
                    Assistant:
                    """
        out = call_bedrock_llm(prompt)
        try:
            return json.loads(out)
        except Exception:
            return {"agent": "ScopingAgent", "error": "Invalid JSON from LLM", "raw": out}