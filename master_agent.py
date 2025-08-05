from scoping_agent import ScopingAgent
from hypothesis_agent import HypothesisGenerationAgent
from data_analysis_agent import DataAnalysisAgent
from hypothesis_testing_agent import HypothesisTestingAgent
import os
from pathlib import Path

class MasterAgent:
    """
    MasterAgent: Orchestrates the workflow and delegates to ScopingAgent, HypothesisGenerationAgent, DataAnalysisAgent, and HypothesisTestingAgent
    """
    def __init__(self):
        self.scoping_agent = ScopingAgent()
        self.hypothesis_agent = HypothesisGenerationAgent()
        self.data_analysis_agent = DataAnalysisAgent()
        self.hypothesis_testing_agent = HypothesisTestingAgent()

    def on_pm_input(self, pm_brief, raw_data=None, document_path=None):
        results = self.run_workflow(pm_brief, raw_data, document_path)
        print("Received scope document, data analysis, hypotheses, and test results:\n", results)

    def run_workflow(self, pm_brief, raw_data=None, document_path=None):
        # Step 1: Analyze data
        data_analysis = None
        document_content = None
        
        # Process document if provided
        if document_path and os.path.exists(document_path):
            document_content = self.extract_document_content(document_path)
            if document_content:
                # If we have document content, add it to raw_data or use it as raw_data
                if raw_data:
                    raw_data = f"{raw_data}\n\n--- DOCUMENT CONTENT ---\n{document_content}"
                else:
                    raw_data = document_content
        
        # Analyze data if available
        if raw_data:
            data_analysis = self.data_analysis_agent.analyze_data(pm_brief, raw_data)
        # Step 2: Generate scope document
        scope_doc = self.scoping_agent.generate_scope(pm_brief)
        # Step 3: Generate hypotheses (using data analysis summary)
        hypotheses = self.hypothesis_agent.generate_hypotheses(pm_brief, data_analysis)
        # Step 4: Test hypotheses against data analysis
        test_results = self.hypothesis_testing_agent.test_hypotheses(hypotheses, data_analysis, raw_data)
        
        results = {
            "scope_document": scope_doc,
            "data_analysis": data_analysis,
            "hypotheses": hypotheses,
            "hypothesis_test_results": test_results
        }
        
        # Add document info if a document was provided
        if document_path:
            results["document_path"] = document_path
            results["document_name"] = Path(document_path).name
            
        return results
        
    def extract_document_content(self, document_path):
        """Extract text content from uploaded documents"""
        try:
            file_ext = Path(document_path).suffix.lower()
            
            # Handle different file types
            if file_ext == '.txt':
                # Simple text file
                with open(document_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
            elif file_ext in ['.pdf']:
                # PDF file - basic extraction
                try:
                    import PyPDF2
                    with open(document_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        text = ''
                        for page_num in range(len(pdf_reader.pages)):
                            text += pdf_reader.pages[page_num].extract_text() + '\n'
                        return text
                except ImportError:
                    return f"[PDF content from {Path(document_path).name} - PDF extraction requires PyPDF2 library]"
                    
            elif file_ext in ['.doc', '.docx']:
                # Word document
                try:
                    import docx
                    doc = docx.Document(document_path)
                    return '\n'.join([para.text for para in doc.paragraphs])
                except ImportError:
                    return f"[Word document content from {Path(document_path).name} - Word extraction requires python-docx library]"
            else:
                return f"[Document content from {Path(document_path).name} - Unsupported file format: {file_ext}]"
                
        except Exception as e:
            print(f"Error extracting document content: {e}")
            return f"[Error extracting content from {Path(document_path).name}: {str(e)}]"