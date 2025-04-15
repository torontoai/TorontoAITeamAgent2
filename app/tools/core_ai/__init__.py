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


"""Core AI/LLM tools initialization for TorontoAITeamAgent Team AI.

This module initializes all Core AI/LLM tools."""

from .openai import OpenAITool
from .ollama import OllamaTool
from .claude import ClaudeTool
from .deepseek import DeepSeekTool
from ..registry import registry

# Register all Core AI/LLM tools
registry.register(OpenAITool)
registry.register(OllamaTool)
registry.register(ClaudeTool)
registry.register(DeepSeekTool)

__all__ = [
    "OpenAITool",
    "OllamaTool",
    "ClaudeTool",
    "DeepSeekTool"
]
