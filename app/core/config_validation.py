"""
Configuration validation module for TORONTO AI TEAM AGENT.

This module provides utilities for validating configuration settings
to ensure all required settings are provided before system initialization.
"""

import os
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, ValidationError, validator


class ConfigurationError(Exception):
    """Exception raised for configuration validation errors."""
    pass


class ApiKeyRequirement(Enum):
    """Enum representing API key requirement levels."""
    REQUIRED = "required"
    OPTIONAL = "optional"
    CONDITIONAL = "conditional"


class ApiKeyConfig(BaseModel):
    """Model for API key configuration validation."""
    name: str
    environment_variable: str
    requirement: ApiKeyRequirement = ApiKeyRequirement.REQUIRED
    depends_on: Optional[str] = None
    description: str
    
    @validator('depends_on')
    def validate_depends_on(cls, v, values):
        """Validate that depends_on is provided if requirement is CONDITIONAL."""
        if values.get('requirement') == ApiKeyRequirement.CONDITIONAL and not v:
            raise ValueError("depends_on must be provided when requirement is CONDITIONAL")
        return v


class DatabaseConfig(BaseModel):
    """Model for database configuration validation."""
    type: str
    connection_string: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: Optional[str] = None
    
    @validator('connection_string', 'host', 'database_name')
    def validate_required_fields(cls, v, values):
        """Validate that either connection_string or host and database_name are provided."""
        if not values.get('connection_string') and not (values.get('host') and values.get('database_name')):
            raise ValueError("Either connection_string or both host and database_name must be provided")
        return v


class VectorDbConfig(BaseModel):
    """Model for vector database configuration validation."""
    type: str
    api_key: Optional[str] = None
    connection_string: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    
    @validator('type')
    def validate_type(cls, v):
        """Validate that the vector database type is supported."""
        supported_types = {"in_memory", "chroma", "pinecone", "weaviate", "milvus", "faiss"}
        if v not in supported_types:
            raise ValueError(f"Vector database type must be one of {supported_types}")
        return v
    
    @validator('api_key')
    def validate_api_key(cls, v, values):
        """Validate that API key is provided for cloud-based vector databases."""
        cloud_dbs = {"pinecone", "weaviate"}
        if values.get('type') in cloud_dbs and not v:
            raise ValueError(f"API key is required for {values.get('type')}")
        return v


class MultimodalConfig(BaseModel):
    """Model for multimodal configuration validation."""
    enabled: bool = True
    llama4_api_key: Optional[str] = None
    image_processing_enabled: bool = True
    audio_processing_enabled: bool = True
    video_processing_enabled: bool = True
    
    @validator('llama4_api_key')
    def validate_llama4_api_key(cls, v, values):
        """Validate that Llama 4 API key is provided if multimodal is enabled."""
        if values.get('enabled') and not v:
            raise ValueError("Llama 4 API key is required when multimodal is enabled")
        return v


class OrchestrationConfig(BaseModel):
    """Model for orchestration configuration validation."""
    enabled: bool = True
    autogen_api_key: Optional[str] = None
    max_agents: int = Field(default=10, ge=1, le=100)
    
    @validator('autogen_api_key')
    def validate_autogen_api_key(cls, v, values):
        """Validate that AutoGen API key is provided if orchestration is enabled."""
        if values.get('enabled') and not v:
            raise ValueError("AutoGen API key is required when orchestration is enabled")
        return v


class CodeGenerationConfig(BaseModel):
    """Model for code generation configuration validation."""
    enabled: bool = True
    deepseek_api_key: Optional[str] = None
    agentiq_api_key: Optional[str] = None
    
    @validator('deepseek_api_key', 'agentiq_api_key')
    def validate_api_keys(cls, v, values, field):
        """Validate that required API keys are provided if code generation is enabled."""
        if values.get('enabled') and not v:
            raise ValueError(f"{field.name} is required when code generation is enabled")
        return v


class IntegrationConfig(BaseModel):
    """Model for integration configuration validation."""
    jira_enabled: bool = False
    jira_url: Optional[str] = None
    jira_username: Optional[str] = None
    jira_api_token: Optional[str] = None
    
    confluence_enabled: bool = False
    confluence_url: Optional[str] = None
    confluence_username: Optional[str] = None
    confluence_api_token: Optional[str] = None
    
    coursera_enabled: bool = False
    coursera_api_key: Optional[str] = None
    
    @validator('jira_url', 'jira_username', 'jira_api_token')
    def validate_jira_config(cls, v, values, field):
        """Validate that Jira configuration is provided if Jira is enabled."""
        if values.get('jira_enabled') and not v:
            raise ValueError(f"{field.name} is required when Jira integration is enabled")
        return v
    
    @validator('confluence_url', 'confluence_username', 'confluence_api_token')
    def validate_confluence_config(cls, v, values, field):
        """Validate that Confluence configuration is provided if Confluence is enabled."""
        if values.get('confluence_enabled') and not v:
            raise ValueError(f"{field.name} is required when Confluence integration is enabled")
        return v
    
    @validator('coursera_api_key')
    def validate_coursera_config(cls, v, values):
        """Validate that Coursera API key is provided if Coursera is enabled."""
        if values.get('coursera_enabled') and not v:
            raise ValueError("coursera_api_key is required when Coursera integration is enabled")
        return v


class SystemConfig(BaseModel):
    """Main configuration model for the entire system."""
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    database: DatabaseConfig
    vector_db: VectorDbConfig
    multimodal: MultimodalConfig
    orchestration: OrchestrationConfig
    code_generation: CodeGenerationConfig
    integration: IntegrationConfig


def validate_config_file(config_path: str) -> Dict[str, Any]:
    """
    Validate a configuration file against the SystemConfig model.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing the validated configuration
        
    Raises:
        ConfigurationError: If the configuration is invalid
    """
    import yaml
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Validate the configuration
        validated_config = SystemConfig(**config_data)
        return validated_config.dict()
    
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Error parsing YAML configuration: {str(e)}")
    except ValidationError as e:
        raise ConfigurationError(f"Configuration validation error: {str(e)}")
    except Exception as e:
        raise ConfigurationError(f"Unexpected error validating configuration: {str(e)}")


def validate_environment_variables(required_vars: List[str]) -> None:
    """
    Validate that required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
        
    Raises:
        ConfigurationError: If any required environment variables are missing
    """
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise ConfigurationError(f"Missing required environment variables: {', '.join(missing_vars)}")


def generate_example_config() -> Dict[str, Any]:
    """
    Generate an example configuration with placeholder values.
    
    Returns:
        Dict containing an example configuration
    """
    example_config = {
        "environment": "development",
        "debug": True,
        "log_level": "INFO",
        
        "database": {
            "type": "sqlite",
            "connection_string": "sqlite:///toronto_ai_team_agent.db"
        },
        
        "vector_db": {
            "type": "in_memory"
        },
        
        "multimodal": {
            "enabled": True,
            "llama4_api_key": "your_llama4_api_key_here",
            "image_processing_enabled": True,
            "audio_processing_enabled": True,
            "video_processing_enabled": True
        },
        
        "orchestration": {
            "enabled": True,
            "autogen_api_key": "your_autogen_api_key_here",
            "max_agents": 10
        },
        
        "code_generation": {
            "enabled": True,
            "deepseek_api_key": "your_deepseek_api_key_here",
            "agentiq_api_key": "your_agentiq_api_key_here"
        },
        
        "integration": {
            "jira_enabled": False,
            "jira_url": "https://your-instance.atlassian.net",
            "jira_username": "your_jira_username",
            "jira_api_token": "your_jira_api_token",
            
            "confluence_enabled": False,
            "confluence_url": "https://your-instance.atlassian.net",
            "confluence_username": "your_confluence_username",
            "confluence_api_token": "your_confluence_api_token",
            
            "coursera_enabled": False,
            "coursera_api_key": "your_coursera_api_key"
        }
    }
    
    return example_config


def write_example_config(output_path: str) -> None:
    """
    Write an example configuration file.
    
    Args:
        output_path: Path to write the example configuration file
        
    Raises:
        ConfigurationError: If there's an error writing the file
    """
    import yaml
    
    try:
        example_config = generate_example_config()
        
        with open(output_path, 'w') as f:
            yaml.dump(example_config, f, default_flow_style=False, sort_keys=False)
            
    except Exception as e:
        raise ConfigurationError(f"Error writing example configuration: {str(e)}")
