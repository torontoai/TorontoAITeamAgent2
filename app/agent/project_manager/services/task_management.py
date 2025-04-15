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

"""Task Management Service for Project Manager Agent.

This module provides services for managing tasks and projects."""

import logging
import asyncio
import datetime
from typing import Dict, Any, List, Optional, Union

from ..models import Project, Task, TaskStatus

logger = logging.getLogger(__name__)

class TaskManagementService:
    """Service for managing tasks and projects."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the task management service.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        self.projects = {}  # In-memory storage for projects
        self.tasks = {}  # In-memory storage for tasks
        logger.info("Task management service initialized")
    
    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        """
        Create a new project.
        
        Args:
            project_data: Project data
            
        Returns:
            Created project
        """
        logger.info(f"Creating project: {project_data.get('name')}")
        
        # Create project from data
        project = Project.from_dict(project_data)
        
        # Store project
        self.projects[project.id] = project
        
        logger.info(f"Project created: {project.id}")
        return project
    
    async def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Project:
        """
        Update an existing project.
        
        Args:
            project_id: Project ID
            project_data: Updated project data
            
        Returns:
            Updated project
        """
        logger.info(f"Updating project: {project_id}")
        
        # Check if project exists
        if project_id not in self.projects:
            raise ValueError(f"Project not found: {project_id}")
        
        # Get existing project
        project = self.projects[project_id]
        
        # Update project fields
        for key, value in project_data.items():
            if key == 'id':
                continue  # Don't update ID
            elif key == 'status' and value:
                project.status = value
            elif key == 'start_date' and value:
                project.start_date = datetime.datetime.fromisoformat(value) if isinstance(value, str) else value
            elif key == 'end_date' and value:
                project.end_date = datetime.datetime.fromisoformat(value) if isinstance(value, str) else value
            elif hasattr(project, key):
                setattr(project, key, value)
        
        # Update timestamp
        project.updated_at = datetime.datetime.now()
        
        # Store updated project
        self.projects[project_id] = project
        
        logger.info(f"Project updated: {project_id}")
        return project
    
    async def get_project(self, project_id: str) -> Project:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project
        """
        logger.info(f"Getting project: {project_id}")
        
        # Check if project exists
        if project_id not in self.projects:
            raise ValueError(f"Project not found: {project_id}")
        
        return self.projects[project_id]
    
    async def list_projects(self) -> List[Project]:
        """
        List all projects.
        
        Returns:
            List of projects
        """
        logger.info("Listing all projects")
        return list(self.projects.values())
    
    async def create_task(self, project_id: str, task_data: Dict[str, Any]) -> Task:
        """
        Create a new task in a project.
        
        Args:
            project_id: Project ID
            task_data: Task data
            
        Returns:
            Created task
        """
        logger.info(f"Creating task in project {project_id}: {task_data.get('name')}")
        
        # Check if project exists
        if project_id not in self.projects:
            raise ValueError(f"Project not found: {project_id}")
        
        # Create task from data
        task_data['project_id'] = project_id
        task = Task.from_dict(task_data)
        
        # Store task
        self.tasks[task.id] = task
        
        # Update project
        project = self.projects[project_id]
        project.tasks.append(task.id)
        project.updated_at = datetime.datetime.now()
        
        logger.info(f"Task created: {task.id}")
        return task
    
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Task:
        """
        Update an existing task.
        
        Args:
            task_id: Task ID
            task_data: Updated task data
            
        Returns:
            Updated task
        """
        logger.info(f"Updating task: {task_id}")
        
        # Check if task exists
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        # Get existing task
        task = self.tasks[task_id]
        
        # Update task fields
        for key, value in task_data.items():
            if key == 'id' or key == 'project_id':
                continue  # Don't update ID or project_id
            elif key == 'status' and value:
                task.status = value if isinstance(value, TaskStatus) else TaskStatus(value)
            elif key == 'due_date' and value:
                task.due_date = datetime.datetime.fromisoformat(value) if isinstance(value, str) else value
            elif hasattr(task, key):
                setattr(task, key, value)
        
        # Update timestamp
        task.updated_at = datetime.datetime.now()
        
        # Store updated task
        self.tasks[task_id] = task
        
        # Update project timestamp
        if task.project_id in self.projects:
            self.projects[task.project_id].updated_at = datetime.datetime.now()
        
        logger.info(f"Task updated: {task_id}")
        return task
    
    async def get_task(self, task_id: str) -> Task:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task
        """
        logger.info(f"Getting task: {task_id}")
        
        # Check if task exists
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        return self.tasks[task_id]
    
    async def list_tasks(self, project_id: str) -> List[Task]:
        """
        List all tasks in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of tasks
        """
        logger.info(f"Listing all tasks in project: {project_id}")
        
        # Check if project exists
        if project_id not in self.projects:
            raise ValueError(f"Project not found: {project_id}")
        
        # Get project
        project = self.projects[project_id]
        
        # Get tasks
        tasks = []
        for task_id in project.tasks:
            if task_id in self.tasks:
                tasks.append(self.tasks[task_id])
        
        return tasks
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting task: {task_id}")
        
        # Check if task exists
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        # Get task
        task = self.tasks[task_id]
        
        # Remove task from project
        if task.project_id in self.projects:
            project = self.projects[task.project_id]
            if task_id in project.tasks:
                project.tasks.remove(task_id)
                project.updated_at = datetime.datetime.now()
        
        # Delete task
        del self.tasks[task_id]
        
        logger.info(f"Task deleted: {task_id}")
        return True
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a project and all its tasks.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting project: {project_id}")
        
        # Check if project exists
        if project_id not in self.projects:
            raise ValueError(f"Project not found: {project_id}")
        
        # Get project
        project = self.projects[project_id]
        
        # Delete all tasks in project
        for task_id in project.tasks:
            if task_id in self.tasks:
                del self.tasks[task_id]
        
        # Delete project
        del self.projects[project_id]
        
        logger.info(f"Project deleted: {project_id}")
        return True
