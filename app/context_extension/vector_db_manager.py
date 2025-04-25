"""
Vector Database Manager for context extension.

This module provides the Vector Database Integration Layer, which serves as the foundation
for persistent storage of all historical context, enabling an almost limitless context window.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)

class VectorDatabaseManager:
    """
    Manager class for integrating with vector databases to store and retrieve context.
    
    This class provides methods for storing documents, retrieving relevant context,
    and managing the sliding context window mechanism.
    """
    
    def __init__(
        self,
        db_provider: str = "chroma",
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
        collection_name: str = "toronto_agent_context",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        similarity_threshold: float = 0.75
    ):
        """
        Initialize the VectorDatabaseManager.
        
        Args:
            db_provider: Vector database provider (chroma, pinecone, etc.)
            embedding_model: Model to use for generating embeddings
            collection_name: Name of the collection to store vectors
            chunk_size: Size of chunks for document segmentation
            chunk_overlap: Overlap between chunks to maintain context
            similarity_threshold: Threshold for similarity search
        """
        self.db_provider = db_provider
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold
        
        # Initialize database and embedding model
        self.db = self._initialize_db()
        self.model = self._load_embedding_model()
        
        logger.info(f"Initialized VectorDatabaseManager with {db_provider} and {embedding_model}")
    
    def _initialize_db(self) -> Any:
        """
        Initialize the vector database based on the provider.
        
        Returns:
            Initialized database instance
        """
        try:
            if self.db_provider.lower() == "chroma":
                try:
                    import chromadb
                    client = chromadb.Client()
                    # Get or create collection
                    collection = client.get_or_create_collection(name=self.collection_name)
                    return collection
                except ImportError:
                    logger.error("ChromaDB not installed. Please install with 'pip install chromadb'")
                    raise
            
            elif self.db_provider.lower() == "pinecone":
                try:
                    import pinecone
                    # Initialize Pinecone with API key from environment
                    api_key = os.environ.get("PINECONE_API_KEY")
                    if not api_key:
                        logger.warning("PINECONE_API_KEY not found in environment variables")
                        api_key = "your-api-key"  # Placeholder, should be replaced
                    
                    pinecone.init(api_key=api_key, environment="us-west1-gcp")
                    
                    # Get or create index
                    if self.collection_name not in pinecone.list_indexes():
                        pinecone.create_index(name=self.collection_name, dimension=768)  # Default dimension for sentence-transformers
                    
                    index = pinecone.Index(self.collection_name)
                    return index
                except ImportError:
                    logger.error("Pinecone not installed. Please install with 'pip install pinecone-client'")
                    raise
            
            else:
                logger.error(f"Unsupported database provider: {self.db_provider}")
                raise ValueError(f"Unsupported database provider: {self.db_provider}")
        
        except Exception as e:
            logger.error(f"Error initializing vector database: {str(e)}")
            # Return a mock DB for development/testing
            return MockVectorDB(self.collection_name)
    
    def _load_embedding_model(self) -> Any:
        """
        Load the embedding model.
        
        Returns:
            Loaded embedding model
        """
        try:
            if "sentence-transformers" in self.embedding_model:
                try:
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer(self.embedding_model)
                    return model
                except ImportError:
                    logger.error("Sentence Transformers not installed. Please install with 'pip install sentence-transformers'")
                    raise
            
            elif "openai" in self.embedding_model.lower():
                try:
                    import openai
                    # OpenAI API key from environment
                    api_key = os.environ.get("OPENAI_API_KEY")
                    if not api_key:
                        logger.warning("OPENAI_API_KEY not found in environment variables")
                        api_key = "your-api-key"  # Placeholder, should be replaced
                    
                    openai.api_key = api_key
                    return openai
                except ImportError:
                    logger.error("OpenAI not installed. Please install with 'pip install openai'")
                    raise
            
            else:
                logger.error(f"Unsupported embedding model: {self.embedding_model}")
                raise ValueError(f"Unsupported embedding model: {self.embedding_model}")
        
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            # Return a mock model for development/testing
            return MockEmbeddingModel()
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to generate embeddings for
        
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        try:
            if isinstance(self.model, MockEmbeddingModel):
                return self.model.encode(texts)
            
            if "sentence-transformers" in self.embedding_model:
                embeddings = self.model.encode(texts)
                return embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
            
            elif "openai" in self.embedding_model.lower():
                embeddings = []
                for text in texts:
                    response = self.model.Embedding.create(
                        input=text,
                        model="text-embedding-ada-002"
                    )
                    embeddings.append(response["data"][0]["embedding"])
                return embeddings
            
            else:
                logger.error(f"Unsupported embedding model: {self.embedding_model}")
                raise ValueError(f"Unsupported embedding model: {self.embedding_model}")
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Return mock embeddings for development/testing
            return [MockEmbeddingModel().encode_single(text) for text in texts]
    
    def _semantic_chunking(self, document: str) -> List[str]:
        """
        Chunk a document semantically based on content and structure.
        
        Args:
            document: Document to chunk
        
        Returns:
            List of chunks
        """
        # Simple chunking by tokens (words) with overlap
        words = document.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def store_document(
        self,
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None
    ) -> List[str]:
        """
        Store a document in the vector database.
        
        Args:
            document: Document to store
            metadata: Optional metadata for the document
            document_id: Optional document ID
        
        Returns:
            List of chunk IDs
        """
        # Generate a document ID if not provided
        if document_id is None:
            import uuid
            document_id = str(uuid.uuid4())
        
        # Initialize metadata if not provided
        if metadata is None:
            metadata = {}
        
        # Add document ID to metadata
        metadata["document_id"] = document_id
        
        # Chunk the document
        chunks = self._semantic_chunking(document)
        
        # Generate embeddings
        embeddings = self._generate_embeddings(chunks)
        
        # Store in database
        chunk_ids = []
        
        try:
            if isinstance(self.db, MockVectorDB):
                chunk_ids = self.db.add(embeddings=embeddings, documents=chunks, metadata=metadata)
            
            elif self.db_provider.lower() == "chroma":
                # Generate chunk IDs
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    chunk_id = f"{document_id}_{i}"
                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk_index"] = i
                    chunk_metadata["total_chunks"] = len(chunks)
                    
                    self.db.add(
                        ids=[chunk_id],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[chunk_metadata]
                    )
                    
                    chunk_ids.append(chunk_id)
            
            elif self.db_provider.lower() == "pinecone":
                # Prepare vectors for upsert
                vectors = []
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    chunk_id = f"{document_id}_{i}"
                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk_index"] = i
                    chunk_metadata["total_chunks"] = len(chunks)
                    chunk_metadata["text"] = chunk
                    
                    vectors.append({
                        "id": chunk_id,
                        "values": embedding,
                        "metadata": chunk_metadata
                    })
                    
                    chunk_ids.append(chunk_id)
                
                # Upsert in batches of 100
                batch_size = 100
                for i in range(0, len(vectors), batch_size):
                    batch = vectors[i:i + batch_size]
                    self.db.upsert(vectors=batch)
            
            else:
                logger.error(f"Unsupported database provider: {self.db_provider}")
                raise ValueError(f"Unsupported database provider: {self.db_provider}")
        
        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
        
        return chunk_ids
    
    def retrieve_relevant_context(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context based on a query.
        
        Args:
            query: Query to search for
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
        
        Returns:
            List of relevant chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embeddings([query])[0]
            
            if isinstance(self.db, MockVectorDB):
                return self.db.search(query_embedding, n_results=n_results, filter_metadata=filter_metadata)
            
            elif self.db_provider.lower() == "chroma":
                # Prepare filter if provided
                where = filter_metadata if filter_metadata else None
                
                # Perform search
                results = self.db.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where
                )
                
                # Format results
                formatted_results = []
                for i, (doc, metadata, distance) in enumerate(zip(
                    results.get("documents", [[]])[0],
                    results.get("metadatas", [[]])[0],
                    results.get("distances", [[]])[0]
                )):
                    formatted_results.append({
                        "text": doc,
                        "metadata": metadata,
                        "similarity": 1.0 - distance  # Convert distance to similarity
                    })
                
                return formatted_results
            
            elif self.db_provider.lower() == "pinecone":
                # Prepare filter if provided
                filter_dict = filter_metadata if filter_metadata else None
                
                # Perform search
                results = self.db.query(
                    vector=query_embedding,
                    top_k=n_results,
                    filter=filter_dict,
                    include_metadata=True
                )
                
                # Format results
                formatted_results = []
                for match in results.get("matches", []):
                    formatted_results.append({
                        "text": match["metadata"].get("text", ""),
                        "metadata": {k: v for k, v in match["metadata"].items() if k != "text"},
                        "similarity": match["score"]
                    })
                
                return formatted_results
            
            else:
                logger.error(f"Unsupported database provider: {self.db_provider}")
                raise ValueError(f"Unsupported database provider: {self.db_provider}")
        
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
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
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_context(
            query=query,
            n_results=window_size,
            filter_metadata=filter_metadata
        )
        
        # Sort chunks by document ID and chunk index if from the same document
        chunks_by_doc = {}
        for chunk in relevant_chunks:
            doc_id = chunk["metadata"].get("document_id", "")
            if doc_id not in chunks_by_doc:
                chunks_by_doc[doc_id] = []
            chunks_by_doc[doc_id].append(chunk)
        
        # Sort chunks within each document by chunk index
        for doc_id in chunks_by_doc:
            chunks_by_doc[doc_id].sort(key=lambda x: x["metadata"].get("chunk_index", 0))
        
        # Concatenate chunks
        context_window = ""
        for doc_id, chunks in chunks_by_doc.items():
            for chunk in chunks:
                context_window += chunk["text"] + "\n\n"
        
        return context_window.strip()
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector database.
        
        Args:
            document_id: Document ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if isinstance(self.db, MockVectorDB):
                return self.db.delete(document_id=document_id)
            
            elif self.db_provider.lower() == "chroma":
                # Get all chunk IDs for the document
                results = self.db.get(where={"document_id": document_id})
                chunk_ids = results.get("ids", [])
                
                # Delete chunks
                if chunk_ids:
                    self.db.delete(ids=chunk_ids)
                
                return True
            
            elif self.db_provider.lower() == "pinecone":
                # Delete by metadata filter
                self.db.delete(filter={"document_id": document_id})
                return True
            
            else:
                logger.error(f"Unsupported database provider: {self.db_provider}")
                raise ValueError(f"Unsupported database provider: {self.db_provider}")
        
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False


class MockVectorDB:
    """Mock vector database for development and testing."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.data = []
    
    def add(self, embeddings: List[List[float]], documents: List[str], metadata: Dict[str, Any]) -> List[str]:
        import uuid
        chunk_ids = []
        
        for i, (embedding, document) in enumerate(zip(embeddings, documents)):
            chunk_id = str(uuid.uuid4())
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(documents)
            
            self.data.append({
                "id": chunk_id,
                "embedding": embedding,
                "document": document,
                "metadata": chunk_metadata
            })
            
            chunk_ids.append(chunk_id)
        
        return chunk_ids
    
    def search(self, query_embedding: List[float], n_results: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Simple mock search (no actual similarity calculation)
        results = []
        
        for item in self.data:
            # Apply filter if provided
            if filter_metadata:
                match = True
                for key, value in filter_metadata.items():
                    if key not in item["metadata"] or item["metadata"][key] != value:
                        match = False
                        break
                
                if not match:
                    continue
            
            results.append({
                "text": item["document"],
                "metadata": item["metadata"],
                "similarity": 0.9  # Mock similarity score
            })
            
            if len(results) >= n_results:
                break
        
        return results
    
    def delete(self, document_id: str) -> bool:
        # Find and remove items with matching document_id
        self.data = [item for item in self.data if item["metadata"].get("document_id") != document_id]
        return True


class MockEmbeddingModel:
    """Mock embedding model for development and testing."""
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        return [self.encode_single(text) for text in texts]
    
    def encode_single(self, text: str) -> List[float]:
        # Generate a deterministic but unique embedding based on the text
        import hashlib
        
        # Create a hash of the text
        hash_object = hashlib.md5(text.encode())
        hash_hex = hash_object.hexdigest()
        
        # Convert the hash to a list of floats
        embedding = []
        for i in range(0, len(hash_hex), 2):
            if i + 2 <= len(hash_hex):
                hex_pair = hash_hex[i:i+2]
                float_val = int(hex_pair, 16) / 255.0  # Normalize to [0, 1]
                embedding.append(float_val)
        
        # Pad or truncate to 768 dimensions (common for sentence-transformers)
        embedding = embedding * (768 // len(embedding) + 1)
        return embedding[:768]
