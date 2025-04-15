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


"""Request Prioritization Mechanism for Project Manager.

This module provides functionality for prioritizing human input requests
based on various factors such as urgency, impact, and agent role."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

class RequestPrioritizationMechanism:
    """Mechanism for prioritizing human input requests."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Request Prioritization Mechanism.
        
        Args:
            config: Configuration with optional settings"""
        self.config = config or {}
        
        # Default weights for prioritization factors
        self.weights = self.config.get("prioritization_weights", {
            "urgency": 0.35,
            "impact": 0.25,
            "agent_role": 0.15,
            "request_age": 0.15,
            "complexity": 0.10
        })
        
        # Agent role priority levels (higher value = higher priority)
        self.agent_role_priorities = self.config.get("agent_role_priorities", {
            "project_manager": 5,
            "product_manager": 4,
            "system_architect": 4,
            "developer": 3,
            "qa_testing_specialist": 3,
            "security_engineer": 4,
            "database_engineer": 3,
            "ui_ux_designer": 3,
            "documentation_specialist": 2,
            "performance_engineer": 3,
            "devops_engineer": 3
        })
        
        # Request category impact levels (higher value = higher impact)
        self.category_impact = self.config.get("category_impact", {
            "decision": 5,      # Blocking decisions have high impact
            "approval": 4,      # Approvals are important for progress
            "feedback": 3,      # Feedback is valuable but less urgent
            "information": 2    # Information requests are typically less critical
        })
        
        logger.info("Request Prioritization Mechanism initialized")
    
    def prioritize_requests(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize a list of human input requests.
        
        Args:
            requests: List of input request objects
            
        Returns:
            Prioritized list of requests with priority scores"""
        if not requests:
            return []
        
        # Calculate priority score for each request
        for request in requests:
            request["priority_score"] = self._calculate_priority_score(request)
        
        # Sort by priority score (descending)
        prioritized_requests = sorted(requests, key=lambda x: x["priority_score"], reverse=True)
        
        logger.info(f"Prioritized {len(requests)} requests")
        
        return prioritized_requests
    
    def _calculate_priority_score(self, request: Dict[str, Any]) -> float:
        """Calculate a priority score for a request based on multiple factors.
        
        Args:
            request: Input request object
            
        Returns:
            Priority score (higher = more important)"""
        # Base priority from request's priority field
        base_priority = {"high": 1.0, "medium": 0.6, "low": 0.3}.get(request.get("priority", "medium"), 0.6)
        
        # Calculate factor scores
        urgency_score = self._calculate_urgency_score(request)
        impact_score = self._calculate_impact_score(request)
        agent_role_score = self._calculate_agent_role_score(request)
        request_age_score = self._calculate_request_age_score(request)
        complexity_score = self._calculate_complexity_score(request)
        
        # Apply weights to each factor
        weighted_score = (
            self.weights["urgency"] * urgency_score +
            self.weights["impact"] * impact_score +
            self.weights["agent_role"] * agent_role_score +
            self.weights["request_age"] * request_age_score +
            self.weights["complexity"] * complexity_score
        )
        
        # Combine base priority with weighted factors
        final_score = base_priority * (0.7 + 0.3 * weighted_score)
        
        # Completed requests always have lowest priority
        if request.get("status") == "completed":
            final_score = 0
        
        return final_score
    
    def _calculate_urgency_score(self, request: Dict[str, Any]) -> float:
        """Calculate urgency score based on due date and status.
        
        Args:
            request: Input request object
            
        Returns:
            Urgency score (0-1)"""
        # If no due date, use medium urgency
        if not request.get("due_by"):
            return 0.5
        
        try:
            due_date = datetime.fromisoformat(request["due_by"])
            now = datetime.now()
            
            # Calculate time remaining in hours
            time_diff = due_date - now
            hours_remaining = time_diff.total_seconds() / 3600
            
            if hours_remaining <= 0:
                # Overdue requests get maximum urgency
                return 1.0
            elif hours_remaining <= 4:
                # Due within 4 hours
                return 0.9
            elif hours_remaining <= 24:
                # Due within 1 day
                return 0.8
            elif hours_remaining <= 48:
                # Due within 2 days
                return 0.6
            elif hours_remaining <= 72:
                # Due within 3 days
                return 0.4
            else:
                # Due in more than 3 days
                return 0.2
        except (ValueError, TypeError):
            # If date parsing fails, use medium urgency
            return 0.5
    
    def _calculate_impact_score(self, request: Dict[str, Any]) -> float:
        """Calculate impact score based on request category and content.
        
        Args:
            request: Input request object
            
        Returns:
            Impact score (0-1)"""
        category = request.get("category", "information")
        
        # Get base impact from category
        base_impact = self.category_impact.get(category, 2) / 5.0
        
        # Adjust based on keywords in title and description
        high_impact_keywords = ["critical", "urgent", "blocker", "blocking", "security", "crash", "bug", "error"]
        medium_impact_keywords = ["important", "significant", "performance", "usability", "feature"]
        
        title = request.get("title", "").lower()
        description = request.get("description", "").lower()
        text = title + " " + description
        
        # Count keyword occurrences
        high_impact_count = sum(1 for keyword in high_impact_keywords if keyword in text)
        medium_impact_count = sum(1 for keyword in medium_impact_keywords if keyword in text)
        
        # Adjust impact based on keywords
        keyword_impact = min(1.0, (high_impact_count * 0.2 + medium_impact_count * 0.1))
        
        # Combine base impact with keyword impact
        return min(1.0, base_impact + keyword_impact)
    
    def _calculate_agent_role_score(self, request: Dict[str, Any]) -> float:
        """Calculate score based on the requesting agent's role.
        
        Args:
            request: Input request object
            
        Returns:
            Agent role score (0-1)"""
        agent_role = request.get("requested_by", "").lower()
        
        # Get priority level for this role
        role_priority = self.agent_role_priorities.get(agent_role, 3)
        
        # Normalize to 0-1 range
        return role_priority / 5.0
    
    def _calculate_request_age_score(self, request: Dict[str, Any]) -> float:
        """Calculate score based on the age of the request.
        
        Args:
            request: Input request object
            
        Returns:
            Request age score (0-1)"""
        if not request.get("created_at"):
            return 0.5
        
        try:
            created_at = datetime.fromisoformat(request["created_at"])
            now = datetime.now()
            
            # Calculate age in hours
            age_hours = (now - created_at).total_seconds() / 3600
            
            # Older requests get higher priority, but with diminishing returns
            # Using a logarithmic scale: log(1 + age_hours/24) / log(8)
            # This gives 0.33 for 1 day, 0.67 for 1 week, 1.0 for 2 months
            normalized_age = math.log(1 + age_hours/24) / math.log(60)
            
            return min(1.0, normalized_age)
        except (ValueError, TypeError):
            # If date parsing fails, use medium age
            return 0.5
    
    def _calculate_complexity_score(self, request: Dict[str, Any]) -> float:
        """Calculate score based on the complexity of the request.
        
        Args:
            request: Input request object
            
        Returns:
            Complexity score (0-1)"""
        # Estimate complexity based on description length and category
        description = request.get("description", "")
        description_length = len(description)
        
        # Longer descriptions often indicate more complex requests
        length_factor = min(1.0, description_length / 1000)
        
        # Certain categories tend to be more complex
        category = request.get("category", "information")
        category_complexity = {
            "decision": 0.8,
            "approval": 0.5,
            "feedback": 0.7,
            "information": 0.4
        }.get(category, 0.5)
        
        # Combine factors
        return (length_factor + category_complexity) / 2.0
    
    def suggest_due_date(self, request: Dict[str, Any]) -> str:
        """Suggest an appropriate due date for a request based on its characteristics.
        
        Args:
            request: Input request object
            
        Returns:
            Suggested due date in ISO format"""
        now = datetime.now()
        priority = request.get("priority", "medium")
        category = request.get("category", "information")
        
        # Base timeframes by priority
        priority_days = {
            "high": 1,
            "medium": 3,
            "low": 5
        }.get(priority, 3)
        
        # Adjust by category
        category_multiplier = {
            "decision": 0.7,  # Decisions need quicker response
            "approval": 0.8,  # Approvals should be timely
            "feedback": 1.2,  # Feedback can take a bit longer
            "information": 1.0  # Information requests are standard
        }.get(category, 1.0)
        
        # Calculate days to add
        days_to_add = priority_days * category_multiplier
        
        # Convert to hours and add some randomness to avoid all requests having same due date
        hours_to_add = int(days_to_add * 24)
        
        # Calculate due date
        due_date = now + timedelta(hours=hours_to_add)
        
        return due_date.isoformat()
    
    def analyze_request_patterns(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in requests to identify trends and potential improvements.
        
        Args:
            requests: List of input request objects
            
        Returns:
            Analysis results"""
        if not requests:
            return {
                "total_requests": 0,
                "patterns": {}
            }
        
        # Count requests by various dimensions
        by_agent = {}
        by_category = {}
        by_priority = {}
        by_status = {}
        
        # Track response times
        response_times = []
        
        for request in requests:
            # Count by agent
            agent = request.get("requested_by", "unknown")
            by_agent[agent] = by_agent.get(agent, 0) + 1
            
            # Count by category
            category = request.get("category", "unknown")
            by_category[category] = by_category.get(category, 0) + 1
            
            # Count by priority
            priority = request.get("priority", "unknown")
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Count by status
            status = request.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            
            # Calculate response time for completed requests
            if status == "completed" and request.get("created_at") and request.get("completed_at"):
                try:
                    created_at = datetime.fromisoformat(request["created_at"])
                    completed_at = datetime.fromisoformat(request["completed_at"])
                    response_time = (completed_at - created_at).total_seconds() / 3600  # hours
                    response_times.append(response_time)
                except (ValueError, TypeError):
                    pass
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Identify frequent requesters
        frequent_requesters = sorted(by_agent.items(), key=lambda x: x[1], reverse=True)
        
        # Identify common request categories
        common_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_requests": len(requests),
            "by_agent": by_agent,
            "by_category": by_category,
            "by_priority": by_priority,
            "by_status": by_status,
            "avg_response_time_hours": avg_response_time,
            "frequent_requesters": frequent_requesters[:3],
            "common_categories": common_categories[:3]
        }
