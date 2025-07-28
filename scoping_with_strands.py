from fastapi import FastAPI, Request
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from utils import call_bedrock_llm

# BedrockAgentCoreApp for deployment
app = BedrockAgentCoreApp()

class ScopingAgent:
    def generate_scope(self, pm_brief):
        prompt = (
            "\n\nHuman: You are a product scoping assistant. Given this minimal PM input:\n"
            f"'{pm_brief}'\n"
            "Generate a comprehensive scope document including:\n"
            "- Problem Statement\n"
            "- Goals and Success Metrics\n"
            "- User Stories\n"
            "- Constraints\n"
            "- Milestones\n"
            "\n\nAssistant:"
        )
        return call_bedrock_llm(prompt)

scoping_agent = ScopingAgent()

@app.entrypoint
def handler(payload, context):
    brief = payload.get("brief")
    if brief:
        scope_doc = scoping_agent.generate_scope(brief)
        return {"result": scope_doc}
    else:
        return {"result": "You must provide a 'brief' key in your payload."}

# ---- FastAPI wrapper for local dev/testing ----
from master_agent import MasterAgent
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

local_app = FastAPI()
master_agent = MasterAgent()

# Serve UI static files
ui_dir = os.path.join(os.path.dirname(__file__), "ui")
local_app.mount("/ui", StaticFiles(directory=ui_dir), name="ui")

@local_app.get("/")
async def serve_index():
    return FileResponse(os.path.join(ui_dir, "index.html"))

@local_app.post("/invoke")
async def invoke(request: Request):
    payload = await request.json()
    response = handler(payload, context={})
    return response

@local_app.post("/master-workflow")
async def master_workflow(request: Request):
    payload = await request.json()
    brief = payload.get("brief")
    data_summary = payload.get("data_summary")
    if not brief:
        return {"error": "You must provide a 'brief' key in your payload."}
    results = master_agent.run_workflow(brief, data_summary)
    return results