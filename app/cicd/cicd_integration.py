"""
GitHub Actions and GitLab CI Integration for TORONTO AI TEAM AGENT.

This module provides functionality to create, manage, and optimize CI/CD pipelines
for automated testing and deployment using GitHub Actions and GitLab CI.
"""

import os
import yaml
import json
from typing import Dict, List, Optional, Union, Any
from enum import Enum


class CICDProvider(Enum):
    """Enum representing supported CI/CD providers."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"


class JobType(Enum):
    """Enum representing types of CI/CD jobs."""
    BUILD = "build"
    TEST = "test"
    LINT = "lint"
    DEPLOY = "deploy"
    SECURITY_SCAN = "security_scan"
    CUSTOM = "custom"


class TriggerEvent(Enum):
    """Enum representing events that can trigger CI/CD workflows."""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    TAG = "tag"
    RELEASE = "release"


class CICDIntegrationManager:
    """
    Manager class for CI/CD integrations.
    
    This class provides functionality to create, manage, and optimize CI/CD pipelines
    for automated testing and deployment using GitHub Actions and GitLab CI.
    """
    
    def __init__(self, provider: CICDProvider, repo_path: str):
        """
        Initialize the CI/CD Integration Manager.
        
        Args:
            provider: The CI/CD provider to use (GitHub Actions or GitLab CI)
            repo_path: Path to the repository
        """
        self.provider = provider
        self.repo_path = repo_path
        self.config_path = self._get_config_path()
        
    def _get_config_path(self) -> str:
        """
        Get the path to the CI/CD configuration file based on the provider.
        
        Returns:
            Path to the configuration file
        """
        if self.provider == CICDProvider.GITHUB_ACTIONS:
            return os.path.join(self.repo_path, ".github", "workflows")
        elif self.provider == CICDProvider.GITLAB_CI:
            return os.path.join(self.repo_path, ".gitlab-ci.yml")
        else:
            raise ValueError(f"Unsupported CI/CD provider: {self.provider}")
    
    def create_workflow(self, name: str, triggers: List[TriggerEvent], jobs: Dict[str, Any]) -> str:
        """
        Create a new CI/CD workflow.
        
        Args:
            name: Name of the workflow
            triggers: List of events that trigger the workflow
            jobs: Dictionary of jobs to include in the workflow
            
        Returns:
            Path to the created workflow file
        """
        if self.provider == CICDProvider.GITHUB_ACTIONS:
            return self._create_github_workflow(name, triggers, jobs)
        elif self.provider == CICDProvider.GITLAB_CI:
            return self._create_gitlab_workflow(name, triggers, jobs)
        else:
            raise ValueError(f"Unsupported CI/CD provider: {self.provider}")
    
    def _create_github_workflow(self, name: str, triggers: List[TriggerEvent], jobs: Dict[str, Any]) -> str:
        """
        Create a GitHub Actions workflow.
        
        Args:
            name: Name of the workflow
            triggers: List of events that trigger the workflow
            jobs: Dictionary of jobs to include in the workflow
            
        Returns:
            Path to the created workflow file
        """
        # Ensure the workflows directory exists
        os.makedirs(os.path.join(self.repo_path, ".github", "workflows"), exist_ok=True)
        
        # Create the workflow file path
        workflow_file = os.path.join(self.repo_path, ".github", "workflows", f"{name.lower().replace(' ', '_')}.yml")
        
        # Create the workflow configuration
        workflow = {
            "name": name,
            "on": self._format_github_triggers(triggers),
            "jobs": self._format_github_jobs(jobs)
        }
        
        # Write the workflow to file
        with open(workflow_file, 'w') as f:
            yaml.dump(workflow, f, sort_keys=False)
        
        return workflow_file
    
    def _format_github_triggers(self, triggers: List[TriggerEvent]) -> Dict[str, Any]:
        """
        Format triggers for GitHub Actions.
        
        Args:
            triggers: List of trigger events
            
        Returns:
            Formatted triggers for GitHub Actions
        """
        result = {}
        for trigger in triggers:
            if trigger == TriggerEvent.PUSH:
                result["push"] = {"branches": ["main", "master"]}
            elif trigger == TriggerEvent.PULL_REQUEST:
                result["pull_request"] = {"branches": ["main", "master"]}
            elif trigger == TriggerEvent.SCHEDULE:
                result["schedule"] = [{"cron": "0 0 * * *"}]  # Daily at midnight
            elif trigger == TriggerEvent.TAG:
                result["push"] = {"tags": ["v*"]}
            elif trigger == TriggerEvent.RELEASE:
                result["release"] = {"types": ["published"]}
        
        return result
    
    def _format_github_jobs(self, jobs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format jobs for GitHub Actions.
        
        Args:
            jobs: Dictionary of jobs
            
        Returns:
            Formatted jobs for GitHub Actions
        """
        formatted_jobs = {}
        
        for job_id, job_config in jobs.items():
            formatted_job = {
                "runs-on": job_config.get("runs-on", "ubuntu-latest"),
                "steps": []
            }
            
            # Add checkout step
            formatted_job["steps"].append({
                "name": "Checkout code",
                "uses": "actions/checkout@v3"
            })
            
            # Add setup steps
            if "setup" in job_config:
                for setup_step in job_config["setup"]:
                    formatted_job["steps"].append(setup_step)
            
            # Add main steps
            if "steps" in job_config:
                for step in job_config["steps"]:
                    formatted_job["steps"].append(step)
            
            # Add dependencies
            if "needs" in job_config:
                formatted_job["needs"] = job_config["needs"]
            
            formatted_jobs[job_id] = formatted_job
        
        return formatted_jobs
    
    def _create_gitlab_workflow(self, name: str, triggers: List[TriggerEvent], jobs: Dict[str, Any]) -> str:
        """
        Create a GitLab CI workflow.
        
        Args:
            name: Name of the workflow
            triggers: List of events that trigger the workflow
            jobs: Dictionary of jobs to include in the workflow
            
        Returns:
            Path to the created workflow file
        """
        # Create the workflow file path
        workflow_file = os.path.join(self.repo_path, ".gitlab-ci.yml")
        
        # Create the workflow configuration
        workflow = {
            "stages": self._get_gitlab_stages(jobs),
            "variables": {
                "WORKFLOW_NAME": name
            }
        }
        
        # Add workflow triggers
        workflow.update(self._format_gitlab_triggers(triggers))
        
        # Add jobs
        workflow.update(self._format_gitlab_jobs(jobs))
        
        # Write the workflow to file
        with open(workflow_file, 'w') as f:
            yaml.dump(workflow, f, sort_keys=False)
        
        return workflow_file
    
    def _get_gitlab_stages(self, jobs: Dict[str, Any]) -> List[str]:
        """
        Extract stages from jobs for GitLab CI.
        
        Args:
            jobs: Dictionary of jobs
            
        Returns:
            List of stages
        """
        stages = set()
        for job_config in jobs.values():
            if "stage" in job_config:
                stages.add(job_config["stage"])
            else:
                stages.add("test")  # Default stage
        
        # Ensure stages are in a logical order
        ordered_stages = []
        for stage in ["build", "test", "lint", "security_scan", "deploy"]:
            if stage in stages:
                ordered_stages.append(stage)
                stages.remove(stage)
        
        # Add any remaining stages
        ordered_stages.extend(list(stages))
        
        return ordered_stages
    
    def _format_gitlab_triggers(self, triggers: List[TriggerEvent]) -> Dict[str, Any]:
        """
        Format triggers for GitLab CI.
        
        Args:
            triggers: List of trigger events
            
        Returns:
            Formatted triggers for GitLab CI
        """
        result = {"workflow": {}}
        
        for trigger in triggers:
            if trigger == TriggerEvent.PUSH:
                result["workflow"]["rules"] = result["workflow"].get("rules", [])
                result["workflow"]["rules"].append({
                    "if": "$CI_COMMIT_BRANCH == 'main' || $CI_COMMIT_BRANCH == 'master'",
                    "when": "always"
                })
            elif trigger == TriggerEvent.PULL_REQUEST:
                result["workflow"]["rules"] = result["workflow"].get("rules", [])
                result["workflow"]["rules"].append({
                    "if": "$CI_PIPELINE_SOURCE == 'merge_request_event'",
                    "when": "always"
                })
            elif trigger == TriggerEvent.SCHEDULE:
                result["workflow"]["rules"] = result["workflow"].get("rules", [])
                result["workflow"]["rules"].append({
                    "if": "$CI_PIPELINE_SOURCE == 'schedule'",
                    "when": "always"
                })
            elif trigger == TriggerEvent.TAG:
                result["workflow"]["rules"] = result["workflow"].get("rules", [])
                result["workflow"]["rules"].append({
                    "if": "$CI_COMMIT_TAG =~ /^v/",
                    "when": "always"
                })
            elif trigger == TriggerEvent.MANUAL:
                result["workflow"]["rules"] = result["workflow"].get("rules", [])
                result["workflow"]["rules"].append({
                    "if": "$CI_PIPELINE_SOURCE == 'web'",
                    "when": "always"
                })
        
        return result
    
    def _format_gitlab_jobs(self, jobs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format jobs for GitLab CI.
        
        Args:
            jobs: Dictionary of jobs
            
        Returns:
            Formatted jobs for GitLab CI
        """
        formatted_jobs = {}
        
        for job_id, job_config in jobs.items():
            formatted_job = {
                "stage": job_config.get("stage", "test"),
                "image": job_config.get("image", "python:3.9"),
                "script": []
            }
            
            # Add setup steps
            if "setup" in job_config:
                for setup_step in job_config["setup"]:
                    if "run" in setup_step:
                        formatted_job["script"].append(setup_step["run"])
            
            # Add main steps
            if "steps" in job_config:
                for step in job_config["steps"]:
                    if "run" in step:
                        formatted_job["script"].append(step["run"])
            
            # Add dependencies
            if "needs" in job_config:
                formatted_job["needs"] = job_config["needs"]
            
            # Add artifacts if specified
            if "artifacts" in job_config:
                formatted_job["artifacts"] = job_config["artifacts"]
            
            formatted_jobs[job_id] = formatted_job
        
        return formatted_jobs
    
    def optimize_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """
        Optimize a CI/CD workflow for better performance and resource usage.
        
        Args:
            workflow_path: Path to the workflow file
            
        Returns:
            Dictionary with optimization results
        """
        # Load the workflow
        with open(workflow_path, 'r') as f:
            if self.provider == CICDProvider.GITHUB_ACTIONS:
                workflow = yaml.safe_load(f)
            else:
                workflow = yaml.safe_load(f)
        
        # Optimization metrics
        metrics = {
            "original_jobs": len(workflow.get("jobs", {})) if self.provider == CICDProvider.GITHUB_ACTIONS else len([k for k in workflow.keys() if k not in ["stages", "variables", "workflow"]]),
            "optimized_jobs": 0,
            "parallelized_jobs": 0,
            "caching_added": 0,
            "estimated_time_saved": 0
        }
        
        # Perform optimizations
        if self.provider == CICDProvider.GITHUB_ACTIONS:
            workflow = self._optimize_github_workflow(workflow, metrics)
        else:
            workflow = self._optimize_gitlab_workflow(workflow, metrics)
        
        # Save the optimized workflow
        with open(workflow_path, 'w') as f:
            yaml.dump(workflow, f, sort_keys=False)
        
        return metrics
    
    def _optimize_github_workflow(self, workflow: Dict[str, Any], metrics: Dict[str, int]) -> Dict[str, Any]:
        """
        Optimize a GitHub Actions workflow.
        
        Args:
            workflow: The workflow configuration
            metrics: Dictionary to track optimization metrics
            
        Returns:
            Optimized workflow configuration
        """
        jobs = workflow.get("jobs", {})
        
        # Add caching to jobs where applicable
        for job_id, job in jobs.items():
            # Add dependency caching for common languages
            if any("python" in str(step).lower() for step in job.get("steps", [])):
                job["steps"].insert(1, {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {"python-version": "3.9"}
                })
                job["steps"].insert(2, {
                    "name": "Cache pip dependencies",
                    "uses": "actions/cache@v3",
                    "with": {
                        "path": "~/.cache/pip",
                        "key": "${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}",
                        "restore-keys": "${{ runner.os }}-pip-"
                    }
                })
                metrics["caching_added"] += 1
            
            if any("node" in str(step).lower() for step in job.get("steps", [])):
                job["steps"].insert(1, {
                    "name": "Set up Node.js",
                    "uses": "actions/setup-node@v3",
                    "with": {"node-version": "16"}
                })
                job["steps"].insert(2, {
                    "name": "Cache npm dependencies",
                    "uses": "actions/cache@v3",
                    "with": {
                        "path": "~/.npm",
                        "key": "${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}",
                        "restore-keys": "${{ runner.os }}-node-"
                    }
                })
                metrics["caching_added"] += 1
        
        # Parallelize independent jobs
        dependency_graph = {}
        for job_id, job in jobs.items():
            dependency_graph[job_id] = job.get("needs", [])
        
        # Find independent jobs that can run in parallel
        independent_jobs = [job_id for job_id, deps in dependency_graph.items() if not deps]
        if len(independent_jobs) > 1:
            metrics["parallelized_jobs"] = len(independent_jobs)
        
        metrics["optimized_jobs"] = len(jobs)
        metrics["estimated_time_saved"] = metrics["caching_added"] * 2 + metrics["parallelized_jobs"] * 3
        
        workflow["jobs"] = jobs
        return workflow
    
    def _optimize_gitlab_workflow(self, workflow: Dict[str, Any], metrics: Dict[str, int]) -> Dict[str, Any]:
        """
        Optimize a GitLab CI workflow.
        
        Args:
            workflow: The workflow configuration
            metrics: Dictionary to track optimization metrics
            
        Returns:
            Optimized workflow configuration
        """
        # Count jobs (excluding special keys)
        jobs = {k: v for k, v in workflow.items() if k not in ["stages", "variables", "workflow"]}
        
        # Add caching to jobs where applicable
        for job_id, job in jobs.items():
            # Add dependency caching for common languages
            if "python" in str(job.get("image", "")).lower() or any("pip" in str(script).lower() for script in job.get("script", [])):
                if "cache" not in job:
                    job["cache"] = {
                        "key": "$CI_COMMIT_REF_SLUG-pip",
                        "paths": [".pip-cache/"],
                        "policy": "pull-push"
                    }
                    # Add pip cache directory configuration
                    job["before_script"] = job.get("before_script", [])
                    job["before_script"].insert(0, "export PIP_CACHE_DIR=.pip-cache")
                    metrics["caching_added"] += 1
            
            if "node" in str(job.get("image", "")).lower() or any("npm" in str(script).lower() for script in job.get("script", [])):
                if "cache" not in job:
                    job["cache"] = {
                        "key": "$CI_COMMIT_REF_SLUG-npm",
                        "paths": ["node_modules/"],
                        "policy": "pull-push"
                    }
                    metrics["caching_added"] += 1
        
        # Optimize job dependencies
        dependency_graph = {}
        for job_id, job in jobs.items():
            dependency_graph[job_id] = job.get("needs", [])
        
        # Find independent jobs that can run in parallel
        independent_jobs = [job_id for job_id, deps in dependency_graph.items() if not deps]
        if len(independent_jobs) > 1:
            metrics["parallelized_jobs"] = len(independent_jobs)
        
        metrics["optimized_jobs"] = len(jobs)
        metrics["estimated_time_saved"] = metrics["caching_added"] * 2 + metrics["parallelized_jobs"] * 3
        
        # Update the workflow with optimized jobs
        for job_id, job in jobs.items():
            workflow[job_id] = job
        
        return workflow
    
    def create_standard_workflow(self, name: str, language: str, triggers: List[TriggerEvent] = None) -> str:
        """
        Create a standard workflow for a specific programming language.
        
        Args:
            name: Name of the workflow
            language: Programming language (python, node, java, etc.)
            triggers: List of events that trigger the workflow (default: push and pull_request)
            
        Returns:
            Path to the created workflow file
        """
        if triggers is None:
            triggers = [TriggerEvent.PUSH, TriggerEvent.PULL_REQUEST]
        
        if language.lower() == "python":
            return self._create_python_workflow(name, triggers)
        elif language.lower() in ["node", "javascript", "typescript"]:
            return self._create_node_workflow(name, triggers)
        elif language.lower() == "java":
            return self._create_java_workflow(name, triggers)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _create_python_workflow(self, name: str, triggers: List[TriggerEvent]) -> str:
        """
        Create a standard Python workflow.
        
        Args:
            name: Name of the workflow
            triggers: List of events that trigger the workflow
            
        Returns:
            Path to the created workflow file
        """
        jobs = {
            "lint": {
                "runs-on": "ubuntu-latest",
                "stage": "lint",
                "setup": [
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "3.9"}
                    },
                    {
                        "name": "Install dependencies",
                        "run": "pip install flake8 black isort"
                    }
                ],
                "steps": [
                    {
                        "name": "Lint with flake8",
                        "run": "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
                    },
                    {
                        "name": "Check formatting with black",
                        "run": "black --check ."
                    },
                    {
                        "name": "Check imports with isort",
                        "run": "isort --check-only --profile black ."
                    }
                ]
            },
            "test": {
                "runs-on": "ubuntu-latest",
                "stage": "test",
                "setup": [
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "3.9"}
                    },
                    {
                        "name": "Install dependencies",
                        "run": "pip install pytest pytest-cov\npip install -r requirements.txt"
                    }
                ],
                "steps": [
                    {
                        "name": "Test with pytest",
                        "run": "pytest --cov=. --cov-report=xml"
                    }
                ]
            },
            "build": {
                "runs-on": "ubuntu-latest",
                "stage": "build",
                "needs": ["test", "lint"],
                "setup": [
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "3.9"}
                    },
                    {
                        "name": "Install dependencies",
                        "run": "pip install build twine"
                    }
                ],
                "steps": [
                    {
                        "name": "Build package",
                        "run": "python -m build"
                    },
                    {
                        "name": "Check package",
                        "run": "twine check dist/*"
                    }
                ]
            }
        }
        
        return self.create_workflow(name, triggers, jobs)
    
    def _create_node_workflow(self, name: str, triggers: List[TriggerEvent]) -> str:
        """
        Create a standard Node.js workflow.
        
        Args:
            name: Name of the workflow
            triggers: List of events that trigger the workflow
            
        Returns:
            Path to the created workflow file
        """
        jobs = {
            "lint": {
                "runs-on": "ubuntu-latest",
                "stage": "lint",
                "setup": [
                    {
                        "name": "Set up Node.js",
                        "uses": "actions/setup-node@v3",
                        "with": {"node-version": "16"}
                    },
                    {
                        "name": "Install dependencies",
                        "run": "npm ci"
                    }
                ],
                "steps": [
                    {
                        "name": "Lint with ESLint",
                        "run": "npm run lint"
                    }
                ]
            },
            "test": {
                "runs-on": "ubuntu-latest",
                "stage": "test",
                "setup": [
                    {
                        "name": "Set up Node.js",
                        "uses": "actions/setup-node@v3",
                        "with": {"node-version": "16"}
                    },
                    {
                        "name": "Install dependencies",
                        "run": "npm ci"
                    }
                ],
                "steps": [
                    {
                        "name": "Test with Jest",
                        "run": "npm test"
                    }
                ]
            },
            "build": {
                "runs-on": "ubuntu-latest",
                "stage": "build",
                "needs": ["test", "lint"],
                "setup": [
                    {
                        "name": "Set up Node.js",
                        "uses": "actions/setup-node@v3",
                        "with": {"node-version": "16"}
                    },
                    {
                        "name": "Install dependencies",
                        "run": "npm ci"
                    }
                ],
                "steps": [
                    {
                        "name": "Build",
                        "run": "npm run build"
                    }
                ]
            }
        }
        
        return self.create_workflow(name, triggers, jobs)
    
    def _create_java_workflow(self, name: str, triggers: List[TriggerEvent]) -> str:
        """
        Create a standard Java workflow.
        
        Args:
            name: Name of the workflow
            triggers: List of events that trigger the workflow
            
        Returns:
            Path to the created workflow file
        """
        jobs = {
            "build": {
                "runs-on": "ubuntu-latest",
                "stage": "build",
                "setup": [
                    {
                        "name": "Set up JDK",
                        "uses": "actions/setup-java@v3",
                        "with": {
                            "java-version": "11",
                            "distribution": "temurin"
                        }
                    }
                ],
                "steps": [
                    {
                        "name": "Build with Maven",
                        "run": "mvn -B package --file pom.xml"
                    }
                ]
            },
            "test": {
                "runs-on": "ubuntu-latest",
                "stage": "test",
                "setup": [
                    {
                        "name": "Set up JDK",
                        "uses": "actions/setup-java@v3",
                        "with": {
                            "java-version": "11",
                            "distribution": "temurin"
                        }
                    }
                ],
                "steps": [
                    {
                        "name": "Test with Maven",
                        "run": "mvn -B test --file pom.xml"
                    }
                ]
            }
        }
        
        return self.create_workflow(name, triggers, jobs)


class GitHubActionsManager:
    """
    Specialized manager for GitHub Actions workflows.
    
    This class provides GitHub Actions-specific functionality for creating and managing workflows.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the GitHub Actions Manager.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = repo_path
        self.workflows_dir = os.path.join(repo_path, ".github", "workflows")
        os.makedirs(self.workflows_dir, exist_ok=True)
    
    def create_matrix_build(self, name: str, language: str, versions: List[str], os_list: List[str] = None) -> str:
        """
        Create a matrix build workflow that tests across multiple versions and operating systems.
        
        Args:
            name: Name of the workflow
            language: Programming language
            versions: List of language versions to test
            os_list: List of operating systems to test on (default: ubuntu-latest, windows-latest, macos-latest)
            
        Returns:
            Path to the created workflow file
        """
        if os_list is None:
            os_list = ["ubuntu-latest", "windows-latest", "macos-latest"]
        
        workflow_file = os.path.join(self.workflows_dir, f"{name.lower().replace(' ', '_')}.yml")
        
        workflow = {
            "name": name,
            "on": {
                "push": {"branches": ["main", "master"]},
                "pull_request": {"branches": ["main", "master"]}
            },
            "jobs": {
                "build": {
                    "runs-on": "${{ matrix.os }}",
                    "strategy": {
                        "matrix": {
                            "os": os_list,
                            f"{language}-version": versions
                        }
                    },
                    "steps": [
                        {"uses": "actions/checkout@v3"}
                    ]
                }
            }
        }
        
        # Add language-specific setup
        if language.lower() == "python":
            workflow["jobs"]["build"]["steps"].append({
                "name": f"Set up Python ${{ matrix.python-version }}",
                "uses": "actions/setup-python@v4",
                "with": {"python-version": f"${{ matrix.python-version }}"}
            })
            workflow["jobs"]["build"]["steps"].append({
                "name": "Install dependencies",
                "run": "python -m pip install --upgrade pip\npip install pytest\npip install -r requirements.txt"
            })
            workflow["jobs"]["build"]["steps"].append({
                "name": "Test with pytest",
                "run": "pytest"
            })
        elif language.lower() in ["node", "nodejs"]:
            workflow["jobs"]["build"]["steps"].append({
                "name": f"Set up Node.js ${{ matrix.node-version }}",
                "uses": "actions/setup-node@v3",
                "with": {"node-version": f"${{ matrix.node-version }}"}
            })
            workflow["jobs"]["build"]["steps"].append({
                "name": "Install dependencies",
                "run": "npm ci"
            })
            workflow["jobs"]["build"]["steps"].append({
                "name": "Run tests",
                "run": "npm test"
            })
        elif language.lower() == "java":
            workflow["jobs"]["build"]["steps"].append({
                "name": f"Set up JDK ${{ matrix.java-version }}",
                "uses": "actions/setup-java@v3",
                "with": {
                    "java-version": f"${{ matrix.java-version }}",
                    "distribution": "temurin"
                }
            })
            workflow["jobs"]["build"]["steps"].append({
                "name": "Build with Maven",
                "run": "mvn -B package --file pom.xml"
            })
        
        # Write the workflow to file
        with open(workflow_file, 'w') as f:
            yaml.dump(workflow, f, sort_keys=False)
        
        return workflow_file
    
    def create_deployment_workflow(self, name: str, environment: str, deploy_steps: List[Dict[str, Any]]) -> str:
        """
        Create a deployment workflow for a specific environment.
        
        Args:
            name: Name of the workflow
            environment: Deployment environment (e.g., production, staging)
            deploy_steps: List of deployment steps
            
        Returns:
            Path to the created workflow file
        """
        workflow_file = os.path.join(self.workflows_dir, f"deploy_{environment.lower()}.yml")
        
        # Define triggers based on environment
        if environment.lower() == "production":
            triggers = {
                "release": {"types": ["published"]}
            }
        else:
            triggers = {
                "push": {"branches": ["develop", "staging"]}
            }
        
        workflow = {
            "name": name,
            "on": triggers,
            "jobs": {
                "deploy": {
                    "runs-on": "ubuntu-latest",
                    "environment": environment,
                    "steps": [
                        {"uses": "actions/checkout@v3"}
                    ]
                }
            }
        }
        
        # Add deployment steps
        workflow["jobs"]["deploy"]["steps"].extend(deploy_steps)
        
        # Write the workflow to file
        with open(workflow_file, 'w') as f:
            yaml.dump(workflow, f, sort_keys=False)
        
        return workflow_file
    
    def create_release_workflow(self, name: str, version_file: str = None) -> str:
        """
        Create a workflow for automated releases.
        
        Args:
            name: Name of the workflow
            version_file: Path to file containing version information (optional)
            
        Returns:
            Path to the created workflow file
        """
        workflow_file = os.path.join(self.workflows_dir, "release.yml")
        
        workflow = {
            "name": name,
            "on": {
                "workflow_dispatch": {
                    "inputs": {
                        "version": {
                            "description": "Version to release",
                            "required": True,
                            "type": "string"
                        },
                        "release_notes": {
                            "description": "Release notes",
                            "required": False,
                            "type": "string"
                        }
                    }
                }
            },
            "jobs": {
                "release": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Create Release",
                            "id": "create_release",
                            "uses": "actions/create-release@v1",
                            "env": {
                                "GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"
                            },
                            "with": {
                                "tag_name": "v${{ github.event.inputs.version }}",
                                "release_name": "Release v${{ github.event.inputs.version }}",
                                "body": "${{ github.event.inputs.release_notes }}",
                                "draft": False,
                                "prerelease": False
                            }
                        }
                    ]
                }
            }
        }
        
        # Add version file update if specified
        if version_file:
            update_version_step = {
                "name": "Update version",
                "run": f"echo \"${{{{ github.event.inputs.version }}}}\" > {version_file}\ngit config --local user.email \"action@github.com\"\ngit config --local user.name \"GitHub Action\"\ngit add {version_file}\ngit commit -m \"Bump version to ${{{{ github.event.inputs.version }}}}\"\ngit push"
            }
            workflow["jobs"]["release"]["steps"].insert(1, update_version_step)
        
        # Write the workflow to file
        with open(workflow_file, 'w') as f:
            yaml.dump(workflow, f, sort_keys=False)
        
        return workflow_file


class GitLabCIManager:
    """
    Specialized manager for GitLab CI workflows.
    
    This class provides GitLab CI-specific functionality for creating and managing workflows.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the GitLab CI Manager.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = repo_path
        self.config_file = os.path.join(repo_path, ".gitlab-ci.yml")
    
    def create_multi_stage_pipeline(self, stages: List[str], jobs: Dict[str, Dict[str, Any]]) -> str:
        """
        Create a multi-stage GitLab CI pipeline.
        
        Args:
            stages: List of pipeline stages
            jobs: Dictionary of jobs
            
        Returns:
            Path to the created pipeline file
        """
        pipeline = {
            "stages": stages
        }
        
        # Add jobs to pipeline
        for job_id, job_config in jobs.items():
            pipeline[job_id] = job_config
        
        # Write the pipeline to file
        with open(self.config_file, 'w') as f:
            yaml.dump(pipeline, f, sort_keys=False)
        
        return self.config_file
    
    def create_auto_devops_pipeline(self, language: str) -> str:
        """
        Create a pipeline using GitLab Auto DevOps templates.
        
        Args:
            language: Programming language
            
        Returns:
            Path to the created pipeline file
        """
        pipeline = {
            "include": [
                {"template": "Auto-DevOps.gitlab-ci.yml"}
            ],
            "variables": {
                "AUTO_DEVOPS_PLATFORM_TARGET": "kubernetes",
                "AUTO_DEVOPS_DEPLOY_STRATEGY": "rolling"
            }
        }
        
        # Add language-specific configurations
        if language.lower() == "python":
            pipeline["variables"]["AUTO_DEVOPS_LANGUAGE"] = "python"
        elif language.lower() in ["node", "nodejs"]:
            pipeline["variables"]["AUTO_DEVOPS_LANGUAGE"] = "nodejs"
        elif language.lower() == "java":
            pipeline["variables"]["AUTO_DEVOPS_LANGUAGE"] = "java"
        
        # Write the pipeline to file
        with open(self.config_file, 'w') as f:
            yaml.dump(pipeline, f, sort_keys=False)
        
        return self.config_file
    
    def create_environment_deployments(self, environments: List[str]) -> str:
        """
        Create a pipeline with deployments to multiple environments.
        
        Args:
            environments: List of environments (e.g., staging, production)
            
        Returns:
            Path to the created pipeline file
        """
        pipeline = {
            "stages": ["build", "test"] + [f"deploy_{env}" for env in environments]
        }
        
        # Add build and test jobs
        pipeline["build"] = {
            "stage": "build",
            "script": ["echo 'Building application'"],
            "artifacts": {
                "paths": ["build/"]
            }
        }
        
        pipeline["test"] = {
            "stage": "test",
            "script": ["echo 'Running tests'"]
        }
        
        # Add deployment jobs for each environment
        for i, env in enumerate(environments):
            needs = ["test"]
            if i > 0:
                needs.append(f"deploy_{environments[i-1]}")
            
            pipeline[f"deploy_{env}"] = {
                "stage": f"deploy_{env}",
                "script": [f"echo 'Deploying to {env}'"],
                "environment": {
                    "name": env,
                    "url": f"https://{env}.example.com"
                },
                "needs": needs
            }
            
            # Add manual approval for production
            if env.lower() == "production":
                pipeline[f"deploy_{env}"]["when"] = "manual"
        
        # Write the pipeline to file
        with open(self.config_file, 'w') as f:
            yaml.dump(pipeline, f, sort_keys=False)
        
        return self.config_file


class CICDTemplateLibrary:
    """
    Library of CI/CD templates for common scenarios.
    
    This class provides pre-defined templates for common CI/CD scenarios.
    """
    
    @staticmethod
    def get_python_template() -> Dict[str, Any]:
        """
        Get a template for Python projects.
        
        Returns:
            Dictionary with Python CI/CD configuration
        """
        return {
            "name": "Python CI",
            "triggers": [TriggerEvent.PUSH, TriggerEvent.PULL_REQUEST],
            "jobs": {
                "lint": {
                    "runs-on": "ubuntu-latest",
                    "stage": "lint",
                    "setup": [
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.9"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install flake8 black isort"
                        }
                    ],
                    "steps": [
                        {
                            "name": "Lint with flake8",
                            "run": "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
                        },
                        {
                            "name": "Check formatting with black",
                            "run": "black --check ."
                        },
                        {
                            "name": "Check imports with isort",
                            "run": "isort --check-only --profile black ."
                        }
                    ]
                },
                "test": {
                    "runs-on": "ubuntu-latest",
                    "stage": "test",
                    "setup": [
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.9"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install pytest pytest-cov\npip install -r requirements.txt"
                        }
                    ],
                    "steps": [
                        {
                            "name": "Test with pytest",
                            "run": "pytest --cov=. --cov-report=xml"
                        }
                    ]
                },
                "build": {
                    "runs-on": "ubuntu-latest",
                    "stage": "build",
                    "needs": ["test", "lint"],
                    "setup": [
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.9"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install build twine"
                        }
                    ],
                    "steps": [
                        {
                            "name": "Build package",
                            "run": "python -m build"
                        },
                        {
                            "name": "Check package",
                            "run": "twine check dist/*"
                        }
                    ]
                }
            }
        }
    
    @staticmethod
    def get_node_template() -> Dict[str, Any]:
        """
        Get a template for Node.js projects.
        
        Returns:
            Dictionary with Node.js CI/CD configuration
        """
        return {
            "name": "Node.js CI",
            "triggers": [TriggerEvent.PUSH, TriggerEvent.PULL_REQUEST],
            "jobs": {
                "lint": {
                    "runs-on": "ubuntu-latest",
                    "stage": "lint",
                    "setup": [
                        {
                            "name": "Set up Node.js",
                            "uses": "actions/setup-node@v3",
                            "with": {"node-version": "16"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "npm ci"
                        }
                    ],
                    "steps": [
                        {
                            "name": "Lint with ESLint",
                            "run": "npm run lint"
                        }
                    ]
                },
                "test": {
                    "runs-on": "ubuntu-latest",
                    "stage": "test",
                    "setup": [
                        {
                            "name": "Set up Node.js",
                            "uses": "actions/setup-node@v3",
                            "with": {"node-version": "16"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "npm ci"
                        }
                    ],
                    "steps": [
                        {
                            "name": "Test with Jest",
                            "run": "npm test"
                        }
                    ]
                },
                "build": {
                    "runs-on": "ubuntu-latest",
                    "stage": "build",
                    "needs": ["test", "lint"],
                    "setup": [
                        {
                            "name": "Set up Node.js",
                            "uses": "actions/setup-node@v3",
                            "with": {"node-version": "16"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "npm ci"
                        }
                    ],
                    "steps": [
                        {
                            "name": "Build",
                            "run": "npm run build"
                        }
                    ]
                }
            }
        }
    
    @staticmethod
    def get_docker_template() -> Dict[str, Any]:
        """
        Get a template for Docker projects.
        
        Returns:
            Dictionary with Docker CI/CD configuration
        """
        return {
            "name": "Docker CI",
            "triggers": [TriggerEvent.PUSH, TriggerEvent.PULL_REQUEST],
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "stage": "build",
                    "steps": [
                        {
                            "name": "Set up Docker Buildx",
                            "uses": "docker/setup-buildx-action@v2"
                        },
                        {
                            "name": "Build Docker image",
                            "uses": "docker/build-push-action@v4",
                            "with": {
                                "context": ".",
                                "push": False,
                                "tags": "myapp:latest",
                                "cache-from": "type=gha",
                                "cache-to": "type=gha,mode=max"
                            }
                        }
                    ]
                },
                "test": {
                    "runs-on": "ubuntu-latest",
                    "stage": "test",
                    "needs": ["build"],
                    "steps": [
                        {
                            "name": "Set up Docker Buildx",
                            "uses": "docker/setup-buildx-action@v2"
                        },
                        {
                            "name": "Build and test",
                            "run": "docker build -t myapp:test --target test ."
                        }
                    ]
                },
                "push": {
                    "runs-on": "ubuntu-latest",
                    "stage": "deploy",
                    "needs": ["test"],
                    "if": "github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')",
                    "steps": [
                        {
                            "name": "Login to DockerHub",
                            "uses": "docker/login-action@v2",
                            "with": {
                                "username": "${{ secrets.DOCKERHUB_USERNAME }}",
                                "password": "${{ secrets.DOCKERHUB_TOKEN }}"
                            }
                        },
                        {
                            "name": "Build and push",
                            "uses": "docker/build-push-action@v4",
                            "with": {
                                "context": ".",
                                "push": True,
                                "tags": "user/myapp:latest"
                            }
                        }
                    ]
                }
            }
        }
    
    @staticmethod
    def get_deployment_template(environment: str) -> Dict[str, Any]:
        """
        Get a template for deployment to a specific environment.
        
        Args:
            environment: Deployment environment (e.g., production, staging)
            
        Returns:
            Dictionary with deployment CI/CD configuration
        """
        # Define triggers based on environment
        if environment.lower() == "production":
            triggers = [TriggerEvent.TAG, TriggerEvent.RELEASE]
        else:
            triggers = [TriggerEvent.PUSH]
        
        return {
            "name": f"Deploy to {environment}",
            "triggers": triggers,
            "jobs": {
                "deploy": {
                    "runs-on": "ubuntu-latest",
                    "stage": "deploy",
                    "steps": [
                        {
                            "name": "Deploy to environment",
                            "run": f"echo 'Deploying to {environment}'"
                        }
                    ]
                }
            }
        }
