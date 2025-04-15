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

"""Team Coordination Service for Project Manager Agent.

This module provides services for coordinating team members and task assignments."""

import logging
import asyncio
import datetime
from typing import Dict, Any, List, Optional, Union

from ..models import TeamMember, Task, Project

logger = logging.getLogger(__name__)

class TeamCoordinationService:
    """Service for coordinating team members and task assignments."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the team coordination service.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        self.team_members = {}  # In-memory storage for team members
        self.task_service = None  # Will be set by dependency injection
        self.project_service = None  # Will be set by dependency injection
        logger.info("Team coordination service initialized")
    
    def set_task_service(self, task_service):
        """Set task service reference."""
        self.task_service = task_service
    
    def set_project_service(self, project_service):
        """Set project service reference."""
        self.project_service = project_service
    
    async def add_team_member(self, project_id: str, team_member_data: Dict[str, Any]) -> TeamMember:
        """
        Add a team member to a project.
        
        Args:
            project_id: Project ID
            team_member_data: Team member data
            
        Returns:
            Added team member
        """
        logger.info(f"Adding team member to project {project_id}: {team_member_data.get('name')}")
        
        # Create team member from data
        team_member = TeamMember.from_dict(team_member_data)
        
        # Add project to team member's projects
        if project_id not in team_member.projects:
            team_member.projects.append(project_id)
        
        # Store team member
        self.team_members[team_member.id] = team_member
        
        # Update project if we have access to the project service
        if self.task_service:
            try:
                project = await self.task_service.get_project(project_id)
                if team_member.id not in project.team_members:
                    project.team_members.append(team_member.id)
                    project.updated_at = datetime.datetime.now()
                    await self.task_service.update_project(project_id, {"team_members": project.team_members})
            except Exception as e:
                logger.error(f"Error updating project: {e}")
        
        logger.info(f"Team member added: {team_member.id}")
        return team_member
    
    async def remove_team_member(self, project_id: str, team_member_id: str) -> bool:
        """
        Remove a team member from a project.
        
        Args:
            project_id: Project ID
            team_member_id: Team member ID
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Removing team member {team_member_id} from project {project_id}")
        
        # Check if team member exists
        if team_member_id not in self.team_members:
            raise ValueError(f"Team member not found: {team_member_id}")
        
        # Get team member
        team_member = self.team_members[team_member_id]
        
        # Remove project from team member's projects
        if project_id in team_member.projects:
            team_member.projects.remove(project_id)
            team_member.updated_at = datetime.datetime.now()
        
        # Update project if we have access to the project service
        if self.task_service:
            try:
                project = await self.task_service.get_project(project_id)
                if team_member_id in project.team_members:
                    project.team_members.remove(team_member_id)
                    project.updated_at = datetime.datetime.now()
                    await self.task_service.update_project(project_id, {"team_members": project.team_members})
            except Exception as e:
                logger.error(f"Error updating project: {e}")
        
        # If team member has no more projects, consider removing them
        if not team_member.projects:
            logger.info(f"Team member {team_member_id} has no more projects, considering removal")
            # For now, we'll keep them in the system
        
        logger.info(f"Team member removed from project: {team_member_id}")
        return True
    
    async def get_team_member(self, team_member_id: str) -> TeamMember:
        """
        Get a team member by ID.
        
        Args:
            team_member_id: Team member ID
            
        Returns:
            Team member
        """
        logger.info(f"Getting team member: {team_member_id}")
        
        # Check if team member exists
        if team_member_id not in self.team_members:
            raise ValueError(f"Team member not found: {team_member_id}")
        
        return self.team_members[team_member_id]
    
    async def list_team_members(self, project_id: str) -> List[TeamMember]:
        """
        List all team members in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of team members
        """
        logger.info(f"Listing all team members in project: {project_id}")
        
        # Get project if we have access to the project service
        project_team_members = []
        if self.task_service:
            try:
                project = await self.task_service.get_project(project_id)
                project_team_members = project.team_members
            except Exception as e:
                logger.error(f"Error getting project: {e}")
                # Fall back to filtering team members by project
        
        # If we have project team members, get those specific team members
        if project_team_members:
            return [self.team_members[tm_id] for tm_id in project_team_members if tm_id in self.team_members]
        
        # Otherwise, filter team members by project
        return [tm for tm in self.team_members.values() if project_id in tm.projects]
    
    async def assign_task(self, task_id: str, team_member_id: str) -> Task:
        """
        Assign a task to a team member.
        
        Args:
            task_id: Task ID
            team_member_id: Team member ID
            
        Returns:
            Updated task
        """
        logger.info(f"Assigning task {task_id} to team member {team_member_id}")
        
        # Check if team member exists
        if team_member_id not in self.team_members:
            raise ValueError(f"Team member not found: {team_member_id}")
        
        # Update task if we have access to the task service
        if self.task_service:
            try:
                task = await self.task_service.get_task(task_id)
                task_data = {"assignee_id": team_member_id}
                updated_task = await self.task_service.update_task(task_id, task_data)
                logger.info(f"Task assigned: {task_id} to {team_member_id}")
                return updated_task
            except Exception as e:
                logger.error(f"Error assigning task: {e}")
                raise
        else:
            raise ValueError("Task service not available")
    
    async def unassign_task(self, task_id: str) -> Task:
        """
        Unassign a task from its current assignee.
        
        Args:
            task_id: Task ID
            
        Returns:
            Updated task
        """
        logger.info(f"Unassigning task: {task_id}")
        
        # Update task if we have access to the task service
        if self.task_service:
            try:
                task = await self.task_service.get_task(task_id)
                task_data = {"assignee_id": None}
                updated_task = await self.task_service.update_task(task_id, task_data)
                logger.info(f"Task unassigned: {task_id}")
                return updated_task
            except Exception as e:
                logger.error(f"Error unassigning task: {e}")
                raise
        else:
            raise ValueError("Task service not available")
    
    async def get_team_member_tasks(self, team_member_id: str) -> List[Task]:
        """
        Get all tasks assigned to a team member.
        
        Args:
            team_member_id: Team member ID
            
        Returns:
            List of tasks
        """
        logger.info(f"Getting tasks for team member: {team_member_id}")
        
        # Check if team member exists
        if team_member_id not in self.team_members:
            raise ValueError(f"Team member not found: {team_member_id}")
        
        # Get team member's tasks if we have access to the task service
        if self.task_service:
            try:
                # Get all tasks and filter by assignee
                team_member = self.team_members[team_member_id]
                tasks = []
                
                # For each project the team member is part of
                for project_id in team_member.projects:
                    project_tasks = await self.task_service.list_tasks(project_id)
                    # Filter tasks assigned to this team member
                    team_member_tasks = [task for task in project_tasks if task.assignee_id == team_member_id]
                    tasks.extend(team_member_tasks)
                
                return tasks
            except Exception as e:
                logger.error(f"Error getting team member tasks: {e}")
                raise
        else:
            raise ValueError("Task service not available")
    
    async def update_team_member(self, team_member_id: str, team_member_data: Dict[str, Any]) -> TeamMember:
        """
        Update a team member.
        
        Args:
            team_member_id: Team member ID
            team_member_data: Updated team member data
            
        Returns:
            Updated team member
        """
        logger.info(f"Updating team member: {team_member_id}")
        
        # Check if team member exists
        if team_member_id not in self.team_members:
            raise ValueError(f"Team member not found: {team_member_id}")
        
        # Get existing team member
        team_member = self.team_members[team_member_id]
        
        # Update team member fields
        for key, value in team_member_data.items():
            if key == 'id':
                continue  # Don't update ID
            elif hasattr(team_member, key):
                setattr(team_member, key, value)
        
        # Update timestamp
        team_member.updated_at = datetime.datetime.now()
        
        # Store updated team member
        self.team_members[team_member_id] = team_member
        
        logger.info(f"Team member updated: {team_member_id}")
        return team_member
    
    async def get_team_workload(self, project_id: str) -> Dict[str, Any]:
        """
        Get workload distribution for team members in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Workload distribution data
        """
        logger.info(f"Getting team workload for project: {project_id}")
        
        # Get team members in project
        team_members = await self.list_team_members(project_id)
        
        # Get tasks for each team member
        workload = {}
        for team_member in team_members:
            try:
                tasks = await self.get_team_member_tasks(team_member.id)
                workload[team_member.id] = {
                    "team_member": team_member.to_dict(),
                    "task_count": len(tasks),
                    "tasks": [task.to_dict() for task in tasks],
                    "estimated_hours": sum(task.estimated_hours or 0 for task in tasks)
                }
            except Exception as e:
                logger.error(f"Error getting tasks for team member {team_member.id}: {e}")
                workload[team_member.id] = {
                    "team_member": team_member.to_dict(),
                    "task_count": 0,
                    "tasks": [],
                    "estimated_hours": 0,
                    "error": str(e)
                }
        
        return workload
