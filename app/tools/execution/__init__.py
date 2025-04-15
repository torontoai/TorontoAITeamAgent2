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


"""Execution/Testing tools initialization for TorontoAITeamAgent Team AI.

This module initializes all Execution/Testing tools."""

from .subprocess import SubprocessTool
from .pytest import PytestTool
from .replit import ReplitTool
from ..registry import registry

# Register all Execution/Testing tools
registry.register(SubprocessTool)
registry.register(PytestTool)
registry.register(ReplitTool)

__all__ = [
    "SubprocessTool",
    "PytestTool",
    "ReplitTool"
]
