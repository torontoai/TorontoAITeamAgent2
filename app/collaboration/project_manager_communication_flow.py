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


"""Project Manager Communication Flow for handling human input requests.

This module extends the Project Manager Interface to handle communication
between agents and human stakeholders, with the Project Manager as the central point."""

from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime
import uuid

from ..agent.project_manager import ProjectManagerAgent
from ..tools.registry import registry

logger = logging.getLogger(__name__)

class HumanInputRequestManager:
    """Manages human input requests across the multi-agent system."""
    
    def __init__(self, project_manager_interface):
        """Initialize the Human Input Request Manager.
        
        Args:
            project_manager_interface: Reference to the Project Manager Interface"""
        self.project_manager_interface = project_manager_interface
        self.input_requests = {}  # Dictionary to store input requests by ID
        self.request_queue = {}   # Dictionary to store request queues by project
        
        logger.info("Human Input Request Manager initialized")
    
    async def create_input_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new human input request.
        
        Args:
            params: Request parameters including project_id, title, description,
                   priority, category, and originating agent
                   
        Returns:
            Request creation result
        """
        project_id = params.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Project ID is required"
            }
        
        # Generate a unique request ID
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        
        # Create the request object
        request = {
            "id": request_id,
            "project_id": project_id,
            "title": params.get("title", "Untitled Request"),
            "description": params.get("description", ""),
            "status": "pending",
            "priority": params.get("priority", "medium"),
            "category": params.get("category", "information"),
            "requested_by": params.get("requested_by", "Unknown Agent"),
            "created_at": datetime.now().isoformat(),
            "due_by": params.get("due_by"),
            "original_request": params.get("original_request", ""),
            "notes": params.get("notes", ""),
            "reformulated": False
        }
        
        # Store the request
        self.input_requests[request_id] = request
        
        # Add to project queue
        if project_id not in self.request_queue:
            self.request_queue[project_id] = []
        
        self.request_queue[project_id].append(request_id)
        
        # Create a notification for the human stakeholder
        await self.project_manager_interface.add_notification({
            "project_id": project_id,
            "title": f"New Input Request: {request['title']}",
            "content": f"A new input request has been created by {request['requested_by']}.",
            "priority": request["priority"]
        })
        
        logger.info(f"Created input request: {request_id} - {request['title']}")
        
        return {
            "success": True,
            "message": "Input request created successfully",
            "request_id": request_id,
            "request": request
        }
    
    async def get_input_requests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get human input requests.
        
        Args:
            params: Parameters including project_id, status, priority, and category filters
            
        Returns:
            Input requests matching the filters
        """
        project_id = params.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Project ID is required"
            }
        
        # Get request IDs for the project
        request_ids = self.request_queue.get(project_id, [])
        
        # Get the actual requests
        requests = [self.input_requests[req_id] for req_id in request_ids if req_id in self.input_requests]
        
        # Apply filters if provided
        status_filter = params.get("status")
        if status_filter and status_filter != "all":
            requests = [req for req in requests if req["status"] == status_filter]
        
        priority_filter = params.get("priority")
        if priority_filter and priority_filter != "all":
            requests = [req for req in requests if req["priority"] == priority_filter]
        
        category_filter = params.get("category")
        if category_filter and category_filter != "all":
            requests = [req for req in requests if req["category"] == category_filter]
        
        # Sort by priority and creation date
        requests.sort(key=lambda x: (
            {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3),
            x["created_at"]
        ))
        
        return {
            "success": True,
            "message": "Input requests retrieved",
            "requests": requests,
            "count": len(requests)
        }
    
    async def get_input_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a specific human input request.
        
        Args:
            params: Parameters including request_id
            
        Returns:
            Input request details
        """
        request_id = params.get("request_id")
        if not request_id or request_id not in self.input_requests:
            return {
                "success": False,
                "message": "Invalid request ID"
            }
        
        return {
            "success": True,
            "message": "Input request retrieved",
            "request": self.input_requests[request_id]
        }
    
    async def update_input_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a human input request.
        
        Args:
            params: Parameters including request_id and updated fields
            
        Returns:
            Update result
        """
        request_id = params.get("request_id")
        if not request_id or request_id not in self.input_requests:
            return {
                "success": False,
                "message": "Invalid request ID"
            }
        
        request = self.input_requests[request_id]
        
        # Update fields if provided
        for field in ["title", "description", "priority", "category", "notes", "due_by"]:
            if field in params:
                request[field] = params[field]
        
        # Handle status changes separately to track completion time
        if "status" in params and params["status"] != request["status"]:
            request["status"] = params["status"]
            if params["status"] == "completed":
                request["completed_at"] = datetime.now().isoformat()
        
        # Mark as reformulated if the project manager edited it
        if params.get("reformulated", False):
            request["reformulated"] = True
        
        logger.info(f"Updated input request: {request_id}")
        
        return {
            "success": True,
            "message": "Input request updated successfully",
            "request": request
        }
    
    async def delete_input_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a human input request.
        
        Args:
            params: Parameters including request_id
            
        Returns:
            Deletion result
        """
        request_id = params.get("request_id")
        if not request_id or request_id not in self.input_requests:
            return {
                "success": False,
                "message": "Invalid request ID"
            }
        
        # Get the project ID before deletion
        project_id = self.input_requests[request_id]["project_id"]
        
        # Remove from input requests
        del self.input_requests[request_id]
        
        # Remove from project queue
        if project_id in self.request_queue:
            if request_id in self.request_queue[project_id]:
                self.request_queue[project_id].remove(request_id)
        
        logger.info(f"Deleted input request: {request_id}")
        
        return {
            "success": True,
            "message": "Input request deleted successfully",
            "request_id": request_id
        }
    
    async def process_agent_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request from an agent that needs human input.
        
        Args:
            params: Parameters including project_id, agent_role, request_content
            
        Returns:
            Processing result
        """
        project_id = params.get("project_id")
        agent_role = params.get("agent_role")
        request_content = params.get("request_content", {})
        
        if not project_id or not agent_role or not request_content:
            return {
                "success": False,
                "message": "Missing required parameters"
            }
        
        # Extract request details
        title = request_content.get("title", f"Request from {agent_role}")
        description = request_content.get("description", "")
        priority = request_content.get("priority", "medium")
        category = request_content.get("category", "information")
        original_request = request_content.get("original_request", "")
        
        # Create the input request
        result = await self.create_input_request({
            "project_id": project_id,
            "title": title,
            "description": description,
            "priority": priority,
            "category": category,
            "requested_by": agent_role,
            "original_request": original_request,
            "notes": f"This request was automatically generated from {agent_role}'s query."
        })
        
        return result
    
    async def get_pending_requests_count(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the count of pending requests for a project.
        
        Args:
            params: Parameters including project_id
            
        Returns:
            Count of pending requests
        """
        project_id = params.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Project ID is required"
            }
        
        # Get request IDs for the project
        request_ids = self.request_queue.get(project_id, [])
        
        # Count pending requests
        pending_count = sum(
            1 for req_id in request_ids 
            if req_id in self.input_requests and self.input_requests[req_id]["status"] == "pending"
        )
        
        return {
            "success": True,
            "message": "Pending requests count retrieved",
            "count": pending_count
        }


class ProjectManagerCommunicationFlow:
    """Handles communication flow between agents and human stakeholders,
    with the Project Manager as the central point."""
    
    def __init__(self, project_manager_interface):
        """Initialize the Project Manager Communication Flow.
        
        Args:
            project_manager_interface: Reference to the Project Manager Interface"""
        self.project_manager_interface = project_manager_interface
        self.input_request_manager = HumanInputRequestManager(project_manager_interface)
        self.agent_messages = {}  # Dictionary to store messages by project and agent
        
        logger.info("Project Manager Communication Flow initialized")
    
    async def handle_agent_to_human_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request from an agent that needs to be forwarded to a human.
        
        Args:
            params: Parameters including project_id, agent_role, request_content
            
        Returns:
            Handling result
        """
        project_id = params.get("project_id")
        agent_role = params.get("agent_role")
        request_content = params.get("request_content", {})
        
        if not project_id or not agent_role or not request_content:
            return {
                "success": False,
                "message": "Missing required parameters"
            }
        
        # Store the original message
        if project_id not in self.agent_messages:
            self.agent_messages[project_id] = {}
        
        if agent_role not in self.agent_messages[project_id]:
            self.agent_messages[project_id][agent_role] = []
        
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        message = {
            "id": message_id,
            "timestamp": datetime.now().isoformat(),
            "content": request_content,
            "processed": False
        }
        
        self.agent_messages[project_id][agent_role].append(message)
        
        # Process the request through the Project Manager Agent
        # This allows the PM to reformulate, prioritize, or filter the request
        reformulated_request = await self.project_manager_interface.project_manager.reformulate_human_input_request({
            "project_id": project_id,
            "agent_role": agent_role,
            "request_content": request_content,
            "message_id": message_id
        })
        
        # If the PM decides to forward the request to the human
        if reformulated_request.get("forward_to_human", True):
            # Create an input request with the reformulated content
            result = await self.input_request_manager.create_input_request({
                "project_id": project_id,
                "title": reformulated_request.get("title", request_content.get("title", f"Request from {agent_role}")),
                "description": reformulated_request.get("description", request_content.get("description", "")),
                "priority": reformulated_request.get("priority", request_content.get("priority", "medium")),
                "category": reformulated_request.get("category", request_content.get("category", "information")),
                "requested_by": agent_role,
                "original_request": request_content.get("original_request", ""),
                "notes": reformulated_request.get("notes", ""),
                "reformulated": True
            })
            
            # Mark the message as processed
            for msg in self.agent_messages[project_id][agent_role]:
                if msg["id"] == message_id:
                    msg["processed"] = True
                    msg["request_id"] = result.get("request_id")
                    break
            
            return {
                "success": True,
                "message": "Agent request forwarded to human via Project Manager",
                "request_id": result.get("request_id"),
                "reformulated": True
            }
        else:
            # PM decided not to forward to human, perhaps handled directly
            return {
                "success": True,
                "message": "Agent request handled by Project Manager without human input",
                "reformulated": False,
                "pm_response": reformulated_request.get("pm_response", {})
            }
    
    async def handle_human_to_agent_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a response from a human that needs to be forwarded to an agent.
        
        Args:
            params: Parameters including project_id, request_id, response_content
            
        Returns:
            Handling result
        """
        project_id = params.get("project_id")
        request_id = params.get("request_id")
        response_content = params.get("response_content", {})
        
        if not project_id or not request_id or not response_content:
            return {
                "success": False,
                "message": "Missing required parameters"
            }
        
        # Get the input request
        request_result = await self.input_request_manager.get_input_request({
            "request_id": request_id
        })
        
        if not request_result.get("success", False):
            return request_result
        
        request = request_result["request"]
        agent_role = request["requested_by"]
        
        # Update the request status
        await self.input_request_manager.update_input_request({
            "request_id": request_id,
            "status": "completed",
        })
        
        # Forward the response to the appropriate agent via the Project Manager
        result = await self.project_manager_interface.project_manager.forward_human_response_to_agent({
            "project_id": project_id,
            "agent_role": agent_role,
            "request_id": request_id,
            "response_content": response_content
        })
        
        return {
            "success": True,
            "message": "Human response forwarded to agent via Project Manager",
            "agent_role": agent_role,
            "request_id": request_id
        }
    
    async def get_agent_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get messages from agents for a project.
        
        Args:
            params: Parameters including project_id and agent_role
            
        Returns:
            Agent messages
        """
        project_id = params.get("project_id")
        agent_role = params.get("agent_role")
        
        if not project_id:
            return {
                "success": False,
                "message": "Project ID is required"
            }
        
        if project_id not in self.agent_messages:
            return {
                "success": True,
                "message": "No messages found for this project",
                "messages": []
            }
        
        if agent_role:
            # Get messages for a specific agent
            if agent_role not in self.agent_messages[project_id]:
                return {
                    "success": True,
                    "message": f"No messages found for {agent_role}",
                    "messages": []
                }
            
            return {
                "success": True,
                "message": f"Messages retrieved for {agent_role}",
                "messages": self.agent_messages[project_id][agent_role]
            }
        else:
            # Get all messages for the project
            all_messages = []
            for role, messages in self.agent_messages[project_id].items():
                for msg in messages:
                    msg_copy = msg.copy()
                    msg_copy["agent_role"] = role
                    all_messages.append(msg_copy)
            
            # Sort by timestamp
            all_messages.sort(key=lambda x: x["timestamp"])
            
            return {
                "success": True,
                "message": "All messages retrieved",
                "messages": all_messages
            }
