"""
Synchronization manager for Slack integration.

This module manages synchronization between the AI system and Slack.
"""

from typing import Dict, Any, List, Optional, Union, Callable
import logging
import time
import json
import threading
import queue
import sqlite3
import os
from .config import SlackConfig
from .client import SlackClient, SlackApiError
from .models import SlackMessage

logger = logging.getLogger(__name__)

class MessageStatus:
    """Message status constants."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"

class SlackSyncManager:
    """Manager for synchronizing messages with Slack."""
    
    def __init__(
        self,
        config: SlackConfig,
        client: SlackClient,
        db_path: Optional[str] = None,
        max_queue_size: int = 100,
        worker_count: int = 1
    ):
        """Initialize the synchronization manager.
        
        Args:
            config: Slack configuration
            client: Slack client
            db_path: Path to the SQLite database
            max_queue_size: Maximum size of the message queue
            worker_count: Number of worker threads
        """
        self.config = config
        self.client = client
        self.db_path = db_path or os.path.join(os.path.expanduser("~"), ".toronto-ai-team-agent", "slack_sync.db")
        self.max_queue_size = max_queue_size
        self.worker_count = worker_count
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        # Initialize message queue
        self.message_queue = queue.Queue(maxsize=max_queue_size)
        
        # Initialize workers
        self.workers = []
        self.running = False
        
        logger.debug("Slack synchronization manager initialized")
    
    def _init_db(self) -> None:
        """Initialize the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create messages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                channel TEXT NOT NULL,
                text TEXT NOT NULL,
                thread_ts TEXT,
                message_type TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                retry_count INTEGER DEFAULT 0,
                slack_ts TEXT,
                error TEXT,
                data TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.debug("Database initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def start(self) -> None:
        """Start the synchronization manager."""
        if self.running:
            logger.warning("Synchronization manager is already running")
            return
        
        self.running = True
        
        # Start worker threads
        for i in range(self.worker_count):
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        
        # Load pending messages from database
        self._load_pending_messages()
        
        logger.info(f"Synchronization manager started with {self.worker_count} workers")
    
    def stop(self) -> None:
        """Stop the synchronization manager."""
        if not self.running:
            logger.warning("Synchronization manager is not running")
            return
        
        self.running = False
        
        # Wait for workers to finish
        for worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=5.0)
        
        self.workers = []
        
        logger.info("Synchronization manager stopped")
    
    def queue_message(self, message: SlackMessage) -> str:
        """Queue a message for sending.
        
        Args:
            message: Message to send
            
        Returns:
            Message ID
        """
        import uuid
        
        # Generate message ID
        message_id = str(uuid.uuid4())
        
        # Store message in database
        self._store_message(message_id, message, MessageStatus.PENDING)
        
        # Add to queue
        try:
            self.message_queue.put(message_id, block=False)
            logger.debug(f"Message {message_id} queued for sending")
        except queue.Full:
            logger.warning("Message queue is full, message will be processed later")
        
        return message_id
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get the status of a message.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT status, slack_ts, error, retry_count, updated_at FROM messages WHERE id = ?",
                (message_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": message_id,
                    "status": row[0],
                    "slack_ts": row[1],
                    "error": row[2],
                    "retry_count": row[3],
                    "updated_at": row[4]
                }
            else:
                return {
                    "id": message_id,
                    "status": "unknown",
                    "error": "Message not found"
                }
        except Exception as e:
            logger.error(f"Error getting message status: {str(e)}")
            return {
                "id": message_id,
                "status": "error",
                "error": str(e)
            }
    
    def _store_message(
        self,
        message_id: str,
        message: SlackMessage,
        status: str,
        slack_ts: Optional[str] = None,
        error: Optional[str] = None,
        retry_count: int = 0
    ) -> None:
        """Store a message in the database.
        
        Args:
            message_id: Message ID
            message: Message to store
            status: Message status
            slack_ts: Slack timestamp
            error: Error message
            retry_count: Retry count
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = int(time.time())
            
            # Convert message to JSON
            message_data = json.dumps(message.to_dict())
            
            cursor.execute(
                '''
                INSERT OR REPLACE INTO messages
                (id, channel, text, thread_ts, message_type, status, created_at, updated_at, 
                retry_count, slack_ts, error, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    message_id,
                    message.channel,
                    message.text,
                    message.thread_ts,
                    message.message_type.value,
                    status,
                    now,
                    now,
                    retry_count,
                    slack_ts,
                    error,
                    message_data
                )
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error storing message: {str(e)}")
    
    def _update_message_status(
        self,
        message_id: str,
        status: str,
        slack_ts: Optional[str] = None,
        error: Optional[str] = None,
        retry_count: Optional[int] = None
    ) -> None:
        """Update the status of a message.
        
        Args:
            message_id: Message ID
            status: New status
            slack_ts: Slack timestamp
            error: Error message
            retry_count: Retry count
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = int(time.time())
            
            # Build update query
            query = "UPDATE messages SET status = ?, updated_at = ?"
            params = [status, now]
            
            if slack_ts is not None:
                query += ", slack_ts = ?"
                params.append(slack_ts)
            
            if error is not None:
                query += ", error = ?"
                params.append(error)
            
            if retry_count is not None:
                query += ", retry_count = ?"
                params.append(retry_count)
            
            query += " WHERE id = ?"
            params.append(message_id)
            
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating message status: {str(e)}")
    
    def _load_pending_messages(self) -> None:
        """Load pending messages from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get pending and retrying messages
            cursor.execute(
                "SELECT id FROM messages WHERE status IN (?, ?) ORDER BY created_at ASC",
                (MessageStatus.PENDING, MessageStatus.RETRYING)
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            # Add to queue
            for row in rows:
                message_id = row[0]
                try:
                    self.message_queue.put(message_id, block=False)
                    logger.debug(f"Loaded pending message {message_id} from database")
                except queue.Full:
                    logger.warning("Message queue is full, some pending messages will be processed later")
                    break
        except Exception as e:
            logger.error(f"Error loading pending messages: {str(e)}")
    
    def _get_message_from_db(self, message_id: str) -> Optional[SlackMessage]:
        """Get a message from the database.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT data, retry_count FROM messages WHERE id = ?",
                (message_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                message_data = json.loads(row[0])
                retry_count = row[1]
                
                # Create message object
                message = SlackMessage(
                    channel=message_data.get("channel", ""),
                    text=message_data.get("text", "")
                )
                
                # Add thread_ts if present
                if "thread_ts" in message_data:
                    message.thread_ts = message_data["thread_ts"]
                
                # Add attachments if present
                if "attachments" in message_data:
                    from .models import SlackAttachment
                    message.attachments = [
                        SlackAttachment(fallback=a.get("fallback", ""))
                        for a in message_data["attachments"]
                    ]
                
                # Add blocks if present
                if "blocks" in message_data:
                    # Simplified block handling
                    pass
                
                return message, retry_count
            else:
                return None, 0
        except Exception as e:
            logger.error(f"Error getting message from database: {str(e)}")
            return None, 0
    
    def _worker_loop(self, worker_id: int) -> None:
        """Worker loop for processing messages.
        
        Args:
            worker_id: Worker ID
        """
        logger.debug(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get message from queue
                try:
                    message_id = self.message_queue.get(block=True, timeout=1.0)
                except queue.Empty:
                    continue
                
                # Get message from database
                message_result = self._get_message_from_db(message_id)
                if not message_result:
                    logger.warning(f"Message {message_id} not found in database")
                    self.message_queue.task_done()
                    continue
                
                message, retry_count = message_result
                
                # Send message
                try:
                    logger.debug(f"Worker {worker_id} sending message {message_id}")
                    
                    # Update status to retrying
                    self._update_message_status(
                        message_id,
                        MessageStatus.RETRYING,
                        retry_count=retry_count
                    )
                    
                    # Send message
                    response = self.client.send_message(message)
                    
                    # Update status to sent
                    self._update_message_status(
                        message_id,
                        MessageStatus.SENT,
                        slack_ts=response.get("ts")
                    )
                    
                    logger.debug(f"Message {message_id} sent successfully")
                except SlackApiError as e:
                    # Check if we should retry
                    if retry_count < self.config.max_retries:
                        # Update status and increment retry count
                        self._update_message_status(
                            message_id,
                            MessageStatus.RETRYING,
                            error=str(e),
                            retry_count=retry_count + 1
                        )
                        
                        # Re-queue message with delay
                        delay = self.config.retry_delay * (2 ** retry_count)
                        logger.debug(f"Message {message_id} failed, retrying in {delay} seconds")
                        
                        def requeue():
                            try:
                                self.message_queue.put(message_id, block=False)
                            except queue.Full:
                                logger.warning(f"Queue full, message {message_id} will be retried later")
                        
                        threading.Timer(delay, requeue).start()
                    else:
                        # Update status to failed
                        self._update_message_status(
                            message_id,
                            MessageStatus.FAILED,
                            error=str(e)
                        )
                        
                        logger.error(f"Message {message_id} failed after {retry_count} retries: {str(e)}")
                except Exception as e:
                    # Update status to failed
                    self._update_message_status(
                        message_id,
                        MessageStatus.FAILED,
                        error=str(e)
                    )
                    
                    logger.error(f"Unexpected error sending message {message_id}: {str(e)}")
                
                # Mark task as done
                self.message_queue.task_done()
            except Exception as e:
                logger.error(f"Error in worker {worker_id}: {str(e)}")
        
        logger.debug(f"Worker {worker_id} stopped")
