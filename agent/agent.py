from bedrock_agentcore.agent import Agent, agent_app, on_message
from utils import call_bedrock_llm

class ScopingAgent(Agent):
    @on_message()
    async def handle_pm_input(self, message):
        pm_brief = message.payload['brief']
        scope_doc = self.generate_scope(pm_brief)
        await self.send("scope_document", {"scope": scope_doc}, to=message.sender)

    def generate_scope(self, pm_brief):
        prompt = (
            "You are a product scoping assistant. Given this minimal PM input:\n"
            f"'{pm_brief}'\n"
            "Generate a comprehensive scope document including:\n"
            "- Problem Statement\n"
            "- Goals and Success Metrics\n"
            "- User Stories\n"
            "- Constraints\n"
            "- Milestones\n"
        )
        return call_bedrock_llm(prompt)

# Register the agent instance with the FastAPI app
agent_app.register_agent(ScopingAgent(name="scoping-agent"))
