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

"""In-Memory Vector Database Implementation for TORONTO AI Team Agent.

This module provides an in-memory implementation of the vector database interface
for testing and development purposes."""

import logging
import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from collections import defaultdict

from ..interface import VectorDBInterface
from ..models import Document, QueryResult, SearchParams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InMemoryVectorDB(VectorDBInterface):
    """In-memory implementation of the vector database interface.
    
    This implementation stores all data in memory and is intended for
    testing and development purposes. It should not be used in production
    for large datasets."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the in-memory vector database.
        
        Args:
            config: Configuration settings"""
        self.config = config
        self.collections: Dict[str, Dict[str, Document]] = defaultdict(dict)
        logger.info("Initialized in-memory vector database")
    
    def create_collection(self, collection_name: str) -> bool:
        """Create a new collection in the vector database.
        
        Args:
            collection_name: Name of the collection to create
            
        Returns:
            True if successful, False otherwise"""
        if collection_name in self.collections:
            logger.warning(f"Collection already exists: {collection_name}")
            return False
        
        self.collections[collection_name] = {}
        logger.info(f"Created collection: {collection_name}")
        return True
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from the vector database.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if successful, False otherwise"""
        if collection_name not in self.collections:
            logger.warning(f"Collection does not exist: {collection_name}")
            return False
        
        del self.collections[collection_name]
        logger.info(f"Deleted collection: {collection_name}")
        return True
    
    def list_collections(self) -> List[str]:
        """List all collections in the vector database.
        
        Returns:
            List of collection names"""
        return list(self.collections.keys())
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists in the vector database.
        
        Args:
            collection_name: Name of the collection to check
            
        Returns:
            True if the collection exists, False otherwise"""
        return collection_name in self.collections
    
    def add_documents(self, collection_name: str, documents: List[Document]) -> List[str]:
        """Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to add
            
        Returns:
            List of document IDs"""
        if collection_name not in self.collections:
            logger.warning(f"Collection does not exist: {collection_name}")
            self.create_collection(collection_name)
        
        document_ids = []
        for document in documents:
            doc_id = document.id or str(uuid.uuid4())
            document.id = doc_id
            self.collections[collection_name][doc_id] = document
            document_ids.append(doc_id)
        
        logger.info(f"Added {len(documents)} documents to collection: {collection_name}")
        return document_ids
    
    def get_document(self, collection_name: str, document_id: str) -> Optional[Document]:
        """Get a document by ID.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document to retrieve
            
        Returns:
            Document if found, None otherwise"""
        if collection_name not in self.collections:
            logger.warning(f"Collection does not exist: {collection_name}")
            return None
        
        return self.collections[collection_name].get(document_id)
    
    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document by ID.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise"""
        if collection_name not in self.collections:
            logger.warning(f"Collection does not exist: {collection_name}")
            return False
        
        if document_id not in self.collections[collection_name]:
            logger.warning(f"Document does not exist: {document_id}")
            return False
        
        del self.collections[collection_name][document_id]
        logger.info(f"Deleted document {document_id} from collection: {collection_name}")
        return True
    
    def search(self, collection_name: str, query: str, params: SearchParams) -> List[QueryResult]:
        """Search for documents in a collection.
        
        Args:
            collection_name: Name of the collection
            query: Query string
            params: Search parameters
            
        Returns:
            List of query results"""
        if collection_name not in self.collections:
            logger.warning(f"Collection does not exist: {collection_name}")
            return []
        
        # Simple keyword matching for in-memory implementation
        results = []
        for doc_id, document in self.collections[collection_name].items():
            # Skip documents that don't match filters
            if not self._matches_filters(document, params.filters):
                continue
            
            # Calculate simple text match score
            score = self._calculate_text_score(document.text, query)
            
            # Skip documents below minimum score
            if params.min_score is not None and score < params.min_score:
                continue
            
            # Create a copy of the document without embeddings if not requested
            result_doc = document
            if not params.include_embeddings and document.embedding is not None:
                result_doc = Document(
                    id=document.id,
                    text=document.text,
                    embedding=None,
                    metadata=document.metadata.copy() if params.include_metadata else {}
                )
            elif not params.include_metadata:
                result_doc = Document(
                    id=document.id,
                    text=document.text,
                    embedding=document.embedding,
                    metadata={}
                )
            
            results.append(QueryResult(
                document=result_doc,
                score=score,
                distance=None
            ))
        
        # Sort by score in descending order
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Apply limit and offset
        return results[params.offset:params.offset + params.limit]
    
    def search_by_vector(self, collection_name: str, vector: List[float], params: SearchParams) -> List[QueryResult]:
        """Search for documents in a collection using a vector.
        
        Args:
            collection_name: Name of the collection
            vector: Query vector
            params: Search parameters
            
        Returns:
            List of query results"""
        if collection_name not in self.collections:
            logger.warning(f"Collection does not exist: {collection_name}")
            return []
        
        # Convert query vector to numpy array
        query_vector = np.array(vector)
        
        results = []
        for doc_id, document in self.collections[collection_name].items():
            # Skip documents without embeddings
            if document.embedding is None:
                continue
            
            # Skip documents that don't match filters
            if not self._matches_filters(document, params.filters):
                continue
            
            # Calculate cosine similarity
            doc_vector = np.array(document.embedding)
            distance = self._calculate_distance(doc_vector, query_vector)
            score = 1.0 - distance  # Convert distance to similarity score
            
            # Skip documents below minimum score or above maximum distance
            if params.min_score is not None and score < params.min_score:
                continue
            if params.max_distance is not None and distance > params.max_distance:
                continue
            
            # Create a copy of the document without embeddings if not requested
            result_doc = document
            if not params.include_embeddings and document.embedding is not None:
                result_doc = Document(
                    id=document.id,
                    text=document.text,
                    embedding=None,
                    metadata=document.metadata.copy() if params.include_metadata else {}
                )
            elif not params.include_metadata:
                result_doc = Document(
                    id=document.id,
                    text=document.text,
                    embedding=document.embedding,
                    metadata={}
                )
            
            results.append(QueryResult(
                document=result_doc,
                score=score,
                distance=distance
            ))
        
        # Sort by score in descending order
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Apply limit and offset
        return results[params.offset:params.offset + params.limit]
    
    def hybrid_search(self, collection_name: str, query: str, vector: List[float], params: SearchParams) -> List[QueryResult]:
        """Perform a hybrid search combining vector similarity and keyword matching.
        
        Args:
            collection_name: Name of the collection
            query: Query string
            vector: Query vector
            params: Search parameters
            
        Returns:
            List of query results"""
        if collection_name not in self.collections:
            logger.warning(f"Collection does not exist: {collection_name}")
            return []
        
        # Convert query vector to numpy array
        query_vector = np.array(vector)
        
        results = []
        for doc_id, document in self.collections[collection_name].items():
            # Skip documents without embeddings
            if document.embedding is None:
                continue
            
            # Skip documents that don't match filters
            if not self._matches_filters(document, params.filters):
                continue
            
            # Calculate vector similarity
            doc_vector = np.array(document.embedding)
            distance = self._calculate_distance(doc_vector, query_vector)
            vector_score = 1.0 - distance  # Convert distance to similarity score
            
            # Calculate text similarity
            text_score = self._calculate_text_score(document.text, query)
            
            # Combine scores using hybrid_alpha parameter
            score = (1 - params.hybrid_alpha) * vector_score + params.hybrid_alpha * text_score
            
            # Skip documents below minimum score or above maximum distance
            if params.min_score is not None and score < params.min_score:
                continue
            if params.max_distance is not None and distance > params.max_distance:
                continue
            
            # Create a copy of the document without embeddings if not requested
            result_doc = document
            if not params.include_embeddings and document.embedding is not None:
                result_doc = Document(
                    id=document.id,
                    text=document.text,
                    embedding=None,
                    metadata=document.metadata.copy() if params.include_metadata else {}
                )
            elif not params.include_metadata:
                result_doc = Document(
                    id=document.id,
                    text=document.text,
                    embedding=document.embedding,
                    metadata={}
                )
            
            results.append(QueryResult(
                document=result_doc,
                score=score,
                distance=distance,
                metadata={
                    "vector_score": vector_score,
                    "text_score": text_score
                }
            ))
        
        # Sort by score in descending order
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Apply limit and offset
        return results[params.offset:params.offset + params.limit]
    
    def count_documents(self, collection_name: str) -> int:
        """Count the number of documents in a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of documents"""
        if collection_name not in self.collections:
            logger.warning(f"Collection does not exist: {collection_name}")
            return 0
        
        return len(self.collections[collection_name])
    
    def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary of statistics"""
        if collection_name not in self.collections:
            logger.warning(f"Collection does not exist: {collection_name}")
            return {}
        
        return {
            "document_count": len(self.collections[collection_name]),
            "collection_name": collection_name,
            "database_type": "in_memory"
        }
    
    def clear(self) -> bool:
        """Clear all data from the vector database.
        
        Returns:
            True if successful, False otherwise"""
        self.collections.clear()
        logger.info("Cleared all collections from in-memory vector database")
        return True
    
    def close(self) -> None:
        """Close the connection to the vector database."""
        # No connection to close for in-memory database
        logger.info("Closed in-memory vector database")
    
    def _calculate_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate the cosine distance between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine distance (1 - cosine similarity)"""
        # Normalize vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)
        
        # Calculate cosine similarity
        similarity = np.dot(vec1_norm, vec2_norm)
        
        # Convert to distance (1 - similarity)
        return 1.0 - similarity
    
    def _calculate_text_score(self, text: str, query: str) -> float:
        """Calculate a simple text match score.
        
        Args:
            text: Document text
            query: Query string
            
        Returns:
            Text match score between 0 and 1"""
        # Simple implementation for demonstration purposes
        # In a real implementation, this would use more sophisticated text matching
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Split query into words
        query_words = query_lower.split()
        
        # Count matching words
        match_count = sum(1 for word in query_words if word in text_lower)
        
        # Calculate score
        if not query_words:
            return 0.0
        
        return match_count / len(query_words)
    
    def _matches_filters(self, document: Document, filters: Dict[str, Any]) -> bool:
        """Check if a document matches the specified filters.
        
        Args:
            document: Document to check
            filters: Dictionary of filters
            
        Returns:
            True if the document matches all filters, False otherwise"""
        if not filters:
            return True
        
        for key, value in filters.items():
            # Handle nested metadata keys with dot notation
            if '.' in key:
                parts = key.split('.')
                current = document.metadata
                for part in parts[:-1]:
                    if part not in current:
                        return False
                    current = current[part]
                
                if parts[-1] not in current or current[parts[-1]] != value:
                    return False
            
            # Handle top-level metadata keys
            elif key not in document.metadata or document.metadata[key] != value:
                return False
        
        return True
