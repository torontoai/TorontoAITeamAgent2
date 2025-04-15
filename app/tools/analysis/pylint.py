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


"""Analysis tools for TorontoAITeamAgent Team AI.

This module provides tools for code analysis using Pylint."""

from typing import Dict, Any, List, Optional
import os
import asyncio
import subprocess
import tempfile
import json
import re
from ..base import BaseTool, ToolResult

class PylintTool(BaseTool):
    """Tool for analyzing Python code using Pylint."""
    
    name = "pylint"
    description = "Provides capabilities for analyzing Python code using Pylint."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Pylint tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.timeout = self.config.get("timeout", 60)  # Default timeout in seconds
        
        # Check if pylint is installed
        try:
            subprocess.run(["pylint", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise ImportError("Pylint is not installed. Install it with 'pip install pylint>=2.17.0'")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Pylint tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (analyze)
                - code: Python code to analyze
                - files: List of files to analyze
                - rcfile: Path to pylintrc file (optional)
                - disable: List of messages to disable (optional)
                - enable: List of messages to enable (optional)
                - timeout: Command timeout in seconds (optional)
                
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
            if operation == "analyze":
                return await self._analyze_code(params)
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
    
    async def _analyze_code(self, params: Dict[str, Any]) -> ToolResult:
        """
        Analyze Python code using Pylint.
        
        Args:
            params: Parameters for code analysis
            
        Returns:
            Tool execution result
        """
        code = params.get("code")
        files = params.get("files", [])
        rcfile = params.get("rcfile")
        disable = params.get("disable", [])
        enable = params.get("enable", [])
        timeout = params.get("timeout", self.timeout)
        
        # Build command
        cmd = ["pylint", "--output-format=json"]
        
        if rcfile:
            cmd.append(f"--rcfile={rcfile}")
            
        if disable:
            cmd.append(f"--disable={','.join(disable)}")
            
        if enable:
            cmd.append(f"--enable={','.join(enable)}")
        
        if code:
            # Analyze code string
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(code)
            
            try:
                # Add the temporary file to the command
                cmd.append(temp_file_path)
                
                # Run in a separate thread to avoid blocking
                loop = asyncio.get_event_loop()
                process = await loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False
                    )
                )
                
                # Parse the JSON output
                messages = []
                score = 0.0
                
                if process.stdout:
                    try:
                        results = json.loads(process.stdout)
                        
                        # Extract messages
                        for message in results:
                            messages.append({
                                "type": message.get("type"),
                                "module": message.get("module"),
                                "obj": message.get("obj"),
                                "line": message.get("line"),
                                "column": message.get("column"),
                                "message_id": message.get("message-id"),
                                "symbol": message.get("symbol"),
                                "message": message.get("message")
                            })
                        
                        # Extract score from stderr
                        if process.stderr:
                            score_match = re.search(r"Your code has been rated at ([-\d.]+)/10", process.stderr)
                            if score_match:
                                score = float(score_match.group(1))
                    except json.JSONDecodeError:
                        return ToolResult(
                            success=False,
                            data={},
                            error=f"Failed to parse Pylint output: {process.stdout}"
                        )
                
                return ToolResult(
                    success=True,
                    data={
                        "messages": messages,
                        "message_count": len(messages),
                        "score": score,
                        "stderr": process.stderr
                    }
                )
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        elif files:
            # Analyze files
            cmd.extend(files)
            
            # Run in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False
                )
            )
            
            # Parse the JSON output
            messages_by_file = {}
            scores_by_file = {}
            
            if process.stdout:
                try:
                    results = json.loads(process.stdout)
                    
                    # Extract messages
                    for message in results:
                        file_path = message.get("path")
                        if file_path not in messages_by_file:
                            messages_by_file[file_path] = []
                        
                        messages_by_file[file_path].append({
                            "type": message.get("type"),
                            "module": message.get("module"),
                            "obj": message.get("obj"),
                            "line": message.get("line"),
                            "column": message.get("column"),
                            "message_id": message.get("message-id"),
                            "symbol": message.get("symbol"),
                            "message": message.get("message")
                        })
                    
                    # Extract scores from stderr
                    if process.stderr:
                        for line in process.stderr.splitlines():
                            score_match = re.search(r"(\S+) has been rated at ([-\d.]+)/10", line)
                            if score_match:
                                file_name = score_match.group(1)
                                score = float(score_match.group(2))
                                scores_by_file[file_name] = score
                except json.JSONDecodeError:
                    return ToolResult(
                        success=False,
                        data={},
                        error=f"Failed to parse Pylint output: {process.stdout}"
                    )
            
            # Calculate total message count
            total_messages = sum(len(messages) for messages in messages_by_file.values())
            
            # Calculate average score
            average_score = 0.0
            if scores_by_file:
                average_score = sum(scores_by_file.values()) / len(scores_by_file)
            
            return ToolResult(
                success=True,
                data={
                    "messages_by_file": messages_by_file,
                    "scores_by_file": scores_by_file,
                    "message_count": total_messages,
                    "average_score": average_score,
                    "files_analyzed": files,
                    "stderr": process.stderr
                }
            )
        
        else:
            return ToolResult(
                success=False,
                data={},
                error="Either code or files parameter is required for analysis"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Analyze Python code for bugs, code smells, and maintainability issues",
            "Provide detailed code quality metrics and scores",
            "Identify potential errors, bad practices, and style violations",
            "Analyze individual files or code strings"
        ]
