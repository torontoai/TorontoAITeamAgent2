"""
MCP/A2A integration for Slack.

This module connects the Slack integration with the MCP/A2A communication frameworks.
"""

from typing import Dict, Any, List, Optional, Union, Callable
import logging
import json
import threading
from .config import SlackConfig
from .client import SlackClient
from .models import SlackMessage, SlackEvent, EventType
from .events import SlackEventHandler
from .sync_manager import SlackSyncManager

logger = logging.getLogger(__name__)

class SlackMCPA2AIntegration:
    """Integration between Slack and MCP/A2A frameworks."""
    
    def __init__(
        self,
        config: SlackConfig,
        client: SlackClient,
        event_handler: SlackEventHandler,
        sync_manager: SlackSyncManager
    ):
        """Initialize the MCP/A2A integration.
        
        Args:
            config: Slack configuration
            client: Slack client
            event_handler: Event handler
            sync_manager: Synchronization manager
        """
        self.config = config
        self.client = client
        self.event_handler = event_handler
        self.sync_manager = sync_manager
        self.message_callbacks = []
        
        # Register event callbacks
        self._register_event_callbacks()
        
        logger.debug("Slack MCP/A2A integration initialized")
    
    def _register_event_callbacks(self) -> None:
        """Register event callbacks."""
        # Register message event callback
        self.event_handler.register_event_callback(
            EventType.MESSAGE,
            self._handle_message_for_mcp_a2a
        )
        
        # Register app mention event callback
        self.event_handler.register_event_callback(
            EventType.APP_MENTION,
            self._handle_app_mention_for_mcp_a2a
        )
    
    def register_message_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for incoming messages.
        
        Args:
            callback: Callback function
        """
        self.message_callbacks.append(callback)
        logger.debug("Registered message callback")
    
    def _handle_message_for_mcp_a2a(self, data: Dict[str, Any]) -> None:
        """Handle a message event for MCP/A2A.
        
        Args:
            data: Event data
        """
        # Skip messages from the bot itself
        if data.get("bot_id"):
            return
        
        # Convert to MCP/A2A message format
        mcp_a2a_message = self._convert_to_mcp_a2a_format(data)
        
        # Call registered callbacks
        for callback in self.message_callbacks:
            try:
                callback(mcp_a2a_message)
            except Exception as e:
                logger.error(f"Error in message callback: {str(e)}")
    
    def _handle_app_mention_for_mcp_a2a(self, data: Dict[str, Any]) -> None:
        """Handle an app mention event for MCP/A2A.
        
        Args:
            data: Event data
        """
        # Convert to MCP/A2A message format with mention flag
        mcp_a2a_message = self._convert_to_mcp_a2a_format(data)
        mcp_a2a_message["is_mention"] = True
        
        # Call registered callbacks
        for callback in self.message_callbacks:
            try:
                callback(mcp_a2a_message)
            except Exception as e:
                logger.error(f"Error in message callback: {str(e)}")
    
    def _convert_to_mcp_a2a_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Slack event data to MCP/A2A format.
        
        Args:
            data: Slack event data
            
        Returns:
            MCP/A2A message
        """
        channel = data.get("channel", "")
        user = data.get("user", "")
        text = data.get("text", "")
        ts = data.get("ts", "")
        thread_ts = data.get("thread_ts")
        
        # Get user info if available
        user_info = None
        try:
            user_info = self.client.get_user_info(user)
        except Exception as e:
            logger.warning(f"Error getting user info: {str(e)}")
        
        # Create MCP/A2A message
        return {
            "source": "slack",
            "channel": channel,
            "user": user,
            "user_name": user_info.name if user_info else None,
            "text": text,
            "timestamp": ts,
            "thread_ts": thread_ts,
            "is_mention": False,
            "raw_data": data
        }
    
    def send_message_from_mcp_a2a(
        self,
        message: Dict[str, Any]
    ) -> str:
        """Send a message from MCP/A2A to Slack.
        
        Args:
            message: MCP/A2A message
            
        Returns:
            Message ID
        """
        # Extract message data
        channel = message.get("channel", self.config.default_channel)
        text = message.get("text", "")
        thread_ts = message.get("thread_ts")
        
        # Create Slack message
        slack_message = SlackMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
        
        # Add attachments if present
        if "attachments" in message:
            from .models import SlackAttachment
            for attachment_data in message["attachments"]:
                attachment = SlackAttachment(
                    fallback=attachment_data.get("fallback", "Attachment"),
                    text=attachment_data.get("text"),
                    title=attachment_data.get("title"),
                    color=attachment_data.get("color"),
                    fields=attachment_data.get("fields", [])
                )
                slack_message.attachments.append(attachment)
        
        # Add blocks if present
        if "blocks" in message:
            # Simplified block handling
            pass
        
        # Queue message for sending
        return self.sync_manager.queue_message(slack_message)
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get the status of a message.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message status
        """
        return self.sync_manager.get_message_status(message_id)
    
    def register_with_mcp(self, mcp_manager: Any) -> None:
        """Register with the MCP manager.
        
        Args:
            mcp_manager: MCP manager
        """
        # This is a placeholder implementation
        # In a real implementation, this would register the Slack integration
        # with the MCP manager
        logger.info("Registering Slack integration with MCP manager")
        
        # Register message callback
        self.register_message_callback(mcp_manager.handle_external_message)
        
        # Register as a message provider
        mcp_manager.register_message_provider("slack", self.send_message_from_mcp_a2a)
    
    def register_with_a2a(self, a2a_manager: Any) -> None:
        """Register with the A2A manager.
        
        Args:
            a2a_manager: A2A manager
        """
        # This is a placeholder implementation
        # In a real implementation, this would register the Slack integration
        # with the A2A manager
        logger.info("Registering Slack integration with A2A manager")
        
        # Register message callback
        self.register_message_callback(a2a_manager.handle_external_message)
        
        # Register as a message provider
        a2a_manager.register_message_provider("slack", self.send_message_from_mcp_a2a)
