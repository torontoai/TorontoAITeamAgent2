"""
Test suite for Multi-agent Architecture Search (MaAS) integration.

This module provides tests to verify the correct functioning of the MaAS integration.
"""

import unittest
import logging
import os
import json
from typing import Dict, Any, List

from app.orchestration.maas.models import (
    ArchitectureModel, AgentModel, ConnectionModel, TaskModel, 
    AgentRole, AgentCapability, SearchSpace, EvaluationResult
)
from app.orchestration.maas.supernet.agentic_supernet import AgenticSupernet
from app.orchestration.maas.supernet.architecture_sampler import ArchitectureSampler
from app.orchestration.maas.supernet.controller import SupernetController
from app.orchestration.maas.evaluation.evaluator import ArchitectureEvaluator
from app.orchestration.maas.evaluation.metrics import MetricsCalculator
from app.orchestration.maas.evaluation.fitness import FitnessFunction
from app.orchestration.maas.integration.autogen_integration import MaaSAutoGenAdapter
from app.orchestration.maas.integration.a2a_integration import MaaSA2AAdapter
from app.orchestration.maas.integration import MaaSIntegrationManager  # Updated import statement
from app.orchestration.maas.visualization.architecture_visualizer import ArchitectureVisualizer
from app.orchestration.maas.visualization.performance_visualizer import PerformanceVisualizer
from app.orchestration.maas.visualization.search_progress_visualizer import SearchProgressVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMaaSIntegration(unittest.TestCase):
    """Test suite for MaAS integration."""
    
    def setUp(self):
        """Set up test environment."""
        # Create test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_output")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create search space
        self.search_space = SearchSpace(
            name="TestSearchSpace",
            min_agents=1,
            max_agents=10,
            allowed_agent_roles=list(AgentRole),
            allowed_agent_capabilities=list(AgentCapability),
            allowed_communication_patterns=["hierarchical", "mesh", "star"],
            parameters={"allowed_models": ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "gemini-pro"]}
        )
        
        # Create sample task
        self.task = TaskModel(
            id="test_task_001",
            name="Test Task",
            description="A test task for MaAS integration testing",
            domain="testing",
            required_capabilities=[
                AgentCapability.PLANNING,
                AgentCapability.CODE_EXECUTION,
                AgentCapability.QUALITY_ASSESSMENT  # Changed from EVALUATION to QUALITY_ASSESSMENT
            ],
            complexity_score=0.5,
            expected_steps=5
        )
        
        # Initialize components
        self.supernet = AgenticSupernet(self.search_space)
        self.evaluator = ArchitectureEvaluator(
            results_dir=os.path.join(self.test_dir, "evaluation_results")
        )
        self.integration_manager = MaaSIntegrationManager(self.supernet, self.evaluator)
    
    def test_architecture_sampling(self):
        """Test architecture sampling from the supernet."""
        logger.info("Testing architecture sampling...")
        
        # Sample an architecture
        architecture = self.supernet.sample_architecture(self.task)
        
        # Verify architecture properties
        self.assertIsNotNone(architecture)
        self.assertIsInstance(architecture, ArchitectureModel)
        self.assertGreaterEqual(len(architecture.agents), self.search_space.min_agents)
        self.assertLessEqual(len(architecture.agents), self.search_space.max_agents)
        
        # Verify required capabilities are present
        present_capabilities = set()
        for agent in architecture.agents:
            if agent.capabilities:
                present_capabilities.update(agent.capabilities)
        
        for capability in self.task.required_capabilities:
            self.assertIn(capability, present_capabilities)
        
        logger.info(f"Successfully sampled architecture with {len(architecture.agents)} agents")
        
        # Save architecture to file for inspection
        arch_file = os.path.join(self.test_dir, "sampled_architecture.json")
        with open(arch_file, 'w') as f:
            json.dump(architecture.to_dict(), f, indent=2)
        
        logger.info(f"Saved sampled architecture to {arch_file}")
    
    def test_architecture_visualization(self):
        """Test architecture visualization."""
        logger.info("Testing architecture visualization...")
        
        # Sample an architecture
        architecture = self.supernet.sample_architecture(self.task)
        
        # Create visualizer
        visualizer = ArchitectureVisualizer()
        
        # Generate static visualization
        static_path = os.path.join(self.test_dir, "architecture_static")
        static_file = visualizer.visualize_architecture(architecture, output_path=static_path)
        
        self.assertTrue(os.path.exists(static_file))
        logger.info(f"Generated static architecture visualization: {static_file}")
        
        # Generate interactive visualization
        visualizer = ArchitectureVisualizer(output_format="html")
        interactive_path = os.path.join(self.test_dir, "architecture_interactive")
        interactive_file = visualizer.visualize_architecture(architecture, output_path=interactive_path)
        
        self.assertTrue(os.path.exists(interactive_file))
        logger.info(f"Generated interactive architecture visualization: {interactive_file}")
    
    def test_metrics_calculation(self):
        """Test metrics calculation."""
        logger.info("Testing metrics calculation...")
        
        # Create sample workflow results
        results = {
            "execution_time": 120.5,
            "iterations": 8,
            "token_usage": 3500,
            "cost": 0.75,
            "success": True,
            "quality_score": 0.85,
            "message_count": 25,
            "agent_metrics": {
                "agent_0": {
                    "messages_sent": 10,
                    "processing_time": 45.2
                },
                "agent_1": {
                    "messages_sent": 15,
                    "processing_time": 60.8
                }
            }
        }
        
        # Sample an architecture
        architecture = self.supernet.sample_architecture(self.task)
        
        # Calculate metrics
        metrics_calculator = MetricsCalculator()
        metrics = metrics_calculator.calculate_metrics(results, self.task, architecture)
        
        # Verify metrics
        self.assertIsNotNone(metrics)
        self.assertIn("execution_time", metrics)
        self.assertIn("success", metrics)
        self.assertIn("quality_score", metrics)
        
        # Verify derived metrics
        self.assertIn("efficiency", metrics)
        self.assertIn("speed", metrics)
        self.assertIn("cost_effectiveness", metrics)
        self.assertIn("architecture_complexity", metrics)
        
        logger.info(f"Successfully calculated {len(metrics)} metrics")
        
        # Save metrics to file for inspection
        metrics_file = os.path.join(self.test_dir, "calculated_metrics.json")
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"Saved calculated metrics to {metrics_file}")
    
    def test_fitness_calculation(self):
        """Test fitness calculation."""
        logger.info("Testing fitness calculation...")
        
        # Create sample metrics
        metrics = {
            "execution_time": 120.5,
            "iterations": 8,
            "token_usage": 3500,
            "cost": 0.75,
            "success": 1.0,
            "quality_score": 0.85,
            "message_count": 25,
            "efficiency": 0.28,
            "speed": 0.008,
            "cost_effectiveness": 1.33,
            "architecture_complexity": 0.45,
            "complexity_efficiency": 2.22
        }
        
        # Calculate fitness
        fitness_function = FitnessFunction()
        fitness = fitness_function.calculate_fitness(metrics, self.task)
        
        # Verify fitness
        self.assertIsNotNone(fitness)
        self.assertGreaterEqual(fitness, 0.0)
        self.assertLessEqual(fitness, 1.0)
        
        logger.info(f"Successfully calculated fitness score: {fitness:.4f}")
    
    def test_architecture_evaluation(self):
        """Test architecture evaluation."""
        logger.info("Testing architecture evaluation...")
        
        # Sample an architecture
        architecture = self.supernet.sample_architecture(self.task)
        
        # Create sample metrics
        metrics = {
            "execution_time": 120.5,
            "iterations": 8,
            "token_usage": 3500,
            "cost": 0.75,
            "success": 1.0,
            "quality_score": 0.85,
            "message_count": 25
        }
        
        # Evaluate architecture
        evaluation_result = self.evaluator.evaluate_architecture(
            architecture=architecture,
            task=self.task,
            metrics=metrics
        )
        
        # Verify evaluation result
        self.assertIsNotNone(evaluation_result)
        self.assertIsInstance(evaluation_result, EvaluationResult)
        self.assertEqual(evaluation_result.architecture_id, architecture.id)
        self.assertEqual(evaluation_result.task_id, self.task.id)
        self.assertGreaterEqual(evaluation_result.fitness, 0.0)
        self.assertLessEqual(evaluation_result.fitness, 1.0)
        
        logger.info(f"Successfully evaluated architecture with fitness: {evaluation_result.fitness:.4f}")
        
        # Generate evaluation report
        report = self.evaluator.generate_evaluation_report([evaluation_result])
        
        # Save report to file for inspection
        report_file = os.path.join(self.test_dir, "evaluation_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Saved evaluation report to {report_file}")
    
    def test_performance_visualization(self):
        """Test performance visualization."""
        logger.info("Testing performance visualization...")
        
        # Create sample evaluation results
        evaluation_results = []
        
        for i in range(3):
            # Sample an architecture
            architecture = self.supernet.sample_architecture(self.task)
            
            # Create metrics with some variation
            base_metrics = {
                "execution_time": 100 + i * 20,
                "iterations": 5 + i,
                "token_usage": 3000 + i * 500,
                "cost": 0.5 + i * 0.25,
                "success": 1.0 - i * 0.1,
                "quality_score": 0.9 - i * 0.1,
                "message_count": 20 + i * 5
            }
            
            # Evaluate architecture
            evaluation_result = self.evaluator.evaluate_architecture(
                architecture=architecture,
                task=self.task,
                metrics=base_metrics
            )
            
            evaluation_results.append(evaluation_result)
        
        # Create visualizer
        visualizer = PerformanceVisualizer()
        
        # Generate metrics visualization
        metrics_path = os.path.join(self.test_dir, "performance_metrics")
        metrics_file = visualizer.visualize_metrics(evaluation_results, output_path=metrics_path)
        
        self.assertTrue(os.path.exists(metrics_file))
        logger.info(f"Generated performance metrics visualization: {metrics_file}")
        
        # Generate comparison visualization
        comparison_path = os.path.join(self.test_dir, "performance_comparison")
        comparison_file = visualizer.visualize_comparison(evaluation_results, output_path=comparison_path)
        
        self.assertTrue(os.path.exists(comparison_file))
        logger.info(f"Generated performance comparison visualization: {comparison_file}")
    
    def test_autogen_integration(self):
        """Test AutoGen integration."""
        logger.info("Testing AutoGen integration...")
        
        # Create AutoGen adapter
        autogen_adapter = MaaSAutoGenAdapter(self.supernet, self.evaluator)
        
        # Create agent team configuration
        autogen_config = autogen_adapter.create_agent_team(self.task)
        
        # Verify configuration
        self.assertIsNotNone(autogen_config)
        self.assertIn("agents", autogen_config)
        self.assertIn("workflow", autogen_config)
        self.assertIn("task", autogen_config)
        
        # Verify agents
        self.assertGreater(len(autogen_config["agents"]), 0)
        
        # Verify workflow
        self.assertIn("graph", autogen_config["workflow"])
        self.assertIn("entry_points", autogen_config["workflow"])
        
        logger.info(f"Successfully created AutoGen team with {len(autogen_config['agents'])} agents")
        
        # Save configuration to file for inspection
        config_file = os.path.join(self.test_dir, "autogen_config.json")
        with open(config_file, 'w') as f:
            json.dump(autogen_config, f, indent=2)
        
        logger.info(f"Saved AutoGen configuration to {config_file}")
    
    def test_a2a_integration(self):
        """Test A2A integration."""
        logger.info("Testing A2A integration...")
        
        # Create A2A adapter
        a2a_adapter = MaaSA2AAdapter(self.supernet, self.evaluator)
        
        # Create agent team configuration
        a2a_config = a2a_adapter.create_agent_team(self.task)
        
        # Verify configuration
        self.assertIsNotNone(a2a_config)
        self.assertIn("agents", a2a_config)
        self.assertIn("graph", a2a_config)
        self.assertIn("task", a2a_config)
        
        # Verify agents
        self.assertGreater(len(a2a_config["agents"]), 0)
        
        logger.info(f"Successfully created A2A team with {len(a2a_config['agents'])} agents")
        
        # Save configuration to file for inspection
        config_file = os.path.join(self.test_dir, "a2a_config.json")
        with open(config_file, 'w') as f:
            json.dump(a2a_config, f, indent=2)
        
        logger.info(f"Saved A2A configuration to {config_file}")
    
    def test_integration_manager(self):
        """Test integration manager."""
        logger.info("Testing integration manager...")
        
        # Create agent team with AutoGen
        autogen_config = self.integration_manager.create_agent_team(
            task=self.task,
            framework="autogen"
        )
        
        # Verify AutoGen configuration
        self.assertIsNotNone(autogen_config)
        self.assertIn("agents", autogen_config)
        
        # Create agent team with A2A
        a2a_config = self.integration_manager.create_agent_team(
            task=self.task,
            framework="a2a"
        )
        
        # Verify A2A configuration
        self.assertIsNotNone(a2a_config)
        self.assertIn("agents", a2a_config)
        
        logger.info("Successfully created agent teams using integration manager")
    
    def test_supernet_feedback(self):
        """Test supernet feedback loop."""
        logger.info("Testing supernet feedback loop...")
        
        # Sample an architecture
        architecture = self.supernet.sample_architecture(self.task)
        
        # Create sample metrics
        metrics = {
            "execution_time": 120.5,
            "iterations": 8,
            "token_usage": 3500,
            "cost": 0.75,
            "success": 1.0,
            "quality_score": 0.85,
            "message_count": 25
        }
        
        # Evaluate architecture
        evaluation_result = self.evaluator.evaluate_architecture(
            architecture=architecture,
            task=self.task,
            metrics=metrics
        )
        
        # Update supernet with feedback
        self.supernet.update_from_feedback(architecture, evaluation_result)
        
        # Sample another architecture after feedback
        updated_architecture = self.supernet.sample_architecture(self.task)
        
        # Verify updated architecture
        self.assertIsNotNone(updated_architecture)
        self.assertIsInstance(updated_architecture, ArchitectureModel)
        
        logger.info("Successfully updated supernet with feedback and sampled new architecture")
    
    def tearDown(self):
        """Clean up after tests."""
        # Nothing to clean up for now
        pass


if __name__ == "__main__":
    unittest.main()
