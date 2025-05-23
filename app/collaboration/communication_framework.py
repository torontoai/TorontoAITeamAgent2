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


"""Agent Communication Framework for TorontoAITeamAgent.

This module provides the communication framework that enables agents to communicate with each other."""

from typing import Dict, Any, List, Optional, Union
import logging
import asyncio
import json
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class AgentCommunicationFramework:
    """Communication framework that enables agents to communicate with each other."""
    
    def __init__(self):
        """Initialize the Agent Communication Framework."""
        self.message_queue = []
        self.subscribers = {}
        self.message_history = []
        self.pending_responses = {}  # Track pending responses for request-response pattern
        self.communication_patterns = {
            "request_response": self._handle_request_response,
            "broadcast": self._handle_broadcast,
            "publish_subscribe": self._handle_publish_subscribe
        }
        
        logger.info("Agent Communication Framework initialized")
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message from one agent to another.
        
        Args:
            message: Message data including from, to, content, and metadata
            
        Returns:
            Message sending result
        """
        if "from" not in message:
            return {
                "success": False,
                "message": "Missing sender information"
            }
        
        if "to" not in message:
            return {
                "success": False,
                "message": "Missing recipient information"
            }
        
        # Add timestamp and message ID
        message_id = f"msg_{uuid.uuid4().hex}"
        message["id"] = message_id
        message["timestamp"] = datetime.now().isoformat()
        
        # Add to message queue
        self.message_queue.append(message)
        
        # Add to message history
        self.message_history.append(message)
        
        # Determine communication pattern
        pattern = message.get("pattern", "request_response")
        if pattern in self.communication_patterns:
            result = await self.communication_patterns[pattern](message)
        else:
            result = await self._handle_request_response(message)
        
        logger.info(f"Message sent from {message['from']} to {message['to']} with pattern {pattern}")
        
        return {
            "success": True,
            "message": "Message sent successfully",
            "message_id": message_id,
            "result": result
        }
    
    async def _handle_request_response(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle request-response communication pattern.
        
        Args:
            message: Message data
            
        Returns:
            Handling result
        """
        # Store the request in pending responses if a response is expected
        if message.get("response_expected", True):
            self.pending_responses[message["id"]] = {
                "request": message,
                "response": None,
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # Set up timeout for response if specified
            timeout = message.get("timeout", 300)  # Default 5 minutes
            if timeout > 0:
                # Schedule timeout check
                asyncio.create_task(self._check_response_timeout(message["id"], timeout))
        
        # Route the message to the recipient agent
        # In a real implementation, this would use a message broker or direct call
        # For now, we'll simulate routing by adding to a recipient-specific queue
        recipient = message["to"]
        if isinstance(recipient, str):
            # Single recipient
            await self._route_message_to_agent(recipient, message)
        elif isinstance(recipient, list):
            # Multiple recipients
            for agent_id in recipient:
                await self._route_message_to_agent(agent_id, message)
        
        return {
            "pattern": "request_response",
            "status": "delivered",
            "response_expected": message.get("response_expected", True),
            "message_id": message["id"]
        }
    
    async def _route_message_to_agent(self, agent_id: str, message: Dict[str, Any]) -> None:
        """
        Route a message to a specific agent.
        
        Args:
            agent_id: Recipient agent ID
            message: Message to route
        """
        # In a real implementation, this would use a message broker or direct call
        # For now, log the routing
        logger.info(f"Routing message {message['id']} to agent {agent_id}")
        
        # Here we would typically push to an agent-specific queue or call an agent method
        # This is a placeholder for the actual implementation
        
    async def _check_response_timeout(self, message_id: str, timeout: int) -> None:
        """
        Check if a response has timed out.
        
        Args:
            message_id: Message ID to check
            timeout: Timeout in seconds
        """
        await asyncio.sleep(timeout)
        
        if message_id in self.pending_responses and self.pending_responses[message_id]["status"] == "pending":
            # Response timed out
            self.pending_responses[message_id]["status"] = "timeout"
            logger.warning(f"Response for message {message_id} timed out after {timeout} seconds")
    
    async def _handle_broadcast(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle broadcast communication pattern.
        
        Args:
            message: Message data
            
        Returns:
            Handling result
        """
        # Determine recipients for broadcast
        recipients = message.get("to", "all")
        recipient_list = []
        
        if recipients == "all":
            # Broadcast to all agents
            # In a real implementation, this would get all active agents
            # For now, use a placeholder list
            recipient_list = ["all_agents"]  # Placeholder
        elif isinstance(recipients, list):
            # Broadcast to specific agents
            recipient_list = recipients
        elif isinstance(recipients, str) and recipients != "all":
            # Broadcast to a specific group
            # In a real implementation, this would get all agents in the group
            # For now, use a placeholder list
            recipient_list = [recipients]  # Placeholder
        
        # Route the message to all recipients
        for recipient in recipient_list:
            await self._route_message_to_agent(recipient, message)
        
        return {
            "pattern": "broadcast",
            "status": "broadcasted",
            "recipients": recipients,
            "recipient_count": len(recipient_list)
        }
    
    async def _handle_publish_subscribe(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle publish-subscribe communication pattern.
        
        Args:
            message: Message data
            
        Returns:
            Handling result
        """
        topic = message.get("topic", "general")
        
        # Notify subscribers
        if topic in self.subscribers:
            subscriber_count = len(self.subscribers[topic])
            
            # Route the message to all subscribers
            for subscriber in self.subscribers[topic]:
                # Create a copy of the message for each subscriber
                subscriber_message = message.copy()
                subscriber_message["to"] = subscriber
                
                # Route the message
                await self._route_message_to_agent(subscriber, subscriber_message)
            
            return {
                "pattern": "publish_subscribe",
                "status": "published",
                "topic": topic,
                "subscriber_count": subscriber_count
            }
        
        return {
            "pattern": "publish_subscribe",
            "status": "published",
            "topic": topic,
            "subscriber_count": 0
        }
    
    async def subscribe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subscribe an agent to a topic.
        
        Args:
            params: Subscription parameters including agent_id and topic
            
        Returns:
            Subscription result
        """
        agent_id = params.get("agent_id")
        if not agent_id:
            return {
                "success": False,
                "message": "Missing agent ID"
            }
        
        topic = params.get("topic", "general")
        
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        
        if agent_id not in self.subscribers[topic]:
            self.subscribers[topic].append(agent_id)
        
        logger.info(f"Agent {agent_id} subscribed to topic {topic}")
        
        return {
            "success": True,
            "message": f"Subscribed to topic {topic}",
            "topic": topic,
            "subscriber_count": len(self.subscribers[topic])
        }
    
    async def unsubscribe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unsubscribe an agent from a topic.
        
        Args:
            params: Unsubscription parameters including agent_id and topic
            
        Returns:
            Unsubscription result
        """
        agent_id = params.get("agent_id")
        if not agent_id:
            return {
                "success": False,
                "message": "Missing agent ID"
            }
        
        topic = params.get("topic", "general")
        
        if topic in self.subscribers and agent_id in self.subscribers[topic]:
            self.subscribers[topic].remove(agent_id)
            logger.info(f"Agent {agent_id} unsubscribed from topic {topic}")
            
            return {
                "success": True,
                "message": f"Unsubscribed from topic {topic}",
                "topic": topic,
                "subscriber_count": len(self.subscribers[topic])
            }
        
        return {
            "success": False,
            "message": f"Agent {agent_id} was not subscribed to topic {topic}"
        }
    
    async def get_message_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get message history.
        
        Args:
            params: History parameters including filters
            
        Returns:
            Message history
        """
        filters = params.get("filters", {})
        
        # Apply filters
        filtered_history = self.message_history
        
        if "from" in filters:
            filtered_history = [msg for msg in filtered_history if msg.get("from") == filters["from"]]
        
        if "to" in filters:
            filtered_history = [msg for msg in filtered_history if msg.get("to") == filters["to"]]
        
        if "pattern" in filters:
            filtered_history = [msg for msg in filtered_history if msg.get("pattern") == filters["pattern"]]
        
        if "topic" in filters:
            filtered_history = [msg for msg in filtered_history if msg.get("topic") == filters["topic"]]
        
        if "start_time" in filters:
            start_time = filters["start_time"]
            filtered_history = [msg for msg in filtered_history if msg.get("timestamp", "") >= start_time]
        
        if "end_time" in filters:
            end_time = filters["end_time"]
            filtered_history = [msg for msg in filtered_history if msg.get("timestamp", "") <= end_time]
        
        # Limit results
        limit = params.get("limit", 100)
        filtered_history = filtered_history[-limit:]
        
        return {
            "success": True,
            "message": "Message history retrieved",
            "history": filtered_history,
            "count": len(filtered_history)
        }
    
    async def respond_to_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Respond to a message.
        
        Args:
            params: Response parameters including:
                - request_id: ID of the original request message
                - from: Sender agent ID
                - content: Response content
                - metadata: Optional metadata
                
        Returns:
            Response result
        """
        request_id = params.get("request_id")
        if not request_id:
            return {
                "success": False,
                "message": "Missing request ID"
            }
        
        sender = params.get("from")
        if not sender:
            return {
                "success": False,
                "message": "Missing sender information"
            }
        
        content = params.get("content")
        if content is None:
            return {
                "success": False,
                "message": "Missing response content"
            }
        
        # Check if the request exists
        if request_id not in self.pending_responses:
            return {
                "success": False,
                "message": f"No pending request found with ID {request_id}"
            }
        
        # Get the original request
        request = self.pending_responses[request_id]["request"]
        
        # Create response message
        response = {
            "id": f"resp_{uuid.uuid4().hex}",
            "request_id": request_id,
            "from": sender,
            "to": request["from"],
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": params.get("metadata", {}),
            "pattern": "response"
        }
        
        # Update pending response
        self.pending_responses[request_id]["response"] = response
        self.pending_responses[request_id]["status"] = "completed"
        
        # Add to message history
        self.message_history.append(response)
        
        # Route the response to the original sender
        await self._route_message_to_agent(request["from"], response)
        
        logger.info(f"Response sent for message {request_id} from {sender} to {request['from']}")
        
        return {
            "success": True,
            "message": "Response sent successfully",
            "response_id": response["id"],
            "request_id": request_id
        }
    
    async def analyze_communication_patterns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze communication patterns to improve agent interactions.
        
        Args:
            params: Analysis parameters including:
                - project_id: Optional project ID to filter messages
                - time_period: Optional time period for analysis
                - agents: Optional list of agents to include
                
        Returns:
            Analysis result
        """
        project_id = params.get("project_id")
        time_period = params.get("time_period", "all")
        agents = params.get("agents", [])
        
        # Filter messages based on parameters
        messages = self.message_history
        
        if project_id:
            messages = [msg for msg in messages if msg.get("project_id") == project_id]
        
        if time_period != "all":
            # Implement time period filtering
            # For now, use all messages
            pass
        
        if agents:
            messages = [
                msg for msg in messages 
                if msg.get("from") in agents or msg.get("to") in agents
            ]
        
        # Analyze communication patterns
        if not messages:
            return {
                "success": True,
                "message": "No messages to analyze",
                "insights": [],
                "recommendations": []
            }
        
        # Calculate basic metrics
        total_messages = len(messages)
        
        # Count messages by pattern
        pattern_counts = {}
        for msg in messages:
            pattern = msg.get("pattern", "request_response")
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Count messages by agent
        agent_sent_counts = {}
        agent_received_counts = {}
        
        for msg in messages:
            sender = msg.get("from")
            if sender:
                agent_sent_counts[sender] = agent_sent_counts.get(sender, 0) + 1
            
            recipient = msg.get("to")
            if recipient:
                if isinstance(recipient, str):
                    agent_received_counts[recipient] = agent_received_counts.get(recipient, 0) + 1
                elif isinstance(recipient, list):
                    for agent in recipient:
                        agent_received_counts[agent] = agent_received_counts.get(agent, 0) + 1
        
        # Calculate response times for request-response patterns
        response_times = []
        for request_id, data in self.pending_responses.items():
            if data["status"] == "completed" and data["response"]:
                request_time = datetime.fromisoformat(data["request"]["timestamp"])
                response_time = datetime.fromisoformat(data["response"]["timestamp"])
                delta = (response_time - request_time).total_seconds()
                response_times.append(delta)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Generate insights
        insights = [
            f"Total messages: {total_messages}",
            f"Most common communication pattern: {max(pattern_counts.items(), key=lambda x: x[1])[0] if pattern_counts else 'None'}",
            f"Average response time: {avg_response_time:.2f} seconds" if response_times else "No response time data available",
            f"Most active sender: {max(agent_sent_counts.items(), key=lambda x: x[1])[0] if agent_sent_counts else 'None'}",
            f"Most active recipient: {max(agent_received_counts.items(), key=lambda x: x[1])[0] if agent_received_counts else 'None'}"
        ]
        
        # Generate recommendations
        recommendations = []
        
        if avg_response_time > 10:
            recommendations.append("Consider optimizing agent response times")
        
        if "broadcast" in pattern_counts and pattern_counts["broadcast"] > total_messages * 0.5:
            recommendations.append("High broadcast usage detected; consider using more targeted communication")
        
        if len(agent_sent_counts) > 0 and len(agent_received_counts) > 0:
            max_sender = max(agent_sent_counts.items(), key=lambda x: x[1])
            max_receiver = max(agent_received_counts.items(), key=lambda x: x[1])
            
            if max_sender[1] > total_messages * 0.7:
                recommendations.append(f"Agent {max_sender[0]} is sending most messages; consider distributing workload")
            
            if max_receiver[1] > total_messages * 0.7:
                recommendations.append(f"Agent {max_receiver[0]} is receiving most messages; potential bottleneck")
        
        # Add default recommendations if none generated
        if not recommendations:
            recommendations = [
                "Implement priority levels for messages",
                "Add structured message formats for better agent understanding",
                "Consider implementing automatic follow-up for unresolved requests"
            ]
        
        return {
            "success": True,
            "message": "Communication patterns analyzed",
            "insights": insights,
            "recommendations": recommendations,
            "metrics": {
                "total_messages": total_messages,
                "pattern_distribution": pattern_counts,
                "agent_sent_counts": agent_sent_counts,
                "agent_received_counts": agent_received_counts,
                "avg_response_time": avg_response_time if response_times else None
            }
        }
