"""
Test module for Slack integration.

This module contains tests for the Slack integration functionality.
"""

import unittest
import os
import json
import logging
import tempfile
from unittest.mock import MagicMock, patch

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import Slack integration modules
from app.integration.slack.config import SlackConfig
from app.integration.slack.auth import SlackAuth
from app.integration.slack.client import SlackClient, SlackApiError
from app.integration.slack.models import (
    SlackMessage, SlackAttachment, SlackBlock, SlackTextBlock,
    SlackUser, SlackChannel, MessageType, EventType, SlackEvent
)
from app.integration.slack.formatter import SlackFormatter
from app.integration.slack.events import SlackEventHandler
from app.integration.slack.webhooks import SlackWebhookHandler
from app.integration.slack.sync_manager import SlackSyncManager
from app.integration.slack.mcp_a2a_integration import SlackMCPA2AIntegration
from app.integration.slack import SlackIntegration

class TestSlackConfig(unittest.TestCase):
    """Test cases for SlackConfig."""
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "bot_token": "xoxb-test-token",
            "app_token": "xapp-test-token",
            "signing_secret": "test-secret",
            "default_channel": "test-channel",
            "max_retries": 5,
            "retry_delay": 2,
            "timeout": 60,
            "debug_mode": True,
            "channel_mappings": {"general": "C12345"},
            "user_mappings": {"user1": "U12345"}
        }
        
        config = SlackConfig.from_dict(config_dict)
        
        self.assertEqual(config.bot_token, "xoxb-test-token")
        self.assertEqual(config.app_token, "xapp-test-token")
        self.assertEqual(config.signing_secret, "test-secret")
        self.assertEqual(config.default_channel, "test-channel")
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.retry_delay, 2)
        self.assertEqual(config.timeout, 60)
        self.assertTrue(config.debug_mode)
        self.assertEqual(config.channel_mappings, {"general": "C12345"})
        self.assertEqual(config.user_mappings, {"user1": "U12345"})
    
    def test_from_file(self):
        """Test creating config from file."""
        config_dict = {
            "bot_token": "xoxb-test-token",
            "default_channel": "test-channel"
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            json.dump(config_dict, f)
            temp_file = f.name
        
        try:
            config = SlackConfig.from_file(temp_file)
            
            self.assertEqual(config.bot_token, "xoxb-test-token")
            self.assertEqual(config.default_channel, "test-channel")
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_validate(self):
        """Test config validation."""
        # Valid config
        config = SlackConfig(bot_token="xoxb-test-token")
        self.assertEqual(config.validate(), [])
        
        # Invalid config - missing bot token
        config = SlackConfig(bot_token="")
        self.assertIn("Bot token is required", config.validate())
        
        # Invalid config - invalid bot token format
        config = SlackConfig(bot_token="invalid-token")
        self.assertIn("Bot token must start with 'xoxb-'", config.validate())
        
        # Invalid config - invalid app token format
        config = SlackConfig(bot_token="xoxb-test-token", app_token="invalid-token")
        self.assertIn("App token must start with 'xapp-'", config.validate())

class TestSlackAuth(unittest.TestCase):
    """Test cases for SlackAuth."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SlackConfig(bot_token="xoxb-test-token")
        self.auth = SlackAuth(self.config)
    
    def test_get_headers(self):
        """Test getting authentication headers."""
        headers = self.auth.get_headers()
        
        self.assertEqual(headers["Authorization"], "Bearer xoxb-test-token")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
    
    @patch("requests.get")
    def test_validate_token_success(self, mock_get):
        """Test successful token validation."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "user_id": "U12345",
            "team_id": "T12345",
            "team": "Test Team",
            "user": "test-user"
        }
        mock_get.return_value = mock_response
        
        result = self.auth.validate_token()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.auth.token_info)
        self.assertEqual(self.auth.token_info["user_id"], "U12345")
    
    @patch("requests.get")
    def test_validate_token_failure(self, mock_get):
        """Test failed token validation."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": False,
            "error": "invalid_auth"
        }
        mock_get.return_value = mock_response
        
        result = self.auth.validate_token()
        
        self.assertFalse(result)
        self.assertIsNone(self.auth.token_info)
    
    def test_verify_webhook_signature(self):
        """Test webhook signature verification."""
        # Set up test data
        self.config.signing_secret = "test-secret"
        timestamp = "1234567890"
        body = "test-body"
        
        # Generate signature
        import hmac
        import hashlib
        
        sig_basestring = f"v0:{timestamp}:{body}"
        signature = 'v0=' + hmac.new(
            self.config.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Test valid signature
        self.assertTrue(self.auth.verify_webhook_signature(signature, timestamp, body))
        
        # Test invalid signature
        self.assertFalse(self.auth.verify_webhook_signature("v0=invalid", timestamp, body))

class TestSlackModels(unittest.TestCase):
    """Test cases for Slack models."""
    
    def test_slack_message(self):
        """Test SlackMessage model."""
        # Create message
        message = SlackMessage(
            channel="C12345",
            text="Hello, world!",
            thread_ts="1234567890.123456"
        )
        
        # Test to_dict
        message_dict = message.to_dict()
        self.assertEqual(message_dict["channel"], "C12345")
        self.assertEqual(message_dict["text"], "Hello, world!")
        self.assertEqual(message_dict["thread_ts"], "1234567890.123456")
        
        # Test with attachments
        attachment = SlackAttachment(
            fallback="Test attachment",
            text="Attachment text",
            color="#36a64f"
        )
        message.attachments.append(attachment)
        message.message_type = MessageType.ATTACHMENT
        
        message_dict = message.to_dict()
        self.assertIn("attachments", message_dict)
        self.assertEqual(len(message_dict["attachments"]), 1)
        self.assertEqual(message_dict["attachments"][0]["fallback"], "Test attachment")
    
    def test_slack_event(self):
        """Test SlackEvent model."""
        # Create event from webhook payload
        payload = {
            "event": {
                "type": "message",
                "channel": "C12345",
                "user": "U12345",
                "text": "Hello, world!",
                "ts": "1234567890.123456"
            },
            "event_id": "Ev12345",
            "event_time": 1234567890,
            "team_id": "T12345"
        }
        
        event = SlackEvent.from_webhook_payload(payload)
        
        self.assertEqual(event.type, EventType.MESSAGE)
        self.assertEqual(event.data["channel"], "C12345")
        self.assertEqual(event.data["user"], "U12345")
        self.assertEqual(event.data["text"], "Hello, world!")
        self.assertEqual(event.event_id, "Ev12345")
        self.assertEqual(event.event_time, 1234567890)
        self.assertEqual(event.team_id, "T12345")

class TestSlackFormatter(unittest.TestCase):
    """Test cases for SlackFormatter."""
    
    def test_text_to_mrkdwn(self):
        """Test converting text to mrkdwn format."""
        # Test HTML-style formatting
        html_text = "This is <b>bold</b> and <i>italic</i> text with <code>code</code>."
        mrkdwn = SlackFormatter.text_to_mrkdwn(html_text)
        self.assertEqual(mrkdwn, "This is *bold* and _italic_ text with `code`.")
        
        # Test Markdown-style links
        md_text = "Check out [this link](https://example.com)."
        mrkdwn = SlackFormatter.text_to_mrkdwn(md_text)
        self.assertEqual(mrkdwn, "Check out <https://example.com|this link>.")
    
    def test_create_blocks(self):
        """Test creating blocks."""
        # Test text block
        text_block = SlackFormatter.create_text_block("Hello, world!")
        self.assertEqual(text_block.type, "section")
        self.assertEqual(text_block.text, "Hello, world!")
        
        # Test divider block
        divider_block = SlackFormatter.create_divider_block()
        self.assertEqual(divider_block.type, "divider")
        
        # Test image block
        image_block = SlackFormatter.create_image_block(
            image_url="https://example.com/image.png",
            alt_text="Example image",
            title="Example"
        )
        self.assertEqual(image_block.type, "image")
        self.assertEqual(image_block.image_url, "https://example.com/image.png")
        self.assertEqual(image_block.alt_text, "Example image")
        self.assertEqual(image_block.title, "Example")

@patch("app.integration.slack.client.requests.post")
@patch("app.integration.slack.client.requests.get")
class TestSlackClient(unittest.TestCase):
    """Test cases for SlackClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SlackConfig(bot_token="xoxb-test-token")
        self.client = SlackClient(self.config)
    
    def test_send_message(self, mock_get, mock_post):
        """Test sending a message."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "channel": "C12345",
            "ts": "1234567890.123456",
            "message": {
                "text": "Hello, world!"
            }
        }
        mock_post.return_value = mock_response
        
        # Create message
        message = SlackMessage(
            channel="C12345",
            text="Hello, world!"
        )
        
        # Send message
        response = self.client.send_message(message)
        
        # Verify response
        self.assertEqual(response["channel"], "C12345")
        self.assertEqual(response["ts"], "1234567890.123456")
        
        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://slack.com/api/chat.postMessage")
        self.assertEqual(kwargs["json"]["channel"], "C12345")
        self.assertEqual(kwargs["json"]["text"], "Hello, world!")
    
    def test_send_message_error(self, mock_get, mock_post):
        """Test sending a message with error."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": False,
            "error": "channel_not_found"
        }
        mock_post.return_value = mock_response
        
        # Create message
        message = SlackMessage(
            channel="invalid-channel",
            text="Hello, world!"
        )
        
        # Send message
        with self.assertRaises(SlackApiError):
            self.client.send_message(message)
    
    def test_get_channels(self, mock_get, mock_post):
        """Test getting channels."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "channels": [
                {
                    "id": "C12345",
                    "name": "general",
                    "is_private": False,
                    "is_archived": False,
                    "topic": {"value": "General discussion"},
                    "purpose": {"value": "This channel is for team-wide communication"},
                    "num_members": 10,
                    "created": 1234567890
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Get channels
        channels = self.client.get_channels()
        
        # Verify channels
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0].id, "C12345")
        self.assertEqual(channels[0].name, "general")
        self.assertEqual(channels[0].topic, "General discussion")
        
        # Verify request
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://slack.com/api/conversations.list")

class TestSlackIntegration(unittest.TestCase):
    """Test cases for SlackIntegration."""
    
    @patch("app.integration.slack.SlackClient")
    @patch("app.integration.slack.SlackEventHandler")
    @patch("app.integration.slack.SlackWebhookHandler")
    @patch("app.integration.slack.SlackSyncManager")
    @patch("app.integration.slack.SlackMCPA2AIntegration")
    def test_initialization(self, mock_mcp_a2a, mock_sync, mock_webhook, mock_event, mock_client):
        """Test initialization."""
        # Create config
        config = SlackConfig(bot_token="xoxb-test-token")
        
        # Create integration
        integration = SlackIntegration(config=config)
        
        # Verify components created
        mock_client.assert_called_once()
        mock_event.assert_called_once()
        mock_sync.assert_called_once()
        mock_webhook.assert_called_once()
        mock_mcp_a2a.assert_called_once()
    
    @patch("app.integration.slack.SlackClient")
    @patch("app.integration.slack.SlackEventHandler")
    @patch("app.integration.slack.SlackWebhookHandler")
    @patch("app.integration.slack.SlackSyncManager")
    @patch("app.integration.slack.SlackMCPA2AIntegration")
    def test_start_stop(self, mock_mcp_a2a, mock_sync, mock_webhook, mock_event, mock_client):
        """Test starting and stopping."""
        # Create mocks
        mock_sync_instance = MagicMock()
        mock_sync.return_value = mock_sync_instance
        
        mock_webhook_instance = MagicMock()
        mock_webhook.return_value = mock_webhook_instance
        
        # Create config
        config = SlackConfig(bot_token="xoxb-test-token")
        
        # Create integration
        integration = SlackIntegration(config=config)
        
        # Start integration
        integration.start()
        
        # Verify components started
        mock_sync_instance.start.assert_called_once()
        mock_webhook_instance.start.assert_called_once()
        
        # Stop integration
        integration.stop()
        
        # Verify components stopped
        mock_sync_instance.stop.assert_called_once()
        mock_webhook_instance.stop.assert_called_once()
    
    @patch("app.integration.slack.SlackClient")
    @patch("app.integration.slack.SlackEventHandler")
    @patch("app.integration.slack.SlackWebhookHandler")
    @patch("app.integration.slack.SlackSyncManager")
    @patch("app.integration.slack.SlackMCPA2AIntegration")
    def test_send_message(self, mock_mcp_a2a, mock_sync, mock_webhook, mock_event, mock_client):
        """Test sending a message."""
        # Create mocks
        mock_sync_instance = MagicMock()
        mock_sync_instance.queue_message.return_value = "msg-123"
        mock_sync.return_value = mock_sync_instance
        
        # Create config
        config = SlackConfig(bot_token="xoxb-test-token")
        
        # Create integration
        integration = SlackIntegration(config=config)
        
        # Send message
        message_id = integration.send_message(
            channel="general",
            text="Hello, world!",
            thread_ts="1234567890.123456"
        )
        
        # Verify message queued
        mock_sync_instance.queue_message.assert_called_once()
        self.assertEqual(message_id, "msg-123")

if __name__ == "__main__":
    unittest.main()
