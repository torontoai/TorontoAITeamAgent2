"""
Configuration module for Slack integration.

This module manages Slack API credentials and configuration settings.
"""

from typing import Dict, Any, Optional, List
import os
import json
import logging

logger = logging.getLogger(__name__)

class SlackConfig:
    """Configuration class for Slack integration."""
    
    def __init__(
        self,
        bot_token: str,
        app_token: Optional[str] = None,
        signing_secret: Optional[str] = None,
        default_channel: str = "general",
        max_retries: int = 3,
        retry_delay: int = 1,
        timeout: int = 30,
        debug_mode: bool = False,
        channel_mappings: Optional[Dict[str, str]] = None,
        user_mappings: Optional[Dict[str, str]] = None
    ):
        """Initialize Slack configuration.
        
        Args:
            bot_token: Slack bot token (xoxb-...)
            app_token: Slack app-level token (xapp-...)
            signing_secret: Webhook signing secret
            default_channel: Default channel for messages
            max_retries: Maximum number of retries for failed requests
            retry_delay: Initial delay between retries (seconds)
            timeout: Request timeout in seconds
            debug_mode: Enable debug logging
            channel_mappings: Mapping of internal channel names to Slack channel IDs
            user_mappings: Mapping of internal user names to Slack user IDs
        """
        self.bot_token = bot_token
        self.app_token = app_token
        self.signing_secret = signing_secret
        self.default_channel = default_channel
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.debug_mode = debug_mode
        self.channel_mappings = channel_mappings or {}
        self.user_mappings = user_mappings or {}
        
        if debug_mode:
            logger.setLevel(logging.DEBUG)
        
        logger.debug("Slack configuration initialized")
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SlackConfig':
        """Create a SlackConfig instance from a dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            SlackConfig instance
        """
        return cls(
            bot_token=config_dict.get("bot_token"),
            app_token=config_dict.get("app_token"),
            signing_secret=config_dict.get("signing_secret"),
            default_channel=config_dict.get("default_channel", "general"),
            max_retries=config_dict.get("max_retries", 3),
            retry_delay=config_dict.get("retry_delay", 1),
            timeout=config_dict.get("timeout", 30),
            debug_mode=config_dict.get("debug_mode", False),
            channel_mappings=config_dict.get("channel_mappings", {}),
            user_mappings=config_dict.get("user_mappings", {})
        )
    
    @classmethod
    def from_env(cls) -> 'SlackConfig':
        """Create a SlackConfig instance from environment variables.
        
        Returns:
            SlackConfig instance
        """
        return cls(
            bot_token=os.environ.get("SLACK_BOT_TOKEN", ""),
            app_token=os.environ.get("SLACK_APP_TOKEN"),
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
            default_channel=os.environ.get("SLACK_DEFAULT_CHANNEL", "general"),
            max_retries=int(os.environ.get("SLACK_MAX_RETRIES", "3")),
            retry_delay=int(os.environ.get("SLACK_RETRY_DELAY", "1")),
            timeout=int(os.environ.get("SLACK_TIMEOUT", "30")),
            debug_mode=os.environ.get("SLACK_DEBUG_MODE", "").lower() == "true",
            channel_mappings=json.loads(os.environ.get("SLACK_CHANNEL_MAPPINGS", "{}")),
            user_mappings=json.loads(os.environ.get("SLACK_USER_MAPPINGS", "{}"))
        )
    
    @classmethod
    def from_file(cls, file_path: str) -> 'SlackConfig':
        """Create a SlackConfig instance from a JSON file.
        
        Args:
            file_path: Path to the JSON configuration file
            
        Returns:
            SlackConfig instance
        """
        try:
            with open(file_path, "r") as f:
                config_dict = json.load(f)
            return cls.from_dict(config_dict)
        except Exception as e:
            logger.error(f"Error loading Slack configuration from file: {str(e)}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            "bot_token": self.bot_token,
            "app_token": self.app_token,
            "signing_secret": self.signing_secret,
            "default_channel": self.default_channel,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout,
            "debug_mode": self.debug_mode,
            "channel_mappings": self.channel_mappings,
            "user_mappings": self.user_mappings
        }
    
    def to_file(self, file_path: str) -> None:
        """Save the configuration to a JSON file.
        
        Args:
            file_path: Path to the JSON configuration file
        """
        try:
            with open(file_path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving Slack configuration to file: {str(e)}")
            raise
    
    def get_channel_id(self, channel_name: str) -> str:
        """Get the Slack channel ID for a channel name.
        
        Args:
            channel_name: Channel name
            
        Returns:
            Slack channel ID or the original name if not found
        """
        return self.channel_mappings.get(channel_name, channel_name)
    
    def get_user_id(self, user_name: str) -> str:
        """Get the Slack user ID for a user name.
        
        Args:
            user_name: User name
            
        Returns:
            Slack user ID or the original name if not found
        """
        return self.user_mappings.get(user_name, user_name)
    
    def update_channel_mapping(self, channel_name: str, channel_id: str) -> None:
        """Update the mapping of a channel name to a Slack channel ID.
        
        Args:
            channel_name: Channel name
            channel_id: Slack channel ID
        """
        self.channel_mappings[channel_name] = channel_id
    
    def update_user_mapping(self, user_name: str, user_id: str) -> None:
        """Update the mapping of a user name to a Slack user ID.
        
        Args:
            user_name: User name
            user_id: Slack user ID
        """
        self.user_mappings[user_name] = user_id
    
    def validate(self) -> List[str]:
        """Validate the configuration.
        
        Returns:
            List of validation errors, empty if valid
        """
        errors = []
        
        if not self.bot_token:
            errors.append("Bot token is required")
        
        if self.bot_token and not self.bot_token.startswith("xoxb-"):
            errors.append("Bot token must start with 'xoxb-'")
        
        if self.app_token and not self.app_token.startswith("xapp-"):
            errors.append("App token must start with 'xapp-'")
        
        return errors
