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


"""Core AI/LLM tools for TorontoAITeamAgent Team AI.

This module provides tools for interacting with Ollama API."""

from typing import Dict, Any, List, Optional
import os
import json
import asyncio
import httpx
from ..base import BaseTool, ToolResult

class OllamaTool(BaseTool):
    """Tool for interacting with Ollama API."""
    
    name = "ollama"
    description = "Provides access to Ollama models for local LLM inference."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Ollama tool.
        
        Args:
            config: Tool configuration with optional host and model settings"""
        super().__init__(config)
        self.host = self.config.get("host", "http://localhost:11434")
        self.default_model = self.config.get("default_model", "llama3")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Ollama tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (generate, embeddings, etc.)
                - model: Model to use (optional, defaults to config)
                - prompt: Text prompt for generation
                - text: Text for embeddings
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
            if operation == "generate":
                return await self._generate(params)
            elif operation == "embeddings":
                return await self._embeddings(params)
            elif operation == "list_models":
                return await self._list_models()
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
    
    async def _generate(self, params: Dict[str, Any]) -> ToolResult:
        """
        Generate text using Ollama.
        
        Args:
            params: Parameters for text generation
            
        Returns:
            Tool execution result
        """
        model = params.get("model", self.default_model)
        prompt = params.get("prompt", "")
        system = params.get("system", "")
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens")
        
        if not prompt:
            return ToolResult(
                success=False,
                data={},
                error="Prompt parameter is required for text generation"
            )
        
        request_data = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
        }
        
        if system:
            request_data["system"] = system
            
        if max_tokens:
            request_data["num_predict"] = max_tokens
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.host}/api/generate",
                json=request_data
            )
            
            if response.status_code != 200:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Ollama API error: {response.text}"
                )
                
            result = response.json()
            
            return ToolResult(
                success=True,
                data={
                    "model": model,
                    "response": result.get("response", ""),
                    "context": result.get("context", []),
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0)
                }
            )
    
    async def _embeddings(self, params: Dict[str, Any]) -> ToolResult:
        """
        Create embeddings using Ollama.
        
        Args:
            params: Parameters for embedding creation
            
        Returns:
            Tool execution result
        """
        model = params.get("model", self.default_model)
        text = params.get("text", "")
        
        if not text:
            return ToolResult(
                success=False,
                data={},
                error="Text parameter is required for embedding creation"
            )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.host}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                }
            )
            
            if response.status_code != 200:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Ollama API error: {response.text}"
                )
                
            result = response.json()
            
            return ToolResult(
                success=True,
                data={
                    "model": model,
                    "embedding": result.get("embedding", [])
                }
            )
    
    async def _list_models(self) -> ToolResult:
        """
        List available Ollama models.
        
        Returns:
            Tool execution result
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.host}/api/tags")
            
            if response.status_code != 200:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Ollama API error: {response.text}"
                )
                
            result = response.json()
            
            return ToolResult(
                success=True,
                data={
                    "models": [
                        {
                            "name": model.get("name", ""),
                            "size": model.get("size", 0),
                            "modified_at": model.get("modified_at", "")
                        }
                        for model in result.get("models", [])
                    ]
                }
            )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Text generation with local Ollama models",
            "Embeddings creation for semantic search and analysis",
            "Model management and listing"
        ]
