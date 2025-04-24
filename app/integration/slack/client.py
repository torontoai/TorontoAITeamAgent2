"""
API client for Slack integration.

This module provides a wrapper around the Slack API.
"""

from typing import Dict, Any, List, Optional, Union
import logging
import requests
import time
import json
from .config import SlackConfig
from .auth import SlackAuth
from .models import (
    SlackMessage, SlackAttachment, SlackBlock, SlackUser, 
    SlackChannel, MessageType
)

logger = logging.getLogger(__name__)

class SlackApiError(Exception):
    """Exception raised for Slack API errors."""
    
    def __init__(self, message: str, response: Optional[Dict[str, Any]] = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            response: API response
        """
        self.message = message
        self.response = response
        super().__init__(self.message)

class SlackClient:
    """Client for interacting with the Slack API."""
    
    BASE_URL = "https://slack.com/api"
    
    def __init__(self, config: SlackConfig):
        """Initialize the Slack client.
        
        Args:
            config: Slack configuration
        """
        self.config = config
        self.auth = SlackAuth(config)
        
        # Validate token on initialization
        if not self.auth.validate_token():
            logger.warning("Slack token validation failed")
        
        logger.debug("Slack client initialized")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Make a request to the Slack API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request data
            files: Files to upload
            retry_count: Current retry count
            
        Returns:
            API response
            
        Raises:
            SlackApiError: If the API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self.auth.get_headers()
        
        try:
            if method.upper() == "GET":
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.config.timeout
                )
            elif method.upper() == "POST":
                if files:
                    # For file uploads, don't use JSON
                    headers.pop("Content-Type", None)
                    response = requests.post(
                        url,
                        headers=headers,
                        data=data,
                        files=files,
                        timeout=self.config.timeout
                    )
                else:
                    response = requests.post(
                        url,
                        headers=headers,
                        json=data,
                        timeout=self.config.timeout
                    )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_data = response.json()
            
            # Check for rate limiting
            if not response_data.get("ok") and response_data.get("error") == "ratelimited":
                retry_after = int(response.headers.get("Retry-After", self.config.retry_delay))
                
                if retry_count < self.config.max_retries:
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds")
                    time.sleep(retry_after)
                    return self._make_request(
                        method, endpoint, params, data, files, retry_count + 1
                    )
                else:
                    raise SlackApiError(
                        f"Rate limit exceeded after {retry_count} retries",
                        response_data
                    )
            
            # Check for other errors
            if not response_data.get("ok"):
                raise SlackApiError(
                    f"Slack API error: {response_data.get('error')}",
                    response_data
                )
            
            return response_data
        
        except requests.RequestException as e:
            if retry_count < self.config.max_retries:
                logger.warning(f"Request failed: {str(e)}. Retrying...")
                time.sleep(self.config.retry_delay * (2 ** retry_count))  # Exponential backoff
                return self._make_request(
                    method, endpoint, params, data, files, retry_count + 1
                )
            else:
                raise SlackApiError(f"Request failed after {retry_count} retries: {str(e)}")
    
    # Channel methods
    
    def get_channels(self, include_private: bool = False) -> List[SlackChannel]:
        """Get a list of channels.
        
        Args:
            include_private: Whether to include private channels
            
        Returns:
            List of channels
        """
        channels = []
        
        # Get public channels
        response = self._make_request(
            "GET",
            "conversations.list",
            params={
                "exclude_archived": "true",
                "types": "public_channel"
            }
        )
        
        for channel_data in response.get("channels", []):
            channels.append(SlackChannel.from_api_response(channel_data))
        
        # Get private channels if requested
        if include_private:
            response = self._make_request(
                "GET",
                "conversations.list",
                params={
                    "exclude_archived": "true",
                    "types": "private_channel"
                }
            )
            
            for channel_data in response.get("channels", []):
                channels.append(SlackChannel.from_api_response(channel_data))
        
        return channels
    
    def get_channel_by_name(self, name: str) -> Optional[SlackChannel]:
        """Get a channel by name.
        
        Args:
            name: Channel name
            
        Returns:
            Channel or None if not found
        """
        channels = self.get_channels(include_private=True)
        
        for channel in channels:
            if channel.name == name:
                return channel
        
        return None
    
    def create_channel(self, name: str, is_private: bool = False) -> SlackChannel:
        """Create a new channel.
        
        Args:
            name: Channel name
            is_private: Whether the channel is private
            
        Returns:
            Created channel
        """
        response = self._make_request(
            "POST",
            "conversations.create",
            data={
                "name": name,
                "is_private": is_private
            }
        )
        
        return SlackChannel.from_api_response(response.get("channel", {}))
    
    def archive_channel(self, channel_id: str) -> bool:
        """Archive a channel.
        
        Args:
            channel_id: Channel ID
            
        Returns:
            True if successful
        """
        response = self._make_request(
            "POST",
            "conversations.archive",
            data={
                "channel": channel_id
            }
        )
        
        return response.get("ok", False)
    
    def unarchive_channel(self, channel_id: str) -> bool:
        """Unarchive a channel.
        
        Args:
            channel_id: Channel ID
            
        Returns:
            True if successful
        """
        response = self._make_request(
            "POST",
            "conversations.unarchive",
            data={
                "channel": channel_id
            }
        )
        
        return response.get("ok", False)
    
    # User methods
    
    def get_users(self) -> List[SlackUser]:
        """Get a list of users.
        
        Returns:
            List of users
        """
        users = []
        
        response = self._make_request(
            "GET",
            "users.list"
        )
        
        for user_data in response.get("members", []):
            users.append(SlackUser.from_api_response(user_data))
        
        return users
    
    def get_user_by_name(self, username: str) -> Optional[SlackUser]:
        """Get a user by username.
        
        Args:
            username: Username
            
        Returns:
            User or None if not found
        """
        users = self.get_users()
        
        for user in users:
            if user.name == username:
                return user
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[SlackUser]:
        """Get a user by email.
        
        Args:
            email: Email address
            
        Returns:
            User or None if not found
        """
        users = self.get_users()
        
        for user in users:
            if user.email == email:
                return user
        
        return None
    
    def get_user_info(self, user_id: str) -> SlackUser:
        """Get information about a user.
        
        Args:
            user_id: User ID
            
        Returns:
            User information
        """
        response = self._make_request(
            "GET",
            "users.info",
            params={
                "user": user_id
            }
        )
        
        return SlackUser.from_api_response(response.get("user", {}))
    
    # Message methods
    
    def send_message(self, message: SlackMessage) -> Dict[str, Any]:
        """Send a message.
        
        Args:
            message: Message to send
            
        Returns:
            API response
        """
        return self._make_request(
            "POST",
            "chat.postMessage",
            data=message.to_dict()
        )
    
    def update_message(self, message: SlackMessage) -> Dict[str, Any]:
        """Update a message.
        
        Args:
            message: Message to update
            
        Returns:
            API response
        """
        if not message.ts:
            raise ValueError("Message timestamp (ts) is required for updates")
        
        data = message.to_dict()
        data["ts"] = message.ts
        
        return self._make_request(
            "POST",
            "chat.update",
            data=data
        )
    
    def delete_message(self, channel_id: str, ts: str) -> bool:
        """Delete a message.
        
        Args:
            channel_id: Channel ID
            ts: Message timestamp
            
        Returns:
            True if successful
        """
        response = self._make_request(
            "POST",
            "chat.delete",
            data={
                "channel": channel_id,
                "ts": ts
            }
        )
        
        return response.get("ok", False)
    
    def get_message_permalink(self, channel_id: str, message_ts: str) -> str:
        """Get a permalink to a message.
        
        Args:
            channel_id: Channel ID
            message_ts: Message timestamp
            
        Returns:
            Message permalink
        """
        response = self._make_request(
            "GET",
            "chat.getPermalink",
            params={
                "channel": channel_id,
                "message_ts": message_ts
            }
        )
        
        return response.get("permalink", "")
    
    # File methods
    
    def upload_file(
        self,
        channels: Union[str, List[str]],
        file_path: Optional[str] = None,
        content: Optional[str] = None,
        filename: Optional[str] = None,
        filetype: Optional[str] = None,
        title: Optional[str] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a file.
        
        Args:
            channels: Channel(s) to share the file with
            file_path: Path to the file to upload
            content: File content (alternative to file_path)
            filename: Filename
            filetype: File type
            title: File title
            thread_ts: Thread timestamp for sharing in a thread
            
        Returns:
            API response
        """
        if not file_path and not content:
            raise ValueError("Either file_path or content must be provided")
        
        if isinstance(channels, list):
            channels = ",".join(channels)
        
        data = {
            "channels": channels
        }
        
        if title:
            data["title"] = title
        
        if thread_ts:
            data["thread_ts"] = thread_ts
        
        files = {}
        
        if file_path:
            files["file"] = open(file_path, "rb")
            if not filename:
                import os
                filename = os.path.basename(file_path)
        else:
            files["file"] = (filename or "file", content)
        
        if filename:
            data["filename"] = filename
        
        if filetype:
            data["filetype"] = filetype
        
        try:
            return self._make_request(
                "POST",
                "files.upload",
                data=data,
                files=files
            )
        finally:
            # Close file if opened
            if file_path and "file" in files and hasattr(files["file"], "close"):
                files["file"].close()
    
    # Reaction methods
    
    def add_reaction(self, channel_id: str, timestamp: str, reaction: str) -> bool:
        """Add a reaction to a message.
        
        Args:
            channel_id: Channel ID
            timestamp: Message timestamp
            reaction: Reaction name (without colons)
            
        Returns:
            True if successful
        """
        response = self._make_request(
            "POST",
            "reactions.add",
            data={
                "channel": channel_id,
                "timestamp": timestamp,
                "name": reaction
            }
        )
        
        return response.get("ok", False)
    
    def remove_reaction(self, channel_id: str, timestamp: str, reaction: str) -> bool:
        """Remove a reaction from a message.
        
        Args:
            channel_id: Channel ID
            timestamp: Message timestamp
            reaction: Reaction name (without colons)
            
        Returns:
            True if successful
        """
        response = self._make_request(
            "POST",
            "reactions.remove",
            data={
                "channel": channel_id,
                "timestamp": timestamp,
                "name": reaction
            }
        )
        
        return response.get("ok", False)
    
    # Convenience methods
    
    def send_text_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a simple text message.
        
        Args:
            channel: Channel ID or name
            text: Message text
            thread_ts: Thread timestamp for replying in a thread
            
        Returns:
            API response
        """
        # Resolve channel name to ID if needed
        if not channel.startswith("C") and not channel.startswith("D"):
            channel_obj = self.get_channel_by_name(channel)
            if channel_obj:
                channel = channel_obj.id
        
        message = SlackMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
        
        return self.send_message(message)
    
    def send_attachment_message(
        self,
        channel: str,
        text: str,
        attachments: List[SlackAttachment],
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message with attachments.
        
        Args:
            channel: Channel ID or name
            text: Message text
            attachments: Message attachments
            thread_ts: Thread timestamp for replying in a thread
            
        Returns:
            API response
        """
        # Resolve channel name to ID if needed
        if not channel.startswith("C") and not channel.startswith("D"):
            channel_obj = self.get_channel_by_name(channel)
            if channel_obj:
                channel = channel_obj.id
        
        message = SlackMessage(
            channel=channel,
            text=text,
            message_type=MessageType.ATTACHMENT,
            thread_ts=thread_ts,
            attachments=attachments
        )
        
        return self.send_message(message)
    
    def send_block_message(
        self,
        channel: str,
        text: str,
        blocks: List[SlackBlock],
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message with blocks.
        
        Args:
            channel: Channel ID or name
            text: Message text
            blocks: Message blocks
            thread_ts: Thread timestamp for replying in a thread
            
        Returns:
            API response
        """
        # Resolve channel name to ID if needed
        if not channel.startswith("C") and not channel.startswith("D"):
            channel_obj = self.get_channel_by_name(channel)
            if channel_obj:
                channel = channel_obj.id
        
        message = SlackMessage(
            channel=channel,
            text=text,
            message_type=MessageType.BLOCK,
            thread_ts=thread_ts,
            blocks=blocks
        )
        
        return self.send_message(message)
