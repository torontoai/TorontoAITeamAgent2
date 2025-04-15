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

"""Milvus Vector Database Implementation for TORONTO AI Team Agent.

This module provides a Milvus implementation of the vector database interface."""

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

class MilvusVectorDB(VectorDBInterface):
    """Milvus implementation of the vector database interface.
    
    This implementation uses Milvus as the backend for vector storage and retrieval."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Milvus vector database.
        
        Args:
            config: Configuration settings"""
        self.config = config
        
        # Import pymilvus here to avoid dependency issues if not installed
        try:
            from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
        except ImportError:
            logger.error("Milvus is not installed. Please install it with 'pip install pymilvus'.")
            raise
        
        # Store required imports for later use
        self._pymilvus_imports = {
            'connections': connections,
            'utility': utility,
            'Collection': Collection,
            'FieldSchema': FieldSchema,
            'CollectionSchema': CollectionSchema,
            'DataType': DataType
        }
        
        # Get configuration settings
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', '19530')
        self.user = config.get('user', '')
        self.password = config.get('password', '')
        self.dimension = config.get('dimension', 1536)  # Default to OpenAI embedding dimension
        self.index_type = config.get('index_type', 'IVF_FLAT')
        self.metric_type = config.get('metric_type', 'COSINE')
        self.index_params = config.get('index_params', {"nlist": 1024})
        self.search_params = config.get('search_params', {"nprobe": 16})
        
        # Connect to Milvus
        connections = self._pymilvus_imports['connections']
        connections.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            alias="default"
        )
        
        logger.info(f"Initialized Milvus vector database with host: {self.host}, port: {self.port}")
    
    def create_collection(self, collection_name: str) -> bool:
        """Create a new collection in the vector database.
        
        Args:
            collection_name: Name of the collection to create
            
        Returns:
            True if successful, False otherwise"""
        try:
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            FieldSchema = self._pymilvus_imports['FieldSchema']
            CollectionSchema = self._pymilvus_imports['CollectionSchema']
            Collection = self._pymilvus_imports['Collection']
            DataType = self._pymilvus_imports['DataType']
            
            # Check if collection already exists
            if utility.has_collection(collection_name):
                logger.warning(f"Collection already exists: {collection_name}")
                return False
            
            # Define fields
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="metadata", dtype=DataType.JSON),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
            ]
            
            # Define schema
            schema = CollectionSchema(fields=fields, description=f"Collection for {collection_name}")
            
            # Create collection
            collection = Collection(name=collection_name, schema=schema)
            
            # Create index
            collection.create_index(
                field_name="embedding",
                index_params={
                    "index_type": self.index_type,
                    "metric_type": self.metric_type,
                    "params": self.index_params
                }
            )
            
            # Load collection
            collection.load()
            
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            
            # Check if collection exists
            if not utility.has_collection(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return False
            
            # Drop collection
            utility.drop_collection(collection_name)
            
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            
            # List collections
            return utility.list_collections()
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            
            # Check if collection exists
            return utility.has_collection(collection_name)
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            Collection = self._pymilvus_imports['Collection']
            
            # Check if collection exists
            if not utility.has_collection(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                self.create_collection(collection_name)
            
            # Get collection
            collection = Collection(name=collection_name)
            
            # Prepare data
            ids = []
            texts = []
            metadatas = []
            embeddings = []
            document_ids = []
            
            for document in documents:
                # Skip documents without embeddings
                if document.embedding is None:
                    logger.warning(f"Document has no embedding, skipping")
                    continue
                
                # Generate ID if not provided
                doc_id = document.id or str(uuid.uuid4())
                document_ids.append(doc_id)
                
                # Add data
                ids.append(doc_id)
                texts.append(document.text)
                metadatas.append(json.dumps(document.metadata))
                embeddings.append(document.embedding)
            
            # Insert data
            if ids:
                collection.insert([ids, texts, metadatas, embeddings])
                
                # Flush to ensure data is persisted
                collection.flush()
            
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            Collection = self._pymilvus_imports['Collection']
            
            # Check if collection exists
            if not utility.has_collection(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return None
            
            # Get collection
            collection = Collection(name=collection_name)
            
            # Query document
            results = collection.query(
                expr=f'id == "{document_id}"',
                output_fields=["id", "text", "metadata", "embedding"]
            )
            
            # Check if document exists
            if not results:
                return None
            
            # Get document data
            result = results[0]
            
            # Parse metadata
            metadata = json.loads(result["metadata"]) if result["metadata"] else {}
            
            # Create document
            return Document(
                id=result["id"],
                text=result["text"],
                embedding=result["embedding"],
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            Collection = self._pymilvus_imports['Collection']
            
            # Check if collection exists
            if not utility.has_collection(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return False
            
            # Get collection
            collection = Collection(name=collection_name)
            
            # Delete document
            collection.delete(f'id == "{document_id}"')
            
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            Collection = self._pymilvus_imports['Collection']
            
            # Check if collection exists
            if not utility.has_collection(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return []
            
            # Get collection
            collection = Collection(name=collection_name)
            
            # Milvus doesn't support text search directly, so we need to use attribute filtering
            # This is a simplified implementation that searches for the query string in the text field
            
            # Prepare expression
            expr = f'text like "%{query}%"'
            
            # Add filters if provided
            if params.filters:
                for key, value in params.filters.items():
                    if isinstance(value, str):
                        expr += f' && metadata."{key}" == "{value}"'
                    elif isinstance(value, (int, float, bool)):
                        expr += f' && metadata."{key}" == {value}'
            
            # Query documents
            results = collection.query(
                expr=expr,
                output_fields=["id", "text", "metadata"],
                limit=params.limit + params.offset
            )
            
            # Process results
            query_results = []
            
            # Apply offset
            results = results[params.offset:params.offset + params.limit]
            
            for result in results:
                # Parse metadata
                metadata = json.loads(result["metadata"]) if result["metadata"] else {}
                
                # Calculate simple text match score
                score = self._calculate_text_score(result["text"], query)
                
                # Skip documents below minimum score
                if params.min_score is not None and score < params.min_score:
                    continue
                
                # Create document
                document = Document(
                    id=result["id"],
                    text=result["text"],
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            Collection = self._pymilvus_imports['Collection']
            
            # Check if collection exists
            if not utility.has_collection(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return []
            
            # Get collection
            collection = Collection(name=collection_name)
            
            # Prepare expression for filters
            expr = None
            if params.filters:
                expr_parts = []
                for key, value in params.filters.items():
                    if isinstance(value, str):
                        expr_parts.append(f'metadata."{key}" == "{value}"')
                    elif isinstance(value, (int, float, bool)):
                        expr_parts.append(f'metadata."{key}" == {value}')
                
                if expr_parts:
                    expr = " && ".join(expr_parts)
            
            # Search
            search_results = collection.search(
                data=[vector],
                anns_field="embedding",
                param=self.search_params,
                limit=params.limit + params.offset,
                expr=expr,
                output_fields=["id", "text", "metadata"]
            )
            
            # Process results
            query_results = []
            
            for hits in search_results:
                # Apply offset
                hits = hits[params.offset:params.offset + params.limit]
                
                for hit in hits:
                    # Parse metadata
                    metadata = json.loads(hit.entity.get("metadata", "{}"))
                    
                    # Get distance and calculate score
                    distance = hit.distance
                    
                    # Convert distance to score based on metric type
                    if self.metric_type == "COSINE":
                        # For cosine distance, score = 1 - distance
                        score = 1.0 - distance
                    elif self.metric_type == "IP":
                        # For inner product, higher is better, normalize to [0, 1]
                        # This is a simplification, proper normalization depends on data
                        score = max(0.0, min(1.0, (distance + 1.0) / 2.0))
                    elif self.metric_type == "L2":
                        # For L2 distance, lower is better, convert to [0, 1]
                        # This is a simplification, proper normalization depends on data
                        score = max(0.0, 1.0 - min(1.0, distance / 10.0))
                    else:
                        # Default fallback
                        score = 1.0 - min(1.0, distance)
                    
                    # Skip documents below minimum score or above maximum distance
                    if params.min_score is not None and score < params.min_score:
                        continue
                    if params.max_distance is not None and distance > params.max_distance:
                        continue
                    
                    # Create document
                    document = Document(
                        id=hit.entity.get("id"),
                        text=hit.entity.get("text", ""),
                        embedding=None,  # Don't include embeddings in results
                        metadata=metadata
                    )
                    
                    # Create query result
                    query_results.append(QueryResult(
                        document=document,
                        score=score,
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
            # Milvus doesn't natively support hybrid search, so we implement it manually
            
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            Collection = self._pymilvus_imports['Collection']
            
            # Check if collection exists
            if not utility.has_collection(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return 0
            
            # Get collection
            collection = Collection(name=collection_name)
            
            # Get count
            return collection.num_entities
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
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            Collection = self._pymilvus_imports['Collection']
            
            # Check if collection exists
            if not utility.has_collection(collection_name):
                logger.warning(f"Collection does not exist: {collection_name}")
                return {}
            
            # Get collection
            collection = Collection(name=collection_name)
            
            # Get count
            count = collection.num_entities
            
            return {
                "document_count": count,
                "collection_name": collection_name,
                "database_type": "milvus",
                "dimension": self.dimension,
                "index_type": self.index_type,
                "metric_type": self.metric_type
            }
        except Exception as e:
            logger.error(f"Error getting stats for collection {collection_name}: {str(e)}")
            return {}
    
    def clear(self) -> bool:
        """Clear all data from the vector database.
        
        Returns:
            True if successful, False otherwise"""
        try:
            # Get pymilvus imports
            utility = self._pymilvus_imports['utility']
            
            # Get all collections
            collections = utility.list_collections()
            
            # Delete each collection
            for collection_name in collections:
                self.delete_collection(collection_name)
            
            logger.info("Cleared all collections from Milvus vector database")
            return True
        except Exception as e:
            logger.error(f"Error clearing Milvus vector database: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the connection to the vector database."""
        try:
            # Get pymilvus imports
            connections = self._pymilvus_imports['connections']
            
            # Disconnect
            connections.disconnect("default")
            
            logger.info("Closed Milvus vector database")
        except Exception as e:
            logger.error(f"Error closing Milvus vector database: {str(e)}")
    
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
