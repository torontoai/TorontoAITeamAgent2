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

"""Risk Management Service for Project Manager Agent.

This module provides services for identifying, assessing, and mitigating project risks."""

import logging
import asyncio
import datetime
from typing import Dict, Any, List, Optional, Union

from ..models import RiskAssessment, RiskSeverity, RiskProbability, Project

logger = logging.getLogger(__name__)

class RiskManagementService:
    """Service for identifying, assessing, and mitigating project risks."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the risk management service.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        self.risks = {}  # In-memory storage for risk assessments
        self.task_service = None  # Will be set by dependency injection
        logger.info("Risk management service initialized")
    
    def set_task_service(self, task_service):
        """Set task service reference."""
        self.task_service = task_service
    
    async def assess_risk(self, project_id: str, risk_data: Dict[str, Any]) -> RiskAssessment:
        """
        Assess a risk for a project.
        
        Args:
            project_id: Project ID
            risk_data: Risk data
            
        Returns:
            Risk assessment
        """
        logger.info(f"Assessing risk for project: {project_id}")
        
        # Add project ID to risk data
        risk_data['project_id'] = project_id
        
        # Create risk assessment from data
        risk = RiskAssessment.from_dict(risk_data)
        
        # Store risk assessment
        self.risks[risk.id] = risk
        
        logger.info(f"Risk assessed: {risk.id}")
        return risk
    
    async def get_risk(self, risk_id: str) -> RiskAssessment:
        """
        Get a risk assessment by ID.
        
        Args:
            risk_id: Risk ID
            
        Returns:
            Risk assessment
        """
        logger.info(f"Getting risk: {risk_id}")
        
        # Check if risk exists
        if risk_id not in self.risks:
            raise ValueError(f"Risk not found: {risk_id}")
        
        return self.risks[risk_id]
    
    async def list_risks(self, project_id: str) -> List[RiskAssessment]:
        """
        List all risks for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of risk assessments
        """
        logger.info(f"Listing all risks for project: {project_id}")
        
        # Filter risks by project
        return [r for r in self.risks.values() if r.project_id == project_id]
    
    async def update_risk(self, risk_id: str, risk_data: Dict[str, Any]) -> RiskAssessment:
        """
        Update a risk assessment.
        
        Args:
            risk_id: Risk ID
            risk_data: Updated risk data
            
        Returns:
            Updated risk assessment
        """
        logger.info(f"Updating risk: {risk_id}")
        
        # Check if risk exists
        if risk_id not in self.risks:
            raise ValueError(f"Risk not found: {risk_id}")
        
        # Get existing risk
        risk = self.risks[risk_id]
        
        # Update risk fields
        for key, value in risk_data.items():
            if key == 'id' or key == 'project_id':
                continue  # Don't update ID or project_id
            elif key == 'severity' and value:
                risk.severity = value if isinstance(value, RiskSeverity) else RiskSeverity(value)
            elif key == 'probability' and value:
                risk.probability = value if isinstance(value, RiskProbability) else RiskProbability(value)
            elif hasattr(risk, key):
                setattr(risk, key, value)
        
        # Update timestamp
        risk.updated_at = datetime.datetime.now()
        
        # Store updated risk
        self.risks[risk_id] = risk
        
        logger.info(f"Risk updated: {risk_id}")
        return risk
    
    async def delete_risk(self, risk_id: str) -> bool:
        """
        Delete a risk assessment.
        
        Args:
            risk_id: Risk ID
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting risk: {risk_id}")
        
        # Check if risk exists
        if risk_id not in self.risks:
            raise ValueError(f"Risk not found: {risk_id}")
        
        # Delete risk
        del self.risks[risk_id]
        
        logger.info(f"Risk deleted: {risk_id}")
        return True
    
    async def calculate_risk_score(self, risk: RiskAssessment) -> float:
        """
        Calculate a numerical risk score based on severity and probability.
        
        Args:
            risk: Risk assessment
            
        Returns:
            Risk score (0.0 to 1.0)
        """
        # Map severity to numerical value
        severity_map = {
            RiskSeverity.LOW: 0.25,
            RiskSeverity.MEDIUM: 0.5,
            RiskSeverity.HIGH: 0.75,
            RiskSeverity.CRITICAL: 1.0
        }
        
        # Map probability to numerical value
        probability_map = {
            RiskProbability.UNLIKELY: 0.25,
            RiskProbability.POSSIBLE: 0.5,
            RiskProbability.LIKELY: 0.75,
            RiskProbability.VERY_LIKELY: 1.0
        }
        
        # Calculate score as severity * probability
        severity_value = severity_map.get(risk.severity, 0.5)
        probability_value = probability_map.get(risk.probability, 0.5)
        
        return severity_value * probability_value
    
    async def get_project_risk_profile(self, project_id: str) -> Dict[str, Any]:
        """
        Get a comprehensive risk profile for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project risk profile
        """
        logger.info(f"Getting risk profile for project: {project_id}")
        
        # Get all risks for project
        risks = await self.list_risks(project_id)
        
        # Calculate risk scores
        risk_scores = []
        for risk in risks:
            score = await self.calculate_risk_score(risk)
            risk_scores.append({
                "risk": risk.to_dict(),
                "score": score
            })
        
        # Sort risks by score (highest first)
        risk_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Calculate overall project risk score (average of all risk scores)
        overall_score = sum(r["score"] for r in risk_scores) / len(risk_scores) if risk_scores else 0.0
        
        # Count risks by severity
        severity_counts = {
            RiskSeverity.LOW.value: 0,
            RiskSeverity.MEDIUM.value: 0,
            RiskSeverity.HIGH.value: 0,
            RiskSeverity.CRITICAL.value: 0
        }
        
        for risk in risks:
            severity_counts[risk.severity.value] += 1
        
        # Get project name if available
        project_name = "Unknown Project"
        if self.task_service:
            try:
                project = await self.task_service.get_project(project_id)
                project_name = project.name
            except Exception as e:
                logger.error(f"Error getting project: {e}")
        
        # Build risk profile
        risk_profile = {
            "project_id": project_id,
            "project_name": project_name,
            "overall_risk_score": overall_score,
            "risk_count": len(risks),
            "severity_distribution": severity_counts,
            "top_risks": risk_scores[:5] if len(risk_scores) > 5 else risk_scores,
            "all_risks": risk_scores
        }
        
        return risk_profile
    
    async def suggest_mitigation_strategies(self, risk_id: str) -> List[Dict[str, Any]]:
        """
        Suggest mitigation strategies for a risk.
        
        Args:
            risk_id: Risk ID
            
        Returns:
            List of suggested mitigation strategies
        """
        logger.info(f"Suggesting mitigation strategies for risk: {risk_id}")
        
        # Check if risk exists
        if risk_id not in self.risks:
            raise ValueError(f"Risk not found: {risk_id}")
        
        # Get risk
        risk = self.risks[risk_id]
        
        # In a real implementation, this would use AI or a knowledge base to suggest strategies
        # For now, we'll return some generic strategies based on severity and impact areas
        
        strategies = []
        
        # Add strategies based on severity
        if risk.severity == RiskSeverity.CRITICAL:
            strategies.append({
                "title": "Escalate to Executive Sponsor",
                "description": "This critical risk requires immediate attention from the executive sponsor.",
                "effort": "Medium",
                "effectiveness": "High"
            })
            
            strategies.append({
                "title": "Develop Contingency Plan",
                "description": "Create a detailed contingency plan to be activated if the risk materializes.",
                "effort": "High",
                "effectiveness": "High"
            })
        
        elif risk.severity == RiskSeverity.HIGH:
            strategies.append({
                "title": "Assign Risk Owner",
                "description": "Designate a specific team member to monitor and manage this risk.",
                "effort": "Low",
                "effectiveness": "Medium"
            })
            
            strategies.append({
                "title": "Regular Risk Reviews",
                "description": "Schedule weekly reviews to monitor this high-severity risk.",
                "effort": "Medium",
                "effectiveness": "Medium"
            })
        
        # Add strategies based on impact areas
        if "schedule" in risk.impact_areas:
            strategies.append({
                "title": "Schedule Buffer",
                "description": "Add buffer time to the project schedule to accommodate potential delays.",
                "effort": "Medium",
                "effectiveness": "Medium"
            })
        
        if "budget" in risk.impact_areas:
            strategies.append({
                "title": "Budget Reserve",
                "description": "Allocate a budget reserve specifically for this risk.",
                "effort": "Medium",
                "effectiveness": "High"
            })
        
        if "quality" in risk.impact_areas:
            strategies.append({
                "title": "Additional Quality Assurance",
                "description": "Implement additional quality assurance measures in affected areas.",
                "effort": "High",
                "effectiveness": "High"
            })
        
        if "resources" in risk.impact_areas:
            strategies.append({
                "title": "Resource Backup Plan",
                "description": "Identify backup resources that can be deployed if needed.",
                "effort": "Medium",
                "effectiveness": "Medium"
            })
        
        # Add generic strategies if we don't have enough
        if len(strategies) < 3:
            strategies.append({
                "title": "Regular Monitoring",
                "description": "Establish regular monitoring of risk indicators.",
                "effort": "Low",
                "effectiveness": "Medium"
            })
            
            strategies.append({
                "title": "Stakeholder Communication",
                "description": "Ensure all stakeholders are aware of the risk and its potential impact.",
                "effort": "Low",
                "effectiveness": "Medium"
            })
        
        return strategies
