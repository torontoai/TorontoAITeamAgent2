"""
Tests for the implemented features in the TORONTO AI TEAM AGENT.

This module contains comprehensive tests for all the implemented features:
- CI/CD Integrations
- Container Orchestration
- IDE Extensions
- Load Balancing System
- Security Features
"""

import unittest
import os
import tempfile
import json
import time
from unittest.mock import MagicMock, patch

# Import CI/CD integration modules
from app.cicd.cicd_integration import (
    CICDPlatform, GitHubActionsIntegration, GitLabCIIntegration,
    WorkflowTemplate, PipelineStage, PipelineJob, JobStep
)

# Import container orchestration modules
from app.container_orchestration.docker_integration import (
    DockerIntegration, DockerImage, DockerContainer, DockerNetwork, DockerVolume
)
from app.container_orchestration.kubernetes_orchestration import (
    KubernetesOrchestration, KubernetesDeployment, KubernetesService,
    KubernetesNamespace, KubernetesPod
)

# Import IDE extensions modules
from app.ide_extensions.ide_extensions import (
    IDEExtension, VSCodeExtension, JetBrainsExtension, ExtensionFeature
)

# Import load balancing modules
from app.load_balancing.load_balancing import (
    LoadBalancingSystem, LoadBalancer, TaskQueue, Agent, Task,
    AgentRole, TaskPriority, TaskStatus, LoadBalancingStrategy
)

# Import security modules
from app.security.security_scanning import (
    SecurityScannerType, VulnerabilitySeverity, Vulnerability, ScanResult,
    SecurityScanner, SnykScanner, SonarQubeScanner, SemgrepScanner,
    SecurityScanningManager
)
from app.security.audit_trail import (
    AuditEventType, AuditEventSeverity, AuditEvent, AuditEventBuilder,
    AuditEventStorage, FileAuditEventStorage, SQLiteAuditEventStorage,
    AuditTrailSystem
)


class TestCICDIntegrations(unittest.TestCase):
    """Test cases for CI/CD integrations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.github_integration = GitHubActionsIntegration(
            repository="torontoai/TorontoAITeamAgent2",
            token="test_token"
        )
        self.gitlab_integration = GitLabCIIntegration(
            project_id="12345",
            token="test_token"
        )
    
    def test_github_actions_workflow_creation(self):
        """Test creating a GitHub Actions workflow."""
        workflow = self.github_integration.create_workflow(
            name="Test Workflow",
            trigger_events=["push", "pull_request"]
        )
        
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.trigger_events, ["push", "pull_request"])
        self.assertEqual(workflow.platform, CICDPlatform.GITHUB_ACTIONS)
    
    def test_github_actions_workflow_with_stages(self):
        """Test creating a GitHub Actions workflow with stages."""
        workflow = self.github_integration.create_workflow(
            name="Build and Test",
            trigger_events=["push"]
        )
        
        build_stage = workflow.add_stage(
            name="build",
            runs_on="ubuntu-latest"
        )
        
        build_job = build_stage.add_job(
            name="build_app",
            display_name="Build Application"
        )
        
        build_job.add_step(
            name="checkout",
            uses="actions/checkout@v2"
        )
        
        build_job.add_step(
            name="setup_node",
            uses="actions/setup-node@v2",
            with_args={"node-version": "16"}
        )
        
        build_job.add_step(
            name="install",
            run="npm install"
        )
        
        build_job.add_step(
            name="build",
            run="npm run build"
        )
        
        self.assertEqual(len(workflow.stages), 1)
        self.assertEqual(len(workflow.stages[0].jobs), 1)
        self.assertEqual(len(workflow.stages[0].jobs[0].steps), 4)
        
        # Verify the generated YAML
        yaml_content = workflow.to_yaml()
        self.assertIn("name: Build and Test", yaml_content)
        self.assertIn("runs-on: ubuntu-latest", yaml_content)
        self.assertIn("actions/checkout@v2", yaml_content)
        self.assertIn("npm install", yaml_content)
    
    def test_gitlab_ci_pipeline_creation(self):
        """Test creating a GitLab CI pipeline."""
        pipeline = self.gitlab_integration.create_pipeline(
            name="Test Pipeline"
        )
        
        self.assertEqual(pipeline.name, "Test Pipeline")
        self.assertEqual(pipeline.platform, CICDPlatform.GITLAB_CI)
    
    def test_gitlab_ci_pipeline_with_stages(self):
        """Test creating a GitLab CI pipeline with stages."""
        pipeline = self.gitlab_integration.create_pipeline(
            name="Build, Test, and Deploy"
        )
        
        pipeline.add_stage(name="build")
        pipeline.add_stage(name="test")
        pipeline.add_stage(name="deploy")
        
        build_job = pipeline.add_job(
            name="build_app",
            stage="build",
            image="node:16-alpine"
        )
        
        build_job.add_step(
            name="install",
            script="npm install"
        )
        
        build_job.add_step(
            name="build",
            script="npm run build"
        )
        
        test_job = pipeline.add_job(
            name="test_app",
            stage="test",
            image="node:16-alpine"
        )
        
        test_job.add_step(
            name="test",
            script="npm test"
        )
        
        self.assertEqual(len(pipeline.stages), 3)
        self.assertEqual(len(pipeline.jobs), 2)
        
        # Verify the generated YAML
        yaml_content = pipeline.to_yaml()
        self.assertIn("stages:", yaml_content)
        self.assertIn("- build", yaml_content)
        self.assertIn("- test", yaml_content)
        self.assertIn("- deploy", yaml_content)
        self.assertIn("build_app:", yaml_content)
        self.assertIn("test_app:", yaml_content)
        self.assertIn("npm install", yaml_content)
        self.assertIn("npm test", yaml_content)


class TestContainerOrchestration(unittest.TestCase):
    """Test cases for container orchestration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.docker_integration = DockerIntegration()
        self.kubernetes_orchestration = KubernetesOrchestration(
            config_file=None  # Use default config
        )
    
    def test_docker_image_operations(self):
        """Test Docker image operations."""
        # Mock the Docker client
        self.docker_integration.client = MagicMock()
        
        # Test building an image
        self.docker_integration.client.images.build.return_value = (MagicMock(), [])
        image = self.docker_integration.build_image(
            path="./app",
            tag="toronto-ai:latest",
            dockerfile="Dockerfile"
        )
        
        self.assertEqual(image.tag, "toronto-ai:latest")
        self.docker_integration.client.images.build.assert_called_once()
        
        # Test pulling an image
        self.docker_integration.client.images.pull.return_value = MagicMock()
        image = self.docker_integration.pull_image(
            repository="node",
            tag="16-alpine"
        )
        
        self.assertEqual(image.repository, "node")
        self.assertEqual(image.tag, "16-alpine")
        self.docker_integration.client.images.pull.assert_called_once()
        
        # Test pushing an image
        self.docker_integration.client.images.push.return_value = "Push successful"
        result = self.docker_integration.push_image(
            repository="toronto-ai",
            tag="latest"
        )
        
        self.assertTrue(result)
        self.docker_integration.client.images.push.assert_called_once()
    
    def test_docker_container_operations(self):
        """Test Docker container operations."""
        # Mock the Docker client
        self.docker_integration.client = MagicMock()
        
        # Test creating a container
        mock_container = MagicMock()
        mock_container.id = "container123"
        self.docker_integration.client.containers.create.return_value = mock_container
        
        container = self.docker_integration.create_container(
            image="toronto-ai:latest",
            name="toronto-ai-app",
            ports={"8080/tcp": 8080},
            environment={"NODE_ENV": "production"}
        )
        
        self.assertEqual(container.id, "container123")
        self.assertEqual(container.name, "toronto-ai-app")
        self.docker_integration.client.containers.create.assert_called_once()
        
        # Test starting a container
        container.start = MagicMock()
        self.docker_integration.start_container(container)
        container.start.assert_called_once()
        
        # Test stopping a container
        container.stop = MagicMock()
        self.docker_integration.stop_container(container)
        container.stop.assert_called_once()
        
        # Test removing a container
        container.remove = MagicMock()
        self.docker_integration.remove_container(container)
        container.remove.assert_called_once()
    
    def test_kubernetes_deployment_operations(self):
        """Test Kubernetes deployment operations."""
        # Mock the Kubernetes client
        self.kubernetes_orchestration.api_client = MagicMock()
        self.kubernetes_orchestration.apps_v1_api = MagicMock()
        self.kubernetes_orchestration.core_v1_api = MagicMock()
        
        # Test creating a deployment
        self.kubernetes_orchestration.apps_v1_api.create_namespaced_deployment.return_value = MagicMock()
        
        deployment = self.kubernetes_orchestration.create_deployment(
            name="toronto-ai-app",
            namespace="default",
            image="toronto-ai:latest",
            replicas=3,
            ports=[{"containerPort": 8080}],
            environment=[{"name": "NODE_ENV", "value": "production"}]
        )
        
        self.assertEqual(deployment.name, "toronto-ai-app")
        self.assertEqual(deployment.namespace, "default")
        self.assertEqual(deployment.replicas, 3)
        self.kubernetes_orchestration.apps_v1_api.create_namespaced_deployment.assert_called_once()
        
        # Test updating a deployment
        self.kubernetes_orchestration.apps_v1_api.patch_namespaced_deployment.return_value = MagicMock()
        
        deployment.replicas = 5
        updated_deployment = self.kubernetes_orchestration.update_deployment(deployment)
        
        self.assertEqual(updated_deployment.replicas, 5)
        self.kubernetes_orchestration.apps_v1_api.patch_namespaced_deployment.assert_called_once()
        
        # Test deleting a deployment
        self.kubernetes_orchestration.apps_v1_api.delete_namespaced_deployment.return_value = MagicMock()
        
        result = self.kubernetes_orchestration.delete_deployment(
            name="toronto-ai-app",
            namespace="default"
        )
        
        self.assertTrue(result)
        self.kubernetes_orchestration.apps_v1_api.delete_namespaced_deployment.assert_called_once()
    
    def test_kubernetes_service_operations(self):
        """Test Kubernetes service operations."""
        # Mock the Kubernetes client
        self.kubernetes_orchestration.api_client = MagicMock()
        self.kubernetes_orchestration.core_v1_api = MagicMock()
        
        # Test creating a service
        self.kubernetes_orchestration.core_v1_api.create_namespaced_service.return_value = MagicMock()
        
        service = self.kubernetes_orchestration.create_service(
            name="toronto-ai-service",
            namespace="default",
            selector={"app": "toronto-ai-app"},
            ports=[{"port": 80, "targetPort": 8080}],
            service_type="LoadBalancer"
        )
        
        self.assertEqual(service.name, "toronto-ai-service")
        self.assertEqual(service.namespace, "default")
        self.assertEqual(service.service_type, "LoadBalancer")
        self.kubernetes_orchestration.core_v1_api.create_namespaced_service.assert_called_once()
        
        # Test deleting a service
        self.kubernetes_orchestration.core_v1_api.delete_namespaced_service.return_value = MagicMock()
        
        result = self.kubernetes_orchestration.delete_service(
            name="toronto-ai-service",
            namespace="default"
        )
        
        self.assertTrue(result)
        self.kubernetes_orchestration.core_v1_api.delete_namespaced_service.assert_called_once()


class TestIDEExtensions(unittest.TestCase):
    """Test cases for IDE extensions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.vscode_extension = VSCodeExtension(
            name="toronto-ai-assistant",
            display_name="Toronto AI Assistant",
            description="AI-powered assistance for developers",
            version="1.0.0",
            publisher="torontoai"
        )
        
        self.jetbrains_extension = JetBrainsExtension(
            name="toronto-ai-assistant",
            display_name="Toronto AI Assistant",
            description="AI-powered assistance for developers",
            version="1.0.0",
            vendor="torontoai"
        )
    
    def test_vscode_extension_creation(self):
        """Test creating a VS Code extension."""
        self.assertEqual(self.vscode_extension.name, "toronto-ai-assistant")
        self.assertEqual(self.vscode_extension.display_name, "Toronto AI Assistant")
        self.assertEqual(self.vscode_extension.version, "1.0.0")
        self.assertEqual(self.vscode_extension.publisher, "torontoai")
    
    def test_vscode_extension_manifest(self):
        """Test generating a VS Code extension manifest."""
        manifest = self.vscode_extension.generate_manifest()
        
        self.assertIsInstance(manifest, dict)
        self.assertEqual(manifest["name"], "toronto-ai-assistant")
        self.assertEqual(manifest["displayName"], "Toronto AI Assistant")
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual(manifest["publisher"], "torontoai")
    
    def test_vscode_extension_features(self):
        """Test adding features to a VS Code extension."""
        self.vscode_extension.add_feature(
            feature_type=ExtensionFeature.COMMAND,
            name="torontoai.generateCode",
            title="Generate Code"
        )
        
        self.vscode_extension.add_feature(
            feature_type=ExtensionFeature.VIEW,
            name="torontoai.assistantView",
            title="AI Assistant"
        )
        
        manifest = self.vscode_extension.generate_manifest()
        
        self.assertIn("contributes", manifest)
        self.assertIn("commands", manifest["contributes"])
        self.assertIn("views", manifest["contributes"])
        self.assertEqual(len(manifest["contributes"]["commands"]), 1)
        self.assertEqual(manifest["contributes"]["commands"][0]["command"], "torontoai.generateCode")
    
    def test_jetbrains_extension_creation(self):
        """Test creating a JetBrains extension."""
        self.assertEqual(self.jetbrains_extension.name, "toronto-ai-assistant")
        self.assertEqual(self.jetbrains_extension.display_name, "Toronto AI Assistant")
        self.assertEqual(self.jetbrains_extension.version, "1.0.0")
        self.assertEqual(self.jetbrains_extension.vendor, "torontoai")
    
    def test_jetbrains_extension_plugin_xml(self):
        """Test generating a JetBrains extension plugin.xml."""
        plugin_xml = self.jetbrains_extension.generate_plugin_xml()
        
        self.assertIsInstance(plugin_xml, str)
        self.assertIn("<idea-plugin>", plugin_xml)
        self.assertIn("<name>Toronto AI Assistant</name>", plugin_xml)
        self.assertIn("<vendor>torontoai</vendor>", plugin_xml)
        self.assertIn("<version>1.0.0</version>", plugin_xml)
    
    def test_jetbrains_extension_features(self):
        """Test adding features to a JetBrains extension."""
        self.jetbrains_extension.add_feature(
            feature_type=ExtensionFeature.ACTION,
            name="GenerateCodeAction",
            text="Generate Code",
            description="Generate code using AI"
        )
        
        self.jetbrains_extension.add_feature(
            feature_type=ExtensionFeature.TOOL_WINDOW,
            name="AIAssistantToolWindow",
            id="AIAssistant",
            icon="icons/assistant.svg"
        )
        
        plugin_xml = self.jetbrains_extension.generate_plugin_xml()
        
        self.assertIn("<actions>", plugin_xml)
        self.assertIn("<action", plugin_xml)
        self.assertIn("id=\"GenerateCodeAction\"", plugin_xml)
        self.assertIn("<toolWindow", plugin_xml)
        self.assertIn("id=\"AIAssistant\"", plugin_xml)


class TestLoadBalancingSystem(unittest.TestCase):
    """Test cases for the load balancing system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.load_balancing_system = LoadBalancingSystem()
        
        # Add some agents
        self.developer1 = Agent(
            id="dev1",
            name="Developer 1",
            role=AgentRole.DEVELOPER,
            capabilities=["python", "javascript"]
        )
        
        self.developer2 = Agent(
            id="dev2",
            name="Developer 2",
            role=AgentRole.DEVELOPER,
            capabilities=["java", "python"]
        )
        
        self.project_manager = Agent(
            id="pm1",
            name="Project Manager 1",
            role=AgentRole.PROJECT_MANAGER,
            capabilities=["planning", "coordination"]
        )
        
        self.load_balancing_system.register_agent(self.developer1)
        self.load_balancing_system.register_agent(self.developer2)
        self.load_balancing_system.register_agent(self.project_manager)
    
    def test_agent_registration(self):
        """Test agent registration."""
        self.assertEqual(len(self.load_balancing_system.get_agents()), 3)
        self.assertEqual(len(self.load_balancing_system.get_agents_by_role(AgentRole.DEVELOPER)), 2)
        self.assertEqual(len(self.load_balancing_system.get_agents_by_role(AgentRole.PROJECT_MANAGER)), 1)
    
    def test_task_assignment(self):
        """Test task assignment."""
        # Create a task
        task = Task(
            id="task1",
            name="Implement Feature X",
            description="Implement Feature X using Python",
            required_capabilities=["python"],
            priority=TaskPriority.HIGH,
            estimated_duration=120  # minutes
        )
        
        # Assign the task
        assigned_agent = self.load_balancing_system.assign_task(task)
        
        # Verify assignment
        self.assertIsNotNone(assigned_agent)
        self.assertIn(assigned_agent.id, [self.developer1.id, self.developer2.id])
        self.assertEqual(task.status, TaskStatus.ASSIGNED)
        self.assertEqual(task.assigned_agent_id, assigned_agent.id)
    
    def test_task_assignment_with_specific_capability(self):
        """Test task assignment with a specific capability."""
        # Create a task requiring Java
        task = Task(
            id="task2",
            name="Implement Feature Y",
            description="Implement Feature Y using Java",
            required_capabilities=["java"],
            priority=TaskPriority.MEDIUM,
            estimated_duration=90  # minutes
        )
        
        # Assign the task
        assigned_agent = self.load_balancing_system.assign_task(task)
        
        # Verify assignment
        self.assertIsNotNone(assigned_agent)
        self.assertEqual(assigned_agent.id, self.developer2.id)
        self.assertEqual(task.status, TaskStatus.ASSIGNED)
        self.assertEqual(task.assigned_agent_id, assigned_agent.id)
    
    def test_load_balancing_strategies(self):
        """Test different load balancing strategies."""
        # Create multiple tasks
        tasks = [
            Task(
                id=f"task{i}",
                name=f"Task {i}",
                description=f"Task {i} description",
                required_capabilities=["python"],
                priority=TaskPriority.MEDIUM,
                estimated_duration=60  # minutes
            )
            for i in range(1, 6)
        ]
        
        # Test round-robin strategy
        self.load_balancing_system.set_strategy(LoadBalancingStrategy.ROUND_ROBIN)
        
        assigned_agents = []
        for task in tasks:
            agent = self.load_balancing_system.assign_task(task)
            assigned_agents.append(agent.id)
        
        # Verify that both developers got tasks
        self.assertIn(self.developer1.id, assigned_agents)
        self.assertIn(self.developer2.id, assigned_agents)
        
        # Reset tasks
        for task in tasks:
            task.status = TaskStatus.PENDING
            task.assigned_agent_id = None
        
        # Reset agent workloads
        self.load_balancing_system.reset()
        
        # Test least-connections strategy
        self.load_balancing_system.set_strategy(LoadBalancingStrategy.LEAST_CONNECTIONS)
        
        # Assign one task to developer1 first
        self.load_balancing_system.assign_task_to_agent(tasks[0], self.developer1)
        
        # Now assign the rest of the tasks
        for i in range(1, 5):
            agent = self.load_balancing_system.assign_task(tasks[i])
            # Developer2 should get more tasks since developer1 already has one
            self.assertEqual(agent.id, self.developer2.id)
    
    def test_task_completion(self):
        """Test task completion."""
        # Create and assign a task
        task = Task(
            id="task3",
            name="Code Review",
            description="Review Pull Request #123",
            required_capabilities=["python"],
            priority=TaskPriority.HIGH,
            estimated_duration=30  # minutes
        )
        
        assigned_agent = self.load_balancing_system.assign_task(task)
        
        # Complete the task
        self.load_balancing_system.complete_task(task.id)
        
        # Verify task status
        updated_task = self.load_balancing_system.get_task(task.id)
        self.assertEqual(updated_task.status, TaskStatus.COMPLETED)
        
        # Verify agent workload
        agent_workload = self.load_balancing_system.get_agent_workload(assigned_agent.id)
        self.assertEqual(agent_workload.active_tasks, 0)
        self.assertEqual(agent_workload.completed_tasks, 1)


class TestSecurityFeatures(unittest.TestCase):
    """Test cases for security features."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Set up security scanning manager
        self.security_scanning_manager = SecurityScanningManager()
        
        # Set up mock scanners
        self.snyk_scanner = SnykScanner(api_token="test_token")
        self.sonarqube_scanner = SonarQubeScanner(
            server_url="http://localhost:9000",
            token="test_token"
        )
        self.semgrep_scanner = SemgrepScanner()
        
        # Register scanners
        self.security_scanning_manager.register_scanner(self.snyk_scanner)
        self.security_scanning_manager.register_scanner(self.sonarqube_scanner)
        self.security_scanning_manager.register_scanner(self.semgrep_scanner)
        
        # Set up audit trail system
        self.temp_dir = tempfile.mkdtemp()
        self.audit_log_file = os.path.join(self.temp_dir, "audit.log")
        self.audit_storage = FileAuditEventStorage(self.audit_log_file)
        self.audit_trail_system = AuditTrailSystem(self.audit_storage, async_mode=False)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary files
        if os.path.exists(self.audit_log_file):
            os.unlink(self.audit_log_file)
        os.rmdir(self.temp_dir)
    
    def test_security_scanner_registration(self):
        """Test security scanner registration."""
        self.assertEqual(len(self.security_scanning_manager.scanners), 3)
        self.assertIn(SecurityScannerType.SNYK, self.security_scanning_manager.scanners)
        self.assertIn(SecurityScannerType.SONARQUBE, self.security_scanning_manager.scanners)
        self.assertIn(SecurityScannerType.SEMGREP, self.security_scanning_manager.scanners)
    
    def test_security_scanning(self):
        """Test security scanning."""
        # Mock the scan method of the Snyk scanner
        self.snyk_scanner.scan = MagicMock()
        
        # Create a mock scan result
        mock_vulnerabilities = [
            Vulnerability(
                id="SNYK-JS-LODASH-567746",
                title="Prototype Pollution",
                description="Lodash vulnerable to prototype pollution",
                severity=VulnerabilitySeverity.HIGH,
                file_path="package.json",
                scanner_type=SecurityScannerType.SNYK,
                cve_id="CVE-2019-10744"
            ),
            Vulnerability(
                id="SNYK-JS-AXIOS-1038255",
                title="Server-Side Request Forgery",
                description="Axios SSRF vulnerability",
                severity=VulnerabilitySeverity.MEDIUM,
                file_path="package.json",
                scanner_type=SecurityScannerType.SNYK,
                cve_id="CVE-2020-28168"
            )
        ]
        
        mock_scan_result = ScanResult(
            scanner_type=SecurityScannerType.SNYK,
            vulnerabilities=mock_vulnerabilities,
            scan_time=time.time(),
            scan_duration=2.5,
            target="/path/to/project",
            success=True
        )
        
        self.snyk_scanner.scan.return_value = mock_scan_result
        
        # Perform a scan
        result = self.security_scanning_manager.scan(
            target="/path/to/project",
            scanner_type=SecurityScannerType.SNYK
        )
        
        # Verify scan result
        self.assertTrue(result.success)
        self.assertEqual(len(result.vulnerabilities), 2)
        self.assertEqual(result.critical_count, 0)
        self.assertEqual(result.high_count, 1)
        self.assertEqual(result.medium_count, 1)
        self.assertEqual(result.low_count, 0)
    
    def test_audit_event_logging(self):
        """Test audit event logging."""
        # Log an agent action
        self.audit_trail_system.log_agent_action(
            agent_id="agent1",
            action="code_generation",
            resource="project/file.py",
            status="success",
            severity=AuditEventSeverity.INFO,
            details={"language": "python", "tokens": 150}
        )
        
        # Log a security event
        self.audit_trail_system.log_security_event(
            actor="user1",
            action="login",
            resource="system",
            status="success",
            severity=AuditEventSeverity.INFO,
            source_ip="192.168.1.1"
        )
        
        # Query events
        events = self.audit_trail_system.query_events()
        
        # Verify events
        self.assertEqual(len(events), 2)
        
        # Verify agent action event
        agent_events = self.audit_trail_system.query_events(
            filters={"event_type": AuditEventType.AGENT_ACTION.value}
        )
        self.assertEqual(len(agent_events), 1)
        self.assertEqual(agent_events[0].actor, "agent1")
        self.assertEqual(agent_events[0].action, "code_generation")
        self.assertEqual(agent_events[0].resource, "project/file.py")
        
        # Verify security event
        security_events = self.audit_trail_system.query_events(
            filters={"event_type": AuditEventType.SECURITY_EVENT.value}
        )
        self.assertEqual(len(security_events), 1)
        self.assertEqual(security_events[0].actor, "user1")
        self.assertEqual(security_events[0].action, "login")
        self.assertEqual(security_events[0].source_ip, "192.168.1.1")
    
    def test_audit_event_filtering(self):
        """Test audit event filtering."""
        # Log multiple events
        for i in range(5):
            self.audit_trail_system.log_system_event(
                action=f"action{i}",
                resource=f"resource{i}",
                severity=AuditEventSeverity.INFO
            )
        
        # Log an error event
        self.audit_trail_system.log_system_event(
            action="failed_operation",
            resource="database",
            status="error",
            severity=AuditEventSeverity.HIGH
        )
        
        # Query all events
        all_events = self.audit_trail_system.query_events()
        self.assertEqual(len(all_events), 6)
        
        # Query error events
        error_events = self.audit_trail_system.query_events(
            filters={"status": "error"}
        )
        self.assertEqual(len(error_events), 1)
        self.assertEqual(error_events[0].action, "failed_operation")
        
        # Query high severity events
        high_severity_events = self.audit_trail_system.query_events(
            filters={"severity": AuditEventSeverity.HIGH.value}
        )
        self.assertEqual(len(high_severity_events), 1)
        
        # Query with time filter
        current_time = time.time()
        time_filtered_events = self.audit_trail_system.query_events(
            start_time=current_time - 60,  # Last minute
            end_time=current_time + 1
        )
        self.assertEqual(len(time_filtered_events), 6)
        
        # Query with limit and offset
        limited_events = self.audit_trail_system.query_events(
            limit=3
        )
        self.assertEqual(len(limited_events), 3)
        
        offset_events = self.audit_trail_system.query_events(
            offset=3
        )
        self.assertEqual(len(offset_events), 3)


if __name__ == "__main__":
    unittest.main()
