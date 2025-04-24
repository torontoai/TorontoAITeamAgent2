"""
Initialization module for Slack integration.

This module provides the main entry point for the Slack integration.
"""

from typing import Dict, Any, Optional
import logging
import os
from .config import SlackConfig
from .client import SlackClient
from .events import SlackEventHandler
from .webhooks import SlackWebhookHandler
from .sync_manager import SlackSyncManager
from .mcp_a2a_integration import SlackMCPA2AIntegration

logger = logging.getLogger(__name__)

class SlackIntegration:
    """Main class for Slack integration."""
    
    def __init__(
        self,
        config: Optional[SlackConfig] = None,
        config_file: Optional[str] = None,
        use_env: bool = False
    ):
        """Initialize the Slack integration.
        
        Args:
            config: Slack configuration
            config_file: Path to configuration file
            use_env: Whether to use environment variables for configuration
        """
        # Load configuration
        if config:
            self.config = config
        elif config_file:
            self.config = SlackConfig.from_file(config_file)
        elif use_env:
            self.config = SlackConfig.from_env()
        else:
            raise ValueError("Either config, config_file, or use_env must be provided")
        
        # Validate configuration
        errors = self.config.validate()
        if errors:
            error_msg = "Invalid Slack configuration: " + ", ".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Create components
        self.client = SlackClient(self.config)
        self.event_handler = SlackEventHandler(self.config, self.client)
        self.sync_manager = SlackSyncManager(self.config, self.client)
        self.webhook_handler = SlackWebhookHandler(self.config, self.event_handler)
        self.mcp_a2a_integration = SlackMCPA2AIntegration(
            self.config, self.client, self.event_handler, self.sync_manager
        )
        
        logger.info("Slack integration initialized")
    
    def start(self) -> None:
        """Start the Slack integration."""
        # Start synchronization manager
        self.sync_manager.start()
        
        # Start webhook handler
        self.webhook_handler.start()
        
        logger.info("Slack integration started")
    
    def stop(self) -> None:
        """Stop the Slack integration."""
        # Stop webhook handler
        self.webhook_handler.stop()
        
        # Stop synchronization manager
        self.sync_manager.stop()
        
        logger.info("Slack integration stopped")
    
    def register_with_mcp(self, mcp_manager: Any) -> None:
        """Register with the MCP manager.
        
        Args:
            mcp_manager: MCP manager
        """
        self.mcp_a2a_integration.register_with_mcp(mcp_manager)
    
    def register_with_a2a(self, a2a_manager: Any) -> None:
        """Register with the A2A manager.
        
        Args:
            a2a_manager: A2A manager
        """
        self.mcp_a2a_integration.register_with_a2a(a2a_manager)
    
    def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None,
        attachments: Optional[list] = None,
        blocks: Optional[list] = None
    ) -> str:
        """Send a message to Slack.
        
        Args:
            channel: Channel name or ID
            text: Message text
            thread_ts: Thread timestamp
            attachments: Message attachments
            blocks: Message blocks
            
        Returns:
            Message ID
        """
        from .models import SlackMessage, MessageType, SlackAttachment
        
        # Create message
        message = SlackMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
        
        # Add attachments if provided
        if attachments:
            message.message_type = MessageType.ATTACHMENT
            for attachment_data in attachments:
                attachment = SlackAttachment(
                    fallback=attachment_data.get("fallback", "Attachment"),
                    text=attachment_data.get("text"),
                    title=attachment_data.get("title"),
                    color=attachment_data.get("color"),
                    fields=attachment_data.get("fields", [])
                )
                message.attachments.append(attachment)
        
        # Add blocks if provided
        if blocks:
            message.message_type = MessageType.BLOCK
            message.blocks = blocks
        
        # Queue message for sending
        return self.sync_manager.queue_message(message)
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get the status of a message.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message status
        """
        return self.sync_manager.get_message_status(message_id)
