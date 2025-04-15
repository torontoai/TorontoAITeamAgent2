"""
OpenAI Swarm integration for TORONTO AI TEAM AGENT.

This module provides integration with OpenAI Swarm for distributed AI agent collaboration
and swarm intelligence capabilities.
"""

import os
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union, Callable
import requests
import uuid

from app.core.error_handling import ErrorHandler, ErrorCategory, ErrorSeverity, safe_execute
from app.orchestration.models.orchestration_models import AgentRole, WorkflowDefinition, WorkflowState

logger = logging.getLogger(__name__)

class SwarmClient:
    """Client for interacting with OpenAI Swarm API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the OpenAI Swarm client.
        
        Args:
            api_key: OpenAI Swarm API key (defaults to OPENAI_SWARM_API_KEY environment variable)
            base_url: Base URL for the OpenAI Swarm API
        """
        self.api_key = api_key or os.environ.get("OPENAI_SWARM_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI Swarm API key not provided. Some functionality may be limited.")
            
        self.base_url = base_url or "https://api.openai-swarm.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def create_swarm(
        self, 
        name: str, 
        description: str,
        agent_count: int = 5,
        agent_types: Optional[List[str]] = None,
        configuration: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new agent swarm.
        
        Args:
            name: Name of the swarm
            description: Description of the swarm's purpose
            agent_count: Number of agents in the swarm
            agent_types: Types of agents to include in the swarm
            configuration: Additional configuration parameters
            
        Returns:
            Dict containing the created swarm details
        """
        with ErrorHandler(
            error_category=ErrorCategory.ORCHESTRATION,
            error_message="Error creating agent swarm",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/swarms"
            
            payload = {
                "name": name,
                "description": description,
                "agent_count": agent_count
            }
            
            if agent_types:
                payload["agent_types"] = agent_types
                
            if configuration:
                payload["configuration"] = configuration
            
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            
            return response.json()
    
    def get_swarm(self, swarm_id: str) -> Dict[str, Any]:
        """
        Get details of an existing swarm.
        
        Args:
            swarm_id: ID of the swarm to retrieve
            
        Returns:
            Dict containing the swarm details
        """
        with ErrorHandler(
            error_category=ErrorCategory.ORCHESTRATION,
            error_message=f"Error retrieving swarm: {swarm_id}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/swarms/{swarm_id}"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def list_swarms(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        List existing swarms.
        
        Args:
            limit: Maximum number of swarms to return
            offset: Offset for pagination
            
        Returns:
            Dict containing the list of swarms
        """
        with ErrorHandler(
            error_category=ErrorCategory.ORCHESTRATION,
            error_message="Error listing swarms",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/swarms?limit={limit}&offset={offset}"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def delete_swarm(self, swarm_id: str) -> Dict[str, Any]:
        """
        Delete an existing swarm.
        
        Args:
            swarm_id: ID of the swarm to delete
            
        Returns:
            Dict containing the deletion result
        """
        with ErrorHandler(
            error_category=ErrorCategory.ORCHESTRATION,
            error_message=f"Error deleting swarm: {swarm_id}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/swarms/{swarm_id}"
            
            response = self.session.delete(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def submit_task(
        self, 
        swarm_id: str, 
        task: str,
        context: Optional[Dict[str, Any]] = None,
        priority: int = 1,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit a task to a swarm.
        
        Args:
            swarm_id: ID of the swarm to submit the task to
            task: Description of the task
            context: Additional context for the task
            priority: Priority of the task (1-5, with 5 being highest)
            callback_url: URL to call when the task is completed
            
        Returns:
            Dict containing the task submission result
        """
        with ErrorHandler(
            error_category=ErrorCategory.ORCHESTRATION,
            error_message=f"Error submitting task to swarm: {swarm_id}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/swarms/{swarm_id}/tasks"
            
            payload = {
                "task": task,
                "priority": priority
            }
            
            if context:
                payload["context"] = context
                
            if callback_url:
                payload["callback_url"] = callback_url
            
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            
            return response.json()
    
    def get_task_status(self, swarm_id: str, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task.
        
        Args:
            swarm_id: ID of the swarm the task was submitted to
            task_id: ID of the task to check
            
        Returns:
            Dict containing the task status
        """
        with ErrorHandler(
            error_category=ErrorCategory.ORCHESTRATION,
            error_message=f"Error getting task status: {task_id}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/swarms/{swarm_id}/tasks/{task_id}"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def get_task_result(self, swarm_id: str, task_id: str) -> Dict[str, Any]:
        """
        Get the result of a completed task.
        
        Args:
            swarm_id: ID of the swarm the task was submitted to
            task_id: ID of the task to get the result for
            
        Returns:
            Dict containing the task result
        """
        with ErrorHandler(
            error_category=ErrorCategory.ORCHESTRATION,
            error_message=f"Error getting task result: {task_id}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/swarms/{swarm_id}/tasks/{task_id}/result"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def update_swarm_configuration(
        self, 
        swarm_id: str, 
        configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the configuration of a swarm.
        
        Args:
            swarm_id: ID of the swarm to update
            configuration: New configuration parameters
            
        Returns:
            Dict containing the update result
        """
        with ErrorHandler(
            error_category=ErrorCategory.ORCHESTRATION,
            error_message=f"Error updating swarm configuration: {swarm_id}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/swarms/{swarm_id}/configuration"
            
            response = self.session.patch(endpoint, json=configuration)
            response.raise_for_status()
            
            return response.json()
    
    def get_swarm_metrics(self, swarm_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a swarm.
        
        Args:
            swarm_id: ID of the swarm to get metrics for
            
        Returns:
            Dict containing the swarm metrics
        """
        with ErrorHandler(
            error_category=ErrorCategory.ORCHESTRATION,
            error_message=f"Error getting swarm metrics: {swarm_id}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/swarms/{swarm_id}/metrics"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()


class SwarmOrchestrationService:
    """Service for integrating OpenAI Swarm with the orchestration system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Swarm Orchestration service.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        api_key = self.config.get("api_key") or os.environ.get("OPENAI_SWARM_API_KEY")
        base_url = self.config.get("base_url")
        
        self.client = SwarmClient(api_key=api_key, base_url=base_url)
        
        # Cache for active swarms
        self.active_swarms = {}
        
        # Default swarm configuration
        self.default_swarm_config = self.config.get("default_swarm_config", {
            "communication_mode": "full_mesh",
            "consensus_threshold": 0.7,
            "max_iterations": 10,
            "timeout_seconds": 300
        })
    
    def create_agent_swarm(
        self, 
        name: str, 
        description: str,
        roles: List[AgentRole],
        swarm_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new agent swarm with specified roles.
        
        Args:
            name: Name of the swarm
            description: Description of the swarm's purpose
            roles: List of agent roles to include in the swarm
            swarm_size: Size of the swarm (defaults to number of roles)
            
        Returns:
            Dict containing the created swarm details
        """
        # Determine swarm size
        if swarm_size is None:
            swarm_size = len(roles)
        
        # Map roles to agent types
        agent_types = [role.name for role in roles]
        
        # Create configuration based on roles
        configuration = self.default_swarm_config.copy()
        configuration["roles"] = [role.to_dict() for role in roles]
        
        # Create the swarm
        swarm_result = self.client.create_swarm(
            name=name,
            description=description,
            agent_count=swarm_size,
            agent_types=agent_types,
            configuration=configuration
        )
        
        # Cache the active swarm
        swarm_id = swarm_result.get("id")
        if swarm_id:
            self.active_swarms[swarm_id] = {
                "name": name,
                "description": description,
                "roles": roles,
                "created_at": time.time(),
                "tasks": {}
            }
        
        return swarm_result
    
    def execute_workflow(
        self, 
        workflow: WorkflowDefinition,
        context: Dict[str, Any],
        callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow using a swarm of agents.
        
        Args:
            workflow: Workflow definition to execute
            context: Context for the workflow execution
            callback: Optional callback function to call when tasks complete
            
        Returns:
            Dict containing the workflow execution result
        """
        # Create a swarm for this workflow
        swarm_result = self.create_agent_swarm(
            name=f"Workflow: {workflow.name}",
            description=workflow.description,
            roles=workflow.roles
        )
        
        swarm_id = swarm_result.get("id")
        if not swarm_id:
            return {"error": "Failed to create swarm", "details": swarm_result}
        
        # Prepare the workflow context
        workflow_context = {
            "workflow": workflow.to_dict(),
            "user_context": context,
            "execution_id": str(uuid.uuid4())
        }
        
        # Submit the workflow as a task
        task_result = self.client.submit_task(
            swarm_id=swarm_id,
            task=f"Execute workflow: {workflow.name}",
            context=workflow_context,
            priority=self.config.get("workflow_priority", 3)
        )
        
        task_id = task_result.get("id")
        if not task_id:
            return {"error": "Failed to submit workflow task", "details": task_result}
        
        # Store task information
        if swarm_id in self.active_swarms:
            self.active_swarms[swarm_id]["tasks"][task_id] = {
                "type": "workflow",
                "workflow": workflow.name,
                "status": "submitted",
                "submitted_at": time.time()
            }
        
        # If callback is provided, start a background thread to monitor the task
        if callback:
            self._monitor_task_async(swarm_id, task_id, callback)
        
        return {
            "swarm_id": swarm_id,
            "task_id": task_id,
            "status": "submitted",
            "workflow": workflow.name
        }
    
    def execute_distributed_task(
        self, 
        task: str,
        roles: List[AgentRole],
        context: Dict[str, Any],
        priority: int = 2,
        wait_for_result: bool = False,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute a task using a distributed swarm of agents.
        
        Args:
            task: Description of the task to execute
            roles: List of agent roles needed for the task
            context: Context for the task execution
            priority: Priority of the task (1-5)
            wait_for_result: Whether to wait for the task to complete
            timeout: Timeout in seconds when waiting for result
            
        Returns:
            Dict containing the task execution result
        """
        # Create a swarm for this task
        swarm_result = self.create_agent_swarm(
            name=f"Task: {task[:30]}...",
            description=task,
            roles=roles
        )
        
        swarm_id = swarm_result.get("id")
        if not swarm_id:
            return {"error": "Failed to create swarm", "details": swarm_result}
        
        # Submit the task
        task_result = self.client.submit_task(
            swarm_id=swarm_id,
            task=task,
            context=context,
            priority=priority
        )
        
        task_id = task_result.get("id")
        if not task_id:
            return {"error": "Failed to submit task", "details": task_result}
        
        # Store task information
        if swarm_id in self.active_swarms:
            self.active_swarms[swarm_id]["tasks"][task_id] = {
                "type": "task",
                "description": task,
                "status": "submitted",
                "submitted_at": time.time()
            }
        
        # If wait_for_result is True, poll for the result
        if wait_for_result:
            return self._wait_for_task_result(swarm_id, task_id, timeout)
        
        return {
            "swarm_id": swarm_id,
            "task_id": task_id,
            "status": "submitted"
        }
    
    def get_workflow_status(self, swarm_id: str, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution.
        
        Args:
            swarm_id: ID of the swarm executing the workflow
            task_id: ID of the workflow task
            
        Returns:
            Dict containing the workflow status
        """
        # Get the task status
        task_status = self.client.get_task_status(swarm_id, task_id)
        
        # Update cached status
        if swarm_id in self.active_swarms and task_id in self.active_swarms[swarm_id]["tasks"]:
            self.active_swarms[swarm_id]["tasks"][task_id]["status"] = task_status.get("status")
            self.active_swarms[swarm_id]["tasks"][task_id]["last_checked"] = time.time()
        
        return task_status
    
    def get_workflow_result(self, swarm_id: str, task_id: str) -> Dict[str, Any]:
        """
        Get the result of a completed workflow execution.
        
        Args:
            swarm_id: ID of the swarm that executed the workflow
            task_id: ID of the workflow task
            
        Returns:
            Dict containing the workflow result
        """
        # Get the task result
        task_result = self.client.get_task_result(swarm_id, task_id)
        
        # Update cached status
        if swarm_id in self.active_swarms and task_id in self.active_swarms[swarm_id]["tasks"]:
            self.active_swarms[swarm_id]["tasks"][task_id]["status"] = "completed"
            self.active_swarms[swarm_id]["tasks"][task_id]["completed_at"] = time.time()
        
        return task_result
    
    def cleanup_swarm(self, swarm_id: str) -> Dict[str, Any]:
        """
        Clean up a swarm after use.
        
        Args:
            swarm_id: ID of the swarm to clean up
            
        Returns:
            Dict containing the cleanup result
        """
        # Delete the swarm
        delete_result = self.client.delete_swarm(swarm_id)
        
        # Remove from cache
        if swarm_id in self.active_swarms:
            del self.active_swarms[swarm_id]
        
        return delete_result
    
    def _wait_for_task_result(self, swarm_id: str, task_id: str, timeout: int) -> Dict[str, Any]:
        """Wait for a task to complete and return the result."""
        start_time = time.time()
        poll_interval = 2  # seconds
        
        while time.time() - start_time < timeout:
            # Get task status
            status = self.get_workflow_status(swarm_id, task_id)
            
            if status.get("status") == "completed":
                # Task is complete, get the result
                return self.get_workflow_result(swarm_id, task_id)
            
            elif status.get("status") == "failed":
                # Task failed
                return {"error": "Task failed", "details": status}
            
            # Wait before polling again
            time.sleep(poll_interval)
            
            # Increase poll interval gradually to avoid too many requests
            poll_interval = min(poll_interval * 1.5, 10)
        
        # Timeout reached
        return {"error": "Timeout waiting for task result", "swarm_id": swarm_id, "task_id": task_id}
    
    def _monitor_task_async(self, swarm_id: str, task_id: str, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Monitor a task asynchronously and call the callback when complete."""
        import threading
        
        def monitor_thread():
            result = self._wait_for_task_result(swarm_id, task_id, self.config.get("default_timeout", 600))
            callback(task_id, result)
        
        thread = threading.Thread(target=monitor_thread)
        thread.daemon = True
        thread.start()


class SwarmWorkflowAdapter:
    """Adapter for integrating OpenAI Swarm with the workflow system."""
    
    def __init__(self, swarm_service: SwarmOrchestrationService):
        """
        Initialize the Swarm Workflow Adapter.
        
        Args:
            swarm_service: SwarmOrchestrationService instance
        """
        self.swarm_service = swarm_service
        self.active_workflows = {}
    
    def execute_workflow(
        self, 
        workflow: WorkflowDefinition,
        initial_state: WorkflowState,
        context: Dict[str, Any]
    ) -> str:
        """
        Execute a workflow using a swarm of agents.
        
        Args:
            workflow: Workflow definition to execute
            initial_state: Initial state of the workflow
            context: Context for the workflow execution
            
        Returns:
            Workflow execution ID
        """
        # Generate a workflow execution ID
        execution_id = str(uuid.uuid4())
        
        # Store initial workflow state
        self.active_workflows[execution_id] = {
            "workflow": workflow,
            "state": initial_state,
            "context": context,
            "status": "initializing",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Prepare callback for workflow updates
        def workflow_update_callback(task_id: str, result: Dict[str, Any]):
            self._handle_workflow_update(execution_id, task_id, result)
        
        # Execute the workflow
        execution_result = self.swarm_service.execute_workflow(
            workflow=workflow,
            context={
                "initial_state": initial_state.to_dict(),
                "user_context": context,
                "execution_id": execution_id
            },
            callback=workflow_update_callback
        )
        
        # Update workflow status
        self.active_workflows[execution_id]["status"] = "running"
        self.active_workflows[execution_id]["swarm_id"] = execution_result.get("swarm_id")
        self.active_workflows[execution_id]["task_id"] = execution_result.get("task_id")
        self.active_workflows[execution_id]["updated_at"] = time.time()
        
        return execution_id
    
    def get_workflow_state(self, execution_id: str) -> Optional[WorkflowState]:
        """
        Get the current state of a workflow execution.
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            Current workflow state or None if not found
        """
        if execution_id not in self.active_workflows:
            return None
        
        return self.active_workflows[execution_id]["state"]
    
    def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution.
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            Dict containing the workflow status
        """
        if execution_id not in self.active_workflows:
            return {"error": "Workflow execution not found", "execution_id": execution_id}
        
        workflow_info = self.active_workflows[execution_id]
        
        # If the workflow is running, get the latest status from the swarm
        if workflow_info["status"] == "running" and "swarm_id" in workflow_info and "task_id" in workflow_info:
            swarm_status = self.swarm_service.get_workflow_status(
                workflow_info["swarm_id"],
                workflow_info["task_id"]
            )
            
            # Update cached status if needed
            if swarm_status.get("status") != workflow_info["status"]:
                workflow_info["status"] = swarm_status.get("status", workflow_info["status"])
                workflow_info["updated_at"] = time.time()
        
        return {
            "execution_id": execution_id,
            "workflow_name": workflow_info["workflow"].name,
            "status": workflow_info["status"],
            "created_at": workflow_info["created_at"],
            "updated_at": workflow_info["updated_at"],
            "current_state": workflow_info["state"].to_dict() if workflow_info["state"] else None
        }
    
    def _handle_workflow_update(self, execution_id: str, task_id: str, result: Dict[str, Any]) -> None:
        """Handle updates from workflow execution."""
        if execution_id not in self.active_workflows:
            logger.warning(f"Received update for unknown workflow execution: {execution_id}")
            return
        
        workflow_info = self.active_workflows[execution_id]
        
        # Check for errors
        if "error" in result:
            workflow_info["status"] = "failed"
            workflow_info["error"] = result["error"]
            workflow_info["updated_at"] = time.time()
            return
        
        # Update workflow state
        if "state" in result:
            try:
                new_state = WorkflowState.from_dict(result["state"])
                workflow_info["state"] = new_state
            except Exception as e:
                logger.error(f"Error updating workflow state: {str(e)}")
        
        # Update workflow status
        workflow_info["status"] = result.get("status", "completed")
        workflow_info["result"] = result.get("result")
        workflow_info["updated_at"] = time.time()
        
        # Clean up swarm if workflow is complete
        if workflow_info["status"] in ["completed", "failed"] and "swarm_id" in workflow_info:
            try:
                self.swarm_service.cleanup_swarm(workflow_info["swarm_id"])
            except Exception as e:
                logger.warning(f"Error cleaning up swarm: {str(e)}")
