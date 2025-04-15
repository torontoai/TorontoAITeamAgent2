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

"""Project Manager Agent - Main Entry Point

This module serves as the main entry point for the Project Manager agent,
integrating all the specialized components into a cohesive interface."""

from typing import Dict, Any, List, Optional, Tuple
import logging
import asyncio
import datetime
import json
import uuid
from collections import defaultdict

from ..base_agent import BaseAgent
from .models import (
    Project,
    Task,
    TeamMember,
    Stakeholder,
    ProjectStatus,
    TaskStatus,
    MeetingRecord,
    DecisionRecord,
    RiskAssessment
)
from .services.task_management import TaskManagementService
from .services.team_coordination import TeamCoordinationService
from .services.stakeholder_communication import StakeholderCommunicationService
from .services.risk_management import RiskManagementService
from .services.decision_making import DecisionMakingService
from .services.reporting import ReportingService

logger = logging.getLogger(__name__)

class ProjectManagerAgent(BaseAgent):
    """Enhanced Project Manager Agent with leadership capabilities.
    
    This agent is responsible for coordinating the team, managing projects,
    communicating with human stakeholders, and ensuring successful delivery."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Project Manager agent.
        
        Args:
            config: Configuration settings"""
        super().__init__(config)
        self.config = config or {}
        
        # Initialize services
        self.task_management = TaskManagementService(self.config.get('task_management', {}))
        self.team_coordination = TeamCoordinationService(self.config.get('team_coordination', {}))
        self.stakeholder_communication = StakeholderCommunicationService(self.config.get('stakeholder_communication', {}))
        self.risk_management = RiskManagementService(self.config.get('risk_management', {}))
        self.decision_making = DecisionMakingService(self.config.get('decision_making', {}))
        self.reporting = ReportingService(self.config.get('reporting', {}))
        
        # Initialize state
        self.projects = {}
        self.active_project_id = None
        
        logger.info("Project Manager agent initialized")
    
    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        """
        Create a new project.
        
        Args:
            project_data: Project data
            
        Returns:
            Created project
        """
        logger.info(f"Creating project: {project_data.get('name')}")
        return await self.task_management.create_project(project_data)
    
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
        return await self.task_management.update_project(project_id, project_data)
    
    async def get_project(self, project_id: str) -> Project:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project
        """
        logger.info(f"Getting project: {project_id}")
        return await self.task_management.get_project(project_id)
    
    async def list_projects(self) -> List[Project]:
        """
        List all projects.
        
        Returns:
            List of projects
        """
        logger.info("Listing all projects")
        return await self.task_management.list_projects()
    
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
        return await self.task_management.create_task(project_id, task_data)
    
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
        return await self.task_management.update_task(task_id, task_data)
    
    async def get_task(self, task_id: str) -> Task:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task
        """
        logger.info(f"Getting task: {task_id}")
        return await self.task_management.get_task(task_id)
    
    async def list_tasks(self, project_id: str) -> List[Task]:
        """
        List all tasks in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of tasks
        """
        logger.info(f"Listing all tasks in project: {project_id}")
        return await self.task_management.list_tasks(project_id)
    
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
        return await self.team_coordination.assign_task(task_id, team_member_id)
    
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
        return await self.team_coordination.add_team_member(project_id, team_member_data)
    
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
        return await self.team_coordination.remove_team_member(project_id, team_member_id)
    
    async def list_team_members(self, project_id: str) -> List[TeamMember]:
        """
        List all team members in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of team members
        """
        logger.info(f"Listing all team members in project: {project_id}")
        return await self.team_coordination.list_team_members(project_id)
    
    async def add_stakeholder(self, project_id: str, stakeholder_data: Dict[str, Any]) -> Stakeholder:
        """
        Add a stakeholder to a project.
        
        Args:
            project_id: Project ID
            stakeholder_data: Stakeholder data
            
        Returns:
            Added stakeholder
        """
        logger.info(f"Adding stakeholder to project {project_id}: {stakeholder_data.get('name')}")
        return await self.stakeholder_communication.add_stakeholder(project_id, stakeholder_data)
    
    async def remove_stakeholder(self, project_id: str, stakeholder_id: str) -> bool:
        """
        Remove a stakeholder from a project.
        
        Args:
            project_id: Project ID
            stakeholder_id: Stakeholder ID
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Removing stakeholder {stakeholder_id} from project {project_id}")
        return await self.stakeholder_communication.remove_stakeholder(project_id, stakeholder_id)
    
    async def list_stakeholders(self, project_id: str) -> List[Stakeholder]:
        """
        List all stakeholders in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of stakeholders
        """
        logger.info(f"Listing all stakeholders in project: {project_id}")
        return await self.stakeholder_communication.list_stakeholders(project_id)
    
    async def send_stakeholder_update(self, project_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Send an update to project stakeholders.
        
        Args:
            project_id: Project ID
            update_data: Update data
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Sending update to stakeholders for project: {project_id}")
        return await self.stakeholder_communication.send_update(project_id, update_data)
    
    async def record_meeting(self, project_id: str, meeting_data: Dict[str, Any]) -> MeetingRecord:
        """
        Record a project meeting.
        
        Args:
            project_id: Project ID
            meeting_data: Meeting data
            
        Returns:
            Meeting record
        """
        logger.info(f"Recording meeting for project: {project_id}")
        return await self.stakeholder_communication.record_meeting(project_id, meeting_data)
    
    async def list_meetings(self, project_id: str) -> List[MeetingRecord]:
        """
        List all meetings for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of meeting records
        """
        logger.info(f"Listing all meetings for project: {project_id}")
        return await self.stakeholder_communication.list_meetings(project_id)
    
    async def assess_risk(self, project_id: str, risk_data: Dict[str, Any]) -> RiskAssessment:
        """
        Assess a risk for a project.
        
        Args:
            project_id: Project ID
            risk_data: Risk data
            
        Returns:
            Risk assessment
        """
        logger.info(f"Assessing risk for project: {project_id}")
        return await self.risk_management.assess_risk(project_id, risk_data)
    
    async def list_risks(self, project_id: str) -> List[RiskAssessment]:
        """
        List all risks for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of risk assessments
        """
        logger.info(f"Listing all risks for project: {project_id}")
        return await self.risk_management.list_risks(project_id)
    
    async def make_decision(self, project_id: str, decision_data: Dict[str, Any]) -> DecisionRecord:
        """
        Make a decision for a project.
        
        Args:
            project_id: Project ID
            decision_data: Decision data
            
        Returns:
            Decision record
        """
        logger.info(f"Making decision for project: {project_id}")
        return await self.decision_making.make_decision(project_id, decision_data)
    
    async def list_decisions(self, project_id: str) -> List[DecisionRecord]:
        """
        List all decisions for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of decision records
        """
        logger.info(f"Listing all decisions for project: {project_id}")
        return await self.decision_making.list_decisions(project_id)
    
    async def generate_report(self, project_id: str, report_type: str) -> Dict[str, Any]:
        """
        Generate a report for a project.
        
        Args:
            project_id: Project ID
            report_type: Report type
            
        Returns:
            Generated report
        """
        logger.info(f"Generating {report_type} report for project: {project_id}")
        return await self.reporting.generate_report(project_id, report_type)
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message.
        
        Args:
            message: Message data
            
        Returns:
            Response message
        """
        logger.info(f"Processing message: {message.get('type')}")
        
        message_type = message.get('type')
        
        if message_type == 'project_create':
            project = await self.create_project(message.get('data', {}))
            return {'type': 'project_created', 'data': project.to_dict()}
        
        elif message_type == 'project_update':
            project = await self.update_project(message.get('project_id'), message.get('data', {}))
            return {'type': 'project_updated', 'data': project.to_dict()}
        
        elif message_type == 'project_get':
            project = await self.get_project(message.get('project_id'))
            return {'type': 'project_data', 'data': project.to_dict()}
        
        elif message_type == 'project_list':
            projects = await self.list_projects()
            return {'type': 'project_list', 'data': [p.to_dict() for p in projects]}
        
        elif message_type == 'task_create':
            task = await self.create_task(message.get('project_id'), message.get('data', {}))
            return {'type': 'task_created', 'data': task.to_dict()}
        
        elif message_type == 'task_update':
            task = await self.update_task(message.get('task_id'), message.get('data', {}))
            return {'type': 'task_updated', 'data': task.to_dict()}
        
        elif message_type == 'task_get':
            task = await self.get_task(message.get('task_id'))
            return {'type': 'task_data', 'data': task.to_dict()}
        
        elif message_type == 'task_list':
            tasks = await self.list_tasks(message.get('project_id'))
            return {'type': 'task_list', 'data': [t.to_dict() for t in tasks]}
        
        elif message_type == 'task_assign':
            task = await self.assign_task(message.get('task_id'), message.get('team_member_id'))
            return {'type': 'task_assigned', 'data': task.to_dict()}
        
        elif message_type == 'team_member_add':
            team_member = await self.add_team_member(message.get('project_id'), message.get('data', {}))
            return {'type': 'team_member_added', 'data': team_member.to_dict()}
        
        elif message_type == 'team_member_remove':
            success = await self.remove_team_member(message.get('project_id'), message.get('team_member_id'))
            return {'type': 'team_member_removed', 'success': success}
        
        elif message_type == 'team_member_list':
            team_members = await self.list_team_members(message.get('project_id'))
            return {'type': 'team_member_list', 'data': [tm.to_dict() for tm in team_members]}
        
        elif message_type == 'stakeholder_add':
            stakeholder = await self.add_stakeholder(message.get('project_id'), message.get('data', {}))
            return {'type': 'stakeholder_added', 'data': stakeholder.to_dict()}
        
        elif message_type == 'stakeholder_remove':
            success = await self.remove_stakeholder(message.get('project_id'), message.get('stakeholder_id'))
            return {'type': 'stakeholder_removed', 'success': success}
        
        elif message_type == 'stakeholder_list':
            stakeholders = await self.list_stakeholders(message.get('project_id'))
            return {'type': 'stakeholder_list', 'data': [s.to_dict() for s in stakeholders]}
        
        elif message_type == 'stakeholder_update_send':
            success = await self.send_stakeholder_update(message.get('project_id'), message.get('data', {}))
            return {'type': 'stakeholder_update_sent', 'success': success}
        
        elif message_type == 'meeting_record':
            meeting = await self.record_meeting(message.get('project_id'), message.get('data', {}))
            return {'type': 'meeting_recorded', 'data': meeting.to_dict()}
        
        elif message_type == 'meeting_list':
            meetings = await self.list_meetings(message.get('project_id'))
            return {'type': 'meeting_list', 'data': [m.to_dict() for m in meetings]}
        
        elif message_type == 'risk_assess':
            risk = await self.assess_risk(message.get('project_id'), message.get('data', {}))
            return {'type': 'risk_assessed', 'data': risk.to_dict()}
        
        elif message_type == 'risk_list':
            risks = await self.list_risks(message.get('project_id'))
            return {'type': 'risk_list', 'data': [r.to_dict() for r in risks]}
        
        elif message_type == 'decision_make':
            decision = await self.make_decision(message.get('project_id'), message.get('data', {}))
            return {'type': 'decision_made', 'data': decision.to_dict()}
        
        elif message_type == 'decision_list':
            decisions = await self.list_decisions(message.get('project_id'))
            return {'type': 'decision_list', 'data': [d.to_dict() for d in decisions]}
        
        elif message_type == 'report_generate':
            report = await self.generate_report(message.get('project_id'), message.get('report_type'))
            return {'type': 'report_generated', 'data': report}
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
            return {'type': 'error', 'message': f"Unknown message type: {message_type}"}
