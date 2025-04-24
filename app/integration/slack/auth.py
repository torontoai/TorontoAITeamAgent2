"""
Authentication module for Slack integration.

This module handles authentication with the Slack API.
"""

from typing import Dict, Any, Optional
import logging
import requests
import time
import json
import os
from .config import SlackConfig

logger = logging.getLogger(__name__)

class SlackAuth:
    """Authentication class for Slack integration."""
    
    def __init__(self, config: SlackConfig):
        """Initialize Slack authentication.
        
        Args:
            config: Slack configuration
        """
        self.config = config
        self.token_info = None
        
        logger.debug("Slack authentication initialized")
    
    def get_headers(self) -> Dict[str, str]:
        """Get the authentication headers for Slack API requests.
        
        Returns:
            Authentication headers
        """
        return {
            "Authorization": f"Bearer {self.config.bot_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
    
    def validate_token(self) -> bool:
        """Validate the bot token by making a test API call.
        
        Returns:
            True if the token is valid, False otherwise
        """
        try:
            response = requests.get(
                "https://slack.com/api/auth.test",
                headers=self.get_headers(),
                timeout=self.config.timeout
            )
            
            data = response.json()
            
            if data.get("ok"):
                self.token_info = {
                    "user_id": data.get("user_id"),
                    "team_id": data.get("team_id"),
                    "team": data.get("team"),
                    "user": data.get("user"),
                    "validated_at": time.time()
                }
                logger.debug(f"Token validated for user {data.get('user')} in team {data.get('team')}")
                return True
            else:
                logger.error(f"Token validation failed: {data.get('error')}")
                return False
        
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False
    
    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the validated token.
        
        Returns:
            Token information or None if not validated
        """
        return self.token_info
    
    def verify_webhook_signature(self, signature: str, timestamp: str, body: str) -> bool:
        """Verify the signature of an incoming webhook request.
        
        Args:
            signature: X-Slack-Signature header value
            timestamp: X-Slack-Request-Timestamp header value
            body: Raw request body
            
        Returns:
            True if the signature is valid, False otherwise
        """
        if not self.config.signing_secret:
            logger.error("Signing secret not configured")
            return False
        
        # Check if the timestamp is too old (>5 minutes)
        current_timestamp = int(time.time())
        if abs(current_timestamp - int(timestamp)) > 300:
            logger.error("Timestamp too old")
            return False
        
        import hmac
        import hashlib
        
        # Create the signature base string
        sig_basestring = f"v0:{timestamp}:{body}"
        
        # Calculate the signature
        my_signature = 'v0=' + hmac.new(
            self.config.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        if hmac.compare_digest(my_signature, signature):
            return True
        else:
            logger.error("Signature verification failed")
            return False
    
    @staticmethod
    def start_oauth_flow(client_id: str, scopes: str, redirect_uri: str) -> str:
        """Start the OAuth flow by generating the authorization URL.
        
        Args:
            client_id: Slack client ID
            scopes: Comma-separated list of scopes
            redirect_uri: Redirect URI
            
        Returns:
            Authorization URL
        """
        params = {
            "client_id": client_id,
            "scope": scopes,
            "redirect_uri": redirect_uri
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://slack.com/oauth/v2/authorize?{query_string}"
    
    @staticmethod
    def complete_oauth_flow(
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """Complete the OAuth flow by exchanging the code for tokens.
        
        Args:
            client_id: Slack client ID
            client_secret: Slack client secret
            code: Authorization code
            redirect_uri: Redirect URI
            
        Returns:
            OAuth response containing tokens
        """
        try:
            response = requests.post(
                "https://slack.com/api/oauth.v2.access",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            data = response.json()
            
            if data.get("ok"):
                return data
            else:
                logger.error(f"OAuth flow failed: {data.get('error')}")
                return {"ok": False, "error": data.get("error")}
        
        except Exception as e:
            logger.error(f"Error completing OAuth flow: {str(e)}")
            return {"ok": False, "error": str(e)}
