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

"""Weaviate Vector Database Implementation for TORONTO AI Team Agent.

This module provides a Weaviate implementation of the vector database interface."""

import logging
import uuid
import json
from typing import Dict, List, Any, Optional, Union, Tuple

from ..interface import VectorDBInterface
from ..models import Document, QueryResult, SearchParams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeaviateVectorDB(VectorDBInterface):
    """Weaviate implementation of the vector database interface.
    
    This implementation uses Weaviate as the backend for vector storage and retrieval."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Weaviate vector database.
        
        Args:
            config: Configuration settings"""
        self.config = config
        
        # Import weaviate here to avoid dependency issues if not installed
        try:
            import weaviate
        except ImportError:
            logger.error("Weaviate is not installed. Please install it with 'pip install weaviate-client'.")
            raise
        
        # Get configuration settings
        self.url = config.get('url')
        if not self.url:
            raise ValueError("Weaviate URL is required")
        
        self.api_key = config.get('api_key')
        self.class_prefix = config.get('class_prefix', 'Toronto')
        
        # Initialize Weaviate client
        auth_config = weaviate.auth.AuthApiKey(api_key=self.api_key) if self.api_key else None
        self.client = weaviate.Client(url=self.url, auth_client_secret=auth_config)
        
        logger.info(f"Initialized Weaviate vector database with URL: {self.url}")
    
    def create_collection(self, collection_name: str) -> bool:
        """Create a new collection in the vector database.
        
        Args:
            collection_name: Name of the collection to create
            
        Returns:
            True if successful, False otherwise"""
        try:
            # Format class name for Weaviate (must start with capital letter)
            class_name = self._format_class_name(collection_name)
            
            # Check if class already exists
            if self.client.schema.exists(class_name):
                logger.warning(f"Collection already exists: {collection_name}")
                return False
            
            # Create class schema
            class_schema = {
                "class": class_name,
                "description": f"Collection for {collection_name}",
                "vectorizer": "none",  # We'll provide our own vectors
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "The text content of the document"
                    },
                    {
                        "name": "metadata",
                        "dataType": ["object"],
                        "description": "Metadata associated with the document"
                    }
                ]
            }
            
            # Create class
            self.client.schema.create_class(class_schema)
            
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            if not self.client.schema.exists(class_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return False
            
            # Delete class
            self.client.schema.delete_class(class_name)
            
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
            # Get schema
            schema = self.client.schema.get()
            
            # Extract class names
            class_names = [cls['class'] for cls in schema['classes']] if 'classes' in schema else []
            
            # Filter by prefix and convert back to collection names
            prefix_len = len(self.class_prefix)
            return [cls[prefix_len:] for cls in class_names if cls.startswith(self.class_prefix)]
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            return self.client.schema.exists(class_name)
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            if not self.client.schema.exists(class_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                self.create_collection(collection_name)
            
            # Prepare batch
            with self.client.batch as batch:
                # Configure batch
                batch.batch_size = 100
                
                # Add documents to batch
                document_ids = []
                for document in documents:
                    # Generate ID if not provided
                    doc_id = document.id or str(uuid.uuid4())
                    document_ids.append(doc_id)
                    
                    # Prepare data object
                    data_object = {
                        "text": document.text,
                        "metadata": document.metadata
                    }
                    
                    # Add to batch
                    batch.add_data_object(
                        data_object=data_object,
                        class_name=class_name,
                        uuid=doc_id,
                        vector=document.embedding
                    )
            
            logger.info(f"Added {len(documents)} documents to collection: {collection_name}")
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            if not self.client.schema.exists(class_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return None
            
            # Get object
            result = self.client.data_object.get_by_id(
                uuid=document_id,
                class_name=class_name,
                with_vector=True
            )
            
            # Check if object exists
            if not result:
                return None
            
            # Create document
            return Document(
                id=document_id,
                text=result.get('properties', {}).get('text', ''),
                embedding=result.get('vector'),
                metadata=result.get('properties', {}).get('metadata', {})
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            if not self.client.schema.exists(class_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return False
            
            # Delete object
            self.client.data_object.delete(
                uuid=document_id,
                class_name=class_name
            )
            
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            if not self.client.schema.exists(class_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return []
            
            # Prepare BM25 search
            query_builder = self.client.query.get(class_name, ["text", "metadata"])
            
            # Add filters if provided
            if params.filters:
                where_filter = self._convert_filters_to_weaviate(params.filters)
                query_builder = query_builder.with_where(where_filter)
            
            # Execute BM25 search
            result = query_builder.with_bm25(query=query, properties=["text"]) \
                                 .with_limit(params.limit + params.offset) \
                                 .do()
            
            # Process results
            query_results = []
            
            # Check if results exist
            if not result or 'data' not in result or 'Get' not in result['data'] or not result['data']['Get'].get(class_name):
                return []
            
            # Get objects
            objects = result['data']['Get'][class_name]
            
            # Apply offset
            objects = objects[params.offset:params.offset + params.limit]
            
            for obj in objects:
                # Calculate score (BM25 doesn't provide scores, so we use a simple text match score)
                score = self._calculate_text_score(obj.get('text', ''), query)
                
                # Skip documents below minimum score
                if params.min_score is not None and score < params.min_score:
                    continue
                
                # Create document
                document = Document(
                    id=obj.get('_additional', {}).get('id'),
                    text=obj.get('text', ''),
                    embedding=None,  # BM25 search doesn't return vectors
                    metadata=obj.get('metadata', {})
                )
                
                # Create query result
                query_results.append(QueryResult(
                    document=document,
                    score=score,
                    distance=None
                ))
            
            return query_results
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            if not self.client.schema.exists(class_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return []
            
            # Prepare vector search
            query_builder = self.client.query.get(class_name, ["text", "metadata"])
            
            # Add filters if provided
            if params.filters:
                where_filter = self._convert_filters_to_weaviate(params.filters)
                query_builder = query_builder.with_where(where_filter)
            
            # Add vector search parameters
            query_builder = query_builder.with_near_vector({
                "vector": vector,
                "certainty": 0.7  # Adjust based on needs
            })
            
            # Add additional fields
            query_builder = query_builder.with_additional(["id", "certainty", "distance"])
            
            # Execute vector search
            result = query_builder.with_limit(params.limit + params.offset).do()
            
            # Process results
            query_results = []
            
            # Check if results exist
            if not result or 'data' not in result or 'Get' not in result['data'] or not result['data']['Get'].get(class_name):
                return []
            
            # Get objects
            objects = result['data']['Get'][class_name]
            
            # Apply offset
            objects = objects[params.offset:params.offset + params.limit]
            
            for obj in objects:
                # Get additional data
                additional = obj.get('_additional', {})
                
                # Get certainty and convert to score and distance
                certainty = additional.get('certainty', 0.0)
                distance = 1.0 - certainty
                
                # Skip documents below minimum score or above maximum distance
                if params.min_score is not None and certainty < params.min_score:
                    continue
                if params.max_distance is not None and distance > params.max_distance:
                    continue
                
                # Create document
                document = Document(
                    id=additional.get('id'),
                    text=obj.get('text', ''),
                    embedding=None,  # Don't include embeddings in results
                    metadata=obj.get('metadata', {})
                )
                
                # Create query result
                query_results.append(QueryResult(
                    document=document,
                    score=certainty,
                    distance=distance
                ))
            
            return query_results
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            if not self.client.schema.exists(class_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return []
            
            # Prepare hybrid search
            query_builder = self.client.query.get(class_name, ["text", "metadata"])
            
            # Add filters if provided
            if params.filters:
                where_filter = self._convert_filters_to_weaviate(params.filters)
                query_builder = query_builder.with_where(where_filter)
            
            # Add hybrid search parameters
            query_builder = query_builder.with_hybrid(
                query=query,
                vector=vector,
                alpha=params.hybrid_alpha
            )
            
            # Add additional fields
            query_builder = query_builder.with_additional(["id", "score"])
            
            # Execute hybrid search
            result = query_builder.with_limit(params.limit + params.offset).do()
            
            # Process results
            query_results = []
            
            # Check if results exist
            if not result or 'data' not in result or 'Get' not in result['data'] or not result['data']['Get'].get(class_name):
                return []
            
            # Get objects
            objects = result['data']['Get'][class_name]
            
            # Apply offset
            objects = objects[params.offset:params.offset + params.limit]
            
            for obj in objects:
                # Get additional data
                additional = obj.get('_additional', {})
                
                # Get score
                score = additional.get('score', 0.0)
                
                # Skip documents below minimum score
                if params.min_score is not None and score < params.min_score:
                    continue
                
                # Create document
                document = Document(
                    id=additional.get('id'),
                    text=obj.get('text', ''),
                    embedding=None,  # Don't include embeddings in results
                    metadata=obj.get('metadata', {})
                )
                
                # Create query result
                query_results.append(QueryResult(
                    document=document,
                    score=score,
                    distance=None,
                    metadata={
                        "hybrid_score": score
                    }
                ))
            
            return query_results
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            if not self.client.schema.exists(class_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return 0
            
            # Execute aggregate query
            result = self.client.query.aggregate(class_name).with_meta_count().do()
            
            # Extract count
            if result and 'data' in result and 'Aggregate' in result['data'] and class_name in result['data']['Aggregate']:
                return result['data']['Aggregate'][class_name][0]['meta']['count']
            
            return 0
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
            # Format class name for Weaviate
            class_name = self._format_class_name(collection_name)
            
            # Check if class exists
            if not self.client.schema.exists(class_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return {}
            
            # Get count
            count = self.count_documents(collection_name)
            
            return {
                "document_count": count,
                "collection_name": collection_name,
                "database_type": "weaviate"
            }
        except Exception as e:
            logger.error(f"Error getting stats for collection {collection_name}: {str(e)}")
            return {}
    
    def clear(self) -> bool:
        """Clear all data from the vector database.
        
        Returns:
            True if successful, False otherwise"""
        try:
            # Get all collections
            collections = self.list_collections()
            
            # Delete each collection
            for collection_name in collections:
                self.delete_collection(collection_name)
            
            logger.info("Cleared all collections from Weaviate vector database")
            return True
        except Exception as e:
            logger.error(f"Error clearing Weaviate vector database: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the connection to the vector database."""
        # Weaviate doesn't require explicit connection closing
        logger.info("Closed Weaviate vector database")
    
    def _format_class_name(self, collection_name: str) -> str:
        """Format a collection name as a Weaviate class name.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Formatted class name"""
        # Weaviate class names must start with a capital letter
        return f"{self.class_prefix}{collection_name.capitalize()}"
    
    def _convert_filters_to_weaviate(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert filter dictionary to Weaviate where filter format.
        
        Args:
            filters: Filter dictionary
            
        Returns:
            Weaviate where filter"""
        # Simple implementation for basic filters
        # In a real implementation, this would handle more complex filters
        where_filter = {}
        
        for key, value in filters.items():
            if key.startswith('metadata.'):
                # Handle metadata filters
                metadata_key = key[9:]  # Remove 'metadata.' prefix
                where_filter[f"metadata.{metadata_key}"] = value
            else:
                # Handle direct property filters
                where_filter[key] = value
        
        return where_filter
    
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
