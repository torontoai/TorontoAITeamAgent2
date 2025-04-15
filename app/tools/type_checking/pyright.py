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


"""Type Checking tools for TorontoAITeamAgent Team AI.

This module provides tools for type checking using Pyright."""

from typing import Dict, Any, List, Optional
import os
import asyncio
import subprocess
import tempfile
import json
from ..base import BaseTool, ToolResult

class PyrightTool(BaseTool):
    """Tool for type checking Python code using Pyright."""
    
    name = "pyright"
    description = "Provides capabilities for static type checking Python code using Pyright."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Pyright tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.timeout = self.config.get("timeout", 60)  # Default timeout in seconds
        
        # Check if pyright is installed
        try:
            subprocess.run(["pyright", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise ImportError("Pyright is not installed. Install it with 'npm install -g pyright'")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Pyright tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (check)
                - code: Python code to check
                - files: List of files to check
                - typeCheckingMode: Type checking mode (optional, 'basic', 'strict', or 'off')
                - reportMissingImports: Whether to report missing imports (optional)
                - reportMissingTypeStubs: Whether to report missing type stubs (optional)
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
            if operation == "check":
                return await self._check_types(params)
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
    
    async def _check_types(self, params: Dict[str, Any]) -> ToolResult:
        """
        Check types in Python code using Pyright.
        
        Args:
            params: Parameters for type checking
            
        Returns:
            Tool execution result
        """
        code = params.get("code")
        files = params.get("files", [])
        type_checking_mode = params.get("typeCheckingMode")
        report_missing_imports = params.get("reportMissingImports")
        report_missing_type_stubs = params.get("reportMissingTypeStubs")
        timeout = params.get("timeout", self.timeout)
        
        # Build command
        cmd = ["pyright", "--outputjson"]
        
        # Create pyrightconfig.json if needed
        config_file = None
        if type_checking_mode or report_missing_imports is not None or report_missing_type_stubs is not None:
            config = {}
            
            if type_checking_mode:
                config["typeCheckingMode"] = type_checking_mode
                
            if report_missing_imports is not None:
                config["reportMissingImports"] = report_missing_imports
                
            if report_missing_type_stubs is not None:
                config["reportMissingTypeStubs"] = report_missing_type_stubs
            
            # Create temporary config file
            config_file = tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False)
            json.dump(config, config_file)
            config_file.close()
            
            cmd.extend(["--project", config_file.name])
        
        if code:
            # Check code string
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
                diagnostics = []
                summary = {}
                
                if process.stdout:
                    try:
                        result = json.loads(process.stdout)
                        
                        # Extract diagnostics
                        for diag in result.get("diagnostics", []):
                            diagnostics.append({
                                "file": diag.get("file"),
                                "severity": diag.get("severity"),
                                "message": diag.get("message"),
                                "rule": diag.get("rule"),
                                "line": diag.get("range", {}).get("start", {}).get("line"),
                                "column": diag.get("range", {}).get("start", {}).get("character")
                            })
                        
                        # Extract summary
                        summary = {
                            "error_count": result.get("summary", {}).get("errorCount", 0),
                            "warning_count": result.get("summary", {}).get("warningCount", 0),
                            "information_count": result.get("summary", {}).get("informationCount", 0),
                            "time": result.get("summary", {}).get("time", 0)
                        }
                    except json.JSONDecodeError:
                        return ToolResult(
                            success=False,
                            data={},
                            error=f"Failed to parse Pyright output: {process.stdout}"
                        )
                
                return ToolResult(
                    success=summary.get("error_count", 0) == 0,
                    data={
                        "diagnostics": diagnostics,
                        "summary": summary,
                        "stdout": process.stdout,
                        "stderr": process.stderr
                    },
                    error="Type checking failed" if summary.get("error_count", 0) > 0 else None
                )
            finally:
                # Clean up the temporary files
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                if config_file and os.path.exists(config_file.name):
                    os.unlink(config_file.name)
        
        elif files:
            # Check files
            cmd.extend(files)
            
            try:
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
                diagnostics = []
                diagnostics_by_file = {}
                summary = {}
                
                if process.stdout:
                    try:
                        result = json.loads(process.stdout)
                        
                        # Extract diagnostics
                        for diag in result.get("diagnostics", []):
                            file_path = diag.get("file")
                            
                            diagnostic = {
                                "file": file_path,
                                "severity": diag.get("severity"),
                                "message": diag.get("message"),
                                "rule": diag.get("rule"),
                                "line": diag.get("range", {}).get("start", {}).get("line"),
                                "column": diag.get("range", {}).get("start", {}).get("character")
                            }
                            
                            diagnostics.append(diagnostic)
                            
                            if file_path not in diagnostics_by_file:
                                diagnostics_by_file[file_path] = []
                            diagnostics_by_file[file_path].append(diagnostic)
                        
                        # Extract summary
                        summary = {
                            "error_count": result.get("summary", {}).get("errorCount", 0),
                            "warning_count": result.get("summary", {}).get("warningCount", 0),
                            "information_count": result.get("summary", {}).get("informationCount", 0),
                            "time": result.get("summary", {}).get("time", 0)
                        }
                    except json.JSONDecodeError:
                        return ToolResult(
                            success=False,
                            data={},
                            error=f"Failed to parse Pyright output: {process.stdout}"
                        )
                
                return ToolResult(
                    success=summary.get("error_count", 0) == 0,
                    data={
                        "diagnostics": diagnostics,
                        "diagnostics_by_file": diagnostics_by_file,
                        "summary": summary,
                        "files_checked": files,
                        "stdout": process.stdout,
                        "stderr": process.stderr
                    },
                    error="Type checking failed" if summary.get("error_count", 0) > 0 else None
                )
            finally:
                # Clean up the temporary config file
                if config_file and os.path.exists(config_file.name):
                    os.unlink(config_file.name)
        
        else:
            return ToolResult(
                success=False,
                data={},
                error="Either code or files parameter is required for type checking"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Static type checking for Python code using Pyright",
            "Identify type errors and inconsistencies",
            "Configurable type checking modes (basic, strict)",
            "Check individual files or code strings"
        ]
