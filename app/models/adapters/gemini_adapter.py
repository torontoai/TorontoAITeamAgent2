"""
Gemini Adapter for TORONTO AI TEAM AGENT

This module provides adapter classes for integrating Google's Gemini models
with the TORONTO AI TEAM AGENT system, enabling advanced reasoning capabilities
and multimodal understanding.

Features:
- Unified interface for working with Gemini models
- Support for different reasoning modes
- Automatic reasoning mode selection based on task complexity
- Multimodal capabilities for processing text and images
- Integration with the agent architecture
"""

import logging
import re
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from enum import Enum

# Import provider
from ..providers.gemini_provider import (
    GeminiProvider, 
    GeminiModel, 
    GeminiReasoningMode,
    GeminiMessage,
    GeminiImage,
    GeminiError
)

# Set up logging
logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Complexity levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class GeminiAdapter:
    """
    Adapter for Google's Gemini models.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: GeminiModel = GeminiModel.GEMINI_PRO,
                 auto_select_reasoning: bool = True):
        """
        Initialize the Gemini adapter.
        
        Args:
            api_key: Google API key (if None, will try to load from environment)
            model: Gemini model to use
            auto_select_reasoning: Whether to automatically select reasoning mode based on task complexity
        """
        self.provider = GeminiProvider(api_key=api_key, model=model)
        self.auto_select_reasoning = auto_select_reasoning
        self.conversation_history: List[GeminiMessage] = []
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 1000,
                         temperature: float = 0.7,
                         reasoning_mode: Optional[GeminiReasoningMode] = None,
                         maintain_history: bool = True) -> str:
        """
        Generate a response using Gemini.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            reasoning_mode: Optional reasoning mode to use
            maintain_history: Whether to maintain conversation history
            
        Returns:
            Generated response
        """
        # Add user message to history
        user_message = GeminiMessage(role="user", content=prompt)
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
                reasoning_mode=reasoning_mode
            )
        else:
            response = self.provider.generate_text(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                reasoning_mode=reasoning_mode
            )
        
        # Add assistant message to history
        if maintain_history:
            assistant_message = GeminiMessage(role="model", content=response)
            self.conversation_history.append(assistant_message)
        
        return response
    
    def generate_multimodal_response(self,
                                    prompt: str,
                                    images: List[GeminiImage],
                                    max_tokens: int = 1000,
                                    temperature: float = 0.7,
                                    reasoning_mode: Optional[GeminiReasoningMode] = None) -> str:
        """
        Generate a response using Gemini with text and images.
        
        Args:
            prompt: User prompt
            images: List of images
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            reasoning_mode: Optional reasoning mode to use
            
        Returns:
            Generated response
        """
        # Ensure we're using a vision model
        current_model = self.provider.model
        if current_model == GeminiModel.GEMINI_PRO:
            self.provider.set_model(GeminiModel.GEMINI_PRO_VISION)
        elif current_model == GeminiModel.GEMINI_ULTRA:
            self.provider.set_model(GeminiModel.GEMINI_ULTRA_VISION)
        
        # Auto-select reasoning mode if enabled and not explicitly provided
        if self.auto_select_reasoning and reasoning_mode is None:
            task_complexity = self._analyze_task_complexity(prompt)
            reasoning_mode = self._select_reasoning_mode(task_complexity)
            logger.info(f"Auto-selected reasoning mode: {reasoning_mode.value} for complexity: {task_complexity.value}")
        
        # Generate response
        response = self.provider.generate_multimodal(
            prompt,
            images,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_mode=reasoning_mode
        )
        
        # Restore original model
        self.provider.set_model(current_model)
        
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
    
    def _select_reasoning_mode(self, complexity: TaskComplexity) -> GeminiReasoningMode:
        """
        Select an appropriate reasoning mode based on task complexity.
        
        Args:
            complexity: Task complexity level
            
        Returns:
            Selected reasoning mode
        """
        if complexity == TaskComplexity.VERY_HIGH:
            return GeminiReasoningMode.ANALYTICAL
        elif complexity == TaskComplexity.HIGH:
            return GeminiReasoningMode.BALANCED
        elif complexity == TaskComplexity.MEDIUM:
            return GeminiReasoningMode.STANDARD
        else:
            return GeminiReasoningMode.STANDARD
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    def set_model(self, model: GeminiModel) -> None:
        """
        Set the Gemini model to use.
        
        Args:
            model: Gemini model
        """
        self.provider.set_model(model)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return self.provider.get_model_info()


class GeminiAnalyticalAdapter(GeminiAdapter):
    """
    Specialized adapter for Gemini with the "analytical" reasoning mode.
    This mode is optimized for complex reasoning tasks that require
    methodical analysis and logical conclusions.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: GeminiModel = GeminiModel.GEMINI_ULTRA):
        """
        Initialize the Gemini Analytical adapter.
        
        Args:
            api_key: Google API key (if None, will try to load from environment)
            model: Gemini model to use
        """
        super().__init__(api_key=api_key, model=model, auto_select_reasoning=False)
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 2000,  # Higher default for analytical mode
                         temperature: float = 0.5,  # Lower temperature for more focused thinking
                         maintain_history: bool = True) -> str:
        """
        Generate a response using Gemini with analytical reasoning mode.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            maintain_history: Whether to maintain conversation history
            
        Returns:
            Generated response
        """
        # Always use ANALYTICAL reasoning mode
        return super().generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_mode=GeminiReasoningMode.ANALYTICAL,
            maintain_history=maintain_history
        )


class GeminiCreativeAdapter(GeminiAdapter):
    """
    Specialized adapter for Gemini with the "creative" reasoning mode.
    This mode is optimized for creative tasks that benefit from
    novel perspectives and unconventional thinking.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: GeminiModel = GeminiModel.GEMINI_PRO):
        """
        Initialize the Gemini Creative adapter.
        
        Args:
            api_key: Google API key (if None, will try to load from environment)
            model: Gemini model to use
        """
        super().__init__(api_key=api_key, model=model, auto_select_reasoning=False)
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 1500,
                         temperature: float = 0.9,  # Higher temperature for more creativity
                         maintain_history: bool = True) -> str:
        """
        Generate a response using Gemini with creative reasoning mode.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            maintain_history: Whether to maintain conversation history
            
        Returns:
            Generated response
        """
        # Always use CREATIVE reasoning mode
        return super().generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_mode=GeminiReasoningMode.CREATIVE,
            maintain_history=maintain_history
        )


class GeminiBalancedAdapter(GeminiAdapter):
    """
    Specialized adapter for Gemini with the "balanced" reasoning mode.
    This mode combines analytical reasoning with creative thinking
    for well-rounded responses.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: GeminiModel = GeminiModel.GEMINI_PRO):
        """
        Initialize the Gemini Balanced adapter.
        
        Args:
            api_key: Google API key (if None, will try to load from environment)
            model: Gemini model to use
        """
        super().__init__(api_key=api_key, model=model, auto_select_reasoning=False)
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 1000,
                         temperature: float = 0.7,  # Balanced temperature
                         maintain_history: bool = True) -> str:
        """
        Generate a response using Gemini with balanced reasoning mode.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            maintain_history: Whether to maintain conversation history
            
        Returns:
            Generated response
        """
        # Always use BALANCED reasoning mode
        return super().generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_mode=GeminiReasoningMode.BALANCED,
            maintain_history=maintain_history
        )


class GeminiMultimodalAdapter(GeminiAdapter):
    """
    Specialized adapter for Gemini with multimodal capabilities.
    This adapter is optimized for tasks that involve both text and images.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[GeminiModel] = None):
        """
        Initialize the Gemini Multimodal adapter.
        
        Args:
            api_key: Google API key (if None, will try to load from environment)
            model: Gemini model to use (defaults to GEMINI_PRO_VISION)
        """
        # Default to vision model if not specified
        if model is None:
            model = GeminiModel.GEMINI_PRO_VISION
        elif model == GeminiModel.GEMINI_PRO:
            model = GeminiModel.GEMINI_PRO_VISION
        elif model == GeminiModel.GEMINI_ULTRA:
            model = GeminiModel.GEMINI_ULTRA_VISION
        
        super().__init__(api_key=api_key, model=model, auto_select_reasoning=True)
    
    def analyze_image(self, 
                     image: GeminiImage, 
                     prompt: str = "Describe this image in detail",
                     max_tokens: int = 1000) -> str:
        """
        Analyze an image using Gemini.
        
        Args:
            image: Image to analyze
            prompt: Prompt for image analysis
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated analysis
        """
        return self.generate_multimodal_response(
            prompt=prompt,
            images=[image],
            max_tokens=max_tokens,
            temperature=0.7
        )
    
    def analyze_multiple_images(self,
                              images: List[GeminiImage],
                              prompt: str = "Compare and analyze these images",
                              max_tokens: int = 1500) -> str:
        """
        Analyze multiple images using Gemini.
        
        Args:
            images: List of images to analyze
            prompt: Prompt for image analysis
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated analysis
        """
        return self.generate_multimodal_response(
            prompt=prompt,
            images=images,
            max_tokens=max_tokens,
            temperature=0.7
        )


class GeminiAdapterFactory:
    """
    Factory for creating Gemini adapters based on task requirements.
    """
    
    @staticmethod
    def create_adapter(adapter_type: str, api_key: Optional[str] = None, model: Optional[GeminiModel] = None) -> GeminiAdapter:
        """
        Create a Gemini adapter of the specified type.
        
        Args:
            adapter_type: Type of adapter to create ("standard", "analytical", "creative", "balanced", "multimodal", or "auto")
            api_key: Google API key (if None, will try to load from environment)
            model: Gemini model to use
            
        Returns:
            Gemini adapter instance
        """
        adapter_type = adapter_type.lower()
        
        # Set default model if not specified
        if model is None:
            if adapter_type == "multimodal":
                model = GeminiModel.GEMINI_PRO_VISION
            else:
                model = GeminiModel.GEMINI_PRO
        
        if adapter_type == "analytical":
            return GeminiAnalyticalAdapter(api_key=api_key, model=model)
        elif adapter_type == "creative":
            return GeminiCreativeAdapter(api_key=api_key, model=model)
        elif adapter_type == "balanced":
            return GeminiBalancedAdapter(api_key=api_key, model=model)
        elif adapter_type == "multimodal":
            return GeminiMultimodalAdapter(api_key=api_key, model=model)
        elif adapter_type == "auto":
            return GeminiAdapter(api_key=api_key, model=model, auto_select_reasoning=True)
        else:  # standard
            return GeminiAdapter(api_key=api_key, model=model, auto_select_reasoning=False)
    
    @staticmethod
    def create_adapter_for_task(task_description: str, api_key: Optional[str] = None, model: Optional[GeminiModel] = None) -> Tuple[GeminiAdapter, str]:
        """
        Create an appropriate Gemini adapter based on task description.
        
        Args:
            task_description: Description of the task
            api_key: Google API key (if None, will try to load from environment)
            model: Gemini model to use
            
        Returns:
            Tuple of (Gemini adapter instance, reasoning mode used)
        """
        # Set default model if not specified
        if model is None:
            model = GeminiModel.GEMINI_PRO
        
        # Check if task involves images
        has_image_keywords = re.search(r'image|picture|photo|diagram|chart|graph|visual', task_description, re.IGNORECASE)
        if has_image_keywords:
            return GeminiMultimodalAdapter(api_key=api_key), "multimodal"
        
        # Create a temporary adapter to analyze the task
        temp_adapter = GeminiAdapter(api_key=api_key, model=model, auto_select_reasoning=True)
        
        # Analyze task complexity
        complexity = temp_adapter._analyze_task_complexity(task_description)
        
        # Select reasoning mode
        reasoning_mode = temp_adapter._select_reasoning_mode(complexity)
        
        # Create and return the appropriate adapter
        if reasoning_mode == GeminiReasoningMode.ANALYTICAL:
            return GeminiAnalyticalAdapter(api_key=api_key, model=model), "analytical"
        elif reasoning_mode == GeminiReasoningMode.CREATIVE:
            return GeminiCreativeAdapter(api_key=api_key, model=model), "creative"
        elif reasoning_mode == GeminiReasoningMode.BALANCED:
            return GeminiBalancedAdapter(api_key=api_key, model=model), "balanced"
        else:
            return GeminiAdapter(api_key=api_key, model=model, auto_select_reasoning=False), "standard"
"""
