"""
Data models for Slack integration.

This module defines the data structures for Slack entities.
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
import datetime
import json

class MessageType(Enum):
    """Enumeration of message types."""
    TEXT = "text"
    ATTACHMENT = "attachment"
    BLOCK = "block"
    INTERACTIVE = "interactive"
    FILE = "file"
    THREAD = "thread"

class EventType(Enum):
    """Enumeration of event types."""
    MESSAGE = "message"
    REACTION = "reaction_added"
    USER_CHANGE = "user_change"
    CHANNEL_CREATED = "channel_created"
    CHANNEL_ARCHIVED = "channel_archived"
    CHANNEL_UNARCHIVED = "channel_unarchived"
    APP_MENTION = "app_mention"
    INTERACTIVE = "interactive"
    COMMAND = "command"

@dataclass
class SlackUser:
    """Slack user model."""
    id: str
    name: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    is_bot: bool = False
    team_id: Optional[str] = None
    profile_image: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SlackUser':
        """Create a SlackUser instance from an API response.
        
        Args:
            data: API response data
            
        Returns:
            SlackUser instance
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            real_name=data.get("real_name"),
            email=data.get("profile", {}).get("email"),
            is_bot=data.get("is_bot", False),
            team_id=data.get("team_id"),
            profile_image=data.get("profile", {}).get("image_72")
        )

@dataclass
class SlackChannel:
    """Slack channel model."""
    id: str
    name: str
    is_private: bool = False
    is_archived: bool = False
    topic: str = ""
    purpose: str = ""
    member_count: int = 0
    created: Optional[datetime.datetime] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SlackChannel':
        """Create a SlackChannel instance from an API response.
        
        Args:
            data: API response data
            
        Returns:
            SlackChannel instance
        """
        created = None
        if "created" in data:
            try:
                created = datetime.datetime.fromtimestamp(float(data["created"]))
            except (ValueError, TypeError):
                pass
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            is_private=data.get("is_private", False),
            is_archived=data.get("is_archived", False),
            topic=data.get("topic", {}).get("value", ""),
            purpose=data.get("purpose", {}).get("value", ""),
            member_count=data.get("num_members", 0),
            created=created
        )

@dataclass
class SlackAttachment:
    """Slack attachment model."""
    fallback: str
    color: Optional[str] = None
    pretext: Optional[str] = None
    author_name: Optional[str] = None
    author_link: Optional[str] = None
    author_icon: Optional[str] = None
    title: Optional[str] = None
    title_link: Optional[str] = None
    text: Optional[str] = None
    fields: List[Dict[str, str]] = field(default_factory=list)
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    footer: Optional[str] = None
    footer_icon: Optional[str] = None
    ts: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the attachment to a dictionary.
        
        Returns:
            Attachment dictionary
        """
        result = {
            "fallback": self.fallback
        }
        
        if self.color:
            result["color"] = self.color
        
        if self.pretext:
            result["pretext"] = self.pretext
        
        if self.author_name:
            result["author_name"] = self.author_name
        
        if self.author_link:
            result["author_link"] = self.author_link
        
        if self.author_icon:
            result["author_icon"] = self.author_icon
        
        if self.title:
            result["title"] = self.title
        
        if self.title_link:
            result["title_link"] = self.title_link
        
        if self.text:
            result["text"] = self.text
        
        if self.fields:
            result["fields"] = self.fields
        
        if self.image_url:
            result["image_url"] = self.image_url
        
        if self.thumb_url:
            result["thumb_url"] = self.thumb_url
        
        if self.footer:
            result["footer"] = self.footer
        
        if self.footer_icon:
            result["footer_icon"] = self.footer_icon
        
        if self.ts:
            result["ts"] = self.ts
        
        return result

@dataclass
class SlackBlock:
    """Base class for Slack block kit blocks."""
    type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the block to a dictionary.
        
        Returns:
            Block dictionary
        """
        return {"type": self.type}

@dataclass
class SlackTextBlock(SlackBlock):
    """Slack text block."""
    text: str
    
    def __init__(self, text: str):
        """Initialize a text block.
        
        Args:
            text: Block text
        """
        super().__init__(type="section")
        self.text = text
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the text block to a dictionary.
        
        Returns:
            Block dictionary
        """
        return {
            "type": self.type,
            "text": {
                "type": "mrkdwn",
                "text": self.text
            }
        }

@dataclass
class SlackDividerBlock(SlackBlock):
    """Slack divider block."""
    
    def __init__(self):
        """Initialize a divider block."""
        super().__init__(type="divider")

@dataclass
class SlackImageBlock(SlackBlock):
    """Slack image block."""
    image_url: str
    alt_text: str
    title: Optional[str] = None
    
    def __init__(self, image_url: str, alt_text: str, title: Optional[str] = None):
        """Initialize an image block.
        
        Args:
            image_url: Image URL
            alt_text: Alternative text
            title: Optional title
        """
        super().__init__(type="image")
        self.image_url = image_url
        self.alt_text = alt_text
        self.title = title
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the image block to a dictionary.
        
        Returns:
            Block dictionary
        """
        result = {
            "type": self.type,
            "image_url": self.image_url,
            "alt_text": self.alt_text
        }
        
        if self.title:
            result["title"] = {
                "type": "plain_text",
                "text": self.title
            }
        
        return result

@dataclass
class SlackButtonElement:
    """Slack button element."""
    text: str
    action_id: str
    value: str
    style: str = "primary"  # primary, danger, or default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the button element to a dictionary.
        
        Returns:
            Button dictionary
        """
        return {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": self.text
            },
            "action_id": self.action_id,
            "value": self.value,
            "style": self.style
        }

@dataclass
class SlackActionsBlock(SlackBlock):
    """Slack actions block."""
    elements: List[Union[SlackButtonElement]] = field(default_factory=list)
    
    def __init__(self, elements: List[Union[SlackButtonElement]] = None):
        """Initialize an actions block.
        
        Args:
            elements: Block elements
        """
        super().__init__(type="actions")
        self.elements = elements or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the actions block to a dictionary.
        
        Returns:
            Block dictionary
        """
        return {
            "type": self.type,
            "elements": [element.to_dict() for element in self.elements]
        }

@dataclass
class SlackMessage:
    """Slack message model."""
    channel: str
    text: str
    message_type: MessageType = MessageType.TEXT
    thread_ts: Optional[str] = None
    attachments: List[SlackAttachment] = field(default_factory=list)
    blocks: List[SlackBlock] = field(default_factory=list)
    user: Optional[str] = None
    ts: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary for API requests.
        
        Returns:
            Message dictionary
        """
        result = {
            "channel": self.channel,
            "text": self.text
        }
        
        if self.thread_ts:
            result["thread_ts"] = self.thread_ts
        
        if self.attachments:
            result["attachments"] = [attachment.to_dict() for attachment in self.attachments]
        
        if self.blocks:
            result["blocks"] = [block.to_dict() for block in self.blocks]
        
        return result
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SlackMessage':
        """Create a SlackMessage instance from an API response.
        
        Args:
            data: API response data
            
        Returns:
            SlackMessage instance
        """
        # Determine message type
        message_type = MessageType.TEXT
        if data.get("attachments"):
            message_type = MessageType.ATTACHMENT
        elif data.get("blocks"):
            message_type = MessageType.BLOCK
        elif data.get("thread_ts"):
            message_type = MessageType.THREAD
        
        # Parse attachments
        attachments = []
        for attachment_data in data.get("attachments", []):
            attachment = SlackAttachment(
                fallback=attachment_data.get("fallback", ""),
                color=attachment_data.get("color"),
                pretext=attachment_data.get("pretext"),
                author_name=attachment_data.get("author_name"),
                author_link=attachment_data.get("author_link"),
                author_icon=attachment_data.get("author_icon"),
                title=attachment_data.get("title"),
                title_link=attachment_data.get("title_link"),
                text=attachment_data.get("text"),
                fields=attachment_data.get("fields", []),
                image_url=attachment_data.get("image_url"),
                thumb_url=attachment_data.get("thumb_url"),
                footer=attachment_data.get("footer"),
                footer_icon=attachment_data.get("footer_icon"),
                ts=attachment_data.get("ts")
            )
            attachments.append(attachment)
        
        # Parse blocks (simplified)
        blocks = []
        
        return cls(
            channel=data.get("channel", ""),
            text=data.get("text", ""),
            message_type=message_type,
            thread_ts=data.get("thread_ts"),
            attachments=attachments,
            blocks=blocks,
            user=data.get("user"),
            ts=data.get("ts")
        )

@dataclass
class SlackEvent:
    """Slack event model."""
    type: EventType
    data: Dict[str, Any]
    event_id: Optional[str] = None
    event_time: Optional[int] = None
    team_id: Optional[str] = None
    
    @classmethod
    def from_webhook_payload(cls, payload: Dict[str, Any]) -> 'SlackEvent':
        """Create a SlackEvent instance from a webhook payload.
        
        Args:
            payload: Webhook payload
            
        Returns:
            SlackEvent instance
        """
        event_data = payload.get("event", {})
        event_type = event_data.get("type")
        
        try:
            event_type_enum = EventType(event_type)
        except ValueError:
            event_type_enum = EventType.MESSAGE  # Default to message
        
        return cls(
            type=event_type_enum,
            data=event_data,
            event_id=payload.get("event_id"),
            event_time=payload.get("event_time"),
            team_id=payload.get("team_id")
        )
