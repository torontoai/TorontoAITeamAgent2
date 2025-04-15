import unittest
from unittest.mock import Mock, patch
import sys
import os
import time

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.performance import PerformanceMetric, PerformanceMonitor, monitor_performance, get_default_monitor

class PerformanceMetricTests(unittest.TestCase):
    """
    Unit tests for the PerformanceMetric class.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.metric = PerformanceMetric("test_metric", "test_category")
    
    def test_initialization(self):
        """Test metric initialization."""
        # Assert
        self.assertEqual(self.metric.name, "test_metric")
        self.assertEqual(self.metric.category, "test_category")
        self.assertEqual(self.metric.calls, 0)
        self.assertEqual(self.metric.total_time, 0.0)
        self.assertEqual(self.metric.min_time, float('inf'))
        self.assertEqual(self.metric.max_time, 0.0)
        self.assertEqual(self.metric.times, [])
        self.assertEqual(self.metric.errors, 0)
        self.assertIsNone(self.metric.last_call_time)
        self.assertIsNone(self.metric.last_error_time)
        self.assertIsNone(self.metric.last_error)
    
    def test_record_call(self):
        """Test recording a call."""
        # Record a call
        self.metric.record_call(0.5)
        
        # Assert
        self.assertEqual(self.metric.calls, 1)
        self.assertEqual(self.metric.total_time, 0.5)
        self.assertEqual(self.metric.min_time, 0.5)
        self.assertEqual(self.metric.max_time, 0.5)
        self.assertEqual(self.metric.times, [0.5])
        self.assertEqual(self.metric.errors, 0)
        self.assertIsNotNone(self.metric.last_call_time)
        self.assertIsNone(self.metric.last_error_time)
        self.assertIsNone(self.metric.last_error)
    
    def test_record_call_with_error(self):
        """Test recording a call with an error."""
        # Record a call with an error
        error = Exception("Test error")
        self.metric.record_call(0.5, error)
        
        # Assert
        self.assertEqual(self.metric.calls, 1)
        self.assertEqual(self.metric.total_time, 0.5)
        self.assertEqual(self.metric.min_time, 0.5)
        self.assertEqual(self.metric.max_time, 0.5)
        self.assertEqual(self.metric.times, [0.5])
        self.assertEqual(self.metric.errors, 1)
        self.assertIsNotNone(self.metric.last_call_time)
        self.assertIsNotNone(self.metric.last_error_time)
        self.assertEqual(self.metric.last_error, "Test error")
    
    def test_get_stats(self):
        """Test getting performance statistics."""
        # Record some calls
        self.metric.record_call(0.5)
        self.metric.record_call(1.0)
        self.metric.record_call(0.2)
        
        # Get stats
        stats = self.metric.get_stats()
        
        # Assert
        self.assertEqual(stats["name"], "test_metric")
        self.assertEqual(stats["category"], "test_category")
        self.assertEqual(stats["calls"], 3)
        self.assertEqual(stats["total_time"], 1.7)
        self.assertAlmostEqual(stats["avg_time"], 0.5667, places=4)
        self.assertEqual(stats["min_time"], 0.2)
        self.assertEqual(stats["max_time"], 1.0)
        self.assertEqual(stats["errors"], 0)
        self.assertEqual(stats["error_rate"], 0)
        self.assertIsNotNone(stats["last_call_time"])

class PerformanceMonitorTests(unittest.TestCase):
    """
    Unit tests for the PerformanceMonitor class.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.monitor = PerformanceMonitor(max_metrics=10)
    
    def test_record(self):
        """Test recording a performance metric."""
        # Record a metric
        self.monitor.record("test_metric", 0.5, "test_category")
        
        # Get metrics
        metrics = self.monitor.get_metrics()
        
        # Assert
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["name"], "test_metric")
        self.assertEqual(metrics[0]["category"], "test_category")
        self.assertEqual(metrics[0]["calls"], 1)
        self.assertEqual(metrics[0]["total_time"], 0.5)
    
    def test_record_multiple(self):
        """Test recording multiple metrics."""
        # Record multiple metrics
        self.monitor.record("metric1", 0.5, "category1")
        self.monitor.record("metric2", 1.0, "category2")
        self.monitor.record("metric1", 0.2, "category1")
        
        # Get metrics
        metrics = self.monitor.get_metrics()
        
        # Assert
        self.assertEqual(len(metrics), 2)
        
        # Find metrics by name
        metric1 = next(m for m in metrics if m["name"] == "metric1")
        metric2 = next(m for m in metrics if m["name"] == "metric2")
        
        # Assert metric1
        self.assertEqual(metric1["category"], "category1")
        self.assertEqual(metric1["calls"], 2)
        self.assertEqual(metric1["total_time"], 0.7)
        
        # Assert metric2
        self.assertEqual(metric2["category"], "category2")
        self.assertEqual(metric2["calls"], 1)
        self.assertEqual(metric2["total_time"], 1.0)
    
    def test_get_metrics_by_category(self):
        """Test getting metrics by category."""
        # Record metrics in different categories
        self.monitor.record("metric1", 0.5, "category1")
        self.monitor.record("metric2", 1.0, "category2")
        self.monitor.record("metric3", 0.2, "category1")
        
        # Get metrics by category
        metrics = self.monitor.get_metrics("category1")
        
        # Assert
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["category"], "category1")
        self.assertEqual(metrics[1]["category"], "category1")
    
    def test_get_metric(self):
        """Test getting a specific metric."""
        # Record a metric
        self.monitor.record("test_metric", 0.5, "test_category")
        
        # Get the metric
        metric = self.monitor.get_metric("test_metric")
        
        # Assert
        self.assertIsNotNone(metric)
        self.assertEqual(metric["name"], "test_metric")
        self.assertEqual(metric["category"], "test_category")
        self.assertEqual(metric["calls"], 1)
        self.assertEqual(metric["total_time"], 0.5)
    
    def test_get_categories(self):
        """Test getting all categories."""
        # Record metrics in different categories
        self.monitor.record("metric1", 0.5, "category1")
        self.monitor.record("metric2", 1.0, "category2")
        self.monitor.record("metric3", 0.2, "category1")
        
        # Get categories
        categories = self.monitor.get_categories()
        
        # Assert
        self.assertEqual(len(categories), 2)
        self.assertIn("category1", categories)
        self.assertIn("category2", categories)
    
    def test_clear(self):
        """Test clearing metrics."""
        # Record metrics
        self.monitor.record("metric1", 0.5, "category1")
        self.monitor.record("metric2", 1.0, "category2")
        
        # Clear metrics
        self.monitor.clear()
        
        # Get metrics
        metrics = self.monitor.get_metrics()
        
        # Assert
        self.assertEqual(len(metrics), 0)
    
    def test_clear_by_category(self):
        """Test clearing metrics by category."""
        # Record metrics in different categories
        self.monitor.record("metric1", 0.5, "category1")
        self.monitor.record("metric2", 1.0, "category2")
        self.monitor.record("metric3", 0.2, "category1")
        
        # Clear metrics by category
        self.monitor.clear("category1")
        
        # Get metrics
        metrics = self.monitor.get_metrics()
        
        # Assert
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["name"], "metric2")
        self.assertEqual(metrics[0]["category"], "category2")
    
    def test_max_metrics(self):
        """Test maximum number of metrics."""
        # Record more metrics than max_metrics
        for i in range(20):
            self.monitor.record(f"metric{i}", 0.5, "test_category")
        
        # Get metrics
        metrics = self.monitor.get_metrics()
        
        # Assert
        self.assertLessEqual(len(metrics), 10)
    
    def test_get_summary(self):
        """Test getting a performance summary."""
        # Record metrics
        self.monitor.record("metric1", 0.5, "category1")
        self.monitor.record("metric2", 1.0, "category2")
        self.monitor.record("metric1", 0.2, "category1")
        
        # Get summary
        summary = self.monitor.get_summary()
        
        # Assert
        self.assertEqual(summary["total_metrics"], 2)
        self.assertEqual(summary["total_calls"], 3)
        self.assertEqual(summary["total_errors"], 0)
        self.assertEqual(summary["error_rate"], 0)
        self.assertAlmostEqual(summary["avg_time"], 0.5667, places=4)
        self.assertEqual(len(summary["slowest_operations"]), 2)
        self.assertEqual(len(summary["most_error_prone"]), 2)
        self.assertEqual(len(summary["most_called"]), 2)

class MonitorPerformanceDecoratorTests(unittest.TestCase):
    """
    Unit tests for the monitor_performance decorator.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.monitor = PerformanceMonitor()
    
    def test_monitor_performance(self):
        """Test monitoring function performance."""
        # Create a test function
        @monitor_performance(name="test_function", category="test_category", monitor=self.monitor)
        def test_function(arg1, arg2):
            time.sleep(0.1)  # Simulate work
            return arg1 + arg2
        
        # Call function
        result = test_function(1, 2)
        
        # Assert
        self.assertEqual(result, 3)
        
        # Get metric
        metric = self.monitor.get_metric("test_function")
        
        # Assert
        self.assertIsNotNone(metric)
        self.assertEqual(metric["name"], "test_function")
        self.assertEqual(metric["category"], "test_category")
        self.assertEqual(metric["calls"], 1)
        self.assertGreaterEqual(metric["total_time"], 0.1)
    
    def test_monitor_performance_with_error(self):
        """Test monitoring function performance with an error."""
        # Create a test function
        @monitor_performance(name="test_function", category="test_category", monitor=self.monitor)
        def test_function():
            time.sleep(0.1)  # Simulate work
            raise ValueError("Test error")
        
        # Call function
        try:
            test_function()
        except ValueError:
            pass
        
        # Get metric
        metric = self.monitor.get_metric("test_function")
        
        # Assert
        self.assertIsNotNone(metric)
        self.assertEqual(metric["name"], "test_function")
        self.assertEqual(metric["category"], "test_category")
        self.assertEqual(metric["calls"], 1)
        self.assertEqual(metric["errors"], 1)
        self.assertEqual(metric["error_rate"], 1.0)
        self.assertGreaterEqual(metric["total_time"], 0.1)
    
    def test_monitor_performance_default_name(self):
        """Test monitoring function performance with default name."""
        # Create a test function
        @monitor_performance(category="test_category", monitor=self.monitor)
        def test_function():
            time.sleep(0.1)  # Simulate work
        
        # Call function
        test_function()
        
        # Get metric
        metric = self.monitor.get_metric("__main__.test_function")
        
        # Assert
        self.assertIsNotNone(metric)
        self.assertEqual(metric["category"], "test_category")
        self.assertEqual(metric["calls"], 1)
        self.assertGreaterEqual(metric["total_time"], 0.1)

class DefaultMonitorTests(unittest.TestCase):
    """
    Unit tests for the default monitor.
    """
    
    def test_default_monitor(self):
        """Test getting the default monitor."""
        # Get default monitor
        default_monitor = get_default_monitor()
        
        # Assert
        self.assertIsNotNone(default_monitor)
        self.assertIsInstance(default_monitor, PerformanceMonitor)
        
        # Record a metric
        default_monitor.record("test_metric", 0.5, "test_category")
        
        # Get the metric
        metric = default_monitor.get_metric("test_metric")
        
        # Assert
        self.assertIsNotNone(metric)
        self.assertEqual(metric["name"], "test_metric")
        self.assertEqual(metric["category"], "test_category")
        self.assertEqual(metric["calls"], 1)
        self.assertEqual(metric["total_time"], 0.5)

if __name__ == "__main__":
    unittest.main()
