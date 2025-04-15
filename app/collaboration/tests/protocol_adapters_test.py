import unittest
import asyncio
import json
import logging
from unittest.mock import MagicMock, patch

from app.collaboration.google_a2a_adapter import (
    GoogleA2AClientAdapter,
    GoogleA2AServerAdapter,
    GoogleA2AMessageTranslator
)
from app.collaboration.anthropic_mcp_adapter import (
    AnthropicMCPClientAdapter,
    AnthropicMCPServerAdapter,
    AnthropicMCPToolMapper
)

# Configure logging
logging.basicConfig(level=logging.INFO)

class TestGoogleA2AAdapter(unittest.TestCase):
    """Test cases for Google A2A protocol adapters."""
    
    def setUp(self):
        """Set up test environment."""
        self.client_config = {
            "default_timeout": 10,
            "max_retries": 2,
            "streaming_buffer_size": 512
        }
        
        self.server_config = {
            "expose_agent_card": True,
            "supported_capabilities": {
                "streaming": True,
                "pushNotifications": False,
                "stateTransitionHistory": True
            }
        }
        
        # Mock agent manager
        self.agent_manager = MagicMock()
        self.agent_manager.list_agents.return_value = [
            {
                "id": "agent1",
                "name": "Test Agent 1",
                "skills": [
                    {
                        "id": "skill1",
                        "name": "Test Skill 1",
                        "description": "A test skill"
                    }
                ]
            }
        ]
        
        # Create adapters
        self.client_adapter = GoogleA2AClientAdapter(self.client_config)
        self.server_adapter = GoogleA2AServerAdapter(self.server_config, self.agent_manager)
    
    async def async_setUp(self):
        """Asynchronous setup."""
        await self.client_adapter.initialize()
        await self.server_adapter.initialize()
    
    async def async_tearDown(self):
        """Asynchronous teardown."""
        await self.client_adapter.shutdown()
        await self.server_adapter.shutdown()
    
    def test_client_adapter_init(self):
        """Test client adapter initialization."""
        self.assertEqual(self.client_adapter.default_timeout, 10)
        self.assertEqual(self.client_adapter.max_retries, 2)
        self.assertEqual(self.client_adapter.streaming_buffer_size, 512)
        self.assertEqual(len(self.client_adapter.connected_servers), 0)
    
    def test_server_adapter_init(self):
        """Test server adapter initialization."""
        self.assertEqual(self.server_adapter.expose_agent_card, True)
        self.assertEqual(self.server_adapter.supported_capabilities["streaming"], True)
        self.assertEqual(self.server_adapter.supported_capabilities["pushNotifications"], False)
        self.assertEqual(len(self.server_adapter.active_tasks), 0)
    
    def test_message_translator(self):
        """Test message translation between internal and A2A formats."""
        # Internal to A2A
        internal_message = {
            "role": "user",
            "content": "Hello, world!",
            "attachments": [
                {
                    "type": "file",
                    "mime_type": "text/plain",
                    "data": "SGVsbG8sIHdvcmxkIQ=="
                }
            ]
        }
        
        a2a_message = GoogleA2AMessageTranslator.internal_to_a2a(internal_message)
        
        self.assertEqual(a2a_message["role"], "user")
        self.assertEqual(len(a2a_message["parts"]), 2)
        self.assertEqual(a2a_message["parts"][0]["text"], "Hello, world!")
        self.assertEqual(a2a_message["parts"][1]["file"]["mime_type"], "text/plain")
        
        # A2A to internal
        a2a_message = {
            "role": "agent",
            "parts": [
                {
                    "text": "I can help with that."
                },
                {
                    "data": {
                        "result": 42
                    }
                }
            ]
        }
        
        internal_message = GoogleA2AMessageTranslator.a2a_to_internal(a2a_message)
        
        self.assertEqual(internal_message["role"], "agent")
        self.assertEqual(internal_message["content"], "I can help with that.")
        self.assertEqual(len(internal_message["attachments"]), 1)
        self.assertEqual(internal_message["attachments"][0]["type"], "data")
        self.assertEqual(internal_message["attachments"][0]["data"]["result"], 42)
    
    def test_agent_card_generation(self):
        """Test agent card generation."""
        agent_card = self.server_adapter.generate_agent_card()
        
        self.assertEqual(agent_card["name"], "TORONTO AI TEAM AGENT")
        self.assertTrue("capabilities" in agent_card)
        self.assertTrue("skills" in agent_card)
        self.assertEqual(len(agent_card["skills"]), 1)
        self.assertEqual(agent_card["skills"][0]["id"], "skill1")
    
    async def test_client_connect(self):
        """Test client connection to server."""
        result = await self.client_adapter.connect_to_server("https://example.com/a2a")
        
        self.assertTrue(result)
        self.assertTrue("https://example.com/a2a" in self.client_adapter.connected_servers)
        self.assertTrue(self.client_adapter.connected_servers["https://example.com/a2a"]["connected"])
    
    async def test_discover_capabilities(self):
        """Test discovering agent capabilities."""
        await self.client_adapter.connect_to_server("https://example.com/a2a")
        capabilities = await self.client_adapter.discover_agent_capabilities("https://example.com/a2a")
        
        self.assertTrue("name" in capabilities)
        self.assertTrue("capabilities" in capabilities)
        self.assertTrue("skills" in capabilities)
        self.assertTrue(len(capabilities["skills"]) > 0)
    
    async def test_send_task(self):
        """Test sending a task to a server."""
        await self.client_adapter.connect_to_server("https://example.com/a2a")
        
        message = {
            "parts": [
                {
                    "text": "Hello, world!"
                }
            ]
        }
        
        response = await self.client_adapter.send_task("https://example.com/a2a", message)
        
        self.assertTrue("jsonrpc" in response)
        self.assertTrue("result" in response)
        self.assertTrue("task" in response["result"])
        self.assertEqual(response["result"]["task"]["status"], "working")
    
    async def test_task_streaming(self):
        """Test task streaming."""
        await self.client_adapter.connect_to_server("https://example.com/a2a")
        
        message = {
            "parts": [
                {
                    "text": "Hello, world!"
                }
            ]
        }
        
        updates = []
        async for update in self.client_adapter.subscribe_to_task("https://example.com/a2a", message):
            updates.append(update)
        
        self.assertTrue(len(updates) > 0)
        self.assertEqual(updates[0]["type"], "TaskStatusUpdateEvent")
        self.assertEqual(updates[-1]["data"]["task"]["status"], "completed")
    
    async def test_handle_task_send(self):
        """Test handling a task send request."""
        request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tasks/send",
            "params": {
                "taskId": "test_task_1",
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "text": "Hello, world!"
                        }
                    ]
                }
            }
        }
        
        response = await self.server_adapter.handle_task_send(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "1")
        self.assertTrue("result" in response)
        self.assertTrue("task" in response["result"])
        self.assertEqual(response["result"]["task"]["id"], "test_task_1")
        self.assertEqual(response["result"]["task"]["status"], "completed")
    
    async def test_handle_task_send_subscribe(self):
        """Test handling a task send subscribe request."""
        request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tasks/sendSubscribe",
            "params": {
                "taskId": "test_task_2",
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "text": "Hello, world!"
                        }
                    ]
                }
            }
        }
        
        updates = []
        async for update in self.server_adapter.handle_task_send_subscribe(request):
            updates.append(update)
        
        self.assertTrue(len(updates) > 0)
        self.assertEqual(updates[0]["type"], "TaskStatusUpdateEvent")
        self.assertEqual(updates[0]["data"]["task"]["id"], "test_task_2")
        self.assertEqual(updates[-1]["data"]["task"]["status"], "completed")
    
    async def test_handle_task_cancel(self):
        """Test handling a task cancel request."""
        # First create a task
        send_request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tasks/send",
            "params": {
                "taskId": "test_task_3",
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "text": "Hello, world!"
                        }
                    ]
                }
            }
        }
        
        await self.server_adapter.handle_task_send(send_request)
        
        # Now cancel it
        cancel_request = {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tasks/cancel",
            "params": {
                "taskId": "test_task_3"
            }
        }
        
        response = await self.server_adapter.handle_task_cancel(cancel_request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "2")
        self.assertTrue("result" in response)
        self.assertTrue(response["result"]["success"])
        self.assertEqual(self.server_adapter.active_tasks["test_task_3"]["status"], "canceled")

class TestAnthropicMCPAdapter(unittest.TestCase):
    """Test cases for Anthropic MCP protocol adapters."""
    
    def setUp(self):
        """Set up test environment."""
        self.client_config = {
            "default_timeout": 10,
            "max_retries": 2
        }
        
        self.server_config = {
            "expose_tool_schema": True,
            "supported_workflow_patterns": [
                "augmented_llm",
                "router",
                "orchestrator_workers"
            ]
        }
        
        # Mock tool manager
        self.tool_manager = MagicMock()
        self.tool_manager.list_tools.return_value = [
            {
                "name": "file_system",
                "description": "Access the file system",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["read", "write", "list"]
                        },
                        "path": {
                            "type": "string"
                        }
                    },
                    "required": ["operation", "path"]
                }
            }
        ]
        
        # Create adapters
        self.client_adapter = AnthropicMCPClientAdapter(self.client_config)
        self.server_adapter = AnthropicMCPServerAdapter(self.server_config, self.tool_manager)
    
    async def async_setUp(self):
        """Asynchronous setup."""
        await self.client_adapter.initialize()
        await self.server_adapter.initialize()
    
    async def async_tearDown(self):
        """Asynchronous teardown."""
        await self.client_adapter.shutdown()
        await self.server_adapter.shutdown()
    
    def test_client_adapter_init(self):
        """Test client adapter initialization."""
        self.assertEqual(self.client_adapter.default_timeout, 10)
        self.assertEqual(self.client_adapter.max_retries, 2)
        self.assertEqual(len(self.client_adapter.connected_servers), 0)
    
    def test_server_adapter_init(self):
        """Test server adapter initialization."""
        self.assertEqual(self.server_adapter.expose_tool_schema, True)
        self.assertEqual(len(self.server_adapter.supported_workflow_patterns), 3)
        self.assertTrue("augmented_llm" in self.server_adapter.supported_workflow_patterns)
        self.assertEqual(len(self.server_adapter.active_sessions), 0)
    
    def test_tool_mapper(self):
        """Test tool mapping between internal and MCP formats."""
        # Internal to MCP
        internal_tool = {
            "name": "calculator",
            "description": "Perform calculations",
            "parameters": {
                "expression": {
                    "type": "string",
                    "description": "The expression to calculate",
                    "required": True
                },
                "precision": {
                    "type": "integer",
                    "description": "Decimal precision",
                    "required": False
                }
            }
        }
        
        mcp_tool = AnthropicMCPToolMapper.internal_to_mcp(internal_tool)
        
        self.assertEqual(mcp_tool["name"], "calculator")
        self.assertEqual(mcp_tool["description"], "Perform calculations")
        self.assertTrue("input_schema" in mcp_tool)
        self.assertTrue("expression" in mcp_tool["input_schema"]["properties"])
        self.assertTrue("precision" in mcp_tool["input_schema"]["properties"])
        self.assertTrue("expression" in mcp_tool["input_schema"]["required"])
        self.assertFalse("precision" in mcp_tool["input_schema"]["required"])
        
        # MCP to internal
        mcp_tool = {
            "name": "web_search",
            "description": "Search the web",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results"
                    }
                },
                "required": ["query"]
            }
        }
        
        internal_tool = AnthropicMCPToolMapper.mcp_to_internal(mcp_tool)
        
        self.assertEqual(internal_tool["name"], "web_search")
        self.assertEqual(internal_tool["description"], "Search the web")
        self.assertTrue("parameters" in internal_tool)
        self.assertTrue("query" in internal_tool["parameters"])
        self.assertTrue("num_results" in internal_tool["parameters"])
        self.assertTrue(internal_tool["parameters"]["query"]["required"])
        self.assertFalse(internal_tool["parameters"]["num_results"]["required"])
    
    def test_tool_schema_generation(self):
        """Test tool schema generation."""
        schema = self.server_adapter.generate_tool_schema()
        
        self.assertTrue("server_info" in schema)
        self.assertEqual(schema["server_info"]["name"], "TORONTO AI TEAM AGENT MCP Server")
        self.assertTrue("tools" in schema)
        self.assertEqual(len(schema["tools"]), 1)
        self.assertEqual(schema["tools"][0]["name"], "file_system")
        self.assertTrue("supported_workflow_patterns" in schema)
        self.assertEqual(len(schema["supported_workflow_patterns"]), 3)
    
    async def test_client_connect(self):
        """Test client connection to server."""
        result = await self.client_adapter.connect_to_server("https://example.com/mcp")
        
        self.assertTrue(result)
        self.assertTrue("https://example.com/mcp" in self.client_adapter.connected_servers)
        self.assertTrue(self.client_adapter.connected_servers["https://example.com/mcp"]["connected"])
    
    async def test_discover_tools(self):
        """Test discovering tools from a server."""
        await self.client_adapter.connect_to_server("https://example.com/mcp")
        tools = await self.client_adapter.discover_tools("https://example.com/mcp")
        
        self.assertTrue(len(tools) > 0)
        self.assertEqual(tools[0]["name"], "file_system")
        self.assertTrue("input_schema" in tools[0])
        self.assertTrue("output_schema" in tools[0])
    
    async def test_invoke_tool(self):
        """Test invoking a tool on a server."""
        await self.client_adapter.connect_to_server("https://example.com/mcp")
        
        params = {
            "operation": "read",
            "path": "/test/file.txt"
        }
        
        result = await self.client_adapter.invoke_tool("https://example.com/mcp", "file_system", params)
        
        self.assertTrue("success" in result)
        self.assertTrue(result["success"])
        self.assertTrue("data" in result)
        self.assertTrue("Simulated content" in result["data"])
    
    async def test_stream_tool_invocation(self):
        """Test streaming tool invocation."""
        await self.client_adapter.connect_to_server("https://example.com/mcp")
        
        params = {
            "operation": "read",
            "path": "/test/file.txt"
        }
        
        updates = []
        async for update in self.client_adapter.stream_tool_invocation("https://example.com/mcp", "file_system", params):
            updates.append(update)
        
        self.assertTrue(len(updates) > 0)
        self.assertEqual(updates[0]["status"], "started")
        self.assertEqual(updates[-1]["status"], "completed")
        self.assertTrue("result" in updates[-1])
        self.assertTrue(updates[-1]["result"]["success"])
    
    async def test_handle_tool_discovery(self):
        """Test handling a tool discovery request."""
        request = {
            "id": "1",
            "method": "discover_tools"
        }
        
        response = await self.server_adapter.handle_tool_discovery(request)
        
        self.assertEqual(response["id"], "1")
        self.assertTrue("result" in response)
        self.assertTrue("server_info" in response["result"])
        self.assertTrue("tools" in response["result"])
        self.assertEqual(len(response["result"]["tools"]), 1)
        self.assertEqual(response["result"]["tools"][0]["name"], "file_system")
    
    async def test_handle_tool_invocation(self):
        """Test handling a tool invocation request."""
        request = {
            "id": "1",
            "method": "invoke_tool",
            "params": {
                "tool": "file_system",
                "params": {
                    "operation": "read",
                    "path": "/test/file.txt"
                },
                "session_id": "test_session_1"
            }
        }
        
        response = await self.server_adapter.handle_tool_invocation(request)
        
        self.assertEqual(response["id"], "1")
        self.assertTrue("result" in response)
        self.assertTrue("success" in response["result"])
        self.assertTrue(response["result"]["success"])
        self.assertTrue("data" in response["result"])
        self.assertTrue("test_session_1" in self.server_adapter.active_sessions)
    
    async def test_handle_streaming_invocation(self):
        """Test handling a streaming tool invocation request."""
        request = {
            "id": "1",
            "method": "stream_invoke_tool",
            "params": {
                "tool": "file_system",
                "params": {
                    "operation": "read",
                    "path": "/test/file.txt"
                },
                "session_id": "test_session_2"
            }
        }
        
        updates = []
        async for update in self.server_adapter.handle_streaming_invocation(request):
            updates.append(update)
        
        self.assertTrue(len(updates) > 0)
        self.assertEqual(updates[0]["id"], "1")
        self.assertEqual(updates[0]["status"], "started")
        self.assertEqual(updates[-1]["status"], "completed")
        self.assertTrue("result" in updates[-1])
        self.assertTrue(updates[-1]["result"]["success"])
        self.assertTrue("test_session_2" in self.server_adapter.active_sessions)

def run_async_tests():
    """Run asynchronous tests."""
    loop = asyncio.get_event_loop()
    
    # Google A2A tests
    a2a_test = TestGoogleA2AAdapter()
    a2a_test.setUp()
    loop.run_until_complete(a2a_test.async_setUp())
    
    # Run A2A tests
    loop.run_until_complete(a2a_test.test_client_connect())
    loop.run_until_complete(a2a_test.test_discover_capabilities())
    loop.run_until_complete(a2a_test.test_send_task())
    loop.run_until_complete(a2a_test.test_task_streaming())
    loop.run_until_complete(a2a_test.test_handle_task_send())
    loop.run_until_complete(a2a_test.test_handle_task_send_subscribe())
    loop.run_until_complete(a2a_test.test_handle_task_cancel())
    
    loop.run_until_complete(a2a_test.async_tearDown())
    
    # Anthropic MCP tests
    mcp_test = TestAnthropicMCPAdapter()
    mcp_test.setUp()
    loop.run_until_complete(mcp_test.async_setUp())
    
    # Run MCP tests
    loop.run_until_complete(mcp_test.test_client_connect())
    loop.run_until_complete(mcp_test.test_discover_tools())
    loop.run_until_complete(mcp_test.test_invoke_tool())
    loop.run_until_complete(mcp_test.test_stream_tool_invocation())
    loop.run_until_complete(mcp_test.test_handle_tool_discovery())
    loop.run_until_complete(mcp_test.test_handle_tool_invocation())
    loop.run_until_complete(mcp_test.test_handle_streaming_invocation())
    
    loop.run_until_complete(mcp_test.async_tearDown())

if __name__ == "__main__":
    # Run synchronous tests
    unittest.main(exit=False)
    
    # Run asynchronous tests
    run_async_tests()
    
    print("All tests completed successfully!")
