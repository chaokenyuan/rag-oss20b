from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import uvicorn
from java_agent import agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Java Development Agent API",
    description="GPT-OSS-20B powered Java development assistant with Neo4j knowledge graph",
    version="1.0.0"
)

# Request/Response models
class ProjectAnalysisRequest(BaseModel):
    project_path: str

class CodeGenerationRequest(BaseModel):
    request: str
    context: Optional[Dict[str, Any]] = None

class CodeImprovementRequest(BaseModel):
    code: str
    context: Optional[Dict[str, Any]] = None

class CodebaseQueryRequest(BaseModel):
    query: str

class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.on_startup
async def startup_event():
    """Initialize the agent on startup"""
    try:
        agent.initialize()
        logger.info("Java Development Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Java Development Agent API",
        "version": "1.0.0",
        "description": "GPT-OSS-20B powered Java development assistant"
    }

@app.get("/status", response_model=APIResponse)
async def get_status():
    """Get agent status and statistics"""
    try:
        status = agent.get_status()
        return APIResponse(success=True, data=status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return APIResponse(success=False, error=str(e))

@app.post("/analyze", response_model=APIResponse)
async def analyze_project(request: ProjectAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a Java project and store its structure in the knowledge graph"""
    try:
        # Run analysis in background for large projects
        background_tasks.add_task(run_project_analysis, request.project_path)
        
        return APIResponse(
            success=True,
            data={
                "message": "Project analysis started",
                "project_path": request.project_path
            }
        )
    except Exception as e:
        logger.error(f"Error starting project analysis: {e}")
        return APIResponse(success=False, error=str(e))

async def run_project_analysis(project_path: str):
    """Background task for project analysis"""
    try:
        result = agent.analyze_project(project_path)
        logger.info(f"Project analysis completed: {result}")
    except Exception as e:
        logger.error(f"Project analysis failed: {e}")

@app.post("/analyze/sync", response_model=APIResponse)
async def analyze_project_sync(request: ProjectAnalysisRequest):
    """Synchronously analyze a Java project"""
    try:
        result = agent.analyze_project(request.project_path)
        return APIResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Error analyzing project: {e}")
        return APIResponse(success=False, error=str(e))

@app.post("/generate", response_model=APIResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate Java code based on natural language request"""
    try:
        result = agent.generate_code(request.request, request.context)
        return APIResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Error generating code: {e}")
        return APIResponse(success=False, error=str(e))

@app.post("/improve", response_model=APIResponse)
async def suggest_improvements(request: CodeImprovementRequest):
    """Suggest improvements for existing Java code"""
    try:
        result = agent.suggest_improvements(request.code, request.context)
        return APIResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Error suggesting improvements: {e}")
        return APIResponse(success=False, error=str(e))

@app.post("/query", response_model=APIResponse)
async def query_codebase(request: CodebaseQueryRequest):
    """Answer questions about the codebase"""
    try:
        result = agent.query_codebase(request.query)
        return APIResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return APIResponse(success=False, error=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = agent.get_status()
        return {
            "status": "healthy" if status.get('initialized', False) else "unhealthy",
            "timestamp": "2025-08-10T22:29:00Z",
            "agent_initialized": status.get('initialized', False)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": "2025-08-10T22:29:00Z",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )