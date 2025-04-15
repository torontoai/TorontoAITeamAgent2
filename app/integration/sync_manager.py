"""TORONTO AI TEAM AGENT - Synchronization Manager for Jira and Confluence

This module provides synchronization mechanisms for keeping entities in sync between
TORONTO AI TEAM AGENT and Jira/Confluence platforms.

Copyright (c) 2025 TORONTO AI
Created by David Tadeusz Chudak
All rights reserved."""

import logging
import sqlite3
import json
import time
import threading
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from queue import Queue, PriorityQueue
import uuid

from .config import JiraConfig, ConfluenceConfig, IntegrationConfig
from .jira_client import JiraApiClient
from .confluence_client import ConfluenceApiClient
from .models import (
    EntityType, SyncDirection, SyncStatus, SyncRecord, SyncEntity,
    JiraProject, JiraIssue, JiraComment, JiraAttachment, JiraWorklog,
    ConfluenceSpace, ConfluencePage, ConfluenceComment, ConfluenceAttachment,
    SyncEntityType
)


logger = logging.getLogger(__name__)


class SyncError(Exception):
    """Exception raised for synchronization errors."""
    pass


class SynchronizationDatabase:
    """Database for storing synchronization state and history.
    Uses SQLite for persistence."""
    
    def __init__(self, db_path: str):
        """Initialize the synchronization database.
        
        Args:
            db_path: Path to the SQLite database file"""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create entities table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            external_id TEXT,
            internal_id TEXT,
            sync_direction TEXT NOT NULL,
            last_sync_time TEXT,
            sync_status TEXT NOT NULL,
            sync_error TEXT,
            version INTEGER NOT NULL,
            metadata TEXT,
            data TEXT NOT NULL
        )
        ''')
        
        # Create sync_records table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_records (
            id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            external_id TEXT,
            internal_id TEXT,
            sync_direction TEXT NOT NULL,
            sync_time TEXT NOT NULL,
            sync_status TEXT NOT NULL,
            sync_error TEXT,
            changes TEXT,
            metadata TEXT,
            FOREIGN KEY (entity_id) REFERENCES entities (id)
        )
        ''')
        
        # Create indices for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_external_id ON entities (external_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_internal_id ON entities (internal_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_entity_type ON entities (entity_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_sync_status ON entities (sync_status)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_records_entity_id ON sync_records (entity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_records_external_id ON sync_records (external_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_records_internal_id ON sync_records (internal_id)')
        
        conn.commit()
        conn.close()
    
    def save_entity(self, entity: SyncEntity) -> None:
        """Save an entity to the database.
        
        Args:
            entity: The entity to save"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert entity to JSON for storage
        entity_data = json.dumps(self._entity_to_dict(entity))
        metadata = json.dumps(entity.metadata) if entity.metadata else '{}'
        
        # Check if entity already exists
        cursor.execute('SELECT id FROM entities WHERE id = ?', (entity.id,))
        exists = cursor.fetchone() is not None
        
        if exists:
            # Update existing entity
            cursor.execute('''
            UPDATE entities SET
                entity_type = ?,
                external_id = ?,
                internal_id = ?,
                sync_direction = ?,
                last_sync_time = ?,
                sync_status = ?,
                sync_error = ?,
                version = ?,
                metadata = ?,
                data = ?
            WHERE id = ?
            ''', (
                entity.entity_type.value,
                entity.external_id,
                entity.internal_id,
                entity.sync_direction.value,
                entity.last_sync_time.isoformat() if entity.last_sync_time else None,
                entity.sync_status.value,
                entity.sync_error,
                entity.version,
                metadata,
                entity_data,
                entity.id
            ))
        else:
            # Insert new entity
            cursor.execute('''
            INSERT INTO entities (
                id, entity_type, external_id, internal_id, sync_direction,
                last_sync_time, sync_status, sync_error, version, metadata, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entity.id,
                entity.entity_type.value,
                entity.external_id,
                entity.internal_id,
                entity.sync_direction.value,
                entity.last_sync_time.isoformat() if entity.last_sync_time else None,
                entity.sync_status.value,
                entity.sync_error,
                entity.version,
                metadata,
                entity_data
            ))
        
        conn.commit()
        conn.close()
    
    def get_entity(self, entity_id: str) -> Optional[SyncEntity]:
        """Get an entity by ID.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            The entity if found, None otherwise"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT data FROM entities WHERE id = ?', (entity_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            entity_data = json.loads(result[0])
            return self._dict_to_entity(entity_data)
        
        return None
    
    def get_entity_by_external_id(self, entity_type: EntityType, external_id: str) -> Optional[SyncEntity]:
        """Get an entity by external ID.
        
        Args:
            entity_type: The entity type
            external_id: The external ID
            
        Returns:
            The entity if found, None otherwise"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT data FROM entities WHERE entity_type = ? AND external_id = ?',
            (entity_type.value, external_id)
        )
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            entity_data = json.loads(result[0])
            return self._dict_to_entity(entity_data)
        
        return None
    
    def get_entity_by_internal_id(self, entity_type: EntityType, internal_id: str) -> Optional[SyncEntity]:
        """Get an entity by internal ID.
        
        Args:
            entity_type: The entity type
            internal_id: The internal ID
            
        Returns:
            The entity if found, None otherwise"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT data FROM entities WHERE entity_type = ? AND internal_id = ?',
            (entity_type.value, internal_id)
        )
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            entity_data = json.loads(result[0])
            return self._dict_to_entity(entity_data)
        
        return None
    
    def get_entities_by_status(self, status: SyncStatus) -> List[SyncEntity]:
        """Get entities by sync status.
        
        Args:
            status: The sync status
            
        Returns:
            List of entities with the specified status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT data FROM entities WHERE sync_status = ?', (status.value,))
        results = cursor.fetchall()
        
        conn.close()
        
        entities = []
        for result in results:
            entity_data = json.loads(result[0])
            entity = self._dict_to_entity(entity_data)
            if entity:
                entities.append(entity)
        
        return entities
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[SyncEntity]:
        """Get entities by type.
        
        Args:
            entity_type: The entity type
            
        Returns:
            List of entities of the specified type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT data FROM entities WHERE entity_type = ?', (entity_type.value,))
        results = cursor.fetchall()
        
        conn.close()
        
        entities = []
        for result in results:
            entity_data = json.loads(result[0])
            entity = self._dict_to_entity(entity_data)
            if entity:
                entities.append(entity)
        
        return entities
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity by ID.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            True if the entity was deleted, False otherwise"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM entities WHERE id = ?', (entity_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def save_sync_record(self, record: SyncRecord) -> None:
        """Save a sync record to the database.
        
        Args:
            record: The sync record to save"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        changes = json.dumps(record.changes) if record.changes else '{}'
        metadata = json.dumps(record.metadata) if record.metadata else '{}'
        
        cursor.execute('''
        INSERT INTO sync_records (
            id, entity_id, entity_type, external_id, internal_id,
            sync_direction, sync_time, sync_status, sync_error, changes, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.id,
            record.entity_id,
            record.entity_type.value,
            record.external_id,
            record.internal_id,
            record.sync_direction.value,
            record.sync_time.isoformat(),
            record.sync_status.value,
            record.sync_error,
            changes,
            metadata
        ))
        
        conn.commit()
        conn.close()
    
    def get_sync_records(self, entity_id: str) -> List[SyncRecord]:
        """Get sync records for an entity.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            List of sync records for the entity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, entity_id, entity_type, external_id, internal_id,
               sync_direction, sync_time, sync_status, sync_error, changes, metadata
        FROM sync_records
        WHERE entity_id = ?
        ORDER BY sync_time DESC
        ''', (entity_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        records = []
        for result in results:
            record = SyncRecord(
                id=result[0],
                entity_id=result[1],
                entity_type=EntityType(result[2]),
                external_id=result[3],
                internal_id=result[4],
                sync_direction=SyncDirection(result[5]),
                sync_time=datetime.fromisoformat(result[6]),
                sync_status=SyncStatus(result[7]),
                sync_error=result[8],
                changes=json.loads(result[9]) if result[9] else {},
                metadata=json.loads(result[10]) if result[10] else {}
            )
            records.append(record)
        
        return records
    
    def _entity_to_dict(self, entity: SyncEntity) -> Dict[str, Any]:
        """Convert an entity to a dictionary for storage.
        
        Args:
            entity: The entity to convert
            
        Returns:
            Dictionary representation of the entity"""
        # Base entity data
        data = {
            "id": entity.id,
            "entity_type": entity.entity_type.value,
            "external_id": entity.external_id,
            "internal_id": entity.internal_id,
            "sync_direction": entity.sync_direction.value,
            "last_sync_time": entity.last_sync_time.isoformat() if entity.last_sync_time else None,
            "sync_status": entity.sync_status.value,
            "sync_error": entity.sync_error,
            "version": entity.version,
            "metadata": entity.metadata,
            "class": entity.__class__.__name__
        }
        
        # Add entity-specific fields
        if isinstance(entity, JiraProject):
            data.update({
                "key": entity.key,
                "name": entity.name,
                "description": entity.description,
                "lead": entity.lead,
                "url": entity.url,
                "project_type": entity.project_type,
                "project_category": entity.project_category,
                "issues": entity.issues
            })
        elif isinstance(entity, JiraIssue):
            data.update({
                "key": entity.key,
                "project_id": entity.project_id,
                "summary": entity.summary,
                "description": entity.description,
                "issue_type": entity.issue_type,
                "status": entity.status,
                "priority": entity.priority,
                "assignee": entity.assignee,
                "reporter": entity.reporter,
                "created": entity.created.isoformat() if entity.created else None,
                "updated": entity.updated.isoformat() if entity.updated else None,
                "due_date": entity.due_date.isoformat() if entity.due_date else None,
                "resolution": entity.resolution,
                "labels": entity.labels,
                "components": entity.components,
                "comments": entity.comments,
                "attachments": entity.attachments,
                "worklogs": entity.worklogs,
                "custom_fields": entity.custom_fields
            })
        elif isinstance(entity, JiraComment):
            data.update({
                "issue_id": entity.issue_id,
                "author": entity.author,
                "body": entity.body,
                "created": entity.created.isoformat() if entity.created else None,
                "updated": entity.updated.isoformat() if entity.updated else None
            })
        elif isinstance(entity, JiraAttachment):
            data.update({
                "issue_id": entity.issue_id,
                "filename": entity.filename,
                "content_type": entity.content_type,
                "size": entity.size,
                "author": entity.author,
                "created": entity.created.isoformat() if entity.created else None,
                "url": entity.url
                # Note: content is not stored in the database
            })
        elif isinstance(entity, JiraWorklog):
            data.update({
                "issue_id": entity.issue_id,
                "author": entity.author,
                "comment": entity.comment,
                "started": entity.started.isoformat() if entity.started else None,
                "time_spent_seconds": entity.time_spent_seconds
            })
        elif isinstance(entity, ConfluenceSpace):
            data.update({
                "key": entity.key,
                "name": entity.name,
                "description": entity.description,
                "type": entity.type,
                "status": entity.status,
                "homepage_id": entity.homepage_id,
                "pages": entity.pages
            })
        elif isinstance(entity, ConfluencePage):
            data.update({
                "space_id": entity.space_id,
                "title": entity.title,
                "body": entity.body,
                "version": entity.version,
                "parent_id": entity.parent_id,
                "creator": entity.creator,
                "created": entity.created.isoformat() if entity.created else None,
                "last_updater": entity.last_updater,
                "last_updated": entity.last_updated.isoformat() if entity.last_updated else None,
                "status": entity.status,
                "comments": entity.comments,
                "attachments": entity.attachments,
                "labels": entity.labels
            })
        elif isinstance(entity, ConfluenceComment):
            data.update({
                "page_id": entity.page_id,
                "author": entity.author,
                "body": entity.body,
                "created": entity.created.isoformat() if entity.created else None,
                "updated": entity.updated.isoformat() if entity.updated else None,
                "parent_comment_id": entity.parent_comment_id
            })
        elif isinstance(entity, ConfluenceAttachment):
            data.update({
                "page_id": entity.page_id,
                "filename": entity.filename,
                "content_type": entity.content_type,
                "size": entity.size,
                "creator": entity.creator,
                "created": entity.created.isoformat() if entity.created else None,
                "url": entity.url
                # Note: content is not stored in the database
            })
        
        return data
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> Optional[SyncEntity]:
        """Convert a dictionary to an entity.
        
        Args:
            data: Dictionary representation of the entity
            
        Returns:
            The entity, or None if conversion fails"""
        try:
            entity_type = EntityType(data.get("entity_type"))
            entity_class = data.get("class")
            
            # Parse common fields
            common_args = {
                "id": data.get("id"),
                "entity_type": entity_type,
                "external_id": data.get("external_id"),
                "internal_id": data.get("internal_id"),
                "sync_direction": SyncDirection(data.get("sync_direction")),
                "sync_status": SyncStatus(data.get("sync_status")),
                "sync_error": data.get("sync_error"),
                "version": data.get("version", 1),
                "metadata": data.get("metadata", {})
            }
            
            # Parse last_sync_time if present
            if data.get("last_sync_time"):
                common_args["last_sync_time"] = datetime.fromisoformat(data.get("last_sync_time"))
            
            # Create entity based on class
            if entity_class == "JiraProject":
                return JiraProject(
                    **common_args,
                    key=data.get("key", ""),
                    name=data.get("name", ""),
                    description=data.get("description", ""),
                    lead=data.get("lead", ""),
                    url=data.get("url", ""),
                    project_type=data.get("project_type", ""),
                    project_category=data.get("project_category"),
                    issues=data.get("issues", [])
                )
            elif entity_class == "JiraIssue":
                issue = JiraIssue(
                    **common_args,
                    key=data.get("key", ""),
                    project_id=data.get("project_id", ""),
                    summary=data.get("summary", ""),
                    description=data.get("description", ""),
                    issue_type=data.get("issue_type", ""),
                    status=data.get("status", ""),
                    priority=data.get("priority"),
                    assignee=data.get("assignee"),
                    reporter=data.get("reporter"),
                    resolution=data.get("resolution"),
                    labels=data.get("labels", []),
                    components=data.get("components", []),
                    comments=data.get("comments", []),
                    attachments=data.get("attachments", []),
                    worklogs=data.get("worklogs", []),
                    custom_fields=data.get("custom_fields", {})
                )
                
                # Parse dates if present
                if data.get("created"):
                    issue.created = datetime.fromisoformat(data.get("created"))
                if data.get("updated"):
                    issue.updated = datetime.fromisoformat(data.get("updated"))
                if data.get("due_date"):
                    issue.due_date = datetime.fromisoformat(data.get("due_date"))
                
                return issue
            elif entity_class == "JiraComment":
                comment = JiraComment(
                    **common_args,
                    issue_id=data.get("issue_id", ""),
                    author=data.get("author", ""),
                    body=data.get("body", "")
                )
                
                # Parse dates if present
                if data.get("created"):
                    comment.created = datetime.fromisoformat(data.get("created"))
                if data.get("updated"):
                    comment.updated = datetime.fromisoformat(data.get("updated"))
                
                return comment
            elif entity_class == "JiraAttachment":
                attachment = JiraAttachment(
                    **common_args,
                    issue_id=data.get("issue_id", ""),
                    filename=data.get("filename", ""),
                    content_type=data.get("content_type", ""),
                    size=data.get("size", 0),
                    author=data.get("author", ""),
                    url=data.get("url", "")
                )
                
                # Parse dates if present
                if data.get("created"):
                    attachment.created = datetime.fromisoformat(data.get("created"))
                
                return attachment
            elif entity_class == "JiraWorklog":
                worklog = JiraWorklog(
                    **common_args,
                    issue_id=data.get("issue_id", ""),
                    author=data.get("author", ""),
                    comment=data.get("comment", ""),
                    time_spent_seconds=data.get("time_spent_seconds", 0)
                )
                
                # Parse dates if present
                if data.get("started"):
                    worklog.started = datetime.fromisoformat(data.get("started"))
                
                return worklog
            elif entity_class == "ConfluenceSpace":
                return ConfluenceSpace(
                    **common_args,
                    key=data.get("key", ""),
                    name=data.get("name", ""),
                    description=data.get("description", ""),
                    type=data.get("type", ""),
                    status=data.get("status", ""),
                    homepage_id=data.get("homepage_id"),
                    pages=data.get("pages", [])
                )
            elif entity_class == "ConfluencePage":
                page = ConfluencePage(
                    **common_args,
                    space_id=data.get("space_id", ""),
                    title=data.get("title", ""),
                    body=data.get("body", ""),
                    version=data.get("version", 1),
                    parent_id=data.get("parent_id"),
                    creator=data.get("creator", ""),
                    last_updater=data.get("last_updater", ""),
                    status=data.get("status", ""),
                    comments=data.get("comments", []),
                    attachments=data.get("attachments", []),
                    labels=data.get("labels", [])
                )
                
                # Parse dates if present
                if data.get("created"):
                    page.created = datetime.fromisoformat(data.get("created"))
                if data.get("last_updated"):
                    page.last_updated = datetime.fromisoformat(data.get("last_updated"))
                
                return page
            elif entity_class == "ConfluenceComment":
                comment = ConfluenceComment(
                    **common_args,
                    page_id=data.get("page_id", ""),
                    author=data.get("author", ""),
                    body=data.get("body", ""),
                    parent_comment_id=data.get("parent_comment_id")
                )
                
                # Parse dates if present
                if data.get("created"):
                    comment.created = datetime.fromisoformat(data.get("created"))
                if data.get("updated"):
                    comment.updated = datetime.fromisoformat(data.get("updated"))
                
                return comment
            elif entity_class == "ConfluenceAttachment":
                attachment = ConfluenceAttachment(
                    **common_args,
                    page_id=data.get("page_id", ""),
                    filename=data.get("filename", ""),
                    content_type=data.get("content_type", ""),
                    size=data.get("size", 0),
                    creator=data.get("creator", ""),
                    url=data.get("url", "")
                )
                
                # Parse dates if present
                if data.get("created"):
                    attachment.created = datetime.fromisoformat(data.get("created"))
                
                return attachment
            
            # Unknown entity class
            logger.warning(f"Unknown entity class: {entity_class}")
            return None
            
        except Exception as e:
            logger.error(f"Error converting dictionary to entity: {str(e)}")
            return None


class SynchronizationManager:
    """Manager for synchronizing entities between TORONTO AI TEAM AGENT and Jira/Confluence.
    Handles scheduling, conflict resolution, and error handling."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize the synchronization manager.
        
        Args:
            config: Integration configuration"""
        self.config = config
        self.db = SynchronizationDatabase(config.sync_database_path)
        
        # Initialize API clients if enabled
        self.jira_client = None
        self.confluence_client = None
        
        if config.jira and config.jira in config.enabled_integrations:
            self.jira_client = JiraApiClient(config.jira)
        
        if config.confluence and config.confluence in config.enabled_integrations:
            self.confluence_client = ConfluenceApiClient(config.confluence)
        
        # Initialize synchronization queue
        self.sync_queue = PriorityQueue()
        
        # Initialize worker thread
        self.worker_thread = None
        self.stop_event = threading.Event()
    
    def start(self) -> None:
        """Start the synchronization manager."""
        if self.worker_thread and self.worker_thread.is_alive():
            logger.warning("Synchronization manager is already running")
            return
        
        self.stop_event.clear()
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        logger.info("Synchronization manager started")
    
    def stop(self) -> None:
        """Stop the synchronization manager."""
        if not self.worker_thread or not self.worker_thread.is_alive():
            logger.warning("Synchronization manager is not running")
            return
        
        self.stop_event.set()
        self.worker_thread.join(timeout=30)
        
        if self.worker_thread.is_alive():
            logger.warning("Synchronization manager worker thread did not stop gracefully")
        else:
            logger.info("Synchronization manager stopped")
    
    def queue_entity_for_sync(
        self, 
        entity: SyncEntity, 
        priority: int = 1,
        force: bool = False
    ) -> None:
        """Queue an entity for synchronization.
        
        Args:
            entity: The entity to synchronize
            priority: Priority level (lower values have higher priority)
            force: Whether to force synchronization even if already in progress"""
        # Check if entity is already in progress
        if not force and entity.sync_status == SyncStatus.IN_PROGRESS:
            logger.warning(f"Entity {entity.id} is already being synchronized")
            return
        
        # Update entity status
        entity.sync_status = SyncStatus.PENDING
        self.db.save_entity(entity)
        
        # Add to queue with priority
        self.sync_queue.put((priority, entity.id))
        
        logger.info(f"Queued entity {entity.id} for synchronization with priority {priority}")
    
    def queue_entity_by_id(
        self, 
        entity_id: str, 
        priority: int = 1,
        force: bool = False
    ) -> bool:
        """Queue an entity for synchronization by ID.
        
        Args:
            entity_id: The entity ID
            priority: Priority level (lower values have higher priority)
            force: Whether to force synchronization even if already in progress
            
        Returns:
            True if the entity was queued, False otherwise"""
        entity = self.db.get_entity(entity_id)
        if not entity:
            logger.warning(f"Entity {entity_id} not found")
            return False
        
        self.queue_entity_for_sync(entity, priority, force)
        return True
    
    def queue_entity_by_external_id(
        self, 
        entity_type: EntityType, 
        external_id: str, 
        priority: int = 1,
        force: bool = False
    ) -> bool:
        """Queue an entity for synchronization by external ID.
        
        Args:
            entity_type: The entity type
            external_id: The external ID
            priority: Priority level (lower values have higher priority)
            force: Whether to force synchronization even if already in progress
            
        Returns:
            True if the entity was queued, False otherwise"""
        entity = self.db.get_entity_by_external_id(entity_type, external_id)
        if not entity:
            logger.warning(f"Entity with external ID {external_id} not found")
            return False
        
        self.queue_entity_for_sync(entity, priority, force)
        return True
    
    def queue_entity_by_internal_id(
        self, 
        entity_type: EntityType, 
        internal_id: str, 
        priority: int = 1,
        force: bool = False
    ) -> bool:
        """Queue an entity for synchronization by internal ID.
        
        Args:
            entity_type: The entity type
            internal_id: The internal ID
            priority: Priority level (lower values have higher priority)
            force: Whether to force synchronization even if already in progress
            
        Returns:
            True if the entity was queued, False otherwise"""
        entity = self.db.get_entity_by_internal_id(entity_type, internal_id)
        if not entity:
            logger.warning(f"Entity with internal ID {internal_id} not found")
            return False
        
        self.queue_entity_for_sync(entity, priority, force)
        return True
    
    def queue_all_pending_entities(self) -> int:
        """Queue all entities with PENDING status for synchronization.
        
        Returns:
            Number of entities queued"""
        entities = self.db.get_entities_by_status(SyncStatus.PENDING)
        count = 0
        
        for entity in entities:
            self.sync_queue.put((1, entity.id))
            count += 1
        
        logger.info(f"Queued {count} pending entities for synchronization")
        return count
    
    def queue_all_entities_by_type(self, entity_type: EntityType, priority: int = 1) -> int:
        """Queue all entities of a specific type for synchronization.
        
        Args:
            entity_type: The entity type
            priority: Priority level (lower values have higher priority)
            
        Returns:
            Number of entities queued"""
        entities = self.db.get_entities_by_type(entity_type)
        count = 0
        
        for entity in entities:
            if entity.sync_status != SyncStatus.IN_PROGRESS:
                entity.sync_status = SyncStatus.PENDING
                self.db.save_entity(entity)
                self.sync_queue.put((priority, entity.id))
                count += 1
        
        logger.info(f"Queued {count} entities of type {entity_type.value} for synchronization")
        return count
    
    def _worker_loop(self) -> None:
        """Worker loop for processing the synchronization queue."""
        logger.info("Synchronization worker thread started")
        
        while not self.stop_event.is_set():
            try:
                # Get next entity from queue with 1-second timeout
                try:
                    priority, entity_id = self.sync_queue.get(timeout=1)
                except Queue.Empty:
                    continue
                
                # Get entity from database
                entity = self.db.get_entity(entity_id)
                if not entity:
                    logger.warning(f"Entity {entity_id} not found in database")
                    self.sync_queue.task_done()
                    continue
                
                # Skip if entity is already being processed
                if entity.sync_status == SyncStatus.IN_PROGRESS:
                    logger.warning(f"Entity {entity_id} is already being processed")
                    self.sync_queue.task_done()
                    continue
                
                # Update entity status
                entity.sync_status = SyncStatus.IN_PROGRESS
                self.db.save_entity(entity)
                
                # Process entity
                try:
                    logger.info(f"Processing entity {entity_id} of type {entity.entity_type.value}")
                    self._synchronize_entity(entity)
                    
                    # Update entity status
                    entity.sync_status = SyncStatus.COMPLETED
                    entity.last_sync_time = datetime.now()
                    entity.sync_error = None
                    self.db.save_entity(entity)
                    
                    logger.info(f"Successfully synchronized entity {entity_id}")
                    
                except Exception as e:
                    logger.error(f"Error synchronizing entity {entity_id}: {str(e)}")
                    
                    # Update entity status
                    entity.sync_status = SyncStatus.FAILED
                    entity.last_sync_time = datetime.now()
                    entity.sync_error = str(e)
                    self.db.save_entity(entity)
                
                # Mark task as done
                self.sync_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in synchronization worker: {str(e)}")
                # Continue processing
        
        logger.info("Synchronization worker thread stopped")
    
    def _synchronize_entity(self, entity: SyncEntity) -> None:
        """Synchronize an entity between TORONTO AI TEAM AGENT and Jira/Confluence.
        
        Args:
            entity: The entity to synchronize
            
        Raises:
            SyncError: If synchronization fails"""
        # Check if the required client is available
        if entity.entity_type in (
            EntityType.JIRA_PROJECT, EntityType.JIRA_ISSUE, 
            EntityType.JIRA_COMMENT, EntityType.JIRA_ATTACHMENT, 
            EntityType.JIRA_WORKLOG
        ):
            if not self.jira_client:
                raise SyncError("Jira client is not available")
        elif entity.entity_type in (
            EntityType.CONFLUENCE_SPACE, EntityType.CONFLUENCE_PAGE,
            EntityType.CONFLUENCE_COMMENT, EntityType.CONFLUENCE_ATTACHMENT
        ):
            if not self.confluence_client:
                raise SyncError("Confluence client is not available")
        
        # Determine synchronization direction
        if entity.sync_direction == SyncDirection.TO_EXTERNAL:
            self._sync_to_external(entity)
        elif entity.sync_direction == SyncDirection.FROM_EXTERNAL:
            self._sync_from_external(entity)
        elif entity.sync_direction == SyncDirection.BIDIRECTIONAL:
            # For bidirectional sync, we need to check which side has changed
            # This is a simplified approach - real implementation would be more complex
            if entity.external_id and not entity.internal_id:
                # Entity exists externally but not internally
                self._sync_from_external(entity)
            elif entity.internal_id and not entity.external_id:
                # Entity exists internally but not externally
                self._sync_to_external(entity)
            else:
                # Entity exists on both sides, need to determine which has changed
                # For now, we'll just sync from external to internal
                self._sync_from_external(entity)
        else:
            raise SyncError(f"Unknown sync direction: {entity.sync_direction}")
    
    def _sync_to_external(self, entity: SyncEntity) -> None:
        """Synchronize an entity from TORONTO AI TEAM AGENT to Jira/Confluence.
        
        Args:
            entity: The entity to synchronize
            
        Raises:
            SyncError: If synchronization fails"""
        # This is a simplified implementation - real implementation would be more complex
        if entity.entity_type == EntityType.JIRA_PROJECT:
            self._sync_jira_project_to_external(entity)
        elif entity.entity_type == EntityType.JIRA_ISSUE:
            self._sync_jira_issue_to_external(entity)
        elif entity.entity_type == EntityType.JIRA_COMMENT:
            self._sync_jira_comment_to_external(entity)
        elif entity.entity_type == EntityType.JIRA_ATTACHMENT:
            self._sync_jira_attachment_to_external(entity)
        elif entity.entity_type == EntityType.JIRA_WORKLOG:
            self._sync_jira_worklog_to_external(entity)
        elif entity.entity_type == EntityType.CONFLUENCE_SPACE:
            self._sync_confluence_space_to_external(entity)
        elif entity.entity_type == EntityType.CONFLUENCE_PAGE:
            self._sync_confluence_page_to_external(entity)
        elif entity.entity_type == EntityType.CONFLUENCE_COMMENT:
            self._sync_confluence_comment_to_external(entity)
        elif entity.entity_type == EntityType.CONFLUENCE_ATTACHMENT:
            self._sync_confluence_attachment_to_external(entity)
        else:
            raise SyncError(f"Unsupported entity type for external sync: {entity.entity_type}")
    
    def _sync_from_external(self, entity: SyncEntity) -> None:
        """Synchronize an entity from Jira/Confluence to TORONTO AI TEAM AGENT.
        
        Args:
            entity: The entity to synchronize
            
        Raises:
            SyncError: If synchronization fails"""
        # This is a simplified implementation - real implementation would be more complex
        if entity.entity_type == EntityType.JIRA_PROJECT:
            self._sync_jira_project_from_external(entity)
        elif entity.entity_type == EntityType.JIRA_ISSUE:
            self._sync_jira_issue_from_external(entity)
        elif entity.entity_type == EntityType.JIRA_COMMENT:
            self._sync_jira_comment_from_external(entity)
        elif entity.entity_type == EntityType.JIRA_ATTACHMENT:
            self._sync_jira_attachment_from_external(entity)
        elif entity.entity_type == EntityType.JIRA_WORKLOG:
            self._sync_jira_worklog_from_external(entity)
        elif entity.entity_type == EntityType.CONFLUENCE_SPACE:
            self._sync_confluence_space_from_external(entity)
        elif entity.entity_type == EntityType.CONFLUENCE_PAGE:
            self._sync_confluence_page_from_external(entity)
        elif entity.entity_type == EntityType.CONFLUENCE_COMMENT:
            self._sync_confluence_comment_from_external(entity)
        elif entity.entity_type == EntityType.CONFLUENCE_ATTACHMENT:
            self._sync_confluence_attachment_from_external(entity)
        else:
            raise SyncError(f"Unsupported entity type for external sync: {entity.entity_type}")
    
    # Implementation of specific sync methods would go here
    # These are placeholders for the actual implementation
    
    def _sync_jira_project_to_external(self, entity: JiraProject) -> None:
        """Sync a Jira project to Jira."""
        if not self.jira_client:
            raise SyncError("Jira client is not available")
        
        # Convert to Jira API format
        project_data = self.jira_client.convert_to_jira_project(entity)
        
        # Create or update project
        if entity.external_id:
            # Update existing project
            # Note: Jira doesn't support direct project updates via API
            # This would require special handling
            raise SyncError("Updating existing Jira projects is not supported via API")
        else:
            # Create new project
            response = self.jira_client.create_project(project_data)
            
            # Update entity with external ID
            entity.external_id = response.get("id")
            entity.key = response.get("key")
            entity.url = response.get("self")
    
    def _sync_jira_project_from_external(self, entity: JiraProject) -> None:
        """Sync a Jira project from Jira."""
        if not self.jira_client:
            raise SyncError("Jira client is not available")
        
        # Get project from Jira
        if entity.external_id:
            # Get by ID
            # Note: Jira API doesn't support getting projects by ID directly
            # We would need to get all projects and filter
            raise SyncError("Getting Jira projects by ID is not supported")
        elif entity.key:
            # Get by key
            response = self.jira_client.get_project(entity.key)
            
            # Update entity with data from Jira
            updated_entity = self.jira_client.convert_from_jira_project(response)
            
            # Copy updated fields to entity
            entity.name = updated_entity.name
            entity.description = updated_entity.description
            entity.lead = updated_entity.lead
            entity.url = updated_entity.url
            entity.project_type = updated_entity.project_type
            entity.project_category = updated_entity.project_category
            entity.external_id = updated_entity.external_id
        else:
            raise SyncError("Cannot sync Jira project without external ID or key")
    
    def _sync_jira_issue_to_external(self, entity: JiraIssue) -> None:
        """Sync a Jira issue to Jira."""
        if not self.jira_client:
            raise SyncError("Jira client is not available")
        
        # Convert to Jira API format
        issue_data = self.jira_client.convert_to_jira_issue(entity)
        
        # Create or update issue
        if entity.external_id or entity.key:
            # Update existing issue
            key = entity.key or entity.external_id
            response = self.jira_client.update_issue(key, issue_data)
            
            # Update entity with data from response
            updated_entity = self.jira_client.convert_from_jira_issue(response)
            
            # Copy updated fields to entity
            entity.key = updated_entity.key
            entity.status = updated_entity.status
            entity.updated = updated_entity.updated
            entity.version = entity.version + 1
        else:
            # Create new issue
            response = self.jira_client.create_issue(issue_data)
            
            # Update entity with external ID and key
            entity.external_id = response.get("id")
            entity.key = response.get("key")
    
    def _sync_jira_issue_from_external(self, entity: JiraIssue) -> None:
        """Sync a Jira issue from Jira."""
        if not self.jira_client:
            raise SyncError("Jira client is not available")
        
        # Get issue from Jira
        if entity.external_id or entity.key:
            # Get by ID or key
            key = entity.key or entity.external_id
            response = self.jira_client.get_issue(key)
            
            # Update entity with data from Jira
            updated_entity = self.jira_client.convert_from_jira_issue(response)
            
            # Copy updated fields to entity
            entity.key = updated_entity.key
            entity.project_id = updated_entity.project_id
            entity.summary = updated_entity.summary
            entity.description = updated_entity.description
            entity.issue_type = updated_entity.issue_type
            entity.status = updated_entity.status
            entity.priority = updated_entity.priority
            entity.assignee = updated_entity.assignee
            entity.reporter = updated_entity.reporter
            entity.created = updated_entity.created
            entity.updated = updated_entity.updated
            entity.due_date = updated_entity.due_date
            entity.resolution = updated_entity.resolution
            entity.labels = updated_entity.labels
            entity.components = updated_entity.components
            entity.custom_fields = updated_entity.custom_fields
            entity.external_id = updated_entity.external_id
            entity.version = entity.version + 1
        else:
            raise SyncError("Cannot sync Jira issue without external ID or key")
    
    # Additional sync methods would be implemented similarly
    
    def _sync_jira_comment_to_external(self, entity: JiraComment) -> None:
        """Placeholder for syncing a Jira comment to Jira."""
        pass
    
    def _sync_jira_comment_from_external(self, entity: JiraComment) -> None:
        """Placeholder for syncing a Jira comment from Jira."""
        pass
    
    def _sync_jira_attachment_to_external(self, entity: JiraAttachment) -> None:
        """Placeholder for syncing a Jira attachment to Jira."""
        pass
    
    def _sync_jira_attachment_from_external(self, entity: JiraAttachment) -> None:
        """Placeholder for syncing a Jira attachment from Jira."""
        pass
    
    def _sync_jira_worklog_to_external(self, entity: JiraWorklog) -> None:
        """Placeholder for syncing a Jira worklog to Jira."""
        pass
    
    def _sync_jira_worklog_from_external(self, entity: JiraWorklog) -> None:
        """Placeholder for syncing a Jira worklog from Jira."""
        pass
    
    def _sync_confluence_space_to_external(self, entity: ConfluenceSpace) -> None:
        """Placeholder for syncing a Confluence space to Confluence."""
        pass
    
    def _sync_confluence_space_from_external(self, entity: ConfluenceSpace) -> None:
        """Placeholder for syncing a Confluence space from Confluence."""
        pass
    
    def _sync_confluence_page_to_external(self, entity: ConfluencePage) -> None:
        """Placeholder for syncing a Confluence page to Confluence."""
        pass
    
    def _sync_confluence_page_from_external(self, entity: ConfluencePage) -> None:
        """Placeholder for syncing a Confluence page from Confluence."""
        pass
    
    def _sync_confluence_comment_to_external(self, entity: ConfluenceComment) -> None:
        """Placeholder for syncing a Confluence comment to Confluence."""
        pass
    
    def _sync_confluence_comment_from_external(self, entity: ConfluenceComment) -> None:
        """Placeholder for syncing a Confluence comment from Confluence."""
        pass
    
    def _sync_confluence_attachment_to_external(self, entity: ConfluenceAttachment) -> None:
        """Placeholder for syncing a Confluence attachment to Confluence."""
        pass
    
    def _sync_confluence_attachment_from_external(self, entity: ConfluenceAttachment) -> None:
        """Placeholder for syncing a Confluence attachment from Confluence."""
        pass
