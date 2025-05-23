"""TORONTO AI TEAM AGENT - Integration Configuration

This module provides configuration settings for the integration with Jira and Confluence.

Copyright (c) 2025 TORONTO AI
Created by David Tadeusz Chudak
All rights reserved."""

from dataclasses import dataclass
from typing import Dict, Optional, List
import os
from enum import Enum


class IntegrationType(Enum):
    """Enum for supported integration types."""
    JIRA = "jira"
    CONFLUENCE = "confluence"


@dataclass
class JiraConfig:
    """Configuration for Jira integration."""
    url: str
    api_token: str
    username: str
    project_key_mapping: Dict[str, str]
    webhook_secret: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30
    sync_interval_minutes: int = 15
    issue_types_mapping: Dict[str, str] = None
    status_mapping: Dict[str, str] = None
    priority_mapping: Dict[str, str] = None
    custom_field_mapping: Dict[str, str] = None


@dataclass
class ConfluenceConfig:
    """Configuration for Confluence integration."""
    url: str
    api_token: str
    username: str
    space_key_mapping: Dict[str, str]
    webhook_secret: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30
    sync_interval_minutes: int = 15
    content_type_mapping: Dict[str, str] = None
    label_mapping: Dict[str, str] = None


@dataclass
class IntegrationConfig:
    """Main configuration for all integrations."""
    jira: Optional[JiraConfig] = None
    confluence: Optional[ConfluenceConfig] = None
    enabled_integrations: List[IntegrationType] = None
    sync_database_path: str = "integration_sync.db"
    log_level: str = "INFO"
    log_file: str = "integration.log"


def load_config_from_env() -> IntegrationConfig:
    """Load integration configuration from environment variables.
    
    Returns:
        IntegrationConfig: The loaded configuration"""
    enabled_integrations = []
    
    # Parse enabled integrations
    if os.environ.get("ENABLE_JIRA_INTEGRATION", "false").lower() == "true":
        enabled_integrations.append(IntegrationType.JIRA)
    
    if os.environ.get("ENABLE_CONFLUENCE_INTEGRATION", "false").lower() == "true":
        enabled_integrations.append(IntegrationType.CONFLUENCE)
    
    # Create Jira config if enabled
    jira_config = None
    if IntegrationType.JIRA in enabled_integrations:
        jira_config = JiraConfig(
            url=os.environ.get("JIRA_URL", ""),
            api_token=os.environ.get("JIRA_API_TOKEN", ""),
            username=os.environ.get("JIRA_USERNAME", ""),
            project_key_mapping={},  # This would be loaded from a more complex source
            webhook_secret=os.environ.get("JIRA_WEBHOOK_SECRET"),
            max_retries=int(os.environ.get("JIRA_MAX_RETRIES", "3")),
            timeout=int(os.environ.get("JIRA_TIMEOUT", "30")),
            sync_interval_minutes=int(os.environ.get("JIRA_SYNC_INTERVAL", "15"))
        )
    
    # Create Confluence config if enabled
    confluence_config = None
    if IntegrationType.CONFLUENCE in enabled_integrations:
        confluence_config = ConfluenceConfig(
            url=os.environ.get("CONFLUENCE_URL", ""),
            api_token=os.environ.get("CONFLUENCE_API_TOKEN", ""),
            username=os.environ.get("CONFLUENCE_USERNAME", ""),
            space_key_mapping={},  # This would be loaded from a more complex source
            webhook_secret=os.environ.get("CONFLUENCE_WEBHOOK_SECRET"),
            max_retries=int(os.environ.get("CONFLUENCE_MAX_RETRIES", "3")),
            timeout=int(os.environ.get("CONFLUENCE_TIMEOUT", "30")),
            sync_interval_minutes=int(os.environ.get("CONFLUENCE_SYNC_INTERVAL", "15"))
        )
    
    return IntegrationConfig(
        jira=jira_config,
        confluence=confluence_config,
        enabled_integrations=enabled_integrations,
        sync_database_path=os.environ.get("INTEGRATION_SYNC_DB", "integration_sync.db"),
        log_level=os.environ.get("INTEGRATION_LOG_LEVEL", "INFO"),
        log_file=os.environ.get("INTEGRATION_LOG_FILE", "integration.log")
    )


def load_config_from_file(config_file: str) -> IntegrationConfig:
    """Load integration configuration from a file.
    
    Args:
        config_file: Path to the configuration file
        
    Returns:
        IntegrationConfig: The loaded configuration"""
    # This would be implemented to load from YAML, JSON, etc.
    # For now, we'll just use the environment variables
    return load_config_from_env()


# Default configuration instance
default_config = load_config_from_env()
