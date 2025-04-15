"""
Agentic Supernet module for Multi-agent Architecture Search (MaAS).

This module provides the implementation of the Agentic Supernet concept,
which enables dynamic architecture sampling based on task requirements.
"""

from .agentic_supernet import AgenticSupernet
from .architecture_sampler import ArchitectureSampler
from .controller import SupernetController

__all__ = [
    "AgenticSupernet",
    "ArchitectureSampler",
    "SupernetController"
]
