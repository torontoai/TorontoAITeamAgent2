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
Real-time collaboration demonstration script for TORONTO AI Team Agent Team AI.

This script demonstrates the real-time collaboration capabilities
of the multi-agent system with a practical example scenario.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.project_manager import ProjectManagerAgent
from app.agent.product_manager import ProductManagerAgent
from app.agent.developer import DeveloperAgent
from app.agent.additional_roles import SystemArchitectAgent, QATestingSpecialistAgent
from app.collaboration.communication_framework import AgentCommunicationFramework
from app.collaboration.framework import RealTimeCollaborationFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'demo.log'))
    ]
)
logger = logging.getLogger(__name__)

class CollaborationDemo:
    """
    Demonstration of real-time collaboration between agents.
    """
    
    def __init__(self, config_path):
        """
        Initialize the collaboration demo.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.agents = {}
        self.comm_framework = AgentCommunicationFramework()
        self.collab_framework = RealTimeCollaborationFramework(self.comm_framework)
        self.session_id = None
        
        logger.info(f"Initialized collaboration demo with config from {config_path}")
    
    def _load_config(self):
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        logger.info(f"Loaded configuration: {config['system']['name']} v{config['system']['version']}")
        return config
    
    async def setup_agents(self):
        """
        Set up agent instances for the demo.
        
        Returns:
            Dictionary of deployed agents
        """
        agent_configs = self.config['agents']
        
        # Create agent instances
        for role, agent_config in agent_configs.items():
            if not agent_config.get('enabled', True):
                logger.info(f"Agent {agent_config['id']} ({role}) is disabled, skipping")
                continue
            
            try:
                agent = self._create_agent_instance(role, agent_config)
                self.agents[agent_config['id']] = agent
                logger.info(f"Set up agent {agent_config['id']} with role {role}")
            except Exception as e:
                logger.error(f"Error setting up agent {agent_config['id']}: {str(e)}")
        
        logger.info(f"Set up {len(self.agents)} agents")
        return self.agents
    
    def _create_agent_instance(self, role, config):
        """
        Create an agent instance based on role.
        
        Args:
            role: Agent role
            config: Agent configuration
            
        Returns:
            Agent instance
        """
        agent_classes = {
            "project_manager": ProjectManagerAgent,
            "product_manager": ProductManagerAgent,
            "developer": DeveloperAgent,
            "system_architect": SystemArchitectAgent,
            "qa_testing_specialist": QATestingSpecialistAgent
        }
        
        if role not in agent_classes:
            raise ValueError(f"Unknown agent role: {role}")
        
        agent_class = agent_classes[role]
        return agent_class(config)
    
    async def start_feature_development_session(self):
        """
        Start a feature development collaboration session.
        
        Returns:
            Session creation result
        """
        # Use all agents for this demo
        participants = list(self.agents.keys())
        
        # Use the project manager as the initiator
        pm_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                           if agent.__class__.__name__ == "ProjectManagerAgent"), participants[0])
        
        # Create session
        result = await self.collab_framework.create_collaboration_session({
            "name": "User Authentication Feature Development",
            "description": "Collaborative session to design and implement user authentication",
            "participants": participants,
            "initiator": pm_agent_id,
            "context": {
                "feature": "user_authentication",
                "priority": "high",
                "deadline": (datetime.now() + timedelta(days=14)).isoformat()
            },
            "session_type": "feature_development"
        })
        
        if result.get("success"):
            self.session_id = result["session_id"]
            logger.info(f"Started feature development session: {self.session_id}")
        else:
            logger.error(f"Failed to start feature development session: {result.get('message')}")
        
        return result
    
    async def demonstrate_real_time_collaboration(self):
        """
        Demonstrate real-time collaboration between agents.
        
        Returns:
            Demonstration results
        """
        if not self.session_id:
            logger.error("No active session found")
            return {
                "success": False,
                "message": "No active session found"
            }
        
        # Get agent IDs by role
        pm_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                           if agent.__class__.__name__ == "ProjectManagerAgent"), None)
        product_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                                if agent.__class__.__name__ == "ProductManagerAgent"), None)
        arch_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                             if agent.__class__.__name__ == "SystemArchitectAgent"), None)
        dev_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                            if agent.__class__.__name__ == "DeveloperAgent"), None)
        qa_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                           if agent.__class__.__name__ == "QATestingSpecialistAgent"), None)
        
        # Store all demonstration steps
        demo_steps = []
        
        # Step 1: Project Manager initiates the feature development
        step1 = await self.collab_framework.send_collaboration_message({
            "session_id": self.session_id,
            "from": pm_agent_id,
            "content": {
                "type": "feature_initiation",
                "feature": "User Authentication",
                "description": "Implement secure user authentication with multiple providers",
                "priority": "high",
                "deadline": (datetime.now() + timedelta(days=14)).isoformat()
            },
            "message_type": "project_management",
            "metadata": {
                "step": "initiation"
            }
        })
        demo_steps.append(("Project Manager Initiates Feature", step1))
        logger.info("Step 1: Project Manager initiated feature development")
        
        # Step 2: Product Manager defines requirements
        step2 = await self.collab_framework.update_shared_state({
            "session_id": self.session_id,
            "agent_id": product_agent_id,
            "updates": {
                "requirements": {
                    "auth_methods": ["email", "google", "github", "microsoft"],
                    "security_features": ["2FA", "password policies", "account lockout"],
                    "user_experience": {
                        "login_flow": "streamlined",
                        "registration_flow": "minimal friction",
                        "password_recovery": "self-service"
                    }
                }
            },
            "operation": "merge"
        })
        demo_steps.append(("Product Manager Defines Requirements", step2))
        logger.info("Step 2: Product Manager defined requirements")
        
        # Step 3: System Architect proposes architecture
        step3 = await self.collab_framework.add_collaboration_artifact({
            "session_id": self.session_id,
            "agent_id": arch_agent_id,
            "name": "authentication_architecture.md",
            "type": "architecture",
            "content": """# Authentication System Architecture

## Components
1. **AuthService** - Core authentication logic
2. **UserRepository** - User data storage and retrieval
3. **TokenManager** - JWT token generation and validation
4. **OAuthProvider** - Integration with external OAuth providers
5. **SecurityPolicies** - Password policies and security rules

## Authentication Flow
1. User initiates login
2. System validates credentials or redirects to OAuth provider
3. Upon successful authentication, JWT token is generated
4. Token is validated on subsequent requests

## Security Considerations
- All passwords hashed with bcrypt
- HTTPS required for all authentication endpoints
- Rate limiting implemented for failed attempts
- Session timeout after 30 minutes of inactivity
""",
            "metadata": {
                "format": "markdown",
                "version": "1.0"
            }
        })
        demo_steps.append(("System Architect Proposes Architecture", step3))
        logger.info("Step 3: System Architect proposed architecture")
        
        # Step 4: Developer responds with implementation plan
        step4 = await self.collab_framework.send_collaboration_message({
            "session_id": self.session_id,
            "from": dev_agent_id,
            "content": {
                "type": "implementation_plan",
                "components": [
                    {
                        "name": "AuthService",
                        "estimated_time": "3 days",
                        "dependencies": []
                    },
                    {
                        "name": "UserRepository",
                        "estimated_time": "2 days",
                        "dependencies": []
                    },
                    {
                        "name": "TokenManager",
                        "estimated_time": "1 day",
                        "dependencies": ["AuthService"]
                    },
                    {
                        "name": "OAuthProvider",
                        "estimated_time": "4 days",
                        "dependencies": ["AuthService", "TokenManager"]
                    },
                    {
                        "name": "SecurityPolicies",
                        "estimated_time": "2 days",
                        "dependencies": ["AuthService"]
                    }
                ],
                "total_estimated_time": "12 days"
            },
            "message_type": "development",
            "metadata": {
                "confidence": "high"
            }
        })
        demo_steps.append(("Developer Provides Implementation Plan", step4))
        logger.info("Step 4: Developer provided implementation plan")
        
        # Step 5: QA Specialist creates test plan
        step5 = await self.collab_framework.add_collaboration_artifact({
            "session_id": self.session_id,
            "agent_id": qa_agent_id,
            "name": "authentication_test_plan.md",
            "type": "test_plan",
            "content": """# Authentication Test Plan

## Functional Tests
1. User registration with email
2. User login with email/password
3. OAuth authentication with all providers
4. Password reset flow
5. Account lockout after failed attempts
6. Two-factor authentication

## Security Tests
1. Password policy enforcement
2. Token expiration and refresh
3. CSRF protection
4. XSS vulnerability testing
5. SQL injection testing
6. Rate limiting effectiveness

## Performance Tests
1. Authentication response time under load
2. Concurrent authentication requests
3. Database connection pool optimization

## User Experience Tests
1. Login flow usability
2. Error message clarity
3. Mobile responsiveness
4. Accessibility compliance
""",
            "metadata": {
                "format": "markdown",
                "version": "1.0"
            }
        })
        demo_steps.append(("QA Specialist Creates Test Plan", step5))
        logger.info("Step 5: QA Specialist created test plan")
        
        # Step 6: Project Manager updates shared state with timeline
        step6 = await self.collab_framework.update_shared_state({
            "session_id": self.session_id,
            "agent_id": pm_agent_id,
            "updates": {
                "timeline": {
                    "design_phase": {
                        "start_date": datetime.now().isoformat(),
                        "end_date": (datetime.now() + timedelta(days=3)).isoformat(),
                        "status": "in_progress"
                    },
                    "development_phase": {
                        "start_date": (datetime.now() + timedelta(days=3)).isoformat(),
                        "end_date": (datetime.now() + timedelta(days=10)).isoformat(),
                        "status": "planned"
                    },
                    "testing_phase": {
                        "start_date": (datetime.now() + timedelta(days=10)).isoformat(),
                        "end_date": (datetime.now() + timedelta(days=13)).isoformat(),
                        "status": "planned"
                    },
                    "deployment_phase": {
                        "start_date": (datetime.now() + timedelta(days=13)).isoformat(),
                        "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
                        "status": "planned"
                    }
                }
            },
            "operation": "merge"
        })
        demo_steps.append(("Project Manager Updates Timeline", step6))
        logger.info("Step 6: Project Manager updated timeline")
        
        # Step 7: Developer adds code artifact
        step7 = await self.collab_framework.add_collaboration_artifact({
            "session_id": self.session_id,
            "agent_id": dev_agent_id,
            "name": "auth_service.py",
            "type": "code",
            "content": """from typing import Dict, Any, Optional
import bcrypt
import jwt
from datetime import datetime, timedelta

class AuthService:
    def __init__(self, user_repository, token_manager):
        self.user_repository = user_repository
        self.token_manager = token_manager
        self.security_policies = SecurityPolicies()
    
    async def register_user(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        # Validate password against security policies
        if not self.security_policies.validate_password(password):
            return {
                "success": False,
                "message": "Password does not meet security requirements"
            }
        
        # Check if user already exists
        existing_user = await self.user_repository.find_by_email(email)
        if existing_user:
            return {
                "success": False,
                "message": "User with this email already exists"
            }
        
        # Hash password
        hashed_password = self._hash_password(password)
        
        # Create user
        user = {
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now().isoformat(),
            **user_data
        }
        
        # Save user
        user_id = await self.user_repository.create(user)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id
        }
    
    async def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        # Get user
        user = await self.user_repository.find_by_email(email)
        if not user:
            return {
                "success": False,
                "message": "Invalid email or password"
            }
        
        # Verify password
        if not self._verify_password(password, user["password"]):
            # Update failed login attempts
            await self.security_policies.record_failed_login(email)
            
            return {
                "success": False,
                "message": "Invalid email or password"
            }
        
        # Check if account is locked
        if await self.security_policies.is_account_locked(email):
            return {
                "success": False,
                "message": "Account is locked due to too many failed attempts"
            }
        
        # Generate token
        token = await self.token_manager.generate_token(user)
        
        return {
            "success": True,
            "message": "Authentication successful",
            "token": token,
            "user": {k: v for k, v in user.items() if k != "password"}
        }
    
    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())


class SecurityPolicies:
    def __init__(self):
        self.password_min_length = 8
        self.password_requires_uppercase = True
        self.password_requires_lowercase = True
        self.password_requires_number = True
        self.password_requires_special = True
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        
        # In a real implementation, this would be stored in a database
        self.failed_attempts = {}
    
    def validate_password(self, password: str) -> bool:
        if len(password) < self.password_min_length:
            return False
        
        if self.password_requires_uppercase and not any(c.isupper() for c in password):
            return False
        
        if self.password_requires_lowercase and not any(c.islower() for c in password):
            return False
        
        if self.password_requires_number and not any(c.isdigit() for c in password):
            return False
        
        if self.password_requires_special and not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~" for c in password):
            return False
        
        return True
    
    async def record_failed_login(self, email: str) -> None:
        if email not in self.failed_attempts:
            self.failed_attempts[email] = {
                "count": 0,
                "last_attempt": None,
                "locked_until": None
            }
        
        self.failed_attempts[email]["count"] += 1
        self.failed_attempts[email]["last_attempt"] = datetime.now()
        
        if self.failed_attempts[email]["count"] >= self.max_failed_attempts:
            self.failed_attempts[email]["locked_until"] = datetime.now() + self.lockout_duration
    
    async def is_account_locked(self, email: str) -> bool:
        if email not in self.failed_attempts:
            return False
        
        if self.failed_attempts[email]["locked_until"] is None:
            return False
        
        if datetime.now() > self.failed_attempts[email]["locked_until"]:
            # Reset lockout
            self.failed_attempts[email]["locked_until"] = None
            self.failed_attempts[email]["count"] = 0
            return False
        
        return True
""",
            "metadata": {
                "language": "python",
                "component": "AuthService"
            }
        })
        demo_steps.append(("Developer Adds Code Artifact", step7))
        logger.info("Step 7: Developer added code artifact")
        
        # Step 8: System Architect reviews code and provides feedback
        step8 = await self.collab_framework.send_collaboration_message({
            "session_id": self.session_id,
            "from": arch_agent_id,
            "content": {
                "type": "code_review",
                "artifact_id": step7["artifact_id"],
                "feedback": [
                    {
                        "type": "suggestion",
                        "location": "AuthService.authenticate",
                        "description": "Consider adding rate limiting for authentication attempts by IP address"
                    },
                    {
                        "type": "improvement",
                        "location": "SecurityPolicies.record_failed_login",
                        "description": "In production, this should use a persistent store like Redis or a database"
                    },
                    {
                        "type": "positive",
                        "location": "AuthService._hash_password",
                        "description": "Good use of bcrypt for password hashing"
                    }
                ],
                "overall_assessment": "Good implementation with proper security practices. Consider the suggestions for production readiness."
            },
            "message_type": "review",
            "metadata": {
                "priority": "medium"
            }
        })
        demo_steps.append(("System Architect Reviews Code", step8))
        logger.info("Step 8: System Architect reviewed code")
        
        # Step 9: QA Specialist adds test cases
        step9 = await self.collab_framework.add_collaboration_artifact({
            "session_id": self.session_id,
            "agent_id": qa_agent_id,
            "name": "auth_service_tests.py",
            "type": "test_code",
            "content": """import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from auth_service import AuthService, SecurityPolicies

@pytest.fixture
def user_repository():
    repo = AsyncMock()
    repo.find_by_email = AsyncMock()
    repo.create = AsyncMock()
    return repo

@pytest.fixture
def token_manager():
    manager = AsyncMock()
    manager.generate_token = AsyncMock(return_value="test_token")
    return manager

@pytest.fixture
def auth_service(user_repository, token_manager):
    return AuthService(user_repository, token_manager)

class TestAuthService:
    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, user_repository):
        # Setup
        user_repository.find_by_email.return_value = None
        user_repository.create.return_value = "user123"
        
        # Execute
        result = await auth_service.register_user(
            "test@example.com", 
            "SecureP@ss123", 
            {"name": "Test User"}
        )
        
        # Verify
        assert result["success"] is True
        assert result["user_id"] == "user123"
        assert user_repository.create.called
    
    @pytest.mark.asyncio
    async def test_register_user_existing_email(self, auth_service, user_repository):
        # Setup
        user_repository.find_by_email.return_value = {"email": "test@example.com"}
        
        # Execute
        result = await auth_service.register_user(
            "test@example.com", 
            "SecureP@ss123", 
            {"name": "Test User"}
        )
        
        # Verify
        assert result["success"] is False
        assert "already exists" in result["message"]
        assert not user_repository.create.called
    
    @pytest.mark.asyncio
    async def test_register_user_weak_password(self, auth_service, user_repository):
        # Setup
        user_repository.find_by_email.return_value = None
        
        # Execute
        result = await auth_service.register_user(
            "test@example.com", 
            "weak", 
            {"name": "Test User"}
        )
        
        # Verify
        assert result["success"] is False
        assert "security requirements" in result["message"]
        assert not user_repository.create.called
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, auth_service, user_repository, token_manager):
        # Setup
        hashed_password = auth_service._hash_password("SecureP@ss123")
        user_repository.find_by_email.return_value = {
            "id": "user123",
            "email": "test@example.com",
            "password": hashed_password,
            "name": "Test User"
        }
        
        # Execute
        result = await auth_service.authenticate("test@example.com", "SecureP@ss123")
        
        # Verify
        assert result["success"] is True
        assert result["token"] == "test_token"
        assert "password" not in result["user"]
        assert token_manager.generate_token.called
    
    @pytest.mark.asyncio
    async def test_authenticate_invalid_password(self, auth_service, user_repository):
        # Setup
        hashed_password = auth_service._hash_password("SecureP@ss123")
        user_repository.find_by_email.return_value = {
            "id": "user123",
            "email": "test@example.com",
            "password": hashed_password,
            "name": "Test User"
        }
        
        # Execute
        result = await auth_service.authenticate("test@example.com", "WrongPassword")
        
        # Verify
        assert result["success"] is False
        assert "Invalid email or password" in result["message"]
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service, user_repository):
        # Setup
        user_repository.find_by_email.return_value = None
        
        # Execute
        result = await auth_service.authenticate("nonexistent@example.com", "SecureP@ss123")
        
        # Verify
        assert result["success"] is False
        assert "Invalid email or password" in result["message"]

class TestSecurityPolicies:
    def test_validate_password_success(self):
        # Setup
        policies = SecurityPolicies()
        
        # Execute & Verify
        assert policies.validate_password("SecureP@ss123") is True
    
    def test_validate_password_too_short(self):
        # Setup
        policies = SecurityPolicies()
        
        # Execute & Verify
        assert policies.validate_password("Short1!") is False
    
    def test_validate_password_no_uppercase(self):
        # Setup
        policies = SecurityPolicies()
        
        # Execute & Verify
        assert policies.validate_password("securep@ss123") is False
    
    def test_validate_password_no_lowercase(self):
        # Setup
        policies = SecurityPolicies()
        
        # Execute & Verify
        assert policies.validate_password("SECUREP@SS123") is False
    
    def test_validate_password_no_number(self):
        # Setup
        policies = SecurityPolicies()
        
        # Execute & Verify
        assert policies.validate_password("SecureP@ssword") is False
    
    def test_validate_password_no_special(self):
        # Setup
        policies = SecurityPolicies()
        
        # Execute & Verify
        assert policies.validate_password("SecurePass123") is False
    
    @pytest.mark.asyncio
    async def test_account_lockout(self):
        # Setup
        policies = SecurityPolicies()
        email = "test@example.com"
        
        # Execute
        for _ in range(policies.max_failed_attempts):
            await policies.record_failed_login(email)
        
        # Verify
        assert await policies.is_account_locked(email) is True
    
    @pytest.mark.asyncio
    async def test_account_lockout_expiry(self):
        # Setup
        policies = SecurityPolicies()
        email = "test@example.com"
        
        # Record failed attempts
        for _ in range(policies.max_failed_attempts):
            await policies.record_failed_login(email)
        
        # Manually expire the lockout
        policies.failed_attempts[email]["locked_until"] = datetime.now() - timedelta(minutes=1)
        
        # Verify
        assert await policies.is_account_locked(email) is False
        assert policies.failed_attempts[email]["count"] == 0
""",
            "metadata": {
                "language": "python",
                "component": "AuthService",
                "test_type": "unit"
            }
        })
        demo_steps.append(("QA Specialist Adds Test Cases", step9))
        logger.info("Step 9: QA Specialist added test cases")
        
        # Step 10: Product Manager updates requirements based on feedback
        step10 = await self.collab_framework.update_shared_state({
            "session_id": self.session_id,
            "agent_id": product_agent_id,
            "updates": {
                "requirements": {
                    "security_features": ["2FA", "password policies", "account lockout", "rate limiting by IP"]
                }
            },
            "operation": "merge"
        })
        demo_steps.append(("Product Manager Updates Requirements", step10))
        logger.info("Step 10: Product Manager updated requirements")
        
        # Get final session state
        session_info = await self.collab_framework.get_collaboration_session({
            "session_id": self.session_id,
            "include_messages": True,
            "include_artifacts": True,
            "include_state": True
        })
        
        # Save demonstration results
        with open(os.path.join(os.path.dirname(__file__), 'demo_results.json'), 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "steps": [
                    {
                        "name": name,
                        "result": {k: v for k, v in result.items() if k != "content"}
                    } for name, result in demo_steps
                ],
                "final_state": {
                    "shared_state": session_info["session"]["shared_state"],
                    "message_count": len(session_info["session"]["messages"]),
                    "artifact_count": len(session_info["session"]["artifacts"])
                }
            }, f, indent=2)
        
        return {
            "success": True,
            "message": "Real-time collaboration demonstration completed successfully",
            "session_id": self.session_id,
            "steps_completed": len(demo_steps),
            "artifacts_created": len(session_info["session"]["artifacts"]),
            "messages_exchanged": len(session_info["session"]["messages"])
        }
    
    async def shutdown(self):
        """
        Shutdown the demo and clean up resources.
        """
        logger.info("Shutting down demonstration")
        # Clean up resources if needed
        self.agents = {}

async def main():
    """
    Main entry point for demonstration.
    """
    # Get config path
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    # Create demo
    demo = CollaborationDemo(config_path)
    
    try:
        # Set up agents
        await demo.setup_agents()
        
        # Start feature development session
        session_result = await demo.start_feature_development_session()
        
        if session_result.get("success"):
            # Run demonstration
            demo_result = await demo.demonstrate_real_time_collaboration()
            logger.info(f"Demonstration result: {demo_result}")
            
            print("\n" + "="*80)
            print("REAL-TIME COLLABORATION DEMONSTRATION COMPLETED")
            print("="*80)
            print(f"Session ID: {demo_result['session_id']}")
            print(f"Steps Completed: {demo_result['steps_completed']}")
            print(f"Artifacts Created: {demo_result['artifacts_created']}")
            print(f"Messages Exchanged: {demo_result['messages_exchanged']}")
            print("\nDetailed results saved to demo_results.json")
            print("="*80 + "\n")
        else:
            logger.error(f"Failed to start feature development session: {session_result.get('message')}")
    
    except Exception as e:
        logger.error(f"Error during demonstration: {str(e)}")
    
    finally:
        # Shutdown demo
        await demo.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
