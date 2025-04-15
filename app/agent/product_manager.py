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


"""Product Manager Agent for TorontoAITeamAgent.

This module defines the Product Manager Agent, which handles requirements gathering,
product vision, and feature prioritization."""

from typing import Dict, Any, List, Optional
import os
import logging
import asyncio
from datetime import datetime

from .base_agent import BaseAgent
from ..tools.registry import registry

logger = logging.getLogger(__name__)

class ProductManagerAgent(BaseAgent):
    """Product Manager Agent handles requirements gathering, product vision, and feature prioritization."""
    
    role = "product_manager"
    description = "Handles requirements gathering, product vision, and feature prioritization"
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Product Manager Agent.
        
        Args:
            config: Agent configuration with optional settings"""
        super().__init__(config)
        
        # Product Manager specific capabilities
        self.capabilities.extend([
            "Gather and analyze requirements",
            "Define product vision and roadmap",
            "Prioritize features based on business value",
            "Create user stories and acceptance criteria",
            "Conduct market research and competitive analysis",
            "Collaborate with stakeholders to refine product requirements"
        ])
        
        # Product Manager specific tools
        self.preferred_tools.extend([
            "openai",  # For advanced reasoning
            "gradio",  # For user interface
            "threading"  # For parallel processing
        ])
        
        # Product state
        self.requirements = {}
        self.user_stories = {}
        self.product_roadmap = {}
        self.feature_priorities = {}
        
        logger.info(f"Product Manager Agent initialized with model: {self.model}")
    
    async def gather_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather and analyze requirements for a project.
        
        Args:
            params: Requirements parameters including project_id and input_data
            
        Returns:
            Requirements gathering result
        """
        project_id = params.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Missing project ID"
            }
        
        input_data = params.get("input_data", {})
        
        # Create requirements entry for this project
        if project_id not in self.requirements:
            self.requirements[project_id] = {
                "functional": [],
                "non_functional": [],
                "constraints": [],
                "assumptions": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        # In a real implementation, this would use LLM to analyze input data and extract requirements
        # For now, use placeholder data
        
        # Process functional requirements
        if "description" in input_data:
            self.requirements[project_id]["functional"].append({
                "id": f"FR{len(self.requirements[project_id]['functional']) + 1}",
                "description": f"The system shall {input_data.get('description')}",
                "priority": "high",
                "source": "user input"
            })
        
        # Process non-functional requirements
        if "performance" in input_data:
            self.requirements[project_id]["non_functional"].append({
                "id": f"NFR{len(self.requirements[project_id]['non_functional']) + 1}",
                "type": "performance",
                "description": f"The system shall {input_data.get('performance')}",
                "priority": "medium",
                "source": "user input"
            })
        
        # Process constraints
        if "constraints" in input_data:
            self.requirements[project_id]["constraints"].append({
                "id": f"CON{len(self.requirements[project_id]['constraints']) + 1}",
                "description": input_data.get("constraints"),
                "source": "user input"
            })
        
        # Update timestamp
        self.requirements[project_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Gathered requirements for project {project_id}")
        
        return {
            "success": True,
            "message": "Requirements gathered successfully",
            "requirements": self.requirements[project_id]
        }
    
    async def create_user_stories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create user stories based on requirements.
        
        Args:
            params: User story parameters including project_id
            
        Returns:
            User story creation result
        """
        project_id = params.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Missing project ID"
            }
        
        if project_id not in self.requirements:
            return {
                "success": False,
                "message": "Requirements not found for this project"
            }
        
        # Create user stories entry for this project
        if project_id not in self.user_stories:
            self.user_stories[project_id] = []
        
        # In a real implementation, this would use LLM to create user stories from requirements
        # For now, use placeholder data
        
        # Create user stories from functional requirements
        for req in self.requirements[project_id]["functional"]:
            story_id = f"US{len(self.user_stories[project_id]) + 1}"
            
            story = {
                "id": story_id,
                "as_a": "user",
                "i_want_to": req["description"].replace("The system shall ", ""),
                "so_that": "I can accomplish my goals",
                "acceptance_criteria": [
                    f"Given I am a user, when I {req['description'].replace('The system shall ', '')}, then the system responds appropriately"
                ],
                "priority": req["priority"],
                "size": "medium",
                "related_requirements": [req["id"]]
            }
            
            self.user_stories[project_id].append(story)
        
        logger.info(f"Created user stories for project {project_id}")
        
        return {
            "success": True,
            "message": "User stories created successfully",
            "user_stories": self.user_stories[project_id]
        }
    
    async def prioritize_features(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prioritize features based on business value.
        
        Args:
            params: Prioritization parameters including project_id
            
        Returns:
            Feature prioritization result
        """
        project_id = params.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Missing project ID"
            }
        
        if project_id not in self.user_stories:
            return {
                "success": False,
                "message": "User stories not found for this project"
            }
        
        # Create feature priorities entry for this project
        if project_id not in self.feature_priorities:
            self.feature_priorities[project_id] = {
                "high": [],
                "medium": [],
                "low": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        # In a real implementation, this would use LLM to prioritize features
        # For now, use placeholder data
        
        # Prioritize features based on user stories
        for story in self.user_stories[project_id]:
            feature = {
                "id": f"F{story['id'].replace('US', '')}",
                "description": f"Feature to {story['i_want_to']}",
                "user_stories": [story["id"]],
                "business_value": "high" if story["priority"] == "high" else "medium"
            }
            
            if story["priority"] == "high":
                self.feature_priorities[project_id]["high"].append(feature)
            elif story["priority"] == "medium":
                self.feature_priorities[project_id]["medium"].append(feature)
            else:
                self.feature_priorities[project_id]["low"].append(feature)
        
        # Update timestamp
        self.feature_priorities[project_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Prioritized features for project {project_id}")
        
        return {
            "success": True,
            "message": "Features prioritized successfully",
            "feature_priorities": self.feature_priorities[project_id]
        }
    
    async def create_product_roadmap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a product roadmap based on prioritized features.
        
        Args:
            params: Roadmap parameters including project_id
            
        Returns:
            Product roadmap creation result
        """
        project_id = params.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Missing project ID"
            }
        
        if project_id not in self.feature_priorities:
            return {
                "success": False,
                "message": "Feature priorities not found for this project"
            }
        
        # Create product roadmap entry for this project
        if project_id not in self.product_roadmap:
            self.product_roadmap[project_id] = {
                "phases": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        # In a real implementation, this would use LLM to create a product roadmap
        # For now, use placeholder data
        
        # Create roadmap phases
        phases = [
            {
                "id": "phase1",
                "name": "MVP",
                "description": "Minimum Viable Product",
                "features": [f["id"] for f in self.feature_priorities[project_id]["high"]],
                "estimated_duration": "4 weeks",
                "start_date": "2023-01-01",
                "end_date": "2023-01-31"
            },
            {
                "id": "phase2",
                "name": "Core Features",
                "description": "Core feature set",
                "features": [f["id"] for f in self.feature_priorities[project_id]["medium"]],
                "estimated_duration": "8 weeks",
                "start_date": "2023-02-01",
                "end_date": "2023-03-31"
            },
            {
                "id": "phase3",
                "name": "Enhanced Features",
                "description": "Enhanced feature set",
                "features": [f["id"] for f in self.feature_priorities[project_id]["low"]],
                "estimated_duration": "12 weeks",
                "start_date": "2023-04-01",
                "end_date": "2023-06-30"
            }
        ]
        
        self.product_roadmap[project_id]["phases"] = phases
        
        # Update timestamp
        self.product_roadmap[project_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Created product roadmap for project {project_id}")
        
        return {
            "success": True,
            "message": "Product roadmap created successfully",
            "product_roadmap": self.product_roadmap[project_id]
        }
    
    async def analyze_market(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct market research and competitive analysis.
        
        Args:
            params: Market analysis parameters including project_id and market_segment
            
        Returns:
            Market analysis result
        """
        project_id = params.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Missing project ID"
            }
        
        market_segment = params.get("market_segment", "general")
        
        # In a real implementation, this would use LLM and web search to conduct market research
        # For now, use placeholder data
        
        market_analysis = {
            "market_segment": market_segment,
            "market_size": "$10B",
            "growth_rate": "15% annually",
            "key_trends": [
                "Increasing adoption of AI technologies",
                "Growing demand for automation solutions",
                "Shift towards cloud-based services"
            ],
            "competitors": [
                {
                    "name": "Competitor A",
                    "market_share": "25%",
                    "strengths": ["Strong brand recognition", "Large customer base"],
                    "weaknesses": ["Outdated technology", "Poor customer service"]
                },
                {
                    "name": "Competitor B",
                    "market_share": "15%",
                    "strengths": ["Innovative features", "Aggressive pricing"],
                    "weaknesses": ["Limited market reach", "Scalability issues"]
                }
            ],
            "opportunities": [
                "Untapped market segments",
                "Integration with emerging technologies",
                "International expansion"
            ],
            "threats": [
                "New market entrants",
                "Changing regulatory landscape",
                "Economic uncertainty"
            ]
        }
        
        logger.info(f"Conducted market analysis for project {project_id}")
        
        return {
            "success": True,
            "message": "Market analysis conducted successfully",
            "market_analysis": market_analysis
        }
    
    async def process_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task assigned to this agent.
        
        Args:
            params: Task parameters including task_id and description
            
        Returns:
            Task processing result
        """
        task_id = params.get("task_id")
        if not task_id:
            return {
                "success": False,
                "message": "Missing task ID"
            }
        
        # Store task in agent's task list
        self.tasks[task_id] = {
            "id": task_id,
            "description": params.get("description", ""),
            "status": "in_progress",
            "progress": 0,
            "result": None
        }
        
        logger.info(f"Product Manager processing task {task_id}")
        
        # Determine task type and execute appropriate method
        task_type = params.get("task_type", "")
        project_id = params.get("project_id", "")
        
        if task_type == "gather_requirements":
            result = await self.gather_requirements({
                "project_id": project_id,
                "input_data": params.get("input_data", {})
            })
        elif task_type == "create_user_stories":
            result = await self.create_user_stories({
                "project_id": project_id
            })
        elif task_type == "prioritize_features":
            result = await self.prioritize_features({
                "project_id": project_id
            })
        elif task_type == "create_product_roadmap":
            result = await self.create_product_roadmap({
                "project_id": project_id
            })
        elif task_type == "analyze_market":
            result = await self.analyze_market({
                "project_id": project_id,
                "market_segment": params.get("market_segment", "general")
            })
        else:
            # Default task processing
            result = await super().process_task(params)
        
        # Update task status
        self.tasks[task_id]["status"] = "completed"
        self.tasks[task_id]["progress"] = 100
        self.tasks[task_id]["result"] = result
        
        return result
