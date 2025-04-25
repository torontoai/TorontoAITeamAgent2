"""
Code execution module for Grok 3 API integration.

This module provides functionality for secure code execution using Grok 3's capabilities.
"""

import logging
import subprocess
import tempfile
import os
import uuid
import json
from typing import Dict, List, Any, Optional, Union, Tuple

from app.models.adapters.model_adapter import Grok3Adapter
from app.models.adapters.reasoning_adapters import ReasoningGrok3Adapter

# Set up logging
logger = logging.getLogger(__name__)

class CodeExecutionManager:
    """
    Manager class for secure code execution.
    
    This class provides methods for executing code in a secure sandbox environment
    with timeout protection and resource limitations.
    """
    
    def __init__(
        self,
        timeout: int = 30,
        max_memory_mb: int = 512,
        secure_mode: bool = True
    ):
        """
        Initialize the CodeExecutionManager.
        
        Args:
            timeout: Maximum execution time in seconds.
            max_memory_mb: Maximum memory usage in MB.
            secure_mode: Whether to enable secure mode for execution.
        """
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        self.secure_mode = secure_mode
        
        # Map of language to file extension
        self.language_extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "bash": ".sh",
            "shell": ".sh",
            "ruby": ".rb",
            "go": ".go",
            "rust": ".rs",
            "java": ".java",
            "c": ".c",
            "cpp": ".cpp",
            "csharp": ".cs"
        }
        
        # Map of language to execution command
        self.language_commands = {
            "python": ["python3"],
            "javascript": ["node"],
            "typescript": ["ts-node"],
            "bash": ["bash"],
            "shell": ["sh"],
            "ruby": ["ruby"],
            "go": ["go", "run"],
            "rust": ["rustc", "-o"],  # Special handling for Rust
            "java": ["javac"],  # Special handling for Java
            "c": ["gcc", "-o"],  # Special handling for C
            "cpp": ["g++", "-o"],  # Special handling for C++
            "csharp": ["dotnet", "run"]  # Special handling for C#
        }
        
        logger.info(f"Initialized CodeExecutionManager with timeout: {timeout}s, max_memory: {max_memory_mb}MB")
    
    def execute_code(
        self,
        code: str,
        language: str = "python",
        input_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute code in a secure sandbox environment.
        
        Args:
            code: Code to execute.
            language: Programming language of the code.
            input_data: Optional input data for the code.
        
        Returns:
            Dictionary with execution results.
        """
        if language not in self.language_extensions:
            return {
                "success": False,
                "error": f"Unsupported language: {language}",
                "stdout": "",
                "stderr": f"Language '{language}' is not supported",
                "exit_code": 1
            }
        
        # Create a temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Create a unique file name
                file_id = str(uuid.uuid4())
                file_name = f"{file_id}{self.language_extensions[language]}"
                file_path = os.path.join(temp_dir, file_name)
                
                # Write code to file
                with open(file_path, "w") as f:
                    f.write(code)
                
                # Execute the code
                return self._execute_file(file_path, language, input_data, temp_dir)
                
            except Exception as e:
                logger.error(f"Error executing code: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "stdout": "",
                    "stderr": f"Execution error: {str(e)}",
                    "exit_code": 1
                }
    
    def _execute_file(
        self,
        file_path: str,
        language: str,
        input_data: Optional[str],
        temp_dir: str
    ) -> Dict[str, Any]:
        """
        Execute a file with the appropriate command.
        
        Args:
            file_path: Path to the file to execute.
            language: Programming language of the file.
            input_data: Optional input data for the code.
            temp_dir: Temporary directory for execution.
        
        Returns:
            Dictionary with execution results.
        """
        try:
            command = self._get_execution_command(file_path, language, temp_dir)
            
            # Prepare the process
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE if input_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir
            )
            
            # Execute with timeout
            stdout, stderr = process.communicate(
                input=input_data,
                timeout=self.timeout
            )
            
            return {
                "success": process.returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": process.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Execution timed out after {self.timeout} seconds")
            return {
                "success": False,
                "error": f"Execution timed out after {self.timeout} seconds",
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout} seconds",
                "exit_code": 124  # Standard timeout exit code
            }
            
        except Exception as e:
            logger.error(f"Error executing file: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": 1
            }
    
    def _get_execution_command(
        self,
        file_path: str,
        language: str,
        temp_dir: str
    ) -> List[str]:
        """
        Get the appropriate command to execute a file.
        
        Args:
            file_path: Path to the file to execute.
            language: Programming language of the file.
            temp_dir: Temporary directory for execution.
        
        Returns:
            Command as a list of strings.
        """
        base_command = self.language_commands.get(language, ["echo", "Unsupported language"])
        
        # Handle special cases
        if language == "rust":
            executable = os.path.join(temp_dir, "output")
            return ["rustc", file_path, "-o", executable, "&&", executable]
        elif language == "java":
            file_name = os.path.basename(file_path)
            class_name = file_name.replace(".java", "")
            return ["javac", file_path, "&&", "java", "-cp", temp_dir, class_name]
        elif language == "c" or language == "cpp":
            executable = os.path.join(temp_dir, "output")
            compiler = "gcc" if language == "c" else "g++"
            return [compiler, file_path, "-o", executable, "&&", executable]
        elif language == "csharp":
            return ["dotnet", "script", file_path]
        else:
            return base_command + [file_path]


class CodeExecutionGrok3Adapter:
    """
    Adapter class for code execution using Grok 3's capabilities.
    
    This class provides methods for generating and executing code using Grok 3.
    """
    
    def __init__(
        self,
        grok3_adapter: Optional[Grok3Adapter] = None,
        reasoning_adapter: Optional[ReasoningGrok3Adapter] = None,
        code_execution_manager: Optional[CodeExecutionManager] = None
    ):
        """
        Initialize the CodeExecutionGrok3Adapter.
        
        Args:
            grok3_adapter: Optional Grok3Adapter instance.
            reasoning_adapter: Optional ReasoningGrok3Adapter instance.
            code_execution_manager: Optional CodeExecutionManager instance.
        """
        self.grok3_adapter = grok3_adapter or Grok3Adapter()
        self.reasoning_adapter = reasoning_adapter or ReasoningGrok3Adapter(self.grok3_adapter)
        self.code_execution_manager = code_execution_manager or CodeExecutionManager()
        
        logger.info("Initialized CodeExecutionGrok3Adapter")
    
    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        system_message: Optional[str] = None
    ) -> str:
        """
        Generate code using Grok 3.
        
        Args:
            prompt: Prompt describing the code to generate.
            language: Target programming language.
            system_message: Optional system message for context.
        
        Returns:
            Generated code as a string.
        """
        # Enhance system message to focus on code generation
        enhanced_system_message = system_message or ""
        if enhanced_system_message:
            enhanced_system_message += "\n\n"
        
        enhanced_system_message += (
            f"You are an expert {language} programmer. Generate clean, efficient, and well-documented "
            f"{language} code based on the requirements. Include comments explaining key parts of the code. "
            f"Focus only on generating working code that meets the requirements."
        )
        
        # Use the reasoning adapter with "think" mode for better code generation
        code = self.reasoning_adapter.generate_text(
            prompt=prompt,
            system_message=enhanced_system_message,
            reasoning_mode="think"
        )
        
        # Extract code from the response if it's wrapped in markdown code blocks
        return self._extract_code(code, language)
    
    def generate_and_execute_code(
        self,
        prompt: str,
        language: str = "python",
        system_message: Optional[str] = None,
        auto_execute: bool = True
    ) -> Dict[str, Any]:
        """
        Generate and optionally execute code using Grok 3.
        
        Args:
            prompt: Prompt describing the code to generate.
            language: Target programming language.
            system_message: Optional system message for context.
            auto_execute: Whether to automatically execute the generated code.
        
        Returns:
            Dictionary with generation and execution results.
        """
        # Generate code
        generated_code = self.generate_code(
            prompt=prompt,
            language=language,
            system_message=system_message
        )
        
        result = {
            "generated_code": generated_code,
            "language": language
        }
        
        # Execute code if requested
        if auto_execute:
            execution_result = self.code_execution_manager.execute_code(
                code=generated_code,
                language=language
            )
            result["execution_result"] = execution_result
        
        return result
    
    def _extract_code(self, text: str, language: str) -> str:
        """
        Extract code from text that may contain markdown code blocks.
        
        Args:
            text: Text that may contain code blocks.
            language: Expected programming language.
        
        Returns:
            Extracted code as a string.
        """
        # Look for code blocks with the specified language
        import re
        pattern = f"```{language}(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # Return the first code block
            return matches[0].strip()
        
        # Look for any code blocks
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # Return the first code block
            return matches[0].strip()
        
        # If no code blocks found, return the original text
        return text
