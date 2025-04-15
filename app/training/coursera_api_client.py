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

"""Optimized Coursera API Client

This module provides an optimized implementation of the Coursera API client
with caching and connection pooling for improved performance."""

import logging
import time
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Set
from datetime import datetime, timedelta

from app.core.cache import cached, get_default_cache, Cache
from app.core.connection_pool import get_pool_manager, ConnectionPool

logger = logging.getLogger(__name__)

class CourseraAPIClient:
    """Optimized Coursera API client with caching and connection pooling."""
    
    def __init__(self, api_key: str, api_secret: str, cache: Cache = None):
        """Initialize the optimized Coursera API client.
        
        Args:
            api_key: Coursera API key
            api_secret: Coursera API secret
            cache: Cache instance (None for default)"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.coursera.org/api"
        self.cache = cache or get_default_cache()
        self._setup_connection_pool()
        logger.info("Initialized optimized Coursera API client")
    
    def _setup_connection_pool(self):
        """Set up connection pool for Coursera API connections."""
        try:
            pool_manager = get_pool_manager()
            
            # Create connection factory
            def create_connection():
                import requests
                session = requests.Session()
                # Add authentication
                session.auth = (self.api_key, self.api_secret)
                return session
            
            # Create connection validator
            def validate_connection(session):
                try:
                    # Make a lightweight request to validate the connection
                    response = session.get(f"{self.base_url}/partners/v1/partners", timeout=5)
                    return response.status_code == 200
                except Exception:
                    return False
            
            # Create connection cleanup
            def cleanup_connection(session):
                session.close()
            
            # Create connection pool
            self.connection_pool = pool_manager.create_pool(
                name="coursera_api",
                factory=create_connection,
                validator=validate_connection,
                cleanup=cleanup_connection,
                min_size=2,
                max_size=10
            )
            
            logger.info("Created connection pool for Coursera API")
        except Exception as e:
            logger.warning(f"Failed to create connection pool for Coursera API: {str(e)}")
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
        session.auth = (self.api_key, self.api_secret)
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
    
    @cached(ttl=3600)
    def get_courses(self, fields: List[str] = None, includes: List[str] = None, 
                   q: str = None, start: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Get courses with caching.
        
        Args:
            fields: Fields to include in the response
            includes: Related resources to include
            q: Search query
            start: Start index
            limit: Maximum number of results
            
        Returns:
            Dictionary with courses and pagination info"""
        session = self._get_connection()
        try:
            params = {
                "start": start,
                "limit": limit
            }
            
            if fields:
                params["fields"] = ",".join(fields)
            
            if includes:
                params["includes"] = ",".join(includes)
            
            if q:
                params["q"] = q
            
            response = session.get(f"{self.base_url}/courses.v1", params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting courses: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=3600)
    def get_course(self, course_id: str, fields: List[str] = None, includes: List[str] = None) -> Dict[str, Any]:
        """Get a course by ID with caching.
        
        Args:
            course_id: Course ID
            fields: Fields to include in the response
            includes: Related resources to include
            
        Returns:
            Course data"""
        session = self._get_connection()
        try:
            params = {}
            
            if fields:
                params["fields"] = ",".join(fields)
            
            if includes:
                params["includes"] = ",".join(includes)
            
            response = session.get(f"{self.base_url}/courses.v1/{course_id}", params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting course {course_id}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=3600)
    def get_specializations(self, fields: List[str] = None, includes: List[str] = None,
                           q: str = None, start: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Get specializations with caching.
        
        Args:
            fields: Fields to include in the response
            includes: Related resources to include
            q: Search query
            start: Start index
            limit: Maximum number of results
            
        Returns:
            Dictionary with specializations and pagination info"""
        session = self._get_connection()
        try:
            params = {
                "start": start,
                "limit": limit
            }
            
            if fields:
                params["fields"] = ",".join(fields)
            
            if includes:
                params["includes"] = ",".join(includes)
            
            if q:
                params["q"] = q
            
            response = session.get(f"{self.base_url}/onDemandSpecializations.v1", params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting specializations: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=3600)
    def get_specialization(self, specialization_id: str, fields: List[str] = None, 
                          includes: List[str] = None) -> Dict[str, Any]:
        """Get a specialization by ID with caching.
        
        Args:
            specialization_id: Specialization ID
            fields: Fields to include in the response
            includes: Related resources to include
            
        Returns:
            Specialization data"""
        session = self._get_connection()
        try:
            params = {}
            
            if fields:
                params["fields"] = ",".join(fields)
            
            if includes:
                params["includes"] = ",".join(includes)
            
            response = session.get(f"{self.base_url}/onDemandSpecializations.v1/{specialization_id}", params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting specialization {specialization_id}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=3600)
    def get_course_materials(self, course_id: str, fields: List[str] = None) -> Dict[str, Any]:
        """Get course materials with caching.
        
        Args:
            course_id: Course ID
            fields: Fields to include in the response
            
        Returns:
            Course materials data"""
        session = self._get_connection()
        try:
            params = {}
            
            if fields:
                params["fields"] = ",".join(fields)
            
            response = session.get(f"{self.base_url}/onDemandCourseMaterials.v1/?courseId={course_id}", params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting course materials for course {course_id}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=3600)
    def get_course_lessons(self, course_id: str, fields: List[str] = None) -> Dict[str, Any]:
        """Get course lessons with caching.
        
        Args:
            course_id: Course ID
            fields: Fields to include in the response
            
        Returns:
            Course lessons data"""
        session = self._get_connection()
        try:
            params = {}
            
            if fields:
                params["fields"] = ",".join(fields)
            
            response = session.get(f"{self.base_url}/onDemandCourseLessons.v1/?courseId={course_id}", params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting course lessons for course {course_id}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=3600)
    def search_courses(self, query: str, start: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Search courses with caching.
        
        Args:
            query: Search query
            start: Start index
            limit: Maximum number of results
            
        Returns:
            Search results"""
        session = self._get_connection()
        try:
            params = {
                "q": query,
                "start": start,
                "limit": limit
            }
            
            response = session.get(f"{self.base_url}/courses.v1", params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error searching courses with query {query}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    @cached(ttl=3600)
    def get_instructors(self, course_id: str, fields: List[str] = None) -> Dict[str, Any]:
        """Get course instructors with caching.
        
        Args:
            course_id: Course ID
            fields: Fields to include in the response
            
        Returns:
            Instructors data"""
        session = self._get_connection()
        try:
            params = {
                "courseId": course_id
            }
            
            if fields:
                params["fields"] = ",".join(fields)
            
            response = session.get(f"{self.base_url}/instructors.v1", params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting instructors for course {course_id}: {str(e)}")
            raise
        finally:
            self._return_connection(session)
    
    def clear_cache(self):
        """Clear all caches."""
        self.cache.clear()
        logger.info("Cleared Coursera API client cache")
    
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
                if "coursera_api" in pool_stats:
                    stats["connection_pool"] = pool_stats["coursera_api"]
            except Exception:
                pass
        
        return stats
