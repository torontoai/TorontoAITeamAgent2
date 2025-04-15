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


"""MCP and A2A Integration Module.

This module integrates the Multi-agent Conversational Protocols (MCP) and
Agent-to-Agent (A2A) frameworks with the existing communication system."""

from typing import Dict, Any, List, Optional, Union, Callable, Type
import logging
import asyncio
import uuid
from datetime import datetime
import json

from app.collaboration.mcp_framework import (
    ConversationProtocol, ConversationContext, ConversationManager,
    InformationExchangeProtocol, NegotiationProtocol, TaskDelegationProtocol,
    CollaborativeProblemSolvingProtocol, ErrorHandlingProtocol
)
from app.collaboration.a2a_framework import (
    Capability, CapabilityRegistry, TrustManager, SecurityManager,
    AgentIdentity, A2AFramework
)
from app.collaboration.communication_framework import (
    CommunicationManager, Message, MessageType, EventBus
)
from app.collaboration.enhanced_communication_framework import (
    EnhancedCommunicationManager, MessagePriority, MessageStatus
)
from app.collaboration.multi_agent_system import (
    MultiAgentSystem, AgentRegistry
)
from app.collaboration.project_manager_communication_flow import (
    ProjectManagerCommunicationFlow
)
from app.collaboration.request_prioritization_mechanism import (
    RequestPrioritizationMechanism
)

logger = logging.getLogger(__name__)

class MCPAdapter:
    """Adapter for integrating MCP with the existing communication system.
    
    This adapter translates between the existing message format and the
    MCP conversation protocol format."""
    
    def __init__(self, conversation_manager: ConversationManager, 
                 communication_manager: Union[CommunicationManager, EnhancedCommunicationManager]):
        """Initialize the MCP adapter.
        
        Args:
            conversation_manager: MCP conversation manager
            communication_manager: Existing communication manager"""
        self.conversation_manager = conversation_manager
        self.communication_manager = communication_manager
        self.conversation_map: Dict[str, str] = {}  # Maps message thread IDs to conversation IDs
        self.protocol_map: Dict[str, str] = {
            "information": "info_exchange",
            "negotiation": "negotiation",
            "task": "task_delegation",
            "problem_solving": "collaborative_problem_solving",
            "error": "error_handling"
        }
        
        logger.info("MCP Adapter initialized")
        
    async def register_standard_protocols(self) -> None:
        """Register standard conversation protocols with the conversation manager."""
        protocols = [
            InformationExchangeProtocol(),
            NegotiationProtocol(),
            TaskDelegationProtocol(),
            CollaborativeProblemSolvingProtocol(),
            ErrorHandlingProtocol()
        ]
        
        for protocol in protocols:
            self.conversation_manager.register_protocol(protocol)
            
        logger.info("Registered standard protocols with conversation manager")
        
    async def message_to_mcp(self, message: Message) -> Dict[str, Any]:
        """
        Convert a standard message to MCP format.
        
        Args:
            message: Standard message
            
        Returns:
            MCP message
        """
        # Determine conversation ID
        conversation_id = None
        thread_id = message.metadata.get("thread_id")
        
        if thread_id and thread_id in self.conversation_map:
            conversation_id = self.conversation_map[thread_id]
            
        # Create MCP message
        mcp_message = {
            "message_id": message.id,
            "sender": {
                "id": message.sender,
                "role": message.metadata.get("sender_role", "unknown")
            },
            "content": {
                "type": self._map_message_type(message.type),
                "subject": message.subject,
                "body": message.content,
                "data": message.data
            },
            "metadata": {
                "created_at": message.timestamp.isoformat() if hasattr(message, "timestamp") else datetime.now().isoformat(),
                "priority": message.metadata.get("priority", "normal"),
                "thread_id": thread_id
            }
        }
        
        return {
            "conversation_id": conversation_id,
            "message": mcp_message
        }
        
    async def mcp_to_message(self, mcp_result: Dict[str, Any]) -> Message:
        """
        Convert an MCP message to standard format.
        
        Args:
            mcp_result: MCP message processing result
            
        Returns:
            Standard message
        """
        if not mcp_result.get("success"):
            logger.error(f"MCP processing failed: {mcp_result.get('message')}")
            return None
            
        mcp_content = mcp_result.get("content", {})
        
        # Create standard message
        message = Message(
            id=mcp_result.get("message_id", str(uuid.uuid4())),
            sender=mcp_result.get("sender"),
            recipients=[mcp_result.get("recipient")] if "recipient" in mcp_result else [],
            subject=mcp_content.get("subject", ""),
            content=mcp_content.get("body", ""),
            type=self._map_mcp_type(mcp_content.get("type", "unknown")),
            data=mcp_content.get("data", {})
        )
        
        # Add metadata
        message.metadata = {
            "thread_id": mcp_result.get("conversation_id"),
            "priority": mcp_result.get("priority", "normal"),
            "status": "processed"
        }
        
        return message
        
    def _map_message_type(self, message_type: MessageType) -> str:
        """Map standard message type to MCP message type.
        
        Args:
            message_type: Standard message type
            
        Returns:
            MCP message type"""
        type_map = {
            MessageType.INFORMATION: "information",
            MessageType.REQUEST: "request",
            MessageType.RESPONSE: "response",
            MessageType.TASK: "assign_task",
            MessageType.STATUS: "progress_update",
            MessageType.ERROR: "report_error",
            MessageType.PROPOSAL: "proposal",
            MessageType.FEEDBACK: "evaluate_solution"
        }
        
        return type_map.get(message_type, "information")
        
    def _map_mcp_type(self, mcp_type: str) -> MessageType:
        """Map MCP message type to standard message type.
        
        Args:
            mcp_type: MCP message type
            
        Returns:
            Standard message type"""
        type_map = {
            "information": MessageType.INFORMATION,
            "request": MessageType.REQUEST,
            "response": MessageType.RESPONSE,
            "assign_task": MessageType.TASK,
            "progress_update": MessageType.STATUS,
            "report_error": MessageType.ERROR,
            "proposal": MessageType.PROPOSAL,
            "evaluate_solution": MessageType.FEEDBACK
        }
        
        return type_map.get(mcp_type, MessageType.INFORMATION)
        
    async def start_conversation(self, thread_id: str, protocol_type: str, participants: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Start a new conversation.
        
        Args:
            thread_id: Message thread ID
            protocol_type: Type of protocol to use
            participants: List of participants
            
        Returns:
            Conversation creation result
        """
        # Map protocol type to protocol ID
        protocol_id = self.protocol_map.get(protocol_type, "info_exchange")
        
        # Create conversation
        result = await self.conversation_manager.create_conversation(
            protocol_id=protocol_id,
            protocol_version="latest",
            participants=participants
        )
        
        if result["success"]:
            # Map thread ID to conversation ID
            self.conversation_map[thread_id] = result["conversation_id"]
            
        return result
        
    async def process_message(self, message: Message) -> Dict[str, Any]:
        """
        Process a message through MCP.
        
        Args:
            message: Message to process
            
        Returns:
            Processing result
        """
        # Convert to MCP format
        mcp_data = await self.message_to_mcp(message)
        conversation_id = mcp_data["conversation_id"]
        mcp_message = mcp_data["message"]
        
        # If no conversation exists, create one
        if not conversation_id:
            thread_id = message.metadata.get("thread_id", str(uuid.uuid4()))
            
            # Determine protocol type based on message type
            protocol_type = "information"
            if message.type == MessageType.TASK:
                protocol_type = "task"
            elif message.type == MessageType.PROPOSAL:
                protocol_type = "negotiation"
            elif message.type == MessageType.ERROR:
                protocol_type = "error"
                
            # Create participants list
            participants = [
                {"id": message.sender, "role": message.metadata.get("sender_role", "unknown")}
            ]
            
            for recipient in message.recipients:
                participants.append({
                    "id": recipient,
                    "role": message.metadata.get(f"recipient_role_{recipient}", "unknown")
                })
                
            # Start conversation
            conv_result = await self.start_conversation(thread_id, protocol_type, participants)
            
            if not conv_result["success"]:
                return {
                    "success": False,
                    "message": f"Failed to create conversation: {conv_result.get('error')}"
                }
                
            conversation_id = conv_result["conversation_id"]
            
        # Add message to conversation
        result = await self.conversation_manager.add_message(conversation_id, mcp_message)
        
        if not result["success"]:
            return {
                "success": False,
                "message": f"Failed to add message to conversation: {result.get('error')}"
            }
            
        # Return success with conversation state
        return {
            "success": True,
            "conversation_id": conversation_id,
            "new_state": result["new_state"],
            "is_terminal": result["is_terminal"],
            "message_id": mcp_message["message_id"]
        }
        
    async def handle_incoming_message(self, message: Message) -> Optional[Message]:
        """
        Handle an incoming message.
        
        Args:
            message: Incoming message
            
        Returns:
            Response message, if any
        """
        # Process through MCP
        result = await self.process_message(message)
        
        if not result["success"]:
            logger.error(f"Failed to process message through MCP: {result.get('message')}")
            return None
            
        # Check if we need to generate a response
        if result.get("is_terminal", False):
            # Create completion notification
            response = Message(
                id=str(uuid.uuid4()),
                sender="system",
                recipients=[message.sender],
                subject=f"Re: {message.subject}",
                content=f"Conversation completed in state: {result['new_state']}",
                type=MessageType.INFORMATION
            )
            
            response.metadata = {
                "thread_id": message.metadata.get("thread_id"),
                "conversation_id": result["conversation_id"],
                "priority": "normal",
                "status": "final"
            }
            
            return response
            
        return None

class A2AAdapter:
    """Adapter for integrating A2A with the existing agent system.
    
    This adapter connects the A2A framework with the existing agent
    registry and communication system."""
    
    def __init__(self, a2a_framework: A2AFramework, 
                 agent_registry: AgentRegistry,
                 communication_manager: Union[CommunicationManager, EnhancedCommunicationManager]):
        """Initialize the A2A adapter.
        
        Args:
            a2a_framework: A2A framework
            agent_registry: Existing agent registry
            communication_manager: Existing communication manager"""
        self.a2a_framework = a2a_framework
        self.agent_registry = agent_registry
        self.communication_manager = communication_manager
        
        logger.info("A2A Adapter initialized")
        
    async def register_existing_agents(self) -> Dict[str, Any]:
        """
        Register existing agents with the A2A framework.
        
        Returns:
            Registration results
        """
        results = []
        
        # Get all agents from registry
        agents = self.agent_registry.get_all_agents()
        
        for agent_id, agent_info in agents.items():
            # Register with A2A framework
            result = await self.a2a_framework.register_agent(
                agent_id=agent_id,
                role=agent_info.get("role", "unknown"),
                name=agent_info.get("name"),
                description=agent_info.get("description")
            )
            
            results.append({
                "agent_id": agent_id,
                "success": result["success"],
                "message": result.get("message")
            })
            
            # Register capabilities
            if result["success"] and "capabilities" in agent_info:
                for capability in agent_info["capabilities"]:
                    await self.register_agent_capability(agent_id, capability)
                    
        logger.info(f"Registered {len(results)} existing agents with A2A framework")
        
        return {
            "success": True,
            "results": results
        }
        
    async def register_agent_capability(self, agent_id: str, capability_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a capability for an agent.
        
        Args:
            agent_id: ID of the agent
            capability_info: Capability information
            
        Returns:
            Registration result
        """
        # Convert to A2A capability format
        capability = {
            "name": capability_info.get("name", "Unknown Capability"),
            "description": capability_info.get("description", ""),
            "parameters": capability_info.get("parameters", {}),
            "performance_metrics": capability_info.get("metrics", {}),
            "semantic_tags": capability_info.get("tags", [])
        }
        
        # Register with A2A framework
        return await self.a2a_framework.register_capability(agent_id, capability)
        
    async def find_agents_for_task(self, task_description: str, required_capabilities: List[str], 
                                  source_agent: str = None) -> Dict[str, Any]:
        """
        Find agents suitable for a task.
        
        Args:
            task_description: Description of the task
            required_capabilities: List of required capabilities
            source_agent: Optional agent ID to use for trust filtering
            
        Returns:
            List of suitable agents
        """
        # Create search criteria
        criteria = {
            "description_keywords": task_description.split(),
            "tags": required_capabilities
        }
        
        # Find agents
        result = await self.a2a_framework.find_capable_agents(
            criteria=criteria,
            trust_source=source_agent,
            min_trust_score=0.6
        )
        
        return result
        
    async def send_secure_message(self, message: Message) -> Dict[str, Any]:
        """
        Send a message securely through A2A.
        
        Args:
            message: Message to send
            
        Returns:
            Sending result
        """
        if not message.recipients:
            return {
                "success": False,
                "message": "No recipients specified"
            }
            
        results = []
        
        # Send to each recipient
        for recipient in message.recipients:
            # Convert to A2A message format
            a2a_message = {
                "id": message.id,
                "subject": message.subject,
                "content": message.content,
                "data": message.data,
                "type": str(message.type),
                "metadata": message.metadata
            }
            
            # Send through A2A framework
            result = await self.a2a_framework.send_message(
                sender_id=message.sender,
                recipient_id=recipient,
                message=a2a_message
            )
            
            results.append({
                "recipient": recipient,
                "success": result["success"],
                "message": result.get("message")
            })
            
        # Check if all sends were successful
        all_success = all(r["success"] for r in results)
        
        return {
            "success": all_success,
            "results": results
        }
        
    async def receive_secure_message(self, recipient_id: str, secured_message: Dict[str, Any]) -> Optional[Message]:
        """
        Receive and process a secure message.
        
        Args:
            recipient_id: ID of the recipient
            secured_message: Secured message
            
        Returns:
            Processed message
        """
        # Receive through A2A framework
        result = await self.a2a_framework.receive_message(
            recipient_id=recipient_id,
            secured_message=secured_message
        )
        
        if not result["success"]:
            logger.error(f"Failed to receive secure message: {result.get('message')}")
            return None
            
        # Convert to standard message format
        content = result["content"]
        
        message = Message(
            id=result["message_id"],
            sender=result["sender"],
            recipients=[recipient_id],
            subject=content.get("subject", ""),
            content=content.get("content", ""),
            type=self._map_type(content.get("type", "INFORMATION")),
            data=content.get("data", {})
        )
        
        message.metadata = content.get("metadata", {})
        
        return message
        
    def _map_type(self, type_str: str) -> MessageType:
        """Map string type to MessageType.
        
        Args:
            type_str: String representation of message type
            
        Returns:
            MessageType enum value"""
        try:
            return MessageType[type_str]
        except (KeyError, ValueError):
            return MessageType.INFORMATION
            
    async def update_agent_trust(self, source_id: str, target_id: str, 
                               interaction_type: str, outcome: str) -> Dict[str, Any]:
        """
        Update trust between agents.
        
        Args:
            source_id: ID of the source agent
            target_id: ID of the target agent
            interaction_type: Type of interaction
            outcome: Outcome of the interaction
            
        Returns:
            Trust update result
        """
        # Record interaction
        result = await self.a2a_framework.trust_manager.record_interaction(
            source_agent=source_id,
            target_agent=target_id,
            interaction_type=interaction_type,
            outcome=outcome
        )
        
        if not result["success"]:
            return result
            
        # Get updated trust score
        trust_result = await self.a2a_framework.get_agent_trust(source_id, target_id)
        
        return {
            "success": True,
            "trust_score": trust_result["trust_score"],
            "interaction_count": trust_result["interaction_count"]
        }

class IntegratedCommunicationSystem:
    """Integrated communication system combining MCP and A2A with existing systems.
    
    This system provides a unified interface for agent communication with
    enhanced protocol support, capability discovery, and trust management."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the integrated communication system.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        
        # Initialize components
        self.event_bus = EventBus()
        self.agent_registry = AgentRegistry()
        
        # Initialize communication manager
        if self.config.get("use_enhanced_communication", True):
            self.communication_manager = EnhancedCommunicationManager(self.event_bus)
        else:
            self.communication_manager = CommunicationManager(self.event_bus)
            
        # Initialize MCP components
        self.conversation_manager = ConversationManager(self.config.get("conversation_manager"))
        self.mcp_adapter = MCPAdapter(self.conversation_manager, self.communication_manager)
        
        # Initialize A2A components
        self.a2a_framework = A2AFramework(self.config.get("a2a_framework"))
        self.a2a_adapter = A2AAdapter(self.a2a_framework, self.agent_registry, self.communication_manager)
        
        # Initialize prioritization mechanism
        self.prioritization = RequestPrioritizationMechanism()
        
        # Initialize multi-agent system
        self.multi_agent_system = MultiAgentSystem(self.agent_registry, self.event_bus)
        
        # Initialize project manager communication flow
        self.pm_communication_flow = ProjectManagerCommunicationFlow(self.communication_manager)
        
        logger.info("Integrated Communication System initialized")
        
    async def initialize(self) -> None:
        """Initialize the system and register components."""
        # Register standard protocols
        await self.mcp_adapter.register_standard_protocols()
        
        # Register existing agents
        await self.a2a_adapter.register_existing_agents()
        
        # Set up event handlers
        self.event_bus.subscribe("message_sent", self._handle_message_sent)
        self.event_bus.subscribe("message_received", self._handle_message_received)
        
        logger.info("Integrated Communication System initialization complete")
        
    async def register_agent(self, agent_id: str, role: str, name: str = None, 
                           description: str = None, capabilities: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Register an agent with the system.
        
        Args:
            agent_id: ID of the agent
            role: Role of the agent
            name: Optional name
            description: Optional description
            capabilities: Optional list of capabilities
            
        Returns:
            Registration result
        """
        # Register with agent registry
        self.agent_registry.register_agent(agent_id, {
            "role": role,
            "name": name,
            "description": description,
            "capabilities": capabilities or []
        })
        
        # Register with A2A framework
        a2a_result = await self.a2a_framework.register_agent(
            agent_id=agent_id,
            role=role,
            name=name,
            description=description
        )
        
        # Register capabilities
        if a2a_result["success"] and capabilities:
            for capability in capabilities:
                await self.a2a_adapter.register_agent_capability(agent_id, capability)
                
        return {
            "success": a2a_result["success"],
            "message": a2a_result.get("message"),
            "security_token": a2a_result.get("security_token")
        }
        
    async def send_message(self, message: Message, secure: bool = True) -> Dict[str, Any]:
        """
        Send a message.
        
        Args:
            message: Message to send
            secure: Whether to send securely through A2A
            
        Returns:
            Sending result
        """
        # Prioritize message
        priority = self.prioritization.prioritize_message(message)
        message.metadata["priority"] = priority
        
        # Send securely if requested
        if secure:
            result = await self.a2a_adapter.send_secure_message(message)
            
            if result["success"]:
                # Notify event bus
                self.event_bus.publish("message_sent", {
                    "message": message,
                    "secure": True
                })
                
            return result
            
        # Otherwise, send through communication manager
        self.communication_manager.send_message(message)
        
        return {
            "success": True,
            "message": "Message sent through communication manager"
        }
        
    async def start_conversation(self, thread_id: str, protocol_type: str, 
                               participants: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Start a new conversation.
        
        Args:
            thread_id: Message thread ID
            protocol_type: Type of protocol to use
            participants: List of participants
            
        Returns:
            Conversation creation result
        """
        return await self.mcp_adapter.start_conversation(thread_id, protocol_type, participants)
        
    async def find_agents_for_task(self, task_description: str, required_capabilities: List[str], 
                                  source_agent: str = None) -> Dict[str, Any]:
        """
        Find agents suitable for a task.
        
        Args:
            task_description: Description of the task
            required_capabilities: List of required capabilities
            source_agent: Optional agent ID to use for trust filtering
            
        Returns:
            List of suitable agents
        """
        return await self.a2a_adapter.find_agents_for_task(
            task_description=task_description,
            required_capabilities=required_capabilities,
            source_agent=source_agent
        )
        
    async def update_agent_trust(self, source_id: str, target_id: str, 
                               interaction_type: str, outcome: str) -> Dict[str, Any]:
        """
        Update trust between agents.
        
        Args:
            source_id: ID of the source agent
            target_id: ID of the target agent
            interaction_type: Type of interaction
            outcome: Outcome of the interaction
            
        Returns:
            Trust update result
        """
        return await self.a2a_adapter.update_agent_trust(
            source_id=source_id,
            target_id=target_id,
            interaction_type=interaction_type,
            outcome=outcome
        )
        
    async def get_agent_capabilities(self, agent_id: str) -> Dict[str, Any]:
        """
        Get capabilities for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent capabilities
        """
        return await self.a2a_framework.get_agent_capabilities(agent_id)
        
    async def get_agent_trust(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """
        Get trust information between agents.
        
        Args:
            source_id: ID of the source agent
            target_id: ID of the target agent
            
        Returns:
            Trust information
        """
        return await self.a2a_framework.get_agent_trust(source_id, target_id)
        
    async def get_agent_reputation(self, agent_id: str) -> Dict[str, Any]:
        """
        Get reputation for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Reputation information
        """
        return await self.a2a_framework.get_agent_reputation(agent_id)
        
    async def _handle_message_sent(self, data: Dict[str, Any]) -> None:
        """
        Handle message sent event.
        
        Args:
            data: Event data
        """
        message = data["message"]
        
        # Process through MCP if not already secure
        if not data.get("secure", False):
            await self.mcp_adapter.process_message(message)
            
    async def _handle_message_received(self, data: Dict[str, Any]) -> None:
        """
        Handle message received event.
        
        Args:
            data: Event data
        """
        message = data["message"]
        
        # Process through MCP
        result = await self.mcp_adapter.process_message(message)
        
        if result["success"]:
            # Check if we need to generate a response
            if result.get("is_terminal", False):
                # Create completion notification
                response = Message(
                    id=str(uuid.uuid4()),
                    sender="system",
                    recipients=[message.sender],
                    subject=f"Re: {message.subject}",
                    content=f"Conversation completed in state: {result['new_state']}",
                    type=MessageType.INFORMATION
                )
                
                response.metadata = {
                    "thread_id": message.metadata.get("thread_id"),
                    "conversation_id": result["conversation_id"],
                    "priority": "normal",
                    "status": "final"
                }
                
                # Send response
                await self.send_message(response, secure=False)
                
    async def maintenance_tasks(self) -> Dict[str, Any]:
        """
        Perform maintenance tasks.
        
        Returns:
            Maintenance results
        """
        # Perform A2A maintenance
        a2a_result = await self.a2a_framework.maintenance_tasks()
        
        # Archive old conversations
        conv_result = await self.conversation_manager.auto_archive_old_conversations()
        
        return {
            "success": True,
            "a2a_maintenance": a2a_result,
            "conversation_maintenance": conv_result
        }
