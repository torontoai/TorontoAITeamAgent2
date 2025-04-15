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

"""Project Manager Models

This module defines the data models used by the Project Manager agent."""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
import datetime
import uuid
from dataclasses import dataclass, field


class ProjectStatus(str, Enum):
    """Project status enum."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    """Task status enum."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Task priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StakeholderRole(str, Enum):
    """Stakeholder role enum."""
    SPONSOR = "sponsor"
    CLIENT = "client"
    END_USER = "end_user"
    SUBJECT_MATTER_EXPERT = "subject_matter_expert"
    REGULATOR = "regulator"
    TEAM_LEAD = "team_lead"


class TeamMemberRole(str, Enum):
    """Team member role enum."""
    PROJECT_MANAGER = "project_manager"
    BUSINESS_ANALYST = "business_analyst"
    DATA_SCIENTIST = "data_scientist"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    QA_ENGINEER = "qa_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    TECHNICAL_WRITER = "technical_writer"


class RiskSeverity(str, Enum):
    """Risk severity enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskProbability(str, Enum):
    """Risk probability enum."""
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    VERY_LIKELY = "very_likely"


class DecisionStatus(str, Enum):
    """Decision status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


@dataclass
class Project:
    """Project data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    owner_id: Optional[str] = None
    team_members: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "owner_id": self.owner_id,
            "team_members": self.team_members,
            "stakeholders": self.stakeholders,
            "tasks": self.tasks,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create from dictionary."""
        project = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=ProjectStatus(data.get("status", ProjectStatus.PLANNING.value)),
            owner_id=data.get("owner_id"),
            team_members=data.get("team_members", []),
            stakeholders=data.get("stakeholders", []),
            tasks=data.get("tasks", []),
            metadata=data.get("metadata", {})
        )
        
        # Handle dates
        if data.get("start_date"):
            project.start_date = datetime.datetime.fromisoformat(data["start_date"])
        if data.get("end_date"):
            project.end_date = datetime.datetime.fromisoformat(data["end_date"])
        if data.get("created_at"):
            project.created_at = datetime.datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            project.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
            
        return project


@dataclass
class Task:
    """Task data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    name: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: Optional[str] = None
    due_date: Optional[datetime.datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assignee_id": self.assignee_id,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create from dictionary."""
        task = cls(
            id=data.get("id", str(uuid.uuid4())),
            project_id=data.get("project_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", TaskStatus.TODO.value)),
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            assignee_id=data.get("assignee_id"),
            estimated_hours=data.get("estimated_hours"),
            actual_hours=data.get("actual_hours"),
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {})
        )
        
        # Handle dates
        if data.get("due_date"):
            task.due_date = datetime.datetime.fromisoformat(data["due_date"])
        if data.get("created_at"):
            task.created_at = datetime.datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            task.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
            
        return task


@dataclass
class TeamMember:
    """Team member data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: Optional[str] = None
    role: TeamMemberRole = TeamMemberRole.DEVELOPER
    is_ai: bool = False
    skills: List[str] = field(default_factory=list)
    availability: Dict[str, Any] = field(default_factory=dict)
    projects: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "is_ai": self.is_ai,
            "skills": self.skills,
            "availability": self.availability,
            "projects": self.projects,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamMember':
        """Create from dictionary."""
        team_member = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            email=data.get("email"),
            role=TeamMemberRole(data.get("role", TeamMemberRole.DEVELOPER.value)),
            is_ai=data.get("is_ai", False),
            skills=data.get("skills", []),
            availability=data.get("availability", {}),
            projects=data.get("projects", []),
            metadata=data.get("metadata", {})
        )
        
        # Handle dates
        if data.get("created_at"):
            team_member.created_at = datetime.datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            team_member.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
            
        return team_member


@dataclass
class Stakeholder:
    """Stakeholder data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: Optional[str] = None
    role: StakeholderRole = StakeholderRole.CLIENT
    organization: Optional[str] = None
    projects: List[str] = field(default_factory=list)
    communication_preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "organization": self.organization,
            "projects": self.projects,
            "communication_preferences": self.communication_preferences,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stakeholder':
        """Create from dictionary."""
        stakeholder = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            email=data.get("email"),
            role=StakeholderRole(data.get("role", StakeholderRole.CLIENT.value)),
            organization=data.get("organization"),
            projects=data.get("projects", []),
            communication_preferences=data.get("communication_preferences", {}),
            metadata=data.get("metadata", {})
        )
        
        # Handle dates
        if data.get("created_at"):
            stakeholder.created_at = datetime.datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            stakeholder.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
            
        return stakeholder


@dataclass
class MeetingRecord:
    """Meeting record data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    title: str = ""
    date: datetime.datetime = field(default_factory=datetime.datetime.now)
    duration_minutes: int = 0
    attendees: List[str] = field(default_factory=list)
    agenda: List[str] = field(default_factory=list)
    notes: str = ""
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "date": self.date.isoformat(),
            "duration_minutes": self.duration_minutes,
            "attendees": self.attendees,
            "agenda": self.agenda,
            "notes": self.notes,
            "action_items": self.action_items,
            "decisions": self.decisions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeetingRecord':
        """Create from dictionary."""
        meeting = cls(
            id=data.get("id", str(uuid.uuid4())),
            project_id=data.get("project_id", ""),
            title=data.get("title", ""),
            duration_minutes=data.get("duration_minutes", 0),
            attendees=data.get("attendees", []),
            agenda=data.get("agenda", []),
            notes=data.get("notes", ""),
            action_items=data.get("action_items", []),
            decisions=data.get("decisions", []),
            metadata=data.get("metadata", {})
        )
        
        # Handle dates
        if data.get("date"):
            meeting.date = datetime.datetime.fromisoformat(data["date"])
        if data.get("created_at"):
            meeting.created_at = datetime.datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            meeting.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
            
        return meeting


@dataclass
class RiskAssessment:
    """Risk assessment data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    name: str = ""
    description: str = ""
    severity: RiskSeverity = RiskSeverity.MEDIUM
    probability: RiskProbability = RiskProbability.POSSIBLE
    impact_areas: List[str] = field(default_factory=list)
    mitigation_strategy: str = ""
    contingency_plan: str = ""
    owner_id: Optional[str] = None
    status: str = "active"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "probability": self.probability.value,
            "impact_areas": self.impact_areas,
            "mitigation_strategy": self.mitigation_strategy,
            "contingency_plan": self.contingency_plan,
            "owner_id": self.owner_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RiskAssessment':
        """Create from dictionary."""
        risk = cls(
            id=data.get("id", str(uuid.uuid4())),
            project_id=data.get("project_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            severity=RiskSeverity(data.get("severity", RiskSeverity.MEDIUM.value)),
            probability=RiskProbability(data.get("probability", RiskProbability.POSSIBLE.value)),
            impact_areas=data.get("impact_areas", []),
            mitigation_strategy=data.get("mitigation_strategy", ""),
            contingency_plan=data.get("contingency_plan", ""),
            owner_id=data.get("owner_id"),
            status=data.get("status", "active"),
            metadata=data.get("metadata", {})
        )
        
        # Handle dates
        if data.get("created_at"):
            risk.created_at = datetime.datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            risk.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
            
        return risk


@dataclass
class DecisionRecord:
    """Decision record data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    title: str = ""
    description: str = ""
    context: str = ""
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    decision: str = ""
    rationale: str = ""
    consequences: str = ""
    status: DecisionStatus = DecisionStatus.PENDING
    stakeholders: List[str] = field(default_factory=list)
    date: datetime.datetime = field(default_factory=datetime.datetime.now)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "alternatives": self.alternatives,
            "decision": self.decision,
            "rationale": self.rationale,
            "consequences": self.consequences,
            "status": self.status.value,
            "stakeholders": self.stakeholders,
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionRecord':
        """Create from dictionary."""
        decision = cls(
            id=data.get("id", str(uuid.uuid4())),
            project_id=data.get("project_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            context=data.get("context", ""),
            alternatives=data.get("alternatives", []),
            decision=data.get("decision", ""),
            rationale=data.get("rationale", ""),
            consequences=data.get("consequences", ""),
            status=DecisionStatus(data.get("status", DecisionStatus.PENDING.value)),
            stakeholders=data.get("stakeholders", []),
            metadata=data.get("metadata", {})
        )
        
        # Handle dates
        if data.get("date"):
            decision.date = datetime.datetime.fromisoformat(data["date"])
        if data.get("created_at"):
            decision.created_at = datetime.datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            decision.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
            
        return decision
