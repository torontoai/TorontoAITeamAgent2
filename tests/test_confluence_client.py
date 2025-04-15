import unittest
from unittest.mock import Mock, patch
import sys
import os
import json

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.integration.optimized_confluence_client import OptimizedConfluenceClient
from app.core.cache import Cache

class OptimizedConfluenceClientTests(unittest.TestCase):
    """
    Unit tests for the OptimizedConfluenceClient class.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create mock auth manager
        self.mock_auth_manager = Mock()
        self.mock_auth_manager.get_confluence_auth_headers.return_value = {"Authorization": "Bearer test_token"}
        
        # Create mock cache
        self.mock_cache = Mock(spec=Cache)
        
        # Create client
        self.client = OptimizedConfluenceClient(
            base_url="https://confluence.example.com",
            auth_manager=self.mock_auth_manager,
            cache=self.mock_cache
        )
        
        # Mock the connection pool
        self.client.connection_pool = None
        
        # Create a mock session
        self.mock_session = Mock()
        
        # Mock _get_connection to return the mock session
        self.original_get_connection = self.client._get_connection
        self.client._get_connection = Mock(return_value=self.mock_session)
        
        # Mock _return_connection
        self.client._return_connection = Mock()
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore original _get_connection
        self.client._get_connection = self.original_get_connection
    
    def test_initialization(self):
        """Test client initialization."""
        # Assert
        self.assertEqual(self.client.base_url, "https://confluence.example.com")
        self.assertEqual(self.client.auth_manager, self.mock_auth_manager)
        self.assertEqual(self.client.cache, self.mock_cache)
    
    async def test_get_spaces(self):
        """Test getting spaces."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "10000", "key": "SPACE1", "name": "Space 1"},
                {"id": "10001", "key": "SPACE2", "name": "Space 2"}
            ],
            "size": 2,
            "limit": 100,
            "start": 0
        }
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get spaces
        spaces = await self.client.get_spaces()
        
        # Assert
        self.assertEqual(len(spaces["spaces"]), 2)
        self.assertEqual(spaces["spaces"][0].key, "SPACE1")
        self.assertEqual(spaces["spaces"][1].key, "SPACE2")
        self.assertEqual(spaces["size"], 2)
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://confluence.example.com/rest/api/space",
            params={"limit": 100, "start": 0}
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    async def test_get_space(self):
        """Test getting a space."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "10000",
            "key": "SPACE1",
            "name": "Space 1"
        }
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get space
        space = await self.client.get_space("SPACE1")
        
        # Assert
        self.assertEqual(space.id, "10000")
        self.assertEqual(space.key, "SPACE1")
        self.assertEqual(space.name, "Space 1")
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://confluence.example.com/rest/api/space/SPACE1"
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    async def test_get_space_not_found(self):
        """Test getting a non-existent space."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 404
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get space
        space = await self.client.get_space("NONEXISTENT")
        
        # Assert
        self.assertIsNone(space)
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://confluence.example.com/rest/api/space/NONEXISTENT"
        )
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    async def test_search_content(self):
        """Test searching content."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "10000",
                    "title": "Page 1",
                    "space": {"key": "SPACE1"},
                    "body": {"view": {"value": "Content 1"}}
                },
                {
                    "id": "10001",
                    "title": "Page 2",
                    "space": {"key": "SPACE2"},
                    "body": {"view": {"value": "Content 2"}}
                }
            ],
            "size": 2,
            "limit": 50,
            "start": 0
        }
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Search content
        result = await self.client.search_content("space = SPACE1")
        
        # Assert
        self.assertEqual(len(result["pages"]), 2)
        self.assertEqual(result["pages"][0].id, "10000")
        self.assertEqual(result["pages"][1].id, "10001")
        self.assertEqual(result["size"], 2)
        
        # Check that API was called
        self.mock_session.get.assert_called_once()
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    async def test_get_page(self):
        """Test getting a page."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "10000",
            "title": "Test Page",
            "space": {"key": "SPACE1"},
            "body": {"view": {"value": "Page content"}},
            "version": {"number": 1},
            "ancestors": []
        }
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get page
        page = await self.client.get_page("10000")
        
        # Assert
        self.assertEqual(page.id, "10000")
        self.assertEqual(page.title, "Test Page")
        self.assertEqual(page.space.key, "SPACE1")
        self.assertEqual(page.body.view.value, "Page content")
        self.assertEqual(page.version.number, 1)
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://confluence.example.com/rest/api/content/10000",
            params={"expand": "space,version,body.view,ancestors"}
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    async def test_create_page(self):
        """Test creating a page."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "10000",
            "title": "New Page",
            "space": {"key": "SPACE1"}
        }
        self.mock_session.post.return_value = mock_response
        
        # Mock get_page to return a page
        self.client.get_page = Mock()
        self.client.get_page.return_value = Mock(
            id="10000",
            title="New Page",
            space=Mock(key="SPACE1")
        )
        
        # Create page
        page = await self.client.create_page(
            space_key="SPACE1",
            title="New Page",
            content="Page content"
        )
        
        # Assert
        self.assertEqual(page.id, "10000")
        self.assertEqual(page.title, "New Page")
        self.assertEqual(page.space.key, "SPACE1")
        
        # Check that API was called
        self.mock_session.post.assert_called_once()
        
        # Check that cache was invalidated
        self.mock_cache.delete.assert_called()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    async def test_update_page(self):
        """Test updating a page."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "10000",
            "title": "Updated Page",
            "space": {"key": "SPACE1"},
            "version": {"number": 2}
        }
        self.mock_session.put.return_value = mock_response
        
        # Mock get_page to return a page
        self.client.get_page = Mock()
        self.client.get_page.return_value = Mock(
            id="10000",
            title="Updated Page",
            space=Mock(key="SPACE1"),
            version=Mock(number=2)
        )
        
        # Update page
        page = await self.client.update_page(
            page_id="10000",
            title="Updated Page",
            content="Updated content",
            version=1
        )
        
        # Assert
        self.assertEqual(page.id, "10000")
        self.assertEqual(page.title, "Updated Page")
        self.assertEqual(page.space.key, "SPACE1")
        self.assertEqual(page.version.number, 2)
        
        # Check that API was called
        self.mock_session.put.assert_called_once()
        
        # Check that cache was invalidated
        self.mock_cache.delete.assert_called()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    async def test_get_attachments(self):
        """Test getting attachments for a page."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "att10000", "title": "attachment1.pdf", "metadata": {"mediaType": "application/pdf"}},
                {"id": "att10001", "title": "attachment2.png", "metadata": {"mediaType": "image/png"}}
            ]
        }
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get attachments
        attachments = await self.client.get_attachments("10000")
        
        # Assert
        self.assertEqual(len(attachments), 2)
        self.assertEqual(attachments[0].id, "att10000")
        self.assertEqual(attachments[0].title, "attachment1.pdf")
        self.assertEqual(attachments[1].id, "att10001")
        self.assertEqual(attachments[1].title, "attachment2.png")
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://confluence.example.com/rest/api/content/10000/child/attachment"
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    async def test_get_user(self):
        """Test getting a user."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "username": "testuser",
            "displayName": "Test User",
            "email": "test@example.com"
        }
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get user
        user = await self.client.get_user("testuser")
        
        # Assert
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.displayName, "Test User")
        self.assertEqual(user.email, "test@example.com")
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://confluence.example.com/rest/api/user",
            params={"username": "testuser"}
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        # Clear cache
        self.client.clear_cache()
        
        # Check that cache was cleared
        self.mock_cache.clear.assert_called_once()
    
    def test_get_stats(self):
        """Test getting client statistics."""
        # Setup cache mock
        self.mock_cache.stats.return_value = {
            "size": 10,
            "hit_count": 100,
            "miss_count": 20
        }
        
        # Get stats
        stats = self.client.get_stats()
        
        # Assert
        self.assertEqual(stats["cache"], self.mock_cache.stats.return_value)

if __name__ == "__main__":
    unittest.main()
