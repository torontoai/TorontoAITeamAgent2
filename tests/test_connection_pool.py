import unittest
from unittest.mock import Mock, patch
import sys
import os
import threading
import time

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.connection_pool import ConnectionPool, ConnectionPoolManager, get_pool_manager

class ConnectionPoolTests(unittest.TestCase):
    """
    Unit tests for the connection pool module.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create a simple connection factory
        self.connection_factory = Mock()
        self.connection_factory.return_value = Mock()
        
        # Create a simple validator
        self.validator = Mock()
        self.validator.return_value = True
        
        # Create a simple cleanup function
        self.cleanup = Mock()
        
        # Create connection pool
        self.pool = ConnectionPool(
            factory=self.connection_factory,
            validator=self.validator,
            cleanup=self.cleanup,
            min_size=2,
            max_size=5
        )
    
    def tearDown(self):
        """Clean up test environment."""
        self.pool.shutdown()
    
    def test_initialization(self):
        """Test pool initialization."""
        # Assert that min_size connections were created
        self.assertEqual(self.connection_factory.call_count, 2)
        
        # Check pool stats
        stats = self.pool.stats()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["in_use"], 0)
        self.assertEqual(stats["available"], 2)
        self.assertEqual(stats["min_size"], 2)
        self.assertEqual(stats["max_size"], 5)
        self.assertTrue(stats["running"])
    
    def test_get_connection(self):
        """Test getting a connection from the pool."""
        # Get a connection
        connection = self.pool.get_connection()
        
        # Assert
        self.assertIsNotNone(connection)
        self.assertEqual(connection, self.connection_factory.return_value)
        
        # Check pool stats
        stats = self.pool.stats()
        self.assertEqual(stats["in_use"], 1)
        self.assertEqual(stats["available"], 1)
    
    def test_return_connection(self):
        """Test returning a connection to the pool."""
        # Get a connection
        connection = self.pool.get_connection()
        
        # Return the connection
        self.pool.return_connection(connection)
        
        # Check pool stats
        stats = self.pool.stats()
        self.assertEqual(stats["in_use"], 0)
        self.assertEqual(stats["available"], 2)
    
    def test_max_size(self):
        """Test maximum pool size."""
        # Get max_size connections
        connections = []
        for _ in range(5):
            connections.append(self.pool.get_connection())
        
        # Check pool stats
        stats = self.pool.stats()
        self.assertEqual(stats["total"], 5)
        self.assertEqual(stats["in_use"], 5)
        self.assertEqual(stats["available"], 0)
        
        # Try to get another connection (should block)
        def get_connection():
            with self.assertRaises(TimeoutError):
                self.pool.get_connection()
        
        # Start thread to get connection
        thread = threading.Thread(target=get_connection)
        thread.start()
        
        # Wait for thread to finish
        thread.join(timeout=2)
        
        # Assert that thread finished
        self.assertFalse(thread.is_alive())
    
    def test_validation(self):
        """Test connection validation."""
        # Set validator to return False
        self.validator.return_value = False
        
        # Get a connection (should create a new one since validation fails)
        with self.assertRaises(Exception):
            connection = self.pool.get_connection()
        
        # Check that cleanup was called for invalid connections
        self.assertEqual(self.cleanup.call_count, 2)
    
    def test_shutdown(self):
        """Test pool shutdown."""
        # Shutdown pool
        self.pool.shutdown()
        
        # Check that cleanup was called for all connections
        self.assertEqual(self.cleanup.call_count, 2)
        
        # Check pool stats
        stats = self.pool.stats()
        self.assertEqual(stats["total"], 0)
        self.assertFalse(stats["running"])
        
        # Try to get a connection (should raise exception)
        with self.assertRaises(RuntimeError):
            self.pool.get_connection()

class ConnectionPoolManagerTests(unittest.TestCase):
    """
    Unit tests for the connection pool manager.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.pool_manager = ConnectionPoolManager()
        
        # Create a simple connection factory
        self.connection_factory = Mock()
        self.connection_factory.return_value = Mock()
    
    def tearDown(self):
        """Clean up test environment."""
        self.pool_manager.shutdown_all()
    
    def test_create_pool(self):
        """Test creating a connection pool."""
        # Create a pool
        pool = self.pool_manager.create_pool(
            name="test_pool",
            factory=self.connection_factory
        )
        
        # Assert
        self.assertIsNotNone(pool)
        self.assertIsInstance(pool, ConnectionPool)
        
        # Check pool manager stats
        stats = self.pool_manager.stats()
        self.assertIn("test_pool", stats)
    
    def test_get_pool(self):
        """Test getting a connection pool."""
        # Create a pool
        created_pool = self.pool_manager.create_pool(
            name="test_pool",
            factory=self.connection_factory
        )
        
        # Get the pool
        pool = self.pool_manager.get_pool("test_pool")
        
        # Assert
        self.assertIs(pool, created_pool)
    
    def test_get_nonexistent_pool(self):
        """Test getting a non-existent connection pool."""
        # Try to get a non-existent pool
        with self.assertRaises(KeyError):
            self.pool_manager.get_pool("non_existent_pool")
    
    def test_shutdown_pool(self):
        """Test shutting down a connection pool."""
        # Create a pool
        pool = self.pool_manager.create_pool(
            name="test_pool",
            factory=self.connection_factory
        )
        
        # Shutdown the pool
        self.pool_manager.shutdown_pool("test_pool")
        
        # Check that pool was removed
        with self.assertRaises(KeyError):
            self.pool_manager.get_pool("test_pool")
    
    def test_shutdown_all(self):
        """Test shutting down all connection pools."""
        # Create multiple pools
        self.pool_manager.create_pool(
            name="test_pool1",
            factory=self.connection_factory
        )
        self.pool_manager.create_pool(
            name="test_pool2",
            factory=self.connection_factory
        )
        
        # Shutdown all pools
        self.pool_manager.shutdown_all()
        
        # Check that all pools were removed
        stats = self.pool_manager.stats()
        self.assertEqual(len(stats), 0)

class GlobalPoolManagerTests(unittest.TestCase):
    """
    Unit tests for the global pool manager.
    """
    
    def test_get_pool_manager(self):
        """Test getting the global pool manager."""
        # Get global pool manager
        pool_manager = get_pool_manager()
        
        # Assert
        self.assertIsNotNone(pool_manager)
        self.assertIsInstance(pool_manager, ConnectionPoolManager)
        
        # Get it again and check it's the same instance
        pool_manager2 = get_pool_manager()
        self.assertIs(pool_manager, pool_manager2)

if __name__ == "__main__":
    unittest.main()
