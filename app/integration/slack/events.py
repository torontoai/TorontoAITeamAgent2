"""
Event handlers for Slack integration.

This module processes incoming events from Slack.
"""

from typing import Dict, Any, List, Optional, Callable, Union
import logging
import json
from .config import SlackConfig
from .auth import SlackAuth
from .client import SlackClient
from .models import SlackEvent, EventType, SlackMessage

logger = logging.getLogger(__name__)

class SlackEventHandler:
    """Handler for Slack events."""
    
    def __init__(self, config: SlackConfig, client: SlackClient):
        """Initialize the event handler.
        
        Args:
            config: Slack configuration
            client: Slack client
        """
        self.config = config
        self.client = client
        self.auth = SlackAuth(config)
        self.event_callbacks = {}
        
        # Register default handlers
        self._register_default_handlers()
        
        logger.debug("Slack event handler initialized")
    
    def _register_default_handlers(self) -> None:
        """Register default event handlers."""
        # Register handlers for common event types
        self.register_event_callback(EventType.MESSAGE, self._handle_message_event)
        self.register_event_callback(EventType.REACTION, self._handle_reaction_event)
        self.register_event_callback(EventType.USER_CHANGE, self._handle_user_change_event)
        self.register_event_callback(EventType.CHANNEL_CREATED, self._handle_channel_created_event)
        self.register_event_callback(EventType.CHANNEL_ARCHIVED, self._handle_channel_archived_event)
        self.register_event_callback(EventType.CHANNEL_UNARCHIVED, self._handle_channel_unarchived_event)
        self.register_event_callback(EventType.APP_MENTION, self._handle_app_mention_event)
    
    def register_event_callback(
        self, 
        event_type: EventType, 
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Register a callback for an event type.
        
        Args:
            event_type: Event type
            callback: Callback function
        """
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        
        self.event_callbacks[event_type].append(callback)
        logger.debug(f"Registered callback for event type: {event_type.value}")
    
    def handle_event(self, event: SlackEvent) -> None:
        """Handle a Slack event.
        
        Args:
            event: Slack event
        """
        logger.debug(f"Handling event: {event.type.value}")
        
        # Call registered callbacks for the event type
        if event.type in self.event_callbacks:
            for callback in self.event_callbacks[event.type]:
                try:
                    callback(event.data)
                except Exception as e:
                    logger.error(f"Error in event callback: {str(e)}")
    
    def process_webhook_payload(self, payload: Dict[str, Any]) -> None:
        """Process a webhook payload.
        
        Args:
            payload: Webhook payload
        """
        # Check if this is a URL verification challenge
        if payload.get("type") == "url_verification":
            return {
                "challenge": payload.get("challenge")
            }
        
        # Process event
        if payload.get("type") == "event_callback":
            event = SlackEvent.from_webhook_payload(payload)
            self.handle_event(event)
            return {"ok": True}
        
        return {"ok": False, "error": "Unsupported payload type"}
    
    # Default event handlers
    
    def _handle_message_event(self, data: Dict[str, Any]) -> None:
        """Handle a message event.
        
        Args:
            data: Event data
        """
        # Skip messages from the bot itself
        if data.get("bot_id"):
            return
        
        # Process the message
        channel = data.get("channel")
        user = data.get("user")
        text = data.get("text", "")
        ts = data.get("ts")
        thread_ts = data.get("thread_ts")
        
        logger.debug(f"Received message from {user} in {channel}: {text}")
        
        # Here you would typically process the message and potentially respond
        # This is a placeholder implementation
        if "hello" in text.lower():
            self.client.send_text_message(
                channel=channel,
                text=f"Hello <@{user}>!",
                thread_ts=thread_ts or ts
            )
    
    def _handle_reaction_event(self, data: Dict[str, Any]) -> None:
        """Handle a reaction event.
        
        Args:
            data: Event data
        """
        user = data.get("user")
        reaction = data.get("reaction")
        item = data.get("item", {})
        channel = item.get("channel")
        ts = item.get("ts")
        
        logger.debug(f"Received reaction {reaction} from {user} in {channel}")
        
        # Here you would typically process the reaction
        # This is a placeholder implementation
    
    def _handle_user_change_event(self, data: Dict[str, Any]) -> None:
        """Handle a user change event.
        
        Args:
            data: Event data
        """
        user = data.get("user", {})
        user_id = user.get("id")
        
        logger.debug(f"User changed: {user_id}")
        
        # Here you would typically update user information
        # This is a placeholder implementation
    
    def _handle_channel_created_event(self, data: Dict[str, Any]) -> None:
        """Handle a channel created event.
        
        Args:
            data: Event data
        """
        channel = data.get("channel", {})
        channel_id = channel.get("id")
        channel_name = channel.get("name")
        
        logger.debug(f"Channel created: {channel_name} ({channel_id})")
        
        # Here you would typically update channel information
        # This is a placeholder implementation
    
    def _handle_channel_archived_event(self, data: Dict[str, Any]) -> None:
        """Handle a channel archived event.
        
        Args:
            data: Event data
        """
        channel = data.get("channel")
        
        logger.debug(f"Channel archived: {channel}")
        
        # Here you would typically update channel information
        # This is a placeholder implementation
    
    def _handle_channel_unarchived_event(self, data: Dict[str, Any]) -> None:
        """Handle a channel unarchived event.
        
        Args:
            data: Event data
        """
        channel = data.get("channel")
        
        logger.debug(f"Channel unarchived: {channel}")
        
        # Here you would typically update channel information
        # This is a placeholder implementation
    
    def _handle_app_mention_event(self, data: Dict[str, Any]) -> None:
        """Handle an app mention event.
        
        Args:
            data: Event data
        """
        channel = data.get("channel")
        user = data.get("user")
        text = data.get("text", "")
        ts = data.get("ts")
        
        logger.debug(f"App mentioned by {user} in {channel}: {text}")
        
        # Here you would typically process the mention and respond
        # This is a placeholder implementation
        self.client.send_text_message(
            channel=channel,
            text=f"Hi <@{user}>, you mentioned me!",
            thread_ts=ts
        )
