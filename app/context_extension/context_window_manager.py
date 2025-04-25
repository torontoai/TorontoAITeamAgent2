"""
Context Window Manager for context extension.

This module provides the Context Window Manager, which integrates all components
of the context extension system to provide an almost limitless context window.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple

from app.context_extension.vector_db_manager import VectorDatabaseManager
from app.context_extension.hierarchical_processor import HierarchicalProcessor
from app.context_extension.recursive_summarizer import RecursiveSummarizer
from app.context_extension.memory_manager import MemoryManager
from app.context_extension.multi_agent_context import MultiAgentContextDistributor

# Set up logging
logger = logging.getLogger(__name__)

class ContextWindowManager:
    """
    Manager class for integrating all context extension components.
    
    This class provides a unified interface for using the context extension system,
    enabling an almost limitless context window for the TORONTO AI TEAM AGENT.
    """
    
    def __init__(
        self,
        vector_db_config: Optional[Dict[str, Any]] = None,
        hierarchical_processor_config: Optional[Dict[str, Any]] = None,
        recursive_summarizer_config: Optional[Dict[str, Any]] = None,
        memory_manager_config: Optional[Dict[str, Any]] = None,
        multi_agent_config: Optional[Dict[str, Any]] = None,
        enable_all_components: bool = True
    ):
        """
        Initialize the ContextWindowManager.
        
        Args:
            vector_db_config: Configuration for the Vector Database Manager
            hierarchical_processor_config: Configuration for the Hierarchical Processor
            recursive_summarizer_config: Configuration for the Recursive Summarizer
            memory_manager_config: Configuration for the Memory Manager
            multi_agent_config: Configuration for the Multi-Agent Context Distributor
            enable_all_components: Whether to enable all components
        """
        self.enable_all_components = enable_all_components
        
        # Initialize components
        self.vector_db = self._init_vector_db(vector_db_config)
        self.hierarchical_processor = self._init_hierarchical_processor(hierarchical_processor_config)
        self.recursive_summarizer = self._init_recursive_summarizer(recursive_summarizer_config)
        self.memory_manager = self._init_memory_manager(memory_manager_config)
        self.multi_agent_distributor = self._init_multi_agent_distributor(multi_agent_config)
        
        logger.info("Initialized ContextWindowManager with all components")
    
    def _init_vector_db(self, config: Optional[Dict[str, Any]]) -> VectorDatabaseManager:
        """
        Initialize the Vector Database Manager.
        
        Args:
            config: Configuration for the Vector Database Manager
        
        Returns:
            Initialized Vector Database Manager
        """
        if config is None:
            config = {}
        
        return VectorDatabaseManager(**config)
    
    def _init_hierarchical_processor(self, config: Optional[Dict[str, Any]]) -> HierarchicalProcessor:
        """
        Initialize the Hierarchical Processor.
        
        Args:
            config: Configuration for the Hierarchical Processor
        
        Returns:
            Initialized Hierarchical Processor
        """
        if config is None:
            config = {}
        
        return HierarchicalProcessor(**config)
    
    def _init_recursive_summarizer(self, config: Optional[Dict[str, Any]]) -> RecursiveSummarizer:
        """
        Initialize the Recursive Summarizer.
        
        Args:
            config: Configuration for the Recursive Summarizer
        
        Returns:
            Initialized Recursive Summarizer
        """
        if config is None:
            config = {}
        
        return RecursiveSummarizer(**config)
    
    def _init_memory_manager(self, config: Optional[Dict[str, Any]]) -> MemoryManager:
        """
        Initialize the Memory Manager.
        
        Args:
            config: Configuration for the Memory Manager
        
        Returns:
            Initialized Memory Manager
        """
        if config is None:
            config = {}
        
        return MemoryManager(**config)
    
    def _init_multi_agent_distributor(self, config: Optional[Dict[str, Any]]) -> MultiAgentContextDistributor:
        """
        Initialize the Multi-Agent Context Distributor.
        
        Args:
            config: Configuration for the Multi-Agent Context Distributor
        
        Returns:
            Initialized Multi-Agent Context Distributor
        """
        if config is None:
            config = {}
        
        return MultiAgentContextDistributor(**config)
    
    def process_document(
        self,
        document: str,
        document_id: Optional[str] = None,
        document_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a document through the context extension system.
        
        Args:
            document: Document to process
            document_id: Optional document ID
            document_type: Optional document type
            metadata: Optional metadata
        
        Returns:
            Processing result with document ID and status
        """
        result = {
            "status": "success",
            "document_id": document_id,
            "components": {}
        }
        
        try:
            # Detect document type if not provided
            if document_type is None:
                document_type = self._detect_document_type(document)
            
            # Process with Hierarchical Processor
            hierarchical_chunks = self.hierarchical_processor.process_document(document, document_type)
            result["components"]["hierarchical_processor"] = {
                "status": "success",
                "chunks": len(hierarchical_chunks["chunks"]),
                "hierarchy_levels": len(set(node["level"] for node in hierarchical_chunks["hierarchy"]))
            }
            
            # Generate recursive summary
            summary_result = self.recursive_summarizer.get_hierarchical_summary(document)
            result["components"]["recursive_summarizer"] = {
                "status": "success",
                "summary_levels": summary_result["level"] + 1,
                "compression_ratio": summary_result["compression_ratio"]
            }
            
            # Store in Vector Database
            if metadata is None:
                metadata = {}
            
            metadata["document_type"] = document_type
            metadata["hierarchical"] = True
            metadata["summary_available"] = True
            
            chunk_ids = self.vector_db.store_document(document, metadata, document_id)
            result["components"]["vector_db"] = {
                "status": "success",
                "chunk_ids": len(chunk_ids)
            }
            
            # Store in Memory Manager
            memory_item = {
                "type": "document",
                "content": summary_result["summary"],
                "document_id": document_id,
                "document_type": document_type,
                "metadata": metadata
            }
            
            memory_id = self.memory_manager.add_to_long_term_memory(memory_item)
            result["components"]["memory_manager"] = {
                "status": "success",
                "memory_id": memory_id
            }
            
            # Distribute to agents if multi-agent is enabled
            if self.enable_all_components:
                agent_assignments = self.multi_agent_distributor.distribute_context(document, document_type)
                result["components"]["multi_agent_distributor"] = {
                    "status": "success",
                    "agent_count": len(agent_assignments)
                }
            
            # Set document ID in result
            if document_id is None:
                import uuid
                document_id = str(uuid.uuid4())
            
            result["document_id"] = document_id
            
            logger.info(f"Successfully processed document {document_id}")
        
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def retrieve_context(
        self,
        query: str,
        context_type: str = "combined",
        max_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve context based on a query.
        
        Args:
            query: Query to search for
            context_type: Type of context to retrieve (vector, memory, hierarchical, summary, combined)
            max_results: Maximum number of results to return
            filter_metadata: Optional metadata filter
        
        Returns:
            Retrieved context with metadata
        """
        result = {
            "status": "success",
            "query": query,
            "context_type": context_type,
            "context": "",
            "sources": []
        }
        
        try:
            if context_type == "vector" or context_type == "combined":
                # Retrieve from Vector Database
                vector_results = self.vector_db.retrieve_relevant_context(query, max_results, filter_metadata)
                
                if vector_results:
                    result["sources"].append({
                        "type": "vector",
                        "count": len(vector_results)
                    })
                    
                    if context_type == "vector":
                        result["context"] = "\n\n".join(item["text"] for item in vector_results)
            
            if context_type == "memory" or context_type == "combined":
                # Retrieve from Memory Manager
                memory_results = self.memory_manager.search_memory(query, max_results=max_results)
                
                if memory_results:
                    result["sources"].append({
                        "type": "memory",
                        "count": len(memory_results)
                    })
                    
                    if context_type == "memory":
                        result["context"] = "\n\n".join(item["item"].get("content", "") for item in memory_results)
            
            if context_type == "combined":
                # Combine results from all sources
                combined_context = []
                
                # Add vector results
                for item in vector_results[:max_results // 2]:
                    combined_context.append(item["text"])
                
                # Add memory results
                for item in memory_results[:max_results // 2]:
                    if "content" in item["item"]:
                        combined_context.append(item["item"]["content"])
                
                result["context"] = "\n\n".join(combined_context)
            
            logger.info(f"Successfully retrieved context for query: {query}")
        
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def get_sliding_context_window(
        self,
        query: str,
        window_size: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get a sliding context window based on a query.
        
        Args:
            query: Query to search for
            window_size: Number of chunks to include in the window
            filter_metadata: Optional metadata filter
        
        Returns:
            Concatenated text of the sliding context window
        """
        return self.vector_db.get_sliding_context_window(query, window_size, filter_metadata)
    
    def drill_down_context(
        self,
        query: str,
        document_id: str
    ) -> Dict[str, Any]:
        """
        Drill down into context based on a query.
        
        Args:
            query: Query to search for
            document_id: Document ID to drill down into
        
        Returns:
            Detailed context with hierarchy information
        """
        result = {
            "status": "success",
            "query": query,
            "document_id": document_id,
            "context": "",
            "hierarchy": []
        }
        
        try:
            # Retrieve document from Vector Database
            filter_metadata = {"document_id": document_id}
            vector_results = self.vector_db.retrieve_relevant_context(query, 1, filter_metadata)
            
            if not vector_results:
                result["status"] = "error"
                result["error"] = f"Document {document_id} not found"
                return result
            
            # Get the full document
            full_document = self.vector_db.get_sliding_context_window("", 100, filter_metadata)
            
            # Process with Hierarchical Processor
            document_type = vector_results[0]["metadata"].get("document_type", "text")
            hierarchical_chunks = self.hierarchical_processor.process_document(full_document, document_type)
            
            # Navigate hierarchy based on query
            relevant_chunks = self.hierarchical_processor.navigate_hierarchy(hierarchical_chunks, query)
            
            if relevant_chunks:
                # Extract context and hierarchy
                context_parts = []
                hierarchy = []
                
                for chunk_with_context in relevant_chunks:
                    context_parts.append(chunk_with_context["chunk"]["content"])
                    
                    # Add parent sections to hierarchy
                    for parent in chunk_with_context["context"]["parent_sections"]:
                        hierarchy.append({
                            "id": parent["id"],
                            "name": parent.get("name", parent["id"]),
                            "level": parent.get("level", 0)
                        })
                
                result["context"] = "\n\n".join(context_parts)
                result["hierarchy"] = hierarchy
            
            logger.info(f"Successfully drilled down into document {document_id} for query: {query}")
        
        except Exception as e:
            logger.error(f"Error drilling down into context: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def get_summary_at_level(
        self,
        document_id: str,
        level: int = 0
    ) -> Dict[str, Any]:
        """
        Get a summary of a document at a specific level of detail.
        
        Args:
            document_id: Document ID to summarize
            level: Level of detail (0 = most summarized)
        
        Returns:
            Summary at the specified level
        """
        result = {
            "status": "success",
            "document_id": document_id,
            "level": level,
            "summary": ""
        }
        
        try:
            # Retrieve document from Vector Database
            filter_metadata = {"document_id": document_id}
            full_document = self.vector_db.get_sliding_context_window("", 100, filter_metadata)
            
            if not full_document:
                result["status"] = "error"
                result["error"] = f"Document {document_id} not found"
                return result
            
            # Generate hierarchical summary
            hierarchical_summary = self.recursive_summarizer.get_hierarchical_summary(full_document)
            
            # Get summary at specified level
            summary = self.recursive_summarizer.get_summary_at_level(hierarchical_summary, level)
            result["summary"] = summary
            
            logger.info(f"Successfully generated level {level} summary for document {document_id}")
        
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def register_agent(
        self,
        agent_id: str,
        agent_interface: Any,
        specializations: List[str] = None,
        context_capacity: int = 10000
    ) -> bool:
        """
        Register an agent with the Multi-Agent Context Distributor.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_interface: Interface for communicating with the agent
            specializations: List of agent specializations
            context_capacity: Maximum context capacity for the agent
        
        Returns:
            True if registration was successful
        """
        return self.multi_agent_distributor.register_agent(
            agent_id, agent_interface, specializations, context_capacity
        )
    
    def start_multi_agent_processing(self) -> bool:
        """
        Start the Multi-Agent Context Distributor.
        
        Returns:
            True if started successfully
        """
        return self.multi_agent_distributor.start_processing()
    
    def stop_multi_agent_processing(self) -> bool:
        """
        Stop the Multi-Agent Context Distributor.
        
        Returns:
            True if stopped successfully
        """
        return self.multi_agent_distributor.stop_processing()
    
    def clean_up_memory(self) -> Tuple[int, int]:
        """
        Clean up old memory items.
        
        Returns:
            Tuple of (long_term_removed, episodic_removed)
        """
        return self.memory_manager.clean_up_memory()
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of the context extension system.
        
        Returns:
            Dictionary with system status information
        """
        status = {
            "vector_db": {
                "type": self.vector_db.db_provider,
                "embedding_model": self.vector_db.embedding_model
            },
            "memory_manager": self.memory_manager.get_memory_stats(),
            "multi_agent": self.multi_agent_distributor.get_system_status() if self.enable_all_components else {"enabled": False}
        }
        
        return status
    
    def _detect_document_type(self, document: str) -> str:
        """
        Detect the type of document based on content.
        
        Args:
            document: Document to analyze
        
        Returns:
            Detected document type
        """
        import re
        
        # Check for code indicators
        code_patterns = [
            r'def\s+\w+\s*\(.*\)\s*:',  # Python function
            r'function\s+\w+\s*\(.*\)\s*{',  # JavaScript function
            r'class\s+\w+\s*[({]',  # Class definition
            r'import\s+[\w.]+',  # Import statement
            r'#include\s+[<"][\w.]+[>"]',  # C/C++ include
            r'public\s+static\s+void\s+main',  # Java main method
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, document):
                return "code"
        
        # Check for markdown indicators
        markdown_patterns = [
            r'^#\s+\w+',  # Heading
            r'^\*\s+\w+',  # Unordered list
            r'^\d+\.\s+\w+',  # Ordered list
            r'\[.*\]\(.*\)',  # Link
            r'```\w*\n',  # Code block
        ]
        
        markdown_count = 0
        for pattern in markdown_patterns:
            markdown_count += len(re.findall(pattern, document, re.MULTILINE))
        
        if markdown_count > 5:  # Arbitrary threshold
            return "markdown"
        
        # Check for conversation indicators
        conversation_patterns = [
            r'(?:^|\n)(?:User|Assistant|System):\s',  # Chat format
            r'(?:^|\n)(?:[A-Za-z0-9_]+):\s',  # Name: format
            r'(?:^|\n)Q:\s.*(?:\n|$).*A:\s',  # Q&A format
        ]
        
        for pattern in conversation_patterns:
            if re.search(pattern, document, re.MULTILINE):
                return "conversation"
        
        # Default to text
        return "text"
