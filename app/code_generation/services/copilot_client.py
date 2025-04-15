"""
GitHub Copilot integration for TORONTO AI TEAM AGENT.

This module provides integration with GitHub Copilot for enhanced code generation
and development assistance capabilities.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Union

import requests

from app.core.error_handling import ErrorHandler, ErrorCategory, ErrorSeverity, safe_execute

logger = logging.getLogger(__name__)

class CopilotClient:
    """Client for interacting with GitHub Copilot API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the GitHub Copilot client.
        
        Args:
            api_key: GitHub Copilot API key (defaults to GITHUB_COPILOT_API_KEY environment variable)
            base_url: Base URL for the GitHub Copilot API
        """
        self.api_key = api_key or os.environ.get("GITHUB_COPILOT_API_KEY")
        if not self.api_key:
            logger.warning("GitHub Copilot API key not provided. Some functionality may be limited.")
            
        self.base_url = base_url or "https://api.githubcopilot.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def generate_code_completion(
        self, 
        prompt: str, 
        language: str, 
        context: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stop_sequences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate code completion using GitHub Copilot.
        
        Args:
            prompt: The prompt or code context to complete
            language: Programming language for the completion
            context: Additional context files (list of dicts with 'filename' and 'content' keys)
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stop_sequences: Sequences that will stop generation
            
        Returns:
            Dict containing the generated code completion
        """
        with ErrorHandler(
            error_category=ErrorCategory.CODE_GENERATION,
            error_message="Error generating code completion with GitHub Copilot",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/completions"
            
            payload = {
                "prompt": prompt,
                "language": language,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            if context:
                payload["context"] = context
                
            if stop_sequences:
                payload["stop"] = stop_sequences
            
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "completion": result.get("choices", [{}])[0].get("text", ""),
                "finish_reason": result.get("choices", [{}])[0].get("finish_reason", ""),
                "model": result.get("model", ""),
                "prompt": prompt,
                "language": language
            }
    
    def generate_code_suggestions(
        self, 
        file_content: str, 
        language: str,
        cursor_position: int,
        project_context: Optional[List[Dict[str, str]]] = None,
        max_suggestions: int = 3
    ) -> Dict[str, Any]:
        """
        Generate code suggestions at a specific cursor position.
        
        Args:
            file_content: Content of the file being edited
            language: Programming language of the file
            cursor_position: Position of the cursor in the file
            project_context: Additional project context files
            max_suggestions: Maximum number of suggestions to generate
            
        Returns:
            Dict containing the generated code suggestions
        """
        with ErrorHandler(
            error_category=ErrorCategory.CODE_GENERATION,
            error_message="Error generating code suggestions with GitHub Copilot",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/suggestions"
            
            payload = {
                "content": file_content,
                "language": language,
                "cursor_position": cursor_position,
                "max_suggestions": max_suggestions
            }
            
            if project_context:
                payload["project_context"] = project_context
            
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "suggestions": result.get("suggestions", []),
                "language": language,
                "cursor_position": cursor_position
            }
    
    def explain_code(
        self, 
        code: str, 
        language: str,
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate an explanation for the provided code.
        
        Args:
            code: The code to explain
            language: Programming language of the code
            detail_level: Level of detail for the explanation (low, medium, high)
            
        Returns:
            Dict containing the code explanation
        """
        with ErrorHandler(
            error_category=ErrorCategory.CODE_GENERATION,
            error_message="Error generating code explanation with GitHub Copilot",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/explain"
            
            payload = {
                "code": code,
                "language": language,
                "detail_level": detail_level
            }
            
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "explanation": result.get("explanation", ""),
                "language": language,
                "detail_level": detail_level
            }
    
    def generate_unit_tests(
        self, 
        code: str, 
        language: str,
        test_framework: Optional[str] = None,
        coverage_level: str = "high"
    ) -> Dict[str, Any]:
        """
        Generate unit tests for the provided code.
        
        Args:
            code: The code to generate tests for
            language: Programming language of the code
            test_framework: Testing framework to use (e.g., pytest, jest)
            coverage_level: Level of test coverage (low, medium, high)
            
        Returns:
            Dict containing the generated unit tests
        """
        with ErrorHandler(
            error_category=ErrorCategory.CODE_GENERATION,
            error_message="Error generating unit tests with GitHub Copilot",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/tests"
            
            payload = {
                "code": code,
                "language": language,
                "coverage_level": coverage_level
            }
            
            if test_framework:
                payload["test_framework"] = test_framework
            
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "tests": result.get("tests", ""),
                "language": language,
                "test_framework": result.get("test_framework", test_framework),
                "coverage_level": coverage_level
            }
    
    def refactor_code(
        self, 
        code: str, 
        language: str,
        goal: str,
        constraints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Refactor code according to specified goals and constraints.
        
        Args:
            code: The code to refactor
            language: Programming language of the code
            goal: Goal of the refactoring (e.g., "improve performance", "enhance readability")
            constraints: List of constraints for the refactoring
            
        Returns:
            Dict containing the refactored code
        """
        with ErrorHandler(
            error_category=ErrorCategory.CODE_GENERATION,
            error_message="Error refactoring code with GitHub Copilot",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.base_url}/refactor"
            
            payload = {
                "code": code,
                "language": language,
                "goal": goal
            }
            
            if constraints:
                payload["constraints"] = constraints
            
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "refactored_code": result.get("refactored_code", ""),
                "changes": result.get("changes", []),
                "language": language,
                "goal": goal
            }


class CopilotService:
    """Service for integrating GitHub Copilot with the code generation system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Copilot service.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        api_key = self.config.get("api_key") or os.environ.get("GITHUB_COPILOT_API_KEY")
        base_url = self.config.get("base_url")
        
        self.client = CopilotClient(api_key=api_key, base_url=base_url)
    
    def enhance_code_generation(
        self, 
        requirements: str, 
        language: str,
        existing_code: Optional[str] = None,
        project_context: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Enhance code generation using GitHub Copilot.
        
        Args:
            requirements: Requirements for the code to generate
            language: Programming language for the code
            existing_code: Existing code to enhance or extend
            project_context: Additional project context files
            
        Returns:
            Dict containing the enhanced code generation
        """
        # Prepare the prompt based on requirements and existing code
        if existing_code:
            prompt = f"// Requirements:\n// {requirements}\n\n// Existing code:\n{existing_code}\n\n// Enhanced implementation:\n"
        else:
            prompt = f"// Requirements:\n// {requirements}\n\n// Implementation:\n"
        
        # Convert project_context to the format expected by Copilot
        context = None
        if project_context:
            context = [
                {"filename": item.get("filename", f"context_{i}.{language}"), "content": item.get("content", "")}
                for i, item in enumerate(project_context)
            ]
        
        # Generate code completion
        completion_result = self.client.generate_code_completion(
            prompt=prompt,
            language=language,
            context=context,
            max_tokens=self.config.get("max_tokens", 1000),
            temperature=self.config.get("temperature", 0.7),
            top_p=self.config.get("top_p", 0.95)
        )
        
        return {
            "code": completion_result.get("completion", ""),
            "language": language,
            "requirements": requirements,
            "existing_code": existing_code
        }
    
    def generate_code_with_tests(
        self, 
        requirements: str, 
        language: str,
        test_framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code with corresponding unit tests.
        
        Args:
            requirements: Requirements for the code to generate
            language: Programming language for the code
            test_framework: Testing framework to use
            
        Returns:
            Dict containing the generated code and tests
        """
        # First, generate the implementation
        implementation_result = self.enhance_code_generation(
            requirements=requirements,
            language=language
        )
        
        implementation_code = implementation_result.get("code", "")
        
        # Then, generate tests for the implementation
        if implementation_code:
            tests_result = self.client.generate_unit_tests(
                code=implementation_code,
                language=language,
                test_framework=test_framework,
                coverage_level=self.config.get("coverage_level", "high")
            )
            
            return {
                "implementation": implementation_code,
                "tests": tests_result.get("tests", ""),
                "language": language,
                "test_framework": tests_result.get("test_framework", test_framework),
                "requirements": requirements
            }
        
        return implementation_result
    
    def improve_existing_code(
        self, 
        code: str, 
        language: str,
        improvement_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Improve existing code using GitHub Copilot.
        
        Args:
            code: The code to improve
            language: Programming language of the code
            improvement_type: Type of improvement (performance, readability, security, all)
            
        Returns:
            Dict containing the improved code
        """
        if improvement_type == "all" or improvement_type == "readability":
            # Improve code readability
            readability_result = self.client.refactor_code(
                code=code,
                language=language,
                goal="enhance readability",
                constraints=["maintain functionality", "improve variable names", "add comments"]
            )
            
            # Use the refactored code for subsequent improvements
            code = readability_result.get("refactored_code", code)
        
        if improvement_type == "all" or improvement_type == "performance":
            # Improve code performance
            performance_result = self.client.refactor_code(
                code=code,
                language=language,
                goal="improve performance",
                constraints=["maintain functionality", "optimize algorithms", "reduce complexity"]
            )
            
            # Use the refactored code for subsequent improvements
            code = performance_result.get("refactored_code", code)
        
        if improvement_type == "all" or improvement_type == "security":
            # Improve code security
            security_result = self.client.refactor_code(
                code=code,
                language=language,
                goal="enhance security",
                constraints=["maintain functionality", "fix vulnerabilities", "follow best practices"]
            )
            
            # Use the refactored code
            code = security_result.get("refactored_code", code)
        
        # Generate an explanation of the improvements
        explanation_result = self.client.explain_code(
            code=code,
            language=language,
            detail_level="high"
        )
        
        return {
            "improved_code": code,
            "explanation": explanation_result.get("explanation", ""),
            "language": language,
            "improvement_type": improvement_type
        }
    
    def generate_code_documentation(
        self, 
        code: str, 
        language: str,
        doc_style: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate documentation for code using GitHub Copilot.
        
        Args:
            code: The code to document
            language: Programming language of the code
            doc_style: Documentation style (standard, google, numpy, jsdoc)
            
        Returns:
            Dict containing the documented code
        """
        # Prepare the prompt based on the documentation style
        doc_style_comment = f"// Add {doc_style} style documentation to the following code:\n"
        prompt = f"{doc_style_comment}\n{code}\n\n// Documented code:\n"
        
        # Generate code completion for documentation
        completion_result = self.client.generate_code_completion(
            prompt=prompt,
            language=language,
            max_tokens=self.config.get("max_tokens", 2000),
            temperature=self.config.get("temperature", 0.5),
            top_p=self.config.get("top_p", 0.95)
        )
        
        return {
            "documented_code": completion_result.get("completion", ""),
            "language": language,
            "doc_style": doc_style
        }
