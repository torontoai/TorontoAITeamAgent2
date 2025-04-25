"""
Audit Trail System for TORONTO AI TEAM AGENT.

This module provides functionality to maintain comprehensive logs of all agent actions
for accountability and compliance.
"""

import os
import json
import logging
import time
import uuid
import hashlib
import threading
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import datetime
import sqlite3
import queue


class AuditEventType(Enum):
    """Enum representing different types of audit events."""
    AGENT_ACTION = "agent_action"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"
    USER_ACTION = "user_action"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION_CHANGE = "configuration_change"
    ERROR = "error"


class AuditEventSeverity(Enum):
    """Enum representing severity levels for audit events."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class AuditEvent:
    """Class representing an audit event."""
    id: str
    event_type: AuditEventType
    timestamp: float
    actor: str
    action: str
    resource: str
    status: str
    severity: AuditEventSeverity
    details: Dict[str, Any] = field(default_factory=dict)
    source_ip: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    @property
    def formatted_timestamp(self) -> str:
        """Get a formatted timestamp string."""
        return datetime.datetime.fromtimestamp(self.timestamp).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the audit event to a dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "formatted_timestamp": self.formatted_timestamp,
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "status": self.status,
            "severity": self.severity.value,
            "details": self.details,
            "source_ip": self.source_ip,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create an audit event from a dictionary."""
        return cls(
            id=data["id"],
            event_type=AuditEventType(data["event_type"]),
            timestamp=data["timestamp"],
            actor=data["actor"],
            action=data["action"],
            resource=data["resource"],
            status=data["status"],
            severity=AuditEventSeverity(data["severity"]),
            details=data.get("details", {}),
            source_ip=data.get("source_ip"),
            session_id=data.get("session_id"),
            correlation_id=data.get("correlation_id")
        )
    
    def get_hash(self) -> str:
        """
        Get a hash of the audit event for integrity verification.
        
        Returns:
            SHA-256 hash of the event data
        """
        event_data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(event_data.encode()).hexdigest()


class AuditEventBuilder:
    """Builder class for creating audit events."""
    
    def __init__(self):
        """Initialize the audit event builder."""
        self.id = str(uuid.uuid4())
        self.event_type = AuditEventType.SYSTEM_EVENT
        self.timestamp = time.time()
        self.actor = "system"
        self.action = ""
        self.resource = ""
        self.status = "success"
        self.severity = AuditEventSeverity.INFO
        self.details = {}
        self.source_ip = None
        self.session_id = None
        self.correlation_id = None
    
    def with_id(self, id: str) -> 'AuditEventBuilder':
        """Set the event ID."""
        self.id = id
        return self
    
    def with_event_type(self, event_type: AuditEventType) -> 'AuditEventBuilder':
        """Set the event type."""
        self.event_type = event_type
        return self
    
    def with_timestamp(self, timestamp: float) -> 'AuditEventBuilder':
        """Set the timestamp."""
        self.timestamp = timestamp
        return self
    
    def with_actor(self, actor: str) -> 'AuditEventBuilder':
        """Set the actor."""
        self.actor = actor
        return self
    
    def with_action(self, action: str) -> 'AuditEventBuilder':
        """Set the action."""
        self.action = action
        return self
    
    def with_resource(self, resource: str) -> 'AuditEventBuilder':
        """Set the resource."""
        self.resource = resource
        return self
    
    def with_status(self, status: str) -> 'AuditEventBuilder':
        """Set the status."""
        self.status = status
        return self
    
    def with_severity(self, severity: AuditEventSeverity) -> 'AuditEventBuilder':
        """Set the severity."""
        self.severity = severity
        return self
    
    def with_details(self, details: Dict[str, Any]) -> 'AuditEventBuilder':
        """Set the details."""
        self.details = details
        return self
    
    def with_source_ip(self, source_ip: str) -> 'AuditEventBuilder':
        """Set the source IP."""
        self.source_ip = source_ip
        return self
    
    def with_session_id(self, session_id: str) -> 'AuditEventBuilder':
        """Set the session ID."""
        self.session_id = session_id
        return self
    
    def with_correlation_id(self, correlation_id: str) -> 'AuditEventBuilder':
        """Set the correlation ID."""
        self.correlation_id = correlation_id
        return self
    
    def build(self) -> AuditEvent:
        """Build the audit event."""
        return AuditEvent(
            id=self.id,
            event_type=self.event_type,
            timestamp=self.timestamp,
            actor=self.actor,
            action=self.action,
            resource=self.resource,
            status=self.status,
            severity=self.severity,
            details=self.details,
            source_ip=self.source_ip,
            session_id=self.session_id,
            correlation_id=self.correlation_id
        )


class AuditEventStorage:
    """Base class for audit event storage backends."""
    
    def store_event(self, event: AuditEvent) -> bool:
        """
        Store an audit event.
        
        Args:
            event: Audit event to store
            
        Returns:
            True if the event was stored successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """
        Get an audit event by ID.
        
        Args:
            event_id: ID of the event to get
            
        Returns:
            Audit event, or None if not found
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def query_events(self, filters: Dict[str, Any] = None, 
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None) -> List[AuditEvent]:
        """
        Query audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of audit events matching the query
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def count_events(self, filters: Dict[str, Any] = None,
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None) -> int:
        """
        Count audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            
        Returns:
            Number of audit events matching the query
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an audit event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if the event was deleted successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def delete_events(self, filters: Dict[str, Any] = None,
                    start_time: Optional[float] = None,
                    end_time: Optional[float] = None) -> int:
        """
        Delete audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            
        Returns:
            Number of audit events deleted
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def close(self):
        """Close the storage backend."""
        pass


class FileAuditEventStorage(AuditEventStorage):
    """File-based audit event storage backend."""
    
    def __init__(self, file_path: str):
        """
        Initialize the file-based audit event storage.
        
        Args:
            file_path: Path to the audit log file
        """
        self.file_path = file_path
        self.lock = threading.Lock()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Create file if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("")
    
    def store_event(self, event: AuditEvent) -> bool:
        """
        Store an audit event.
        
        Args:
            event: Audit event to store
            
        Returns:
            True if the event was stored successfully, False otherwise
        """
        try:
            with self.lock:
                with open(self.file_path, "a") as f:
                    f.write(json.dumps(event.to_dict()) + "\n")
            return True
        except Exception as e:
            logging.error(f"Error storing audit event: {e}")
            return False
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """
        Get an audit event by ID.
        
        Args:
            event_id: ID of the event to get
            
        Returns:
            Audit event, or None if not found
        """
        try:
            with self.lock:
                with open(self.file_path, "r") as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            if event_data.get("id") == event_id:
                                return AuditEvent.from_dict(event_data)
                        except json.JSONDecodeError:
                            continue
            return None
        except Exception as e:
            logging.error(f"Error getting audit event: {e}")
            return None
    
    def query_events(self, filters: Dict[str, Any] = None, 
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None) -> List[AuditEvent]:
        """
        Query audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of audit events matching the query
        """
        if filters is None:
            filters = {}
        
        events = []
        skipped = 0
        
        try:
            with self.lock:
                with open(self.file_path, "r") as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            
                            # Apply time filters
                            timestamp = event_data.get("timestamp", 0)
                            if start_time is not None and timestamp < start_time:
                                continue
                            if end_time is not None and timestamp >= end_time:
                                continue
                            
                            # Apply other filters
                            match = True
                            for key, value in filters.items():
                                if key not in event_data or event_data[key] != value:
                                    match = False
                                    break
                            
                            if not match:
                                continue
                            
                            # Apply offset
                            if offset is not None and skipped < offset:
                                skipped += 1
                                continue
                            
                            # Add event to results
                            events.append(AuditEvent.from_dict(event_data))
                            
                            # Apply limit
                            if limit is not None and len(events) >= limit:
                                break
                        except json.JSONDecodeError:
                            continue
            
            return events
        except Exception as e:
            logging.error(f"Error querying audit events: {e}")
            return []
    
    def count_events(self, filters: Dict[str, Any] = None,
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None) -> int:
        """
        Count audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            
        Returns:
            Number of audit events matching the query
        """
        if filters is None:
            filters = {}
        
        count = 0
        
        try:
            with self.lock:
                with open(self.file_path, "r") as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            
                            # Apply time filters
                            timestamp = event_data.get("timestamp", 0)
                            if start_time is not None and timestamp < start_time:
                                continue
                            if end_time is not None and timestamp >= end_time:
                                continue
                            
                            # Apply other filters
                            match = True
                            for key, value in filters.items():
                                if key not in event_data or event_data[key] != value:
                                    match = False
                                    break
                            
                            if not match:
                                continue
                            
                            # Increment count
                            count += 1
                        except json.JSONDecodeError:
                            continue
            
            return count
        except Exception as e:
            logging.error(f"Error counting audit events: {e}")
            return 0
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an audit event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if the event was deleted successfully, False otherwise
        """
        try:
            with self.lock:
                # Read all events
                events = []
                with open(self.file_path, "r") as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            if event_data.get("id") != event_id:
                                events.append(line)
                        except json.JSONDecodeError:
                            events.append(line)
                
                # Write back all events except the one to delete
                with open(self.file_path, "w") as f:
                    f.writelines(events)
            
            return True
        except Exception as e:
            logging.error(f"Error deleting audit event: {e}")
            return False
    
    def delete_events(self, filters: Dict[str, Any] = None,
                    start_time: Optional[float] = None,
                    end_time: Optional[float] = None) -> int:
        """
        Delete audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            
        Returns:
            Number of audit events deleted
        """
        if filters is None:
            filters = {}
        
        deleted_count = 0
        
        try:
            with self.lock:
                # Read all events
                events_to_keep = []
                with open(self.file_path, "r") as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            
                            # Apply time filters
                            timestamp = event_data.get("timestamp", 0)
                            if start_time is not None and timestamp < start_time:
                                events_to_keep.append(line)
                                continue
                            if end_time is not None and timestamp >= end_time:
                                events_to_keep.append(line)
                                continue
                            
                            # Apply other filters
                            match = True
                            for key, value in filters.items():
                                if key not in event_data or event_data[key] != value:
                                    match = False
                                    break
                            
                            if not match:
                                events_to_keep.append(line)
                                continue
                            
                            # Event matches filters, don't keep it
                            deleted_count += 1
                        except json.JSONDecodeError:
                            events_to_keep.append(line)
                
                # Write back events to keep
                with open(self.file_path, "w") as f:
                    f.writelines(events_to_keep)
            
            return deleted_count
        except Exception as e:
            logging.error(f"Error deleting audit events: {e}")
            return 0


class SQLiteAuditEventStorage(AuditEventStorage):
    """SQLite-based audit event storage backend."""
    
    def __init__(self, db_path: str):
        """
        Initialize the SQLite-based audit event storage.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Create audit events table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    status TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    details TEXT NOT NULL,
                    source_ip TEXT,
                    session_id TEXT,
                    correlation_id TEXT
                )
                ''')
                
                # Create index on timestamp for efficient querying
                cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp
                ON audit_events (timestamp)
                ''')
                
                conn.commit()
            finally:
                conn.close()
    
    def store_event(self, event: AuditEvent) -> bool:
        """
        Store an audit event.
        
        Args:
            event: Audit event to store
            
        Returns:
            True if the event was stored successfully, False otherwise
        """
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                try:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    INSERT INTO audit_events (
                        id, event_type, timestamp, actor, action, resource,
                        status, severity, details, source_ip, session_id, correlation_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event.id,
                        event.event_type.value,
                        event.timestamp,
                        event.actor,
                        event.action,
                        event.resource,
                        event.status,
                        event.severity.value,
                        json.dumps(event.details),
                        event.source_ip,
                        event.session_id,
                        event.correlation_id
                    ))
                    
                    conn.commit()
                    return True
                finally:
                    conn.close()
        except Exception as e:
            logging.error(f"Error storing audit event: {e}")
            return False
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """
        Get an audit event by ID.
        
        Args:
            event_id: ID of the event to get
            
        Returns:
            Audit event, or None if not found
        """
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                try:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    SELECT id, event_type, timestamp, actor, action, resource,
                           status, severity, details, source_ip, session_id, correlation_id
                    FROM audit_events
                    WHERE id = ?
                    ''', (event_id,))
                    
                    row = cursor.fetchone()
                    if row is None:
                        return None
                    
                    return AuditEvent(
                        id=row[0],
                        event_type=AuditEventType(row[1]),
                        timestamp=row[2],
                        actor=row[3],
                        action=row[4],
                        resource=row[5],
                        status=row[6],
                        severity=AuditEventSeverity(row[7]),
                        details=json.loads(row[8]),
                        source_ip=row[9],
                        session_id=row[10],
                        correlation_id=row[11]
                    )
                finally:
                    conn.close()
        except Exception as e:
            logging.error(f"Error getting audit event: {e}")
            return None
    
    def query_events(self, filters: Dict[str, Any] = None, 
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None) -> List[AuditEvent]:
        """
        Query audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of audit events matching the query
        """
        if filters is None:
            filters = {}
        
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                try:
                    cursor = conn.cursor()
                    
                    # Build query
                    query = '''
                    SELECT id, event_type, timestamp, actor, action, resource,
                           status, severity, details, source_ip, session_id, correlation_id
                    FROM audit_events
                    WHERE 1=1
                    '''
                    params = []
                    
                    # Add time filters
                    if start_time is not None:
                        query += " AND timestamp >= ?"
                        params.append(start_time)
                    
                    if end_time is not None:
                        query += " AND timestamp < ?"
                        params.append(end_time)
                    
                    # Add other filters
                    for key, value in filters.items():
                        if key in ["id", "event_type", "actor", "action", "resource", "status", "severity", "source_ip", "session_id", "correlation_id"]:
                            query += f" AND {key} = ?"
                            params.append(value)
                    
                    # Add order by
                    query += " ORDER BY timestamp DESC"
                    
                    # Add limit and offset
                    if limit is not None:
                        query += " LIMIT ?"
                        params.append(limit)
                    
                    if offset is not None:
                        query += " OFFSET ?"
                        params.append(offset)
                    
                    # Execute query
                    cursor.execute(query, params)
                    
                    # Process results
                    events = []
                    for row in cursor.fetchall():
                        events.append(AuditEvent(
                            id=row[0],
                            event_type=AuditEventType(row[1]),
                            timestamp=row[2],
                            actor=row[3],
                            action=row[4],
                            resource=row[5],
                            status=row[6],
                            severity=AuditEventSeverity(row[7]),
                            details=json.loads(row[8]),
                            source_ip=row[9],
                            session_id=row[10],
                            correlation_id=row[11]
                        ))
                    
                    return events
                finally:
                    conn.close()
        except Exception as e:
            logging.error(f"Error querying audit events: {e}")
            return []
    
    def count_events(self, filters: Dict[str, Any] = None,
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None) -> int:
        """
        Count audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            
        Returns:
            Number of audit events matching the query
        """
        if filters is None:
            filters = {}
        
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                try:
                    cursor = conn.cursor()
                    
                    # Build query
                    query = '''
                    SELECT COUNT(*)
                    FROM audit_events
                    WHERE 1=1
                    '''
                    params = []
                    
                    # Add time filters
                    if start_time is not None:
                        query += " AND timestamp >= ?"
                        params.append(start_time)
                    
                    if end_time is not None:
                        query += " AND timestamp < ?"
                        params.append(end_time)
                    
                    # Add other filters
                    for key, value in filters.items():
                        if key in ["id", "event_type", "actor", "action", "resource", "status", "severity", "source_ip", "session_id", "correlation_id"]:
                            query += f" AND {key} = ?"
                            params.append(value)
                    
                    # Execute query
                    cursor.execute(query, params)
                    
                    # Get count
                    row = cursor.fetchone()
                    return row[0] if row else 0
                finally:
                    conn.close()
        except Exception as e:
            logging.error(f"Error counting audit events: {e}")
            return 0
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an audit event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if the event was deleted successfully, False otherwise
        """
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                try:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    DELETE FROM audit_events
                    WHERE id = ?
                    ''', (event_id,))
                    
                    conn.commit()
                    return cursor.rowcount > 0
                finally:
                    conn.close()
        except Exception as e:
            logging.error(f"Error deleting audit event: {e}")
            return False
    
    def delete_events(self, filters: Dict[str, Any] = None,
                    start_time: Optional[float] = None,
                    end_time: Optional[float] = None) -> int:
        """
        Delete audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            
        Returns:
            Number of audit events deleted
        """
        if filters is None:
            filters = {}
        
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                try:
                    cursor = conn.cursor()
                    
                    # Build query
                    query = '''
                    DELETE FROM audit_events
                    WHERE 1=1
                    '''
                    params = []
                    
                    # Add time filters
                    if start_time is not None:
                        query += " AND timestamp >= ?"
                        params.append(start_time)
                    
                    if end_time is not None:
                        query += " AND timestamp < ?"
                        params.append(end_time)
                    
                    # Add other filters
                    for key, value in filters.items():
                        if key in ["id", "event_type", "actor", "action", "resource", "status", "severity", "source_ip", "session_id", "correlation_id"]:
                            query += f" AND {key} = ?"
                            params.append(value)
                    
                    # Execute query
                    cursor.execute(query, params)
                    
                    # Get count of deleted rows
                    deleted_count = cursor.rowcount
                    
                    conn.commit()
                    return deleted_count
                finally:
                    conn.close()
        except Exception as e:
            logging.error(f"Error deleting audit events: {e}")
            return 0
    
    def close(self):
        """Close the storage backend."""
        pass


class AuditTrailSystem:
    """
    Audit trail system for maintaining comprehensive logs of all agent actions.
    
    This class provides functionality to log and query audit events for accountability
    and compliance purposes.
    """
    
    def __init__(self, storage: AuditEventStorage, async_mode: bool = True,
               max_queue_size: int = 1000):
        """
        Initialize the audit trail system.
        
        Args:
            storage: Storage backend for audit events
            async_mode: Whether to log events asynchronously
            max_queue_size: Maximum size of the event queue in async mode
        """
        self.storage = storage
        self.async_mode = async_mode
        self.max_queue_size = max_queue_size
        self.logger = logging.getLogger(__name__)
        
        # Initialize async processing if needed
        if async_mode:
            self.event_queue = queue.Queue(maxsize=max_queue_size)
            self.worker_thread = threading.Thread(target=self._process_events)
            self.worker_thread.daemon = True
            self.running = True
            self.worker_thread.start()
    
    def log_event(self, event: AuditEvent) -> bool:
        """
        Log an audit event.
        
        Args:
            event: Audit event to log
            
        Returns:
            True if the event was logged successfully, False otherwise
        """
        if self.async_mode:
            try:
                self.event_queue.put(event, block=False)
                return True
            except queue.Full:
                self.logger.error("Audit event queue is full, dropping event")
                return False
        else:
            return self.storage.store_event(event)
    
    def log_agent_action(self, agent_id: str, action: str, resource: str,
                       status: str = "success", severity: AuditEventSeverity = AuditEventSeverity.INFO,
                       details: Dict[str, Any] = None, session_id: Optional[str] = None) -> bool:
        """
        Log an agent action.
        
        Args:
            agent_id: ID of the agent performing the action
            action: Action performed
            resource: Resource affected by the action
            status: Status of the action
            severity: Severity of the event
            details: Additional details about the action
            session_id: Session ID
            
        Returns:
            True if the event was logged successfully, False otherwise
        """
        if details is None:
            details = {}
        
        event = AuditEventBuilder() \
            .with_event_type(AuditEventType.AGENT_ACTION) \
            .with_actor(agent_id) \
            .with_action(action) \
            .with_resource(resource) \
            .with_status(status) \
            .with_severity(severity) \
            .with_details(details) \
            .with_session_id(session_id) \
            .build()
        
        return self.log_event(event)
    
    def log_system_event(self, action: str, resource: str,
                       status: str = "success", severity: AuditEventSeverity = AuditEventSeverity.INFO,
                       details: Dict[str, Any] = None) -> bool:
        """
        Log a system event.
        
        Args:
            action: Action performed
            resource: Resource affected by the action
            status: Status of the action
            severity: Severity of the event
            details: Additional details about the action
            
        Returns:
            True if the event was logged successfully, False otherwise
        """
        if details is None:
            details = {}
        
        event = AuditEventBuilder() \
            .with_event_type(AuditEventType.SYSTEM_EVENT) \
            .with_actor("system") \
            .with_action(action) \
            .with_resource(resource) \
            .with_status(status) \
            .with_severity(severity) \
            .with_details(details) \
            .build()
        
        return self.log_event(event)
    
    def log_security_event(self, actor: str, action: str, resource: str,
                         status: str = "success", severity: AuditEventSeverity = AuditEventSeverity.INFO,
                         details: Dict[str, Any] = None, source_ip: Optional[str] = None,
                         session_id: Optional[str] = None) -> bool:
        """
        Log a security event.
        
        Args:
            actor: Actor performing the action
            action: Action performed
            resource: Resource affected by the action
            status: Status of the action
            severity: Severity of the event
            details: Additional details about the action
            source_ip: Source IP address
            session_id: Session ID
            
        Returns:
            True if the event was logged successfully, False otherwise
        """
        if details is None:
            details = {}
        
        event = AuditEventBuilder() \
            .with_event_type(AuditEventType.SECURITY_EVENT) \
            .with_actor(actor) \
            .with_action(action) \
            .with_resource(resource) \
            .with_status(status) \
            .with_severity(severity) \
            .with_details(details) \
            .with_source_ip(source_ip) \
            .with_session_id(session_id) \
            .build()
        
        return self.log_event(event)
    
    def log_user_action(self, user_id: str, action: str, resource: str,
                      status: str = "success", severity: AuditEventSeverity = AuditEventSeverity.INFO,
                      details: Dict[str, Any] = None, source_ip: Optional[str] = None,
                      session_id: Optional[str] = None) -> bool:
        """
        Log a user action.
        
        Args:
            user_id: ID of the user performing the action
            action: Action performed
            resource: Resource affected by the action
            status: Status of the action
            severity: Severity of the event
            details: Additional details about the action
            source_ip: Source IP address
            session_id: Session ID
            
        Returns:
            True if the event was logged successfully, False otherwise
        """
        if details is None:
            details = {}
        
        event = AuditEventBuilder() \
            .with_event_type(AuditEventType.USER_ACTION) \
            .with_actor(user_id) \
            .with_action(action) \
            .with_resource(resource) \
            .with_status(status) \
            .with_severity(severity) \
            .with_details(details) \
            .with_source_ip(source_ip) \
            .with_session_id(session_id) \
            .build()
        
        return self.log_event(event)
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """
        Get an audit event by ID.
        
        Args:
            event_id: ID of the event to get
            
        Returns:
            Audit event, or None if not found
        """
        return self.storage.get_event(event_id)
    
    def query_events(self, filters: Dict[str, Any] = None, 
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None) -> List[AuditEvent]:
        """
        Query audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of audit events matching the query
        """
        return self.storage.query_events(filters, start_time, end_time, limit, offset)
    
    def count_events(self, filters: Dict[str, Any] = None,
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None) -> int:
        """
        Count audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            
        Returns:
            Number of audit events matching the query
        """
        return self.storage.count_events(filters, start_time, end_time)
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an audit event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if the event was deleted successfully, False otherwise
        """
        return self.storage.delete_event(event_id)
    
    def delete_events(self, filters: Dict[str, Any] = None,
                    start_time: Optional[float] = None,
                    end_time: Optional[float] = None) -> int:
        """
        Delete audit events.
        
        Args:
            filters: Filters to apply to the query
            start_time: Start time for the query (inclusive)
            end_time: End time for the query (exclusive)
            
        Returns:
            Number of audit events deleted
        """
        return self.storage.delete_events(filters, start_time, end_time)
    
    def _process_events(self):
        """Process events from the queue (async mode)."""
        while self.running:
            try:
                # Get event from queue
                event = self.event_queue.get(block=True, timeout=1.0)
                
                # Store event
                success = self.storage.store_event(event)
                if not success:
                    self.logger.error(f"Failed to store audit event: {event.id}")
                
                # Mark task as done
                self.event_queue.task_done()
            except queue.Empty:
                # Queue is empty, continue waiting
                pass
            except Exception as e:
                self.logger.error(f"Error processing audit event: {e}")
    
    def shutdown(self):
        """Shut down the audit trail system."""
        if self.async_mode:
            # Stop worker thread
            self.running = False
            self.worker_thread.join(timeout=5.0)
            
            # Process remaining events
            while not self.event_queue.empty():
                try:
                    event = self.event_queue.get(block=False)
                    self.storage.store_event(event)
                    self.event_queue.task_done()
                except queue.Empty:
                    break
                except Exception as e:
                    self.logger.error(f"Error processing audit event during shutdown: {e}")
        
        # Close storage
        self.storage.close()
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.shutdown()
