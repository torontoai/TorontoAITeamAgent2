"""
Context Extension module for TORONTO AI TEAM AGENT.

This module provides components for implementing an almost limitless context window,
enabling the agent to handle extremely large projects including code repositories,
documents, and conversations.
"""

from app.context_extension.vector_db_manager import VectorDatabaseManager
from app.context_extension.hierarchical_processor import HierarchicalProcessor
from app.context_extension.recursive_summarizer import RecursiveSummarizer
from app.context_extension.memory_manager import MemoryManager
from app.context_extension.multi_agent_context import MultiAgentContextDistributor
from app.context_extension.context_window_manager import ContextWindowManager
