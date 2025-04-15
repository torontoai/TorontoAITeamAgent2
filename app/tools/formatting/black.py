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


"""Formatting/Style tools for TorontoAITeamAgent Team AI.

This module provides tools for code formatting using Black."""

from typing import Dict, Any, List, Optional
import os
import asyncio
import subprocess
import tempfile
from ..base import BaseTool, ToolResult

class BlackTool(BaseTool):
    """Tool for formatting Python code using Black."""
    
    name = "black"
    description = "Provides capabilities for formatting Python code using Black."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Black tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.line_length = self.config.get("line_length", 88)
        self.timeout = self.config.get("timeout", 30)  # Default timeout in seconds
        
        # Check if black is installed
        try:
            subprocess.run(["black", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise ImportError("Black is not installed. Install it with 'pip install black>=23.0.0'")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Black tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (format, check)
                - code: Python code to format (for format operation)
                - files: List of files to format or check
                - line_length: Maximum line length (optional)
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
            if operation == "format":
                return await self._format_code(params)
            elif operation == "check":
                return await self._check_code(params)
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
    
    async def _format_code(self, params: Dict[str, Any]) -> ToolResult:
        """
        Format Python code using Black.
        
        Args:
            params: Parameters for code formatting
            
        Returns:
            Tool execution result
        """
        code = params.get("code")
        files = params.get("files", [])
        line_length = params.get("line_length", self.line_length)
        timeout = params.get("timeout", self.timeout)
        
        if code:
            # Format code string
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(code)
            
            try:
                # Run black on the temporary file
                cmd = ["black", "--quiet", f"--line-length={line_length}", temp_file_path]
                
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
                
                if process.returncode != 0:
                    return ToolResult(
                        success=False,
                        data={
                            "stdout": process.stdout,
                            "stderr": process.stderr
                        },
                        error=f"Black failed with exit code {process.returncode}"
                    )
                
                # Read the formatted code
                with open(temp_file_path, "r") as f:
                    formatted_code = f.read()
                
                return ToolResult(
                    success=True,
                    data={
                        "formatted_code": formatted_code
                    }
                )
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        elif files:
            # Format files
            cmd = ["black", "--quiet", f"--line-length={line_length}"] + files
            
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
            
            return ToolResult(
                success=process.returncode == 0,
                data={
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "files_formatted": files
                },
                error=f"Black failed with exit code {process.returncode}" if process.returncode != 0 else None
            )
        
        else:
            return ToolResult(
                success=False,
                data={},
                error="Either code or files parameter is required for formatting"
            )
    
    async def _check_code(self, params: Dict[str, Any]) -> ToolResult:
        """
        Check if Python code is formatted according to Black.
        
        Args:
            params: Parameters for code checking
            
        Returns:
            Tool execution result
        """
        code = params.get("code")
        files = params.get("files", [])
        line_length = params.get("line_length", self.line_length)
        timeout = params.get("timeout", self.timeout)
        
        if code:
            # Check code string
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(code)
            
            try:
                # Run black in check mode on the temporary file
                cmd = ["black", "--check", "--quiet", f"--line-length={line_length}", temp_file_path]
                
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
                
                return ToolResult(
                    success=True,
                    data={
                        "is_formatted": process.returncode == 0,
                        "stdout": process.stdout,
                        "stderr": process.stderr
                    }
                )
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        elif files:
            # Check files
            cmd = ["black", "--check", "--quiet", f"--line-length={line_length}"] + files
            
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
            
            return ToolResult(
                success=True,
                data={
                    "is_formatted": process.returncode == 0,
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "files_checked": files
                }
            )
        
        else:
            return ToolResult(
                success=False,
                data={},
                error="Either code or files parameter is required for checking"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Format Python code according to Black style guide",
            "Check if Python code is formatted according to Black style guide",
            "Format individual files or code strings"
        ]
