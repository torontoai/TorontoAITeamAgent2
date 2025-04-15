"""TORONTO AI TEAM AGENT - Jira API Client

This module provides a client for interacting with the Jira API.

Copyright (c) 2025 TORONTO AI
Created by David Tadeusz Chudak
All rights reserved."""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
import requests
from requests.exceptions import RequestException, Timeout

from .config import JiraConfig
from .auth import token_manager
from .models import (
    JiraProject, JiraIssue, JiraComment, JiraAttachment, JiraWorklog,
    SyncStatus, SyncDirection
)


logger = logging.getLogger(__name__)


class JiraApiError(Exception):
    """Exception raised for Jira API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"{message} - Status: {status_code}, Response: {response_text}")


class JiraApiClient:
    """Client for interacting with the Jira API.
    Handles API requests, rate limiting, and error handling."""
    
    def __init__(self, config: JiraConfig):
        """Initialize the Jira API client.
        
        Args:
            config: Jira configuration"""
        self.config = config
        self.base_url = config.url.rstrip('/')
        self.api_base = f"{self.base_url}/rest/api/3"
        self.max_retries = config.max_retries
        self.timeout = config.timeout
        
        # Validate credentials on initialization
        if not token_manager.validate_jira_credentials(config):
            raise JiraApiError("Failed to validate Jira credentials")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Tuple[int, Dict[str, Any]]:
        """Make a request to the Jira API with retry logic and error handling.
        
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
            JiraApiError: If the request fails after all retries"""
        headers, auth = token_manager.get_jira_auth(self.config)
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
                    logger.warning(f"Rate limited by Jira API. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    return self._make_request(method, endpoint, data, params, files, retry_count + 1)
                else:
                    raise JiraApiError(
                        "Exceeded maximum retries due to rate limiting", 
                        response.status_code, 
                        response.text
                    )
            
            # Handle server errors
            if response.status_code >= 500:
                if retry_count < self.max_retries:
                    # Use exponential backoff
                    retry_after = 2 ** retry_count
                    logger.warning(f"Jira API server error. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    return self._make_request(method, endpoint, data, params, files, retry_count + 1)
                else:
                    raise JiraApiError(
                        "Exceeded maximum retries due to server errors", 
                        response.status_code, 
                        response.text
                    )
            
            # Handle authentication errors
            if response.status_code in (401, 403):
                raise JiraApiError(
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
                logger.warning(f"Jira API request timed out. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, data, params, files, retry_count + 1)
            else:
                raise JiraApiError(f"Jira API request timed out after {self.max_retries} retries")
        
        except RequestException as e:
            if retry_count < self.max_retries:
                retry_after = 2 ** retry_count
                logger.warning(f"Jira API request failed: {str(e)}. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, data, params, files, retry_count + 1)
            else:
                raise JiraApiError(f"Jira API request failed after {self.max_retries} retries: {str(e)}")
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get information about the current user.
        
        Returns:
            User information"""
        status_code, response = self._make_request('GET', 'myself')
        
        if status_code != 200:
            raise JiraApiError("Failed to get current user", status_code, response)
        
        return response
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects accessible to the current user.
        
        Returns:
            List of projects"""
        status_code, response = self._make_request('GET', 'project')
        
        if status_code != 200:
            raise JiraApiError("Failed to get projects", status_code, response)
        
        return response
    
    def get_project(self, project_key: str) -> Dict[str, Any]:
        """Get information about a specific project.
        
        Args:
            project_key: The project key
            
        Returns:
            Project information"""
        status_code, response = self._make_request('GET', f'project/{project_key}')
        
        if status_code != 200:
            raise JiraApiError(f"Failed to get project {project_key}", status_code, response)
        
        return response
    
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project.
        
        Args:
            project_data: Project data
            
        Returns:
            Created project information"""
        status_code, response = self._make_request('POST', 'project', data=project_data)
        
        if status_code != 201:
            raise JiraApiError("Failed to create project", status_code, response)
        
        return response
    
    def get_issues(self, project_key: str, jql: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get issues for a project, optionally filtered by JQL.
        
        Args:
            project_key: The project key
            jql: JQL query string
            max_results: Maximum number of results to return
            
        Returns:
            List of issues"""
        if not jql:
            jql = f"project = {project_key}"
        else:
            jql = f"project = {project_key} AND {jql}"
        
        params = {
            "jql": jql,
            "maxResults": max_results
        }
        
        status_code, response = self._make_request('GET', 'search', params=params)
        
        if status_code != 200:
            raise JiraApiError(f"Failed to get issues for project {project_key}", status_code, response)
        
        return response.get("issues", [])
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get information about a specific issue.
        
        Args:
            issue_key: The issue key
            
        Returns:
            Issue information"""
        status_code, response = self._make_request('GET', f'issue/{issue_key}')
        
        if status_code != 200:
            raise JiraApiError(f"Failed to get issue {issue_key}", status_code, response)
        
        return response
    
    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue.
        
        Args:
            issue_data: Issue data
            
        Returns:
            Created issue information"""
        status_code, response = self._make_request('POST', 'issue', data=issue_data)
        
        if status_code != 201:
            raise JiraApiError("Failed to create issue", status_code, response)
        
        return response
    
    def update_issue(self, issue_key: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing issue.
        
        Args:
            issue_key: The issue key
            issue_data: Issue data to update
            
        Returns:
            Updated issue information"""
        status_code, response = self._make_request('PUT', f'issue/{issue_key}', data=issue_data)
        
        if status_code not in (200, 204):
            raise JiraApiError(f"Failed to update issue {issue_key}", status_code, response)
        
        # If successful, get the updated issue
        return self.get_issue(issue_key)
    
    def get_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get comments for an issue.
        
        Args:
            issue_key: The issue key
            
        Returns:
            List of comments"""
        status_code, response = self._make_request('GET', f'issue/{issue_key}/comment')
        
        if status_code != 200:
            raise JiraApiError(f"Failed to get comments for issue {issue_key}", status_code, response)
        
        return response.get("comments", [])
    
    def add_comment(self, issue_key: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a comment to an issue.
        
        Args:
            issue_key: The issue key
            comment_data: Comment data
            
        Returns:
            Created comment information"""
        status_code, response = self._make_request('POST', f'issue/{issue_key}/comment', data=comment_data)
        
        if status_code != 201:
            raise JiraApiError(f"Failed to add comment to issue {issue_key}", status_code, response)
        
        return response
    
    def get_attachments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get attachments for an issue.
        
        Args:
            issue_key: The issue key
            
        Returns:
            List of attachments"""
        # Attachments are included in the issue response
        issue = self.get_issue(issue_key)
        return issue.get("fields", {}).get("attachment", [])
    
    def add_attachment(self, issue_key: str, file_path: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Add an attachment to an issue.
        
        Args:
            issue_key: The issue key
            file_path: Path to the file to attach
            filename: Optional filename to use (defaults to the file's basename)
            
        Returns:
            Created attachment information"""
        import os
        
        if not filename:
            filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            status_code, response = self._make_request(
                'POST', 
                f'issue/{issue_key}/attachments', 
                files=files
            )
        
        if status_code != 200:
            raise JiraApiError(f"Failed to add attachment to issue {issue_key}", status_code, response)
        
        return response[0] if isinstance(response, list) and response else response
    
    def get_worklogs(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get worklogs for an issue.
        
        Args:
            issue_key: The issue key
            
        Returns:
            List of worklogs"""
        status_code, response = self._make_request('GET', f'issue/{issue_key}/worklog')
        
        if status_code != 200:
            raise JiraApiError(f"Failed to get worklogs for issue {issue_key}", status_code, response)
        
        return response.get("worklogs", [])
    
    def add_worklog(self, issue_key: str, worklog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a worklog to an issue.
        
        Args:
            issue_key: The issue key
            worklog_data: Worklog data
            
        Returns:
            Created worklog information"""
        status_code, response = self._make_request('POST', f'issue/{issue_key}/worklog', data=worklog_data)
        
        if status_code != 201:
            raise JiraApiError(f"Failed to add worklog to issue {issue_key}", status_code, response)
        
        return response
    
    def get_issue_types(self) -> List[Dict[str, Any]]:
        """Get all issue types.
        
        Returns:
            List of issue types"""
        status_code, response = self._make_request('GET', 'issuetype')
        
        if status_code != 200:
            raise JiraApiError("Failed to get issue types", status_code, response)
        
        return response
    
    def get_priorities(self) -> List[Dict[str, Any]]:
        """Get all priorities.
        
        Returns:
            List of priorities"""
        status_code, response = self._make_request('GET', 'priority')
        
        if status_code != 200:
            raise JiraApiError("Failed to get priorities", status_code, response)
        
        return response
    
    def get_statuses(self) -> List[Dict[str, Any]]:
        """Get all statuses.
        
        Returns:
            List of statuses"""
        status_code, response = self._make_request('GET', 'status')
        
        if status_code != 200:
            raise JiraApiError("Failed to get statuses", status_code, response)
        
        return response
    
    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get available transitions for an issue.
        
        Args:
            issue_key: The issue key
            
        Returns:
            List of available transitions"""
        status_code, response = self._make_request('GET', f'issue/{issue_key}/transitions')
        
        if status_code != 200:
            raise JiraApiError(f"Failed to get transitions for issue {issue_key}", status_code, response)
        
        return response.get("transitions", [])
    
    def transition_issue(self, issue_key: str, transition_data: Dict[str, Any]) -> None:
        """Transition an issue to a new status.
        
        Args:
            issue_key: The issue key
            transition_data: Transition data including the transition ID"""
        status_code, response = self._make_request('POST', f'issue/{issue_key}/transitions', data=transition_data)
        
        if status_code not in (200, 204):
            raise JiraApiError(f"Failed to transition issue {issue_key}", status_code, response)
    
    def search_users(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for users.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of users"""
        params = {
            "query": query,
            "maxResults": max_results
        }
        
        status_code, response = self._make_request('GET', 'user/search', params=params)
        
        if status_code != 200:
            raise JiraApiError("Failed to search users", status_code, response)
        
        return response
    
    def convert_to_jira_project(self, project: JiraProject) -> Dict[str, Any]:
        """Convert a JiraProject model to Jira API format.
        
        Args:
            project: JiraProject model
            
        Returns:
            Jira API project data"""
        # This is a simplified conversion - actual implementation would be more complex
        return {
            "key": project.key,
            "name": project.name,
            "description": project.description,
            "leadAccountId": project.lead,
            "projectTypeKey": project.project_type,
            "projectTemplateKey": "com.pyxis.greenhopper.jira:basic-software-development-template"
        }
    
    def convert_to_jira_issue(self, issue: JiraIssue) -> Dict[str, Any]:
        """Convert a JiraIssue model to Jira API format.
        
        Args:
            issue: JiraIssue model
            
        Returns:
            Jira API issue data"""
        # This is a simplified conversion - actual implementation would be more complex
        fields = {
            "project": {
                "key": issue.project_id
            },
            "summary": issue.summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": issue.description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": issue.issue_type
            }
        }
        
        if issue.priority:
            fields["priority"] = {"name": issue.priority}
        
        if issue.assignee:
            fields["assignee"] = {"id": issue.assignee}
        
        if issue.labels:
            fields["labels"] = issue.labels
        
        if issue.components:
            fields["components"] = [{"name": c} for c in issue.components]
        
        if issue.due_date:
            fields["duedate"] = issue.due_date.strftime("%Y-%m-%d")
        
        # Add custom fields
        for key, value in issue.custom_fields.items():
            fields[key] = value
        
        return {"fields": fields}
    
    def convert_from_jira_project(self, jira_project: Dict[str, Any]) -> JiraProject:
        """Convert Jira API project data to JiraProject model.
        
        Args:
            jira_project: Jira API project data
            
        Returns:
            JiraProject model"""
        project = JiraProject(
            external_id=jira_project.get("id"),
            key=jira_project.get("key", ""),
            name=jira_project.get("name", ""),
            description=jira_project.get("description", ""),
            lead=jira_project.get("lead", {}).get("accountId", ""),
            url=jira_project.get("self", ""),
            project_type=jira_project.get("projectTypeKey", ""),
            project_category=jira_project.get("projectCategory", {}).get("name", ""),
            sync_status=SyncStatus.COMPLETED,
            last_sync_time=datetime.now()
        )
        
        return project
    
    def convert_from_jira_issue(self, jira_issue: Dict[str, Any]) -> JiraIssue:
        """Convert Jira API issue data to JiraIssue model.
        
        Args:
            jira_issue: Jira API issue data
            
        Returns:
            JiraIssue model"""
        fields = jira_issue.get("fields", {})
        
        # Extract description text from the document structure
        description = ""
        desc_content = fields.get("description", {})
        if isinstance(desc_content, dict) and "content" in desc_content:
            # This is a simplified extraction - actual implementation would be more complex
            for content in desc_content.get("content", []):
                if content.get("type") == "paragraph":
                    for text_content in content.get("content", []):
                        if text_content.get("type") == "text":
                            description += text_content.get("text", "")
        elif isinstance(desc_content, str):
            description = desc_content
        
        # Parse dates
        created = None
        updated = None
        due_date = None
        
        if fields.get("created"):
            try:
                created = datetime.fromisoformat(fields.get("created").replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        
        if fields.get("updated"):
            try:
                updated = datetime.fromisoformat(fields.get("updated").replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        
        if fields.get("duedate"):
            try:
                due_date = datetime.strptime(fields.get("duedate"), "%Y-%m-%d")
            except (ValueError, AttributeError):
                pass
        
        issue = JiraIssue(
            external_id=jira_issue.get("id"),
            key=jira_issue.get("key", ""),
            project_id=fields.get("project", {}).get("key", ""),
            summary=fields.get("summary", ""),
            description=description,
            issue_type=fields.get("issuetype", {}).get("name", ""),
            status=fields.get("status", {}).get("name", ""),
            priority=fields.get("priority", {}).get("name", ""),
            assignee=fields.get("assignee", {}).get("accountId", ""),
            reporter=fields.get("reporter", {}).get("accountId", ""),
            created=created,
            updated=updated,
            due_date=due_date,
            resolution=fields.get("resolution", {}).get("name", ""),
            labels=fields.get("labels", []),
            components=[c.get("name", "") for c in fields.get("components", [])],
            sync_status=SyncStatus.COMPLETED,
            last_sync_time=datetime.now()
        )
        
        # Extract custom fields
        for key, value in fields.items():
            if key.startswith("customfield_"):
                issue.custom_fields[key] = value
        
        return issue
