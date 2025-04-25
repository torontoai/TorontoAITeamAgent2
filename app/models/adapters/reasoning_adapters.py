"""
Reasoning adapters module for Grok 3 API integration.

This module contains adapter classes for using Grok 3's advanced reasoning modes.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import logging

from app.models.adapters.model_adapter import Grok3Adapter

# Set up logging
logger = logging.getLogger(__name__)

class ReasoningGrok3Adapter:
    """
    Adapter class for using Grok 3's advanced reasoning capabilities.
    
    This class provides methods for leveraging Grok 3's specialized reasoning modes
    such as "think" mode for step-by-step reasoning and "big_brain" mode for
    complex tasks.
    """
    
    def __init__(
        self,
        grok3_adapter: Optional[Grok3Adapter] = None,
        default_reasoning_mode: str = "auto"
    ):
        """
        Initialize the ReasoningGrok3Adapter.
        
        Args:
            grok3_adapter: Optional Grok3Adapter instance.
            default_reasoning_mode: Default reasoning mode to use.
        """
        self.grok3_adapter = grok3_adapter or Grok3Adapter()
        self.default_reasoning_mode = default_reasoning_mode
        
        # Initialize specialized adapters
        self.think_adapter = ThinkModeAdapter(self.grok3_adapter)
        self.big_brain_adapter = BigBrainModeAdapter(self.grok3_adapter)
        
        logger.info(f"Initialized ReasoningGrok3Adapter with default mode: {default_reasoning_mode}")
    
    def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        reasoning_mode: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using the appropriate reasoning mode.
        
        Args:
            prompt: Text prompt for generation.
            system_message: Optional system message for context.
            reasoning_mode: Reasoning mode to use (auto, think, big_brain).
            **kwargs: Additional arguments to pass to the underlying adapter.
        
        Returns:
            Generated text as a string.
        """
        reasoning_mode = reasoning_mode or self.default_reasoning_mode
        
        if reasoning_mode == "think":
            return self.think_adapter.generate_text(
                prompt=prompt,
                system_message=system_message,
                **kwargs
            )
        elif reasoning_mode == "big_brain":
            return self.big_brain_adapter.generate_text(
                prompt=prompt,
                system_message=system_message,
                **kwargs
            )
        elif reasoning_mode == "auto":
            # Automatically select the appropriate reasoning mode based on the prompt
            return self._auto_select_reasoning_mode(
                prompt=prompt,
                system_message=system_message,
                **kwargs
            )
        else:
            logger.warning(f"Unknown reasoning mode: {reasoning_mode}. Using default adapter.")
            return self.grok3_adapter.generate_text(
                prompt=prompt,
                system_message=system_message,
                **kwargs
            )
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        reasoning_mode: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response in a chat conversation using the appropriate reasoning mode.
        
        Args:
            messages: List of messages in the conversation.
            reasoning_mode: Reasoning mode to use (auto, think, big_brain).
            **kwargs: Additional arguments to pass to the underlying adapter.
        
        Returns:
            Generated response as a string.
        """
        reasoning_mode = reasoning_mode or self.default_reasoning_mode
        
        if reasoning_mode == "think":
            return self.think_adapter.generate_chat_response(
                messages=messages,
                **kwargs
            )
        elif reasoning_mode == "big_brain":
            return self.big_brain_adapter.generate_chat_response(
                messages=messages,
                **kwargs
            )
        elif reasoning_mode == "auto":
            # Automatically select the appropriate reasoning mode based on the messages
            return self._auto_select_reasoning_mode_for_chat(
                messages=messages,
                **kwargs
            )
        else:
            logger.warning(f"Unknown reasoning mode: {reasoning_mode}. Using default adapter.")
            return self.grok3_adapter.generate_chat_response(
                messages=messages,
                **kwargs
            )
    
    def _auto_select_reasoning_mode(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Automatically select the appropriate reasoning mode based on the prompt.
        
        Args:
            prompt: Text prompt for generation.
            system_message: Optional system message for context.
            **kwargs: Additional arguments to pass to the underlying adapter.
        
        Returns:
            Generated text as a string.
        """
        # Simple heuristic for mode selection based on prompt complexity
        # In a real implementation, this would be more sophisticated
        
        # Check for indicators of complex reasoning needs
        complex_indicators = [
            "explain step by step",
            "analyze",
            "compare and contrast",
            "solve this problem",
            "prove",
            "derive",
            "step-by-step",
            "reasoning",
            "think through"
        ]
        
        # Check for indicators of very complex tasks
        very_complex_indicators = [
            "complex",
            "advanced",
            "sophisticated",
            "in-depth analysis",
            "comprehensive review",
            "research",
            "implications",
            "synthesize",
            "evaluate the evidence"
        ]
        
        prompt_lower = prompt.lower()
        
        # Count the indicators
        complex_count = sum(1 for indicator in complex_indicators if indicator in prompt_lower)
        very_complex_count = sum(1 for indicator in very_complex_indicators if indicator in prompt_lower)
        
        # Select mode based on indicator counts and prompt length
        if very_complex_count >= 2 or len(prompt.split()) > 100:
            logger.info("Auto-selected 'big_brain' reasoning mode based on prompt complexity")
            return self.big_brain_adapter.generate_text(
                prompt=prompt,
                system_message=system_message,
                **kwargs
            )
        elif complex_count >= 2 or len(prompt.split()) > 50:
            logger.info("Auto-selected 'think' reasoning mode based on prompt complexity")
            return self.think_adapter.generate_text(
                prompt=prompt,
                system_message=system_message,
                **kwargs
            )
        else:
            logger.info("Using default adapter for simple prompt")
            return self.grok3_adapter.generate_text(
                prompt=prompt,
                system_message=system_message,
                **kwargs
            )
    
    def _auto_select_reasoning_mode_for_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Automatically select the appropriate reasoning mode based on chat messages.
        
        Args:
            messages: List of messages in the conversation.
            **kwargs: Additional arguments to pass to the underlying adapter.
        
        Returns:
            Generated response as a string.
        """
        # Extract the last user message for analysis
        last_user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                last_user_message = message.get("content", "")
                break
        
        # If we found a user message, use it to select the reasoning mode
        if last_user_message:
            # Create a temporary prompt from the last user message
            temp_prompt = last_user_message
            
            # Use the same logic as for text generation
            complex_indicators = [
                "explain step by step",
                "analyze",
                "compare and contrast",
                "solve this problem",
                "prove",
                "derive",
                "step-by-step",
                "reasoning",
                "think through"
            ]
            
            very_complex_indicators = [
                "complex",
                "advanced",
                "sophisticated",
                "in-depth analysis",
                "comprehensive review",
                "research",
                "implications",
                "synthesize",
                "evaluate the evidence"
            ]
            
            prompt_lower = temp_prompt.lower()
            
            complex_count = sum(1 for indicator in complex_indicators if indicator in prompt_lower)
            very_complex_count = sum(1 for indicator in very_complex_indicators if indicator in prompt_lower)
            
            if very_complex_count >= 2 or len(temp_prompt.split()) > 100:
                logger.info("Auto-selected 'big_brain' reasoning mode based on message complexity")
                return self.big_brain_adapter.generate_chat_response(
                    messages=messages,
                    **kwargs
                )
            elif complex_count >= 2 or len(temp_prompt.split()) > 50:
                logger.info("Auto-selected 'think' reasoning mode based on message complexity")
                return self.think_adapter.generate_chat_response(
                    messages=messages,
                    **kwargs
                )
        
        # Default case
        logger.info("Using default adapter for chat")
        return self.grok3_adapter.generate_chat_response(
            messages=messages,
            **kwargs
        )


class ThinkModeAdapter:
    """
    Adapter for using Grok 3's "think" mode for step-by-step reasoning.
    """
    
    def __init__(self, grok3_adapter: Grok3Adapter):
        """
        Initialize the ThinkModeAdapter.
        
        Args:
            grok3_adapter: Grok3Adapter instance to use.
        """
        self.grok3_adapter = grok3_adapter
        logger.info("Initialized ThinkModeAdapter")
    
    def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using Grok 3's "think" mode.
        
        Args:
            prompt: Text prompt for generation.
            system_message: Optional system message for context.
            **kwargs: Additional arguments to pass to the underlying adapter.
        
        Returns:
            Generated text as a string.
        """
        # Enhance system message to encourage step-by-step thinking
        enhanced_system_message = system_message or ""
        if enhanced_system_message:
            enhanced_system_message += "\n\n"
        
        enhanced_system_message += (
            "Please think through this step-by-step. Break down your reasoning "
            "process clearly, considering different angles and explaining your "
            "thought process as you go."
        )
        
        return self.grok3_adapter.generate_text(
            prompt=prompt,
            system_message=enhanced_system_message,
            reasoning_mode="think",
            **kwargs
        )
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate a chat response using Grok 3's "think" mode.
        
        Args:
            messages: List of messages in the conversation.
            **kwargs: Additional arguments to pass to the underlying adapter.
        
        Returns:
            Generated response as a string.
        """
        # Add or enhance system message to encourage step-by-step thinking
        has_system_message = False
        enhanced_messages = []
        
        for message in messages:
            if message.get("role") == "system":
                has_system_message = True
                content = message.get("content", "")
                if content:
                    content += "\n\n"
                
                content += (
                    "Please think through this step-by-step. Break down your reasoning "
                    "process clearly, considering different angles and explaining your "
                    "thought process as you go."
                )
                
                enhanced_messages.append({
                    "role": "system",
                    "content": content
                })
            else:
                enhanced_messages.append(message)
        
        if not has_system_message:
            enhanced_messages = [{
                "role": "system",
                "content": (
                    "Please think through this step-by-step. Break down your reasoning "
                    "process clearly, considering different angles and explaining your "
                    "thought process as you go."
                )
            }] + enhanced_messages
        
        return self.grok3_adapter.generate_chat_response(
            messages=enhanced_messages,
            reasoning_mode="think",
            **kwargs
        )


class BigBrainModeAdapter:
    """
    Adapter for using Grok 3's "big_brain" mode for complex tasks.
    """
    
    def __init__(self, grok3_adapter: Grok3Adapter):
        """
        Initialize the BigBrainModeAdapter.
        
        Args:
            grok3_adapter: Grok3Adapter instance to use.
        """
        self.grok3_adapter = grok3_adapter
        logger.info("Initialized BigBrainModeAdapter")
    
    def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using Grok 3's "big_brain" mode.
        
        Args:
            prompt: Text prompt for generation.
            system_message: Optional system message for context.
            **kwargs: Additional arguments to pass to the underlying adapter.
        
        Returns:
            Generated text as a string.
        """
        # Enhance system message to encourage comprehensive analysis
        enhanced_system_message = system_message or ""
        if enhanced_system_message:
            enhanced_system_message += "\n\n"
        
        enhanced_system_message += (
            "Please provide a comprehensive, in-depth analysis. Consider multiple perspectives, "
            "evaluate evidence thoroughly, and develop sophisticated insights. Organize your "
            "response with clear structure, and ensure your analysis is nuanced and considers "
            "the full complexity of the topic."
        )
        
        return self.grok3_adapter.generate_text(
            prompt=prompt,
            system_message=enhanced_system_message,
            reasoning_mode="big_brain",
            **kwargs
        )
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate a chat response using Grok 3's "big_brain" mode.
        
        Args:
            messages: List of messages in the conversation.
            **kwargs: Additional arguments to pass to the underlying adapter.
        
        Returns:
            Generated response as a string.
        """
        # Add or enhance system message to encourage comprehensive analysis
        has_system_message = False
        enhanced_messages = []
        
        for message in messages:
            if message.get("role") == "system":
                has_system_message = True
                content = message.get("content", "")
                if content:
                    content += "\n\n"
                
                content += (
                    "Please provide a comprehensive, in-depth analysis. Consider multiple perspectives, "
                    "evaluate evidence thoroughly, and develop sophisticated insights. Organize your "
                    "response with clear structure, and ensure your analysis is nuanced and considers "
                    "the full complexity of the topic."
                )
                
                enhanced_messages.append({
                    "role": "system",
                    "content": content
                })
            else:
                enhanced_messages.append(message)
        
        if not has_system_message:
            enhanced_messages = [{
                "role": "system",
                "content": (
                    "Please provide a comprehensive, in-depth analysis. Consider multiple perspectives, "
                    "evaluate evidence thoroughly, and develop sophisticated insights. Organize your "
                    "response with clear structure, and ensure your analysis is nuanced and considers "
                    "the full complexity of the topic."
                )
            }] + enhanced_messages
        
        return self.grok3_adapter.generate_chat_response(
            messages=enhanced_messages,
            reasoning_mode="big_brain",
            **kwargs
        )
