"""
Webhook handlers for Slack integration.

This module handles incoming webhooks from Slack.
"""

from typing import Dict, Any, List, Optional, Callable
import logging
import json
import time
from flask import Flask, request, jsonify, Response
import threading
from .config import SlackConfig
from .auth import SlackAuth
from .events import SlackEventHandler

logger = logging.getLogger(__name__)

class SlackWebhookHandler:
    """Handler for Slack webhooks."""
    
    def __init__(self, config: SlackConfig, event_handler: SlackEventHandler, port: int = 3000):
        """Initialize the webhook handler.
        
        Args:
            config: Slack configuration
            event_handler: Event handler
            port: Port to listen on
        """
        self.config = config
        self.auth = SlackAuth(config)
        self.event_handler = event_handler
        self.port = port
        self.app = Flask(__name__)
        self.server_thread = None
        self.running = False
        
        # Register routes
        self._register_routes()
        
        logger.debug("Slack webhook handler initialized")
    
    def _register_routes(self) -> None:
        """Register Flask routes."""
        
        @self.app.route('/slack/events', methods=['POST'])
        def handle_events():
            # Verify request signature
            if self.config.signing_secret:
                signature = request.headers.get('X-Slack-Signature', '')
                timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
                body = request.get_data(as_text=True)
                
                if not self.auth.verify_webhook_signature(signature, timestamp, body):
                    logger.warning("Invalid webhook signature")
                    return jsonify({"error": "Invalid signature"}), 401
            
            # Parse payload
            payload = request.json
            
            # Handle URL verification challenge
            if payload.get('type') == 'url_verification':
                return jsonify({"challenge": payload.get("challenge")})
            
            # Process event
            try:
                result = self.event_handler.process_webhook_payload(payload)
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error processing webhook payload: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/slack/commands', methods=['POST'])
        def handle_commands():
            # Verify request signature
            if self.config.signing_secret:
                signature = request.headers.get('X-Slack-Signature', '')
                timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
                body = request.get_data(as_text=True)
                
                if not self.auth.verify_webhook_signature(signature, timestamp, body):
                    logger.warning("Invalid webhook signature")
                    return jsonify({"error": "Invalid signature"}), 401
            
            # Parse form data
            command = request.form.get('command', '')
            text = request.form.get('text', '')
            user_id = request.form.get('user_id', '')
            channel_id = request.form.get('channel_id', '')
            
            logger.debug(f"Received command: {command} {text} from {user_id} in {channel_id}")
            
            # Process command
            try:
                # This is a placeholder implementation
                # You would typically dispatch to a command handler
                return jsonify({
                    "response_type": "ephemeral",
                    "text": f"Received command: {command} {text}"
                })
            except Exception as e:
                logger.error(f"Error processing command: {str(e)}")
                return jsonify({
                    "response_type": "ephemeral",
                    "text": f"Error: {str(e)}"
                })
        
        @self.app.route('/slack/interactive', methods=['POST'])
        def handle_interactive():
            # Verify request signature
            if self.config.signing_secret:
                signature = request.headers.get('X-Slack-Signature', '')
                timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
                body = request.get_data(as_text=True)
                
                if not self.auth.verify_webhook_signature(signature, timestamp, body):
                    logger.warning("Invalid webhook signature")
                    return jsonify({"error": "Invalid signature"}), 401
            
            # Parse payload
            payload_str = request.form.get('payload', '{}')
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                logger.error("Invalid JSON payload")
                return jsonify({"error": "Invalid payload"}), 400
            
            # Process interactive payload
            try:
                # This is a placeholder implementation
                # You would typically dispatch to an interactive handler
                action_type = payload.get('type', '')
                
                if action_type == 'block_actions':
                    actions = payload.get('actions', [])
                    for action in actions:
                        action_id = action.get('action_id', '')
                        value = action.get('value', '')
                        logger.debug(f"Received block action: {action_id} with value {value}")
                
                return jsonify({"response_type": "ephemeral", "text": "Received"})
            except Exception as e:
                logger.error(f"Error processing interactive payload: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "ok"})
    
    def start(self) -> None:
        """Start the webhook server."""
        if self.running:
            logger.warning("Webhook server is already running")
            return
        
        def run_server():
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.running = True
        
        logger.info(f"Webhook server started on port {self.port}")
    
    def stop(self) -> None:
        """Stop the webhook server."""
        if not self.running:
            logger.warning("Webhook server is not running")
            return
        
        # Shutdown Flask server
        import requests
        try:
            requests.get(f"http://localhost:{self.port}/shutdown")
        except:
            pass
        
        self.running = False
        logger.info("Webhook server stopped")
