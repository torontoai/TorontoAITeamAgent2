"""
Test script for the Agent Performance Analytics feature.

This script tests the functionality of the Agent Performance Analytics module,
which provides comprehensive monitoring of agent performance metrics.
"""

import os
import sys
import logging
import json
import datetime
import unittest
from typing import Dict, Any, List
from unittest.mock import MagicMock, patch

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import performance monitoring components
from app.performance_monitoring.agent_performance_analytics import (
    MetricType, MetricUnit, AgentRole, TaskStatus, TaskPriority,
    PerformanceMetric, AgentTask, AgentProfile, PerformanceAnalytics,
    PerformanceReport, PerformanceVisualization, TeamPerformanceMonitor
)


class TestAgentPerformanceAnalytics(unittest.TestCase):
    """Test cases for Agent Performance Analytics."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create performance analytics system
        self.analytics = PerformanceAnalytics()
        
        # Create agent profiles
        self.agent1 = self.analytics.create_agent_profile(
            agent_id="agent1",
            name="Developer Agent",
            role=AgentRole.DEVELOPER,
            capabilities=["python", "javascript", "api_development"]
        )
        
        self.agent2 = self.analytics.create_agent_profile(
            agent_id="agent2",
            name="QA Agent",
            role=AgentRole.QA_TESTER,
            capabilities=["testing", "bug_reporting", "test_automation"]
        )
        
        self.agent3 = self.analytics.create_agent_profile(
            agent_id="agent3",
            name="Project Manager Agent",
            role=AgentRole.PROJECT_MANAGER,
            capabilities=["planning", "coordination", "reporting"]
        )
    
    def test_performance_metric_creation(self):
        """Test creating performance metrics."""
        # Create a metric
        metric = PerformanceMetric(
            metric_id="metric1",
            agent_id="agent1",
            metric_type=MetricType.COMPLETION_TIME,
            value=45.5,
            unit=MetricUnit.MINUTES,
            task_id="task1"
        )
        
        self.assertEqual(metric.metric_id, "metric1")
        self.assertEqual(metric.agent_id, "agent1")
        self.assertEqual(metric.metric_type, MetricType.COMPLETION_TIME)
        self.assertEqual(metric.value, 45.5)
        self.assertEqual(metric.unit, MetricUnit.MINUTES)
        self.assertEqual(metric.task_id, "task1")
        self.assertIsInstance(metric.timestamp, datetime.datetime)
    
    def test_agent_task_lifecycle(self):
        """Test the lifecycle of an agent task."""
        # Create a task
        task = AgentTask(
            task_id="task1",
            agent_id="agent1",
            title="Implement API Endpoint",
            description="Create a new REST API endpoint for user authentication.",
            priority=TaskPriority.HIGH,
            estimated_duration=60.0  # minutes
        )
        
        self.assertEqual(task.task_id, "task1")
        self.assertEqual(task.agent_id, "agent1")
        self.assertEqual(task.title, "Implement API Endpoint")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIsNone(task.started_at)
        self.assertIsNone(task.completed_at)
        
        # Start the task
        task.start()
        
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        self.assertIsNotNone(task.started_at)
        self.assertIsNone(task.completed_at)
        
        # Complete the task
        task.complete()
        
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.completed_at)
        self.assertIsNotNone(task.actual_duration)
        
        # Check completion percentage
        self.assertEqual(task.get_completion_percentage(), 100.0)
    
    def test_agent_profile_metrics(self):
        """Test adding metrics to an agent profile."""
        # Create metrics
        completion_metric = PerformanceMetric(
            metric_id="metric1",
            agent_id="agent1",
            metric_type=MetricType.COMPLETION_TIME,
            value=45.5,
            unit=MetricUnit.MINUTES,
            task_id="task1"
        )
        
        quality_metric = PerformanceMetric(
            metric_id="metric2",
            agent_id="agent1",
            metric_type=MetricType.QUALITY,
            value=85.0,
            unit=MetricUnit.PERCENTAGE,
            task_id="task1"
        )
        
        # Add metrics to agent profile
        self.agent1.add_metric(completion_metric)
        self.agent1.add_metric(quality_metric)
        
        # Check metrics were added
        self.assertEqual(len(self.agent1.metrics), 2)
        
        # Check performance history was updated
        self.assertIn(MetricType.COMPLETION_TIME.value, self.agent1.performance_history)
        self.assertIn(MetricType.QUALITY.value, self.agent1.performance_history)
        self.assertEqual(len(self.agent1.performance_history[MetricType.COMPLETION_TIME.value]), 1)
        self.assertEqual(len(self.agent1.performance_history[MetricType.QUALITY.value]), 1)
    
    def test_agent_task_management(self):
        """Test managing tasks for an agent."""
        # Create tasks
        task1 = AgentTask(
            task_id="task1",
            agent_id="agent1",
            title="Implement API Endpoint",
            description="Create a new REST API endpoint for user authentication.",
            priority=TaskPriority.HIGH,
            estimated_duration=60.0
        )
        
        task2 = AgentTask(
            task_id="task2",
            agent_id="agent1",
            title="Fix Bug in Login Flow",
            description="Address the issue with login validation.",
            priority=TaskPriority.CRITICAL,
            estimated_duration=30.0
        )
        
        # Add tasks to agent profile
        self.agent1.add_task(task1)
        self.agent1.add_task(task2)
        
        # Check tasks were added
        self.assertEqual(len(self.agent1.tasks), 2)
        self.assertIn("task1", self.agent1.tasks)
        self.assertIn("task2", self.agent1.tasks)
        
        # Start and complete tasks
        task1.start()
        task2.start()
        
        task1.complete()
        
        # Check task status
        self.assertEqual(self.agent1.tasks["task1"].status, TaskStatus.COMPLETED)
        self.assertEqual(self.agent1.tasks["task2"].status, TaskStatus.IN_PROGRESS)
    
    def test_agent_capabilities(self):
        """Test managing agent capabilities."""
        # Add capabilities
        self.agent1.add_capability("database_design")
        self.agent1.add_capability("system_architecture")
        
        # Check capabilities were added
        self.assertIn("database_design", self.agent1.capabilities)
        self.assertIn("system_architecture", self.agent1.capabilities)
        
        # Add duplicate capability (should not duplicate)
        self.agent1.add_capability("python")
        
        # Count occurrences of "python"
        python_count = self.agent1.capabilities.count("python")
        self.assertEqual(python_count, 1)
    
    def test_agent_strengths_and_improvements(self):
        """Test managing agent strengths and areas for improvement."""
        # Add strengths
        self.agent1.add_strength("Fast code implementation")
        self.agent1.add_strength("Clean code structure")
        
        # Add areas for improvement
        self.agent1.add_area_for_improvement("Documentation quality")
        self.agent1.add_area_for_improvement("Test coverage")
        
        # Check they were added
        self.assertIn("Fast code implementation", self.agent1.strengths)
        self.assertIn("Clean code structure", self.agent1.strengths)
        self.assertIn("Documentation quality", self.agent1.areas_for_improvement)
        self.assertIn("Test coverage", self.agent1.areas_for_improvement)
    
    def test_average_metrics(self):
        """Test calculating average metrics."""
        # Create and add multiple metrics
        for i in range(5):
            completion_metric = PerformanceMetric(
                metric_id=f"completion{i}",
                agent_id="agent1",
                metric_type=MetricType.COMPLETION_TIME,
                value=30.0 + i * 10,  # 30, 40, 50, 60, 70
                unit=MetricUnit.MINUTES,
                task_id=f"task{i}"
            )
            
            quality_metric = PerformanceMetric(
                metric_id=f"quality{i}",
                agent_id="agent1",
                metric_type=MetricType.QUALITY,
                value=80.0 + i * 2,  # 80, 82, 84, 86, 88
                unit=MetricUnit.PERCENTAGE,
                task_id=f"task{i}"
            )
            
            self.agent1.add_metric(completion_metric)
            self.agent1.add_metric(quality_metric)
        
        # Calculate average completion time
        avg_completion = self.agent1.get_average_metric(MetricType.COMPLETION_TIME)
        self.assertEqual(avg_completion, 50.0)  # (30+40+50+60+70)/5 = 50
        
        # Calculate average quality
        avg_quality = self.agent1.get_average_metric(MetricType.QUALITY)
        self.assertEqual(avg_quality, 84.0)  # (80+82+84+86+88)/5 = 84
    
    def test_performance_trends(self):
        """Test calculating performance trends."""
        # Create timestamps
        now = datetime.datetime.now()
        timestamps = [
            now - datetime.timedelta(days=4),
            now - datetime.timedelta(days=3),
            now - datetime.timedelta(days=2),
            now - datetime.timedelta(days=1),
            now
        ]
        
        # Create and add metrics with specific timestamps
        for i in range(5):
            completion_metric = PerformanceMetric(
                metric_id=f"completion{i}",
                agent_id="agent1",
                metric_type=MetricType.COMPLETION_TIME,
                value=70.0 - i * 10,  # 70, 60, 50, 40, 30 (improving)
                unit=MetricUnit.MINUTES,
                task_id=f"task{i}",
                timestamp=timestamps[i]
            )
            
            self.agent1.add_metric(completion_metric)
        
        # Calculate trend (should be negative, indicating improvement)
        trend = self.agent1.calculate_metric_trend(MetricType.COMPLETION_TIME)
        self.assertLess(trend, 0)
    
    def test_performance_analytics_system(self):
        """Test the performance analytics system."""
        # Create tasks
        task1 = self.analytics.create_task(
            agent_id="agent1",
            title="Implement API Endpoint",
            description="Create a new REST API endpoint for user authentication.",
            priority=TaskPriority.HIGH,
            estimated_duration=60.0
        )
        
        task2 = self.analytics.create_task(
            agent_id="agent2",
            title="Test API Endpoint",
            description="Verify the functionality of the new API endpoint.",
            priority=TaskPriority.MEDIUM,
            estimated_duration=45.0
        )
        
        # Start tasks
        self.analytics.start_task(task1.task_id)
        self.analytics.start_task(task2.task_id)
        
        # Record metrics
        self.analytics.record_metric(
            agent_id="agent1",
            metric_type=MetricType.COMPLETION_TIME,
            value=55.0,
            unit=MetricUnit.MINUTES,
            task_id=task1.task_id
        )
        
        self.analytics.record_metric(
            agent_id="agent1",
            metric_type=MetricType.QUALITY,
            value=90.0,
            unit=MetricUnit.PERCENTAGE,
            task_id=task1.task_id
        )
        
        self.analytics.record_metric(
            agent_id="agent2",
            metric_type=MetricType.COMPLETION_TIME,
            value=40.0,
            unit=MetricUnit.MINUTES,
            task_id=task2.task_id
        )
        
        self.analytics.record_metric(
            agent_id="agent2",
            metric_type=MetricType.ACCURACY,
            value=95.0,
            unit=MetricUnit.PERCENTAGE,
            task_id=task2.task_id
        )
        
        # Complete tasks
        self.analytics.complete_task(task1.task_id)
        self.analytics.complete_task(task2.task_id)
        
        # Get agent profiles
        agent1_profile = self.analytics.get_agent_profile("agent1")
        agent2_profile = self.analytics.get_agent_profile("agent2")
        
        # Check metrics were recorded
        self.assertEqual(len(agent1_profile.metrics), 2)
        self.assertEqual(len(agent2_profile.metrics), 2)
        
        # Check tasks were completed
        self.assertEqual(agent1_profile.tasks[task1.task_id].status, TaskStatus.COMPLETED)
        self.assertEqual(agent2_profile.tasks[task2.task_id].status, TaskStatus.COMPLETED)
    
    def test_performance_report_generation(self):
        """Test generating performance reports."""
        # Add tasks and metrics
        for i in range(5):
            task = self.analytics.create_task(
                agent_id="agent1",
                title=f"Task {i+1}",
                description=f"Description for Task {i+1}",
                priority=TaskPriority.MEDIUM,
                estimated_duration=30.0
            )
            
            self.analytics.start_task(task.task_id)
            
            self.analytics.record_metric(
                agent_id="agent1",
                metric_type=MetricType.COMPLETION_TIME,
                value=25.0 + i * 2,
                unit=MetricUnit.MINUTES,
                task_id=task.task_id
            )
            
            self.analytics.record_metric(
                agent_id="agent1",
                metric_type=MetricType.QUALITY,
                value=85.0 + i,
                unit=MetricUnit.PERCENTAGE,
                task_id=task.task_id
            )
            
            self.analytics.complete_task(task.task_id)
        
        # Generate individual agent report
        agent_report = self.analytics.generate_agent_report("agent1")
        
        self.assertIsInstance(agent_report, PerformanceReport)
        self.assertEqual(agent_report.agent_id, "agent1")
        self.assertEqual(len(agent_report.metrics_summary), 2)  # COMPLETION_TIME and QUALITY
        self.assertEqual(len(agent_report.tasks_summary), 5)
        
        # Generate team report
        team_report = self.analytics.generate_team_report(["agent1", "agent2", "agent3"])
        
        self.assertIsInstance(team_report, PerformanceReport)
        self.assertEqual(team_report.report_type, "team")
        self.assertGreaterEqual(len(team_report.agent_summaries), 3)
    
    def test_performance_visualization(self):
        """Test performance visualization."""
        # Add metrics for visualization
        for i in range(10):
            timestamp = datetime.datetime.now() - datetime.timedelta(days=9-i)
            
            self.analytics.record_metric(
                agent_id="agent1",
                metric_type=MetricType.COMPLETION_TIME,
                value=50.0 - i * 2,  # Improving over time
                unit=MetricUnit.MINUTES,
                timestamp=timestamp
            )
            
            self.analytics.record_metric(
                agent_id="agent1",
                metric_type=MetricType.QUALITY,
                value=80.0 + i,  # Improving over time
                unit=MetricUnit.PERCENTAGE,
                timestamp=timestamp
            )
        
        # Create visualization
        visualization = self.analytics.create_visualization(
            agent_id="agent1",
            metric_type=MetricType.COMPLETION_TIME,
            chart_type="line",
            title="Completion Time Trend",
            time_period=(datetime.datetime.now() - datetime.timedelta(days=10), datetime.datetime.now())
        )
        
        self.assertIsInstance(visualization, PerformanceVisualization)
        self.assertEqual(visualization.agent_id, "agent1")
        self.assertEqual(visualization.metric_type, MetricType.COMPLETION_TIME)
        self.assertEqual(visualization.chart_type, "line")
        
        # Check visualization data
        self.assertEqual(len(visualization.data_points), 10)
        
        # Check trend direction (should be negative/improving for completion time)
        self.assertLess(visualization.trend, 0)
    
    def test_team_performance_monitor(self):
        """Test the team performance monitor."""
        # Create team monitor
        team_monitor = TeamPerformanceMonitor(self.analytics)
        
        # Add agents to team
        team_monitor.add_agent("agent1")
        team_monitor.add_agent("agent2")
        team_monitor.add_agent("agent3")
        
        # Check team composition
        team_composition = team_monitor.get_team_composition()
        self.assertEqual(len(team_composition), 3)
        
        # Add tasks
        for i in range(3):
            for agent_id in ["agent1", "agent2", "agent3"]:
                task = self.analytics.create_task(
                    agent_id=agent_id,
                    title=f"Task {i+1} for {agent_id}",
                    description=f"Description for Task {i+1}",
                    priority=TaskPriority.MEDIUM,
                    estimated_duration=30.0
                )
                
                self.analytics.start_task(task.task_id)
                
                # Record different metrics based on agent role
                if agent_id == "agent1":  # Developer
                    self.analytics.record_metric(
                        agent_id=agent_id,
                        metric_type=MetricType.COMPLETION_TIME,
                        value=25.0 + i * 5,
                        unit=MetricUnit.MINUTES,
                        task_id=task.task_id
                    )
                    
                    self.analytics.record_metric(
                        agent_id=agent_id,
                        metric_type=MetricType.QUALITY,
                        value=85.0 + i * 2,
                        unit=MetricUnit.PERCENTAGE,
                        task_id=task.task_id
                    )
                    
                elif agent_id == "agent2":  # QA
                    self.analytics.record_metric(
                        agent_id=agent_id,
                        metric_type=MetricType.ACCURACY,
                        value=90.0 + i * 2,
                        unit=MetricUnit.PERCENTAGE,
                        task_id=task.task_id
                    )
                    
                    self.analytics.record_metric(
                        agent_id=agent_id,
                        metric_type=MetricType.THROUGHPUT,
                        value=10.0 + i,
                        unit=MetricUnit.COUNT,
                        task_id=task.task_id
                    )
                    
                else:  # Project Manager
                    self.analytics.record_metric(
                        agent_id=agent_id,
                        metric_type=MetricType.EFFICIENCY,
                        value=80.0 + i * 3,
                        unit=MetricUnit.PERCENTAGE,
                        task_id=task.task_id
                    )
                
                self.analytics.complete_task(task.task_id)
        
        # Get team performance summary
        team_summary = team_monitor.get_team_performance_summary()
        
        self.assertIsInstance(team_summary, dict)
        self.assertIn("overall_metrics", team_summary)
        self.assertIn("agent_metrics", team_summary)
        self.assertIn("task_completion", team_summary)
        
        # Check workload distribution
        workload = team_monitor.get_workload_distribution()
        self.assertEqual(len(workload), 3)
        
        # Check role-based performance
        role_performance = team_monitor.get_role_based_performance()
        self.assertIn(AgentRole.DEVELOPER.value, role_performance)
        self.assertIn(AgentRole.QA_TESTER.value, role_performance)
        self.assertIn(AgentRole.PROJECT_MANAGER.value, role_performance)
    
    def test_serialization(self):
        """Test serialization and deserialization of performance data."""
        # Create a task
        task = AgentTask(
            task_id="task_serialize",
            agent_id="agent1",
            title="Serialization Test Task",
            description="Testing serialization and deserialization.",
            priority=TaskPriority.MEDIUM,
            estimated_duration=45.0
        )
        
        # Start and complete the task
        task.start()
        task.complete()
        
        # Add a metric
        metric = PerformanceMetric(
            metric_id="metric_serialize",
            agent_id="agent1",
            metric_type=MetricType.COMPLETION_TIME,
            value=40.0,
            unit=MetricUnit.MINUTES,
            task_id="task_serialize"
        )
        
        # Convert to dictionaries
        task_dict = task.to_dict()
        metric_dict = metric.to_dict()
        
        # Create from dictionaries
        new_task = AgentTask.from_dict(task_dict)
        new_metric = PerformanceMetric.from_dict(metric_dict)
        
        # Check equality
        self.assertEqual(new_task.task_id, task.task_id)
        self.assertEqual(new_task.title, task.title)
        self.assertEqual(new_task.status, task.status)
        
        self.assertEqual(new_metric.metric_id, metric.metric_id)
        self.assertEqual(new_metric.metric_type, metric.metric_type)
        self.assertEqual(new_metric.value, metric.value)


if __name__ == "__main__":
    unittest.main()
