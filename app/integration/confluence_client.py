"""TORONTO AI TEAM AGENT - Confluence API Client

This module provides a client for interacting with the Confluence API.

Copyright (c) 2025 TORONTO AI
Created by David Tadeusz Chudak
All rights reserved."""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import requests
from requests.exceptions import RequestException, Timeout

from .config import ConfluenceConfig
from .auth import token_manager
from .models import (
    ConfluenceSpace, ConfluencePage, ConfluenceComment, ConfluenceAttachment,
    SyncStatus, SyncDirection
)


logger = logging.getLogger(__name__)


class ConfluenceApiError(Exception):
    """Exception raised for Confluence API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"{message} - Status: {status_code}, Response: {response_text}")


class ConfluenceApiClient:
    """Client for interacting with the Confluence API.
    Handles API requests, rate limiting, and error handling."""
    
    def __init__(self, config: ConfluenceConfig):
        """Initialize the Confluence API client.
        
        Args:
            config: Confluence configuration"""
        self.config = config
        self.base_url = config.url.rstrip('/')
        self.api_base = f"{self.base_url}/rest/api"
        self.max_retries = config.max_retries
        self.timeout = config.timeout
        
        # Validate credentials on initialization
        if not token_manager.validate_confluence_credentials(config):
            raise ConfluenceApiError("Failed to validate Confluence credentials")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Tuple[int, Dict[str, Any]]:
        """Make a request to the Confluence API with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request data (for POST/PUT)
            params: Query parameters
            files: Files to upload
            retry_count: Current retry attempt
            
        Returns:
            Tuple of (status_code, response_json)
            
        Raises:
            ConfluenceApiError: If the request fails after all retries"""
        headers, auth = token_manager.get_confluence_auth(self.config)
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        
        try:
            if method == 'GET':
                response = requests.get(
                    url, 
                    headers=headers, 
                    auth=auth, 
                    params=params,
                    timeout=self.timeout
                )
            elif method == 'POST':
                if files:
                    # For file uploads, don't include the JSON content-type header
                    headers.pop('Content-Type', None)
                    response = requests.post(
                        url, 
                        headers=headers, 
                        auth=auth, 
                        params=params,
                        files=files,
                        data=data,  # For file uploads, data should be form fields
                        timeout=self.timeout
                    )
                else:
                    response = requests.post(
                        url, 
                        headers=headers, 
                        auth=auth, 
                        params=params,
                        json=data,
                        timeout=self.timeout
                    )
            elif method == 'PUT':
                response = requests.put(
                    url, 
                    headers=headers, 
                    auth=auth, 
                    params=params,
                    json=data,
                    timeout=self.timeout
                )
            elif method == 'DELETE':
                response = requests.delete(
                    url, 
                    headers=headers, 
                    auth=auth, 
                    params=params,
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle rate limiting
            if response.status_code == 429:
                if retry_count < self.max_retries:
                    # Get retry-after header or use exponential backoff
                    retry_after = int(response.headers.get('Retry-After', 2 ** retry_count))
                    logger.warning(f"Rate limited by Confluence API. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    return self._make_request(method, endpoint, data, params, files, retry_count + 1)
                else:
                    raise ConfluenceApiError(
                        "Exceeded maximum retries due to rate limiting", 
                        response.status_code, 
                        response.text
                    )
            
            # Handle server errors
            if response.status_code >= 500:
                if retry_count < self.max_retries:
                    # Use exponential backoff
                    retry_after = 2 ** retry_count
                    logger.warning(f"Confluence API server error. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    return self._make_request(method, endpoint, data, params, files, retry_count + 1)
                else:
                    raise ConfluenceApiError(
                        "Exceeded maximum retries due to server errors", 
                        response.status_code, 
                        response.text
                    )
            
            # Handle authentication errors
            if response.status_code in (401, 403):
                raise ConfluenceApiError(
                    "Authentication or authorization error", 
                    response.status_code, 
                    response.text
                )
            
            # Parse response
            response_data = {}
            if response.text:
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    # Some endpoints might not return JSON
                    response_data = {"text": response.text}
            
            return response.status_code, response_data
            
        except Timeout:
            if retry_count < self.max_retries:
                retry_after = 2 ** retry_count
                logger.warning(f"Confluence API request timed out. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, data, params, files, retry_count + 1)
            else:
                raise ConfluenceApiError(f"Confluence API request timed out after {self.max_retries} retries")
        
        except RequestException as e:
            if retry_count < self.max_retries:
                retry_after = 2 ** retry_count
                logger.warning(f"Confluence API request failed: {str(e)}. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, data, params, files, retry_count + 1)
            else:
                raise ConfluenceApiError(f"Confluence API request failed after {self.max_retries} retries: {str(e)}")
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get information about the current user.
        
        Returns:
            User information"""
        status_code, response = self._make_request('GET', 'user/current')
        
        if status_code != 200:
            raise ConfluenceApiError("Failed to get current user", status_code, response)
        
        return response
    
    def get_spaces(self, limit: int = 25, start: int = 0) -> Dict[str, Any]:
        """Get all spaces accessible to the current user.
        
        Args:
            limit: Maximum number of spaces to return
            start: Index of the first space to return
            
        Returns:
            Dictionary containing spaces and pagination information"""
        params = {
            "limit": limit,
            "start": start
        }
        
        status_code, response = self._make_request('GET', 'space', params=params)
        
        if status_code != 200:
            raise ConfluenceApiError("Failed to get spaces", status_code, response)
        
        return response
    
    def get_space(self, space_key: str) -> Dict[str, Any]:
        """Get information about a specific space.
        
        Args:
            space_key: The space key
            
        Returns:
            Space information"""
        status_code, response = self._make_request('GET', f'space/{space_key}')
        
        if status_code != 200:
            raise ConfluenceApiError(f"Failed to get space {space_key}", status_code, response)
        
        return response
    
    def create_space(self, space_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new space.
        
        Args:
            space_data: Space data
            
        Returns:
            Created space information"""
        status_code, response = self._make_request('POST', 'space', data=space_data)
        
        if status_code != 200:
            raise ConfluenceApiError("Failed to create space", status_code, response)
        
        return response
    
    def get_content(
        self, 
        space_key: Optional[str] = None, 
        type: str = "page", 
        title: Optional[str] = None,
        limit: int = 25, 
        start: int = 0
    ) -> Dict[str, Any]:
        """Get content from Confluence.
        
        Args:
            space_key: Optional space key to filter by
            type: Content type (page, blogpost, comment, attachment)
            title: Optional title to filter by
            limit: Maximum number of items to return
            start: Index of the first item to return
            
        Returns:
            Dictionary containing content and pagination information"""
        params = {
            "type": type,
            "limit": limit,
            "start": start
        }
        
        if space_key:
            params["spaceKey"] = space_key
        
        if title:
            params["title"] = title
        
        status_code, response = self._make_request('GET', 'content', params=params)
        
        if status_code != 200:
            raise ConfluenceApiError("Failed to get content", status_code, response)
        
        return response
    
    def get_content_by_id(self, content_id: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """Get content by ID.
        
        Args:
            content_id: The content ID
            expand: Optional comma-separated list of properties to expand
            
        Returns:
            Content information"""
        params = {}
        if expand:
            params["expand"] = expand
        
        status_code, response = self._make_request('GET', f'content/{content_id}', params=params)
        
        if status_code != 200:
            raise ConfluenceApiError(f"Failed to get content {content_id}", status_code, response)
        
        return response
    
    def create_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new content.
        
        Args:
            content_data: Content data
            
        Returns:
            Created content information"""
        status_code, response = self._make_request('POST', 'content', data=content_data)
        
        if status_code != 200:
            raise ConfluenceApiError("Failed to create content", status_code, response)
        
        return response
    
    def update_content(self, content_id: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing content.
        
        Args:
            content_id: The content ID
            content_data: Content data to update
            
        Returns:
            Updated content information"""
        status_code, response = self._make_request('PUT', f'content/{content_id}', data=content_data)
        
        if status_code != 200:
            raise ConfluenceApiError(f"Failed to update content {content_id}", status_code, response)
        
        return response
    
    def delete_content(self, content_id: str) -> None:
        """Delete content.
        
        Args:
            content_id: The content ID"""
        status_code, response = self._make_request('DELETE', f'content/{content_id}')
        
        if status_code != 204:
            raise ConfluenceApiError(f"Failed to delete content {content_id}", status_code, response)
    
    def get_content_children(
        self, 
        content_id: str, 
        child_type: str = "page", 
        limit: int = 25, 
        start: int = 0
    ) -> Dict[str, Any]:
        """Get children of content.
        
        Args:
            content_id: The content ID
            child_type: Child type (page, comment, attachment)
            limit: Maximum number of items to return
            start: Index of the first item to return
            
        Returns:
            Dictionary containing children and pagination information"""
        params = {
            "limit": limit,
            "start": start
        }
        
        status_code, response = self._make_request(
            'GET', 
            f'content/{content_id}/child/{child_type}', 
            params=params
        )
        
        if status_code != 200:
            raise ConfluenceApiError(f"Failed to get children for content {content_id}", status_code, response)
        
        return response
    
    def get_content_comments(self, content_id: str, limit: int = 25, start: int = 0) -> Dict[str, Any]:
        """Get comments for content.
        
        Args:
            content_id: The content ID
            limit: Maximum number of comments to return
            start: Index of the first comment to return
            
        Returns:
            Dictionary containing comments and pagination information"""
        return self.get_content_children(content_id, "comment", limit, start)
    
    def get_content_attachments(self, content_id: str, limit: int = 25, start: int = 0) -> Dict[str, Any]:
        """Get attachments for content.
        
        Args:
            content_id: The content ID
            limit: Maximum number of attachments to return
            start: Index of the first attachment to return
            
        Returns:
            Dictionary containing attachments and pagination information"""
        return self.get_content_children(content_id, "attachment", limit, start)
    
    def add_attachment(
        self, 
        content_id: str, 
        file_path: str, 
        filename: Optional[str] = None, 
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add an attachment to content.
        
        Args:
            content_id: The content ID
            file_path: Path to the file to attach
            filename: Optional filename to use (defaults to the file's basename)
            comment: Optional comment for the attachment
            
        Returns:
            Created attachment information"""
        import os
        
        if not filename:
            filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            data = {}
            
            if comment:
                data['comment'] = comment
            
            status_code, response = self._make_request(
                'POST', 
                f'content/{content_id}/child/attachment', 
                data=data,
                files=files
            )
        
        if status_code != 200:
            raise ConfluenceApiError(f"Failed to add attachment to content {content_id}", status_code, response)
        
        return response
    
    def search(self, cql: str, limit: int = 25, start: int = 0) -> Dict[str, Any]:
        """Search Confluence using CQL.
        
        Args:
            cql: Confluence Query Language string
            limit: Maximum number of results to return
            start: Index of the first result to return
            
        Returns:
            Dictionary containing search results and pagination information"""
        params = {
            "cql": cql,
            "limit": limit,
            "start": start
        }
        
        status_code, response = self._make_request('GET', 'content/search', params=params)
        
        if status_code != 200:
            raise ConfluenceApiError("Failed to search content", status_code, response)
        
        return response
    
    def convert_to_confluence_space(self, space: ConfluenceSpace) -> Dict[str, Any]:
        """Convert a ConfluenceSpace model to Confluence API format.
        
        Args:
            space: ConfluenceSpace model
            
        Returns:
            Confluence API space data"""
        return {
            "key": space.key,
            "name": space.name,
            "description": {
                "plain": {
                    "value": space.description,
                    "representation": "plain"
                }
            },
            "type": space.type
        }
    
    def convert_to_confluence_page(self, page: ConfluencePage) -> Dict[str, Any]:
        """Convert a ConfluencePage model to Confluence API format.
        
        Args:
            page: ConfluencePage model
            
        Returns:
            Confluence API page data"""
        data = {
            "type": "page",
            "title": page.title,
            "space": {
                "key": page.space_id
            },
            "body": {
                "storage": {
                    "value": page.body,
                    "representation": "storage"
                }
            },
            "version": {
                "number": page.version
            }
        }
        
        if page.parent_id:
            data["ancestors"] = [{"id": page.parent_id}]
        
        return data
    
    def convert_to_confluence_comment(self, comment: ConfluenceComment) -> Dict[str, Any]:
        """Convert a ConfluenceComment model to Confluence API format.
        
        Args:
            comment: ConfluenceComment model
            
        Returns:
            Confluence API comment data"""
        data = {
            "type": "comment",
            "container": {
                "id": comment.page_id,
                "type": "page"
            },
            "body": {
                "storage": {
                    "value": comment.body,
                    "representation": "storage"
                }
            }
        }
        
        if comment.parent_comment_id:
            data["ancestors"] = [{"id": comment.parent_comment_id}]
        
        return data
    
    def convert_from_confluence_space(self, confluence_space: Dict[str, Any]) -> ConfluenceSpace:
        """Convert Confluence API space data to ConfluenceSpace model.
        
        Args:
            confluence_space: Confluence API space data
            
        Returns:
            ConfluenceSpace model"""
        # Extract description from the potentially complex structure
        description = ""
        if "description" in confluence_space:
            if "plain" in confluence_space["description"]:
                description = confluence_space["description"]["plain"].get("value", "")
            elif "view" in confluence_space["description"]:
                description = confluence_space["description"]["view"].get("value", "")
        
        space = ConfluenceSpace(
            external_id=confluence_space.get("id"),
            key=confluence_space.get("key", ""),
            name=confluence_space.get("name", ""),
            description=description,
            type=confluence_space.get("type", ""),
            status=confluence_space.get("status", ""),
            homepage_id=confluence_space.get("homepage", {}).get("id"),
            sync_status=SyncStatus.COMPLETED,
            last_sync_time=datetime.now()
        )
        
        return space
    
    def convert_from_confluence_page(self, confluence_page: Dict[str, Any]) -> ConfluencePage:
        """Convert Confluence API page data to ConfluencePage model.
        
        Args:
            confluence_page: Confluence API page data
            
        Returns:
            ConfluencePage model"""
        # Extract body content from the potentially complex structure
        body = ""
        if "body" in confluence_page:
            if "storage" in confluence_page["body"]:
                body = confluence_page["body"]["storage"].get("value", "")
            elif "view" in confluence_page["body"]:
                body = confluence_page["body"]["view"].get("value", "")
        
        # Parse dates
        created = None
        updated = None
        
        if "history" in confluence_page:
            if "createdDate" in confluence_page["history"]:
                try:
                    created = datetime.fromisoformat(
                        confluence_page["history"]["createdDate"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass
            
            if "lastUpdated" in confluence_page["history"]:
                if "when" in confluence_page["history"]["lastUpdated"]:
                    try:
                        updated = datetime.fromisoformat(
                            confluence_page["history"]["lastUpdated"]["when"].replace("Z", "+00:00")
                        )
                    except (ValueError, AttributeError):
                        pass
        
        # Get parent ID if available
        parent_id = None
        if "ancestors" in confluence_page and confluence_page["ancestors"]:
            # Get the last ancestor (immediate parent)
            parent_id = confluence_page["ancestors"][-1].get("id")
        
        # Get space key
        space_id = ""
        if "space" in confluence_page and "key" in confluence_page["space"]:
            space_id = confluence_page["space"]["key"]
        
        page = ConfluencePage(
            external_id=confluence_page.get("id"),
            space_id=space_id,
            title=confluence_page.get("title", ""),
            body=body,
            version=confluence_page.get("version", {}).get("number", 1),
            parent_id=parent_id,
            creator=confluence_page.get("history", {}).get("createdBy", {}).get("accountId", ""),
            created=created,
            last_updater=confluence_page.get("history", {}).get("lastUpdated", {}).get("by", {}).get("accountId", ""),
            last_updated=updated,
            status=confluence_page.get("status", ""),
            sync_status=SyncStatus.COMPLETED,
            last_sync_time=datetime.now()
        )
        
        return page
    
    def convert_from_confluence_comment(self, confluence_comment: Dict[str, Any]) -> ConfluenceComment:
        """Convert Confluence API comment data to ConfluenceComment model.
        
        Args:
            confluence_comment: Confluence API comment data
            
        Returns:
            ConfluenceComment model"""
        # Extract body content from the potentially complex structure
        body = ""
        if "body" in confluence_comment:
            if "storage" in confluence_comment["body"]:
                body = confluence_comment["body"]["storage"].get("value", "")
            elif "view" in confluence_comment["body"]:
                body = confluence_comment["body"]["view"].get("value", "")
        
        # Parse dates
        created = None
        updated = None
        
        if "history" in confluence_comment:
            if "createdDate" in confluence_comment["history"]:
                try:
                    created = datetime.fromisoformat(
                        confluence_comment["history"]["createdDate"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass
            
            if "lastUpdated" in confluence_comment["history"]:
                if "when" in confluence_comment["history"]["lastUpdated"]:
                    try:
                        updated = datetime.fromisoformat(
                            confluence_comment["history"]["lastUpdated"]["when"].replace("Z", "+00:00")
                        )
                    except (ValueError, AttributeError):
                        pass
        
        # Get parent comment ID if available
        parent_comment_id = None
        if "ancestors" in confluence_comment and confluence_comment["ancestors"]:
            # Get the last ancestor (immediate parent)
            parent_comment_id = confluence_comment["ancestors"][-1].get("id")
        
        # Get page ID
        page_id = ""
        if "container" in confluence_comment and "id" in confluence_comment["container"]:
            page_id = confluence_comment["container"]["id"]
        
        comment = ConfluenceComment(
            external_id=confluence_comment.get("id"),
            page_id=page_id,
            author=confluence_comment.get("history", {}).get("createdBy", {}).get("accountId", ""),
            body=body,
            created=created,
            updated=updated,
            parent_comment_id=parent_comment_id,
            sync_status=SyncStatus.COMPLETED,
            last_sync_time=datetime.now()
        )
        
        return comment
    
    def convert_from_confluence_attachment(self, confluence_attachment: Dict[str, Any]) -> ConfluenceAttachment:
        """Convert Confluence API attachment data to ConfluenceAttachment model.
        
        Args:
            confluence_attachment: Confluence API attachment data
            
        Returns:
            ConfluenceAttachment model"""
        # Parse dates
        created = None
        
        if "history" in confluence_attachment:
            if "createdDate" in confluence_attachment["history"]:
                try:
                    created = datetime.fromisoformat(
                        confluence_attachment["history"]["createdDate"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass
        
        # Get page ID
        page_id = ""
        if "container" in confluence_attachment and "id" in confluence_attachment["container"]:
            page_id = confluence_attachment["container"]["id"]
        
        attachment = ConfluenceAttachment(
            external_id=confluence_attachment.get("id"),
            page_id=page_id,
            filename=confluence_attachment.get("title", ""),
            content_type=confluence_attachment.get("metadata", {}).get("mediaType", ""),
            size=confluence_attachment.get("extensions", {}).get("fileSize", 0),
            creator=confluence_attachment.get("history", {}).get("createdBy", {}).get("accountId", ""),
            created=created,
            url=confluence_attachment.get("_links", {}).get("download", ""),
            sync_status=SyncStatus.COMPLETED,
            last_sync_time=datetime.now()
        )
        
        return attachment
