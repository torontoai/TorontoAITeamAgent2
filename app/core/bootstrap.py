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

"""Application Bootstrap Module

This module initializes the application and sets up the dependency injection container."""

import logging
from typing import Dict, Any, Optional

from app.core.dependency_injection import container, DependencyContainer
from app.training.vector_db.interface import VectorDatabase
from app.training.vector_db.factory import VectorDatabaseFactory
from app.training.vector_db.manager import VectorDatabaseManager
from app.training.vector_db.repository import VectorRepository
from app.agent.project_manager.services.task_management import TaskManagementService
from app.agent.project_manager.services.team_coordination import TeamCoordinationService
from app.agent.project_manager.services.stakeholder_communication import StakeholderCommunicationService
from app.agent.project_manager.services.risk_management import RiskManagementService
from app.agent.project_manager.services.decision_making import DecisionMakingService
from app.agent.project_manager.services.reporting import ReportingService
from app.technical_capabilities.services.code_generation import CodeGenerationService
from app.technical_capabilities.services.code_review import CodeReviewService
from app.technical_capabilities.services.test_generation import TestGenerationService
from app.technical_capabilities.services.documentation_generation import DocumentationGenerationService
from app.technical_capabilities.services.api_design import ApiDesignService
from app.integration.jira_client import JiraClient
from app.integration.confluence_client import ConfluenceClient
from app.integration.sync_manager import SyncManager
from app.integration.auth import AuthenticationManager
from app.training.coursera_integration import CourseraApiClient
from app.training.coursera_training import CourseraTrainingService

logger = logging.getLogger(__name__)

def bootstrap_application(config: Dict[str, Any] = None) -> DependencyContainer:
    """Bootstrap the application and set up the dependency injection container.
    
    Args:
        config: Application configuration
        
    Returns:
        Configured dependency injection container"""
    logger.info("Bootstrapping application...")
    
    # Use provided config or empty dict
    config = config or {}
    
    # Register core services
    register_core_services(container, config)
    
    # Register vector database services
    register_vector_db_services(container, config)
    
    # Register project manager services
    register_project_manager_services(container, config)
    
    # Register technical capability services
    register_technical_capability_services(container, config)
    
    # Register integration services
    register_integration_services(container, config)
    
    # Register training services
    register_training_services(container, config)
    
    logger.info("Application bootstrap complete")
    return container

def register_core_services(container: DependencyContainer, config: Dict[str, Any]):
    """Register core services with the container.
    
    Args:
        container: Dependency container
        config: Application configuration"""
    logger.info("Registering core services...")
    
    # Register configuration
    container.register_instance(config, Dict[str, Any], "app_config")

def register_vector_db_services(container: DependencyContainer, config: Dict[str, Any]):
    """Register vector database services with the container.
    
    Args:
        container: Dependency container
        config: Application configuration"""
    logger.info("Registering vector database services...")
    
    # Extract vector DB config
    vector_db_config = config.get("vector_db", {})
    
    # Register factory
    container.register(VectorDatabaseFactory, singleton=True)
    
    # Register manager
    container.register(VectorDatabaseManager, singleton=True)
    
    # Register repository
    container.register(VectorRepository, singleton=True)
    
    # Register default vector database
    default_backend = vector_db_config.get("default_backend", "in_memory")
    factory = container.resolve(VectorDatabaseFactory)
    vector_db = factory.create(default_backend, vector_db_config)
    container.register_instance(vector_db, VectorDatabase)

def register_project_manager_services(container: DependencyContainer, config: Dict[str, Any]):
    """Register project manager services with the container.
    
    Args:
        container: Dependency container
        config: Application configuration"""
    logger.info("Registering project manager services...")
    
    # Extract project manager config
    pm_config = config.get("project_manager", {})
    
    # Register services
    container.register(TaskManagementService, singleton=True)
    container.register(TeamCoordinationService, singleton=True)
    container.register(StakeholderCommunicationService, singleton=True)
    container.register(RiskManagementService, singleton=True)
    container.register(DecisionMakingService, singleton=True)
    container.register(ReportingService, singleton=True)
    
    # Resolve services for dependency injection
    task_service = container.resolve(TaskManagementService)
    team_service = container.resolve(TeamCoordinationService)
    stakeholder_service = container.resolve(StakeholderCommunicationService)
    risk_service = container.resolve(RiskManagementService)
    decision_service = container.resolve(DecisionMakingService)
    reporting_service = container.resolve(ReportingService)
    
    # Inject dependencies
    team_service.set_task_service(task_service)
    stakeholder_service.set_task_service(task_service)
    risk_service.set_task_service(task_service)
    decision_service.set_task_service(task_service)
    decision_service.set_stakeholder_service(stakeholder_service)
    reporting_service.set_task_service(task_service)
    reporting_service.set_team_service(team_service)
    reporting_service.set_stakeholder_service(stakeholder_service)
    reporting_service.set_risk_service(risk_service)
    reporting_service.set_decision_service(decision_service)

def register_technical_capability_services(container: DependencyContainer, config: Dict[str, Any]):
    """Register technical capability services with the container.
    
    Args:
        container: Dependency container
        config: Application configuration"""
    logger.info("Registering technical capability services...")
    
    # Extract technical capabilities config
    tc_config = config.get("technical_capabilities", {})
    
    # Register services
    container.register(CodeGenerationService, singleton=True)
    container.register(CodeReviewService, singleton=True)
    container.register(TestGenerationService, singleton=True)
    container.register(DocumentationGenerationService, singleton=True)
    container.register(ApiDesignService, singleton=True)

def register_integration_services(container: DependencyContainer, config: Dict[str, Any]):
    """Register integration services with the container.
    
    Args:
        container: Dependency container
        config: Application configuration"""
    logger.info("Registering integration services...")
    
    # Extract integration config
    integration_config = config.get("integration", {})
    
    # Register services
    container.register(AuthenticationManager, singleton=True)
    container.register(JiraClient, singleton=True)
    container.register(ConfluenceClient, singleton=True)
    container.register(SyncManager, singleton=True)
    
    # Resolve services for dependency injection
    auth_manager = container.resolve(AuthenticationManager)
    jira_client = container.resolve(JiraClient)
    confluence_client = container.resolve(ConfluenceClient)
    sync_manager = container.resolve(SyncManager)
    
    # Inject dependencies
    jira_client.set_auth_manager(auth_manager)
    confluence_client.set_auth_manager(auth_manager)
    sync_manager.set_jira_client(jira_client)
    sync_manager.set_confluence_client(confluence_client)

def register_training_services(container: DependencyContainer, config: Dict[str, Any]):
    """Register training services with the container.
    
    Args:
        container: Dependency container
        config: Application configuration"""
    logger.info("Registering training services...")
    
    # Extract training config
    training_config = config.get("training", {})
    
    # Register services
    container.register(CourseraApiClient, singleton=True)
    container.register(CourseraTrainingService, singleton=True)
    
    # Resolve services for dependency injection
    coursera_client = container.resolve(CourseraApiClient)
    coursera_training = container.resolve(CourseraTrainingService)
    vector_repo = container.resolve(VectorRepository)
    
    # Inject dependencies
    coursera_training.set_api_client(coursera_client)
    coursera_training.set_vector_repository(vector_repo)
