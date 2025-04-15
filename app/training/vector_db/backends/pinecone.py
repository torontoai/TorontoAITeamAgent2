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

"""Pinecone Vector Database Implementation for TORONTO AI Team Agent.

This module provides a Pinecone implementation of the vector database interface."""

import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Union, Tuple
import json

from ..interface import VectorDBInterface
from ..models import Document, QueryResult, SearchParams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PineconeVectorDB(VectorDBInterface):
    """Pinecone implementation of the vector database interface.
    
    This implementation uses Pinecone as the backend for vector storage and retrieval."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Pinecone vector database.
        
        Args:
            config: Configuration settings"""
        self.config = config
        
        # Import pinecone here to avoid dependency issues if not installed
        try:
            import pinecone
        except ImportError:
            logger.error("Pinecone is not installed. Please install it with 'pip install pinecone-client'.")
            raise
        
        # Get configuration settings
        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("Pinecone API key is required")
        
        self.environment = config.get('environment')
        if not self.environment:
            raise ValueError("Pinecone environment is required")
        
        self.namespace = config.get('namespace', '')
        self.dimension = config.get('dimension', 1536)  # Default to OpenAI embedding dimension
        self.metric = config.get('metric', 'cosine')
        self.pod_type = config.get('pod_type', 'p1')
        
        # Initialize Pinecone client
        pinecone.init(api_key=self.api_key, environment=self.environment)
        
        logger.info(f"Initialized Pinecone vector database with environment: {self.environment}")
    
    def create_collection(self, collection_name: str) -> bool:
        """Create a new collection in the vector database.
        
        Args:
            collection_name: Name of the collection to create
            
        Returns:
            True if successful, False otherwise"""
        try:
            import pinecone
            
            # Check if index already exists
            if collection_name in pinecone.list_indexes():
                logger.warning(f"Collection already exists: {collection_name}")
                return False
            
            # Create index
            pinecone.create_index(
                name=collection_name,
                dimension=self.dimension,
                metric=self.metric,
                pod_type=self.pod_type
            )
            
            # Wait for index to be ready
            while not collection_name in pinecone.list_indexes():
                time.sleep(1)
            
            logger.info(f"Created collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {str(e)}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from the vector database.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if successful, False otherwise"""
        try:
            import pinecone
            
            # Check if index exists
            if collection_name not in pinecone.list_indexes():
                logger.warning(f"Collection does not exist: {collection_name}")
                return False
            
            # Delete index
            pinecone.delete_index(collection_name)
            
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {str(e)}")
            return False
    
    def list_collections(self) -> List[str]:
        """List all collections in the vector database.
        
        Returns:
            List of collection names"""
        try:
            import pinecone
            return pinecone.list_indexes()
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return []
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists in the vector database.
        
        Args:
            collection_name: Name of the collection to check
            
        Returns:
            True if the collection exists, False otherwise"""
        try:
            import pinecone
            return collection_name in pinecone.list_indexes()
        except Exception as e:
            logger.error(f"Error checking if collection {collection_name} exists: {str(e)}")
            return False
    
    def add_documents(self, collection_name: str, documents: List[Document]) -> List[str]:
        """Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to add
            
        Returns:
            List of document IDs"""
        try:
            import pinecone
            
            # Check if index exists
            if not self.collection_exists(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                self.create_collection(collection_name)
            
            # Get index
            index = pinecone.Index(collection_name)
            
            # Prepare data for Pinecone
            vectors = []
            document_ids = []
            
            for document in documents:
                # Skip documents without embeddings
                if document.embedding is None:
                    logger.warning(f"Document has no embedding, skipping")
                    continue
                
                # Generate ID if not provided
                doc_id = document.id or str(uuid.uuid4())
                document_ids.append(doc_id)
                
                # Prepare metadata
                metadata = document.metadata.copy()
                metadata['text'] = document.text
                
                # Add to vectors
                vectors.append({
                    'id': doc_id,
                    'values': document.embedding,
                    'metadata': metadata
                })
            
            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                index.upsert(vectors=batch, namespace=self.namespace)
            
            logger.info(f"Added {len(document_ids)} documents to collection: {collection_name}")
            return document_ids
        except Exception as e:
            logger.error(f"Error adding documents to collection {collection_name}: {str(e)}")
            return []
    
    def get_document(self, collection_name: str, document_id: str) -> Optional[Document]:
        """Get a document by ID.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document to retrieve
            
        Returns:
            Document if found, None otherwise"""
        try:
            import pinecone
            
            # Check if index exists
            if not self.collection_exists(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return None
            
            # Get index
            index = pinecone.Index(collection_name)
            
            # Fetch vector
            result = index.fetch(ids=[document_id], namespace=self.namespace)
            
            # Check if document exists
            if document_id not in result['vectors']:
                return None
            
            # Get vector data
            vector_data = result['vectors'][document_id]
            
            # Extract metadata and text
            metadata = vector_data['metadata'].copy() if 'metadata' in vector_data else {}
            text = metadata.pop('text', '') if 'text' in metadata else ''
            
            # Create document
            return Document(
                id=document_id,
                text=text,
                embedding=vector_data['values'] if 'values' in vector_data else None,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error getting document {document_id} from collection {collection_name}: {str(e)}")
            return None
    
    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document by ID.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise"""
        try:
            import pinecone
            
            # Check if index exists
            if not self.collection_exists(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return False
            
            # Get index
            index = pinecone.Index(collection_name)
            
            # Delete vector
            index.delete(ids=[document_id], namespace=self.namespace)
            
            logger.info(f"Deleted document {document_id} from collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id} from collection {collection_name}: {str(e)}")
            return False
    
    def search(self, collection_name: str, query: str, params: SearchParams) -> List[QueryResult]:
        """Search for documents in a collection.
        
        Args:
            collection_name: Name of the collection
            query: Query string
            params: Search parameters
            
        Returns:
            List of query results"""
        try:
            import pinecone
            
            # Check if index exists
            if not self.collection_exists(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return []
            
            # Get index
            index = pinecone.Index(collection_name)
            
            # Pinecone doesn't support text search directly, so we need to use metadata filtering
            # This is a simplified implementation that searches for the query string in the text field
            
            # Prepare filter
            filter_dict = params.filters.copy() if params.filters else {}
            
            # Execute query (metadata-only)
            results = index.query(
                vector=[0.0] * self.dimension,  # Dummy vector for metadata-only query
                top_k=params.limit + params.offset,
                namespace=self.namespace,
                filter=filter_dict,
                include_metadata=True
            )
            
            # Process results
            query_results = []
            
            # Filter results by text content
            for match in results['matches']:
                # Get metadata and text
                metadata = match['metadata'].copy() if 'metadata' in match else {}
                text = metadata.pop('text', '') if 'text' in metadata else ''
                
                # Check if text contains query
                if query.lower() in text.lower():
                    # Calculate simple text match score
                    score = self._calculate_text_score(text, query)
                    
                    # Skip documents below minimum score
                    if params.min_score is not None and score < params.min_score:
                        continue
                    
                    # Create document
                    document = Document(
                        id=match['id'],
                        text=text,
                        embedding=None,  # Don't include embeddings in results
                        metadata=metadata
                    )
                    
                    # Create query result
                    query_results.append(QueryResult(
                        document=document,
                        score=score,
                        distance=None
                    ))
            
            # Sort by score in descending order
            query_results.sort(key=lambda x: x.score, reverse=True)
            
            # Apply offset and limit
            return query_results[params.offset:params.offset + params.limit]
        except Exception as e:
            logger.error(f"Error searching collection {collection_name}: {str(e)}")
            return []
    
    def search_by_vector(self, collection_name: str, vector: List[float], params: SearchParams) -> List[QueryResult]:
        """Search for documents in a collection using a vector.
        
        Args:
            collection_name: Name of the collection
            vector: Query vector
            params: Search parameters
            
        Returns:
            List of query results"""
        try:
            import pinecone
            
            # Check if index exists
            if not self.collection_exists(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return []
            
            # Get index
            index = pinecone.Index(collection_name)
            
            # Prepare filter
            filter_dict = params.filters.copy() if params.filters else {}
            
            # Execute query
            results = index.query(
                vector=vector,
                top_k=params.limit + params.offset,
                namespace=self.namespace,
                filter=filter_dict,
                include_metadata=True,
                include_values=params.include_embeddings
            )
            
            # Process results
            query_results = []
            
            for match in results['matches']:
                # Get metadata and text
                metadata = match['metadata'].copy() if 'metadata' in match else {}
                text = metadata.pop('text', '') if 'text' in metadata else ''
                
                # Get distance and calculate score
                distance = 1.0 - match['score']  # Pinecone returns similarity, convert to distance
                score = match['score']  # Pinecone score is already a similarity measure
                
                # Skip documents below minimum score or above maximum distance
                if params.min_score is not None and score < params.min_score:
                    continue
                if params.max_distance is not None and distance > params.max_distance:
                    continue
                
                # Create document
                document = Document(
                    id=match['id'],
                    text=text,
                    embedding=match.get('values') if params.include_embeddings else None,
                    metadata=metadata
                )
                
                # Create query result
                query_results.append(QueryResult(
                    document=document,
                    score=score,
                    distance=distance
                ))
            
            # Apply offset
            return query_results[params.offset:min(params.offset + params.limit, len(query_results))]
        except Exception as e:
            logger.error(f"Error searching collection {collection_name} by vector: {str(e)}")
            return []
    
    def hybrid_search(self, collection_name: str, query: str, vector: List[float], params: SearchParams) -> List[QueryResult]:
        """Perform a hybrid search combining vector similarity and keyword matching.
        
        Args:
            collection_name: Name of the collection
            query: Query string
            vector: Query vector
            params: Search parameters
            
        Returns:
            List of query results"""
        try:
            import pinecone
            
            # Pinecone doesn't natively support hybrid search, so we implement it manually
            
            # Get vector search results
            vector_results = self.search_by_vector(collection_name, vector, params)
            
            # Process results to add text scores
            hybrid_results = []
            
            for result in vector_results:
                # Calculate text score
                text_score = self._calculate_text_score(result.document.text, query)
                
                # Calculate hybrid score
                hybrid_score = (1 - params.hybrid_alpha) * result.score + params.hybrid_alpha * text_score
                
                # Skip documents below minimum score
                if params.min_score is not None and hybrid_score < params.min_score:
                    continue
                
                # Create query result
                hybrid_results.append(QueryResult(
                    document=result.document,
                    score=hybrid_score,
                    distance=result.distance,
                    metadata={
                        "vector_score": result.score,
                        "text_score": text_score
                    }
                ))
            
            # Sort by score in descending order
            hybrid_results.sort(key=lambda x: x.score, reverse=True)
            
            # Apply limit
            return hybrid_results[:params.limit]
        except Exception as e:
            logger.error(f"Error performing hybrid search on collection {collection_name}: {str(e)}")
            return []
    
    def count_documents(self, collection_name: str) -> int:
        """Count the number of documents in a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of documents"""
        try:
            import pinecone
            
            # Check if index exists
            if not self.collection_exists(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return 0
            
            # Get index
            index = pinecone.Index(collection_name)
            
            # Get stats
            stats = index.describe_index_stats()
            
            # Get namespace count
            if self.namespace:
                return stats['namespaces'].get(self.namespace, {}).get('vector_count', 0)
            else:
                return stats['total_vector_count']
        except Exception as e:
            logger.error(f"Error counting documents in collection {collection_name}: {str(e)}")
            return 0
    
    def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary of statistics"""
        try:
            import pinecone
            
            # Check if index exists
            if not self.collection_exists(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return {}
            
            # Get index
            index = pinecone.Index(collection_name)
            
            # Get stats
            stats = index.describe_index_stats()
            
            # Format stats
            result = {
                "collection_name": collection_name,
                "database_type": "pinecone",
                "dimension": stats.get('dimension'),
                "index_fullness": stats.get('index_fullness'),
                "total_vector_count": stats.get('total_vector_count')
            }
            
            # Add namespace stats if available
            if self.namespace and self.namespace in stats.get('namespaces', {}):
                result["namespace"] = self.namespace
                result["namespace_vector_count"] = stats['namespaces'][self.namespace].get('vector_count', 0)
            
            return result
        except Exception as e:
            logger.error(f"Error getting stats for collection {collection_name}: {str(e)}")
            return {}
    
    def clear(self) -> bool:
        """Clear all data from the vector database.
        
        Returns:
            True if successful, False otherwise"""
        try:
            import pinecone
            
            # Get all indexes
            indexes = pinecone.list_indexes()
            
            # Delete each index
            for index_name in indexes:
                self.delete_collection(index_name)
            
            logger.info("Cleared all collections from Pinecone vector database")
            return True
        except Exception as e:
            logger.error(f"Error clearing Pinecone vector database: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the connection to the vector database."""
        # Pinecone doesn't require explicit connection closing
        logger.info("Closed Pinecone vector database")
    
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
