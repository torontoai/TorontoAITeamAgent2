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


"""Enhanced Agent Adaptation Layer for TORONTO AI Team Agent.

This module provides an enhanced adaptation layer that integrates knowledge retrieval
capabilities into agent roles with advanced query formulation, personalization,
and knowledge feedback mechanisms."""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import json
import asyncio
import re
import time
import uuid
import numpy as np
from collections import deque

from ..agent.base_agent import BaseAgent
from .knowledge_extraction import pipeline as knowledge_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentAdaptationLayer:
    """Enhanced adaptation layer that integrates knowledge retrieval capabilities into agent roles."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Agent Adaptation Layer.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        
        # Default configuration values
        self.knowledge_weight = self.config.get("knowledge_weight", 0.7)
        self.max_knowledge_chunks = self.config.get("max_knowledge_chunks", 3)
        self.context_window_size = self.config.get("context_window_size", 5)
        self.enable_knowledge_feedback = self.config.get("enable_knowledge_feedback", True)
        self.enable_personalization = self.config.get("enable_personalization", True)
        self.enable_multi_agent_sharing = self.config.get("enable_multi_agent_sharing", True)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.6)
        
        # Initialize context tracking
        self.agent_contexts = {}
        
        # Initialize knowledge sharing
        self.shared_knowledge = {}
        
        # Initialize personalization profiles
        self.agent_profiles = {}
        
        # Knowledge usage statistics
        self.knowledge_usage_stats = {
            "total_queries": 0,
            "successful_retrievals": 0,
            "by_role": {},
            "by_section": {},
            "feedback": {
                "positive": 0,
                "negative": 0
            }
        }
        
        logger.info("Enhanced Agent Adaptation Layer initialized")
    
    def patch_agent_class(self, agent_class: type) -> type:
        """Patch an agent class to integrate knowledge retrieval capabilities.
        
        Args:
            agent_class: The agent class to patch
            
        Returns:
            Patched agent class"""
        original_init = agent_class.__init__
        original_process_task = agent_class.process_task
        
        def patched_init(self, config=None, *args, **kwargs):
            # Call original init
            original_init(self, config, *args, **kwargs)
            
            # Add knowledge retrieval capabilities
            self.knowledge_enabled = True
            self.knowledge_context = []
            self.knowledge_feedback = []
            self.knowledge_stats = {
                "queries": 0,
                "retrievals": 0,
                "sections_used": set(),
                "feedback": {
                    "positive": 0,
                    "negative": 0
                }
            }
            
            # Initialize personalization profile
            if hasattr(self, "role"):
                self._initialize_personalization_profile()
            
            # Add to capabilities
            if hasattr(self, "capabilities"):
                self.capabilities.append("Knowledge-enhanced reasoning")
            
            logger.info(f"Added enhanced knowledge capabilities to {self.role if hasattr(self, 'role') else 'unknown'} agent")
        
        async def patched_process_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
            # Enhance task with relevant knowledge
            enhanced_params = self._enhance_with_knowledge(params)
            
            # Call original process_task with enhanced params
            result = await original_process_task(self, enhanced_params)
            
            # Add knowledge attribution if knowledge was used
            if hasattr(self, "knowledge_context") and self.knowledge_context:
                result["knowledge_attribution"] = {
                    "used": True,
                    "sources": [item["source"] for item in self.knowledge_context[-self.max_knowledge_chunks:]]
                }
            
            # Process knowledge feedback
            if hasattr(self, "knowledge_enabled") and self.knowledge_enabled:
                self._process_knowledge_feedback(result)
                
                # Share valuable knowledge with other agents if enabled
                if self.enable_multi_agent_sharing:
                    self._share_valuable_knowledge(result)
            
            return result
        
        def _enhance_with_knowledge(self, params: Dict[str, Any]) -> Dict[str, Any]:
            """Enhance task parameters with relevant knowledge.
            
            Args:
                params: Original task parameters
                
            Returns:
                Enhanced task parameters"""
            if not hasattr(self, "knowledge_enabled") or not self.knowledge_enabled:
                return params
            
            # Create a copy of the parameters
            enhanced_params = params.copy()
            
            # Extract task description
            task_description = params.get("description", "")
            if not task_description:
                return enhanced_params
            
            # Update context with current task
            if hasattr(self, "knowledge_context"):
                self.knowledge_context.append({
                    "type": "task",
                    "content": task_description,
                    "timestamp": time.time()
                })
                # Trim context if it gets too long
                if len(self.knowledge_context) > self.context_window_size * 2:
                    self.knowledge_context = self.knowledge_context[-self.context_window_size:]
            
            # Formulate query from task and context
            query = self._formulate_knowledge_query(task_description)
            
            # Retrieve relevant knowledge
            knowledge_chunks = self._retrieve_knowledge(query)
            
            if knowledge_chunks:
                # Format knowledge for inclusion
                knowledge_text = self._format_knowledge_for_task(knowledge_chunks)
                
                # Add knowledge to parameters
                enhanced_params["knowledge_context"] = knowledge_text
                
                # Update stats
                if hasattr(self, "knowledge_stats"):
                    self.knowledge_stats["retrievals"] += 1
                    for chunk in knowledge_chunks:
                        if "document" in chunk and "section" in chunk["document"]:
                            self.knowledge_stats["sections_used"].add(chunk["document"]["section"])
            
            # Update query stats
            if hasattr(self, "knowledge_stats"):
                self.knowledge_stats["queries"] += 1
            
            return enhanced_params
        
        def _formulate_knowledge_query(self, task_description: str) -> str:
            """Formulate an optimized query for knowledge retrieval based on task and context.
            
            Args:
                task_description: Task description
                
            Returns:
                Optimized query"""
            # Extract key concepts from task description
            key_concepts = self._extract_key_concepts(task_description)
            
            # Combine with role-specific focus
            role_focus = f"as a {self.role}" if hasattr(self, "role") else ""
            
            # Create base query
            query = f"{key_concepts} {role_focus}".strip()
            
            # Add context if available
            if hasattr(self, "knowledge_context") and self.knowledge_context:
                # Get recent task contexts
                recent_contexts = [
                    item["content"] for item in self.knowledge_context[-self.context_window_size:]
                    if item["type"] == "task"
                ]
                
                if recent_contexts:
                    # Extract key terms from recent contexts
                    context_terms = self._extract_key_concepts(" ".join(recent_contexts))
                    
                    # Add context terms with lower weight
                    query = f"{query} considering {context_terms}"
            
            # Add personalization if enabled
            if self.enable_personalization and hasattr(self, "personalization_profile"):
                # Add preferred topics
                preferred_topics = self.personalization_profile.get("preferred_topics", [])
                if preferred_topics:
                    top_topics = preferred_topics[:3]  # Use top 3 topics
                    query = f"{query} specializing in {', '.join(top_topics)}"
                
                # Add expertise level
                expertise_level = self.personalization_profile.get("expertise_level", "")
                if expertise_level:
                    query = f"{query} at {expertise_level} level"
            
            # Add shared knowledge references if available and relevant
            if self.enable_multi_agent_sharing and hasattr(self, "role"):
                relevant_shared = self._get_relevant_shared_knowledge(task_description)
                if relevant_shared:
                    shared_concepts = " ".join([item["key_concept"] for item in relevant_shared[:2]])
                    query = f"{query} including {shared_concepts}"
            
            return query
        
        def _extract_key_concepts(self, text: str) -> str:
            """Extract key concepts from text for query optimization.
            
            Args:
                text: Input text
                
            Returns:
                Key concepts as a string"""
            # Remove common words
            common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about", "as"}
            words = text.lower().split()
            filtered_words = [word for word in words if word not in common_words]
            
            # Find potential technical terms (capitalized words or words with special characters)
            technical_terms = []
            for word in words:
                if len(word) > 1 and word[0].isupper() and word.lower() not in common_words:
                    technical_terms.append(word)
                elif re.search(r'[-_/]', word) and len(word) > 3:
                    technical_terms.append(word)
            
            # Combine most frequent terms and technical terms
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top terms by frequency
            top_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            top_terms = [term[0] for term in top_terms]
            
            # Combine with technical terms
            key_terms = list(set(top_terms + technical_terms))[:10]
            
            return " ".join(key_terms)
        
        def _retrieve_knowledge(self, query: str) -> List[Dict[str, Any]]:
            """Retrieve relevant knowledge based on the query.
            
            Args:
                query: Knowledge query
                
            Returns:
                List of relevant knowledge chunks"""
            try:
                # Query the knowledge pipeline
                role_filter = self.role if hasattr(self, "role") else None
                knowledge_chunks = knowledge_pipeline.query_knowledge(
                    query=query,
                    role=role_filter,
                    top_k=self.max_knowledge_chunks
                )
                
                # Filter by confidence threshold
                filtered_chunks = [
                    chunk for chunk in knowledge_chunks
                    if chunk.get("score", 0) >= self.confidence_threshold
                ]
                
                # Apply personalization if enabled
                if self.enable_personalization and hasattr(self, "personalization_profile"):
                    filtered_chunks = self._personalize_knowledge_results(filtered_chunks)
                
                # Update context with retrieved knowledge
                if hasattr(self, "knowledge_context"):
                    for chunk in filtered_chunks:
                        self.knowledge_context.append({
                            "type": "knowledge",
                            "content": chunk["document"].get("content", ""),
                            "source": chunk["document"].get("source", ""),
                            "section": chunk["document"].get("section", ""),
                            "score": chunk.get("score", 0),
                            "timestamp": time.time()
                        })
                
                return filtered_chunks
                
            except Exception as e:
                logger.error(f"Error retrieving knowledge: {str(e)}")
                return []
        
        def _personalize_knowledge_results(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """Personalize knowledge results based on agent profile.
            
            Args:
                chunks: Knowledge chunks
                
            Returns:
                Personalized knowledge chunks"""
            if not chunks:
                return chunks
            
            # Get personalization profile
            profile = self.personalization_profile
            
            # Apply personalization factors
            personalized_chunks = []
            
            for chunk in chunks:
                # Start with original score
                original_score = chunk.get("score", 0)
                personalized_score = original_score
                
                # Adjust score based on preferred topics
                preferred_topics = profile.get("preferred_topics", [])
                if preferred_topics and "document" in chunk:
                    document = chunk["document"]
                    content = document.get("content", "").lower()
                    
                    # Check if content contains preferred topics
                    topic_matches = sum(1 for topic in preferred_topics if topic.lower() in content)
                    if topic_matches > 0:
                        # Boost score based on number of matches
                        topic_boost = min(0.2, 0.05 * topic_matches)
                        personalized_score += topic_boost
                
                # Adjust score based on previously useful sections
                useful_sections = profile.get("useful_sections", [])
                if useful_sections and "document" in chunk:
                    section = chunk["document"].get("section", "")
                    if section in useful_sections:
                        personalized_score += 0.1
                
                # Adjust score based on expertise level
                expertise_level = profile.get("expertise_level", "intermediate")
                if expertise_level and "document" in chunk:
                    document = chunk["document"]
                    
                    # Adjust for beginner (prefer simpler content)
                    if expertise_level == "beginner":
                        content = document.get("content", "")
                        # Simple heuristic: shorter sentences tend to be simpler
                        avg_sentence_length = len(content) / max(1, len(re.split(r'[.!?]', content)))
                        if avg_sentence_length < 20:  # Short sentences
                            personalized_score += 0.15
                    
                    # Adjust for advanced (prefer detailed content)
                    elif expertise_level == "advanced":
                        content = document.get("content", "")
                        # Simple heuristic: longer content tends to be more detailed
                        if len(content) > 500:
                            personalized_score += 0.1
                
                # Update score
                chunk["score"] = personalized_score
                chunk["original_score"] = original_score
                chunk["personalization_applied"] = personalized_score != original_score
                
                personalized_chunks.append(chunk)
            
            # Re-sort by personalized score
            personalized_chunks.sort(key=lambda x: x["score"], reverse=True)
            
            return personalized_chunks[:self.max_knowledge_chunks]
        
        def _format_knowledge_for_task(self, chunks: List[Dict[str, Any]]) -> str:
            """Format knowledge chunks for inclusion in task parameters.
            
            Args:
                chunks: Knowledge chunks
                
            Returns:
                Formatted knowledge text"""
            if not chunks:
                return ""
            
            formatted_text = "Relevant knowledge:\n\n"
            
            for i, chunk in enumerate(chunks):
                document = chunk["document"]
                content = document.get("content", "")
                title = document.get("title", "")
                section = document.get("section", "")
                source = document.get("source", "")
                
                formatted_text += f"--- Knowledge {i+1} ---\n"
                formatted_text += f"Title: {title}\n"
                if section:
                    formatted_text += f"Section: {section}\n"
                formatted_text += f"Source: {source}\n"
                formatted_text += f"Relevance: {chunk.get('score', 0):.2f}\n"
                formatted_text += f"\n{content}\n\n"
            
            return formatted_text
        
        def _process_knowledge_feedback(self, result: Dict[str, Any]) -> None:
            """Process feedback on knowledge usefulness.
            
            Args:
                result: Task processing result"""
            if not self.enable_knowledge_feedback:
                return
            
            # Check if result contains feedback
            feedback = result.get("knowledge_feedback", {})
            if not feedback:
                return
            
            # Process feedback
            useful = feedback.get("useful", False)
            knowledge_ids = feedback.get("knowledge_ids", [])
            
            if useful and hasattr(self, "knowledge_stats"):
                self.knowledge_stats["feedback"]["positive"] += 1
                
                # Update personalization profile
                if self.enable_personalization and hasattr(self, "personalization_profile"):
                    # Get sections from recent knowledge context
                    recent_knowledge = [
                        item for item in self.knowledge_context[-self.context_window_size:]
                        if item["type"] == "knowledge"
                    ]
                    
                    # Update useful sections
                    useful_sections = self.personalization_profile.get("useful_sections", [])
                    for item in recent_knowledge:
                        section = item.get("section", "")
                        if section and section not in useful_sections:
                            useful_sections.append(section)
                    
                    # Keep only the most recent useful sections
                    self.personalization_profile["useful_sections"] = useful_sections[-10:]
            elif hasattr(self, "knowledge_stats"):
                self.knowledge_stats["feedback"]["negative"] += 1
        
        def _initialize_personalization_profile(self) -> None:
            """Initialize personalization profile for the agent."""
            if not self.enable_personalization:
                return
            
            if not hasattr(self, "role"):
                return
            
            # Create default profile
            self.personalization_profile = {
                "role": self.role,
                "preferred_topics": [],
                "expertise_level": "intermediate",
                "useful_sections": [],
                "learning_style": "balanced",
                "created_at": time.time(),
                "updated_at": time.time()
            }
            
            # Set role-specific defaults
            if self.role == "project_manager":
                self.personalization_profile.update({
                    "preferred_topics": ["project planning", "risk management", "team coordination"],
                    "expertise_level": "advanced"
                })
            elif self.role == "product_manager":
                self.personalization_profile.update({
                    "preferred_topics": ["product strategy", "market analysis", "user experience"],
                    "expertise_level": "advanced"
                })
            elif self.role == "developer":
                self.personalization_profile.update({
                    "preferred_topics": ["coding", "software architecture", "testing"],
                    "expertise_level": "intermediate"
                })
            elif self.role == "system_architect":
                self.personalization_profile.update({
                    "preferred_topics": ["system design", "architecture patterns", "scalability"],
                    "expertise_level": "advanced"
                })
        
        def _share_valuable_knowledge(self, result: Dict[str, Any]) -> None:
            """Share valuable knowledge with other agents.
            
            Args:
                result: Task processing result"""
            if not self.enable_multi_agent_sharing:
                return
            
            if not hasattr(self, "role"):
                return
            
            # Check if result was successful and used knowledge
            if not result.get("success", False) or not result.get("knowledge_attribution", {}).get("used", False):
                return
            
            # Get task description
            task_description = result.get("task_description", "")
            if not task_description:
                return
            
            # Extract key concept from task
            key_concept = self._extract_key_concepts(task_description)
            
            # Get recent knowledge context
            recent_knowledge = [
                item for item in self.knowledge_context[-self.max_knowledge_chunks:]
                if item["type"] == "knowledge"
            ]
            
            if not recent_knowledge:
                return
            
            # Share the most relevant knowledge
            top_knowledge = sorted(recent_knowledge, key=lambda x: x.get("score", 0), reverse=True)[0]
            
            # Create shared knowledge entry
            shared_id = str(uuid.uuid4())
            shared_entry = {
                "id": shared_id,
                "role": self.role,
                "key_concept": key_concept,
                "content": top_knowledge.get("content", ""),
                "source": top_knowledge.get("source", ""),
                "section": top_knowledge.get("section", ""),
                "shared_at": time.time()
            }
            
            # Add to shared knowledge
            self.shared_knowledge[shared_id] = shared_entry
            
            # Trim shared knowledge if too large
            if len(self.shared_knowledge) > 100:
                # Remove oldest entries
                sorted_entries = sorted(self.shared_knowledge.items(), key=lambda x: x[1]["shared_at"])
                for i in range(len(sorted_entries) - 100):
                    del self.shared_knowledge[sorted_entries[i][0]]
        
        def _get_relevant_shared_knowledge(self, query: str) -> List[Dict[str, Any]]:
            """Get relevant shared knowledge for a query.
            
            Args:
                query: Query string
                
            Returns:
                List of relevant shared knowledge entries"""
            if not self.shared_knowledge:
                return []
            
            # Extract key concepts from query
            query_concepts = set(self._extract_key_concepts(query).lower().split())
            
            # Find relevant shared knowledge
            relevant_entries = []
            
            for entry_id, entry in self.shared_knowledge.items():
                # Skip entries from this agent
                if entry.get("role") == self.role:
                    continue
                
                # Get key concepts from entry
                entry_concepts = set(entry.get("key_concept", "").lower().split())
                
                # Calculate relevance score (Jaccard similarity)
                if not query_concepts or not entry_concepts:
                    continue
                
                intersection = len(query_concepts.intersection(entry_concepts))
                union = len(query_concepts.union(entry_concepts))
                
                relevance = intersection / union if union > 0 else 0
                
                if relevance > 0.2:  # Minimum relevance threshold
                    entry_copy = entry.copy()
                    entry_copy["relevance"] = relevance
                    relevant_entries.append(entry_copy)
            
            # Sort by relevance
            relevant_entries.sort(key=lambda x: x.get("relevance", 0), reverse=True)
            
            return relevant_entries[:3]  # Return top 3 relevant entries
        
        # Add methods to agent class
        agent_class._enhance_with_knowledge = _enhance_with_knowledge
        agent_class._formulate_knowledge_query = _formulate_knowledge_query
        agent_class._extract_key_concepts = _extract_key_concepts
        agent_class._retrieve_knowledge = _retrieve_knowledge
        agent_class._format_knowledge_for_task = _format_knowledge_for_task
        agent_class._process_knowledge_feedback = _process_knowledge_feedback
        agent_class._initialize_personalization_profile = _initialize_personalization_profile
        agent_class._personalize_knowledge_results = _personalize_knowledge_results
        agent_class._share_valuable_knowledge = _share_valuable_knowledge
        agent_class._get_relevant_shared_knowledge = _get_relevant_shared_knowledge
        
        # Replace methods
        agent_class.__init__ = patched_init
        agent_class.process_task = patched_process_task
        
        return agent_class
    
    def adapt_agent_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt an agent role with knowledge capabilities.
        
        Args:
            params: Adaptation parameters including role, training_id, and adaptation_config
            
        Returns:
            Adaptation result"""
        role = params.get("role")
        training_id = params.get("training_id")
        adaptation_config = params.get("adaptation_config", {})
        
        if not role:
            return {
                "success": False,
                "message": "Role is required"
            }
        
        if not training_id:
            return {
                "success": False,
                "message": "Training ID is required"
            }
        
        try:
            # Generate adaptation ID
            adaptation_id = f"adapt_{role}_{uuid.uuid4().hex[:8]}"
            
            # Update agent context
            self.agent_contexts[role] = {
                "adaptation_id": adaptation_id,
                "training_id": training_id,
                "context": [],
                "created_at": time.time(),
                "updated_at": time.time()
            }
            
            # Create personalization profile
            if self.enable_personalization:
                self.agent_profiles[role] = {
                    "role": role,
                    "preferred_topics": adaptation_config.get("preferred_topics", []),
                    "expertise_level": adaptation_config.get("expertise_level", "intermediate"),
                    "useful_sections": [],
                    "learning_style": adaptation_config.get("learning_style", "balanced"),
                    "created_at": time.time(),
                    "updated_at": time.time()
                }
            
            # Update knowledge usage stats
            if role not in self.knowledge_usage_stats["by_role"]:
                self.knowledge_usage_stats["by_role"][role] = {
                    "queries": 0,
                    "retrievals": 0,
                    "feedback": {
                        "positive": 0,
                        "negative": 0
                    }
                }
            
            logger.info(f"Adapted agent role {role} with knowledge capabilities")
            
            return {
                "success": True,
                "message": f"Successfully adapted agent role {role}",
                "adaptation_id": adaptation_id,
                "role": role
            }
            
        except Exception as e:
            logger.error(f"Error adapting agent role: {str(e)}")
            return {
                "success": False,
                "message": f"Error adapting agent role: {str(e)}"
            }
    
    def get_agent_context(self, role: str) -> Dict[str, Any]:
        """Get context for an agent role.
        
        Args:
            role: Agent role
            
        Returns:
            Agent context"""
        return self.agent_contexts.get(role, {})
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge usage statistics.
        
        Returns:
            Knowledge usage statistics"""
        return self.knowledge_usage_stats
    
    def get_personalization_profile(self, role: str) -> Dict[str, Any]:
        """Get personalization profile for an agent role.
        
        Args:
            role: Agent role
            
        Returns:
            Personalization profile"""
        return self.agent_profiles.get(role, {})
    
    def update_personalization_profile(self, role: str, profile_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update personalization profile for an agent role.
        
        Args:
            role: Agent role
            profile_updates: Profile updates
            
        Returns:
            Updated profile"""
        if not self.enable_personalization:
            return {
                "success": False,
                "message": "Personalization is disabled"
            }
        
        if role not in self.agent_profiles:
            return {
                "success": False,
                "message": f"Profile not found for role {role}"
            }
        
        try:
            # Update profile
            profile = self.agent_profiles[role]
            
            for key, value in profile_updates.items():
                if key in profile:
                    profile[key] = value
            
            # Update timestamp
            profile["updated_at"] = time.time()
            
            return {
                "success": True,
                "message": f"Updated profile for role {role}",
                "profile": profile
            }
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return {
                "success": False,
                "message": f"Error updating profile: {str(e)}"
            }
    
    def get_shared_knowledge(self, role: Optional[str] = None) -> Dict[str, Any]:
        """Get shared knowledge.
        
        Args:
            role: Optional role filter
            
        Returns:
            Shared knowledge"""
        if not self.enable_multi_agent_sharing:
            return {
                "success": False,
                "message": "Multi-agent knowledge sharing is disabled"
            }
        
        try:
            if role:
                # Filter by role
                filtered_knowledge = {
                    k: v for k, v in self.shared_knowledge.items()
                    if v.get("role") == role
                }
                
                return {
                    "success": True,
                    "message": f"Retrieved shared knowledge for role {role}",
                    "shared_knowledge": filtered_knowledge
                }
            else:
                return {
                    "success": True,
                    "message": "Retrieved all shared knowledge",
                    "shared_knowledge": self.shared_knowledge
                }
                
        except Exception as e:
            logger.error(f"Error retrieving shared knowledge: {str(e)}")
            return {
                "success": False,
                "message": f"Error retrieving shared knowledge: {str(e)}"
            }


# Create a singleton instance
adaptation_layer = AgentAdaptationLayer()
