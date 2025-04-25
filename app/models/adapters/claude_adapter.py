"""
Claude Adapter for TORONTO AI TEAM AGENT

This module provides adapter classes for integrating Anthropic's Claude 3 models
with the TORONTO AI TEAM AGENT system, enabling advanced reasoning capabilities
and large context window processing.

Features:
- Unified interface for working with Claude models
- Support for different reasoning modes
- Automatic reasoning mode selection based on task complexity
- Integration with the agent architecture
"""

import logging
import re
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from enum import Enum

# Import provider
from ..providers.claude_provider import (
    ClaudeProvider, 
    ClaudeModel, 
    ClaudeReasoningMode,
    ClaudeMessage,
    ClaudeError
)

# Set up logging
logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Complexity levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ClaudeAdapter:
    """
    Adapter for Anthropic's Claude models.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: ClaudeModel = ClaudeModel.CLAUDE_3_OPUS,
                 auto_select_reasoning: bool = True):
        """
        Initialize the Claude adapter.
        
        Args:
            api_key: Anthropic API key (if None, will try to load from environment)
            model: Claude model to use
            auto_select_reasoning: Whether to automatically select reasoning mode based on task complexity
        """
        self.provider = ClaudeProvider(api_key=api_key, model=model)
        self.auto_select_reasoning = auto_select_reasoning
        self.conversation_history: List[ClaudeMessage] = []
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 1000,
                         temperature: float = 0.7,
                         reasoning_mode: Optional[ClaudeReasoningMode] = None,
                         system_prompt: Optional[str] = None,
                         maintain_history: bool = True) -> str:
        """
        Generate a response using Claude.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            reasoning_mode: Optional reasoning mode to use
            system_prompt: Optional system prompt
            maintain_history: Whether to maintain conversation history
            
        Returns:
            Generated response
        """
        # Add user message to history
        user_message = ClaudeMessage(role="user", content=prompt)
        if maintain_history:
            self.conversation_history.append(user_message)
        
        # Auto-select reasoning mode if enabled and not explicitly provided
        if self.auto_select_reasoning and reasoning_mode is None:
            task_complexity = self._analyze_task_complexity(prompt)
            reasoning_mode = self._select_reasoning_mode(task_complexity)
            logger.info(f"Auto-selected reasoning mode: {reasoning_mode.value} for complexity: {task_complexity.value}")
        
        # Generate response
        if maintain_history:
            response = self.provider.chat_completion(
                self.conversation_history,
                max_tokens=max_tokens,
                temperature=temperature,
                reasoning_mode=reasoning_mode,
                system_prompt=system_prompt
            )
        else:
            response = self.provider.generate_text(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                reasoning_mode=reasoning_mode,
                system_prompt=system_prompt
            )
        
        # Add assistant message to history
        if maintain_history:
            assistant_message = ClaudeMessage(role="assistant", content=response)
            self.conversation_history.append(assistant_message)
        
        return response
    
    def _analyze_task_complexity(self, prompt: str) -> TaskComplexity:
        """
        Analyze the complexity of a task based on the prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            Task complexity level
        """
        # Count tokens as a basic complexity measure
        token_count = self.provider.count_tokens(prompt)
        
        # Check for complexity indicators in the prompt
        has_code = bool(re.search(r'```|def |class |function|import |#include|public class', prompt))
        has_math = bool(re.search(r'\$\$|\\\(|\\begin{equation}|\\sum|\\int|\\frac', prompt))
        has_reasoning_request = bool(re.search(r'step[- ]by[- ]step|explain|analyze|evaluate|compare|critique', prompt, re.IGNORECASE))
        has_complex_task = bool(re.search(r'complex|difficult|challenging|sophisticated|advanced', prompt, re.IGNORECASE))
        
        # Determine complexity based on indicators
        complexity_score = 0
        
        if token_count > 1000:
            complexity_score += 2
        elif token_count > 500:
            complexity_score += 1
        
        if has_code:
            complexity_score += 1
        
        if has_math:
            complexity_score += 1
        
        if has_reasoning_request:
            complexity_score += 1
        
        if has_complex_task:
            complexity_score += 1
        
        # Map score to complexity level
        if complexity_score >= 4:
            return TaskComplexity.VERY_HIGH
        elif complexity_score >= 3:
            return TaskComplexity.HIGH
        elif complexity_score >= 1:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.LOW
    
    def _select_reasoning_mode(self, complexity: TaskComplexity) -> ClaudeReasoningMode:
        """
        Select an appropriate reasoning mode based on task complexity.
        
        Args:
            complexity: Task complexity level
            
        Returns:
            Selected reasoning mode
        """
        if complexity == TaskComplexity.VERY_HIGH:
            return ClaudeReasoningMode.THINK
        elif complexity == TaskComplexity.HIGH:
            return ClaudeReasoningMode.PRECISE
        elif complexity == TaskComplexity.MEDIUM:
            return ClaudeReasoningMode.STANDARD
        else:
            return ClaudeReasoningMode.STANDARD
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    def set_model(self, model: ClaudeModel) -> None:
        """
        Set the Claude model to use.
        
        Args:
            model: Claude model
        """
        self.provider.set_model(model)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return self.provider.get_model_info()


class ClaudeThinkAdapter(ClaudeAdapter):
    """
    Specialized adapter for Claude with the "think" reasoning mode.
    This mode is optimized for complex reasoning tasks that require
    step-by-step thinking and careful analysis.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: ClaudeModel = ClaudeModel.CLAUDE_3_OPUS):
        """
        Initialize the Claude Think adapter.
        
        Args:
            api_key: Anthropic API key (if None, will try to load from environment)
            model: Claude model to use
        """
        super().__init__(api_key=api_key, model=model, auto_select_reasoning=False)
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 2000,  # Higher default for think mode
                         temperature: float = 0.5,  # Lower temperature for more focused thinking
                         system_prompt: Optional[str] = None,
                         maintain_history: bool = True) -> str:
        """
        Generate a response using Claude with think reasoning mode.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            system_prompt: Optional system prompt
            maintain_history: Whether to maintain conversation history
            
        Returns:
            Generated response
        """
        # Always use THINK reasoning mode
        return super().generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_mode=ClaudeReasoningMode.THINK,
            system_prompt=system_prompt,
            maintain_history=maintain_history
        )


class ClaudeCreativeAdapter(ClaudeAdapter):
    """
    Specialized adapter for Claude with the "creative" reasoning mode.
    This mode is optimized for creative tasks that benefit from
    novel perspectives and unconventional thinking.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: ClaudeModel = ClaudeModel.CLAUDE_3_OPUS):
        """
        Initialize the Claude Creative adapter.
        
        Args:
            api_key: Anthropic API key (if None, will try to load from environment)
            model: Claude model to use
        """
        super().__init__(api_key=api_key, model=model, auto_select_reasoning=False)
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 1500,
                         temperature: float = 0.9,  # Higher temperature for more creativity
                         system_prompt: Optional[str] = None,
                         maintain_history: bool = True) -> str:
        """
        Generate a response using Claude with creative reasoning mode.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            system_prompt: Optional system prompt
            maintain_history: Whether to maintain conversation history
            
        Returns:
            Generated response
        """
        # Always use CREATIVE reasoning mode
        return super().generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_mode=ClaudeReasoningMode.CREATIVE,
            system_prompt=system_prompt,
            maintain_history=maintain_history
        )


class ClaudePreciseAdapter(ClaudeAdapter):
    """
    Specialized adapter for Claude with the "precise" reasoning mode.
    This mode is optimized for tasks that require high accuracy,
    factual correctness, and clear communication.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: ClaudeModel = ClaudeModel.CLAUDE_3_OPUS):
        """
        Initialize the Claude Precise adapter.
        
        Args:
            api_key: Anthropic API key (if None, will try to load from environment)
            model: Claude model to use
        """
        super().__init__(api_key=api_key, model=model, auto_select_reasoning=False)
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 1000,
                         temperature: float = 0.3,  # Lower temperature for more deterministic outputs
                         system_prompt: Optional[str] = None,
                         maintain_history: bool = True) -> str:
        """
        Generate a response using Claude with precise reasoning mode.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            system_prompt: Optional system prompt
            maintain_history: Whether to maintain conversation history
            
        Returns:
            Generated response
        """
        # Always use PRECISE reasoning mode
        return super().generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_mode=ClaudeReasoningMode.PRECISE,
            system_prompt=system_prompt,
            maintain_history=maintain_history
        )


class ClaudeAdapterFactory:
    """
    Factory for creating Claude adapters based on task requirements.
    """
    
    @staticmethod
    def create_adapter(adapter_type: str, api_key: Optional[str] = None, model: ClaudeModel = ClaudeModel.CLAUDE_3_OPUS) -> ClaudeAdapter:
        """
        Create a Claude adapter of the specified type.
        
        Args:
            adapter_type: Type of adapter to create ("standard", "think", "creative", "precise", or "auto")
            api_key: Anthropic API key (if None, will try to load from environment)
            model: Claude model to use
            
        Returns:
            Claude adapter instance
        """
        adapter_type = adapter_type.lower()
        
        if adapter_type == "think":
            return ClaudeThinkAdapter(api_key=api_key, model=model)
        elif adapter_type == "creative":
            return ClaudeCreativeAdapter(api_key=api_key, model=model)
        elif adapter_type == "precise":
            return ClaudePreciseAdapter(api_key=api_key, model=model)
        elif adapter_type == "auto":
            return ClaudeAdapter(api_key=api_key, model=model, auto_select_reasoning=True)
        else:  # standard
            return ClaudeAdapter(api_key=api_key, model=model, auto_select_reasoning=False)
    
    @staticmethod
    def create_adapter_for_task(task_description: str, api_key: Optional[str] = None, model: ClaudeModel = ClaudeModel.CLAUDE_3_OPUS) -> Tuple[ClaudeAdapter, str]:
        """
        Create an appropriate Claude adapter based on task description.
        
        Args:
            task_description: Description of the task
            api_key: Anthropic API key (if None, will try to load from environment)
            model: Claude model to use
            
        Returns:
            Tuple of (Claude adapter instance, reasoning mode used)
        """
        # Create a temporary adapter to analyze the task
        temp_adapter = ClaudeAdapter(api_key=api_key, model=model, auto_select_reasoning=True)
        
        # Analyze task complexity
        complexity = temp_adapter._analyze_task_complexity(task_description)
        
        # Select reasoning mode
        reasoning_mode = temp_adapter._select_reasoning_mode(complexity)
        
        # Create and return the appropriate adapter
        if reasoning_mode == ClaudeReasoningMode.THINK:
            return ClaudeThinkAdapter(api_key=api_key, model=model), "think"
        elif reasoning_mode == ClaudeReasoningMode.CREATIVE:
            return ClaudeCreativeAdapter(api_key=api_key, model=model), "creative"
        elif reasoning_mode == ClaudeReasoningMode.PRECISE:
            return ClaudePreciseAdapter(api_key=api_key, model=model), "precise"
        else:
            return ClaudeAdapter(api_key=api_key, model=model, auto_select_reasoning=False), "standard"
