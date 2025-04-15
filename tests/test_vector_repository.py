import unittest
from unittest.mock import Mock, patch
import sys
import os
import tempfile

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.training.vector_db.optimized_repository import OptimizedVectorRepository
from app.core.cache import Cache

class OptimizedVectorRepositoryTests(unittest.TestCase):
    """
    Unit tests for the OptimizedVectorRepository class.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create mock backend
        self.mock_backend = Mock()
        
        # Create mock cache
        self.mock_cache = Mock(spec=Cache)
        
        # Create repository
        self.repository = OptimizedVectorRepository(
            backend=self.mock_backend,
            cache=self.mock_cache,
            namespace="test_namespace"
        )
    
    def test_initialization(self):
        """Test repository initialization."""
        # Assert
        self.assertEqual(self.repository.namespace, "test_namespace")
        self.assertEqual(self.repository.backend, self.mock_backend)
        self.assertEqual(self.repository.cache, self.mock_cache)
    
    def test_add_document(self):
        """Test adding a document."""
        # Setup mock
        self.mock_backend.add_document.return_value = "doc_id_123"
        
        # Add document
        doc_id = self.repository.add_document(
            text="Test document",
            metadata={"source": "test"}
        )
        
        # Assert
        self.assertEqual(doc_id, "doc_id_123")
        self.mock_backend.add_document.assert_called_once_with(
            text="Test document",
            metadata={"source": "test"},
            namespace="test_namespace"
        )
        
        # Check that cache was invalidated
        self.mock_cache.delete.assert_called()
    
    def test_add_documents(self):
        """Test adding multiple documents."""
        # Setup mock
        self.mock_backend.add_documents.return_value = ["doc_id_1", "doc_id_2"]
        
        # Add documents
        doc_ids = self.repository.add_documents(
            texts=["Doc 1", "Doc 2"],
            metadatas=[{"source": "test1"}, {"source": "test2"}]
        )
        
        # Assert
        self.assertEqual(doc_ids, ["doc_id_1", "doc_id_2"])
        self.mock_backend.add_documents.assert_called_once_with(
            texts=["Doc 1", "Doc 2"],
            metadatas=[{"source": "test1"}, {"source": "test2"}],
            namespace="test_namespace"
        )
        
        # Check that cache was invalidated
        self.mock_cache.delete.assert_called()
    
    def test_get_document(self):
        """Test getting a document."""
        # Setup mock
        self.mock_backend.get_document.return_value = {
            "id": "doc_id_123",
            "text": "Test document",
            "metadata": {"source": "test"}
        }
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get document
        doc = self.repository.get_document("doc_id_123")
        
        # Assert
        self.assertEqual(doc["id"], "doc_id_123")
        self.assertEqual(doc["text"], "Test document")
        self.assertEqual(doc["metadata"]["source"], "test")
        
        # Check that backend was called
        self.mock_backend.get_document.assert_called_once_with(
            doc_id="doc_id_123",
            namespace="test_namespace"
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
    
    def test_get_document_cached(self):
        """Test getting a document from cache."""
        # Setup cache mock
        cached_doc = {
            "id": "doc_id_123",
            "text": "Test document",
            "metadata": {"source": "test"}
        }
        self.mock_cache.get.return_value = cached_doc  # Cache hit
        
        # Get document
        doc = self.repository.get_document("doc_id_123")
        
        # Assert
        self.assertEqual(doc, cached_doc)
        
        # Check that backend was not called
        self.mock_backend.get_document.assert_not_called()
    
    def test_search(self):
        """Test searching documents."""
        # Setup mock
        search_results = [
            {"id": "doc_id_1", "text": "Doc 1", "metadata": {"source": "test1"}, "score": 0.9},
            {"id": "doc_id_2", "text": "Doc 2", "metadata": {"source": "test2"}, "score": 0.8}
        ]
        self.mock_backend.search.return_value = search_results
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Search
        results = self.repository.search(
            query="test query",
            limit=10,
            filters={"source": "test"}
        )
        
        # Assert
        self.assertEqual(results, search_results)
        
        # Check that backend was called
        self.mock_backend.search.assert_called_once_with(
            query="test query",
            limit=10,
            filters={"source": "test"},
            namespace="test_namespace"
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
    
    def test_search_cached(self):
        """Test searching documents from cache."""
        # Setup cache mock
        cached_results = [
            {"id": "doc_id_1", "text": "Doc 1", "metadata": {"source": "test1"}, "score": 0.9},
            {"id": "doc_id_2", "text": "Doc 2", "metadata": {"source": "test2"}, "score": 0.8}
        ]
        self.mock_cache.get.return_value = cached_results  # Cache hit
        
        # Search
        results = self.repository.search(
            query="test query",
            limit=10,
            filters={"source": "test"}
        )
        
        # Assert
        self.assertEqual(results, cached_results)
        
        # Check that backend was not called
        self.mock_backend.search.assert_not_called()
    
    def test_delete_document(self):
        """Test deleting a document."""
        # Setup mock
        self.mock_backend.delete_document.return_value = True
        
        # Delete document
        success = self.repository.delete_document("doc_id_123")
        
        # Assert
        self.assertTrue(success)
        self.mock_backend.delete_document.assert_called_once_with(
            doc_id="doc_id_123",
            namespace="test_namespace"
        )
        
        # Check that cache was invalidated
        self.mock_cache.delete.assert_called()
    
    def test_update_document(self):
        """Test updating a document."""
        # Setup mock
        self.mock_backend.update_document.return_value = True
        
        # Update document
        success = self.repository.update_document(
            doc_id="doc_id_123",
            text="Updated document",
            metadata={"source": "test", "updated": True}
        )
        
        # Assert
        self.assertTrue(success)
        self.mock_backend.update_document.assert_called_once_with(
            doc_id="doc_id_123",
            text="Updated document",
            metadata={"source": "test", "updated": True},
            namespace="test_namespace"
        )
        
        # Check that cache was invalidated
        self.mock_cache.delete.assert_called()
    
    def test_clear(self):
        """Test clearing the repository."""
        # Setup mock
        self.mock_backend.clear.return_value = True
        
        # Clear repository
        success = self.repository.clear()
        
        # Assert
        self.assertTrue(success)
        self.mock_backend.clear.assert_called_once_with(
            namespace="test_namespace"
        )
        
        # Check that cache was cleared
        self.mock_cache.clear.assert_called_once()
    
    def test_count(self):
        """Test counting documents."""
        # Setup mock
        self.mock_backend.count.return_value = 42
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Count documents
        count = self.repository.count()
        
        # Assert
        self.assertEqual(count, 42)
        self.mock_backend.count.assert_called_once_with(
            namespace="test_namespace"
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
    
    def test_count_cached(self):
        """Test counting documents from cache."""
        # Setup cache mock
        self.mock_cache.get.return_value = 42  # Cache hit
        
        # Count documents
        count = self.repository.count()
        
        # Assert
        self.assertEqual(count, 42)
        
        # Check that backend was not called
        self.mock_backend.count.assert_not_called()
    
    def test_get_stats(self):
        """Test getting repository statistics."""
        # Setup mocks
        self.mock_backend.get_stats.return_value = {
            "document_count": 42,
            "vector_dimension": 768
        }
        self.mock_cache.stats.return_value = {
            "size": 10,
            "hit_count": 100,
            "miss_count": 20
        }
        
        # Get stats
        stats = self.repository.get_stats()
        
        # Assert
        self.assertEqual(stats["backend"]["document_count"], 42)
        self.assertEqual(stats["backend"]["vector_dimension"], 768)
        self.assertEqual(stats["cache"]["size"], 10)
        self.assertEqual(stats["cache"]["hit_count"], 100)
        self.assertEqual(stats["cache"]["miss_count"], 20)
        self.assertEqual(stats["namespace"], "test_namespace")

if __name__ == "__main__":
    unittest.main()
