# TORONTO AI TEAM AGENT - PROPRIETARY
#
# Copyright (c) 2025 TORONTO AI
# Creator: David Tadeusz Chudak
# All Rights Reserved
#
# This file is part of the TORONTO AI TEAM AGENT software.
#
# This software is based on OpenManus (Copyright (c) 2025 manna_and_poem),
# which is licensed under the MIT License. The original license is included
# in the LICENSE file in the root directory of this project.
#
# This software has been substantially modified with proprietary enhancements.


"""API Integration for Human Input Request System.

This module provides the API endpoints for the Human Input Request System
to connect the frontend UI with the backend communication and prioritization mechanisms."""

from typing import Dict, Any, List, Optional
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..collaboration.project_manager_communication_flow import ProjectManagerCommunicationFlow, HumanInputRequestManager
from ..collaboration.request_prioritization_mechanism import RequestPrioritizationMechanism

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/human-input", tags=["human-input"])

# Models for API requests and responses
class InputRequestCreate(BaseModel):
    project_id: str
    title: str
    description: str
    priority: str = "medium"
    category: str = "information"
    requested_by: str
    original_request: str = ""
    notes: str = ""
    due_by: Optional[str] = None

class InputRequestUpdate(BaseModel):
    request_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    due_by: Optional[str] = None
    reformulated: Optional[bool] = None

class InputRequestResponse(BaseModel):
    project_id: str
    title: str
    response_content: Dict[str, Any]

class InputRequestFilter(BaseModel):
    project_id: str
    status: Optional[str] = "all"
    priority: Optional[str] = "all"
    category: Optional[str] = "all"

# Dependency to get communication flow
async def get_communication_flow():
    # This would normally be initialized at application startup and stored in a state manager
    # For now, we'll create a new instance each time
    from ..interface.project_manager_interface import ProjectManagerInterface
    project_manager_interface = ProjectManagerInterface()
    return ProjectManagerCommunicationFlow(project_manager_interface)

# Dependency to get prioritization mechanism
async def get_prioritization_mechanism():
    # This would normally be initialized at application startup and stored in a state manager
    return RequestPrioritizationMechanism()

@router.post("/requests", response_model=Dict[str, Any])
async def create_input_request(
    request: InputRequestCreate,
    comm_flow: ProjectManagerCommunicationFlow = Depends(get_communication_flow)
):
    """
    Create a new human input request.
    """
    try:
        result = await comm_flow.input_request_manager.create_input_request({
            "project_id": request.project_id,
            "title": request.title,
            "description": request.description,
            "priority": request.priority,
            "category": request.category,
            "requested_by": request.requested_by,
            "original_request": request.original_request,
            "notes": request.notes,
            "due_by": request.due_by
        })
        return result
    except Exception as e:
        logger.error(f"Error creating input request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating input request: {str(e)}")

@router.get("/requests/{project_id}", response_model=Dict[str, Any])
async def get_input_requests(
    project_id: str,
    status: str = "all",
    priority: str = "all",
    category: str = "all",
    comm_flow: ProjectManagerCommunicationFlow = Depends(get_communication_flow),
    prioritization: RequestPrioritizationMechanism = Depends(get_prioritization_mechanism)
):
    """
    Get human input requests for a project, filtered and prioritized.
    """
    try:
        # Get requests with filters
        result = await comm_flow.input_request_manager.get_input_requests({
            "project_id": project_id,
            "status": status,
            "priority": priority,
            "category": category
        })
        
        if not result.get("success", False):
            raise HTTPException(status_code=404, detail=result.get("message", "Failed to retrieve requests"))
        
        # Prioritize the requests
        prioritized_requests = prioritization.prioritize_requests(result["requests"])
        
        return {
            "success": True,
            "message": "Requests retrieved and prioritized",
            "requests": prioritized_requests,
            "count": len(prioritized_requests)
        }
    except Exception as e:
        logger.error(f"Error getting input requests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting input requests: {str(e)}")

@router.get("/requests/detail/{request_id}", response_model=Dict[str, Any])
async def get_input_request_detail(
    request_id: str,
    comm_flow: ProjectManagerCommunicationFlow = Depends(get_communication_flow)
):
    """
    Get details of a specific human input request.
    """
    try:
        result = await comm_flow.input_request_manager.get_input_request({
            "request_id": request_id
        })
        
        if not result.get("success", False):
            raise HTTPException(status_code=404, detail=result.get("message", "Request not found"))
        
        return result
    except Exception as e:
        logger.error(f"Error getting input request detail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting input request detail: {str(e)}")

@router.put("/requests/{request_id}", response_model=Dict[str, Any])
async def update_input_request(
    request_id: str,
    request: InputRequestUpdate,
    comm_flow: ProjectManagerCommunicationFlow = Depends(get_communication_flow)
):
    """
    Update a human input request.
    """
    try:
        # Create update params
        update_params = {"request_id": request_id}
        
        # Add optional fields if provided
        for field in ["title", "description", "status", "priority", "category", "notes", "due_by", "reformulated"]:
            value = getattr(request, field, None)
            if value is not None:
                update_params[field] = value
        
        result = await comm_flow.input_request_manager.update_input_request(update_params)
        
        if not result.get("success", False):
            raise HTTPException(status_code=404, detail=result.get("message", "Failed to update request"))
        
        return result
    except Exception as e:
        logger.error(f"Error updating input request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating input request: {str(e)}")

@router.post("/requests/{request_id}/respond", response_model=Dict[str, Any])
async def respond_to_input_request(
    request_id: str,
    response: InputRequestResponse,
    comm_flow: ProjectManagerCommunicationFlow = Depends(get_communication_flow)
):
    """
    Respond to a human input request.
    """
    try:
        result = await comm_flow.handle_human_to_agent_response({
            "project_id": response.project_id,
            "request_id": request_id,
            "response_content": response.response_content
        })
        
        if not result.get("success", False):
            raise HTTPException(status_code=404, detail=result.get("message", "Failed to process response"))
        
        return result
    except Exception as e:
        logger.error(f"Error responding to input request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error responding to input request: {str(e)}")

@router.get("/requests/count/{project_id}", response_model=Dict[str, Any])
async def get_pending_requests_count(
    project_id: str,
    comm_flow: ProjectManagerCommunicationFlow = Depends(get_communication_flow)
):
    """
    Get the count of pending human input requests for a project.
    """
    try:
        result = await comm_flow.input_request_manager.get_pending_requests_count({
            "project_id": project_id
        })
        
        if not result.get("success", False):
            raise HTTPException(status_code=404, detail=result.get("message", "Failed to get pending count"))
        
        return result
    except Exception as e:
        logger.error(f"Error getting pending requests count: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting pending requests count: {str(e)}")

@router.post("/agent-request", response_model=Dict[str, Any])
async def process_agent_request(
    project_id: str,
    agent_role: str,
    request_content: Dict[str, Any],
    comm_flow: ProjectManagerCommunicationFlow = Depends(get_communication_flow)
):
    """
    Process a request from an agent that needs human input.
    """
    try:
        result = await comm_flow.handle_agent_to_human_request({
            "project_id": project_id,
            "agent_role": agent_role,
            "request_content": request_content
        })
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to process agent request"))
        
        return result
    except Exception as e:
        logger.error(f"Error processing agent request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing agent request: {str(e)}")

@router.get("/analysis/{project_id}", response_model=Dict[str, Any])
async def analyze_request_patterns(
    project_id: str,
    comm_flow: ProjectManagerCommunicationFlow = Depends(get_communication_flow),
    prioritization: RequestPrioritizationMechanism = Depends(get_prioritization_mechanism)
):
    """
    Analyze patterns in human input requests for a project.
    """
    try:
        # Get all requests for the project
        result = await comm_flow.input_request_manager.get_input_requests({
            "project_id": project_id,
            "status": "all",
            "priority": "all",
            "category": "all"
        })
        
        if not result.get("success", False):
            raise HTTPException(status_code=404, detail=result.get("message", "Failed to retrieve requests"))
        
        # Analyze request patterns
        analysis = prioritization.analyze_request_patterns(result["requests"])
        
        return {
            "success": True,
            "message": "Request patterns analyzed",
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Error analyzing request patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing request patterns: {str(e)}")
