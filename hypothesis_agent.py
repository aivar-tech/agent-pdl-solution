from utils import call_bedrock_llm

class HypothesisGenerationAgent:
    """
    Automates hypothesis creation using historical data and causal analysis.
    Call generate_hypotheses() with a description of the product/problem and any relevant data summary.
    """
    def generate_hypotheses(self, problem_description, data_summary=None):
        import json
        data_summary_block = f'Relevant Historical Data or Causal Summary:\n"""\n{data_summary}\n"""' if data_summary else ''

        prompt = f"""Human: You are a Hypothesis Generation Agent. Your job is to help product teams by automatically generating insightful hypotheses based on historical data and causal analysis.

        Product or Problem Description:

        {problem_description}

        {data_summary_block}

        You MUST reply with a JSON object conforming to the following JSON schema. Do not include any commentary, markdown, or extra text—ONLY valid JSON.

        JSON Schema (use as reference):
        {{
          "agent": "HypothesisGenerationAgent",
          "sections": [
            {{
              "hypothesis": "string (the hypothesis itself)",
              "rationale": "string (why this hypothesis makes sense)",
              "test": "string (how to test or validate it)"
            }}
            // ... more hypotheses
          ]
        }}

        Section requirements:
        - Each hypothesis must have a clear rationale and a suggested test or experiment.
        - Provide at least 3 hypotheses.

        Reply with ONLY valid JSON matching the schema above.
        Assistant:
        """
        out = call_bedrock_llm(prompt)
        try:
            return json.loads(out)
        except Exception:
            return {"agent": "HypothesisGenerationAgent", "error": "Invalid JSON from LLM", "raw": out}
