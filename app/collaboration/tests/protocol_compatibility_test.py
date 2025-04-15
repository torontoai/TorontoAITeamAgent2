import os
import sys
import asyncio
import logging
from typing import Dict, Any, List

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.collaboration.google_a2a_adapter import GoogleA2AClientAdapter
from app.collaboration.anthropic_mcp_adapter import AnthropicMCPClientAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("protocol_compatibility_test")

async def test_google_a2a_compatibility():
    """Test compatibility with Google's A2A protocol."""
    logger.info("Testing Google A2A protocol compatibility...")
    
    # Initialize client adapter
    client_config = {
        "default_timeout": 30,
        "max_retries": 3,
        "streaming_buffer_size": 1024
    }
    client = GoogleA2AClientAdapter(client_config)
    
    try:
        # Initialize the adapter
        await client.initialize()
        logger.info("✓ Successfully initialized Google A2A client adapter")
        
        # Connect to a simulated A2A server
        server_url = "https://example.com/a2a"
        connected = await client.connect_to_server(server_url)
        
        if connected:
            logger.info(f"✓ Successfully connected to A2A server: {server_url}")
            
            # Discover agent capabilities
            capabilities = await client.discover_agent_capabilities(server_url)
            logger.info(f"✓ Successfully discovered agent capabilities: {capabilities['name']}")
            logger.info(f"  - Capabilities: {capabilities['capabilities']}")
            logger.info(f"  - Skills: {[skill['name'] for skill in capabilities['skills']]}")
            
            # Send a task
            message = {
                "parts": [
                    {
                        "text": "Hello, this is a test message from TORONTO AI TEAM AGENT."
                    }
                ]
            }
            
            response = await client.send_task(server_url, message)
            logger.info(f"✓ Successfully sent task to A2A server")
            logger.info(f"  - Task ID: {response['result']['task']['id']}")
            logger.info(f"  - Task Status: {response['result']['task']['status']}")
            
            # Test streaming
            logger.info("Testing streaming task updates...")
            
            updates = []
            async for update in client.subscribe_to_task(server_url, message):
                updates.append(update)
                logger.info(f"  - Received update: {update['type']}")
            
            logger.info(f"✓ Successfully received {len(updates)} streaming updates")
            logger.info(f"  - Final status: {updates[-1]['data']['task']['status']}")
            
            logger.info("Google A2A protocol compatibility test completed successfully!")
        else:
            logger.error(f"Failed to connect to A2A server: {server_url}")
    
    except Exception as e:
        logger.error(f"Error during Google A2A compatibility test: {str(e)}")
    
    finally:
        # Shutdown the adapter
        await client.shutdown()
        logger.info("Google A2A client adapter shut down")

async def test_anthropic_mcp_compatibility():
    """Test compatibility with Anthropic's MCP."""
    logger.info("Testing Anthropic MCP compatibility...")
    
    # Initialize client adapter
    client_config = {
        "default_timeout": 30,
        "max_retries": 3
    }
    client = AnthropicMCPClientAdapter(client_config)
    
    try:
        # Initialize the adapter
        await client.initialize()
        logger.info("✓ Successfully initialized Anthropic MCP client adapter")
        
        # Connect to a simulated MCP server
        server_url = "https://example.com/mcp"
        connected = await client.connect_to_server(server_url)
        
        if connected:
            logger.info(f"✓ Successfully connected to MCP server: {server_url}")
            
            # Discover tools
            tools = await client.discover_tools(server_url)
            logger.info(f"✓ Successfully discovered {len(tools)} tools")
            for tool in tools:
                logger.info(f"  - Tool: {tool['name']} - {tool['description']}")
            
            # Invoke file system tool
            file_params = {
                "operation": "read",
                "path": "/test/example.txt"
            }
            
            file_result = await client.invoke_tool(server_url, "file_system", file_params)
            logger.info(f"✓ Successfully invoked file_system tool")
            logger.info(f"  - Success: {file_result.get('success', False)}")
            logger.info(f"  - Data: {file_result.get('data', 'N/A')}")
            
            # Invoke web search tool
            search_params = {
                "query": "TORONTO AI TEAM AGENT",
                "num_results": 3
            }
            
            search_result = await client.invoke_tool(server_url, "web_search", search_params)
            logger.info(f"✓ Successfully invoked web_search tool")
            logger.info(f"  - Results: {len(search_result.get('results', []))}")
            
            # Test streaming
            logger.info("Testing streaming tool invocation...")
            
            updates = []
            async for update in client.stream_tool_invocation(server_url, "file_system", file_params):
                updates.append(update)
                logger.info(f"  - Received update: {update['status']}")
            
            logger.info(f"✓ Successfully received {len(updates)} streaming updates")
            logger.info(f"  - Final status: {updates[-1]['status']}")
            
            logger.info("Anthropic MCP compatibility test completed successfully!")
        else:
            logger.error(f"Failed to connect to MCP server: {server_url}")
    
    except Exception as e:
        logger.error(f"Error during Anthropic MCP compatibility test: {str(e)}")
    
    finally:
        # Shutdown the adapter
        await client.shutdown()
        logger.info("Anthropic MCP client adapter shut down")

async def run_compatibility_tests():
    """Run all protocol compatibility tests."""
    logger.info("Starting protocol compatibility tests...")
    
    # Test Google A2A protocol
    await test_google_a2a_compatibility()
    
    logger.info("-" * 80)
    
    # Test Anthropic MCP
    await test_anthropic_mcp_compatibility()
    
    logger.info("All protocol compatibility tests completed!")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_compatibility_tests())
