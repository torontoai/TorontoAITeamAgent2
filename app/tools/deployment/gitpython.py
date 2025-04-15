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


"""Deployment tools for TorontoAITeamAgent Team AI.

This module provides tools for Git operations using GitPython."""

from typing import Dict, Any, List, Optional
import os
import asyncio
import tempfile
from ..base import BaseTool, ToolResult

class GitPythonTool(BaseTool):
    """Tool for Git operations using GitPython."""
    
    name = "gitpython"
    description = "Provides capabilities for Git operations using GitPython."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the GitPython tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.timeout = self.config.get("timeout", 60)  # Default timeout in seconds
        
        # Import here to avoid dependency issues
        try:
            import git
            self.git_module = git
        except ImportError:
            raise ImportError("GitPython is not installed. Install it with 'pip install gitpython>=3.1.0'")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the GitPython tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (clone, commit, push, etc.)
                - repo_url: Repository URL for clone operation
                - repo_path: Repository path for operations on existing repositories
                - branch: Branch name for various operations
                - message: Commit message for commit operation
                - files: List of files to add for commit operation
                - username: Git username for authentication
                - password: Git password or token for authentication
                - timeout: Command timeout in seconds (optional)
                
        Returns:
            Tool execution result
        """
        operation = params.get("operation")
        if not operation:
            return ToolResult(
                success=False,
                data={},
                error="Operation parameter is required"
            )
            
        try:
            if operation == "clone":
                return await self._clone_repo(params)
            elif operation == "commit":
                return await self._commit_changes(params)
            elif operation == "push":
                return await self._push_changes(params)
            elif operation == "pull":
                return await self._pull_changes(params)
            elif operation == "status":
                return await self._get_status(params)
            elif operation == "checkout":
                return await self._checkout_branch(params)
            else:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unsupported operation: {operation}"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=str(e)
            )
    
    async def _clone_repo(self, params: Dict[str, Any]) -> ToolResult:
        """
        Clone a Git repository.
        
        Args:
            params: Parameters for repository cloning
            
        Returns:
            Tool execution result
        """
        repo_url = params.get("repo_url")
        repo_path = params.get("repo_path")
        branch = params.get("branch")
        username = params.get("username")
        password = params.get("password")
        timeout = params.get("timeout", self.timeout)
        
        if not repo_url:
            return ToolResult(
                success=False,
                data={},
                error="Repository URL parameter is required for clone operation"
            )
            
        if not repo_path:
            return ToolResult(
                success=False,
                data={},
                error="Repository path parameter is required for clone operation"
            )
        
        # Prepare authentication if provided
        if username and password:
            # Insert credentials into URL
            url_parts = repo_url.split("://")
            if len(url_parts) == 2:
                repo_url = f"{url_parts[0]}://{username}:{password}@{url_parts[1]}"
        
        # Run in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            repo = await loop.run_in_executor(
                None,
                lambda: self.git_module.Repo.clone_from(
                    repo_url,
                    repo_path,
                    branch=branch,
                    depth=1 if not branch else None
                )
            )
            
            return ToolResult(
                success=True,
                data={
                    "repo_path": repo_path,
                    "branch": repo.active_branch.name,
                    "commit": repo.head.commit.hexsha
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to clone repository: {str(e)}"
            )
    
    async def _commit_changes(self, params: Dict[str, Any]) -> ToolResult:
        """
        Commit changes to a Git repository.
        
        Args:
            params: Parameters for committing changes
            
        Returns:
            Tool execution result
        """
        repo_path = params.get("repo_path")
        message = params.get("message", "Commit by TorontoAITeamAgent Team AI")
        files = params.get("files", [])
        timeout = params.get("timeout", self.timeout)
        
        if not repo_path:
            return ToolResult(
                success=False,
                data={},
                error="Repository path parameter is required for commit operation"
            )
        
        # Run in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            repo = await loop.run_in_executor(
                None,
                lambda: self.git_module.Repo(repo_path)
            )
            
            # Add files if specified, otherwise add all changes
            if files:
                for file_path in files:
                    await loop.run_in_executor(
                        None,
                        lambda: repo.git.add(file_path)
                    )
            else:
                await loop.run_in_executor(
                    None,
                    lambda: repo.git.add(A=True)
                )
            
            # Commit changes
            commit = await loop.run_in_executor(
                None,
                lambda: repo.index.commit(message)
            )
            
            return ToolResult(
                success=True,
                data={
                    "commit": commit.hexsha,
                    "message": message,
                    "author": f"{commit.author.name} <{commit.author.email}>",
                    "files_changed": [item.a_path for item in commit.stats.files]
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to commit changes: {str(e)}"
            )
    
    async def _push_changes(self, params: Dict[str, Any]) -> ToolResult:
        """
        Push changes to a remote Git repository.
        
        Args:
            params: Parameters for pushing changes
            
        Returns:
            Tool execution result
        """
        repo_path = params.get("repo_path")
        remote = params.get("remote", "origin")
        branch = params.get("branch")
        username = params.get("username")
        password = params.get("password")
        timeout = params.get("timeout", self.timeout)
        
        if not repo_path:
            return ToolResult(
                success=False,
                data={},
                error="Repository path parameter is required for push operation"
            )
        
        # Run in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            repo = await loop.run_in_executor(
                None,
                lambda: self.git_module.Repo(repo_path)
            )
            
            # Set up authentication if provided
            if username and password:
                remote_url = await loop.run_in_executor(
                    None,
                    lambda: repo.remotes[remote].url
                )
                
                # Insert credentials into URL
                url_parts = remote_url.split("://")
                if len(url_parts) == 2:
                    new_url = f"{url_parts[0]}://{username}:{password}@{url_parts[1]}"
                    
                    await loop.run_in_executor(
                        None,
                        lambda: repo.remotes[remote].set_url(new_url)
                    )
            
            # Push changes
            push_info = await loop.run_in_executor(
                None,
                lambda: repo.remotes[remote].push(branch) if branch else repo.remotes[remote].push()
            )
            
            # Reset remote URL if it was modified
            if username and password:
                remote_url = await loop.run_in_executor(
                    None,
                    lambda: repo.remotes[remote].url
                )
                
                # Remove credentials from URL
                url_parts = remote_url.split("@")
                if len(url_parts) == 2:
                    protocol = remote_url.split("://")[0]
                    new_url = f"{protocol}://{url_parts[1]}"
                    
                    await loop.run_in_executor(
                        None,
                        lambda: repo.remotes[remote].set_url(new_url)
                    )
            
            return ToolResult(
                success=all(info.flags & info.ERROR == 0 for info in push_info),
                data={
                    "remote": remote,
                    "branch": branch or "current branch",
                    "push_info": [
                        {
                            "local_ref": info.local_ref.name if info.local_ref else None,
                            "remote_ref": info.remote_ref.name if info.remote_ref else None,
                            "summary": info.summary
                        }
                        for info in push_info
                    ]
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to push changes: {str(e)}"
            )
    
    async def _pull_changes(self, params: Dict[str, Any]) -> ToolResult:
        """
        Pull changes from a remote Git repository.
        
        Args:
            params: Parameters for pulling changes
            
        Returns:
            Tool execution result
        """
        repo_path = params.get("repo_path")
        remote = params.get("remote", "origin")
        branch = params.get("branch")
        username = params.get("username")
        password = params.get("password")
        timeout = params.get("timeout", self.timeout)
        
        if not repo_path:
            return ToolResult(
                success=False,
                data={},
                error="Repository path parameter is required for pull operation"
            )
        
        # Run in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            repo = await loop.run_in_executor(
                None,
                lambda: self.git_module.Repo(repo_path)
            )
            
            # Set up authentication if provided
            if username and password:
                remote_url = await loop.run_in_executor(
                    None,
                    lambda: repo.remotes[remote].url
                )
                
                # Insert credentials into URL
                url_parts = remote_url.split("://")
                if len(url_parts) == 2:
                    new_url = f"{url_parts[0]}://{username}:{password}@{url_parts[1]}"
                    
                    await loop.run_in_executor(
                        None,
                        lambda: repo.remotes[remote].set_url(new_url)
                    )
            
            # Pull changes
            pull_info = await loop.run_in_executor(
                None,
                lambda: repo.remotes[remote].pull(branch) if branch else repo.remotes[remote].pull()
            )
            
            # Reset remote URL if it was modified
            if username and password:
                remote_url = await loop.run_in_executor(
                    None,
                    lambda: repo.remotes[remote].url
                )
                
                # Remove credentials from URL
                url_parts = remote_url.split("@")
                if len(url_parts) == 2:
                    protocol = remote_url.split("://")[0]
                    new_url = f"{protocol}://{url_parts[1]}"
                    
                    await loop.run_in_executor(
                        None,
                        lambda: repo.remotes[remote].set_url(new_url)
                    )
            
            return ToolResult(
                success=True,
                data={
                    "remote": remote,
                    "branch": branch or "current branch",
                    "pull_info": [
                        {
                            "ref": info.ref.name,
                            "note": info.note,
                            "commit": info.commit.hexsha if info.commit else None
                        }
                        for info in pull_info
                    ]
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to pull changes: {str(e)}"
            )
    
    async def _get_status(self, params: Dict[str, Any]) -> ToolResult:
        """
        Get the status of a Git repository.
        
        Args:
            params: Parameters for getting repository status
            
        Returns:
            Tool execution result
        """
        repo_path = params.get("repo_path")
        timeout = params.get("timeout", self.timeout)
        
        if not repo_path:
            return ToolResult(
                success=False,
                data={},
                error="Repository path parameter is required for status operation"
            )
        
        # Run in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            repo = await loop.run_in_executor(
                None,
                lambda: self.git_module.Repo(repo_path)
            )
            
            # Get status
            status = await loop.run_in_executor(
                None,
                lambda: repo.git.status(porcelain=True)
            )
            
            # Parse status output
            untracked_files = []
            modified_files = []
            deleted_files = []
            staged_files = []
            
            for line in status.splitlines():
                if line.startswith("??"):
                    untracked_files.append(line[3:])
                elif line.startswith(" M"):
                    modified_files.append(line[3:])
                elif line.startswith(" D"):
                    deleted_files.append(line[3:])
                elif line.startswith("M ") or line.startswith("A ") or line.startswith("D "):
                    staged_files.append(line[3:])
            
            return ToolResult(
                success=True,
                data={
                    "branch": repo.active_branch.name,
                    "commit": repo.head.commit.hexsha,
                    "untracked_files": untracked_files,
                    "modified_files": modified_files,
                    "deleted_files": deleted_files,
                    "staged_files": staged_files,
                    "is_dirty": repo.is_dirty(),
                    "has_untracked_files": len(untracked_files) > 0
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to get repository status: {str(e)}"
            )
    
    async def _checkout_branch(self, params: Dict[str, Any]) -> ToolResult:
        """
        Checkout a branch in a Git repository.
        
        Args:
            params: Parameters for checking out a branch
            
        Returns:
            Tool execution result
        """
        repo_path = params.get("repo_path")
        branch = params.get("branch")
        create = params.get("create", False)
        timeout = params.get("timeout", self.timeout)
        
        if not repo_path:
            return ToolResult(
                success=False,
                data={},
                error="Repository path parameter is required for checkout operation"
            )
            
        if not branch:
            return ToolResult(
                success=False,
                data={},
                error="Branch parameter is required for checkout operation"
            )
        
        # Run in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            repo = await loop.run_in_executor(
                None,
                lambda: self.git_module.Repo(repo_path)
            )
            
            # Check if branch exists
            branch_exists = branch in [b.name for b in repo.branches]
            
            if not branch_exists and not create:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Branch '{branch}' does not exist and create flag is not set"
                )
            
            # Checkout or create branch
            if branch_exists:
                await loop.run_in_executor(
                    None,
                    lambda: repo.git.checkout(branch)
                )
            else:
                await loop.run_in_executor(
                    None,
                    lambda: repo.git.checkout("-b", branch)
                )
            
            return ToolResult(
                success=True,
                data={
                    "branch": branch,
                    "commit": repo.head.commit.hexsha,
                    "created": not branch_exists and create
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to checkout branch: {str(e)}"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Clone Git repositories",
            "Commit changes to Git repositories",
            "Push changes to remote Git repositories",
            "Pull changes from remote Git repositories",
            "Get status of Git repositories",
            "Checkout branches in Git repositories"
        ]
