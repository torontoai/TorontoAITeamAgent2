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


"""Agentic Coding tools initialization for TorontoAITeamAgent Team AI.

This module initializes all Agentic Coding tools."""

from .aider import AiderTool
from .cursor import CursorTool
from ..registry import registry

# Register all Agentic Coding tools
registry.register(AiderTool)
registry.register(CursorTool)

__all__ = [
    "AiderTool",
    "CursorTool"
]
