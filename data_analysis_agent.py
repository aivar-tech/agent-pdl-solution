from utils import call_bedrock_llm

class DataAnalysisAgent:
    """
    Analyzes historical or product data and returns a summary of key findings, trends, and causal insights.
    Call analyze_data() with a description of the product/problem and the raw or summarized data.
    """
    def analyze_data(self, problem_description, raw_data):
        import json
        prompt = f"""Human: You are a Data Analysis Agent. Your job is to analyze historical or product data and extract key findings, trends, anomalies, and possible causal relationships to help product teams make better decisions.

                Product or Problem Description:
                
                {problem_description}
                
                Data Provided:
                
                {raw_data or 'No data provided.'}
                

                You MUST reply with a JSON object conforming to the following JSON schema. Do not include any commentary, markdown, or extra text—ONLY valid JSON.

                JSON Schema (use as reference):
                {{
                "agent": "DataAnalysisAgent",
                "sections": {{
                    "main_trends": ["string", ...],
                    "anomalies": ["string", ...],
                    "causal_factors": ["string", ...],
                    "actionable_insights": ["string", ...]
                }}
                }}

                Section requirements:
                - main_trends: List key trends or patterns in the data.
                - anomalies: List notable anomalies or outliers.
                - causal_factors: List possible causes for observed trends/anomalies.
                - actionable_insights: List concrete recommendations or next steps.

                Reply with ONLY valid JSON matching the schema above.
                Assistant:
                """
        out = call_bedrock_llm(prompt)
        try:
            return json.loads(out)
        except Exception:
            return {"agent": "DataAnalysisAgent", "error": "Invalid JSON from LLM", "raw": out}

        out = call_bedrock_llm(prompt)
        try:
            return json.loads(out)
        except Exception:
            return {"agent": "DataAnalysisAgent", "error": "Invalid JSON from LLM", "raw": out}
