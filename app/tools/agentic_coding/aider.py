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


"""Agentic Coding tools for TorontoAITeamAgent Team AI.

This module provides tools for agentic coding using Aider."""

from typing import Dict, Any, List, Optional
import os
import json
import asyncio
import subprocess
import tempfile
from ..base import BaseTool, ToolResult

class AiderTool(BaseTool):
    """Tool for agentic coding using Aider."""
    
    name = "aider"
    description = "Provides AI-assisted coding capabilities using Aider."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Aider tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.openai_api_key = self.config.get("openai_api_key", os.environ.get("OPENAI_API_KEY"))
        self.model = self.config.get("model", "gpt-4o")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for Aider")
            
        # Check if aider is installed
        try:
            subprocess.run(["aider", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise ImportError("Aider is not installed. Install it with 'pip install aider-chat>=0.10.0'")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Aider tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (edit, chat, etc.)
                - files: List of files to edit
                - instructions: Instructions for editing
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
            if operation == "edit":
                return await self._edit_files(params)
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
    
    async def _edit_files(self, params: Dict[str, Any]) -> ToolResult:
        """
        Edit files using Aider.
        
        Args:
            params: Parameters for file editing
            
        Returns:
            Tool execution result
        """
        files = params.get("files", [])
        instructions = params.get("instructions", "")
        
        if not files:
            return ToolResult(
                success=False,
                data={},
                error="Files parameter is required for editing"
            )
            
        if not instructions:
            return ToolResult(
                success=False,
                data={},
                error="Instructions parameter is required for editing"
            )
        
        # Create a temporary directory for the work
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create instruction file
            instruction_file = os.path.join(temp_dir, "instructions.txt")
            with open(instruction_file, "w") as f:
                f.write(instructions)
            
            # Copy files to temporary directory
            file_paths = []
            for file_info in files:
                if isinstance(file_info, str):
                    # Just a file path
                    src_path = file_info
                    file_name = os.path.basename(src_path)
                else:
                    # Dictionary with path and content
                    src_path = file_info.get("path")
                    content = file_info.get("content")
                    file_name = os.path.basename(src_path)
                    
                    # Write content to temporary file
                    temp_path = os.path.join(temp_dir, file_name)
                    with open(temp_path, "w") as f:
                        f.write(content)
                    
                    file_paths.append(temp_path)
                    continue
                
                # Copy existing file
                if os.path.exists(src_path):
                    temp_path = os.path.join(temp_dir, file_name)
                    with open(src_path, "r") as src, open(temp_path, "w") as dst:
                        dst.write(src.read())
                    file_paths.append(temp_path)
            
            # Run aider in the temporary directory
            cmd = [
                "aider",
                "--no-git",
                "--model", self.model,
                "--input-file", instruction_file,
                "--yes"  # Auto-apply changes
            ] + file_paths
            
            env = os.environ.copy()
            env["OPENAI_API_KEY"] = self.openai_api_key
            
            # Run in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=temp_dir
                )
            )
            
            # Check for errors
            if process.returncode != 0:
                return ToolResult(
                    success=False,
                    data={
                        "stdout": process.stdout,
                        "stderr": process.stderr
                    },
                    error=f"Aider failed with exit code {process.returncode}"
                )
            
            # Read modified files
            modified_files = {}
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                with open(file_path, "r") as f:
                    modified_files[file_name] = f.read()
            
            return ToolResult(
                success=True,
                data={
                    "modified_files": modified_files,
                    "stdout": process.stdout,
                    "stderr": process.stderr
                }
            )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "AI-assisted code editing",
            "Multi-file code modifications",
            "Code generation based on natural language instructions"
        ]
