"""TORONTO AI TEAM AGENT - Coursera API Integration

This module provides integration with the Coursera API for accessing course content
and training materials to enhance agent knowledge and capabilities.

Copyright (c) 2025 TORONTO AI
Created by David Tadeusz Chudak
All rights reserved."""

import os
import json
import logging
import time
import base64
import requests
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CourseraAPIError(Exception):
    """Exception raised for Coursera API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"{message} - Status: {status_code}, Response: {response_text}")


class CourseraConfig:
    """Configuration for Coursera API integration."""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        business_id: Optional[str] = None,
        base_url: str = "https://api.coursera.com",
        token_url: str = "https://api.coursera.com/oauth2/client_credentials/token",
        max_retries: int = 3,
        timeout: int = 30,
        token_cache_path: Optional[str] = None
    ):
        """Initialize Coursera API configuration.
        
        Args:
            api_key: Coursera API key
            api_secret: Coursera API secret
            business_id: Coursera Business ID (optional)
            base_url: Base URL for API requests
            token_url: URL for token requests
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
            token_cache_path: Path to cache access tokens (optional)"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.business_id = business_id
        self.base_url = base_url
        self.token_url = token_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.token_cache_path = token_cache_path


class CourseraTokenManager:
    """Manager for Coursera API access tokens."""
    
    def __init__(self, config: CourseraConfig):
        """Initialize the token manager.
        
        Args:
            config: Coursera API configuration"""
        self.config = config
        self._access_token = None
        self._token_expiry = None
        self._load_cached_token()
    
    def _load_cached_token(self) -> None:
        """Load cached token if available."""
        if not self.config.token_cache_path or not os.path.exists(self.config.token_cache_path):
            return
        
        try:
            with open(self.config.token_cache_path, 'r') as f:
                token_data = json.load(f)
                
                if 'access_token' in token_data and 'expiry' in token_data:
                    expiry = datetime.fromisoformat(token_data['expiry'])
                    
                    # Add a buffer to ensure we refresh before actual expiry
                    if expiry > datetime.now() + timedelta(minutes=5):
                        self._access_token = token_data['access_token']
                        self._token_expiry = expiry
                        logger.info("Loaded cached Coursera API token")
        except Exception as e:
            logger.warning(f"Failed to load cached token: {str(e)}")
    
    def _save_token_to_cache(self) -> None:
        """Save token to cache if cache path is configured."""
        if not self.config.token_cache_path:
            return
        
        try:
            token_data = {
                'access_token': self._access_token,
                'expiry': self._token_expiry.isoformat()
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config.token_cache_path), exist_ok=True)
            
            with open(self.config.token_cache_path, 'w') as f:
                json.dump(token_data, f)
                
            logger.info("Saved Coursera API token to cache")
        except Exception as e:
            logger.warning(f"Failed to save token to cache: {str(e)}")
    
    def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary.
        
        Returns:
            Access token"""
        # Check if token is still valid
        if self._access_token and self._token_expiry and self._token_expiry > datetime.now():
            return self._access_token
        
        # Token is expired or not set, get a new one
        self._refresh_token()
        return self._access_token
    
    def _refresh_token(self) -> None:
        """Refresh the access token.
        
        Raises:
            CourseraAPIError: If token refresh fails"""
        auth_header = base64.b64encode(f"{self.config.api_key}:{self.config.api_secret}".encode()).decode()
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(
                self.config.token_url,
                headers=headers,
                data=data,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                raise CourseraAPIError(
                    "Failed to refresh access token",
                    response.status_code,
                    response.text
                )
            
            token_data = response.json()
            
            if 'access_token' not in token_data or 'expires_in' not in token_data:
                raise CourseraAPIError(
                    "Invalid token response",
                    response.status_code,
                    response.text
                )
            
            self._access_token = token_data['access_token']
            self._token_expiry = datetime.now() + timedelta(seconds=token_data['expires_in'])
            
            # Save token to cache
            self._save_token_to_cache()
            
            logger.info("Successfully refreshed Coursera API token")
            
        except requests.RequestException as e:
            raise CourseraAPIError(f"Request error during token refresh: {str(e)}")


class CourseraAPIClient:
    """Client for interacting with the Coursera API.
    Handles API requests, authentication, and error handling."""
    
    def __init__(self, config: CourseraConfig):
        """Initialize the Coursera API client.
        
        Args:
            config: Coursera API configuration"""
        self.config = config
        self.token_manager = CourseraTokenManager(config)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Make a request to the Coursera API with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request data (for POST/PUT)
            retry_count: Current retry attempt
            
        Returns:
            Response data
            
        Raises:
            CourseraAPIError: If the request fails after all retries"""
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        # Get access token
        access_token = self.token_manager.get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method == 'GET':
                response = requests.get(
                    url, 
                    headers=headers, 
                    params=params,
                    timeout=self.config.timeout
                )
            elif method == 'POST':
                response = requests.post(
                    url, 
                    headers=headers, 
                    params=params,
                    json=data,
                    timeout=self.config.timeout
                )
            elif method == 'PUT':
                response = requests.put(
                    url, 
                    headers=headers, 
                    params=params,
                    json=data,
                    timeout=self.config.timeout
                )
            elif method == 'DELETE':
                response = requests.delete(
                    url, 
                    headers=headers, 
                    params=params,
                    timeout=self.config.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle rate limiting
            if response.status_code == 429:
                if retry_count < self.config.max_retries:
                    # Get retry-after header or use exponential backoff
                    retry_after = int(response.headers.get('Retry-After', 2 ** retry_count))
                    logger.warning(f"Rate limited by Coursera API. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    return self._make_request(method, endpoint, params, data, retry_count + 1)
                else:
                    raise CourseraAPIError(
                        "Exceeded maximum retries due to rate limiting", 
                        response.status_code, 
                        response.text
                    )
            
            # Handle server errors
            if response.status_code >= 500:
                if retry_count < self.config.max_retries:
                    # Use exponential backoff
                    retry_after = 2 ** retry_count
                    logger.warning(f"Coursera API server error. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    return self._make_request(method, endpoint, params, data, retry_count + 1)
                else:
                    raise CourseraAPIError(
                        "Exceeded maximum retries due to server errors", 
                        response.status_code, 
                        response.text
                    )
            
            # Handle authentication errors
            if response.status_code in (401, 403):
                if retry_count < 1:  # Only retry once for auth errors
                    # Force token refresh
                    self.token_manager._refresh_token()
                    return self._make_request(method, endpoint, params, data, retry_count + 1)
                else:
                    raise CourseraAPIError(
                        "Authentication or authorization error", 
                        response.status_code, 
                        response.text
                    )
            
            # Handle other client errors
            if response.status_code >= 400:
                raise CourseraAPIError(
                    f"Client error: {response.status_code}", 
                    response.status_code, 
                    response.text
                )
            
            # Parse response
            if response.text:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"text": response.text}
            
            return {}
            
        except requests.RequestException as e:
            if retry_count < self.config.max_retries:
                retry_after = 2 ** retry_count
                logger.warning(f"Coursera API request failed: {str(e)}. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            else:
                raise CourseraAPIError(f"Coursera API request failed after {self.config.max_retries} retries: {str(e)}")
    
    def get_business_programs(self) -> List[Dict[str, Any]]:
        """Get all programs for the business.
        
        Returns:
            List of programs
        
        Raises:
            CourseraAPIError: If the business ID is not set or the request fails"""
        if not self.config.business_id:
            raise CourseraAPIError("Business ID is not set")
        
        response = self._make_request(
            'GET', 
            f"ent/api/businesses.v1/{self.config.business_id}/programs"
        )
        
        return response.get("elements", [])
    
    def get_program_details(self, program_id: str) -> Dict[str, Any]:
        """Get details for a specific program.
        
        Args:
            program_id: The program ID
            
        Returns:
            Program details"""
        if not self.config.business_id:
            raise CourseraAPIError("Business ID is not set")
        
        response = self._make_request(
            'GET', 
            f"ent/api/businesses.v1/{self.config.business_id}/programs/{program_id}"
        )
        
        return response
    
    def get_courses(self, program_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get courses, optionally filtered by program.
        
        Args:
            program_id: Optional program ID to filter by
            
        Returns:
            List of courses"""
        if not self.config.business_id:
            raise CourseraAPIError("Business ID is not set")
        
        endpoint = f"ent/api/businesses.v1/{self.config.business_id}/courses"
        params = {}
        
        if program_id:
            params["program_id"] = program_id
        
        response = self._make_request('GET', endpoint, params=params)
        
        return response.get("elements", [])
    
    def get_course_details(self, course_id: str) -> Dict[str, Any]:
        """Get details for a specific course.
        
        Args:
            course_id: The course ID
            
        Returns:
            Course details"""
        if not self.config.business_id:
            raise CourseraAPIError("Business ID is not set")
        
        response = self._make_request(
            'GET', 
            f"ent/api/businesses.v1/{self.config.business_id}/courses/{course_id}"
        )
        
        return response
    
    def get_course_materials(self, course_id: str) -> List[Dict[str, Any]]:
        """Get materials for a specific course.
        
        Args:
            course_id: The course ID
            
        Returns:
            List of course materials"""
        if not self.config.business_id:
            raise CourseraAPIError("Business ID is not set")
        
        response = self._make_request(
            'GET', 
            f"ent/api/businesses.v1/{self.config.business_id}/courses/{course_id}/materials"
        )
        
        return response.get("elements", [])
    
    def get_specializations(self) -> List[Dict[str, Any]]:
        """Get all specializations for the business.
        
        Returns:
            List of specializations"""
        if not self.config.business_id:
            raise CourseraAPIError("Business ID is not set")
        
        response = self._make_request(
            'GET', 
            f"ent/api/businesses.v1/{self.config.business_id}/specializations"
        )
        
        return response.get("elements", [])
    
    def get_specialization_details(self, specialization_id: str) -> Dict[str, Any]:
        """Get details for a specific specialization.
        
        Args:
            specialization_id: The specialization ID
            
        Returns:
            Specialization details"""
        if not self.config.business_id:
            raise CourseraAPIError("Business ID is not set")
        
        response = self._make_request(
            'GET', 
            f"ent/api/businesses.v1/{self.config.business_id}/specializations/{specialization_id}"
        )
        
        return response
    
    def search_courses(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for courses.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching courses"""
        if not self.config.business_id:
            raise CourseraAPIError("Business ID is not set")
        
        params = {
            "q": query,
            "limit": limit
        }
        
        response = self._make_request(
            'GET', 
            f"ent/api/businesses.v1/{self.config.business_id}/search/courses",
            params=params
        )
        
        return response.get("elements", [])


class CourseraContentExtractor:
    """Extracts and processes content from Coursera courses for agent training."""
    
    def __init__(self, api_client: CourseraAPIClient):
        """Initialize the content extractor.
        
        Args:
            api_client: Coursera API client"""
        self.api_client = api_client
    
    def extract_course_content(self, course_id: str) -> Dict[str, Any]:
        """Extract content from a course for agent training.
        
        Args:
            course_id: The course ID
            
        Returns:
            Structured course content"""
        # Get course details
        course_details = self.api_client.get_course_details(course_id)
        
        # Get course materials
        materials = self.api_client.get_course_materials(course_id)
        
        # Structure the content
        content = {
            "course_id": course_id,
            "title": course_details.get("title", ""),
            "description": course_details.get("description", ""),
            "skills": course_details.get("skills", []),
            "modules": [],
            "materials": []
        }
        
        # Process materials
        for material in materials:
            material_type = material.get("type", "")
            
            if material_type == "lecture":
                module = self._find_or_create_module(content, material.get("moduleId", ""))
                module["lectures"].append({
                    "id": material.get("id", ""),
                    "title": material.get("title", ""),
                    "content": material.get("content", ""),
                    "duration": material.get("duration", 0)
                })
            elif material_type == "reading":
                module = self._find_or_create_module(content, material.get("moduleId", ""))
                module["readings"].append({
                    "id": material.get("id", ""),
                    "title": material.get("title", ""),
                    "content": material.get("content", "")
                })
            elif material_type == "quiz":
                module = self._find_or_create_module(content, material.get("moduleId", ""))
                module["quizzes"].append({
                    "id": material.get("id", ""),
                    "title": material.get("title", ""),
                    "questions": material.get("questions", [])
                })
            else:
                content["materials"].append(material)
        
        return content
    
    def _find_or_create_module(self, content: Dict[str, Any], module_id: str) -> Dict[str, Any]:
        """Find or create a module in the content structure.
        
        Args:
            content: The content structure
            module_id: The module ID
            
        Returns:
            The module"""
        for module in content["modules"]:
            if module["id"] == module_id:
                return module
        
        # Module not found, create it
        module = {
            "id": module_id,
            "title": f"Module {len(content['modules']) + 1}",
            "lectures": [],
            "readings": [],
            "quizzes": []
        }
        
        content["modules"].append(module)
        return module
    
    def extract_specialization_content(self, specialization_id: str) -> Dict[str, Any]:
        """Extract content from a specialization for agent training.
        
        Args:
            specialization_id: The specialization ID
            
        Returns:
            Structured specialization content"""
        # Get specialization details
        specialization_details = self.api_client.get_specialization_details(specialization_id)
        
        # Structure the content
        content = {
            "specialization_id": specialization_id,
            "title": specialization_details.get("title", ""),
            "description": specialization_details.get("description", ""),
            "skills": specialization_details.get("skills", []),
            "courses": []
        }
        
        # Get courses in the specialization
        courses = specialization_details.get("courses", [])
        
        # Extract content for each course
        for course in courses:
            course_id = course.get("id", "")
            if course_id:
                course_content = self.extract_course_content(course_id)
                content["courses"].append(course_content)
        
        return content
    
    def search_and_extract_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for courses and extract content.
        
        Args:
            query: Search query
            limit: Maximum number of courses to process
            
        Returns:
            List of structured course content"""
        # Search for courses
        courses = self.api_client.search_courses(query, limit=limit)
        
        # Extract content for each course
        content_list = []
        for course in courses[:limit]:
            course_id = course.get("id", "")
            if course_id:
                try:
                    course_content = self.extract_course_content(course_id)
                    content_list.append(course_content)
                except CourseraAPIError as e:
                    logger.warning(f"Failed to extract content for course {course_id}: {str(e)}")
        
        return content_list


class CourseraKnowledgePipeline:
    """Pipeline for integrating Coursera content into agent training."""
    
    def __init__(self, content_extractor: CourseraContentExtractor):
        """Initialize the knowledge pipeline.
        
        Args:
            content_extractor: Coursera content extractor"""
        self.content_extractor = content_extractor
    
    def process_course_for_role(
        self, 
        course_id: str, 
        role: str,
        output_dir: str
    ) -> str:
        """Process a course for a specific agent role.
        
        Args:
            course_id: The course ID
            role: The agent role
            output_dir: Directory to save processed content
            
        Returns:
            Path to the processed content file"""
        # Extract course content
        content = self.content_extractor.extract_course_content(course_id)
        
        # Create role-specific directory
        role_dir = os.path.join(output_dir, role)
        os.makedirs(role_dir, exist_ok=True)
        
        # Generate a filename based on course title
        filename = f"{content['title'].lower().replace(' ', '_')}.json"
        filepath = os.path.join(role_dir, filename)
        
        # Save the content
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=2)
        
        return filepath
    
    def process_specialization_for_role(
        self, 
        specialization_id: str, 
        role: str,
        output_dir: str
    ) -> List[str]:
        """Process a specialization for a specific agent role.
        
        Args:
            specialization_id: The specialization ID
            role: The agent role
            output_dir: Directory to save processed content
            
        Returns:
            List of paths to the processed content files"""
        # Extract specialization content
        content = self.content_extractor.extract_specialization_content(specialization_id)
        
        # Create role-specific directory
        role_dir = os.path.join(output_dir, role)
        os.makedirs(role_dir, exist_ok=True)
        
        # Generate a filename for the specialization
        spec_filename = f"{content['title'].lower().replace(' ', '_')}_specialization.json"
        spec_filepath = os.path.join(role_dir, spec_filename)
        
        # Save the specialization content
        with open(spec_filepath, 'w') as f:
            json.dump(content, f, indent=2)
        
        # Process each course in the specialization
        course_filepaths = [spec_filepath]
        for course_content in content["courses"]:
            course_filename = f"{course_content['title'].lower().replace(' ', '_')}.json"
            course_filepath = os.path.join(role_dir, course_filename)
            
            # Save the course content
            with open(course_filepath, 'w') as f:
                json.dump(course_content, f, indent=2)
            
            course_filepaths.append(course_filepath)
        
        return course_filepaths
    
    def search_and_process_for_role(
        self, 
        query: str, 
        role: str,
        output_dir: str,
        limit: int = 5
    ) -> List[str]:
        """Search for courses and process them for a specific agent role.
        
        Args:
            query: Search query
            role: The agent role
            output_dir: Directory to save processed content
            limit: Maximum number of courses to process
            
        Returns:
            List of paths to the processed content files"""
        # Extract content from search results
        content_list = self.content_extractor.search_and_extract_content(query, limit=limit)
        
        # Create role-specific directory
        role_dir = os.path.join(output_dir, role)
        os.makedirs(role_dir, exist_ok=True)
        
        # Process each course
        filepaths = []
        for content in content_list:
            filename = f"{content['title'].lower().replace(' ', '_')}.json"
            filepath = os.path.join(role_dir, filename)
            
            # Save the content
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=2)
            
            filepaths.append(filepath)
        
        return filepaths
    
    def generate_knowledge_base_for_role(
        self, 
        role: str,
        queries: List[str],
        output_dir: str,
        limit_per_query: int = 3
    ) -> Dict[str, Any]:
        """Generate a comprehensive knowledge base for a specific agent role.
        
        Args:
            role: The agent role
            queries: List of search queries relevant to the role
            output_dir: Directory to save processed content
            limit_per_query: Maximum number of courses to process per query
            
        Returns:
            Summary of the generated knowledge base"""
        # Create role-specific directory
        role_dir = os.path.join(output_dir, role)
        os.makedirs(role_dir, exist_ok=True)
        
        # Process each query
        all_filepaths = []
        for query in queries:
            filepaths = self.search_and_process_for_role(
                query, role, output_dir, limit=limit_per_query
            )
            all_filepaths.extend(filepaths)
        
        # Generate a summary file
        summary = {
            "role": role,
            "queries": queries,
            "total_courses": len(all_filepaths),
            "courses": []
        }
        
        # Add details for each course
        for filepath in all_filepaths:
            try:
                with open(filepath, 'r') as f:
                    content = json.load(f)
                    
                    summary["courses"].append({
                        "title": content.get("title", ""),
                        "course_id": content.get("course_id", ""),
                        "skills": content.get("skills", []),
                        "filepath": filepath
                    })
            except Exception as e:
                logger.warning(f"Failed to read course content from {filepath}: {str(e)}")
        
        # Save the summary
        summary_filepath = os.path.join(role_dir, f"{role}_knowledge_base_summary.json")
        with open(summary_filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary


def create_role_specific_queries() -> Dict[str, List[str]]:
    """Create role-specific search queries for the knowledge pipeline.
    
    Returns:
        Dictionary mapping roles to lists of search queries"""
    return {
        "project_manager": [
            "project management fundamentals",
            "agile project management",
            "project planning and scheduling",
            "risk management in projects",
            "project stakeholder management",
            "project leadership",
            "project management tools",
            "project management certification"
        ],
        "business_analyst": [
            "business analysis fundamentals",
            "requirements gathering techniques",
            "business process modeling",
            "data analysis for business",
            "business intelligence",
            "stakeholder analysis",
            "business case development",
            "business analysis certification"
        ],
        "data_scientist": [
            "data science fundamentals",
            "machine learning algorithms",
            "statistical analysis",
            "data visualization",
            "big data analytics",
            "predictive modeling",
            "natural language processing",
            "deep learning"
        ],
        "software_engineer": [
            "software development fundamentals",
            "object-oriented programming",
            "software architecture",
            "web development",
            "mobile app development",
            "database design",
            "software testing",
            "devops practices"
        ],
        "ux_designer": [
            "user experience design",
            "user interface design",
            "user research methods",
            "interaction design",
            "usability testing",
            "information architecture",
            "design thinking",
            "prototyping tools"
        ],
        "product_manager": [
            "product management fundamentals",
            "product strategy",
            "product roadmap planning",
            "market research",
            "product metrics and analytics",
            "product launch",
            "customer development",
            "product management certification"
        ]
    }


def initialize_coursera_integration(
    api_key: str,
    api_secret: str,
    business_id: Optional[str] = None,
    token_cache_path: Optional[str] = None
) -> CourseraKnowledgePipeline:
    """Initialize the Coursera integration.
    
    Args:
        api_key: Coursera API key
        api_secret: Coursera API secret
        business_id: Coursera Business ID (optional)
        token_cache_path: Path to cache access tokens (optional)
        
    Returns:
        Initialized knowledge pipeline"""
    # Create configuration
    config = CourseraConfig(
        api_key=api_key,
        api_secret=api_secret,
        business_id=business_id,
        token_cache_path=token_cache_path
    )
    
    # Create API client
    api_client = CourseraAPIClient(config)
    
    # Create content extractor
    content_extractor = CourseraContentExtractor(api_client)
    
    # Create knowledge pipeline
    knowledge_pipeline = CourseraKnowledgePipeline(content_extractor)
    
    return knowledge_pipeline
