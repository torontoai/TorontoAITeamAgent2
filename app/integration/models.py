"""TORONTO AI TEAM AGENT - Data Models for Jira and Confluence Integration

This module provides data models for synchronizing entities between TORONTO AI TEAM AGENT
and Jira/Confluence platforms.

Copyright (c) 2025 TORONTO AI
Created by David Tadeusz Chudak
All rights reserved."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import uuid


class SyncDirection(Enum):
    """Enum for synchronization direction."""
    TO_EXTERNAL = "to_external"  # TORONTO AI TEAM AGENT to Jira/Confluence
    FROM_EXTERNAL = "from_external"  # Jira/Confluence to TORONTO AI TEAM AGENT
    BIDIRECTIONAL = "bidirectional"  # Both directions


class SyncStatus(Enum):
    """Enum for synchronization status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class EntityType(Enum):
    """Enum for entity types that can be synchronized."""
    # Jira entity types
    JIRA_PROJECT = "jira_project"
    JIRA_ISSUE = "jira_issue"
    JIRA_COMMENT = "jira_comment"
    JIRA_ATTACHMENT = "jira_attachment"
    JIRA_WORKLOG = "jira_worklog"
    
    # Confluence entity types
    CONFLUENCE_SPACE = "confluence_space"
    CONFLUENCE_PAGE = "confluence_page"
    CONFLUENCE_COMMENT = "confluence_comment"
    CONFLUENCE_ATTACHMENT = "confluence_attachment"


@dataclass
class SyncEntity:
    """Base class for entities that can be synchronized."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType = None
    external_id: Optional[str] = None
    internal_id: Optional[str] = None
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    last_sync_time: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.PENDING
    sync_error: Optional[str] = None
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JiraProject(SyncEntity):
    """Model for a Jira project."""
    entity_type: EntityType = EntityType.JIRA_PROJECT
    key: str = ""
    name: str = ""
    description: str = ""
    lead: str = ""
    url: str = ""
    project_type: str = ""
    project_category: Optional[str] = None
    issues: List[str] = field(default_factory=list)  # List of issue IDs


@dataclass
class JiraIssue(SyncEntity):
    """Model for a Jira issue."""
    entity_type: EntityType = EntityType.JIRA_ISSUE
    key: str = ""
    project_id: str = ""
    summary: str = ""
    description: str = ""
    issue_type: str = ""
    status: str = ""
    priority: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    due_date: Optional[datetime] = None
    resolution: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)  # List of comment IDs
    attachments: List[str] = field(default_factory=list)  # List of attachment IDs
    worklogs: List[str] = field(default_factory=list)  # List of worklog IDs
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JiraComment(SyncEntity):
    """Model for a Jira comment."""
    entity_type: EntityType = EntityType.JIRA_COMMENT
    issue_id: str = ""
    author: str = ""
    body: str = ""
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


@dataclass
class JiraAttachment(SyncEntity):
    """Model for a Jira attachment."""
    entity_type: EntityType = EntityType.JIRA_ATTACHMENT
    issue_id: str = ""
    filename: str = ""
    content_type: str = ""
    size: int = 0
    author: str = ""
    created: Optional[datetime] = None
    content: Optional[bytes] = None
    url: str = ""


@dataclass
class JiraWorklog(SyncEntity):
    """Model for a Jira worklog."""
    entity_type: EntityType = EntityType.JIRA_WORKLOG
    issue_id: str = ""
    author: str = ""
    comment: str = ""
    started: datetime = field(default_factory=datetime.now)
    time_spent_seconds: int = 0


@dataclass
class ConfluenceSpace(SyncEntity):
    """Model for a Confluence space."""
    entity_type: EntityType = EntityType.CONFLUENCE_SPACE
    key: str = ""
    name: str = ""
    description: str = ""
    type: str = ""
    status: str = ""
    homepage_id: Optional[str] = None
    pages: List[str] = field(default_factory=list)  # List of page IDs


@dataclass
class ConfluencePage(SyncEntity):
    """Model for a Confluence page."""
    entity_type: EntityType = EntityType.CONFLUENCE_PAGE
    space_id: str = ""
    title: str = ""
    body: str = ""
    version: int = 1
    parent_id: Optional[str] = None
    creator: str = ""
    created: Optional[datetime] = None
    last_updater: str = ""
    last_updated: Optional[datetime] = None
    status: str = ""
    comments: List[str] = field(default_factory=list)  # List of comment IDs
    attachments: List[str] = field(default_factory=list)  # List of attachment IDs
    labels: List[str] = field(default_factory=list)


@dataclass
class ConfluenceComment(SyncEntity):
    """Model for a Confluence comment."""
    entity_type: EntityType = EntityType.CONFLUENCE_COMMENT
    page_id: str = ""
    author: str = ""
    body: str = ""
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    parent_comment_id: Optional[str] = None


@dataclass
class ConfluenceAttachment(SyncEntity):
    """Model for a Confluence attachment."""
    entity_type: EntityType = EntityType.CONFLUENCE_ATTACHMENT
    page_id: str = ""
    filename: str = ""
    content_type: str = ""
    size: int = 0
    creator: str = ""
    created: Optional[datetime] = None
    content: Optional[bytes] = None
    url: str = ""


@dataclass
class SyncRecord:
    """Record of a synchronization operation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str = ""
    entity_type: EntityType = None
    external_id: Optional[str] = None
    internal_id: Optional[str] = None
    sync_direction: SyncDirection = None
    sync_time: datetime = field(default_factory=datetime.now)
    sync_status: SyncStatus = None
    sync_error: Optional[str] = None
    changes: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# Type alias for any sync entity
SyncEntityType = Union[
    JiraProject, JiraIssue, JiraComment, JiraAttachment, JiraWorklog,
    ConfluenceSpace, ConfluencePage, ConfluenceComment, ConfluenceAttachment
]
