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


"""Execution/Testing tools for TorontoAITeamAgent Team AI.

This module provides tools for Replit integration."""

from typing import Dict, Any, List, Optional
import os
import json
import asyncio
import httpx
from ..base import BaseTool, ToolResult

class ReplitTool(BaseTool):
    """Tool for interacting with Replit API."""
    
    name = "replit"
    description = "Provides capabilities for executing code and managing Repls using Replit API."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Replit tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.api_key = self.config.get("api_key", os.environ.get("REPLIT_API_KEY"))
        self.api_base = self.config.get("api_base", "https://replit.com/api")
        
        if not self.api_key:
            raise ValueError("Replit API key is required")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Replit tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (execute, create, etc.)
                - language: Programming language for code execution
                - code: Code to execute
                - repl_id: ID of existing Repl
                - files: Files to include in the Repl
                - other operation-specific parameters
                
        Returns:
            Tool execution result
        """
        operation = params.get("operation")
        if not operation:
            return ToolResult(
                success=False,
                data={},
                error="Operation parameter is required"
            )
            
        try:
            if operation == "execute":
                return await self._execute_code(params)
            elif operation == "create":
                return await self._create_repl(params)
            elif operation == "get":
                return await self._get_repl(params)
            else:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unsupported operation: {operation}"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=str(e)
            )
    
    async def _execute_code(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute code using Replit API.
        
        Args:
            params: Parameters for code execution
            
        Returns:
            Tool execution result
        """
        language = params.get("language", "python")
        code = params.get("code")
        inputs = params.get("inputs", [])
        
        if not code:
            return ToolResult(
                success=False,
                data={},
                error="Code parameter is required for execution"
            )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/v1/execute",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "language": language,
                    "code": code,
                    "inputs": inputs
                }
            )
            
            if response.status_code != 200:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Replit API error: {response.text}"
                )
                
            result = response.json()
            
            return ToolResult(
                success=result.get("success", False),
                data={
                    "output": result.get("output", ""),
                    "execution_time": result.get("execution_time", 0)
                },
                error=result.get("error")
            )
    
    async def _create_repl(self, params: Dict[str, Any]) -> ToolResult:
        """
        Create a new Repl using Replit API.
        
        Args:
            params: Parameters for Repl creation
            
        Returns:
            Tool execution result
        """
        title = params.get("title", "TorontoAITeamAgent Repl")
        description = params.get("description", "Created by TorontoAITeamAgent Team AI")
        language = params.get("language", "python")
        files = params.get("files", {})
        is_public = params.get("is_public", True)
        
        if not files:
            return ToolResult(
                success=False,
                data={},
                error="Files parameter is required for Repl creation"
            )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/v1/repls",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "title": title,
                    "description": description,
                    "language": language,
                    "files": files,
                    "is_public": is_public
                }
            )
            
            if response.status_code != 201:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Replit API error: {response.text}"
                )
                
            result = response.json()
            
            return ToolResult(
                success=True,
                data={
                    "repl_id": result.get("id"),
                    "url": result.get("url"),
                    "title": result.get("title")
                }
            )
    
    async def _get_repl(self, params: Dict[str, Any]) -> ToolResult:
        """
        Get information about a Repl using Replit API.
        
        Args:
            params: Parameters for getting Repl information
            
        Returns:
            Tool execution result
        """
        repl_id = params.get("repl_id")
        
        if not repl_id:
            return ToolResult(
                success=False,
                data={},
                error="Repl ID parameter is required"
            )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/v1/repls/{repl_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Replit API error: {response.text}"
                )
                
            result = response.json()
            
            return ToolResult(
                success=True,
                data={
                    "repl_id": result.get("id"),
                    "url": result.get("url"),
                    "title": result.get("title"),
                    "description": result.get("description"),
                    "language": result.get("language"),
                    "owner": result.get("owner"),
                    "created_at": result.get("created_at"),
                    "updated_at": result.get("updated_at")
                }
            )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Execute code in various programming languages",
            "Create and manage Repls for collaborative development",
            "Access Repl information and metadata"
        ]
