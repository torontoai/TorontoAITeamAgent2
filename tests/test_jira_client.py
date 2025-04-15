import unittest
from unittest.mock import Mock, patch
import sys
import os
import json

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.integration.optimized_jira_client import OptimizedJiraClient
from app.core.cache import Cache

class OptimizedJiraClientTests(unittest.TestCase):
    """
    Unit tests for the OptimizedJiraClient class.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create mock auth manager
        self.mock_auth_manager = Mock()
        self.mock_auth_manager.get_jira_auth_headers.return_value = {"Authorization": "Bearer test_token"}
        
        # Create mock cache
        self.mock_cache = Mock(spec=Cache)
        
        # Create client
        self.client = OptimizedJiraClient(
            base_url="https://jira.example.com",
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
        self.assertEqual(self.client.base_url, "https://jira.example.com")
        self.assertEqual(self.client.auth_manager, self.mock_auth_manager)
        self.assertEqual(self.client.cache, self.mock_cache)
    
    def test_get_projects(self):
        """Test getting projects."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "10000", "key": "TEST", "name": "Test Project"},
            {"id": "10001", "key": "DEV", "name": "Development Project"}
        ]
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get projects
        projects = self.client.get_projects()
        
        # Assert
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0].key, "TEST")
        self.assertEqual(projects[1].key, "DEV")
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://jira.example.com/rest/api/2/project"
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    def test_get_projects_cached(self):
        """Test getting projects from cache."""
        # Setup cache mock
        cached_projects = [
            {"id": "10000", "key": "TEST", "name": "Test Project"},
            {"id": "10001", "key": "DEV", "name": "Development Project"}
        ]
        self.mock_cache.get.return_value = cached_projects  # Cache hit
        
        # Get projects
        projects = self.client.get_projects()
        
        # Assert
        self.assertEqual(projects, cached_projects)
        
        # Check that API was not called
        self.mock_session.get.assert_not_called()
        
        # Check that connection was not used
        self.client._return_connection.assert_not_called()
    
    def test_get_project(self):
        """Test getting a project."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "10000",
            "key": "TEST",
            "name": "Test Project"
        }
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get project
        project = self.client.get_project("TEST")
        
        # Assert
        self.assertEqual(project.id, "10000")
        self.assertEqual(project.key, "TEST")
        self.assertEqual(project.name, "Test Project")
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://jira.example.com/rest/api/2/project/TEST"
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    def test_get_project_not_found(self):
        """Test getting a non-existent project."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 404
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get project
        project = self.client.get_project("NONEXISTENT")
        
        # Assert
        self.assertIsNone(project)
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://jira.example.com/rest/api/2/project/NONEXISTENT"
        )
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    def test_search_issues(self):
        """Test searching issues."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "id": "10000",
                    "key": "TEST-1",
                    "fields": {
                        "summary": "Test Issue 1",
                        "description": "Description 1"
                    }
                },
                {
                    "id": "10001",
                    "key": "TEST-2",
                    "fields": {
                        "summary": "Test Issue 2",
                        "description": "Description 2"
                    }
                }
            ],
            "total": 2,
            "maxResults": 50,
            "startAt": 0
        }
        self.mock_session.post.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Search issues
        result = self.client.search_issues("project = TEST")
        
        # Assert
        self.assertEqual(len(result["issues"]), 2)
        self.assertEqual(result["issues"][0].key, "TEST-1")
        self.assertEqual(result["issues"][1].key, "TEST-2")
        self.assertEqual(result["total"], 2)
        
        # Check that API was called
        self.mock_session.post.assert_called_once()
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    def test_get_issue(self):
        """Test getting an issue."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "10000",
            "key": "TEST-1",
            "fields": {
                "summary": "Test Issue",
                "description": "Description",
                "issuetype": {"name": "Bug"},
                "priority": {"name": "High"},
                "status": {"name": "Open"}
            }
        }
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get issue
        issue = self.client.get_issue("TEST-1")
        
        # Assert
        self.assertEqual(issue.id, "10000")
        self.assertEqual(issue.key, "TEST-1")
        self.assertEqual(issue.fields.summary, "Test Issue")
        self.assertEqual(issue.fields.description, "Description")
        self.assertEqual(issue.fields.issuetype.name, "Bug")
        self.assertEqual(issue.fields.priority.name, "High")
        self.assertEqual(issue.fields.status.name, "Open")
        
        # Check that API was called
        self.mock_session.get.assert_called_once_with(
            "https://jira.example.com/rest/api/2/issue/TEST-1",
            params={"expand": "renderedFields,transitions,changelog"}
        )
        
        # Check that result was cached
        self.mock_cache.set.assert_called_once()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    def test_create_issue(self):
        """Test creating an issue."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "10000",
            "key": "TEST-1"
        }
        self.mock_session.post.return_value = mock_response
        
        # Create issue
        issue_key = self.client.create_issue(
            project_key="TEST",
            summary="New Issue",
            description="Description",
            issue_type="Bug"
        )
        
        # Assert
        self.assertEqual(issue_key, "TEST-1")
        
        # Check that API was called
        self.mock_session.post.assert_called_once()
        
        # Check that cache was invalidated
        self.mock_cache.delete.assert_called()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    def test_update_issue(self):
        """Test updating an issue."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 204
        self.mock_session.put.return_value = mock_response
        
        # Update issue
        success = self.client.update_issue(
            issue_key="TEST-1",
            fields={
                "summary": "Updated Issue",
                "description": "Updated Description"
            }
        )
        
        # Assert
        self.assertTrue(success)
        
        # Check that API was called
        self.mock_session.put.assert_called_once()
        
        # Check that cache was invalidated
        self.mock_cache.delete.assert_called()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    def test_add_comment(self):
        """Test adding a comment to an issue."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "10000",
            "body": "Test Comment"
        }
        self.mock_session.post.return_value = mock_response
        
        # Add comment
        comment = self.client.add_comment("TEST-1", "Test Comment")
        
        # Assert
        self.assertEqual(comment.id, "10000")
        self.assertEqual(comment.body, "Test Comment")
        
        # Check that API was called
        self.mock_session.post.assert_called_once()
        
        # Check that cache was invalidated
        self.mock_cache.delete.assert_called()
        
        # Check that connection was returned
        self.client._return_connection.assert_called_once_with(self.mock_session)
    
    def test_get_comments(self):
        """Test getting comments for an issue."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "comments": [
                {"id": "10000", "body": "Comment 1"},
                {"id": "10001", "body": "Comment 2"}
            ],
            "total": 2,
            "maxResults": 50,
            "startAt": 0
        }
        self.mock_session.get.return_value = mock_response
        
        # Setup cache mock
        self.mock_cache.get.return_value = None  # Cache miss
        
        # Get comments
        comments = self.client.get_comments("TEST-1")
        
        # Assert
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0].id, "10000")
        self.assertEqual(comments[0].body, "Comment 1")
        self.assertEqual(comments[1].id, "10001")
        self.assertEqual(comments[1].body, "Comment 2")
        
        # Check that API was called
        self.mock_session.get.assert_called_once()
        
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
