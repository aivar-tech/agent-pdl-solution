from utils import call_bedrock_llm
import json

class HypothesisTestingAgent:
    """
    HypothesisTestingAgent: Tests hypotheses against data and provides analysis results
    """
    def __init__(self):
        pass
        
    def determine_required_data(self, hypothesis):
        """
        First API call to determine what data is required for testing the hypothesis
        
        Args:
            hypothesis (str): The hypothesis to analyze
            
        Returns:
            dict: Data requirements and structure needed for testing the hypothesis
        """
        prompt = f"""
        You are a data requirements analyst for a gametech platform. For the following hypothesis, 
        determine what specific data would be needed to properly test it:
        
        HYPOTHESIS: {hypothesis}
        
        Provide a detailed specification of the data requirements:
        1. List all metrics, indicators, and data points that would be relevant
        2. Specify the data structure and format needed (time series, categorical, etc.)
        3. Identify minimum sample sizes or time periods required
        4. Note what types of patterns or trends would support or contradict this hypothesis
        5. Specify any segmentation of data that would be valuable (user types, game categories, etc.)
        
        Format your response as a structured JSON object with the following format:
        {{
          "data_requirements": [list of required metrics/data points], 
          "data_structure": {{detailed structure specification}}, 
          "sample_size": {{minimum requirements}},
          "key_indicators": {{what would indicate support or contradiction}}
        }}
        
        Do not include any explanations outside the JSON structure.
        """
        
        # Call Bedrock to determine data requirements
        requirements_str = call_bedrock_llm(prompt)
        
        # Parse the JSON response
        try:
            # Extract JSON if it's wrapped in markdown code blocks
            if "```json" in requirements_str:
                requirements_str = requirements_str.split("```json")[1].split("```")[0].strip()
            elif "```" in requirements_str:
                requirements_str = requirements_str.split("```")[1].split("```")[0].strip()
                
            requirements = json.loads(requirements_str)
            return requirements
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw string
            return {"error": "Failed to parse data requirements", "raw_data": requirements_str}
    
    def generate_sample_data(self, hypothesis):
        """
        Generate sample data for a specific hypothesis using Bedrock in two steps:
        1. Determine what data is required
        2. Generate the actual data based on those requirements
        
        Args:
            hypothesis (str): The hypothesis to generate sample data for
            
        Returns:
            dict: Sample data relevant to the hypothesis
        """
        # First API call: Determine what data is required
        data_requirements = self.determine_required_data(hypothesis)
        
        # Second API call: Generate the actual data based on requirements
        prompt = f"""
        You are a data generation expert for a gametech platform. Generate realistic sample data that would be relevant 
        for testing the following hypothesis:
        
        HYPOTHESIS: {hypothesis}
        
        DATA REQUIREMENTS:
        {json.dumps(data_requirements, indent=2)}
        
        Based on these specific requirements, create a comprehensive relevant dataset with the following characteristics:
        1. Include all the metrics and indicators specified in the requirements
        2. Follow the data structure outlined in the requirements
        3. Generate at least 20 data points that would be useful for testing this specific hypothesis
        4. Include both supporting and contradicting evidence to allow for proper analysis
        5. Make the data realistic for a gaming technology platform
        
        Format your response as a structured JSON object with appropriate keys and values.
        The JSON should be well-organized with categories of data relevant to the hypothesis.
        Do not include any explanations outside the JSON structure.
        """
        
        # Call Bedrock to generate the sample data
        sample_data_str = call_bedrock_llm(prompt)
        
        # Parse the JSON response
        try:
            # Extract JSON if it's wrapped in markdown code blocks
            if "```json" in sample_data_str:
                sample_data_str = sample_data_str.split("```json")[1].split("```")[0].strip()
            elif "```" in sample_data_str:
                sample_data_str = sample_data_str.split("```")[1].split("```")[0].strip()
                
            sample_data = json.loads(sample_data_str)
            
            # Include the data requirements in the returned data
            result = {
                "requirements": data_requirements,
                "generated_data": sample_data
            }
            
            return result
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw string
            return {"error": "Failed to parse generated data", "raw_data": sample_data_str}
    
    def test_hypotheses(self, hypotheses, data_analysis, raw_data=None):
        """
        Test the generated hypotheses against the data analysis and raw data
        
        Args:
            hypotheses (list): List of hypotheses to test
            data_analysis (dict): Results from data analysis
            raw_data (dict, optional): Raw data for additional testing
            
        Returns:
            dict: Test results for each hypothesis with supporting evidence
        """
        if not hypotheses:
            return {"error": "No hypotheses provided for testing"}
        
        # Generate sample data for each hypothesis if no raw_data is provided
        generated_data = {}
        if not raw_data:
            print("No raw data provided. Generating sample data for each hypothesis...")
            for i, hypothesis in enumerate(hypotheses):
                print(f"Generating data for hypothesis {i+1}...")
                hypothesis_data = self.generate_sample_data(hypothesis)
                generated_data[f"hypothesis_{i+1}"] = hypothesis_data
            
            # Use the generated data as raw_data if no raw_data was provided
            if generated_data:
                print("Sample data generation complete.")
                raw_data = {"generated_sample_data": generated_data}
            
        # Prepare the prompt for the LLM
        prompt = self._create_testing_prompt(hypotheses, data_analysis, raw_data)
        
        # Call the LLM to analyze and test the hypotheses
        test_results = call_bedrock_llm(prompt)
        
        return test_results
    
    def _create_testing_prompt(self, hypotheses, data_analysis, raw_data):
        """Create a prompt for the LLM to test hypotheses"""
        prompt = f"""
        You are a hypothesis testing expert. Your task is to evaluate the following hypotheses 
        against the provided data analysis and determine if they are supported, contradicted, 
        or if there is insufficient evidence.
        
        HYPOTHESES:
        {hypotheses}
        
        DATA ANALYSIS:
        """
        
        # If data_analysis is provided, use it; otherwise instruct to use the generated data
        if data_analysis:
            prompt += f"{data_analysis}\n\n"
        else:
            prompt += """No specific data analysis is provided. Please use the generated sample data provided below 
            to test these hypotheses. The sample data contains metrics, user behaviors, and platform performance 
            indicators that are relevant for testing each hypothesis.
            """
        
        # If raw_data is provided, include it
        if raw_data:
            # Check if it's our generated sample data
            if isinstance(raw_data, dict) and "generated_sample_data" in raw_data:
                prompt += "\nGENERATED SAMPLE DATA:\n"
                prompt += "The following data has been generated specifically to test each hypothesis:\n"
                
                # Format the generated data in a readable way
                for hyp_key, hyp_data in raw_data["generated_sample_data"].items():
                    prompt += f"\n{hyp_key.upper()}:\n"
                    
                    # Handle the new structure with requirements and generated_data
                    if isinstance(hyp_data, dict) and "requirements" in hyp_data and "generated_data" in hyp_data:
                        prompt += "DATA REQUIREMENTS:\n"
                        prompt += json.dumps(hyp_data["requirements"], indent=2)
                        prompt += "\n\nGENERATED DATA:\n"
                        prompt += json.dumps(hyp_data["generated_data"], indent=2)
                    else:
                        # Fallback for old format
                        prompt += json.dumps(hyp_data, indent=2)
                    
                    prompt += "\n"
            else:
                # Regular raw data
                prompt += f"\nRAW DATA:\n{raw_data}\n"
        else:
            prompt += "\nNo raw data is provided. Please make reasonable assumptions about underlying data points when needed.\n"
        
        prompt += """
        For each hypothesis:
        1. Evaluate if the data supports, contradicts, or is insufficient to prove/disprove it
        2. Provide specific evidence from the data that supports your conclusion
        3. Assign a confidence score (0-100%) to your evaluation
        4. Suggest any additional data that would be helpful to better test this hypothesis
        
        Format your response as a structured JSON with the following format:
        {
            "hypothesis_1": {
                "status": "supported|contradicted|insufficient evidence",
                "evidence": "Key evidence from the data",
                "confidence": 85,
                "additional_data_needed": "Description of helpful additional data"
            },
            ...
        }
        
        Make sure to reference specific data points from the generated sample data in your evidence.
        """
        
        return prompt