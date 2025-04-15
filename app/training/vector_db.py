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


"""Enhanced Vector Database System for TORONTO AI Team Agent.

This module provides an enhanced vector database system with support for multiple
vector database backends, hybrid search, and advanced retrieval capabilities."""

import os
import logging
import json
import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDatabaseFactory:
    """Factory for creating vector database instances based on configuration."""
    
    @staticmethod
    def create_vector_db(config: Dict[str, Any]) -> 'BaseVectorDatabase':
        """Create a vector database instance based on configuration.
        
        Args:
            config: Configuration settings
            
        Returns:
            Vector database instance"""
        db_type = config.get("vector_db_type", "in_memory").lower()
        
        if db_type == "chroma":
            return ChromaVectorDatabase(config)
        elif db_type == "pinecone":
            return PineconeVectorDatabase(config)
        elif db_type == "weaviate":
            return WeaviateVectorDatabase(config)
        elif db_type == "milvus":
            return MilvusVectorDatabase(config)
        elif db_type == "faiss":
            return FaissVectorDatabase(config)
        elif db_type == "in_memory":
            return InMemoryVectorDatabase(config)
        else:
            logger.warning(f"Unsupported vector database type: {db_type}, falling back to in-memory")
            return InMemoryVectorDatabase(config)


class BaseVectorDatabase:
    """Base class for vector database implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the vector database.
        
        Args:
            config: Configuration settings"""
        self.config = config
        self.dimension = config.get("embedding_dimension", 1536)
        self.collection_name = config.get("collection_name", "training_materials")
        self.cache_enabled = config.get("enable_cache", True)
        self.cache_size = config.get("cache_size", 100)
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Initialize metrics
        self.metrics = {
            "queries": 0,
            "insertions": 0,
            "updates": 0,
            "deletions": 0,
            "avg_query_time": 0,
            "total_query_time": 0
        }
        
        logger.info(f"Initialized {self.__class__.__name__} with dimension {self.dimension}")
    
    def add_vectors(self, vectors: List[np.ndarray], documents: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """Add vectors to the database.
        
        Args:
            vectors: List of vector embeddings
            documents: List of document metadata
            ids: Optional list of IDs
            
        Returns:
            List of IDs for the added vectors"""
        raise NotImplementedError("Subclasses must implement add_vectors")
    
    def query(self, query_vector: np.ndarray, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the database for similar vectors.
        
        Args:
            query_vector: Query vector embedding
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of query results"""
        raise NotImplementedError("Subclasses must implement query")
    
    def hybrid_query(self, query_vector: np.ndarray, query_text: str, top_k: int = 5, 
                    filter_dict: Optional[Dict[str, Any]] = None, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """Perform a hybrid search combining vector similarity and keyword matching.
        
        Args:
            query_vector: Query vector embedding
            query_text: Query text for keyword matching
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            alpha: Weight for vector similarity (1-alpha for keyword matching)
            
        Returns:
            List of hybrid query results"""
        # Default implementation falls back to vector search
        logger.warning("Hybrid search not implemented for this database, falling back to vector search")
        return self.query(query_vector, top_k, filter_dict)
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from the database.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Success status"""
        raise NotImplementedError("Subclasses must implement delete_vectors")
    
    def update_vectors(self, ids: List[str], vectors: List[np.ndarray], documents: List[Dict[str, Any]]) -> bool:
        """Update vectors in the database.
        
        Args:
            ids: List of vector IDs to update
            vectors: List of new vector embeddings
            documents: List of new document metadata
            
        Returns:
            Success status"""
        raise NotImplementedError("Subclasses must implement update_vectors")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics.
        
        Returns:
            Dictionary of metrics"""
        return self.metrics
    
    def _update_metrics(self, operation: str, query_time: Optional[float] = None):
        """Update database metrics.
        
        Args:
            operation: Operation type (query, insertion, update, deletion)
            query_time: Query execution time (for queries only)"""
        if operation == "query":
            self.metrics["queries"] += 1
            if query_time is not None:
                self.metrics["total_query_time"] += query_time
                self.metrics["avg_query_time"] = self.metrics["total_query_time"] / self.metrics["queries"]
        elif operation == "insertion":
            self.metrics["insertions"] += 1
        elif operation == "update":
            self.metrics["updates"] += 1
        elif operation == "deletion":
            self.metrics["deletions"] += 1
    
    def _check_cache(self, query_key: str) -> Optional[List[Dict[str, Any]]]:
        """Check if query result is in cache.
        
        Args:
            query_key: Cache key
            
        Returns:
            Cached result or None"""
        if not self.cache_enabled:
            return None
        
        if query_key in self.cache:
            self.cache_hits += 1
            # Move to end to mark as recently used
            result = self.cache.pop(query_key)
            self.cache[query_key] = result
            return result
        
        self.cache_misses += 1
        return None
    
    def _update_cache(self, query_key: str, result: List[Dict[str, Any]]):
        """Update cache with query result.
        
        Args:
            query_key: Cache key
            result: Query result"""
        if not self.cache_enabled:
            return
        
        # If cache is full, remove oldest item (first item)
        if len(self.cache) >= self.cache_size:
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[query_key] = result


class InMemoryVectorDatabase(BaseVectorDatabase):
    """In-memory vector database implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the in-memory vector database.
        
        Args:
            config: Configuration settings"""
        super().__init__(config)
        self.vectors = []
        self.documents = []
        self.ids = []
        
        logger.info("Initialized in-memory vector database")
    
    def add_vectors(self, vectors: List[np.ndarray], documents: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """Add vectors to the database.
        
        Args:
            vectors: List of vector embeddings
            documents: List of document metadata
            ids: Optional list of IDs
            
        Returns:
            List of IDs for the added vectors"""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        for i, (vector, document, id) in enumerate(zip(vectors, documents, ids)):
            self.vectors.append(vector)
            self.documents.append(document)
            self.ids.append(id)
            self._update_metrics("insertion")
        
        return ids
    
    def query(self, query_vector: np.ndarray, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the database for similar vectors.
        
        Args:
            query_vector: Query vector embedding
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of query results"""
        # Generate cache key
        cache_key = f"query_{hash(query_vector.tobytes())}_{top_k}_{hash(str(filter_dict))}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        if not self.vectors:
            self._update_metrics("query", 0)
            return []
        
        # Calculate cosine similarity
        similarities = []
        for i, vector in enumerate(self.vectors):
            # Apply filter if provided
            if filter_dict and not self._matches_filter(self.documents[i], filter_dict):
                continue
            
            similarity = self._cosine_similarity(query_vector, vector)
            similarities.append((similarity, i))
        
        # Sort by similarity (descending)
        similarities.sort(reverse=True)
        
        # Get top-k results
        results = []
        for similarity, i in similarities[:top_k]:
            results.append({
                "id": self.ids[i],
                "document": self.documents[i],
                "score": float(similarity)
            })
        
        query_time = time.time() - start_time
        self._update_metrics("query", query_time)
        
        # Update cache
        self._update_cache(cache_key, results)
        
        return results
    
    def hybrid_query(self, query_vector: np.ndarray, query_text: str, top_k: int = 5, 
                    filter_dict: Optional[Dict[str, Any]] = None, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """Perform a hybrid search combining vector similarity and keyword matching.
        
        Args:
            query_vector: Query vector embedding
            query_text: Query text for keyword matching
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            alpha: Weight for vector similarity (1-alpha for keyword matching)
            
        Returns:
            List of hybrid query results"""
        # Generate cache key
        cache_key = f"hybrid_{hash(query_vector.tobytes())}_{hash(query_text)}_{top_k}_{hash(str(filter_dict))}_{alpha}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        if not self.vectors:
            self._update_metrics("query", 0)
            return []
        
        # Calculate combined scores
        scores = []
        for i, vector in enumerate(self.vectors):
            # Apply filter if provided
            if filter_dict and not self._matches_filter(self.documents[i], filter_dict):
                continue
            
            # Vector similarity score
            vector_score = self._cosine_similarity(query_vector, vector)
            
            # Keyword matching score
            keyword_score = self._keyword_match_score(query_text, self.documents[i])
            
            # Combined score
            combined_score = alpha * vector_score + (1 - alpha) * keyword_score
            
            scores.append((combined_score, i))
        
        # Sort by combined score (descending)
        scores.sort(reverse=True)
        
        # Get top-k results
        results = []
        for score, i in scores[:top_k]:
            results.append({
                "id": self.ids[i],
                "document": self.documents[i],
                "score": float(score),
                "vector_score": float(self._cosine_similarity(query_vector, self.vectors[i])),
                "keyword_score": float(self._keyword_match_score(query_text, self.documents[i]))
            })
        
        query_time = time.time() - start_time
        self._update_metrics("query", query_time)
        
        # Update cache
        self._update_cache(cache_key, results)
        
        return results
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from the database.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Success status"""
        deleted_count = 0
        for id in ids:
            try:
                index = self.ids.index(id)
                self.vectors.pop(index)
                self.documents.pop(index)
                self.ids.pop(index)
                deleted_count += 1
                self._update_metrics("deletion")
            except ValueError:
                logger.warning(f"Vector ID not found: {id}")
        
        # Clear cache after deletion
        if deleted_count > 0 and self.cache_enabled:
            self.cache = {}
        
        return deleted_count == len(ids)
    
    def update_vectors(self, ids: List[str], vectors: List[np.ndarray], documents: List[Dict[str, Any]]) -> bool:
        """Update vectors in the database.
        
        Args:
            ids: List of vector IDs to update
            vectors: List of new vector embeddings
            documents: List of new document metadata
            
        Returns:
            Success status"""
        updated_count = 0
        for id, vector, document in zip(ids, vectors, documents):
            try:
                index = self.ids.index(id)
                self.vectors[index] = vector
                self.documents[index] = document
                updated_count += 1
                self._update_metrics("update")
            except ValueError:
                logger.warning(f"Vector ID not found: {id}")
        
        # Clear cache after update
        if updated_count > 0 and self.cache_enabled:
            self.cache = {}
        
        return updated_count == len(ids)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Cosine similarity"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def _keyword_match_score(self, query_text: str, document: Dict[str, Any]) -> float:
        """Calculate keyword matching score.
        
        Args:
            query_text: Query text
            document: Document metadata
            
        Returns:
            Keyword matching score"""
        # Simple keyword matching implementation
        query_terms = set(query_text.lower().split())
        
        # Extract text from document
        doc_text = ""
        if "content" in document:
            doc_text += document["content"].lower() + " "
        if "title" in document:
            doc_text += document["title"].lower() + " "
        if "description" in document:
            doc_text += document["description"].lower() + " "
        
        doc_terms = set(doc_text.split())
        
        # Calculate Jaccard similarity
        if not query_terms or not doc_terms:
            return 0.0
        
        intersection = len(query_terms.intersection(doc_terms))
        union = len(query_terms.union(doc_terms))
        
        return intersection / union
    
    def _matches_filter(self, document: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if document matches filter criteria.
        
        Args:
            document: Document metadata
            filter_dict: Filter criteria
            
        Returns:
            True if document matches filter, False otherwise"""
        for key, value in filter_dict.items():
            if key not in document:
                return False
            
            if isinstance(value, list):
                if document[key] not in value:
                    return False
            else:
                if document[key] != value:
                    return False
        
        return True


class ChromaVectorDatabase(BaseVectorDatabase):
    """ChromaDB vector database implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the ChromaDB vector database.
        
        Args:
            config: Configuration settings"""
        super().__init__(config)
        
        self.db_path = config.get("vector_db_path", "./vector_db")
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create directory if it doesn't exist
            os.makedirs(self.db_path, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "TORONTO AI Team Agent training materials"}
            )
            
            logger.info(f"Initialized ChromaDB at {self.db_path}")
            self.initialized = True
            
        except ImportError:
            logger.error("ChromaDB not installed. Please install with: pip install chromadb")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            self.initialized = False
    
    def add_vectors(self, vectors: List[np.ndarray], documents: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """Add vectors to the database.
        
        Args:
            vectors: List of vector embeddings
            documents: List of document metadata
            ids: Optional list of IDs
            
        Returns:
            List of IDs for the added vectors"""
        if not self.initialized:
            logger.error("ChromaDB not initialized")
            return []
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        try:
            # Extract document content and metadata
            metadatas = []
            documents_text = []
            
            for doc in documents:
                # Extract content
                content = doc.get("content", "")
                documents_text.append(content)
                
                # Extract metadata (excluding content to avoid duplication)
                metadata = {k: v for k, v in doc.items() if k != "content"}
                metadatas.append(metadata)
            
            # Convert vectors to list format
            embeddings = [vector.tolist() for vector in vectors]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents_text,
                metadatas=metadatas,
                ids=ids
            )
            
            for _ in range(len(vectors)):
                self._update_metrics("insertion")
            
            return ids
            
        except Exception as e:
            logger.error(f"Error adding vectors to ChromaDB: {str(e)}")
            return []
    
    def query(self, query_vector: np.ndarray, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the database for similar vectors.
        
        Args:
            query_vector: Query vector embedding
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of query results"""
        if not self.initialized:
            logger.error("ChromaDB not initialized")
            return []
        
        # Generate cache key
        cache_key = f"query_{hash(query_vector.tobytes())}_{top_k}_{hash(str(filter_dict))}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            # Convert query vector to list
            query_embedding = query_vector.tolist()
            
            # Prepare filter
            where = filter_dict if filter_dict else None
            
            # Query collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where
            )
            
            # Format results
            formatted_results = []
            
            if results["ids"] and results["ids"][0]:
                for i, id in enumerate(results["ids"][0]):
                    document = {
                        "content": results["documents"][0][i] if results["documents"] and results["documents"][0] else ""
                    }
                    
                    # Add metadata
                    if results["metadatas"] and results["metadatas"][0]:
                        document.update(results["metadatas"][0][i])
                    
                    formatted_results.append({
                        "id": id,
                        "document": document,
                        "score": float(results["distances"][0][i]) if results["distances"] and results["distances"][0] else 0.0
                    })
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def hybrid_query(self, query_vector: np.ndarray, query_text: str, top_k: int = 5, 
                    filter_dict: Optional[Dict[str, Any]] = None, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """Perform a hybrid search combining vector similarity and keyword matching.
        
        Args:
            query_vector: Query vector embedding
            query_text: Query text for keyword matching
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            alpha: Weight for vector similarity (1-alpha for keyword matching)
            
        Returns:
            List of hybrid query results"""
        if not self.initialized:
            logger.error("ChromaDB not initialized")
            return []
        
        # Generate cache key
        cache_key = f"hybrid_{hash(query_vector.tobytes())}_{hash(query_text)}_{top_k}_{hash(str(filter_dict))}_{alpha}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            # Convert query vector to list
            query_embedding = query_vector.tolist()
            
            # Prepare filter
            where = filter_dict if filter_dict else None
            
            # Get more results than needed for reranking
            n_results = min(top_k * 3, 100)  # Get more results for reranking
            
            # Query collection with both vector and text
            results = self.collection.query(
                query_embeddings=[query_embedding],
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            
            # Format and rerank results
            candidates = []
            
            if results["ids"] and results["ids"][0]:
                for i, id in enumerate(results["ids"][0]):
                    document = {
                        "content": results["documents"][0][i] if results["documents"] and results["documents"][0] else ""
                    }
                    
                    # Add metadata
                    if results["metadatas"] and results["metadatas"][0]:
                        document.update(results["metadatas"][0][i])
                    
                    # Get scores
                    vector_score = float(results["distances"][0][i]) if results["distances"] and results["distances"][0] else 0.0
                    
                    # Calculate keyword score
                    keyword_score = self._keyword_match_score(query_text, document)
                    
                    # Combined score
                    combined_score = alpha * vector_score + (1 - alpha) * keyword_score
                    
                    candidates.append({
                        "id": id,
                        "document": document,
                        "score": combined_score,
                        "vector_score": vector_score,
                        "keyword_score": keyword_score
                    })
            
            # Sort by combined score (descending)
            candidates.sort(key=lambda x: x["score"], reverse=True)
            
            # Get top-k results
            formatted_results = candidates[:top_k]
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing hybrid query in ChromaDB: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from the database.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("ChromaDB not initialized")
            return False
        
        try:
            self.collection.delete(ids=ids)
            
            for _ in range(len(ids)):
                self._update_metrics("deletion")
            
            # Clear cache after deletion
            if self.cache_enabled:
                self.cache = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from ChromaDB: {str(e)}")
            return False
    
    def update_vectors(self, ids: List[str], vectors: List[np.ndarray], documents: List[Dict[str, Any]]) -> bool:
        """Update vectors in the database.
        
        Args:
            ids: List of vector IDs to update
            vectors: List of new vector embeddings
            documents: List of new document metadata
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("ChromaDB not initialized")
            return False
        
        try:
            # Delete existing vectors
            self.delete_vectors(ids)
            
            # Add new vectors
            self.add_vectors(vectors, documents, ids)
            
            for _ in range(len(ids)):
                self._update_metrics("update")
            
            # Clear cache after update
            if self.cache_enabled:
                self.cache = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating vectors in ChromaDB: {str(e)}")
            return False
    
    def _keyword_match_score(self, query_text: str, document: Dict[str, Any]) -> float:
        """Calculate keyword matching score.
        
        Args:
            query_text: Query text
            document: Document metadata
            
        Returns:
            Keyword matching score"""
        # Simple keyword matching implementation
        query_terms = set(query_text.lower().split())
        
        # Extract text from document
        doc_text = ""
        if "content" in document:
            doc_text += document["content"].lower() + " "
        if "title" in document:
            doc_text += document["title"].lower() + " "
        if "description" in document:
            doc_text += document["description"].lower() + " "
        
        doc_terms = set(doc_text.split())
        
        # Calculate Jaccard similarity
        if not query_terms or not doc_terms:
            return 0.0
        
        intersection = len(query_terms.intersection(doc_terms))
        union = len(query_terms.union(doc_terms))
        
        return intersection / union


class PineconeVectorDatabase(BaseVectorDatabase):
    """Pinecone vector database implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Pinecone vector database.
        
        Args:
            config: Configuration settings"""
        super().__init__(config)
        
        self.api_key = config.get("pinecone_api_key", "")
        self.environment = config.get("pinecone_environment", "")
        self.index_name = config.get("pinecone_index_name", self.collection_name)
        
        if not self.api_key:
            logger.error("Pinecone API key not provided")
            self.initialized = False
            return
        
        if not self.environment:
            logger.error("Pinecone environment not provided")
            self.initialized = False
            return
        
        try:
            import pinecone
            
            # Initialize Pinecone
            pinecone.init(api_key=self.api_key, environment=self.environment)
            
            # Check if index exists
            if self.index_name not in pinecone.list_indexes():
                # Create index
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine"
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            # Connect to index
            self.index = pinecone.Index(self.index_name)
            
            logger.info(f"Initialized Pinecone index: {self.index_name}")
            self.initialized = True
            
        except ImportError:
            logger.error("Pinecone not installed. Please install with: pip install pinecone-client")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {str(e)}")
            self.initialized = False
    
    def add_vectors(self, vectors: List[np.ndarray], documents: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """Add vectors to the database.
        
        Args:
            vectors: List of vector embeddings
            documents: List of document metadata
            ids: Optional list of IDs
            
        Returns:
            List of IDs for the added vectors"""
        if not self.initialized:
            logger.error("Pinecone not initialized")
            return []
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        try:
            # Prepare vectors for upsert
            items = []
            
            for i, (id, vector, document) in enumerate(zip(ids, vectors, documents)):
                # Convert vector to list
                vector_list = vector.tolist()
                
                # Prepare metadata
                metadata = {k: v for k, v in document.items() if k != "content"}
                
                # Add content with length limit
                if "content" in document:
                    content = document["content"]
                    # Pinecone has metadata size limits, so truncate if necessary
                    if len(content) > 1000:
                        content = content[:1000] + "..."
                    metadata["content"] = content
                
                items.append({
                    "id": id,
                    "values": vector_list,
                    "metadata": metadata
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(items), batch_size):
                batch = items[i:i+batch_size]
                self.index.upsert(vectors=batch)
            
            for _ in range(len(vectors)):
                self._update_metrics("insertion")
            
            return ids
            
        except Exception as e:
            logger.error(f"Error adding vectors to Pinecone: {str(e)}")
            return []
    
    def query(self, query_vector: np.ndarray, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the database for similar vectors.
        
        Args:
            query_vector: Query vector embedding
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of query results"""
        if not self.initialized:
            logger.error("Pinecone not initialized")
            return []
        
        # Generate cache key
        cache_key = f"query_{hash(query_vector.tobytes())}_{top_k}_{hash(str(filter_dict))}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            # Convert query vector to list
            query_list = query_vector.tolist()
            
            # Query index
            results = self.index.query(
                vector=query_list,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            
            for match in results["matches"]:
                document = match["metadata"]
                
                formatted_results.append({
                    "id": match["id"],
                    "document": document,
                    "score": float(match["score"])
                })
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying Pinecone: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def hybrid_query(self, query_vector: np.ndarray, query_text: str, top_k: int = 5, 
                    filter_dict: Optional[Dict[str, Any]] = None, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """Perform a hybrid search combining vector similarity and keyword matching.
        
        Args:
            query_vector: Query vector embedding
            query_text: Query text for keyword matching
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            alpha: Weight for vector similarity (1-alpha for keyword matching)
            
        Returns:
            List of hybrid query results"""
        # For Pinecone, we'll implement hybrid search by:
        # 1. Getting more results than needed from vector search
        # 2. Reranking based on keyword matching
        
        if not self.initialized:
            logger.error("Pinecone not initialized")
            return []
        
        # Generate cache key
        cache_key = f"hybrid_{hash(query_vector.tobytes())}_{hash(query_text)}_{top_k}_{hash(str(filter_dict))}_{alpha}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            # Get more results than needed for reranking
            n_results = min(top_k * 3, 100)
            
            # Convert query vector to list
            query_list = query_vector.tolist()
            
            # Query index
            results = self.index.query(
                vector=query_list,
                top_k=n_results,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Rerank results
            candidates = []
            
            for match in results["matches"]:
                document = match["metadata"]
                
                # Vector score
                vector_score = float(match["score"])
                
                # Keyword score
                keyword_score = self._keyword_match_score(query_text, document)
                
                # Combined score
                combined_score = alpha * vector_score + (1 - alpha) * keyword_score
                
                candidates.append({
                    "id": match["id"],
                    "document": document,
                    "score": combined_score,
                    "vector_score": vector_score,
                    "keyword_score": keyword_score
                })
            
            # Sort by combined score (descending)
            candidates.sort(key=lambda x: x["score"], reverse=True)
            
            # Get top-k results
            formatted_results = candidates[:top_k]
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing hybrid query in Pinecone: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from the database.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("Pinecone not initialized")
            return False
        
        try:
            self.index.delete(ids=ids)
            
            for _ in range(len(ids)):
                self._update_metrics("deletion")
            
            # Clear cache after deletion
            if self.cache_enabled:
                self.cache = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from Pinecone: {str(e)}")
            return False
    
    def update_vectors(self, ids: List[str], vectors: List[np.ndarray], documents: List[Dict[str, Any]]) -> bool:
        """Update vectors in the database.
        
        Args:
            ids: List of vector IDs to update
            vectors: List of new vector embeddings
            documents: List of new document metadata
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("Pinecone not initialized")
            return False
        
        # Pinecone upsert will automatically update existing vectors
        result = self.add_vectors(vectors, documents, ids)
        
        if len(result) == len(ids):
            for _ in range(len(ids)):
                self._update_metrics("update")
            
            # Clear cache after update
            if self.cache_enabled:
                self.cache = {}
            
            return True
        else:
            return False
    
    def _keyword_match_score(self, query_text: str, document: Dict[str, Any]) -> float:
        """Calculate keyword matching score.
        
        Args:
            query_text: Query text
            document: Document metadata
            
        Returns:
            Keyword matching score"""
        # Simple keyword matching implementation
        query_terms = set(query_text.lower().split())
        
        # Extract text from document
        doc_text = ""
        if "content" in document:
            doc_text += document["content"].lower() + " "
        if "title" in document:
            doc_text += document["title"].lower() + " "
        if "description" in document:
            doc_text += document["description"].lower() + " "
        
        doc_terms = set(doc_text.split())
        
        # Calculate Jaccard similarity
        if not query_terms or not doc_terms:
            return 0.0
        
        intersection = len(query_terms.intersection(doc_terms))
        union = len(query_terms.union(doc_terms))
        
        return intersection / union


class WeaviateVectorDatabase(BaseVectorDatabase):
    """Weaviate vector database implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Weaviate vector database.
        
        Args:
            config: Configuration settings"""
        super().__init__(config)
        
        self.url = config.get("weaviate_url", "")
        self.api_key = config.get("weaviate_api_key", "")
        self.class_name = config.get("weaviate_class_name", "TrainingMaterial")
        
        if not self.url:
            logger.error("Weaviate URL not provided")
            self.initialized = False
            return
        
        try:
            import weaviate
            from weaviate.auth import AuthApiKey
            
            # Initialize authentication
            auth_config = None
            if self.api_key:
                auth_config = AuthApiKey(api_key=self.api_key)
            
            # Initialize Weaviate client
            self.client = weaviate.Client(
                url=self.url,
                auth_client_secret=auth_config
            )
            
            # Check if class exists
            if not self.client.schema.exists(self.class_name):
                # Create class
                class_obj = {
                    "class": self.class_name,
                    "description": "TORONTO AI Team Agent training materials",
                    "vectorizer": "none",  # We'll provide our own vectors
                    "properties": [
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "Content of the training material"
                        },
                        {
                            "name": "title",
                            "dataType": ["text"],
                            "description": "Title of the training material"
                        },
                        {
                            "name": "role",
                            "dataType": ["text"],
                            "description": "Agent role"
                        },
                        {
                            "name": "section",
                            "dataType": ["text"],
                            "description": "Section of the training material"
                        },
                        {
                            "name": "source",
                            "dataType": ["text"],
                            "description": "Source of the training material"
                        }
                    ]
                }
                
                self.client.schema.create_class(class_obj)
                logger.info(f"Created Weaviate class: {self.class_name}")
            
            logger.info(f"Initialized Weaviate client for class: {self.class_name}")
            self.initialized = True
            
        except ImportError:
            logger.error("Weaviate not installed. Please install with: pip install weaviate-client")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing Weaviate: {str(e)}")
            self.initialized = False
    
    def add_vectors(self, vectors: List[np.ndarray], documents: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """Add vectors to the database.
        
        Args:
            vectors: List of vector embeddings
            documents: List of document metadata
            ids: Optional list of IDs
            
        Returns:
            List of IDs for the added vectors"""
        if not self.initialized:
            logger.error("Weaviate not initialized")
            return []
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        try:
            # Add objects in batches
            with self.client.batch as batch:
                batch.batch_size = 100
                
                for i, (id, vector, document) in enumerate(zip(ids, vectors, documents)):
                    # Convert vector to list
                    vector_list = vector.tolist()
                    
                    # Prepare properties
                    properties = {}
                    
                    # Add standard properties
                    if "content" in document:
                        properties["content"] = document["content"]
                    
                    if "title" in document:
                        properties["title"] = document["title"]
                    
                    if "role" in document:
                        properties["role"] = document["role"]
                    
                    if "section" in document:
                        properties["section"] = document["section"]
                    
                    if "source" in document:
                        properties["source"] = document["source"]
                    
                    # Add object
                    batch.add_data_object(
                        data_object=properties,
                        class_name=self.class_name,
                        uuid=id,
                        vector=vector_list
                    )
                    
                    self._update_metrics("insertion")
            
            return ids
            
        except Exception as e:
            logger.error(f"Error adding vectors to Weaviate: {str(e)}")
            return []
    
    def query(self, query_vector: np.ndarray, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the database for similar vectors.
        
        Args:
            query_vector: Query vector embedding
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of query results"""
        if not self.initialized:
            logger.error("Weaviate not initialized")
            return []
        
        # Generate cache key
        cache_key = f"query_{hash(query_vector.tobytes())}_{top_k}_{hash(str(filter_dict))}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            import weaviate.classes as wvc
            
            # Convert query vector to list
            query_list = query_vector.tolist()
            
            # Prepare query
            query = self.client.query.get(
                self.class_name,
                ["content", "title", "role", "section", "source"]
            ).with_near_vector(
                content={"vector": query_list}
            ).with_limit(top_k)
            
            # Add filter if provided
            if filter_dict:
                where_filter = {}
                
                for key, value in filter_dict.items():
                    if isinstance(value, list):
                        where_filter["operator"] = "Or"
                        where_filter["operands"] = [
                            {
                                "path": [key],
                                "operator": "Equal",
                                "valueText": v
                            } for v in value
                        ]
                    else:
                        where_filter = {
                            "path": [key],
                            "operator": "Equal",
                            "valueText": value
                        }
                
                query = query.with_where(where_filter)
            
            # Execute query
            result = query.do()
            
            # Format results
            formatted_results = []
            
            if "data" in result and "Get" in result["data"] and self.class_name in result["data"]["Get"]:
                for item in result["data"]["Get"][self.class_name]:
                    # Extract document properties
                    document = {}
                    
                    if "content" in item:
                        document["content"] = item["content"]
                    
                    if "title" in item:
                        document["title"] = item["title"]
                    
                    if "role" in item:
                        document["role"] = item["role"]
                    
                    if "section" in item:
                        document["section"] = item["section"]
                    
                    if "source" in item:
                        document["source"] = item["source"]
                    
                    # Extract ID and score
                    id = item["_additional"]["id"]
                    score = item["_additional"]["distance"]
                    
                    formatted_results.append({
                        "id": id,
                        "document": document,
                        "score": float(score)
                    })
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying Weaviate: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def hybrid_query(self, query_vector: np.ndarray, query_text: str, top_k: int = 5, 
                    filter_dict: Optional[Dict[str, Any]] = None, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """Perform a hybrid search combining vector similarity and keyword matching.
        
        Args:
            query_vector: Query vector embedding
            query_text: Query text for keyword matching
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            alpha: Weight for vector similarity (1-alpha for keyword matching)
            
        Returns:
            List of hybrid query results"""
        if not self.initialized:
            logger.error("Weaviate not initialized")
            return []
        
        # Generate cache key
        cache_key = f"hybrid_{hash(query_vector.tobytes())}_{hash(query_text)}_{top_k}_{hash(str(filter_dict))}_{alpha}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            import weaviate.classes as wvc
            
            # Convert query vector to list
            query_list = query_vector.tolist()
            
            # Prepare hybrid query
            query = self.client.query.get(
                self.class_name,
                ["content", "title", "role", "section", "source"]
            ).with_hybrid(
                query=query_text,
                vector=query_list,
                alpha=alpha
            ).with_limit(top_k)
            
            # Add filter if provided
            if filter_dict:
                where_filter = {}
                
                for key, value in filter_dict.items():
                    if isinstance(value, list):
                        where_filter["operator"] = "Or"
                        where_filter["operands"] = [
                            {
                                "path": [key],
                                "operator": "Equal",
                                "valueText": v
                            } for v in value
                        ]
                    else:
                        where_filter = {
                            "path": [key],
                            "operator": "Equal",
                            "valueText": value
                        }
                
                query = query.with_where(where_filter)
            
            # Execute query
            result = query.do()
            
            # Format results
            formatted_results = []
            
            if "data" in result and "Get" in result["data"] and self.class_name in result["data"]["Get"]:
                for item in result["data"]["Get"][self.class_name]:
                    # Extract document properties
                    document = {}
                    
                    if "content" in item:
                        document["content"] = item["content"]
                    
                    if "title" in item:
                        document["title"] = item["title"]
                    
                    if "role" in item:
                        document["role"] = item["role"]
                    
                    if "section" in item:
                        document["section"] = item["section"]
                    
                    if "source" in item:
                        document["source"] = item["source"]
                    
                    # Extract ID and score
                    id = item["_additional"]["id"]
                    score = item["_additional"]["score"]
                    
                    formatted_results.append({
                        "id": id,
                        "document": document,
                        "score": float(score)
                    })
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing hybrid query in Weaviate: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from the database.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("Weaviate not initialized")
            return False
        
        try:
            for id in ids:
                self.client.data_object.delete(
                    uuid=id,
                    class_name=self.class_name
                )
                self._update_metrics("deletion")
            
            # Clear cache after deletion
            if self.cache_enabled:
                self.cache = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from Weaviate: {str(e)}")
            return False
    
    def update_vectors(self, ids: List[str], vectors: List[np.ndarray], documents: List[Dict[str, Any]]) -> bool:
        """Update vectors in the database.
        
        Args:
            ids: List of vector IDs to update
            vectors: List of new vector embeddings
            documents: List of new document metadata
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("Weaviate not initialized")
            return False
        
        try:
            # Update objects in batches
            with self.client.batch as batch:
                batch.batch_size = 100
                
                for i, (id, vector, document) in enumerate(zip(ids, vectors, documents)):
                    # Convert vector to list
                    vector_list = vector.tolist()
                    
                    # Prepare properties
                    properties = {}
                    
                    # Add standard properties
                    if "content" in document:
                        properties["content"] = document["content"]
                    
                    if "title" in document:
                        properties["title"] = document["title"]
                    
                    if "role" in document:
                        properties["role"] = document["role"]
                    
                    if "section" in document:
                        properties["section"] = document["section"]
                    
                    if "source" in document:
                        properties["source"] = document["source"]
                    
                    # Update object
                    batch.add_data_object(
                        data_object=properties,
                        class_name=self.class_name,
                        uuid=id,
                        vector=vector_list
                    )
                    
                    self._update_metrics("update")
            
            # Clear cache after update
            if self.cache_enabled:
                self.cache = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating vectors in Weaviate: {str(e)}")
            return False


class MilvusVectorDatabase(BaseVectorDatabase):
    """Milvus vector database implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Milvus vector database.
        
        Args:
            config: Configuration settings"""
        super().__init__(config)
        
        self.host = config.get("milvus_host", "localhost")
        self.port = config.get("milvus_port", 19530)
        self.user = config.get("milvus_user", "")
        self.password = config.get("milvus_password", "")
        self.collection_name = config.get("collection_name", "training_materials")
        
        try:
            from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
            
            # Connect to Milvus
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                self.collection.load()
            else:
                # Define fields
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=255),
                    FieldSchema(name="role", dtype=DataType.VARCHAR, max_length=100),
                    FieldSchema(name="section", dtype=DataType.VARCHAR, max_length=255),
                    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255)
                ]
                
                # Define schema
                schema = CollectionSchema(fields=fields, description="TORONTO AI Team Agent training materials")
                
                # Create collection
                self.collection = Collection(name=self.collection_name, schema=schema)
                
                # Create index
                self.collection.create_index(
                    field_name="vector",
                    index_params={
                        "metric_type": "COSINE",
                        "index_type": "HNSW",
                        "params": {"M": 8, "efConstruction": 64}
                    }
                )
                
                # Load collection
                self.collection.load()
                
                logger.info(f"Created Milvus collection: {self.collection_name}")
            
            logger.info(f"Initialized Milvus collection: {self.collection_name}")
            self.initialized = True
            
        except ImportError:
            logger.error("PyMilvus not installed. Please install with: pip install pymilvus")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing Milvus: {str(e)}")
            self.initialized = False
    
    def add_vectors(self, vectors: List[np.ndarray], documents: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """Add vectors to the database.
        
        Args:
            vectors: List of vector embeddings
            documents: List of document metadata
            ids: Optional list of IDs
            
        Returns:
            List of IDs for the added vectors"""
        if not self.initialized:
            logger.error("Milvus not initialized")
            return []
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        try:
            # Prepare data
            data = {
                "id": ids,
                "vector": [vector.tolist() for vector in vectors]
            }
            
            # Add document fields
            data["content"] = [doc.get("content", "") for doc in documents]
            data["title"] = [doc.get("title", "") for doc in documents]
            data["role"] = [doc.get("role", "") for doc in documents]
            data["section"] = [doc.get("section", "") for doc in documents]
            data["source"] = [doc.get("source", "") for doc in documents]
            
            # Insert data
            self.collection.insert(data)
            
            for _ in range(len(vectors)):
                self._update_metrics("insertion")
            
            return ids
            
        except Exception as e:
            logger.error(f"Error adding vectors to Milvus: {str(e)}")
            return []
    
    def query(self, query_vector: np.ndarray, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the database for similar vectors.
        
        Args:
            query_vector: Query vector embedding
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of query results"""
        if not self.initialized:
            logger.error("Milvus not initialized")
            return []
        
        # Generate cache key
        cache_key = f"query_{hash(query_vector.tobytes())}_{top_k}_{hash(str(filter_dict))}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            # Convert query vector to list
            query_list = query_vector.tolist()
            
            # Prepare search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"ef": 64}
            }
            
            # Prepare filter expression
            expr = None
            if filter_dict:
                conditions = []
                for key, value in filter_dict.items():
                    if isinstance(value, list):
                        sub_conditions = [f"{key} == '{v}'" for v in value]
                        conditions.append(f"({' || '.join(sub_conditions)})")
                    else:
                        conditions.append(f"{key} == '{value}'")
                
                if conditions:
                    expr = " && ".join(conditions)
            
            # Search
            results = self.collection.search(
                data=[query_list],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=["content", "title", "role", "section", "source"]
            )
            
            # Format results
            formatted_results = []
            
            for hits in results:
                for hit in hits:
                    document = {
                        "content": hit.entity.get("content", ""),
                        "title": hit.entity.get("title", ""),
                        "role": hit.entity.get("role", ""),
                        "section": hit.entity.get("section", ""),
                        "source": hit.entity.get("source", "")
                    }
                    
                    formatted_results.append({
                        "id": hit.id,
                        "document": document,
                        "score": float(hit.score)
                    })
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying Milvus: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def hybrid_query(self, query_vector: np.ndarray, query_text: str, top_k: int = 5, 
                    filter_dict: Optional[Dict[str, Any]] = None, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """Perform a hybrid search combining vector similarity and keyword matching.
        
        Args:
            query_vector: Query vector embedding
            query_text: Query text for keyword matching
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            alpha: Weight for vector similarity (1-alpha for keyword matching)
            
        Returns:
            List of hybrid query results"""
        # For Milvus, we'll implement hybrid search by:
        # 1. Getting more results than needed from vector search
        # 2. Reranking based on keyword matching
        
        if not self.initialized:
            logger.error("Milvus not initialized")
            return []
        
        # Generate cache key
        cache_key = f"hybrid_{hash(query_vector.tobytes())}_{hash(query_text)}_{top_k}_{hash(str(filter_dict))}_{alpha}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            # Get more results than needed for reranking
            n_results = min(top_k * 3, 100)
            
            # Convert query vector to list
            query_list = query_vector.tolist()
            
            # Prepare search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"ef": 64}
            }
            
            # Prepare filter expression
            expr = None
            if filter_dict:
                conditions = []
                for key, value in filter_dict.items():
                    if isinstance(value, list):
                        sub_conditions = [f"{key} == '{v}'" for v in value]
                        conditions.append(f"({' || '.join(sub_conditions)})")
                    else:
                        conditions.append(f"{key} == '{value}'")
                
                if conditions:
                    expr = " && ".join(conditions)
            
            # Search
            results = self.collection.search(
                data=[query_list],
                anns_field="vector",
                param=search_params,
                limit=n_results,
                expr=expr,
                output_fields=["content", "title", "role", "section", "source"]
            )
            
            # Rerank results
            candidates = []
            
            for hits in results:
                for hit in hits:
                    document = {
                        "content": hit.entity.get("content", ""),
                        "title": hit.entity.get("title", ""),
                        "role": hit.entity.get("role", ""),
                        "section": hit.entity.get("section", ""),
                        "source": hit.entity.get("source", "")
                    }
                    
                    # Vector score
                    vector_score = float(hit.score)
                    
                    # Keyword score
                    keyword_score = self._keyword_match_score(query_text, document)
                    
                    # Combined score
                    combined_score = alpha * vector_score + (1 - alpha) * keyword_score
                    
                    candidates.append({
                        "id": hit.id,
                        "document": document,
                        "score": combined_score,
                        "vector_score": vector_score,
                        "keyword_score": keyword_score
                    })
            
            # Sort by combined score (descending)
            candidates.sort(key=lambda x: x["score"], reverse=True)
            
            # Get top-k results
            formatted_results = candidates[:top_k]
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing hybrid query in Milvus: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from the database.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("Milvus not initialized")
            return False
        
        try:
            # Prepare expression
            expr = f"id in {ids}"
            
            # Delete
            self.collection.delete(expr)
            
            for _ in range(len(ids)):
                self._update_metrics("deletion")
            
            # Clear cache after deletion
            if self.cache_enabled:
                self.cache = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from Milvus: {str(e)}")
            return False
    
    def update_vectors(self, ids: List[str], vectors: List[np.ndarray], documents: List[Dict[str, Any]]) -> bool:
        """Update vectors in the database.
        
        Args:
            ids: List of vector IDs to update
            vectors: List of new vector embeddings
            documents: List of new document metadata
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("Milvus not initialized")
            return False
        
        try:
            # Delete existing vectors
            self.delete_vectors(ids)
            
            # Add new vectors
            self.add_vectors(vectors, documents, ids)
            
            for _ in range(len(ids)):
                self._update_metrics("update")
            
            # Clear cache after update
            if self.cache_enabled:
                self.cache = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating vectors in Milvus: {str(e)}")
            return False
    
    def _keyword_match_score(self, query_text: str, document: Dict[str, Any]) -> float:
        """Calculate keyword matching score.
        
        Args:
            query_text: Query text
            document: Document metadata
            
        Returns:
            Keyword matching score"""
        # Simple keyword matching implementation
        query_terms = set(query_text.lower().split())
        
        # Extract text from document
        doc_text = ""
        if "content" in document:
            doc_text += document["content"].lower() + " "
        if "title" in document:
            doc_text += document["title"].lower() + " "
        if "description" in document:
            doc_text += document["description"].lower() + " "
        
        doc_terms = set(doc_text.split())
        
        # Calculate Jaccard similarity
        if not query_terms or not doc_terms:
            return 0.0
        
        intersection = len(query_terms.intersection(doc_terms))
        union = len(query_terms.union(doc_terms))
        
        return intersection / union


class FaissVectorDatabase(BaseVectorDatabase):
    """FAISS vector database implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the FAISS vector database.
        
        Args:
            config: Configuration settings"""
        super().__init__(config)
        
        self.index_path = config.get("faiss_index_path", "./faiss_index")
        self.metadata_path = config.get("faiss_metadata_path", "./faiss_metadata.json")
        
        try:
            import faiss
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Check if index exists
            if os.path.exists(self.index_path):
                # Load index
                self.index = faiss.read_index(self.index_path)
                logger.info(f"Loaded FAISS index from {self.index_path}")
            else:
                # Create index
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity with normalized vectors)
                logger.info(f"Created new FAISS index with dimension {self.dimension}")
            
            # Load metadata
            self.metadata = {}
            if os.path.exists(self.metadata_path):
                try:
                    with open(self.metadata_path, "r") as f:
                        self.metadata = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading FAISS metadata: {str(e)}")
            
            # Initialize ID mapping
            self.id_to_index = {}
            self.index_to_id = {}
            
            for id, info in self.metadata.items():
                index = info.get("index")
                if index is not None:
                    self.id_to_index[id] = index
                    self.index_to_id[index] = id
            
            logger.info(f"Initialized FAISS vector database with {self.index.ntotal} vectors")
            self.initialized = True
            
        except ImportError:
            logger.error("FAISS not installed. Please install with: pip install faiss-cpu or faiss-gpu")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing FAISS: {str(e)}")
            self.initialized = False
    
    def add_vectors(self, vectors: List[np.ndarray], documents: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """Add vectors to the database.
        
        Args:
            vectors: List of vector embeddings
            documents: List of document metadata
            ids: Optional list of IDs
            
        Returns:
            List of IDs for the added vectors"""
        if not self.initialized:
            logger.error("FAISS not initialized")
            return []
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        try:
            # Convert vectors to numpy array
            vectors_array = np.array([vector for vector in vectors], dtype=np.float32)
            
            # Normalize vectors for cosine similarity
            faiss.normalize_L2(vectors_array)
            
            # Get current index size
            start_index = self.index.ntotal
            
            # Add vectors to index
            self.index.add(vectors_array)
            
            # Update metadata
            for i, (id, document) in enumerate(zip(ids, documents)):
                index = start_index + i
                self.metadata[id] = {
                    "index": index,
                    "document": document
                }
                self.id_to_index[id] = index
                self.index_to_id[index] = id
                
                self._update_metrics("insertion")
            
            # Save index and metadata
            self._save_index_and_metadata()
            
            return ids
            
        except Exception as e:
            logger.error(f"Error adding vectors to FAISS: {str(e)}")
            return []
    
    def query(self, query_vector: np.ndarray, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the database for similar vectors.
        
        Args:
            query_vector: Query vector embedding
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of query results"""
        if not self.initialized:
            logger.error("FAISS not initialized")
            return []
        
        # Generate cache key
        cache_key = f"query_{hash(query_vector.tobytes())}_{top_k}_{hash(str(filter_dict))}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            import faiss
            
            # Convert query vector to numpy array
            query_array = np.array([query_vector], dtype=np.float32)
            
            # Normalize query vector for cosine similarity
            faiss.normalize_L2(query_array)
            
            # Get more results if filtering
            actual_top_k = top_k
            if filter_dict:
                actual_top_k = min(top_k * 10, self.index.ntotal)  # Get more results for filtering
            
            # Query index
            distances, indices = self.index.search(query_array, actual_top_k)
            
            # Format results
            formatted_results = []
            
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < 0 or idx >= self.index.ntotal:
                    continue
                
                # Get ID and document
                id = self.index_to_id.get(int(idx))
                if not id or id not in self.metadata:
                    continue
                
                document = self.metadata[id].get("document", {})
                
                # Apply filter if provided
                if filter_dict and not self._matches_filter(document, filter_dict):
                    continue
                
                formatted_results.append({
                    "id": id,
                    "document": document,
                    "score": float(distance)
                })
                
                # Stop if we have enough results
                if len(formatted_results) >= top_k:
                    break
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying FAISS: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def hybrid_query(self, query_vector: np.ndarray, query_text: str, top_k: int = 5, 
                    filter_dict: Optional[Dict[str, Any]] = None, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """Perform a hybrid search combining vector similarity and keyword matching.
        
        Args:
            query_vector: Query vector embedding
            query_text: Query text for keyword matching
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            alpha: Weight for vector similarity (1-alpha for keyword matching)
            
        Returns:
            List of hybrid query results"""
        if not self.initialized:
            logger.error("FAISS not initialized")
            return []
        
        # Generate cache key
        cache_key = f"hybrid_{hash(query_vector.tobytes())}_{hash(query_text)}_{top_k}_{hash(str(filter_dict))}_{alpha}"
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        start_time = time.time()
        
        try:
            import faiss
            
            # Convert query vector to numpy array
            query_array = np.array([query_vector], dtype=np.float32)
            
            # Normalize query vector for cosine similarity
            faiss.normalize_L2(query_array)
            
            # Get more results for reranking
            n_results = min(top_k * 10, self.index.ntotal)
            
            # Query index
            distances, indices = self.index.search(query_array, n_results)
            
            # Rerank results
            candidates = []
            
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < 0 or idx >= self.index.ntotal:
                    continue
                
                # Get ID and document
                id = self.index_to_id.get(int(idx))
                if not id or id not in self.metadata:
                    continue
                
                document = self.metadata[id].get("document", {})
                
                # Apply filter if provided
                if filter_dict and not self._matches_filter(document, filter_dict):
                    continue
                
                # Vector score
                vector_score = float(distance)
                
                # Keyword score
                keyword_score = self._keyword_match_score(query_text, document)
                
                # Combined score
                combined_score = alpha * vector_score + (1 - alpha) * keyword_score
                
                candidates.append({
                    "id": id,
                    "document": document,
                    "score": combined_score,
                    "vector_score": vector_score,
                    "keyword_score": keyword_score
                })
            
            # Sort by combined score (descending)
            candidates.sort(key=lambda x: x["score"], reverse=True)
            
            # Get top-k results
            formatted_results = candidates[:top_k]
            
            query_time = time.time() - start_time
            self._update_metrics("query", query_time)
            
            # Update cache
            self._update_cache(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing hybrid query in FAISS: {str(e)}")
            self._update_metrics("query", time.time() - start_time)
            return []
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from the database.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("FAISS not initialized")
            return False
        
        try:
            import faiss
            
            # FAISS doesn't support direct deletion, so we need to rebuild the index
            # Get all vectors except the ones to delete
            keep_ids = []
            keep_vectors = []
            keep_documents = []
            
            for id, info in self.metadata.items():
                if id not in ids:
                    keep_ids.append(id)
                    
                    # Get index
                    index = info.get("index")
                    if index is None:
                        continue
                    
                    # Get vector
                    vector = np.array([self.index.reconstruct(index)], dtype=np.float32)
                    keep_vectors.append(vector[0])
                    
                    # Get document
                    document = info.get("document", {})
                    keep_documents.append(document)
            
            # Create new index
            new_index = faiss.IndexFlatIP(self.dimension)
            
            # Add vectors to new index
            if keep_vectors:
                vectors_array = np.array(keep_vectors, dtype=np.float32)
                faiss.normalize_L2(vectors_array)
                new_index.add(vectors_array)
            
            # Update index
            self.index = new_index
            
            # Update metadata
            self.metadata = {}
            self.id_to_index = {}
            self.index_to_id = {}
            
            for i, (id, document) in enumerate(zip(keep_ids, keep_documents)):
                self.metadata[id] = {
                    "index": i,
                    "document": document
                }
                self.id_to_index[id] = i
                self.index_to_id[i] = id
            
            # Save index and metadata
            self._save_index_and_metadata()
            
            for _ in range(len(ids)):
                self._update_metrics("deletion")
            
            # Clear cache after deletion
            if self.cache_enabled:
                self.cache = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from FAISS: {str(e)}")
            return False
    
    def update_vectors(self, ids: List[str], vectors: List[np.ndarray], documents: List[Dict[str, Any]]) -> bool:
        """Update vectors in the database.
        
        Args:
            ids: List of vector IDs to update
            vectors: List of new vector embeddings
            documents: List of new document metadata
            
        Returns:
            Success status"""
        if not self.initialized:
            logger.error("FAISS not initialized")
            return False
        
        try:
            # Delete existing vectors
            self.delete_vectors(ids)
            
            # Add new vectors
            self.add_vectors(vectors, documents, ids)
            
            for _ in range(len(ids)):
                self._update_metrics("update")
            
            # Clear cache after update
            if self.cache_enabled:
                self.cache = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating vectors in FAISS: {str(e)}")
            return False
    
    def _save_index_and_metadata(self):
        """Save index and metadata to disk."""
        try:
            import faiss
            
            # Save index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            with open(self.metadata_path, "w") as f:
                json.dump(self.metadata, f, indent=2)
            
            logger.info(f"Saved FAISS index to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index and metadata: {str(e)}")
    
    def _matches_filter(self, document: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if document matches filter criteria.
        
        Args:
            document: Document metadata
            filter_dict: Filter criteria
            
        Returns:
            True if document matches filter, False otherwise"""
        for key, value in filter_dict.items():
            if key not in document:
                return False
            
            if isinstance(value, list):
                if document[key] not in value:
                    return False
            else:
                if document[key] != value:
                    return False
        
        return True
    
    def _keyword_match_score(self, query_text: str, document: Dict[str, Any]) -> float:
        """Calculate keyword matching score.
        
        Args:
            query_text: Query text
            document: Document metadata
            
        Returns:
            Keyword matching score"""
        # Simple keyword matching implementation
        query_terms = set(query_text.lower().split())
        
        # Extract text from document
        doc_text = ""
        if "content" in document:
            doc_text += document["content"].lower() + " "
        if "title" in document:
            doc_text += document["title"].lower() + " "
        if "description" in document:
            doc_text += document["description"].lower() + " "
        
        doc_terms = set(doc_text.split())
        
        # Calculate Jaccard similarity
        if not query_terms or not doc_terms:
            return 0.0
        
        intersection = len(query_terms.intersection(doc_terms))
        union = len(query_terms.union(doc_terms))
        
        return intersection / union
