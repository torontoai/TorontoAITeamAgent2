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


"""Base classes for tools in the TorontoAITeamAgent Team AI system.

This module provides the base classes and interfaces for all tools in the system,
ensuring a consistent interface for agent usage."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result of a tool execution."""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    
    
class BaseTool:
    """Base class for all tools."""
    name: str
    description: str
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the tool with optional configuration.
        
        Args:
            config: Tool configuration"""
        self.config = config or {}
        
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with the given parameters.
        
        Args:
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError("Tool must implement execute method")
        
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        raise NotImplementedError("Tool must implement get_capabilities method")
