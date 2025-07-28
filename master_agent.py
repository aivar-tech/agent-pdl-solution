from scoping_agent import ScopingAgent
from hypothesis_agent import HypothesisGenerationAgent
from data_analysis_agent import DataAnalysisAgent
from hypothesis_testing_agent import HypothesisTestingAgent

class MasterAgent:
    """
    MasterAgent: Orchestrates the workflow and delegates to ScopingAgent, HypothesisGenerationAgent, DataAnalysisAgent, and HypothesisTestingAgent
    """
    def __init__(self):
        self.scoping_agent = ScopingAgent()
        self.hypothesis_agent = HypothesisGenerationAgent()
        self.data_analysis_agent = DataAnalysisAgent()
        self.hypothesis_testing_agent = HypothesisTestingAgent()

    def on_pm_input(self, pm_brief, raw_data=None):
        results = self.run_workflow(pm_brief, raw_data)
        print("Received scope document, data analysis, hypotheses, and test results:\n", results)

    def run_workflow(self, pm_brief, raw_data=None):
        # Step 1: Analyze data
        if raw_data:
            data_analysis = self.data_analysis_agent.analyze_data(pm_brief, raw_data)
        else:
            data_analysis = None
        # Step 2: Generate scope document
        scope_doc = self.scoping_agent.generate_scope(pm_brief)
        # Step 3: Generate hypotheses (using data analysis summary)
        hypotheses = self.hypothesis_agent.generate_hypotheses(pm_brief, data_analysis)
        # Step 4: Test hypotheses against data analysis
        test_results = self.hypothesis_testing_agent.test_hypotheses(hypotheses, data_analysis, raw_data)
        
        return {
            "scope_document": scope_doc,
            "data_analysis": data_analysis,
            "hypotheses": hypotheses,
            "hypothesis_test_results": test_results
        }