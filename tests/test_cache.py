import unittest
from unittest.mock import Mock, patch
import sys
import os
import tempfile

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.cache import Cache, PersistentCache, cached, get_default_cache

class CacheTests(unittest.TestCase):
    """
    Unit tests for the cache module.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.cache = Cache(max_size=10, cleanup_interval=1)
    
    def test_get_set(self):
        """Test getting and setting values."""
        # Set value
        self.cache.set("test_key", "test_value")
        
        # Get value
        value = self.cache.get("test_key")
        
        # Assert
        self.assertEqual(value, "test_value")
    
    def test_get_default(self):
        """Test getting a non-existent key with default value."""
        # Get non-existent value
        value = self.cache.get("non_existent_key", "default_value")
        
        # Assert
        self.assertEqual(value, "default_value")
    
    def test_delete(self):
        """Test deleting a value."""
        # Set value
        self.cache.set("test_key", "test_value")
        
        # Delete value
        result = self.cache.delete("test_key")
        
        # Assert
        self.assertTrue(result)
        self.assertIsNone(self.cache.get("test_key"))
    
    def test_delete_non_existent(self):
        """Test deleting a non-existent key."""
        # Delete non-existent value
        result = self.cache.delete("non_existent_key")
        
        # Assert
        self.assertFalse(result)
    
    def test_clear(self):
        """Test clearing the cache."""
        # Set values
        self.cache.set("test_key1", "test_value1")
        self.cache.set("test_key2", "test_value2")
        
        # Clear cache
        self.cache.clear()
        
        # Assert
        self.assertIsNone(self.cache.get("test_key1"))
        self.assertIsNone(self.cache.get("test_key2"))
    
    def test_expiry(self):
        """Test value expiry."""
        # Set value with expiry
        self.cache.set("test_key", "test_value", ttl=1)
        
        # Get value immediately
        value = self.cache.get("test_key")
        self.assertEqual(value, "test_value")
        
        # Wait for expiry
        import time
        time.sleep(1.1)
        
        # Get value after expiry
        value = self.cache.get("test_key")
        self.assertIsNone(value)
    
    def test_max_size(self):
        """Test maximum cache size."""
        # Set more values than max size
        for i in range(20):
            self.cache.set(f"key{i}", f"value{i}")
        
        # Check that some values were evicted
        self.assertLess(len(self.cache._cache), 20)
    
    def test_stats(self):
        """Test cache statistics."""
        # Set values
        self.cache.set("test_key1", "test_value1")
        self.cache.set("test_key2", "test_value2")
        
        # Get values
        self.cache.get("test_key1")
        self.cache.get("test_key1")
        
        # Get stats
        stats = self.cache.stats()
        
        # Assert
        self.assertEqual(stats["size"], 2)
        self.assertEqual(stats["max_size"], 10)
        self.assertEqual(stats["hit_count"], 3)

class PersistentCacheTests(unittest.TestCase):
    """
    Unit tests for the persistent cache.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = PersistentCache(self.temp_dir, max_size=10, cleanup_interval=1)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_persistence(self):
        """Test cache persistence."""
        # Set value
        self.cache.set("test_key", "test_value")
        
        # Create new cache instance
        new_cache = PersistentCache(self.temp_dir)
        
        # Get value from new instance
        value = new_cache.get("test_key")
        
        # Assert
        self.assertEqual(value, "test_value")
    
    def test_clear_persistence(self):
        """Test clearing the persistent cache."""
        # Set value
        self.cache.set("test_key", "test_value")
        
        # Clear cache
        self.cache.clear()
        
        # Create new cache instance
        new_cache = PersistentCache(self.temp_dir)
        
        # Get value from new instance
        value = new_cache.get("test_key")
        
        # Assert
        self.assertIsNone(value)

class CachedDecoratorTests(unittest.TestCase):
    """
    Unit tests for the cached decorator.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.cache = Cache()
    
    def test_cached_function(self):
        """Test caching function results."""
        # Create a test function
        call_count = [0]
        
        @cached(ttl=60, cache_instance=self.cache)
        def test_function(arg1, arg2):
            call_count[0] += 1
            return arg1 + arg2
        
        # Call function twice with same arguments
        result1 = test_function(1, 2)
        result2 = test_function(1, 2)
        
        # Assert
        self.assertEqual(result1, 3)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count[0], 1)  # Function should only be called once
    
    def test_cached_function_different_args(self):
        """Test caching function results with different arguments."""
        # Create a test function
        call_count = [0]
        
        @cached(ttl=60, cache_instance=self.cache)
        def test_function(arg1, arg2):
            call_count[0] += 1
            return arg1 + arg2
        
        # Call function with different arguments
        result1 = test_function(1, 2)
        result2 = test_function(3, 4)
        
        # Assert
        self.assertEqual(result1, 3)
        self.assertEqual(result2, 7)
        self.assertEqual(call_count[0], 2)  # Function should be called twice
    
    def test_cached_function_custom_key(self):
        """Test caching function results with custom key function."""
        # Create a test function
        call_count = [0]
        
        def key_function(arg1, arg2):
            return f"custom_key:{arg1}:{arg2}"
        
        @cached(ttl=60, key_fn=key_function, cache_instance=self.cache)
        def test_function(arg1, arg2):
            call_count[0] += 1
            return arg1 + arg2
        
        # Call function twice with same arguments
        result1 = test_function(1, 2)
        result2 = test_function(1, 2)
        
        # Assert
        self.assertEqual(result1, 3)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count[0], 1)  # Function should only be called once
        
        # Check that custom key was used
        self.assertIsNotNone(self.cache.get("custom_key:1:2"))

class DefaultCacheTests(unittest.TestCase):
    """
    Unit tests for the default cache.
    """
    
    def test_default_cache(self):
        """Test getting the default cache."""
        # Get default cache
        default_cache = get_default_cache()
        
        # Assert
        self.assertIsInstance(default_cache, Cache)
        
        # Set and get value
        default_cache.set("test_key", "test_value")
        value = default_cache.get("test_key")
        
        # Assert
        self.assertEqual(value, "test_value")

if __name__ == "__main__":
    unittest.main()
