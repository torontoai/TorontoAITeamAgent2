"""
Documentation Style Guide for TORONTO AI TEAM AGENT

This document defines the standardized documentation format for all code in the TORONTO AI TEAM AGENT project.

## Module Documentation

Each module should have a module-level docstring that includes:
1. A brief description of the module's purpose
2. Any important notes about usage
3. Examples if appropriate
4. Dependencies or requirements

Example:
```python
\"\"\"
Vector Database Module

This module provides a vector database implementation for storing and retrieving
embeddings with metadata. It supports multiple backends including in-memory,
ChromaDB, Pinecone, Weaviate, Milvus, and FAISS.

Important:
    - Configure the backend in config.py before using
    - Ensure required dependencies are installed for the chosen backend

Example:
    >>> from app.training.vector_db import get_vector_db
    >>> db = get_vector_db(backend="in_memory")
    >>> db.add_document("This is a test document", {"source": "test"})
    >>> results = db.search("test document", limit=5)
\"\"\"
```

## Class Documentation

Each class should have a class-level docstring that includes:
1. A brief description of the class's purpose
2. Any important notes about usage
3. Examples if appropriate
4. Attributes (if any)

Example:
```python
class VectorDatabase:
    \"\"\"
    Vector database for storing and retrieving embeddings with metadata.
    
    This class provides a unified interface for working with vector databases,
    abstracting away the details of specific backend implementations.
    
    Attributes:
        backend (str): The name of the backend being used
        namespace (str): The namespace for this database instance
        embedding_dim (int): Dimension of the embedding vectors
    
    Example:
        >>> db = VectorDatabase(backend="in_memory")
        >>> db.add_document("This is a test document", {"source": "test"})
        >>> results = db.search("test document", limit=5)
    \"\"\"
```

## Method/Function Documentation

Each method or function should have a docstring that includes:
1. A brief description of what the method/function does
2. Parameters (with types and descriptions)
3. Return value (with type and description)
4. Exceptions raised (if any)
5. Examples if appropriate

Example:
```python
def search(self, query: str, limit: int = 10, filters: dict = None) -> List[Dict]:
    \"\"\"
    Search for documents similar to the query text.
    
    Args:
        query (str): The query text to search for
        limit (int, optional): Maximum number of results to return. Defaults to 10.
        filters (dict, optional): Metadata filters to apply. Defaults to None.
    
    Returns:
        List[Dict]: List of documents with similarity scores, each containing:
            - id (str): Document ID
            - text (str): Document text
            - metadata (dict): Document metadata
            - score (float): Similarity score (0-1)
    
    Raises:
        ValueError: If query is empty or limit is less than 1
        ConnectionError: If backend is unavailable
    
    Example:
        >>> results = db.search("machine learning", limit=5, filters={"category": "AI"})
        >>> for doc in results:
        ...     print(f"{doc['score']:.2f}: {doc['text'][:50]}...")
    \"\"\"
```

## Variable Documentation

Important variables, especially class attributes, should be documented with type hints and comments:

Example:
```python
# Maximum number of connections in the pool
max_connections: int = 10

# Cache TTL in seconds (None for no expiry)
cache_ttl: Optional[int] = 3600
```

## Constants Documentation

Constants should be in ALL_CAPS and documented with a comment:

Example:
```python
# Default embedding dimension
DEFAULT_EMBEDDING_DIM = 768

# Maximum number of results that can be returned in a single query
MAX_RESULTS_LIMIT = 100
```

## Type Hints

Use type hints for all function parameters and return values:

Example:
```python
def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
    ...

def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[str]:
    ...
```

## Exceptions

Document all exceptions that might be raised:

Example:
```python
def connect(self) -> None:
    \"\"\"
    Connect to the database.
    
    Raises:
        ConnectionError: If connection fails
        AuthenticationError: If authentication fails
        ConfigurationError: If configuration is invalid
    \"\"\"
```

## TODOs

Mark incomplete or future work with TODO comments that include ownership:

Example:
```python
# TODO(username): Implement caching for search results
```

## Deprecation Notices

Mark deprecated functions or methods with deprecation notices:

Example:
```python
def old_method(self):
    \"\"\"
    This method is deprecated and will be removed in version 2.0.
    Use new_method() instead.
    
    Deprecated since version 1.5.
    \"\"\"
    warnings.warn(
        "old_method is deprecated and will be removed in version 2.0. "
        "Use new_method instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()
```
"""
