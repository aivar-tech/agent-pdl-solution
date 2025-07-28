# Aivar PDL Agents: Asynchronous Multi-Agent Workflow System

![Aivar Logo](https://niyo.aivar.app/icons/aivar.png)

## Overview

Aivar PDL Agents is a powerful asynchronous multi-agent workflow system designed for product and data analysis. The system orchestrates multiple specialized AI agents that work together to analyze product briefs, generate insights, form hypotheses, and test them against data. With a modern, responsive UI and real-time execution tracking, PDL Agents streamlines the product analysis process from concept to actionable insights.

## Features

### Core Functionality

- **Multi-Agent Architecture**: Specialized agents for scoping, data analysis, hypothesis generation, and hypothesis testing
- **Asynchronous Execution**: Non-blocking workflow execution with real-time status updates
- **Persistent Execution Tracking**: All executions are stored and can be revisited at any time
- **Real-time UI Updates**: Live status indicators show which agent is currently executing
- **PDF Export**: Export complete analysis reports as professionally formatted PDF documents

### Agent Capabilities

1. **Scoping Agent**: Analyzes product briefs to define problem statements, goals, success metrics, and key requirements
2. **Data Analysis Agent**: Processes raw data to extract patterns, trends, and key insights
3. **Hypothesis Generation Agent**: Creates testable hypotheses based on the scope and data analysis
4. **Hypothesis Testing Agent**: Tests hypotheses against data using a two-step approach:
   - First determines what data is required for testing
   - Then generates relevant sample data and evaluates each hypothesis

### User Interface

- **Clean, Modern Design**: Intuitive interface with Aivar brand styling (blue, purple, gold accents)
- **Sidebar Navigation**: Easy access to agents and previous executions
- **Agent Status Indicators**: Visual indicators show which agent is currently active
- **Responsive Layout**: Works on desktop and mobile devices
- **Interactive Results**: Collapsible sections for detailed exploration of agent outputs

## Technical Architecture

### Backend

- **FastAPI Framework**: High-performance API server with async support
- **Agent System**: Modular agent architecture for easy extension
- **Execution Storage**: JSON-based persistent storage of all execution data
- **Bedrock Integration**: Uses AWS Bedrock for LLM capabilities

### Frontend

- **Vanilla JavaScript**: Clean, dependency-minimal frontend implementation
- **CSS3**: Modern styling with variables, flexbox, and responsive design
- **Dynamic Content Rendering**: Client-side rendering of agent results
- **PDF Generation**: Client-side PDF generation using jsPDF and html2canvas

## Getting Started

### Prerequisites

- Python 3.9+
- AWS credentials configured for Bedrock access
- Modern web browser

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aivar-ai/pdl-agents.git
   cd pdl-agents
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure AWS credentials:
   ```bash
   aws configure
   ```

### Running the Application

1. Start the API server:
   ```bash
   python api.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

## Usage Guide

### Creating a New Analysis

1. Enter a product brief in the "Brief" field
2. Optionally add relevant data in the "Raw Data" field
3. Click "Run Multiagent Workflow"
4. Watch the real-time status indicators as each agent processes your request
5. Review the comprehensive analysis when complete

### Viewing Previous Analyses

1. Select any previous execution from the "Agent Executions" sidebar
2. The complete results will be loaded and displayed

### Exporting Results

1. After an analysis is complete, click the "Export as PDF" button
2. A professionally formatted PDF with all agent outputs will be generated and downloaded
3. The PDF includes timestamps, execution ID, and all analysis details

## Development

### Project Structure

```
pdl-agents/
├── agent/                 # Base agent implementation
├── api.py                 # FastAPI server implementation
├── data_analysis_agent.py # Data analysis agent implementation
├── executions/            # Stored execution results
├── hypothesis_agent.py    # Hypothesis generation agent implementation
├── hypothesis_testing_agent.py # Hypothesis testing agent implementation
├── main.py                # Main workflow orchestration
├── master_agent.py        # Master agent for coordination
├── requirements.txt       # Python dependencies
├── scoping_agent.py       # Scoping agent implementation
├── ui/                    # Frontend files
│   ├── index.html         # Main HTML structure
│   ├── main.js            # JavaScript functionality
│   └── examples.js        # Example briefs
└── utils.py               # Utility functions
```

### Adding a New Agent

1. Create a new agent class file (e.g., `new_agent.py`)
2. Implement the agent interface with required methods
3. Register the agent in `main.py`
4. Add UI components in `index.html` and `main.js`

## Advanced Features

### Two-Step Hypothesis Testing

The hypothesis testing agent uses a sophisticated two-step approach:

1. **Data Requirements Analysis**: First determines what specific data would be needed to properly test each hypothesis
2. **Targeted Data Generation**: Uses the requirements to generate highly relevant sample data
3. **Comprehensive Evaluation**: Tests hypotheses against the generated data with confidence scores

### Real-time Agent Status Tracking

The UI provides visual feedback on the current execution state:

- Gray indicators show inactive agents
- Gold, pulsing indicators show the currently executing agent
- Status updates automatically as the workflow progresses

### PDF Export Customization

The PDF export feature includes:

- Title page with execution details
- Formatted agent outputs with proper styling
- Page breaks between sections
- Footer with page numbers and timestamp
- Automatic filename based on execution ID

## Troubleshooting

### Common Issues

- **Execution Timeout**: For complex analyses, increase the timeout setting in `api.py`
- **PDF Generation Fails**: Ensure all content is properly loaded before attempting export
- **Agent Errors**: Check the console logs for detailed error messages

### Support

For issues, feature requests, or contributions, please contact the Aivar team or open an issue on the repository.

## License

Copyright © 2025 Aivar AI. All rights reserved.

---

Built with ❤️ by [Aivar](https://aivar.app)
