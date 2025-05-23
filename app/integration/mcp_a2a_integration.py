"""TORONTO AI TEAM AGENT - Integration with MCP/A2A Frameworks

This module provides integration between Jira/Confluence and the MCP/A2A frameworks.

Copyright (c) 2025 TORONTO AI
Created by David Tadeusz Chudak
All rights reserved."""

import logging
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

from ..collaboration.mcp_framework import MCPMessage, MCPAgent, MCPMessageType
from ..collaboration.a2a_framework import A2AMessage, A2AAgent, A2AMessageType
from ..collaboration.mcp_a2a_integration import IntegratedAgent

from .models import (
    EntityType, SyncDirection, SyncStatus, SyncRecord, SyncEntity,
    JiraProject, JiraIssue, JiraComment, JiraAttachment, JiraWorklog,
    ConfluenceSpace, ConfluencePage, ConfluenceComment, ConfluenceAttachment
)
from .sync_manager import SynchronizationManager


logger = logging.getLogger(__name__)


class JiraConfluenceAgent(IntegratedAgent):
    """Agent for integrating Jira and Confluence with the MCP/A2A frameworks.
    Handles communication between the frameworks and the synchronization manager."""
    
    def __init__(self, sync_manager: SynchronizationManager):
        """Initialize the Jira/Confluence agent.
        
        Args:
            sync_manager: The synchronization manager"""
        super().__init__(agent_id="jira_confluence_agent", agent_name="Jira/Confluence Integration Agent")
        self.sync_manager = sync_manager
        
        # Register message handlers
        self.register_mcp_handler(MCPMessageType.TASK_ASSIGNMENT, self._handle_mcp_task_assignment)
        self.register_mcp_handler(MCPMessageType.STATUS_REQUEST, self._handle_mcp_status_request)
        self.register_mcp_handler(MCPMessageType.KNOWLEDGE_REQUEST, self._handle_mcp_knowledge_request)
        
        self.register_a2a_handler(A2AMessageType.QUERY, self._handle_a2a_query)
        self.register_a2a_handler(A2AMessageType.UPDATE, self._handle_a2a_update)
        self.register_a2a_handler(A2AMessageType.NOTIFICATION, self._handle_a2a_notification)
    
    def start(self) -> None:
        """Start the agent and the synchronization manager."""
        self.sync_manager.start()
        logger.info("Jira/Confluence agent started")
    
    def stop(self) -> None:
        """Stop the agent and the synchronization manager."""
        self.sync_manager.stop()
        logger.info("Jira/Confluence agent stopped")
    
    def _handle_mcp_task_assignment(self, message: MCPMessage) -> None:
        """Handle task assignment messages from the MCP framework.
        
        Args:
            message: The MCP message"""
        task_data = message.content.get("task_data", {})
        task_type = task_data.get("type")
        
        if task_type == "sync_entity":
            # Handle entity synchronization task
            entity_type = task_data.get("entity_type")
            entity_id = task_data.get("entity_id")
            sync_direction = task_data.get("sync_direction", "bidirectional")
            priority = task_data.get("priority", 1)
            
            if not entity_type or not entity_id:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.TASK_STATUS,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "task_id": message.content.get("task_id"),
                            "status": "failed",
                            "error": "Missing entity_type or entity_id in task data"
                        }
                    )
                )
                return
            
            # Convert string to enum
            try:
                entity_type_enum = EntityType(entity_type)
                sync_direction_enum = SyncDirection(sync_direction)
            except ValueError as e:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.TASK_STATUS,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "task_id": message.content.get("task_id"),
                            "status": "failed",
                            "error": f"Invalid entity_type or sync_direction: {str(e)}"
                        }
                    )
                )
                return
            
            # Queue entity for synchronization
            success = self.sync_manager.queue_entity_by_id(entity_id, priority)
            
            if success:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.TASK_STATUS,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "task_id": message.content.get("task_id"),
                            "status": "in_progress",
                            "message": f"Entity {entity_id} queued for synchronization"
                        }
                    )
                )
            else:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.TASK_STATUS,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "task_id": message.content.get("task_id"),
                            "status": "failed",
                            "error": f"Failed to queue entity {entity_id} for synchronization"
                        }
                    )
                )
        
        elif task_type == "create_jira_issue":
            # Handle Jira issue creation task
            project_key = task_data.get("project_key")
            summary = task_data.get("summary")
            description = task_data.get("description")
            issue_type = task_data.get("issue_type", "Task")
            priority = task_data.get("priority")
            assignee = task_data.get("assignee")
            
            if not project_key or not summary:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.TASK_STATUS,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "task_id": message.content.get("task_id"),
                            "status": "failed",
                            "error": "Missing project_key or summary in task data"
                        }
                    )
                )
                return
            
            # Create Jira issue entity
            issue = JiraIssue(
                entity_type=EntityType.JIRA_ISSUE,
                sync_direction=SyncDirection.TO_EXTERNAL,
                sync_status=SyncStatus.PENDING,
                project_id=project_key,
                summary=summary,
                description=description or "",
                issue_type=issue_type,
                priority=priority,
                assignee=assignee
            )
            
            # Save entity and queue for synchronization
            self.sync_manager.db.save_entity(issue)
            self.sync_manager.queue_entity_for_sync(issue)
            
            self.send_mcp_message(
                MCPMessage(
                    message_type=MCPMessageType.TASK_STATUS,
                    sender=self.agent_id,
                    recipient=message.sender,
                    content={
                        "task_id": message.content.get("task_id"),
                        "status": "in_progress",
                        "message": "Jira issue creation queued",
                        "entity_id": issue.id
                    }
                )
            )
        
        elif task_type == "create_confluence_page":
            # Handle Confluence page creation task
            space_key = task_data.get("space_key")
            title = task_data.get("title")
            body = task_data.get("body")
            parent_id = task_data.get("parent_id")
            
            if not space_key or not title or not body:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.TASK_STATUS,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "task_id": message.content.get("task_id"),
                            "status": "failed",
                            "error": "Missing space_key, title, or body in task data"
                        }
                    )
                )
                return
            
            # Create Confluence page entity
            page = ConfluencePage(
                entity_type=EntityType.CONFLUENCE_PAGE,
                sync_direction=SyncDirection.TO_EXTERNAL,
                sync_status=SyncStatus.PENDING,
                space_id=space_key,
                title=title,
                body=body,
                parent_id=parent_id
            )
            
            # Save entity and queue for synchronization
            self.sync_manager.db.save_entity(page)
            self.sync_manager.queue_entity_for_sync(page)
            
            self.send_mcp_message(
                MCPMessage(
                    message_type=MCPMessageType.TASK_STATUS,
                    sender=self.agent_id,
                    recipient=message.sender,
                    content={
                        "task_id": message.content.get("task_id"),
                        "status": "in_progress",
                        "message": "Confluence page creation queued",
                        "entity_id": page.id
                    }
                )
            )
        
        else:
            # Unknown task type
            self.send_mcp_message(
                MCPMessage(
                    message_type=MCPMessageType.TASK_STATUS,
                    sender=self.agent_id,
                    recipient=message.sender,
                    content={
                        "task_id": message.content.get("task_id"),
                        "status": "failed",
                        "error": f"Unknown task type: {task_type}"
                    }
                )
            )
    
    def _handle_mcp_status_request(self, message: MCPMessage) -> None:
        """Handle status request messages from the MCP framework.
        
        Args:
            message: The MCP message"""
        request_type = message.content.get("request_type")
        
        if request_type == "entity_status":
            # Handle entity status request
            entity_id = message.content.get("entity_id")
            
            if not entity_id:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.STATUS_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": "Missing entity_id in request"
                        }
                    )
                )
                return
            
            # Get entity from database
            entity = self.sync_manager.db.get_entity(entity_id)
            
            if entity:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.STATUS_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "success",
                            "entity_id": entity_id,
                            "entity_type": entity.entity_type.value,
                            "sync_status": entity.sync_status.value,
                            "sync_direction": entity.sync_direction.value,
                            "last_sync_time": entity.last_sync_time.isoformat() if entity.last_sync_time else None,
                            "sync_error": entity.sync_error
                        }
                    )
                )
            else:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.STATUS_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": f"Entity {entity_id} not found"
                        }
                    )
                )
        
        elif request_type == "sync_queue_status":
            # Handle sync queue status request
            queue_size = self.sync_manager.sync_queue.qsize()
            
            self.send_mcp_message(
                MCPMessage(
                    message_type=MCPMessageType.STATUS_RESPONSE,
                    sender=self.agent_id,
                    recipient=message.sender,
                    content={
                        "request_id": message.content.get("request_id"),
                        "status": "success",
                        "queue_size": queue_size
                    }
                )
            )
        
        else:
            # Unknown request type
            self.send_mcp_message(
                MCPMessage(
                    message_type=MCPMessageType.STATUS_RESPONSE,
                    sender=self.agent_id,
                    recipient=message.sender,
                    content={
                        "request_id": message.content.get("request_id"),
                        "status": "error",
                        "error": f"Unknown request type: {request_type}"
                    }
                )
            )
    
    def _handle_mcp_knowledge_request(self, message: MCPMessage) -> None:
        """Handle knowledge request messages from the MCP framework.
        
        Args:
            message: The MCP message"""
        request_type = message.content.get("request_type")
        
        if request_type == "jira_projects":
            # Handle Jira projects request
            if not self.sync_manager.jira_client:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": "Jira client is not available"
                        }
                    )
                )
                return
            
            try:
                # Get projects from Jira
                projects = self.sync_manager.jira_client.get_projects()
                
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "success",
                            "projects": projects
                        }
                    )
                )
            except Exception as e:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": f"Failed to get Jira projects: {str(e)}"
                        }
                    )
                )
        
        elif request_type == "jira_issues":
            # Handle Jira issues request
            project_key = message.content.get("project_key")
            
            if not project_key:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": "Missing project_key in request"
                        }
                    )
                )
                return
            
            if not self.sync_manager.jira_client:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": "Jira client is not available"
                        }
                    )
                )
                return
            
            try:
                # Get issues from Jira
                issues = self.sync_manager.jira_client.get_issues(project_key)
                
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "success",
                            "issues": issues
                        }
                    )
                )
            except Exception as e:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": f"Failed to get Jira issues: {str(e)}"
                        }
                    )
                )
        
        elif request_type == "confluence_spaces":
            # Handle Confluence spaces request
            if not self.sync_manager.confluence_client:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": "Confluence client is not available"
                        }
                    )
                )
                return
            
            try:
                # Get spaces from Confluence
                spaces = self.sync_manager.confluence_client.get_spaces()
                
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "success",
                            "spaces": spaces
                        }
                    )
                )
            except Exception as e:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": f"Failed to get Confluence spaces: {str(e)}"
                        }
                    )
                )
        
        elif request_type == "confluence_pages":
            # Handle Confluence pages request
            space_key = message.content.get("space_key")
            
            if not space_key:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": "Missing space_key in request"
                        }
                    )
                )
                return
            
            if not self.sync_manager.confluence_client:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": "Confluence client is not available"
                        }
                    )
                )
                return
            
            try:
                # Get pages from Confluence
                pages = self.sync_manager.confluence_client.get_content(space_key, "page")
                
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "success",
                            "pages": pages
                        }
                    )
                )
            except Exception as e:
                self.send_mcp_message(
                    MCPMessage(
                        message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "request_id": message.content.get("request_id"),
                            "status": "error",
                            "error": f"Failed to get Confluence pages: {str(e)}"
                        }
                    )
                )
        
        else:
            # Unknown request type
            self.send_mcp_message(
                MCPMessage(
                    message_type=MCPMessageType.KNOWLEDGE_RESPONSE,
                    sender=self.agent_id,
                    recipient=message.sender,
                    content={
                        "request_id": message.content.get("request_id"),
                        "status": "error",
                        "error": f"Unknown request type: {request_type}"
                    }
                )
            )
    
    def _handle_a2a_query(self, message: A2AMessage) -> None:
        """Handle query messages from the A2A framework.
        
        Args:
            message: The A2A message"""
        query_type = message.content.get("query_type")
        
        if query_type == "entity_status":
            # Handle entity status query
            entity_id = message.content.get("entity_id")
            
            if not entity_id:
                self.send_a2a_message(
                    A2AMessage(
                        message_type=A2AMessageType.RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "query_id": message.content.get("query_id"),
                            "status": "error",
                            "error": "Missing entity_id in query"
                        }
                    )
                )
                return
            
            # Get entity from database
            entity = self.sync_manager.db.get_entity(entity_id)
            
            if entity:
                self.send_a2a_message(
                    A2AMessage(
                        message_type=A2AMessageType.RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "query_id": message.content.get("query_id"),
                            "status": "success",
                            "entity_id": entity_id,
                            "entity_type": entity.entity_type.value,
                            "sync_status": entity.sync_status.value,
                            "sync_direction": entity.sync_direction.value,
                            "last_sync_time": entity.last_sync_time.isoformat() if entity.last_sync_time else None,
                            "sync_error": entity.sync_error
                        }
                    )
                )
            else:
                self.send_a2a_message(
                    A2AMessage(
                        message_type=A2AMessageType.RESPONSE,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "query_id": message.content.get("query_id"),
                            "status": "error",
                            "error": f"Entity {entity_id} not found"
                        }
                    )
                )
        
        else:
            # Unknown query type
            self.send_a2a_message(
                A2AMessage(
                    message_type=A2AMessageType.RESPONSE,
                    sender=self.agent_id,
                    recipient=message.sender,
                    content={
                        "query_id": message.content.get("query_id"),
                        "status": "error",
                        "error": f"Unknown query type: {query_type}"
                    }
                )
            )
    
    def _handle_a2a_update(self, message: A2AMessage) -> None:
        """Handle update messages from the A2A framework.
        
        Args:
            message: The A2A message"""
        update_type = message.content.get("update_type")
        
        if update_type == "sync_entity":
            # Handle entity synchronization update
            entity_id = message.content.get("entity_id")
            priority = message.content.get("priority", 1)
            
            if not entity_id:
                self.send_a2a_message(
                    A2AMessage(
                        message_type=A2AMessageType.NOTIFICATION,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "update_id": message.content.get("update_id"),
                            "status": "error",
                            "error": "Missing entity_id in update"
                        }
                    )
                )
                return
            
            # Queue entity for synchronization
            success = self.sync_manager.queue_entity_by_id(entity_id, priority)
            
            if success:
                self.send_a2a_message(
                    A2AMessage(
                        message_type=A2AMessageType.NOTIFICATION,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "update_id": message.content.get("update_id"),
                            "status": "success",
                            "message": f"Entity {entity_id} queued for synchronization"
                        }
                    )
                )
            else:
                self.send_a2a_message(
                    A2AMessage(
                        message_type=A2AMessageType.NOTIFICATION,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            "update_id": message.content.get("update_id"),
                            "status": "error",
                            "error": f"Failed to queue entity {entity_id} for synchronization"
                        }
                    )
                )
        
        else:
            # Unknown update type
            self.send_a2a_message(
                A2AMessage(
                    message_type=A2AMessageType.NOTIFICATION,
                    sender=self.agent_id,
                    recipient=message.sender,
                    content={
                        "update_id": message.content.get("update_id"),
                        "status": "error",
                        "error": f"Unknown update type: {update_type}"
                    }
                )
            )
    
    def _handle_a2a_notification(self, message: A2AMessage) -> None:
        """Handle notification messages from the A2A framework.
        
        Args:
            message: The A2A message"""
        notification_type = message.content.get("notification_type")
        
        if notification_type == "entity_updated":
            # Handle entity updated notification
            entity_id = message.content.get("entity_id")
            
            if not entity_id:
                logger.warning("Received entity_updated notification without entity_id")
                return
            
            # Get entity from database
            entity = self.sync_manager.db.get_entity(entity_id)
            
            if entity:
                # Queue entity for synchronization
                self.sync_manager.queue_entity_for_sync(entity)
                logger.info(f"Queued updated entity {entity_id} for synchronization")
            else:
                logger.warning(f"Entity {entity_id} not found for entity_updated notification")
        
        elif notification_type == "sync_status_changed":
            # Handle sync status changed notification
            entity_id = message.content.get("entity_id")
            new_status = message.content.get("new_status")
            
            if not entity_id or not new_status:
                logger.warning("Received sync_status_changed notification without entity_id or new_status")
                return
            
            # Get entity from database
            entity = self.sync_manager.db.get_entity(entity_id)
            
            if entity:
                try:
                    # Update entity status
                    entity.sync_status = SyncStatus(new_status)
                    self.sync_manager.db.save_entity(entity)
                    logger.info(f"Updated entity {entity_id} status to {new_status}")
                except ValueError:
                    logger.warning(f"Invalid sync status in notification: {new_status}")
            else:
                logger.warning(f"Entity {entity_id} not found for sync_status_changed notification")
        
        # Other notification types can be handled here
