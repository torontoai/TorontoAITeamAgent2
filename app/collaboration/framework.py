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


"""Real-time Collaboration Framework for TorontoAITeamAgent.

This module provides real-time collaboration mechanisms for agents to work together
on complex tasks, enabling synchronous communication and coordination."""

from typing import Dict, Any, List, Optional, Union, Callable
import logging
import asyncio
import json
import uuid
from datetime import datetime
import time
from .communication_framework import AgentCommunicationFramework

logger = logging.getLogger(__name__)

class RealTimeCollaborationFramework:
    """Framework for real-time collaboration between agents.
    
    This framework extends the basic communication framework to enable
    real-time collaboration, synchronization, and coordination between agents."""
    
    def __init__(self, communication_framework: AgentCommunicationFramework = None):
        """Initialize the Real-time Collaboration Framework.
        
        Args:
            communication_framework: Optional existing communication framework to use"""
        self.communication_framework = communication_framework or AgentCommunicationFramework()
        self.collaboration_sessions = {}
        self.active_collaborations = {}
        self.session_callbacks = {}
        self.session_locks = {}
        
        logger.info("Real-time Collaboration Framework initialized")
    
    async def create_collaboration_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new collaboration session between agents.
        
        Args:
            params: Session parameters including:
                - name: Session name
                - description: Session description
                - participants: List of agent IDs to include
                - initiator: Agent ID that initiated the session
                - context: Collaboration context data
                - session_type: Type of collaboration session
                
        Returns:
            Session creation result
        """
        name = params.get("name", "Untitled Collaboration")
        description = params.get("description", "")
        participants = params.get("participants", [])
        initiator = params.get("initiator")
        context = params.get("context", {})
        session_type = params.get("session_type", "general")
        
        if not initiator:
            return {
                "success": False,
                "message": "Missing initiator agent ID"
            }
        
        if not participants:
            return {
                "success": False,
                "message": "At least one participant is required"
            }
        
        # Ensure initiator is in participants
        if initiator not in participants:
            participants.append(initiator)
        
        # Generate session ID
        session_id = f"collab_{uuid.uuid4().hex}"
        
        # Create session
        session = {
            "id": session_id,
            "name": name,
            "description": description,
            "participants": participants,
            "initiator": initiator,
            "context": context,
            "session_type": session_type,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "shared_state": {},
            "artifacts": []
        }
        
        # Store session
        self.collaboration_sessions[session_id] = session
        
        # Create session lock
        self.session_locks[session_id] = asyncio.Lock()
        
        # Initialize active collaborations for each participant
        for participant in participants:
            if participant not in self.active_collaborations:
                self.active_collaborations[participant] = []
            
            self.active_collaborations[participant].append(session_id)
        
        # Notify participants
        notification_tasks = []
        for participant in participants:
            if participant != initiator:  # Don't notify the initiator
                notification_tasks.append(
                    self.communication_framework.send_message({
                        "from": initiator,
                        "to": participant,
                        "content": {
                            "type": "collaboration_invitation",
                            "session_id": session_id,
                            "name": name,
                            "description": description,
                            "initiator": initiator,
                            "participants": participants,
                            "session_type": session_type
                        },
                        "pattern": "request_response",
                        "response_expected": True,
                        "metadata": {
                            "priority": "high",
                            "category": "collaboration"
                        }
                    })
                )
        
        if notification_tasks:
            await asyncio.gather(*notification_tasks)
        
        logger.info(f"Collaboration session {session_id} created by {initiator} with {len(participants)} participants")
        
        return {
            "success": True,
            "message": "Collaboration session created successfully",
            "session_id": session_id,
            "name": name,
            "participants": participants
        }
    
    async def join_collaboration_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Join an existing collaboration session.
        
        Args:
            params: Join parameters including:
                - session_id: Session ID to join
                - agent_id: Agent ID joining the session
                - metadata: Optional metadata about the agent
                
        Returns:
            Join result
        """
        session_id = params.get("session_id")
        agent_id = params.get("agent_id")
        metadata = params.get("metadata", {})
        
        if not session_id:
            return {
                "success": False,
                "message": "Missing session ID"
            }
        
        if not agent_id:
            return {
                "success": False,
                "message": "Missing agent ID"
            }
        
        # Check if session exists
        if session_id not in self.collaboration_sessions:
            return {
                "success": False,
                "message": f"Collaboration session {session_id} not found"
            }
        
        # Get session
        session = self.collaboration_sessions[session_id]
        
        # Check if session is active
        if session["status"] != "active":
            return {
                "success": False,
                "message": f"Collaboration session {session_id} is not active"
            }
        
        # Check if agent is already a participant
        if agent_id in session["participants"]:
            return {
                "success": True,
                "message": f"Agent {agent_id} is already a participant in session {session_id}",
                "session": session
            }
        
        # Add agent to participants
        async with self.session_locks[session_id]:
            session["participants"].append(agent_id)
            session["updated_at"] = datetime.now().isoformat()
        
        # Add session to agent's active collaborations
        if agent_id not in self.active_collaborations:
            self.active_collaborations[agent_id] = []
        
        self.active_collaborations[agent_id].append(session_id)
        
        # Notify other participants
        notification_tasks = []
        for participant in session["participants"]:
            if participant != agent_id:  # Don't notify the joining agent
                notification_tasks.append(
                    self.communication_framework.send_message({
                        "from": agent_id,
                        "to": participant,
                        "content": {
                            "type": "agent_joined",
                            "session_id": session_id,
                            "agent_id": agent_id,
                            "metadata": metadata
                        },
                        "pattern": "broadcast",
                        "metadata": {
                            "category": "collaboration"
                        }
                    })
                )
        
        if notification_tasks:
            await asyncio.gather(*notification_tasks)
        
        logger.info(f"Agent {agent_id} joined collaboration session {session_id}")
        
        return {
            "success": True,
            "message": f"Joined collaboration session {session_id}",
            "session": session
        }
    
    async def leave_collaboration_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Leave a collaboration session.
        
        Args:
            params: Leave parameters including:
                - session_id: Session ID to leave
                - agent_id: Agent ID leaving the session
                - reason: Optional reason for leaving
                
        Returns:
            Leave result
        """
        session_id = params.get("session_id")
        agent_id = params.get("agent_id")
        reason = params.get("reason", "")
        
        if not session_id:
            return {
                "success": False,
                "message": "Missing session ID"
            }
        
        if not agent_id:
            return {
                "success": False,
                "message": "Missing agent ID"
            }
        
        # Check if session exists
        if session_id not in self.collaboration_sessions:
            return {
                "success": False,
                "message": f"Collaboration session {session_id} not found"
            }
        
        # Get session
        session = self.collaboration_sessions[session_id]
        
        # Check if agent is a participant
        if agent_id not in session["participants"]:
            return {
                "success": False,
                "message": f"Agent {agent_id} is not a participant in session {session_id}"
            }
        
        # Remove agent from participants
        async with self.session_locks[session_id]:
            session["participants"].remove(agent_id)
            session["updated_at"] = datetime.now().isoformat()
        
        # Remove session from agent's active collaborations
        if agent_id in self.active_collaborations and session_id in self.active_collaborations[agent_id]:
            self.active_collaborations[agent_id].remove(session_id)
        
        # Notify other participants
        notification_tasks = []
        for participant in session["participants"]:
            notification_tasks.append(
                self.communication_framework.send_message({
                    "from": agent_id,
                    "to": participant,
                    "content": {
                        "type": "agent_left",
                        "session_id": session_id,
                        "agent_id": agent_id,
                        "reason": reason
                    },
                    "pattern": "broadcast",
                    "metadata": {
                        "category": "collaboration"
                    }
                })
            )
        
        if notification_tasks:
            await asyncio.gather(*notification_tasks)
        
        # Check if session should be closed (no participants left)
        if not session["participants"]:
            session["status"] = "closed"
            logger.info(f"Collaboration session {session_id} closed (no participants left)")
        
        logger.info(f"Agent {agent_id} left collaboration session {session_id}")
        
        return {
            "success": True,
            "message": f"Left collaboration session {session_id}",
            "remaining_participants": len(session["participants"])
        }
    
    async def send_collaboration_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message within a collaboration session.
        
        Args:
            params: Message parameters including:
                - session_id: Session ID
                - from: Sender agent ID
                - content: Message content
                - message_type: Type of message
                - metadata: Optional metadata
                
        Returns:
            Message sending result
        """
        session_id = params.get("session_id")
        sender = params.get("from")
        content = params.get("content")
        message_type = params.get("message_type", "text")
        metadata = params.get("metadata", {})
        
        if not session_id:
            return {
                "success": False,
                "message": "Missing session ID"
            }
        
        if not sender:
            return {
                "success": False,
                "message": "Missing sender agent ID"
            }
        
        if content is None:
            return {
                "success": False,
                "message": "Missing message content"
            }
        
        # Check if session exists
        if session_id not in self.collaboration_sessions:
            return {
                "success": False,
                "message": f"Collaboration session {session_id} not found"
            }
        
        # Get session
        session = self.collaboration_sessions[session_id]
        
        # Check if session is active
        if session["status"] != "active":
            return {
                "success": False,
                "message": f"Collaboration session {session_id} is not active"
            }
        
        # Check if agent is a participant
        if sender not in session["participants"]:
            return {
                "success": False,
                "message": f"Agent {sender} is not a participant in session {session_id}"
            }
        
        # Create message
        message = {
            "id": f"msg_{uuid.uuid4().hex}",
            "session_id": session_id,
            "from": sender,
            "content": content,
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        # Add message to session
        async with self.session_locks[session_id]:
            session["messages"].append(message)
            session["updated_at"] = datetime.now().isoformat()
        
        # Notify other participants
        notification_tasks = []
        for participant in session["participants"]:
            if participant != sender:  # Don't notify the sender
                notification_tasks.append(
                    self.communication_framework.send_message({
                        "from": sender,
                        "to": participant,
                        "content": {
                            "type": "collaboration_message",
                            "session_id": session_id,
                            "message": message
                        },
                        "pattern": "broadcast",
                        "metadata": {
                            "category": "collaboration"
                        }
                    })
                )
        
        if notification_tasks:
            await asyncio.gather(*notification_tasks)
        
        logger.info(f"Message sent in collaboration session {session_id} by {sender}")
        
        return {
            "success": True,
            "message": "Collaboration message sent successfully",
            "message_id": message["id"],
            "session_id": session_id
        }
    
    async def update_shared_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the shared state of a collaboration session.
        
        Args:
            params: Update parameters including:
                - session_id: Session ID
                - agent_id: Agent ID making the update
                - updates: Dictionary of state updates
                - operation: Update operation (set, merge, delete)
                
        Returns:
            Update result
        """
        session_id = params.get("session_id")
        agent_id = params.get("agent_id")
        updates = params.get("updates", {})
        operation = params.get("operation", "merge")
        
        if not session_id:
            return {
                "success": False,
                "message": "Missing session ID"
            }
        
        if not agent_id:
            return {
                "success": False,
                "message": "Missing agent ID"
            }
        
        if not updates and operation != "delete":
            return {
                "success": False,
                "message": "Missing state updates"
            }
        
        # Check if session exists
        if session_id not in self.collaboration_sessions:
            return {
                "success": False,
                "message": f"Collaboration session {session_id} not found"
            }
        
        # Get session
        session = self.collaboration_sessions[session_id]
        
        # Check if session is active
        if session["status"] != "active":
            return {
                "success": False,
                "message": f"Collaboration session {session_id} is not active"
            }
        
        # Check if agent is a participant
        if agent_id not in session["participants"]:
            return {
                "success": False,
                "message": f"Agent {agent_id} is not a participant in session {session_id}"
            }
        
        # Update shared state
        async with self.session_locks[session_id]:
            if operation == "set":
                # Replace entire state
                session["shared_state"] = updates
            elif operation == "merge":
                # Merge updates with existing state
                self._deep_merge(session["shared_state"], updates)
            elif operation == "delete":
                # Delete specified keys
                if isinstance(updates, list):
                    for key in updates:
                        if key in session["shared_state"]:
                            del session["shared_state"][key]
                elif isinstance(updates, dict):
                    for key in updates:
                        if key in session["shared_state"]:
                            del session["shared_state"][key]
                else:
                    return {
                        "success": False,
                        "message": "Invalid delete format; must be list or dict"
                    }
            else:
                return {
                    "success": False,
                    "message": f"Invalid operation: {operation}"
                }
            
            session["updated_at"] = datetime.now().isoformat()
        
        # Notify other participants
        notification_tasks = []
        for participant in session["participants"]:
            if participant != agent_id:  # Don't notify the updater
                notification_tasks.append(
                    self.communication_framework.send_message({
                        "from": agent_id,
                        "to": participant,
                        "content": {
                            "type": "state_update",
                            "session_id": session_id,
                            "updates": updates,
                            "operation": operation,
                            "new_state": session["shared_state"]
                        },
                        "pattern": "broadcast",
                        "metadata": {
                            "category": "collaboration",
                            "priority": "high"
                        }
                    })
                )
        
        if notification_tasks:
            await asyncio.gather(*notification_tasks)
        
        logger.info(f"Shared state updated in collaboration session {session_id} by {agent_id}")
        
        return {
            "success": True,
            "message": "Shared state updated successfully",
            "session_id": session_id,
            "new_state": session["shared_state"]
        }
    
    async def add_collaboration_artifact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an artifact to a collaboration session.
        
        Args:
            params: Artifact parameters including:
                - session_id: Session ID
                - agent_id: Agent ID adding the artifact
                - name: Artifact name
                - type: Artifact type
                - content: Artifact content
                - metadata: Optional metadata
                
        Returns:
            Artifact addition result
        """
        session_id = params.get("session_id")
        agent_id = params.get("agent_id")
        name = params.get("name")
        artifact_type = params.get("type")
        content = params.get("content")
        metadata = params.get("metadata", {})
        
        if not session_id:
            return {
                "success": False,
                "message": "Missing session ID"
            }
        
        if not agent_id:
            return {
                "success": False,
                "message": "Missing agent ID"
            }
        
        if not name:
            return {
                "success": False,
                "message": "Missing artifact name"
            }
        
        if not artifact_type:
            return {
                "success": False,
                "message": "Missing artifact type"
            }
        
        if content is None:
            return {
                "success": False,
                "message": "Missing artifact content"
            }
        
        # Check if session exists
        if session_id not in self.collaboration_sessions:
            return {
                "success": False,
                "message": f"Collaboration session {session_id} not found"
            }
        
        # Get session
        session = self.collaboration_sessions[session_id]
        
        # Check if session is active
        if session["status"] != "active":
            return {
                "success": False,
                "message": f"Collaboration session {session_id} is not active"
            }
        
        # Check if agent is a participant
        if agent_id not in session["participants"]:
            return {
                "success": False,
                "message": f"Agent {agent_id} is not a participant in session {session_id}"
            }
        
        # Create artifact
        artifact = {
            "id": f"artifact_{uuid.uuid4().hex}",
            "name": name,
            "type": artifact_type,
            "content": content,
            "created_by": agent_id,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        # Add artifact to session
        async with self.session_locks[session_id]:
            session["artifacts"].append(artifact)
            session["updated_at"] = datetime.now().isoformat()
        
        # Notify other participants
        notification_tasks = []
        for participant in session["participants"]:
            if participant != agent_id:  # Don't notify the creator
                notification_tasks.append(
                    self.communication_framework.send_message({
                        "from": agent_id,
                        "to": participant,
                        "content": {
                            "type": "artifact_added",
                            "session_id": session_id,
                            "artifact": {
                                "id": artifact["id"],
                                "name": artifact["name"],
                                "type": artifact["type"],
                                "created_by": artifact["created_by"],
                                "created_at": artifact["created_at"],
                                "metadata": artifact["metadata"]
                                # Note: Content may be large, so not included in notification
                            }
                        },
                        "pattern": "broadcast",
                        "metadata": {
                            "category": "collaboration"
                        }
                    })
                )
        
        if notification_tasks:
            await asyncio.gather(*notification_tasks)
        
        logger.info(f"Artifact {artifact['id']} added to collaboration session {session_id} by {agent_id}")
        
        return {
            "success": True,
            "message": "Artifact added successfully",
            "artifact_id": artifact["id"],
            "session_id": session_id
        }
    
    async def get_collaboration_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about a collaboration session.
        
        Args:
            params: Query parameters including:
                - session_id: Session ID
                - include_messages: Whether to include messages
                - include_artifacts: Whether to include artifacts
                - include_state: Whether to include shared state
                
        Returns:
            Session information
        """
        session_id = params.get("session_id")
        include_messages = params.get("include_messages", True)
        include_artifacts = params.get("include_artifacts", True)
        include_state = params.get("include_state", True)
        
        if not session_id:
            return {
                "success": False,
                "message": "Missing session ID"
            }
        
        # Check if session exists
        if session_id not in self.collaboration_sessions:
            return {
                "success": False,
                "message": f"Collaboration session {session_id} not found"
            }
        
        # Get session
        session = self.collaboration_sessions[session_id]
        
        # Create response
        response = {
            "id": session["id"],
            "name": session["name"],
            "description": session["description"],
            "participants": session["participants"],
            "initiator": session["initiator"],
            "session_type": session["session_type"],
            "status": session["status"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        }
        
        # Include optional data
        if include_messages:
            response["messages"] = session["messages"]
        
        if include_artifacts:
            response["artifacts"] = session["artifacts"]
        
        if include_state:
            response["shared_state"] = session["shared_state"]
        
        return {
            "success": True,
            "session": response
        }
    
    async def get_agent_collaborations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all collaboration sessions for an agent.
        
        Args:
            params: Query parameters including:
                - agent_id: Agent ID
                - status: Optional status filter
                
        Returns:
            Agent's collaboration sessions
        """
        agent_id = params.get("agent_id")
        status_filter = params.get("status")
        
        if not agent_id:
            return {
                "success": False,
                "message": "Missing agent ID"
            }
        
        # Check if agent has any active collaborations
        if agent_id not in self.active_collaborations:
            return {
                "success": True,
                "message": f"No active collaborations found for agent {agent_id}",
                "sessions": []
            }
        
        # Get session IDs
        session_ids = self.active_collaborations[agent_id]
        
        # Get sessions
        sessions = []
        for session_id in session_ids:
            if session_id in self.collaboration_sessions:
                session = self.collaboration_sessions[session_id]
                
                # Apply status filter if provided
                if status_filter and session["status"] != status_filter:
                    continue
                
                # Add basic session info
                sessions.append({
                    "id": session["id"],
                    "name": session["name"],
                    "description": session["description"],
                    "participants": session["participants"],
                    "initiator": session["initiator"],
                    "session_type": session["session_type"],
                    "status": session["status"],
                    "created_at": session["created_at"],
                    "updated_at": session["updated_at"]
                })
        
        return {
            "success": True,
            "message": f"Found {len(sessions)} collaboration sessions for agent {agent_id}",
            "sessions": sessions
        }
    
    async def register_session_callback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a callback for session events.
        
        Args:
            params: Callback parameters including:
                - session_id: Session ID
                - agent_id: Agent ID
                - event_types: List of event types to listen for
                - callback: Callback function or identifier
                
        Returns:
            Registration result
        """
        session_id = params.get("session_id")
        agent_id = params.get("agent_id")
        event_types = params.get("event_types", ["all"])
        callback = params.get("callback")
        
        if not session_id:
            return {
                "success": False,
                "message": "Missing session ID"
            }
        
        if not agent_id:
            return {
                "success": False,
                "message": "Missing agent ID"
            }
        
        if not callback:
            return {
                "success": False,
                "message": "Missing callback"
            }
        
        # Check if session exists
        if session_id not in self.collaboration_sessions:
            return {
                "success": False,
                "message": f"Collaboration session {session_id} not found"
            }
        
        # Get session
        session = self.collaboration_sessions[session_id]
        
        # Check if agent is a participant
        if agent_id not in session["participants"]:
            return {
                "success": False,
                "message": f"Agent {agent_id} is not a participant in session {session_id}"
            }
        
        # Create callback key
        callback_key = f"{session_id}_{agent_id}_{uuid.uuid4().hex}"
        
        # Register callback
        self.session_callbacks[callback_key] = {
            "session_id": session_id,
            "agent_id": agent_id,
            "event_types": event_types,
            "callback": callback
        }
        
        logger.info(f"Callback registered for agent {agent_id} in session {session_id}")
        
        return {
            "success": True,
            "message": "Callback registered successfully",
            "callback_key": callback_key
        }
    
    async def unregister_session_callback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unregister a session callback.
        
        Args:
            params: Unregister parameters including:
                - callback_key: Callback key to unregister
                
        Returns:
            Unregistration result
        """
        callback_key = params.get("callback_key")
        
        if not callback_key:
            return {
                "success": False,
                "message": "Missing callback key"
            }
        
        # Check if callback exists
        if callback_key not in self.session_callbacks:
            return {
                "success": False,
                "message": f"Callback with key {callback_key} not found"
            }
        
        # Get callback info
        callback_info = self.session_callbacks[callback_key]
        
        # Unregister callback
        del self.session_callbacks[callback_key]
        
        logger.info(f"Callback unregistered for agent {callback_info['agent_id']} in session {callback_info['session_id']}")
        
        return {
            "success": True,
            "message": "Callback unregistered successfully"
        }
    
    async def close_collaboration_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Close a collaboration session.
        
        Args:
            params: Close parameters including:
                - session_id: Session ID
                - agent_id: Agent ID closing the session
                - reason: Optional reason for closing
                
        Returns:
            Close result
        """
        session_id = params.get("session_id")
        agent_id = params.get("agent_id")
        reason = params.get("reason", "")
        
        if not session_id:
            return {
                "success": False,
                "message": "Missing session ID"
            }
        
        if not agent_id:
            return {
                "success": False,
                "message": "Missing agent ID"
            }
        
        # Check if session exists
        if session_id not in self.collaboration_sessions:
            return {
                "success": False,
                "message": f"Collaboration session {session_id} not found"
            }
        
        # Get session
        session = self.collaboration_sessions[session_id]
        
        # Check if agent is the initiator or has permission to close
        if agent_id != session["initiator"]:
            return {
                "success": False,
                "message": f"Agent {agent_id} does not have permission to close session {session_id}"
            }
        
        # Close session
        async with self.session_locks[session_id]:
            session["status"] = "closed"
            session["updated_at"] = datetime.now().isoformat()
        
        # Notify participants
        notification_tasks = []
        for participant in session["participants"]:
            if participant != agent_id:  # Don't notify the closer
                notification_tasks.append(
                    self.communication_framework.send_message({
                        "from": agent_id,
                        "to": participant,
                        "content": {
                            "type": "session_closed",
                            "session_id": session_id,
                            "closed_by": agent_id,
                            "reason": reason
                        },
                        "pattern": "broadcast",
                        "metadata": {
                            "category": "collaboration",
                            "priority": "high"
                        }
                    })
                )
        
        if notification_tasks:
            await asyncio.gather(*notification_tasks)
        
        # Remove session from active collaborations
        for participant in session["participants"]:
            if participant in self.active_collaborations and session_id in self.active_collaborations[participant]:
                self.active_collaborations[participant].remove(session_id)
        
        logger.info(f"Collaboration session {session_id} closed by {agent_id}")
        
        return {
            "success": True,
            "message": f"Collaboration session {session_id} closed successfully",
            "session_id": session_id
        }
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Deep merge two dictionaries.
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
