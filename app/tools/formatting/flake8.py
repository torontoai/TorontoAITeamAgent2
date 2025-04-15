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

This module provides tools for code linting using Flake8."""

from typing import Dict, Any, List, Optional
import os
import asyncio
import subprocess
import tempfile
import json
from ..base import BaseTool, ToolResult

class Flake8Tool(BaseTool):
    """Tool for linting Python code using Flake8."""
    
    name = "flake8"
    description = "Provides capabilities for linting Python code using Flake8."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Flake8 tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.max_line_length = self.config.get("max_line_length", 88)
        self.timeout = self.config.get("timeout", 30)  # Default timeout in seconds
        
        # Check if flake8 is installed
        try:
            subprocess.run(["flake8", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise ImportError("Flake8 is not installed. Install it with 'pip install flake8>=6.0.0'")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Flake8 tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (lint)
                - code: Python code to lint
                - files: List of files to lint
                - max_line_length: Maximum line length (optional)
                - ignore: List of error codes to ignore (optional)
                - select: List of error codes to select (optional)
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
            if operation == "lint":
                return await self._lint_code(params)
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
    
    async def _lint_code(self, params: Dict[str, Any]) -> ToolResult:
        """
        Lint Python code using Flake8.
        
        Args:
            params: Parameters for code linting
            
        Returns:
            Tool execution result
        """
        code = params.get("code")
        files = params.get("files", [])
        max_line_length = params.get("max_line_length", self.max_line_length)
        ignore = params.get("ignore", [])
        select = params.get("select", [])
        timeout = params.get("timeout", self.timeout)
        
        # Build command
        cmd = ["flake8", "--format=json"]
        
        if max_line_length:
            cmd.append(f"--max-line-length={max_line_length}")
            
        if ignore:
            cmd.append(f"--ignore={','.join(ignore)}")
            
        if select:
            cmd.append(f"--select={','.join(select)}")
        
        if code:
            # Lint code string
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
                violations = []
                if process.stdout:
                    try:
                        violations_dict = json.loads(process.stdout)
                        for file_path, file_violations in violations_dict.items():
                            for violation in file_violations:
                                violations.append({
                                    "line": violation.get("line_number"),
                                    "column": violation.get("column_number"),
                                    "code": violation.get("code"),
                                    "message": violation.get("text")
                                })
                    except json.JSONDecodeError:
                        # Fall back to parsing the text output
                        for line in process.stdout.splitlines():
                            if ":" in line:
                                parts = line.split(":", 4)
                                if len(parts) >= 4:
                                    violations.append({
                                        "line": int(parts[1]),
                                        "column": int(parts[2]),
                                        "code": parts[3].strip().split(" ")[0],
                                        "message": parts[3].strip()
                                    })
                
                return ToolResult(
                    success=True,
                    data={
                        "violations": violations,
                        "violation_count": len(violations),
                        "has_violations": len(violations) > 0
                    }
                )
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        elif files:
            # Lint files
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
            violations_by_file = {}
            if process.stdout:
                try:
                    violations_dict = json.loads(process.stdout)
                    for file_path, file_violations in violations_dict.items():
                        violations_by_file[file_path] = []
                        for violation in file_violations:
                            violations_by_file[file_path].append({
                                "line": violation.get("line_number"),
                                "column": violation.get("column_number"),
                                "code": violation.get("code"),
                                "message": violation.get("text")
                            })
                except json.JSONDecodeError:
                    # Fall back to parsing the text output
                    for line in process.stdout.splitlines():
                        if ":" in line:
                            parts = line.split(":", 4)
                            if len(parts) >= 4:
                                file_path = parts[0]
                                if file_path not in violations_by_file:
                                    violations_by_file[file_path] = []
                                violations_by_file[file_path].append({
                                    "line": int(parts[1]),
                                    "column": int(parts[2]),
                                    "code": parts[3].strip().split(" ")[0],
                                    "message": parts[3].strip()
                                })
            
            # Count total violations
            total_violations = sum(len(violations) for violations in violations_by_file.values())
            
            return ToolResult(
                success=True,
                data={
                    "violations_by_file": violations_by_file,
                    "violation_count": total_violations,
                    "has_violations": total_violations > 0,
                    "files_checked": files
                }
            )
        
        else:
            return ToolResult(
                success=False,
                data={},
                error="Either code or files parameter is required for linting"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Lint Python code for style and syntax issues",
            "Identify PEP 8 violations in Python code",
            "Check code quality and maintainability",
            "Lint individual files or code strings"
        ]
