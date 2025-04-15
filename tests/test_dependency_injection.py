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

"""
Test Module for Dependency Injection Framework

This module contains unit tests for the dependency injection framework.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.dependency_injection import DependencyContainer
from app.core.service_locator import ServiceLocator
from app.core.config import ConfigurationManager

# Test classes for dependency injection
class TestService:
    def __init__(self, name="default"):
        self.name = name

class TestDependentService:
    def __init__(self, service: TestService):
        self.service = service

class TestServiceWithSetter:
    def __init__(self):
        self.dependency = None
    
    def set_dependency(self, dependency):
        self.dependency = dependency

class DependencyInjectionTests(unittest.TestCase):
    """
    Unit tests for the dependency injection framework.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.container = DependencyContainer()
    
    def test_register_and_resolve(self):
        """Test registering and resolving a service."""
        # Register service
        self.container.register(TestService)
        
        # Resolve service
        service = self.container.resolve(TestService)
        
        # Assert
        self.assertIsInstance(service, TestService)
        self.assertEqual(service.name, "default")
    
    def test_register_with_factory(self):
        """Test registering a service with a factory function."""
        # Register service with factory
        self.container.register(TestService, lambda c: TestService("factory"))
        
        # Resolve service
        service = self.container.resolve(TestService)
        
        # Assert
        self.assertIsInstance(service, TestService)
        self.assertEqual(service.name, "factory")
    
    def test_register_instance(self):
        """Test registering an existing instance."""
        # Create instance
        instance = TestService("instance")
        
        # Register instance
        self.container.register_instance(instance)
        
        # Resolve service
        service = self.container.resolve(TestService)
        
        # Assert
        self.assertIs(service, instance)
        self.assertEqual(service.name, "instance")
    
    def test_singleton(self):
        """Test singleton lifecycle."""
        # Register service as singleton
        self.container.register(TestService, singleton=True)
        
        # Resolve service twice
        service1 = self.container.resolve(TestService)
        service2 = self.container.resolve(TestService)
        
        # Assert
        self.assertIs(service1, service2)
    
    def test_transient(self):
        """Test transient lifecycle."""
        # Register service as transient
        self.container.register(TestService, singleton=False)
        
        # Resolve service twice
        service1 = self.container.resolve(TestService)
        service2 = self.container.resolve(TestService)
        
        # Assert
        self.assertIsNot(service1, service2)
    
    def test_dependency_injection(self):
        """Test dependency injection."""
        # Register services
        self.container.register(TestService)
        self.container.register(TestDependentService)
        
        # Resolve dependent service
        dependent = self.container.resolve(TestDependentService)
        
        # Assert
        self.assertIsInstance(dependent, TestDependentService)
        self.assertIsInstance(dependent.service, TestService)
    
    def test_named_registration(self):
        """Test named registration."""
        # Register services with different names
        self.container.register(TestService, lambda c: TestService("service1"), name="service1")
        self.container.register(TestService, lambda c: TestService("service2"), name="service2")
        
        # Resolve services
        service1 = self.container.resolve(TestService, name="service1")
        service2 = self.container.resolve(TestService, name="service2")
        
        # Assert
        self.assertEqual(service1.name, "service1")
        self.assertEqual(service2.name, "service2")
    
    def test_inject_method(self):
        """Test inject method."""
        # Register services
        self.container.register(TestService)
        self.container.register(TestServiceWithSetter)
        
        # Resolve service
        service = self.container.resolve(TestServiceWithSetter)
        
        # Inject dependencies
        self.container.inject(service)
        
        # Assert
        self.assertIsNone(service.dependency)  # Not injected because method name doesn't match pattern
        
        # Set the dependency manually
        test_service = self.container.resolve(TestService)
        service.set_dependency(test_service)
        
        # Assert
        self.assertIsInstance(service.dependency, TestService)
    
    def test_type_mapping(self):
        """Test type mapping."""
        # Create interface and implementation
        class IService:
            pass
        
        class ServiceImpl(IService):
            pass
        
        # Register type mapping
        self.container.register_type(IService, ServiceImpl)
        self.container.register(ServiceImpl)
        
        # Resolve interface
        service = self.container.resolve(IService)
        
        # Assert
        self.assertIsInstance(service, ServiceImpl)

class ServiceLocatorTests(unittest.TestCase):
    """
    Unit tests for the service locator.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.container = DependencyContainer()
        ServiceLocator.set_container(self.container)
    
    def test_get_service(self):
        """Test getting a service from the service locator."""
        # Register service
        self.container.register(TestService)
        
        # Get service
        service = ServiceLocator.get_service(TestService)
        
        # Assert
        self.assertIsInstance(service, TestService)
    
    def test_get_config(self):
        """Test getting configuration from the service locator."""
        # Register config
        config = {"key": "value"}
        self.container.register_instance(config, dict, "app_config")
        
        # Get config
        result = ServiceLocator.get_config()
        
        # Assert
        self.assertEqual(result, config)

class ConfigurationManagerTests(unittest.TestCase):
    """
    Unit tests for the configuration manager.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.config_manager = ConfigurationManager()
    
    def test_get_and_set(self):
        """Test getting and setting configuration values."""
        # Set value
        self.config_manager.set("test.key", "value")
        
        # Get value
        value = self.config_manager.get("test.key")
        
        # Assert
        self.assertEqual(value, "value")
    
    def test_get_with_default(self):
        """Test getting a configuration value with a default."""
        # Get non-existent value with default
        value = self.config_manager.get("non.existent.key", "default")
        
        # Assert
        self.assertEqual(value, "default")
    
    def test_get_all(self):
        """Test getting all configuration values."""
        # Set values
        self.config_manager.set("test.key1", "value1")
        self.config_manager.set("test.key2", "value2")
        
        # Get all values
        config = self.config_manager.get_all()
        
        # Assert
        self.assertEqual(config["test"]["key1"], "value1")
        self.assertEqual(config["test"]["key2"], "value2")
    
    @patch("os.environ", {"TEST_PREFIX__KEY": "value"})
    def test_load_from_env(self):
        """Test loading configuration from environment variables."""
        # Load from environment
        self.config_manager._load_from_env("TEST_PREFIX__")
        
        # Get value
        value = self.config_manager.get("key")
        
        # Assert
        self.assertEqual(value, "value")
    
    def test_convert_value(self):
        """Test converting string values to appropriate types."""
        # Test boolean conversion
        self.assertEqual(self.config_manager._convert_value("true"), True)
        self.assertEqual(self.config_manager._convert_value("false"), False)
        
        # Test null conversion
        self.assertIsNone(self.config_manager._convert_value("null"))
        self.assertIsNone(self.config_manager._convert_value("none"))
        
        # Test number conversion
        self.assertEqual(self.config_manager._convert_value("123"), 123)
        self.assertEqual(self.config_manager._convert_value("123.45"), 123.45)
        
        # Test string
        self.assertEqual(self.config_manager._convert_value("hello"), "hello")

if __name__ == "__main__":
    unittest.main()
