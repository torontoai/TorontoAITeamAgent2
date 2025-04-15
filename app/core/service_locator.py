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

"""Service Locator Module

This module provides a lightweight service locator pattern implementation
for components that cannot use dependency injection directly."""

import logging
from typing import Dict, Any, Type, Optional

from app.core.dependency_injection import container, DependencyContainer

logger = logging.getLogger(__name__)

class ServiceLocator:
    """Service Locator for accessing services from global container.
    
    This class provides a static interface to the dependency container
    for components that cannot use dependency injection directly."""
    
    _container = container
    
    @classmethod
    def set_container(cls, container: DependencyContainer):
        """Set the container used by the service locator.
        
        Args:
            container: Dependency container"""
        cls._container = container
        logger.debug("Set container for ServiceLocator")
    
    @classmethod
    def get_service(cls, service_type: Type, name: str = None) -> Any:
        """Get a service from the container.
        
        Args:
            service_type: Type of service to get
            name: Optional name of the service
            
        Returns:
            Service instance"""
        try:
            return cls._container.resolve(service_type, name)
        except Exception as e:
            logger.error(f"Error resolving service {service_type.__name__}: {str(e)}")
            raise
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get the application configuration.
        
        Returns:
            Application configuration"""
        try:
            return cls._container.resolve(Dict[str, Any], "app_config")
        except Exception as e:
            logger.error(f"Error resolving application configuration: {str(e)}")
            return {}
