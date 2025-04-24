"""
Script to update the API integration manager with Slack integration support.

This script updates the API integration manager to fully support Slack integration.
"""

import sys
import os
import logging

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_integration_manager():
    """Update the API integration manager with Slack integration support."""
    
    # Path to the integration manager file
    file_path = os.path.join('app', 'api', 'integration_manager.py')
    
    # Read the current file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if Slack test method is already implemented
    if '_test_slack_connection' in content and 'def _test_slack_connection' not in content:
        # Add the Slack test method implementation
        slack_test_method = '''
    def _test_slack_connection(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test Slack connection."""
        try:
            # Import Slack integration modules
            from app.integration.slack import SlackConfig, SlackClient
            
            # Create Slack configuration
            slack_config = SlackConfig(
                bot_token=self._decrypt_api_key(config_data.get("api_key")),
                app_token=config_data.get("settings", {}).get("app_token"),
                signing_secret=config_data.get("settings", {}).get("signing_secret"),
                default_channel=config_data.get("settings", {}).get("default_channel", "general")
            )
            
            # Create Slack client
            client = SlackClient(slack_config)
            
            # Test connection by getting channels
            try:
                channels = client.get_channels()
                channel_names = [channel.name for channel in channels]
                
                return {
                    "success": True,
                    "message": "Successfully connected to Slack API",
                    "channels": channel_names
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error connecting to Slack API: {str(e)}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error connecting to Slack API: {str(e)}"
            }
'''
        
        # Find the position to insert the method
        insert_pos = content.find('def _test_custom_connection')
        if insert_pos == -1:
            insert_pos = content.find('def _create_slack_client')
        
        if insert_pos != -1:
            # Insert the method before the found position
            content = content[:insert_pos] + slack_test_method + content[insert_pos:]
        else:
            logger.error("Could not find insertion point for Slack test method")
            return False
    
    # Check if Slack client creation method is already implemented
    if '_create_slack_client' in content and 'def _create_slack_client' not in content:
        # Add the Slack client creation method implementation
        slack_client_method = '''
    def _create_slack_client(self, config_data: Dict[str, Any]) -> Any:
        """Create Slack client."""
        # Import Slack integration modules
        from app.integration.slack import SlackConfig, SlackClient
        
        # Create Slack configuration
        slack_config = SlackConfig(
            bot_token=self._decrypt_api_key(config_data.get("api_key")),
            app_token=config_data.get("settings", {}).get("app_token"),
            signing_secret=config_data.get("settings", {}).get("signing_secret"),
            default_channel=config_data.get("settings", {}).get("default_channel", "general")
        )
        
        # Create and return Slack client
        return SlackClient(slack_config)
'''
        
        # Find the position to insert the method
        insert_pos = content.find('def _create_custom_client')
        
        if insert_pos != -1:
            # Insert the method before the found position
            content = content[:insert_pos] + slack_client_method + content[insert_pos:]
        else:
            logger.error("Could not find insertion point for Slack client method")
            return False
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    logger.info("Successfully updated API integration manager with Slack integration support")
    return True

if __name__ == "__main__":
    update_integration_manager()
