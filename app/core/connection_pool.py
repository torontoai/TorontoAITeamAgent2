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

"""Connection Pool Module

This module provides connection pooling for database and API connections
to improve performance and resource utilization."""

import logging
import time
import threading
import queue
from typing import Dict, Any, Optional, Callable, List, TypeVar, Generic, Union

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic type for connection objects

class PooledConnection(Generic[T]):
    """Wrapper for a pooled connection with metadata."""
    
    def __init__(self, connection: T, created_at: float = None):
        """Initialize a pooled connection.
        
        Args:
            connection: Connection object
            created_at: Creation timestamp"""
        self.connection = connection
        self.created_at = created_at or time.time()
        self.last_used = self.created_at
        self.use_count = 0
        self.in_use = False
    
    def mark_used(self) -> None:
        """Mark the connection as being used."""
        self.last_used = time.time()
        self.use_count += 1
        self.in_use = True
    
    def mark_returned(self) -> None:
        """Mark the connection as returned to the pool."""
        self.in_use = False

class ConnectionPool(Generic[T]):
    """Generic connection pool for database and API connections."""
    
    def __init__(
        self, 
        factory: Callable[[], T], 
        validator: Callable[[T], bool] = None,
        cleanup: Callable[[T], None] = None,
        min_size: int = 1, 
        max_size: int = 10, 
        max_idle_time: int = 300,
        max_age: int = 3600,
        block: bool = True,
        timeout: float = 30.0
    ):
        """Initialize the connection pool.
        
        Args:
            factory: Function to create new connections
            validator: Function to validate connections (None for no validation)
            cleanup: Function to clean up connections (None for no cleanup)
            min_size: Minimum number of connections in the pool
            max_size: Maximum number of connections in the pool
            max_idle_time: Maximum time in seconds a connection can be idle
            max_age: Maximum age in seconds for a connection
            block: Whether to block when getting a connection if none available
            timeout: Timeout in seconds when blocking"""
        self._factory = factory
        self._validator = validator or (lambda conn: True)
        self._cleanup = cleanup or (lambda conn: None)
        self._min_size = min_size
        self._max_size = max_size
        self._max_idle_time = max_idle_time
        self._max_age = max_age
        self._block = block
        self._timeout = timeout
        
        self._pool: List[PooledConnection[T]] = []
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._running = True
        
        # Start maintenance thread
        self._maintenance_thread = threading.Thread(
            target=self._maintenance_loop,
            daemon=True,
            name="ConnectionPool-Maintenance"
        )
        self._maintenance_thread.start()
        
        # Initialize pool with minimum connections
        self._initialize()
        
        logger.info(f"Initialized connection pool with min_size={min_size}, max_size={max_size}")
    
    def _initialize(self) -> None:
        """Initialize the pool with minimum connections."""
        with self._lock:
            for _ in range(self._min_size):
                try:
                    connection = self._create_connection()
                    self._pool.append(connection)
                except Exception as e:
                    logger.error(f"Error creating initial connection: {str(e)}")
    
    def _create_connection(self) -> PooledConnection[T]:
        """Create a new connection.
        
        Returns:
            Pooled connection"""
        try:
            connection = self._factory()
            return PooledConnection(connection)
        except Exception as e:
            logger.error(f"Error creating connection: {str(e)}")
            raise
    
    def _validate_connection(self, pooled_conn: PooledConnection[T]) -> bool:
        """Validate a connection.
        
        Args:
            pooled_conn: Pooled connection
            
        Returns:
            True if valid, False otherwise"""
        try:
            return self._validator(pooled_conn.connection)
        except Exception as e:
            logger.error(f"Error validating connection: {str(e)}")
            return False
    
    def _cleanup_connection(self, pooled_conn: PooledConnection[T]) -> None:
        """Clean up a connection.
        
        Args:
            pooled_conn: Pooled connection"""
        try:
            self._cleanup(pooled_conn.connection)
        except Exception as e:
            logger.error(f"Error cleaning up connection: {str(e)}")
    
    def get_connection(self) -> T:
        """Get a connection from the pool.
        
        Returns:
            Connection object
            
        Raises:
            queue.Empty: If no connection is available and block is False
            TimeoutError: If timeout occurs while waiting for a connection"""
        with self._lock:
            # Check if pool is running
            if not self._running:
                raise RuntimeError("Connection pool is shut down")
            
            # Try to get an available connection
            for i, pooled_conn in enumerate(self._pool):
                if not pooled_conn.in_use:
                    # Validate connection
                    if self._validate_connection(pooled_conn):
                        pooled_conn.mark_used()
                        return pooled_conn.connection
                    else:
                        # Remove invalid connection
                        self._cleanup_connection(pooled_conn)
                        self._pool.pop(i)
            
            # No available connection, create new if possible
            if len(self._pool) < self._max_size:
                try:
                    pooled_conn = self._create_connection()
                    pooled_conn.mark_used()
                    self._pool.append(pooled_conn)
                    return pooled_conn.connection
                except Exception as e:
                    logger.error(f"Error creating new connection: {str(e)}")
            
            # Pool is full and all connections are in use
            if not self._block:
                raise queue.Empty("No connection available")
            
            # Wait for a connection to become available
            start_time = time.time()
            while True:
                # Wait for notification
                self._condition.wait(self._timeout)
                
                # Check if timeout occurred
                if time.time() - start_time > self._timeout:
                    raise TimeoutError("Timeout waiting for connection")
                
                # Try to get an available connection
                for pooled_conn in self._pool:
                    if not pooled_conn.in_use:
                        # Validate connection
                        if self._validate_connection(pooled_conn):
                            pooled_conn.mark_used()
                            return pooled_conn.connection
                        else:
                            # Remove invalid connection
                            self._cleanup_connection(pooled_conn)
                            self._pool.remove(pooled_conn)
    
    def return_connection(self, connection: T) -> None:
        """Return a connection to the pool.
        
        Args:
            connection: Connection object"""
        with self._lock:
            # Find the pooled connection
            for pooled_conn in self._pool:
                if pooled_conn.connection is connection:
                    pooled_conn.mark_returned()
                    # Notify waiters
                    self._condition.notify()
                    return
            
            # Connection not found in pool
            logger.warning("Returned connection not found in pool")
    
    def _maintenance_loop(self) -> None:
        """Maintenance loop for the connection pool."""
        while self._running:
            try:
                # Sleep for a while
                time.sleep(60)
                
                # Perform maintenance
                self._perform_maintenance()
            except Exception as e:
                logger.error(f"Error in maintenance loop: {str(e)}")
    
    def _perform_maintenance(self) -> None:
        """Perform maintenance on the connection pool."""
        with self._lock:
            # Check if pool is running
            if not self._running:
                return
            
            now = time.time()
            to_remove = []
            
            # Check for idle and old connections
            for pooled_conn in self._pool:
                if pooled_conn.in_use:
                    continue
                
                # Check if connection is too old
                if now - pooled_conn.created_at > self._max_age:
                    to_remove.append(pooled_conn)
                    continue
                
                # Check if connection is idle for too long
                if now - pooled_conn.last_used > self._max_idle_time:
                    to_remove.append(pooled_conn)
                    continue
            
            # Remove connections
            for pooled_conn in to_remove:
                self._cleanup_connection(pooled_conn)
                self._pool.remove(pooled_conn)
            
            # Create new connections if needed
            while len(self._pool) < self._min_size:
                try:
                    pooled_conn = self._create_connection()
                    self._pool.append(pooled_conn)
                except Exception as e:
                    logger.error(f"Error creating connection during maintenance: {str(e)}")
                    break
            
            if to_remove:
                logger.debug(f"Removed {len(to_remove)} connections during maintenance")
    
    def shutdown(self) -> None:
        """Shut down the connection pool."""
        with self._lock:
            self._running = False
            
            # Clean up all connections
            for pooled_conn in self._pool:
                self._cleanup_connection(pooled_conn)
            
            # Clear pool
            self._pool.clear()
            
            # Notify all waiters
            self._condition.notify_all()
            
            logger.info("Connection pool shut down")
    
    def stats(self) -> Dict[str, Any]:
        """Get connection pool statistics.
        
        Returns:
            Connection pool statistics"""
        with self._lock:
            in_use = sum(1 for conn in self._pool if conn.in_use)
            return {
                "total": len(self._pool),
                "in_use": in_use,
                "available": len(self._pool) - in_use,
                "min_size": self._min_size,
                "max_size": self._max_size,
                "running": self._running
            }

class ConnectionPoolManager:
    """Manager for multiple connection pools."""
    
    def __init__(self):
        """Initialize the connection pool manager."""
        self._pools: Dict[str, ConnectionPool] = {}
        self._lock = threading.RLock()
        logger.info("Initialized connection pool manager")
    
    def create_pool(
        self, 
        name: str, 
        factory: Callable[[], T], 
        validator: Callable[[T], bool] = None,
        cleanup: Callable[[T], None] = None,
        min_size: int = 1, 
        max_size: int = 10, 
        max_idle_time: int = 300,
        max_age: int = 3600,
        block: bool = True,
        timeout: float = 30.0
    ) -> ConnectionPool[T]:
        """Create a new connection pool.
        
        Args:
            name: Pool name
            factory: Function to create new connections
            validator: Function to validate connections (None for no validation)
            cleanup: Function to clean up connections (None for no cleanup)
            min_size: Minimum number of connections in the pool
            max_size: Maximum number of connections in the pool
            max_idle_time: Maximum time in seconds a connection can be idle
            max_age: Maximum age in seconds for a connection
            block: Whether to block when getting a connection if none available
            timeout: Timeout in seconds when blocking
            
        Returns:
            Connection pool"""
        with self._lock:
            # Check if pool already exists
            if name in self._pools:
                raise ValueError(f"Pool already exists: {name}")
            
            # Create pool
            pool = ConnectionPool(
                factory=factory,
                validator=validator,
                cleanup=cleanup,
                min_size=min_size,
                max_size=max_size,
                max_idle_time=max_idle_time,
                max_age=max_age,
                block=block,
                timeout=timeout
            )
            
            # Store pool
            self._pools[name] = pool
            
            logger.info(f"Created connection pool: {name}")
            return pool
    
    def get_pool(self, name: str) -> ConnectionPool:
        """Get a connection pool by name.
        
        Args:
            name: Pool name
            
        Returns:
            Connection pool
            
        Raises:
            KeyError: If pool not found"""
        with self._lock:
            if name not in self._pools:
                raise KeyError(f"Pool not found: {name}")
            return self._pools[name]
    
    def shutdown_pool(self, name: str) -> None:
        """Shut down a connection pool.
        
        Args:
            name: Pool name
            
        Raises:
            KeyError: If pool not found"""
        with self._lock:
            if name not in self._pools:
                raise KeyError(f"Pool not found: {name}")
            
            # Shut down pool
            self._pools[name].shutdown()
            
            # Remove pool
            del self._pools[name]
            
            logger.info(f"Shut down connection pool: {name}")
    
    def shutdown_all(self) -> None:
        """Shut down all connection pools."""
        with self._lock:
            for name, pool in list(self._pools.items()):
                pool.shutdown()
            
            # Clear pools
            self._pools.clear()
            
            logger.info("Shut down all connection pools")
    
    def stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all connection pools.
        
        Returns:
            Statistics for all connection pools"""
        with self._lock:
            return {name: pool.stats() for name, pool in self._pools.items()}

# Global connection pool manager
_pool_manager = ConnectionPoolManager()

def get_pool_manager() -> ConnectionPoolManager:
    """Get the global connection pool manager.
    
    Returns:
        Global connection pool manager"""
    return _pool_manager
