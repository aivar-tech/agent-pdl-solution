from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List, Any
import uuid
import json
import os
import time
from datetime import datetime
from pathlib import Path
import threading
import asyncio

from master_agent import MasterAgent

# Create FastAPI app
app = FastAPI(title="PDL Agents API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Serve index.html at root
@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse("ui/index.html")

# Create execution directory if it doesn't exist
EXECUTIONS_DIR = Path("executions")
EXECUTIONS_DIR.mkdir(exist_ok=True)

# Models
class WorkflowRequest(BaseModel):
    brief: str
    raw_data: Optional[str] = None

class ExecutionStatus(BaseModel):
    request_id: str
    status: str  # "pending", "running", "completed", "failed"
    created_at: str
    updated_at: str
    brief: str
    raw_data: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    current_step: Optional[str] = None
    error: Optional[str] = None

# In-memory store for active executions
active_executions = {}

# Background task to run the workflow
def run_workflow_task(request_id: str, brief: str, raw_data: Optional[str] = None):
    try:
        # Update status to running
        update_execution_status(request_id, "running", current_step="Starting workflow")
        
        # Initialize the master agent
        master_agent = MasterAgent()
        
        # Update status - data analysis
        update_execution_status(request_id, "running", current_step="Analyzing data")
        
        # Run the workflow
        if raw_data:
            results = master_agent.run_workflow(brief, raw_data)
        else:
            results = master_agent.run_workflow(brief)
        
        # Update status to completed with results
        update_execution_status(request_id, "completed", results=results)
        
    except Exception as e:
        # Update status to failed with error
        update_execution_status(request_id, "failed", error=str(e))

def update_execution_status(request_id: str, status: str, current_step: str = None, 
                          results: Dict[str, Any] = None, error: str = None):
    """Update the execution status and save to file"""
    
    # Get the execution data
    execution_file = EXECUTIONS_DIR / f"{request_id}.json"
    
    if execution_file.exists():
        with open(execution_file, "r") as f:
            execution_data = json.load(f)
    else:
        # This shouldn't happen, but just in case
        execution_data = active_executions.get(request_id, {})
    
    # Update the execution data
    execution_data["status"] = status
    execution_data["updated_at"] = datetime.now().isoformat()
    
    if current_step is not None:
        execution_data["current_step"] = current_step
    
    if results is not None:
        execution_data["results"] = results
    
    if error is not None:
        execution_data["error"] = error
    
    # Save to file
    with open(execution_file, "w") as f:
        json.dump(execution_data, f, indent=2)
    
    # Update in-memory store
    active_executions[request_id] = execution_data

@app.post("/api/workflow", response_model=ExecutionStatus)
async def create_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Start a new workflow execution"""
    
    # Generate a unique ID for this execution
    request_id = str(uuid.uuid4())
    
    # Create execution data
    execution_data = {
        "request_id": request_id,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "brief": request.brief,
        "raw_data": request.raw_data,
        "current_step": "Queued"
    }
    
    # Save to file
    execution_file = EXECUTIONS_DIR / f"{request_id}.json"
    with open(execution_file, "w") as f:
        json.dump(execution_data, f, indent=2)
    
    # Store in memory
    active_executions[request_id] = execution_data
    
    # Start the workflow in the background
    background_tasks.add_task(
        run_workflow_task, 
        request_id=request_id, 
        brief=request.brief, 
        raw_data=request.raw_data
    )
    
    return execution_data

@app.get("/api/workflow/{request_id}", response_model=ExecutionStatus)
async def get_workflow_status(request_id: str):
    """Get the status of a workflow execution"""
    
    # Check if the execution exists
    execution_file = EXECUTIONS_DIR / f"{request_id}.json"
    if not execution_file.exists():
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Load the execution data
    with open(execution_file, "r") as f:
        execution_data = json.load(f)
    
    return execution_data

@app.get("/api/workflows", response_model=List[ExecutionStatus])
async def list_workflows():
    """List all workflow executions"""
    
    executions = []
    
    # Load all execution files
    for execution_file in EXECUTIONS_DIR.glob("*.json"):
        with open(execution_file, "r") as f:
            execution_data = json.load(f)
        executions.append(execution_data)
    
    # Sort by created_at (newest first)
    executions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return executions

# This comment replaces the duplicate root endpoint
