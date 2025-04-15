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


"""Security tools for TorontoAITeamAgent Team AI.

This module provides tools for security scanning using Bandit."""

from typing import Dict, Any, List, Optional
import os
import asyncio
import subprocess
import tempfile
import json
from ..base import BaseTool, ToolResult

class BanditTool(BaseTool):
    """Tool for security scanning Python code using Bandit."""
    
    name = "bandit"
    description = "Provides capabilities for security scanning Python code using Bandit."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Bandit tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.timeout = self.config.get("timeout", 60)  # Default timeout in seconds
        
        # Check if bandit is installed
        try:
            subprocess.run(["bandit", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise ImportError("Bandit is not installed. Install it with 'pip install bandit>=1.7.0'")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Bandit tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (scan)
                - code: Python code to scan
                - files: List of files to scan
                - recursive: Whether to scan directories recursively (optional)
                - severity: Minimum severity level to report (optional)
                - confidence: Minimum confidence level to report (optional)
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
            if operation == "scan":
                return await self._scan_code(params)
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
    
    async def _scan_code(self, params: Dict[str, Any]) -> ToolResult:
        """
        Scan Python code for security issues using Bandit.
        
        Args:
            params: Parameters for security scanning
            
        Returns:
            Tool execution result
        """
        code = params.get("code")
        files = params.get("files", [])
        recursive = params.get("recursive", True)
        severity = params.get("severity")
        confidence = params.get("confidence")
        timeout = params.get("timeout", self.timeout)
        
        # Build command
        cmd = ["bandit", "-f", "json"]
        
        if recursive:
            cmd.append("-r")
            
        if severity:
            cmd.extend(["-l", severity])
            
        if confidence:
            cmd.extend(["-c", confidence])
        
        if code:
            # Scan code string
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
                issues = []
                metrics = {}
                
                if process.stdout:
                    try:
                        result = json.loads(process.stdout)
                        
                        # Extract issues
                        for issue in result.get("results", []):
                            issues.append({
                                "severity": issue.get("issue_severity"),
                                "confidence": issue.get("issue_confidence"),
                                "text": issue.get("issue_text"),
                                "test_id": issue.get("test_id"),
                                "test_name": issue.get("test_name"),
                                "filename": issue.get("filename"),
                                "line": issue.get("line_number"),
                                "code": issue.get("code")
                            })
                        
                        # Extract metrics
                        metrics = {
                            "total_files": result.get("metrics", {}).get("_totals", {}).get("loc", 0),
                            "total_lines": result.get("metrics", {}).get("_totals", {}).get("nosec", 0),
                            "skipped_tests": result.get("metrics", {}).get("_totals", {}).get("skipped_tests", 0),
                            "high_severity": len([i for i in issues if i.get("severity") == "HIGH"]),
                            "medium_severity": len([i for i in issues if i.get("severity") == "MEDIUM"]),
                            "low_severity": len([i for i in issues if i.get("severity") == "LOW"])
                        }
                    except json.JSONDecodeError:
                        return ToolResult(
                            success=False,
                            data={},
                            error=f"Failed to parse Bandit output: {process.stdout}"
                        )
                
                return ToolResult(
                    success=len(issues) == 0,
                    data={
                        "issues": issues,
                        "metrics": metrics,
                        "issue_count": len(issues),
                        "has_issues": len(issues) > 0,
                        "stdout": process.stdout,
                        "stderr": process.stderr
                    },
                    error="Security issues found" if len(issues) > 0 else None
                )
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        elif files:
            # Scan files
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
            issues = []
            issues_by_file = {}
            metrics = {}
            
            if process.stdout:
                try:
                    result = json.loads(process.stdout)
                    
                    # Extract issues
                    for issue in result.get("results", []):
                        file_path = issue.get("filename")
                        
                        issue_data = {
                            "severity": issue.get("issue_severity"),
                            "confidence": issue.get("issue_confidence"),
                            "text": issue.get("issue_text"),
                            "test_id": issue.get("test_id"),
                            "test_name": issue.get("test_name"),
                            "filename": file_path,
                            "line": issue.get("line_number"),
                            "code": issue.get("code")
                        }
                        
                        issues.append(issue_data)
                        
                        if file_path not in issues_by_file:
                            issues_by_file[file_path] = []
                        issues_by_file[file_path].append(issue_data)
                    
                    # Extract metrics
                    metrics = {
                        "total_files": result.get("metrics", {}).get("_totals", {}).get("loc", 0),
                        "total_lines": result.get("metrics", {}).get("_totals", {}).get("nosec", 0),
                        "skipped_tests": result.get("metrics", {}).get("_totals", {}).get("skipped_tests", 0),
                        "high_severity": len([i for i in issues if i.get("severity") == "HIGH"]),
                        "medium_severity": len([i for i in issues if i.get("severity") == "MEDIUM"]),
                        "low_severity": len([i for i in issues if i.get("severity") == "LOW"])
                    }
                except json.JSONDecodeError:
                    return ToolResult(
                        success=False,
                        data={},
                        error=f"Failed to parse Bandit output: {process.stdout}"
                    )
            
            return ToolResult(
                success=len(issues) == 0,
                data={
                    "issues": issues,
                    "issues_by_file": issues_by_file,
                    "metrics": metrics,
                    "issue_count": len(issues),
                    "has_issues": len(issues) > 0,
                    "files_scanned": files,
                    "stdout": process.stdout,
                    "stderr": process.stderr
                },
                error="Security issues found" if len(issues) > 0 else None
            )
        
        else:
            return ToolResult(
                success=False,
                data={},
                error="Either code or files parameter is required for security scanning"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Security scanning for Python code",
            "Identify common security vulnerabilities",
            "Detect potentially dangerous code patterns",
            "Scan individual files or code strings"
        ]
