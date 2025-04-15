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


"""Agent-to-Agent (A2A) Framework.

This module implements the core A2A framework that enables agents to discover
each other's capabilities, establish trust, and communicate securely."""

from typing import Dict, Any, List, Optional, Union, Callable, Type
import logging
import asyncio
import uuid
from datetime import datetime
import json
import hashlib
import base64
import math

logger = logging.getLogger(__name__)

class Capability:
    """Description of an agent capability.
    
    A capability represents a specific skill or function that an agent can perform,
    including its parameters, performance metrics, and semantic description."""
    
    def __init__(self, capability_id: str, name: str, description: str, 
                 parameters: Optional[Dict[str, Any]] = None, 
                 performance_metrics: Optional[Dict[str, Any]] = None):
        """Initialize a capability.
        
        Args:
            capability_id: Unique identifier for the capability
            name: Human-readable name
            description: Detailed description of the capability
            parameters: Optional parameters that define the capability
            performance_metrics: Optional metrics about the capability's performance"""
        self.capability_id = capability_id
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.performance_metrics = performance_metrics or {}
        self.semantic_tags = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
    def add_semantic_tag(self, tag: str) -> None:
        """Add a semantic tag to the capability.
        
        Args:
            tag: Semantic tag to add"""
        if tag not in self.semantic_tags:
            self.semantic_tags.append(tag)
            self.updated_at = datetime.now().isoformat()
            
    def update_performance_metric(self, metric_name: str, value: Any) -> None:
        """Update a performance metric.
        
        Args:
            metric_name: Name of the metric to update
            value: New value for the metric"""
        self.performance_metrics[metric_name] = value
        self.updated_at = datetime.now().isoformat()
        
    def update_parameter(self, param_name: str, value: Any) -> None:
        """Update a capability parameter.
        
        Args:
            param_name: Name of the parameter to update
            value: New value for the parameter"""
        self.parameters[param_name] = value
        self.updated_at = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the capability to a dictionary.
        
        Returns:
            Dictionary representation of the capability"""
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "performance_metrics": self.performance_metrics,
            "semantic_tags": self.semantic_tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Capability':
        """Create a capability from a dictionary.
        
        Args:
            data: Dictionary representation of the capability
            
        Returns:
            The created capability"""
        capability = cls(
            capability_id=data["capability_id"],
            name=data["name"],
            description=data["description"],
            parameters=data.get("parameters", {}),
            performance_metrics=data.get("performance_metrics", {})
        )
        
        # Add semantic tags
        for tag in data.get("semantic_tags", []):
            capability.add_semantic_tag(tag)
            
        # Set timestamps if available
        if "created_at" in data:
            capability.created_at = data["created_at"]
            
        if "updated_at" in data:
            capability.updated_at = data["updated_at"]
            
        return capability

class CapabilityRegistry:
    """Registry for agent capabilities.
    
    The capability registry maintains a database of agent capabilities,
    allowing agents to discover and match capabilities for collaboration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the capability registry.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        self.capabilities: Dict[str, Capability] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.capability_expiry_days = self.config.get("capability_expiry_days", 30)
        
        logger.info("Capability Registry initialized")
        
    async def register_capability(self, agent_id: str, capability: Capability) -> Dict[str, Any]:
        """
        Register a capability for an agent.
        
        Args:
            agent_id: ID of the agent registering the capability
            capability: Capability to register
            
        Returns:
            Registration result
        """
        # Store the capability
        self.capabilities[capability.capability_id] = capability
        
        # Associate with the agent
        if agent_id not in self.agent_capabilities:
            self.agent_capabilities[agent_id] = []
            
        if capability.capability_id not in self.agent_capabilities[agent_id]:
            self.agent_capabilities[agent_id].append(capability.capability_id)
            
        logger.info(f"Registered capability {capability.capability_id} for agent {agent_id}")
        
        return {
            "success": True,
            "message": f"Capability {capability.name} registered successfully",
            "capability_id": capability.capability_id
        }
        
    async def unregister_capability(self, agent_id: str, capability_id: str) -> Dict[str, Any]:
        """
        Unregister a capability for an agent.
        
        Args:
            agent_id: ID of the agent
            capability_id: ID of the capability to unregister
            
        Returns:
            Unregistration result
        """
        # Check if the agent has this capability
        if agent_id not in self.agent_capabilities or capability_id not in self.agent_capabilities[agent_id]:
            return {
                "success": False,
                "message": f"Capability {capability_id} not registered for agent {agent_id}"
            }
            
        # Remove the capability from the agent
        self.agent_capabilities[agent_id].remove(capability_id)
        
        # Check if any other agents have this capability
        other_agents_have_capability = any(
            capability_id in caps for agent, caps in self.agent_capabilities.items() if agent != agent_id
        )
        
        # If no other agents have this capability, remove it from the registry
        if not other_agents_have_capability and capability_id in self.capabilities:
            del self.capabilities[capability_id]
            
        logger.info(f"Unregistered capability {capability_id} for agent {agent_id}")
        
        return {
            "success": True,
            "message": f"Capability {capability_id} unregistered successfully"
        }
        
    async def find_agents_with_capability(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find agents that have a specific capability.
        
        Args:
            criteria: Search criteria including tags, parameters, and performance requirements
            
        Returns:
            List of matching agents and their capabilities
        """
        matching_agents = {}
        
        # Extract search criteria
        tags = criteria.get("tags", [])
        name_keywords = criteria.get("name_keywords", [])
        description_keywords = criteria.get("description_keywords", [])
        required_parameters = criteria.get("parameters", {})
        performance_requirements = criteria.get("performance", {})
        
        # Check each agent's capabilities
        for agent_id, capability_ids in self.agent_capabilities.items():
            agent_matches = []
            
            for capability_id in capability_ids:
                capability = self.capabilities.get(capability_id)
                if not capability:
                    continue
                    
                # Check if capability matches the criteria
                if self._capability_matches_criteria(capability, tags, name_keywords, 
                                                    description_keywords, required_parameters, 
                                                    performance_requirements):
                    agent_matches.append({
                        "capability_id": capability_id,
                        "name": capability.name,
                        "match_score": self._calculate_match_score(capability, criteria)
                    })
                    
            if agent_matches:
                # Sort matches by score
                agent_matches.sort(key=lambda x: x["match_score"], reverse=True)
                matching_agents[agent_id] = agent_matches
                
        return {
            "success": True,
            "matching_agents": matching_agents,
            "count": len(matching_agents)
        }
        
    def _capability_matches_criteria(self, capability: Capability, 
                                    tags: List[str], 
                                    name_keywords: List[str],
                                    description_keywords: List[str],
                                    required_parameters: Dict[str, Any],
                                    performance_requirements: Dict[str, Any]) -> bool:
        """Check if a capability matches the search criteria.
        
        Args:
            capability: Capability to check
            tags: Required semantic tags
            name_keywords: Keywords that should appear in the name
            description_keywords: Keywords that should appear in the description
            required_parameters: Parameters that the capability should have
            performance_requirements: Performance metrics that the capability should meet
            
        Returns:
            Whether the capability matches the criteria"""
        # Check tags
        if tags and not any(tag in capability.semantic_tags for tag in tags):
            return False
            
        # Check name keywords
        if name_keywords and not any(keyword.lower() in capability.name.lower() for keyword in name_keywords):
            return False
            
        # Check description keywords
        if description_keywords and not any(keyword.lower() in capability.description.lower() for keyword in description_keywords):
            return False
            
        # Check required parameters
        for param_name, param_value in required_parameters.items():
            if param_name not in capability.parameters:
                return False
                
            # If the parameter value is a list, check if any value matches
            if isinstance(param_value, list):
                if not isinstance(capability.parameters[param_name], list):
                    if capability.parameters[param_name] not in param_value:
                        return False
                else:
                    if not any(v in param_value for v in capability.parameters[param_name]):
                        return False
            # Otherwise, check for exact match
            elif capability.parameters[param_name] != param_value:
                return False
                
        # Check performance requirements
        for metric_name, required_value in performance_requirements.items():
            if metric_name not in capability.performance_metrics:
                return False
                
            actual_value = capability.performance_metrics[metric_name]
            
            # Handle different types of comparisons
            if isinstance(required_value, dict):
                # Dictionary with comparison operators
                if "min" in required_value and actual_value < required_value["min"]:
                    return False
                if "max" in required_value and actual_value > required_value["max"]:
                    return False
                if "equals" in required_value and actual_value != required_value["equals"]:
                    return False
            else:
                # Direct comparison
                if actual_value != required_value:
                    return False
                    
        return True
        
    def _calculate_match_score(self, capability: Capability, criteria: Dict[str, Any]) -> float:
        """Calculate a match score for a capability against criteria.
        
        Args:
            capability: Capability to score
            criteria: Search criteria
            
        Returns:
            Match score (0-1)"""
        score_components = []
        
        # Score tags
        tags = criteria.get("tags", [])
        if tags:
            tag_matches = sum(1 for tag in tags if tag in capability.semantic_tags)
            tag_score = tag_matches / len(tags)
            score_components.append(("tags", tag_score, 0.3))
            
        # Score name keywords
        name_keywords = criteria.get("name_keywords", [])
        if name_keywords:
            name_matches = sum(1 for keyword in name_keywords if keyword.lower() in capability.name.lower())
            name_score = name_matches / len(name_keywords)
            score_components.append(("name", name_score, 0.2))
            
        # Score description keywords
        description_keywords = criteria.get("description_keywords", [])
        if description_keywords:
            desc_matches = sum(1 for keyword in description_keywords if keyword.lower() in capability.description.lower())
            desc_score = desc_matches / len(description_keywords)
            score_components.append(("description", desc_score, 0.1))
            
        # Score parameters
        required_parameters = criteria.get("parameters", {})
        if required_parameters:
            param_matches = sum(1 for param_name in required_parameters if param_name in capability.parameters)
            param_score = param_matches / len(required_parameters)
            score_components.append(("parameters", param_score, 0.2))
            
        # Score performance
        performance_requirements = criteria.get("performance", {})
        if performance_requirements:
            perf_scores = []
            
            for metric_name, required_value in performance_requirements.items():
                if metric_name not in capability.performance_metrics:
                    perf_scores.append(0)
                    continue
                    
                actual_value = capability.performance_metrics[metric_name]
                
                # Handle different types of comparisons
                if isinstance(required_value, dict):
                    # Dictionary with comparison operators
                    if "min" in required_value:
                        min_val = required_value["min"]
                        if actual_value < min_val:
                            perf_scores.append(0)
                        else:
                            # Score based on how much it exceeds the minimum
                            perf_scores.append(min(1.0, actual_value / min_val))
                    elif "max" in required_value:
                        max_val = required_value["max"]
                        if actual_value > max_val:
                            perf_scores.append(0)
                        else:
                            # Score based on how close it is to the maximum
                            perf_scores.append(min(1.0, max_val / actual_value if actual_value > 0 else 0))
                    elif "equals" in required_value:
                        equals_val = required_value["equals"]
                        # Score based on how close it is to the target value
                        perf_scores.append(1.0 if actual_value == equals_val else 0.0)
                else:
                    # Direct comparison
                    perf_scores.append(1.0 if actual_value == required_value else 0.0)
                    
            perf_score = sum(perf_scores) / len(perf_scores) if perf_scores else 0
            score_components.append(("performance", perf_score, 0.2))
            
        # Calculate weighted score
        if score_components:
            weighted_score = sum(score * weight for _, score, weight in score_components)
            total_weight = sum(weight for _, _, weight in score_components)
            return weighted_score / total_weight if total_weight > 0 else 0
        else:
            return 0.5  # Default score if no criteria specified
        
    async def get_agent_capabilities(self, agent_id: str) -> Dict[str, Any]:
        """
        Get all capabilities for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of agent capabilities
        """
        if agent_id not in self.agent_capabilities:
            return {
                "success": True,
                "message": f"No capabilities registered for agent {agent_id}",
                "capabilities": []
            }
            
        capabilities = []
        
        for capability_id in self.agent_capabilities[agent_id]:
            capability = self.capabilities.get(capability_id)
            if capability:
                capabilities.append(capability.to_dict())
                
        return {
            "success": True,
            "message": f"Retrieved {len(capabilities)} capabilities for agent {agent_id}",
            "capabilities": capabilities
        }
        
    async def update_capability(self, agent_id: str, capability_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a capability.
        
        Args:
            agent_id: ID of the agent
            capability_id: ID of the capability to update
            updates: Fields to update
            
        Returns:
            Update result
        """
        # Check if the agent has this capability
        if agent_id not in self.agent_capabilities or capability_id not in self.agent_capabilities[agent_id]:
            return {
                "success": False,
                "message": f"Capability {capability_id} not registered for agent {agent_id}"
            }
            
        # Get the capability
        capability = self.capabilities.get(capability_id)
        if not capability:
            return {
                "success": False,
                "message": f"Capability {capability_id} not found in registry"
            }
            
        # Update fields
        if "name" in updates:
            capability.name = updates["name"]
            
        if "description" in updates:
            capability.description = updates["description"]
            
        if "parameters" in updates:
            for param_name, param_value in updates["parameters"].items():
                capability.update_parameter(param_name, param_value)
                
        if "performance_metrics" in updates:
            for metric_name, metric_value in updates["performance_metrics"].items():
                capability.update_performance_metric(metric_name, metric_value)
                
        if "semantic_tags" in updates:
            for tag in updates["semantic_tags"]:
                capability.add_semantic_tag(tag)
                
        capability.updated_at = datetime.now().isoformat()
        
        logger.info(f"Updated capability {capability_id} for agent {agent_id}")
        
        return {
            "success": True,
            "message": f"Capability {capability_id} updated successfully",
            "capability": capability.to_dict()
        }
        
    async def clean_expired_capabilities(self) -> Dict[str, Any]:
        """
        Clean up expired capabilities.
        
        Returns:
            Cleanup result
        """
        now = datetime.now()
        expiry_seconds = self.capability_expiry_days * 24 * 60 * 60  # Convert days to seconds
        
        expired_capabilities = []
        
        for capability_id, capability in list(self.capabilities.items()):
            try:
                updated = datetime.fromisoformat(capability.updated_at)
                age_seconds = (now - updated).total_seconds()
                
                if age_seconds > expiry_seconds:
                    # Remove from all agents
                    for agent_id in list(self.agent_capabilities.keys()):
                        if capability_id in self.agent_capabilities[agent_id]:
                            self.agent_capabilities[agent_id].remove(capability_id)
                            
                    # Remove from capabilities
                    del self.capabilities[capability_id]
                    
                    expired_capabilities.append(capability_id)
            except (ValueError, TypeError):
                # Skip if date parsing fails
                pass
                
        logger.info(f"Cleaned up {len(expired_capabilities)} expired capabilities")
        
        return {
            "success": True,
            "message": f"Cleaned up {len(expired_capabilities)} expired capabilities",
            "expired_capabilities": expired_capabilities
        }

class TrustManager:
    """Manages trust and reputation between agents.
    
    The trust manager tracks interactions between agents and calculates
    trust scores based on interaction outcomes."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the trust manager.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        self.trust_scores: Dict[str, Dict[str, float]] = {}
        self.interaction_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Default configuration
        self.default_trust_score = self.config.get("default_trust_score", 0.7)
        self.min_interactions = self.config.get("min_interactions", 5)
        self.decay_factor = self.config.get("decay_factor", 0.05)
        self.max_history_per_pair = self.config.get("max_history_per_pair", 100)
        
        logger.info("Trust Manager initialized")
        
    async def record_interaction(self, source_agent: str, target_agent: str, 
                                interaction_type: str, outcome: str, 
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record an interaction between agents.
        
        Args:
            source_agent: ID of the source agent
            target_agent: ID of the target agent
            interaction_type: Type of interaction
            outcome: Outcome of the interaction ("success", "failure", "partial")
            context: Optional context information
            
        Returns:
            Recording result
        """
        # Create interaction record
        interaction = {
            "source_agent": source_agent,
            "target_agent": target_agent,
            "interaction_type": interaction_type,
            "outcome": outcome,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Create pair key for history
        pair_key = f"{source_agent}:{target_agent}"
        
        # Add to history
        if pair_key not in self.interaction_history:
            self.interaction_history[pair_key] = []
            
        self.interaction_history[pair_key].append(interaction)
        
        # Limit history size
        if len(self.interaction_history[pair_key]) > self.max_history_per_pair:
            self.interaction_history[pair_key] = self.interaction_history[pair_key][-self.max_history_per_pair:]
            
        # Update trust score
        await self.calculate_trust_score(source_agent, target_agent)
        
        logger.info(f"Recorded {outcome} {interaction_type} interaction from {source_agent} to {target_agent}")
        
        return {
            "success": True,
            "message": "Interaction recorded successfully"
        }
        
    async def calculate_trust_score(self, source_agent: str, target_agent: str) -> float:
        """
        Calculate the trust score between two agents.
        
        Args:
            source_agent: ID of the source agent
            target_agent: ID of the target agent
            
        Returns:
            Trust score (0-1)
        """
        pair_key = f"{source_agent}:{target_agent}"
        
        # If no interactions, use default score
        if pair_key not in self.interaction_history or not self.interaction_history[pair_key]:
            score = self.default_trust_score
        else:
            interactions = self.interaction_history[pair_key]
            
            # If fewer than minimum interactions, blend with default score
            if len(interactions) < self.min_interactions:
                blend_factor = len(interactions) / self.min_interactions
                calculated_score = self._calculate_from_interactions(interactions)
                score = (calculated_score * blend_factor) + (self.default_trust_score * (1 - blend_factor))
            else:
                score = self._calculate_from_interactions(interactions)
                
        # Store the score
        if source_agent not in self.trust_scores:
            self.trust_scores[source_agent] = {}
            
        self.trust_scores[source_agent][target_agent] = score
        
        return score
        
    def _calculate_from_interactions(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate trust score from interaction history.
        
        Args:
            interactions: List of interaction records
            
        Returns:
            Trust score (0-1)"""
        if not interactions:
            return self.default_trust_score
            
        # Sort by timestamp
        sorted_interactions = sorted(interactions, key=lambda x: x["timestamp"])
        
        # Calculate time-weighted score
        total_weight = 0
        weighted_sum = 0
        
        for i, interaction in enumerate(sorted_interactions):
            # More recent interactions have higher weight
            recency_weight = 1.0 - (self.decay_factor * (len(sorted_interactions) - i - 1))
            recency_weight = max(0.1, recency_weight)  # Ensure minimum weight
            
            # Convert outcome to score
            if interaction["outcome"] == "success":
                outcome_score = 1.0
            elif interaction["outcome"] == "partial":
                outcome_score = 0.5
            else:  # failure
                outcome_score = 0.0
                
            # Apply weight
            weighted_sum += outcome_score * recency_weight
            total_weight += recency_weight
            
        # Calculate final score
        return weighted_sum / total_weight if total_weight > 0 else self.default_trust_score
        
    async def get_trust_score(self, source_agent: str, target_agent: str) -> Dict[str, Any]:
        """
        Get the trust score between two agents.
        
        Args:
            source_agent: ID of the source agent
            target_agent: ID of the target agent
            
        Returns:
            Trust score information
        """
        # Calculate if not already calculated
        if source_agent not in self.trust_scores or target_agent not in self.trust_scores[source_agent]:
            score = await self.calculate_trust_score(source_agent, target_agent)
        else:
            score = self.trust_scores[source_agent][target_agent]
            
        # Get interaction count
        pair_key = f"{source_agent}:{target_agent}"
        interaction_count = len(self.interaction_history.get(pair_key, []))
        
        return {
            "success": True,
            "trust_score": score,
            "interaction_count": interaction_count,
            "confidence": min(1.0, interaction_count / self.min_interactions)
        }
        
    async def get_agent_reputation(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the overall reputation of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Reputation information
        """
        # Collect all trust scores for this agent
        scores = []
        
        for source, targets in self.trust_scores.items():
            if agent_id in targets:
                scores.append(targets[agent_id])
                
        # Calculate average reputation
        if scores:
            reputation = sum(scores) / len(scores)
            confidence = min(1.0, len(scores) / 5)  # Confidence based on number of agents rating this agent
        else:
            reputation = self.default_trust_score
            confidence = 0.0
            
        return {
            "success": True,
            "reputation": reputation,
            "rating_count": len(scores),
            "confidence": confidence
        }
        
    async def update_trust_model(self) -> Dict[str, Any]:
        """
        Update all trust scores based on interaction history.
        
        Returns:
            Update result
        """
        updated_count = 0
        
        # Recalculate all trust scores
        for pair_key in self.interaction_history:
            source_agent, target_agent = pair_key.split(":")
            await self.calculate_trust_score(source_agent, target_agent)
            updated_count += 1
            
        logger.info(f"Updated {updated_count} trust relationships")
        
        return {
            "success": True,
            "message": f"Updated {updated_count} trust relationships"
        }

class SecurityManager:
    """Manages security for agent communications.
    
    The security manager handles authentication, authorization, and
    secure message passing between agents."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the security manager.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        self.agent_credentials: Dict[str, Dict[str, Any]] = {}
        self.access_policies: Dict[str, Dict[str, Any]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        # Default configuration
        self.message_encryption = self.config.get("message_encryption", True)
        self.authentication_required = self.config.get("authentication_required", True)
        self.audit_logging = self.config.get("audit_logging", True)
        self.max_audit_log_size = self.config.get("max_audit_log_size", 10000)
        
        logger.info("Security Manager initialized")
        
    async def register_agent(self, agent_id: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register an agent with the security manager.
        
        Args:
            agent_id: ID of the agent
            credentials: Agent credentials
            
        Returns:
            Registration result
        """
        # Generate a secure token for the agent
        token = self._generate_token(agent_id)
        
        # Store credentials
        self.agent_credentials[agent_id] = {
            "token": token,
            "created_at": datetime.now().isoformat(),
            "last_authenticated": None,
            "credentials": credentials
        }
        
        # Create default access policy
        self.access_policies[agent_id] = {
            "default_action": "allow",
            "rules": []
        }
        
        logger.info(f"Registered agent {agent_id} with security manager")
        
        return {
            "success": True,
            "message": "Agent registered successfully",
            "token": token
        }
        
    def _generate_token(self, agent_id: str) -> str:
        """Generate a secure token for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Secure token"""
        # Create a unique token based on agent ID and timestamp
        timestamp = datetime.now().isoformat()
        token_base = f"{agent_id}:{timestamp}:{uuid.uuid4().hex}"
        
        # Hash the token
        token_hash = hashlib.sha256(token_base.encode()).digest()
        
        # Encode as base64
        token = base64.urlsafe_b64encode(token_hash).decode()
        
        return token
        
    async def authenticate_agent(self, agent_id: str, token: str) -> Dict[str, Any]:
        """
        Authenticate an agent.
        
        Args:
            agent_id: ID of the agent
            token: Authentication token
            
        Returns:
            Authentication result
        """
        # Check if agent is registered
        if agent_id not in self.agent_credentials:
            return {
                "success": False,
                "message": "Agent not registered"
            }
            
        # Check token
        if self.agent_credentials[agent_id]["token"] != token:
            # Log failed authentication attempt
            if self.audit_logging:
                self._log_operation(agent_id, "authenticate", "system", "failure", {
                    "reason": "Invalid token"
                })
                
            return {
                "success": False,
                "message": "Invalid token"
            }
            
        # Update last authentication time
        self.agent_credentials[agent_id]["last_authenticated"] = datetime.now().isoformat()
        
        # Log successful authentication
        if self.audit_logging:
            self._log_operation(agent_id, "authenticate", "system", "success")
            
        return {
            "success": True,
            "message": "Authentication successful"
        }
        
    async def authorize_operation(self, agent_id: str, operation: str, resource: str) -> Dict[str, Any]:
        """
        Authorize an operation on a resource.
        
        Args:
            agent_id: ID of the agent
            operation: Operation to perform
            resource: Resource to operate on
            
        Returns:
            Authorization result
        """
        # Check if agent is registered
        if agent_id not in self.agent_credentials:
            return {
                "success": False,
                "message": "Agent not registered"
            }
            
        # Get access policy
        policy = self.access_policies.get(agent_id, {"default_action": "deny", "rules": []})
        
        # Check rules
        for rule in policy["rules"]:
            # Check if rule applies to this operation and resource
            if (rule.get("operation") == operation or rule.get("operation") == "*") and \
               (rule.get("resource") == resource or rule.get("resource") == "*"):
                
                # Log authorization decision
                if self.audit_logging:
                    self._log_operation(agent_id, "authorize", resource, 
                                       "success" if rule["action"] == "allow" else "failure", {
                                           "operation": operation,
                                           "rule": rule
                                       })
                
                return {
                    "success": rule["action"] == "allow",
                    "message": f"Operation {operation} on {resource} {'allowed' if rule['action'] == 'allow' else 'denied'} by rule"
                }
                
        # No matching rules, use default action
        default_action = policy["default_action"]
        
        # Log authorization decision
        if self.audit_logging:
            self._log_operation(agent_id, "authorize", resource, 
                               "success" if default_action == "allow" else "failure", {
                                   "operation": operation,
                                   "default_action": default_action
                               })
        
        return {
            "success": default_action == "allow",
            "message": f"Operation {operation} on {resource} {'allowed' if default_action == 'allow' else 'denied'} by default"
        }
        
    async def secure_message(self, message: Dict[str, Any], sender: str, recipient: str) -> Dict[str, Any]:
        """
        Secure a message for transmission.
        
        Args:
            message: Message to secure
            sender: ID of the sender
            recipient: ID of the recipient
            
        Returns:
            Secured message
        """
        # Check if sender is registered
        if sender not in self.agent_credentials:
            return {
                "success": False,
                "message": "Sender not registered"
            }
            
        # Check if recipient is registered
        if recipient not in self.agent_credentials:
            return {
                "success": False,
                "message": "Recipient not registered"
            }
            
        # Create secured message
        secured_message = {
            "sender": sender,
            "recipient": recipient,
            "timestamp": datetime.now().isoformat(),
            "message_id": str(uuid.uuid4()),
            "content": message
        }
        
        # Add authentication information
        secured_message["auth"] = {
            "sender_token": self.agent_credentials[sender]["token"]
        }
        
        # Encrypt message if enabled
        if self.message_encryption:
            # In a real implementation, this would use proper encryption
            # For this example, we'll just mark it as encrypted
            secured_message["encrypted"] = True
            
        # Log message sending
        if self.audit_logging:
            self._log_operation(sender, "send_message", recipient, "success", {
                "message_id": secured_message["message_id"]
            })
            
        return {
            "success": True,
            "secured_message": secured_message
        }
        
    async def verify_message(self, secured_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify and extract a secured message.
        
        Args:
            secured_message: Secured message to verify
            
        Returns:
            Verification result with extracted message
        """
        # Check required fields
        required_fields = ["sender", "recipient", "timestamp", "message_id", "content", "auth"]
        for field in required_fields:
            if field not in secured_message:
                return {
                    "success": False,
                    "message": f"Missing required field: {field}"
                }
                
        sender = secured_message["sender"]
        recipient = secured_message["recipient"]
        
        # Check if sender is registered
        if sender not in self.agent_credentials:
            return {
                "success": False,
                "message": "Sender not registered"
            }
            
        # Check if recipient is registered
        if recipient not in self.agent_credentials:
            return {
                "success": False,
                "message": "Recipient not registered"
            }
            
        # Verify sender token
        if self.authentication_required:
            sender_token = secured_message["auth"].get("sender_token")
            if sender_token != self.agent_credentials[sender]["token"]:
                # Log authentication failure
                if self.audit_logging:
                    self._log_operation(recipient, "verify_message", sender, "failure", {
                        "message_id": secured_message["message_id"],
                        "reason": "Invalid sender token"
                    })
                    
                return {
                    "success": False,
                    "message": "Invalid sender token"
                }
                
        # Decrypt message if encrypted
        content = secured_message["content"]
        if secured_message.get("encrypted", False):
            # In a real implementation, this would use proper decryption
            # For this example, we'll just use the content as is
            pass
            
        # Log message verification
        if self.audit_logging:
            self._log_operation(recipient, "verify_message", sender, "success", {
                "message_id": secured_message["message_id"]
            })
            
        return {
            "success": True,
            "sender": sender,
            "recipient": recipient,
            "timestamp": secured_message["timestamp"],
            "message_id": secured_message["message_id"],
            "content": content
        }
        
    def _log_operation(self, agent_id: str, operation: str, resource: str, 
                      outcome: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log an operation in the audit log.
        
        Args:
            agent_id: ID of the agent
            operation: Operation performed
            resource: Resource operated on
            outcome: Outcome of the operation
            details: Optional details about the operation"""
        if not self.audit_logging:
            return
            
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "operation": operation,
            "resource": resource,
            "outcome": outcome,
            "details": details or {}
        }
        
        # Add to audit log
        self.audit_log.append(log_entry)
        
        # Limit audit log size
        if len(self.audit_log) > self.max_audit_log_size:
            self.audit_log = self.audit_log[-self.max_audit_log_size:]
            
    async def get_audit_log(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get entries from the audit log.
        
        Args:
            filters: Optional filters for the log entries
            
        Returns:
            Filtered audit log entries
        """
        if not self.audit_logging:
            return {
                "success": False,
                "message": "Audit logging is disabled"
            }
            
        filters = filters or {}
        
        # Apply filters
        filtered_log = self.audit_log
        
        if "agent_id" in filters:
            filtered_log = [entry for entry in filtered_log if entry["agent_id"] == filters["agent_id"]]
            
        if "operation" in filters:
            filtered_log = [entry for entry in filtered_log if entry["operation"] == filters["operation"]]
            
        if "resource" in filters:
            filtered_log = [entry for entry in filtered_log if entry["resource"] == filters["resource"]]
            
        if "outcome" in filters:
            filtered_log = [entry for entry in filtered_log if entry["outcome"] == filters["outcome"]]
            
        if "start_time" in filters:
            try:
                start_time = datetime.fromisoformat(filters["start_time"])
                filtered_log = [
                    entry for entry in filtered_log 
                    if datetime.fromisoformat(entry["timestamp"]) >= start_time
                ]
            except (ValueError, TypeError):
                pass
                
        if "end_time" in filters:
            try:
                end_time = datetime.fromisoformat(filters["end_time"])
                filtered_log = [
                    entry for entry in filtered_log 
                    if datetime.fromisoformat(entry["timestamp"]) <= end_time
                ]
            except (ValueError, TypeError):
                pass
                
        return {
            "success": True,
            "log_entries": filtered_log,
            "count": len(filtered_log)
        }
        
    async def add_access_rule(self, agent_id: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an access rule for an agent.
        
        Args:
            agent_id: ID of the agent
            rule: Access rule to add
            
        Returns:
            Rule addition result
        """
        # Check if agent is registered
        if agent_id not in self.agent_credentials:
            return {
                "success": False,
                "message": "Agent not registered"
            }
            
        # Validate rule
        required_fields = ["operation", "resource", "action"]
        for field in required_fields:
            if field not in rule:
                return {
                    "success": False,
                    "message": f"Missing required field in rule: {field}"
                }
                
        if rule["action"] not in ["allow", "deny"]:
            return {
                "success": False,
                "message": "Invalid action in rule: must be 'allow' or 'deny'"
            }
            
        # Add rule to policy
        if agent_id not in self.access_policies:
            self.access_policies[agent_id] = {
                "default_action": "deny",
                "rules": []
            }
            
        self.access_policies[agent_id]["rules"].append(rule)
        
        logger.info(f"Added access rule for agent {agent_id}: {rule}")
        
        return {
            "success": True,
            "message": "Access rule added successfully"
        }
        
    async def set_default_action(self, agent_id: str, default_action: str) -> Dict[str, Any]:
        """
        Set the default action for an agent's access policy.
        
        Args:
            agent_id: ID of the agent
            default_action: Default action ("allow" or "deny")
            
        Returns:
            Update result
        """
        # Check if agent is registered
        if agent_id not in self.agent_credentials:
            return {
                "success": False,
                "message": "Agent not registered"
            }
            
        # Validate default action
        if default_action not in ["allow", "deny"]:
            return {
                "success": False,
                "message": "Invalid default action: must be 'allow' or 'deny'"
            }
            
        # Update default action
        if agent_id not in self.access_policies:
            self.access_policies[agent_id] = {
                "default_action": default_action,
                "rules": []
            }
        else:
            self.access_policies[agent_id]["default_action"] = default_action
            
        logger.info(f"Set default action for agent {agent_id} to {default_action}")
        
        return {
            "success": True,
            "message": f"Default action set to {default_action}"
        }

class AgentIdentity:
    """Represents an agent's identity.
    
    An agent identity includes the agent's ID, role, capabilities,
    and security credentials."""
    
    def __init__(self, agent_id: str, role: str, name: Optional[str] = None, 
                description: Optional[str] = None):
        """Initialize an agent identity.
        
        Args:
            agent_id: Unique identifier for the agent
            role: Role of the agent
            name: Optional human-readable name
            description: Optional description"""
        self.agent_id = agent_id
        self.role = role
        self.name = name or f"Agent {agent_id}"
        self.description = description or f"{role.capitalize()} agent"
        self.capabilities = []
        self.security_token = None
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the identity to a dictionary.
        
        Returns:
            Dictionary representation of the identity"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "name": self.name,
            "description": self.description,
            "capability_count": len(self.capabilities),
            "created_at": self.created_at
        }
        
    def to_reference(self) -> Dict[str, str]:
        """Create a reference to this agent for use in messages.
        
        Returns:
            Agent reference dictionary"""
        return {
            "id": self.agent_id,
            "role": self.role
        }

class A2AFramework:
    """Core framework for Agent-to-Agent communication.
    
    The A2A framework integrates capability discovery, trust management,
    and secure communication for agent collaboration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the A2A framework.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        
        # Initialize components
        self.capability_registry = CapabilityRegistry(self.config.get("capability_registry"))
        self.trust_manager = TrustManager(self.config.get("trust"))
        self.security_manager = SecurityManager(self.config.get("security"))
        
        # Agent identities
        self.agent_identities: Dict[str, AgentIdentity] = {}
        
        logger.info("A2A Framework initialized")
        
    async def register_agent(self, agent_id: str, role: str, name: Optional[str] = None, 
                           description: Optional[str] = None) -> Dict[str, Any]:
        """
        Register an agent with the framework.
        
        Args:
            agent_id: Unique identifier for the agent
            role: Role of the agent
            name: Optional human-readable name
            description: Optional description
            
        Returns:
            Registration result
        """
        # Create agent identity
        identity = AgentIdentity(agent_id, role, name, description)
        
        # Register with security manager
        security_result = await self.security_manager.register_agent(agent_id, {
            "role": role
        })
        
        if not security_result["success"]:
            return {
                "success": False,
                "message": f"Failed to register with security manager: {security_result['message']}"
            }
            
        # Store security token
        identity.security_token = security_result["token"]
        
        # Store identity
        self.agent_identities[agent_id] = identity
        
        logger.info(f"Registered agent {agent_id} with role {role}")
        
        return {
            "success": True,
            "message": "Agent registered successfully",
            "agent_id": agent_id,
            "security_token": identity.security_token
        }
        
    async def register_capability(self, agent_id: str, capability: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a capability for an agent.
        
        Args:
            agent_id: ID of the agent
            capability: Capability information
            
        Returns:
            Registration result
        """
        # Check if agent is registered
        if agent_id not in self.agent_identities:
            return {
                "success": False,
                "message": "Agent not registered"
            }
            
        # Create capability object
        capability_obj = Capability(
            capability_id=capability.get("capability_id", f"cap_{uuid.uuid4().hex[:8]}"),
            name=capability["name"],
            description=capability["description"],
            parameters=capability.get("parameters"),
            performance_metrics=capability.get("performance_metrics")
        )
        
        # Add semantic tags
        for tag in capability.get("semantic_tags", []):
            capability_obj.add_semantic_tag(tag)
            
        # Register with capability registry
        result = await self.capability_registry.register_capability(agent_id, capability_obj)
        
        if result["success"]:
            # Add to agent's capabilities
            self.agent_identities[agent_id].capabilities.append(capability_obj.capability_id)
            
        return result
        
    async def find_capable_agents(self, criteria: Dict[str, Any], 
                                trust_source: Optional[str] = None,
                                min_trust_score: float = 0.5) -> Dict[str, Any]:
        """
        Find agents with specific capabilities.
        
        Args:
            criteria: Capability search criteria
            trust_source: Optional agent ID to use for trust filtering
            min_trust_score: Minimum trust score for inclusion
            
        Returns:
            List of matching agents
        """
        # Find agents with matching capabilities
        capability_result = await self.capability_registry.find_agents_with_capability(criteria)
        
        if not capability_result["success"]:
            return capability_result
            
        matching_agents = capability_result["matching_agents"]
        
        # If trust filtering is requested
        if trust_source:
            filtered_agents = {}
            
            for agent_id, capabilities in matching_agents.items():
                # Get trust score
                trust_result = await self.trust_manager.get_trust_score(trust_source, agent_id)
                
                # Include if trust score is sufficient
                if trust_result["success"] and trust_result["trust_score"] >= min_trust_score:
                    filtered_agents[agent_id] = capabilities
                    
            matching_agents = filtered_agents
            
        # Add agent identity information
        result_agents = {}
        
        for agent_id, capabilities in matching_agents.items():
            if agent_id in self.agent_identities:
                identity = self.agent_identities[agent_id]
                result_agents[agent_id] = {
                    "identity": identity.to_dict(),
                    "capabilities": capabilities
                }
            
        return {
            "success": True,
            "matching_agents": result_agents,
            "count": len(result_agents)
        }
        
    async def send_message(self, sender_id: str, recipient_id: str, 
                         message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message from one agent to another.
        
        Args:
            sender_id: ID of the sender
            recipient_id: ID of the recipient
            message: Message content
            
        Returns:
            Message sending result
        """
        # Check if sender is registered
        if sender_id not in self.agent_identities:
            return {
                "success": False,
                "message": "Sender not registered"
            }
            
        # Check if recipient is registered
        if recipient_id not in self.agent_identities:
            return {
                "success": False,
                "message": "Recipient not registered"
            }
            
        # Secure the message
        secure_result = await self.security_manager.secure_message(message, sender_id, recipient_id)
        
        if not secure_result["success"]:
            return secure_result
            
        secured_message = secure_result["secured_message"]
        
        # In a real implementation, this would send the message through a transport layer
        # For this example, we'll just return the secured message
        
        logger.info(f"Sent message from {sender_id} to {recipient_id}")
        
        return {
            "success": True,
            "message": "Message sent successfully",
            "secured_message": secured_message
        }
        
    async def receive_message(self, recipient_id: str, secured_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive and process a message.
        
        Args:
            recipient_id: ID of the recipient
            secured_message: Secured message to process
            
        Returns:
            Message processing result
        """
        # Check if recipient is registered
        if recipient_id not in self.agent_identities:
            return {
                "success": False,
                "message": "Recipient not registered"
            }
            
        # Verify the message
        verify_result = await self.security_manager.verify_message(secured_message)
        
        if not verify_result["success"]:
            return verify_result
            
        # Check that the recipient matches
        if verify_result["recipient"] != recipient_id:
            return {
                "success": False,
                "message": "Message recipient mismatch"
            }
            
        sender_id = verify_result["sender"]
        
        # Record interaction for trust
        await self.trust_manager.record_interaction(
            recipient_id, sender_id, 
            "message_received", "success"
        )
        
        logger.info(f"Received message from {sender_id} to {recipient_id}")
        
        return {
            "success": True,
            "sender": sender_id,
            "message_id": verify_result["message_id"],
            "content": verify_result["content"]
        }
        
    async def get_agent_capabilities(self, agent_id: str) -> Dict[str, Any]:
        """
        Get capabilities for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent capabilities
        """
        return await self.capability_registry.get_agent_capabilities(agent_id)
        
    async def get_agent_trust(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """
        Get trust information between agents.
        
        Args:
            source_id: ID of the source agent
            target_id: ID of the target agent
            
        Returns:
            Trust information
        """
        return await self.trust_manager.get_trust_score(source_id, target_id)
        
    async def get_agent_reputation(self, agent_id: str) -> Dict[str, Any]:
        """
        Get reputation for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Reputation information
        """
        return await self.trust_manager.get_agent_reputation(agent_id)
        
    async def maintenance_tasks(self) -> Dict[str, Any]:
        """
        Perform maintenance tasks.
        
        Returns:
            Maintenance results
        """
        # Clean expired capabilities
        capability_result = await self.capability_registry.clean_expired_capabilities()
        
        # Update trust model
        trust_result = await self.trust_manager.update_trust_model()
        
        return {
            "success": True,
            "capability_maintenance": capability_result,
            "trust_maintenance": trust_result
        }
