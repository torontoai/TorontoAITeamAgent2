# TORONTO AI TEAM AGENT - PROPRIETARY
#
# Copyright (c) 2025 TORONTO AI
# Creator: David Tadeusz Chudak
# All Rights Reserved
#
# This file is part of the TORONTO AI TEAM AGENT software.
#
# This software is based on OpenManus (Copyright (c) 2025 manna_and_poem),
# which is licensed under the MIT License. The original license is included
# in the LICENSE file in the root directory of this project.
#
# This software has been substantially modified with proprietary enhancements.


"""UI/Utilities tools for TorontoAITeamAgent Team AI.

This module provides tools for creating web interfaces using Gradio."""

from typing import Dict, Any, List, Optional, Callable
import os
import asyncio
import tempfile
import json
from ..base import BaseTool, ToolResult

class GradioTool(BaseTool):
    """Tool for creating web interfaces using Gradio."""
    
    name = "gradio"
    description = "Provides capabilities for creating web interfaces using Gradio."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Gradio tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.timeout = self.config.get("timeout", 60)  # Default timeout in seconds
        self.interfaces = {}  # Store active interfaces
        
        # Import here to avoid dependency issues
        try:
            import gradio as gr
            self.gr = gr
        except ImportError:
            raise ImportError("Gradio is not installed. Install it with 'pip install gradio>=3.50.0'")
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Gradio tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (create, update, close)
                - interface_id: Identifier for the interface
                - components: List of component definitions for create operation
                - function: Function to be called when interface is used
                - title: Title of the interface
                - description: Description of the interface
                - theme: Theme for the interface
                - share: Whether to create a public link
                - auth: Authentication credentials
                - port: Port to run the interface on
                
        Returns:
            Tool execution result
        """
        operation = params.get("operation")
        if not operation:
            return ToolResult(
                success=False,
                data={},
                error="Operation parameter is required"
            )
            
        try:
            if operation == "create":
                return await self._create_interface(params)
            elif operation == "update":
                return await self._update_interface(params)
            elif operation == "close":
                return await self._close_interface(params)
            elif operation == "list":
                return await self._list_interfaces(params)
            else:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unsupported operation: {operation}"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=str(e)
            )
    
    async def _create_interface(self, params: Dict[str, Any]) -> ToolResult:
        """
        Create a Gradio interface.
        
        Args:
            params: Parameters for creating an interface
            
        Returns:
            Tool execution result
        """
        interface_id = params.get("interface_id")
        components_in = params.get("components_in", [])
        components_out = params.get("components_out", [])
        function_code = params.get("function")
        title = params.get("title", "Gradio Interface")
        description = params.get("description", "")
        theme = params.get("theme", "default")
        share = params.get("share", False)
        auth = params.get("auth")
        port = params.get("port", None)
        
        if not interface_id:
            return ToolResult(
                success=False,
                data={},
                error="Interface ID parameter is required for create operation"
            )
            
        if not function_code:
            return ToolResult(
                success=False,
                data={},
                error="Function parameter is required for create operation"
            )
            
        if not components_in or not components_out:
            return ToolResult(
                success=False,
                data={},
                error="Components parameters are required for create operation"
            )
        
        # Check if interface already exists
        if interface_id in self.interfaces:
            return ToolResult(
                success=False,
                data={},
                error=f"Interface with ID '{interface_id}' already exists"
            )
        
        # Create function from code
        try:
            # Create a namespace for the function
            namespace = {}
            exec(function_code, namespace)
            
            # Get the function from the namespace
            function_name = None
            for name, obj in namespace.items():
                if callable(obj) and name != "__builtins__":
                    function_name = name
                    break
            
            if not function_name:
                return ToolResult(
                    success=False,
                    data={},
                    error="No function found in the provided code"
                )
            
            function = namespace[function_name]
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to create function from code: {str(e)}"
            )
        
        # Create input components
        inputs = []
        for comp in components_in:
            comp_type = comp.get("type")
            comp_params = comp.get("params", {})
            
            if not hasattr(self.gr, comp_type):
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unknown component type: {comp_type}"
                )
            
            try:
                component_class = getattr(self.gr, comp_type)
                inputs.append(component_class(**comp_params))
            except Exception as e:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Failed to create input component '{comp_type}': {str(e)}"
                )
        
        # Create output components
        outputs = []
        for comp in components_out:
            comp_type = comp.get("type")
            comp_params = comp.get("params", {})
            
            if not hasattr(self.gr, comp_type):
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unknown component type: {comp_type}"
                )
            
            try:
                component_class = getattr(self.gr, comp_type)
                outputs.append(component_class(**comp_params))
            except Exception as e:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Failed to create output component '{comp_type}': {str(e)}"
                )
        
        # Create interface
        try:
            interface = self.gr.Interface(
                fn=function,
                inputs=inputs,
                outputs=outputs,
                title=title,
                description=description,
                theme=theme,
                auth=auth
            )
            
            # Launch interface in a separate thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: interface.launch(share=share, prevent_thread_lock=True, server_port=port)
            )
            
            # Store interface
            self.interfaces[interface_id] = {
                "interface": interface,
                "local_url": result.local_url,
                "share_url": result.share_url if share else None,
                "function": function,
                "function_code": function_code
            }
            
            return ToolResult(
                success=True,
                data={
                    "interface_id": interface_id,
                    "local_url": result.local_url,
                    "share_url": result.share_url if share else None,
                    "title": title,
                    "description": description
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to create interface: {str(e)}"
            )
    
    async def _update_interface(self, params: Dict[str, Any]) -> ToolResult:
        """
        Update a Gradio interface.
        
        Args:
            params: Parameters for updating an interface
            
        Returns:
            Tool execution result
        """
        interface_id = params.get("interface_id")
        function_code = params.get("function")
        title = params.get("title")
        description = params.get("description")
        
        if not interface_id:
            return ToolResult(
                success=False,
                data={},
                error="Interface ID parameter is required for update operation"
            )
        
        # Check if interface exists
        if interface_id not in self.interfaces:
            return ToolResult(
                success=False,
                data={},
                error=f"Interface with ID '{interface_id}' does not exist"
            )
        
        interface_data = self.interfaces[interface_id]
        interface = interface_data["interface"]
        
        # Update function if provided
        if function_code:
            try:
                # Create a namespace for the function
                namespace = {}
                exec(function_code, namespace)
                
                # Get the function from the namespace
                function_name = None
                for name, obj in namespace.items():
                    if callable(obj) and name != "__builtins__":
                        function_name = name
                        break
                
                if not function_name:
                    return ToolResult(
                        success=False,
                        data={},
                        error="No function found in the provided code"
                    )
                
                function = namespace[function_name]
                
                # Update function
                interface.fn = function
                interface_data["function"] = function
                interface_data["function_code"] = function_code
            except Exception as e:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Failed to update function: {str(e)}"
                )
        
        # Update title if provided
        if title:
            interface.title = title
        
        # Update description if provided
        if description:
            interface.description = description
        
        return ToolResult(
            success=True,
            data={
                "interface_id": interface_id,
                "local_url": interface_data["local_url"],
                "share_url": interface_data["share_url"],
                "title": interface.title,
                "description": interface.description
            }
        )
    
    async def _close_interface(self, params: Dict[str, Any]) -> ToolResult:
        """
        Close a Gradio interface.
        
        Args:
            params: Parameters for closing an interface
            
        Returns:
            Tool execution result
        """
        interface_id = params.get("interface_id")
        
        if not interface_id:
            return ToolResult(
                success=False,
                data={},
                error="Interface ID parameter is required for close operation"
            )
        
        # Check if interface exists
        if interface_id not in self.interfaces:
            return ToolResult(
                success=False,
                data={},
                error=f"Interface with ID '{interface_id}' does not exist"
            )
        
        interface_data = self.interfaces[interface_id]
        interface = interface_data["interface"]
        
        # Close interface
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: interface.close()
            )
            
            # Remove interface from storage
            del self.interfaces[interface_id]
            
            return ToolResult(
                success=True,
                data={
                    "interface_id": interface_id,
                    "closed": True
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to close interface: {str(e)}"
            )
    
    async def _list_interfaces(self, params: Dict[str, Any]) -> ToolResult:
        """
        List active Gradio interfaces.
        
        Args:
            params: Parameters for listing interfaces
            
        Returns:
            Tool execution result
        """
        interfaces = []
        
        for interface_id, interface_data in self.interfaces.items():
            interfaces.append({
                "interface_id": interface_id,
                "local_url": interface_data["local_url"],
                "share_url": interface_data["share_url"],
                "title": interface_data["interface"].title,
                "description": interface_data["interface"].description
            })
        
        return ToolResult(
            success=True,
            data={
                "interfaces": interfaces,
                "count": len(interfaces)
            }
        )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Create web interfaces for Python functions",
            "Update existing web interfaces",
            "Close web interfaces",
            "List active web interfaces",
            "Create shareable links for web interfaces"
        ]
