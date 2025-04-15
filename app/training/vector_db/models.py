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

"""Vector Database Models for TORONTO AI Team Agent.

This module defines the data models used by the vector database system."""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field


@dataclass
class Document:
    """Document model for vector database storage.
    
    Represents a document with text content, embedding vector, and metadata."""
    
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None


@dataclass
class QueryResult:
    """Query result model for vector database searches.
    
    Represents a search result with document, score, and distance."""
    
    document: Document
    score: float
    distance: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchParams:
    """Search parameters for vector database queries.
    
    Configures search behavior including limits, filters, and scoring."""
    
    limit: int = 10
    offset: int = 0
    filters: Dict[str, Any] = field(default_factory=dict)
    include_metadata: bool = True
    include_embeddings: bool = False
    min_score: Optional[float] = None
    max_distance: Optional[float] = None
    hybrid_alpha: float = 0.5  # Weight between vector (0) and text (1) for hybrid search
