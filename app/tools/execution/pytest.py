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

This module provides tools for pytest testing."""

from typing import Dict, Any, List, Optional
import os
import asyncio
import subprocess
import tempfile
from ..base import BaseTool, ToolResult

class PytestTool(BaseTool):
    """Tool for running pytest tests."""
    
    name = "pytest"
    description = "Provides capabilities for running Python tests using pytest."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Pytest tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.timeout = self.config.get("timeout", 300)  # Default timeout in seconds
        self.max_output_size = self.config.get("max_output_size", 1024 * 1024)  # 1MB
        
        # Check if pytest is installed
        try:
            subprocess.run(["pytest", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise ImportError("Pytest is not installed. Install it with 'pip install pytest>=7.0.0'")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Pytest tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (run, generate, etc.)
                - test_files: List of test files to run
                - test_dir: Directory containing tests to run
                - source_files: List of source files to test
                - pytest_args: Additional pytest arguments
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
            if operation == "run":
                return await self._run_tests(params)
            elif operation == "generate":
                return await self._generate_tests(params)
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
    
    async def _run_tests(self, params: Dict[str, Any]) -> ToolResult:
        """
        Run pytest tests.
        
        Args:
            params: Parameters for running tests
            
        Returns:
            Tool execution result
        """
        test_files = params.get("test_files", [])
        test_dir = params.get("test_dir")
        pytest_args = params.get("pytest_args", [])
        timeout = params.get("timeout", self.timeout)
        
        if not test_files and not test_dir:
            return ToolResult(
                success=False,
                data={},
                error="Either test_files or test_dir parameter is required"
            )
        
        # Build command
        cmd = ["pytest", "-v"]
        
        # Add any additional pytest arguments
        if pytest_args:
            cmd.extend(pytest_args)
        
        # Add test files or directory
        if test_files:
            cmd.extend(test_files)
        elif test_dir:
            cmd.append(test_dir)
        
        # Run in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        process = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False  # Don't raise exception on test failures
            )
        )
        
        # Truncate output if too large
        stdout = process.stdout
        stderr = process.stderr
        
        if len(stdout) > self.max_output_size:
            stdout = stdout[:self.max_output_size] + "\n... (output truncated)"
            
        if len(stderr) > self.max_output_size:
            stderr = stderr[:self.max_output_size] + "\n... (output truncated)"
        
        # Parse test results
        test_summary = self._parse_test_summary(stdout)
        
        return ToolResult(
            success=process.returncode == 0,
            data={
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "test_summary": test_summary
            },
            error="Tests failed" if process.returncode != 0 else None
        )
    
    async def _generate_tests(self, params: Dict[str, Any]) -> ToolResult:
        """
        Generate pytest tests for source files.
        
        Args:
            params: Parameters for generating tests
            
        Returns:
            Tool execution result
        """
        source_files = params.get("source_files", [])
        
        if not source_files:
            return ToolResult(
                success=False,
                data={},
                error="Source files parameter is required for test generation"
            )
        
        # Create a temporary directory for the work
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy source files to temporary directory
            for file_path in source_files:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    temp_path = os.path.join(temp_dir, file_name)
                    with open(file_path, "r") as src, open(temp_path, "w") as dst:
                        dst.write(src.read())
            
            # Generate test file names
            test_files = {}
            for file_path in source_files:
                file_name = os.path.basename(file_path)
                module_name = os.path.splitext(file_name)[0]
                test_file_name = f"test_{module_name}.py"
                test_files[file_path] = test_file_name
            
            # Use OpenAI to generate tests (assuming OpenAI tool is available)
            from ..core_ai.openai import OpenAITool
            openai_tool = OpenAITool(self.config.get("openai_config"))
            
            generated_tests = {}
            for file_path, test_file_name in test_files.items():
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        source_code = f.read()
                    
                    # Generate tests using OpenAI
                    result = await openai_tool.execute({
                        "operation": "chat",
                        "messages": [
                            {"role": "system", "content": "You are an expert Python developer specializing in writing pytest tests. Generate comprehensive pytest tests for the provided Python code."},
                            {"role": "user", "content": f"Generate pytest tests for the following Python code. Include tests for all functions and edge cases. Return only the test code without explanations.\n\n```python\n{source_code}\n```"}
                        ]
                    })
                    
                    if result.success:
                        test_code = result.data["choices"][0]["message"]["content"]
                        generated_tests[file_path] = {
                            "test_file_name": test_file_name,
                            "test_code": test_code
                        }
                    else:
                        return ToolResult(
                            success=False,
                            data={},
                            error=f"Failed to generate tests for {file_path}: {result.error}"
                        )
            
            return ToolResult(
                success=True,
                data={
                    "generated_tests": generated_tests
                }
            )
    
    def _parse_test_summary(self, output: str) -> Dict[str, Any]:
        """Parse pytest output to extract test summary.
        
        Args:
            output: Pytest output
            
        Returns:
            Test summary"""
        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "warnings": 0,
            "duration": 0
        }
        
        # Look for the summary line
        for line in output.splitlines():
            if "= " in line and " in " in line and "s =" in line:
                parts = line.strip().split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        summary["passed"] = int(parts[i-1])
                    elif part == "failed":
                        summary["failed"] = int(parts[i-1])
                    elif part == "skipped":
                        summary["skipped"] = int(parts[i-1])
                    elif part == "errors":
                        summary["errors"] = int(parts[i-1])
                    elif part == "warnings":
                        summary["warnings"] = int(parts[i-1])
                
                # Calculate total
                summary["total"] = summary["passed"] + summary["failed"] + summary["skipped"] + summary["errors"]
                
                # Extract duration
                for i, part in enumerate(parts):
                    if part == "in" and i+1 < len(parts) and "s" in parts[i+1]:
                        try:
                            summary["duration"] = float(parts[i+1].replace("s", ""))
                        except ValueError:
                            pass
                
                break
        
        return summary
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Run pytest tests on Python code",
            "Generate pytest tests for Python code",
            "Parse and analyze test results"
        ]
