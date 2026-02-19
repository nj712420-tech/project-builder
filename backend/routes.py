# routes.py
import json
from fastapi import APIRouter, HTTPException
from schemas import ProjectRequest
from ai_service import build_and_execute_project

# Initialize the router
project_router = APIRouter()

@project_router.post("/build")
def generate_project_endpoint(request: ProjectRequest):
    try:
        # Call the logic from your service file
        result = build_and_execute_project(
            prompt=request.prompt, 
            include_db=request.include_db
        )
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))