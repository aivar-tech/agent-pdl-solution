import boto3
import json
import os

def call_bedrock_llm(prompt, model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"):
    """
    Calls an Amazon Bedrock LLM model. Uses the Messages API for Claude 3.5+ models, and invoke_model for legacy models.
    Returns the main answer text.
    """
    import boto3
    import json

    # Set up the client (add bearer token or other credentials as needed)
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

    # Claude 3.5+ (Sonnet, Haiku, Opus) require the Messages API (converse)
    if "claude-3-5" in model_id or "claude-3" in model_id:
        # Claude 3.5/3 models expect messages, not a prompt string
        messages = [
            {"role": "user", "content": [{"text": prompt}]}
        ]
        response = client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={
                "temperature": 0.7,
            },
        )
        # Parse the output for the main answer
        try:
            return response["output"]["message"]["content"][0]["text"]
        except Exception:
            return str(response)
    else:
        # Legacy Claude models (v1, v2) and others use invoke_model
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 1024,
                "temperature": 0.7,
            })
        )
        result = response["body"]
        if hasattr(result, "read"):
            result = result.read().decode("utf-8")
        try:
            result_json = json.loads(result)
            return result_json.get("completion") or result_json.get("output") or result_json
        except Exception:
            return result