"""
CI/CD Integration Examples and Usage Patterns.

This module provides examples and usage patterns for the CI/CD integration components.
"""

import os
from typing import List, Dict, Any

from .cicd_integration import (
    CICDIntegrationManager,
    CICDProvider,
    GitHubActionsManager,
    GitLabCIManager,
    CICDTemplateLibrary,
    TriggerEvent,
    JobType
)


def create_github_python_workflow(repo_path: str, project_name: str) -> str:
    """
    Create a GitHub Actions workflow for a Python project.
    
    Args:
        repo_path: Path to the repository
        project_name: Name of the project
        
    Returns:
        Path to the created workflow file
    """
    manager = CICDIntegrationManager(CICDProvider.GITHUB_ACTIONS, repo_path)
    template = CICDTemplateLibrary.get_python_template()
    template["name"] = f"{project_name} CI"
    
    return manager.create_workflow(
        name=template["name"],
        triggers=template["triggers"],
        jobs=template["jobs"]
    )


def create_gitlab_python_workflow(repo_path: str, project_name: str) -> str:
    """
    Create a GitLab CI workflow for a Python project.
    
    Args:
        repo_path: Path to the repository
        project_name: Name of the project
        
    Returns:
        Path to the created workflow file
    """
    manager = CICDIntegrationManager(CICDProvider.GITLAB_CI, repo_path)
    template = CICDTemplateLibrary.get_python_template()
    template["name"] = f"{project_name} CI"
    
    return manager.create_workflow(
        name=template["name"],
        triggers=template["triggers"],
        jobs=template["jobs"]
    )


def create_github_matrix_build(repo_path: str, project_name: str, language: str, versions: List[str]) -> str:
    """
    Create a GitHub Actions matrix build workflow.
    
    Args:
        repo_path: Path to the repository
        project_name: Name of the project
        language: Programming language
        versions: List of language versions to test
        
    Returns:
        Path to the created workflow file
    """
    github_manager = GitHubActionsManager(repo_path)
    return github_manager.create_matrix_build(
        name=f"{project_name} Matrix Build",
        language=language,
        versions=versions
    )


def create_gitlab_multi_stage_pipeline(repo_path: str, stages: List[str], jobs: Dict[str, Dict[str, Any]]) -> str:
    """
    Create a GitLab CI multi-stage pipeline.
    
    Args:
        repo_path: Path to the repository
        stages: List of pipeline stages
        jobs: Dictionary of jobs
        
    Returns:
        Path to the created pipeline file
    """
    gitlab_manager = GitLabCIManager(repo_path)
    return gitlab_manager.create_multi_stage_pipeline(stages, jobs)


def optimize_github_workflow(repo_path: str, workflow_name: str) -> Dict[str, Any]:
    """
    Optimize a GitHub Actions workflow.
    
    Args:
        repo_path: Path to the repository
        workflow_name: Name of the workflow file
        
    Returns:
        Dictionary with optimization results
    """
    manager = CICDIntegrationManager(CICDProvider.GITHUB_ACTIONS, repo_path)
    workflow_path = os.path.join(repo_path, ".github", "workflows", f"{workflow_name}.yml")
    
    return manager.optimize_workflow(workflow_path)


def optimize_gitlab_workflow(repo_path: str) -> Dict[str, Any]:
    """
    Optimize a GitLab CI workflow.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with optimization results
    """
    manager = CICDIntegrationManager(CICDProvider.GITLAB_CI, repo_path)
    workflow_path = os.path.join(repo_path, ".gitlab-ci.yml")
    
    return manager.optimize_workflow(workflow_path)


def create_deployment_pipeline(repo_path: str, provider: CICDProvider, environments: List[str]) -> str:
    """
    Create a deployment pipeline for multiple environments.
    
    Args:
        repo_path: Path to the repository
        provider: CI/CD provider
        environments: List of environments
        
    Returns:
        Path to the created pipeline file
    """
    if provider == CICDProvider.GITHUB_ACTIONS:
        github_manager = GitHubActionsManager(repo_path)
        
        # Create deployment workflows for each environment
        workflow_paths = []
        for env in environments:
            deploy_steps = [
                {
                    "name": f"Deploy to {env}",
                    "run": f"echo 'Deploying to {env}'"
                }
            ]
            
            workflow_path = github_manager.create_deployment_workflow(
                name=f"Deploy to {env}",
                environment=env,
                deploy_steps=deploy_steps
            )
            workflow_paths.append(workflow_path)
        
        return workflow_paths[0]  # Return the first workflow path
    
    elif provider == CICDProvider.GITLAB_CI:
        gitlab_manager = GitLabCIManager(repo_path)
        return gitlab_manager.create_environment_deployments(environments)
    
    else:
        raise ValueError(f"Unsupported CI/CD provider: {provider}")
