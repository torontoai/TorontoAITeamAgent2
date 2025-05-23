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

"""Optimized Confluence Client

This module provides an optimized implementation of the Confluence client
with caching and connection pooling for improved performance."""

import logging
import time
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Set
from datetime import datetime, timedelta

from app.core.cache import cached, get_default_cache, Cache
from app.core.connection_pool import get_pool_manager, ConnectionPool
from app.integration.auth import AuthenticationManager
from app.integration.models import ConfluencePage, ConfluenceSpace, ConfluenceAttachment, ConfluenceUser

logger = logging.getLogger(__name__)

class OptimizedConfluenceClient:
    """Optimized Confluence client with caching and connection pooling."""
    
    def __init__(self, base_url: str, auth_manager: AuthenticationManager, cache: Cache = None):
        """Initialize the optimized Confluence client.
        
        Args:
            base_url: Confluence API base URL
            auth_manager: Authentication manager
            cache: Cache instance (None for default)"""
        self.base_url = base_url
        self.auth_manager = auth_manager
        self.cache = cache or get_default_cache()
        self._setup_connection_pool()
        logger.info(f"Initialized optimized Confluence client for {base_url}")
    
    def _setup_connection_pool(self):
        """Set up connection pool for Confluence API connections."""
        try:
            pool_manager = get_pool_manager()
            
            # Create connection factory
            def create_connection():
                import requests
                session = requests.Session()
                # Add authentication headers
                headers = self.auth_manager.get_confluence_auth_headers()
                session.headers.update(headers)
                return session
            
            # Create connection validator
            def validate_connection(session):
                try:
                    # Make a lightweight request to validate the connection
                    response = session.get(f"{self.base_url}/rest/api/user/current", timeout=5)
                    return response.status_code == 200
                except Exception:
                    return False
            
            # Create connection cleanup
            def cleanup_connection(session):
                session.close()
            
            # Create connection pool
            self.connection_pool = pool_manager.create_pool(
                name=f"confluence_{self.base_url}",
                factory=create_connection,
                validator=validate_connection,
                cleanup=cleanup_connection,
                min_size=2,
                max_size=10
            )
            
            logger.info("Created connection pool for Confluence API")
        except Exception as e:
            logger.warning(f"Failed to create connection pool for Confluence API: {str(e)}")
            self.connection_pool = None
    
    def _get_connection(self):
        """Get a connection from the pool or create a new session.
        
        Returns:
            Requests session"""
        if self.connection_pool:
            try:
                return self.connection_pool.get_connection()
            except Exception as e:
                logger.warning(f"Failed to get connection from pool: {str(e)}")
        
        # Fallback to creating a new session
        import requests
        session = requests.Session()
        headers = self.auth_manager.get_confluence_auth_headers()
        session.headers.update(headers)
        return session
    
    def _return_connection(self, session):
        """Return a connection to the pool or close it.
        
        Args:
            session: Requests session"""
        if self.connection_pool:
            try:
                self.connection_pool.return_connection(session)
                return
            except Exception as e:
                logger.warning(f"Failed to return connection to pool: {str(e)}")
        
        # Fallback to closing the session
        session.close()
    
    @cached(ttl=600)
    async def get_spaces(self, limit: int = 100, start: int = 0) -> Dict[str, Any]:
        """
        Get all spaces with caching.
        
        Args:
            limit: Maximum number of spaces to return
            start: Start index
            
        Returns:
            Dictionary with spaces and pagination info
        """
        session = self._get_connection()
        try:
            params = {
                "limit": limit,
                "start": start
            }
            
            response = session.get(f"{self.base_url}/rest/api/space", params=params)
            response.raise_for_status()
            
            spaces_data = response.json()
            
            # Convert spaces to model objects
            spaces = []
            for space_data in spaces_data.get("results", []):
                spaces.append(ConfluenceSpace.from_dict(space_data))
            
            return {
                "spaces": spaces,
                "size": spaces_data.get("size", 0),
                "limit": spaces_data.get("limit", 0),
                "start": spaces_data.get("start", 0)
            }
        except Exception as e:
            logger.error(f"Error getting spaces: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=600)
    async def get_space(self, space_key: str) -> Optional[ConfluenceSpace]:
        """
        Get a space by key with caching.
        
        Args:
            space_key: Space key
            
        Returns:
            Confluence space or None if not found
        """
        session = self._get_connection()
        try:
            response = session.get(f"{self.base_url}/rest/api/space/{space_key}")
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            
            space_data = response.json()
            space = ConfluenceSpace.from_dict(space_data)
            
            return space
        except Exception as e:
            logger.error(f"Error getting space {space_key}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=300)
    async def search_content(self, cql: str, limit: int = 50, start: int = 0) -> Dict[str, Any]:
        """
        Search content with caching.
        
        Args:
            cql: CQL query
            limit: Maximum number of results
            start: Start index
            
        Returns:
            Search results
        """
        session = self._get_connection()
        try:
            params = {
                "cql": cql,
                "limit": limit,
                "start": start,
                "expand": "space,version,body.view"
            }
            
            response = session.get(f"{self.base_url}/rest/api/content/search", params=params)
            response.raise_for_status()
            
            search_data = response.json()
            
            # Convert pages to model objects
            pages = []
            for page_data in search_data.get("results", []):
                pages.append(ConfluencePage.from_dict(page_data))
            
            return {
                "pages": pages,
                "size": search_data.get("size", 0),
                "limit": search_data.get("limit", 0),
                "start": search_data.get("start", 0)
            }
        except Exception as e:
            logger.error(f"Error searching content with CQL {cql}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=300)
    async def get_page(self, page_id: str) -> Optional[ConfluencePage]:
        """
        Get a page by ID with caching.
        
        Args:
            page_id: Page ID
            
        Returns:
            Confluence page or None if not found
        """
        session = self._get_connection()
        try:
            response = session.get(
                f"{self.base_url}/rest/api/content/{page_id}",
                params={"expand": "space,version,body.view,ancestors"}
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            
            page_data = response.json()
            page = ConfluencePage.from_dict(page_data)
            
            return page
        except Exception as e:
            logger.error(f"Error getting page {page_id}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    async def create_page(self, space_key: str, title: str, content: str, parent_id: str = None) -> ConfluencePage:
        """
        Create a new page.
        
        Args:
            space_key: Space key
            title: Page title
            content: Page content (HTML)
            parent_id: Parent page ID (None for root page)
            
        Returns:
            Created Confluence page
        """
        session = self._get_connection()
        try:
            page_data = {
                "type": "page",
                "title": title,
                "space": {"key": space_key},
                "body": {
                    "storage": {
                        "value": content,
                        "representation": "storage"
                    }
                }
            }
            
            if parent_id:
                page_data["ancestors"] = [{"id": parent_id}]
            
            response = session.post(
                f"{self.base_url}/rest/api/content",
                json=page_data
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Get the created page
            page_id = result.get("id")
            page = await self.get_page(page_id)
            
            # Invalidate relevant caches
            self._invalidate_page_caches(page)
            
            return page
        except Exception as e:
            logger.error(f"Error creating page in space {space_key}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    async def update_page(self, page_id: str, title: str, content: str, version: int) -> Optional[ConfluencePage]:
        """
        Update a page.
        
        Args:
            page_id: Page ID
            title: Page title
            content: Page content (HTML)
            version: Current page version
            
        Returns:
            Updated Confluence page or None if failed
        """
        session = self._get_connection()
        try:
            page_data = {
                "type": "page",
                "title": title,
                "body": {
                    "storage": {
                        "value": content,
                        "representation": "storage"
                    }
                },
                "version": {
                    "number": version + 1
                }
            }
            
            response = session.put(
                f"{self.base_url}/rest/api/content/{page_id}",
                json=page_data
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            
            result = response.json()
            
            # Get the updated page
            page = await self.get_page(page_id)
            
            # Invalidate caches
            self._invalidate_page_caches(page)
            
            return page
        except Exception as e:
            logger.error(f"Error updating page {page_id}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=300)
    async def get_attachments(self, page_id: str) -> List[ConfluenceAttachment]:
        """
        Get attachments for a page with caching.
        
        Args:
            page_id: Page ID
            
        Returns:
            List of Confluence attachments
        """
        session = self._get_connection()
        try:
            response = session.get(f"{self.base_url}/rest/api/content/{page_id}/child/attachment")
            
            if response.status_code == 404:
                return []
            
            response.raise_for_status()
            
            attachments_data = response.json()
            attachments = [ConfluenceAttachment.from_dict(data) for data in attachments_data.get("results", [])]
            
            return attachments
        except Exception as e:
            logger.error(f"Error getting attachments for page {page_id}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=3600)
    async def get_user(self, username: str) -> Optional[ConfluenceUser]:
        """
        Get a user by username with caching.
        
        Args:
            username: Username
            
        Returns:
            Confluence user or None if not found
        """
        session = self._get_connection()
        try:
            response = session.get(f"{self.base_url}/rest/api/user", params={"username": username})
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            
            user_data = response.json()
            user = ConfluenceUser.from_dict(user_data)
            
            return user
        except Exception as e:
            logger.error(f"Error getting user {username}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    def _invalidate_page_caches(self, page: ConfluencePage):
        """Invalidate caches related to a page.
        
        Args:
            page: Confluence page"""
        if page and page.id:
            self.cache.delete(f"get_page:{page.id}")
            self.cache.delete(f"get_attachments:{page.id}")
        
        if page and page.space and page.space.key:
            self.cache.delete(f"get_space:{page.space.key}")
        
        self._invalidate_search_caches()
    
    def _invalidate_search_caches(self):
        """Invalidate search caches."""
        # This is a simplistic approach; in a real implementation,
        # we would need a more sophisticated cache invalidation strategy
        keys_to_delete = []
        for key in dir(self.cache):
            if key.startswith("search_content:"):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.cache.delete(key)
    
    def clear_cache(self):
        """Clear all caches."""
        self.cache.clear()
        logger.info("Cleared Confluence client cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics.
        
        Returns:
            Client statistics"""
        stats = {
            "cache": self.cache.stats()
        }
        
        # Add connection pool stats if available
        if self.connection_pool:
            try:
                pool_manager = get_pool_manager()
                pool_stats = pool_manager.stats()
                if f"confluence_{self.base_url}" in pool_stats:
                    stats["connection_pool"] = pool_stats[f"confluence_{self.base_url}"]
            except Exception:
                pass
        
        return stats
