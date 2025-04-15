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

"""Performance Monitoring Module

This module provides utilities for monitoring and analyzing performance
of database operations and API calls."""

import logging
import time
import threading
import json
import os
from typing import Dict, Any, List, Optional, Callable, Union
from functools import wraps
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

class PerformanceMetric:
    """Performance metric for a single operation."""
    
    def __init__(self, name: str, category: str = None):
        """Initialize a performance metric.
        
        Args:
            name: Metric name
            category: Metric category"""
        self.name = name
        self.category = category or "default"
        self.calls = 0
        self.total_time = 0.0
        self.min_time = float('inf')
        self.max_time = 0.0
        self.times = []
        self.errors = 0
        self.last_call_time = None
        self.last_error_time = None
        self.last_error = None
    
    def record_call(self, duration: float, error: Exception = None) -> None:
        """Record a call to the operation.
        
        Args:
            duration: Call duration in seconds
            error: Exception if call failed"""
        self.calls += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.times.append(duration)
        self.last_call_time = time.time()
        
        if error:
            self.errors += 1
            self.last_error_time = time.time()
            self.last_error = str(error)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics.
        
        Returns:
            Performance statistics"""
        stats = {
            "name": self.name,
            "category": self.category,
            "calls": self.calls,
            "total_time": self.total_time,
            "avg_time": self.total_time / self.calls if self.calls > 0 else 0,
            "min_time": self.min_time if self.calls > 0 else 0,
            "max_time": self.max_time,
            "errors": self.errors,
            "error_rate": self.errors / self.calls if self.calls > 0 else 0,
            "last_call_time": self.last_call_time
        }
        
        # Calculate percentiles if we have enough data
        if len(self.times) >= 10:
            stats["median_time"] = statistics.median(self.times)
            stats["p95_time"] = statistics.quantiles(self.times, n=20)[18]  # 95th percentile
            stats["p99_time"] = statistics.quantiles(self.times, n=100)[98]  # 99th percentile
        
        if self.last_error:
            stats["last_error"] = self.last_error
            stats["last_error_time"] = self.last_error_time
        
        return stats

class PerformanceMonitor:
    """Performance monitor for tracking operation performance."""
    
    def __init__(self, max_metrics: int = 1000):
        """Initialize the performance monitor.
        
        Args:
            max_metrics: Maximum number of metrics to track"""
        self._metrics: Dict[str, PerformanceMetric] = {}
        self._max_metrics = max_metrics
        self._lock = threading.RLock()
        logger.info(f"Initialized performance monitor with max_metrics={max_metrics}")
    
    def record(self, name: str, duration: float, category: str = None, error: Exception = None) -> None:
        """Record a performance metric.
        
        Args:
            name: Metric name
            duration: Operation duration in seconds
            category: Metric category
            error: Exception if operation failed"""
        with self._lock:
            # Check if we need to create a new metric
            if name not in self._metrics:
                # Check if we've reached the maximum number of metrics
                if len(self._metrics) >= self._max_metrics:
                    # Remove the least used metric
                    least_used = min(self._metrics.items(), key=lambda x: x[1].calls)
                    del self._metrics[least_used[0]]
                
                # Create new metric
                self._metrics[name] = PerformanceMetric(name, category)
            
            # Record the call
            self._metrics[name].record_call(duration, error)
    
    def get_metrics(self, category: str = None) -> List[Dict[str, Any]]:
        """Get all performance metrics.
        
        Args:
            category: Filter by category
            
        Returns:
            List of performance metrics"""
        with self._lock:
            metrics = []
            
            for metric in self._metrics.values():
                if category is None or metric.category == category:
                    metrics.append(metric.get_stats())
            
            return metrics
    
    def get_metric(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific performance metric.
        
        Args:
            name: Metric name
            
        Returns:
            Performance metric or None if not found"""
        with self._lock:
            if name in self._metrics:
                return self._metrics[name].get_stats()
            return None
    
    def get_categories(self) -> List[str]:
        """Get all metric categories.
        
        Returns:
            List of categories"""
        with self._lock:
            return list(set(metric.category for metric in self._metrics.values()))
    
    def clear(self, category: str = None) -> None:
        """Clear performance metrics.
        
        Args:
            category: Filter by category"""
        with self._lock:
            if category is None:
                self._metrics.clear()
            else:
                keys_to_delete = [name for name, metric in self._metrics.items() if metric.category == category]
                for key in keys_to_delete:
                    del self._metrics[key]
    
    def export_to_json(self, file_path: str, category: str = None) -> None:
        """Export performance metrics to a JSON file.
        
        Args:
            file_path: Output file path
            category: Filter by category"""
        metrics = self.get_metrics(category)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"Exported {len(metrics)} performance metrics to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting performance metrics to {file_path}: {str(e)}")
    
    def get_summary(self, category: str = None) -> Dict[str, Any]:
        """Get a summary of performance metrics.
        
        Args:
            category: Filter by category
            
        Returns:
            Performance summary"""
        metrics = self.get_metrics(category)
        
        if not metrics:
            return {
                "total_metrics": 0,
                "total_calls": 0,
                "total_errors": 0,
                "error_rate": 0,
                "avg_time": 0
            }
        
        total_calls = sum(metric["calls"] for metric in metrics)
        total_errors = sum(metric["errors"] for metric in metrics)
        total_time = sum(metric["total_time"] for metric in metrics)
        
        return {
            "total_metrics": len(metrics),
            "total_calls": total_calls,
            "total_errors": total_errors,
            "error_rate": total_errors / total_calls if total_calls > 0 else 0,
            "avg_time": total_time / total_calls if total_calls > 0 else 0,
            "slowest_operations": sorted(metrics, key=lambda x: x["avg_time"], reverse=True)[:5],
            "most_error_prone": sorted(metrics, key=lambda x: x["error_rate"], reverse=True)[:5],
            "most_called": sorted(metrics, key=lambda x: x["calls"], reverse=True)[:5]
        }

def monitor_performance(name: str = None, category: str = None, monitor: PerformanceMonitor = None):
    """Decorator for monitoring function performance.
    
    Args:
        name: Metric name (None for function name)
        category: Metric category
        monitor: Performance monitor (None for default)
        
    Returns:
        Decorated function"""
    # Use default monitor if not specified
    if monitor is None:
        monitor = _default_monitor
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine metric name
            metric_name = name or f"{func.__module__}.{func.__name__}"
            
            # Record start time
            start_time = time.time()
            error = None
            
            try:
                # Call function
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                # Calculate duration
                duration = time.time() - start_time
                
                # Record metric
                monitor.record(metric_name, duration, category, error)
        return wrapper
    return decorator

# Default performance monitor
_default_monitor = PerformanceMonitor()

def get_default_monitor() -> PerformanceMonitor:
    """Get the default performance monitor.
    
    Returns:
        Default performance monitor"""
    return _default_monitor
