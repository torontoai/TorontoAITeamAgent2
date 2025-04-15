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

This module provides tools for queue operations."""

from typing import Dict, Any, List, Optional, Callable
import os
import asyncio
import queue
import threading
import time
import uuid
from ..base import BaseTool, ToolResult

class QueueTool(BaseTool):
    """Tool for managing queues and message passing between processes."""
    
    name = "queue"
    description = "Provides capabilities for managing queues and message passing between processes."
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Queue tool.
        
        Args:
            config: Tool configuration with optional settings"""
        super().__init__(config)
        self.queues = {}  # Store active queues
        self.max_queues = self.config.get("max_queues", 10)
        self.default_timeout = self.config.get("default_timeout", 5)  # Default timeout in seconds
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the Queue tool with the given parameters.
        
        Args:
            params: Tool parameters including:
                - operation: Operation to perform (create, put, get, list, delete)
                - queue_id: Identifier for the queue
                - item: Item to put in the queue (for put operation)
                - timeout: Timeout for get operation (optional)
                - maxsize: Maximum size of the queue (for create operation)
                
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
                return await self._create_queue(params)
            elif operation == "put":
                return await self._put_item(params)
            elif operation == "get":
                return await self._get_item(params)
            elif operation == "list":
                return await self._list_queues(params)
            elif operation == "delete":
                return await self._delete_queue(params)
            elif operation == "size":
                return await self._get_queue_size(params)
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
    
    async def _create_queue(self, params: Dict[str, Any]) -> ToolResult:
        """
        Create a new queue.
        
        Args:
            params: Parameters for creating a queue
            
        Returns:
            Tool execution result
        """
        queue_id = params.get("queue_id", str(uuid.uuid4()))
        maxsize = params.get("maxsize", 0)  # 0 means unlimited
        
        # Check if queue already exists
        if queue_id in self.queues:
            return ToolResult(
                success=False,
                data={},
                error=f"Queue with ID '{queue_id}' already exists"
            )
        
        # Check if max queues reached
        if len(self.queues) >= self.max_queues:
            return ToolResult(
                success=False,
                data={},
                error=f"Maximum number of queues ({self.max_queues}) reached"
            )
        
        # Create queue
        self.queues[queue_id] = {
            "queue": queue.Queue(maxsize=maxsize),
            "create_time": time.time(),
            "maxsize": maxsize,
            "item_count": 0,
            "total_items_processed": 0
        }
        
        return ToolResult(
            success=True,
            data={
                "queue_id": queue_id,
                "maxsize": maxsize,
                "status": "created"
            }
        )
    
    async def _put_item(self, params: Dict[str, Any]) -> ToolResult:
        """
        Put an item in a queue.
        
        Args:
            params: Parameters for putting an item in a queue
            
        Returns:
            Tool execution result
        """
        queue_id = params.get("queue_id")
        item = params.get("item")
        block = params.get("block", True)
        timeout = params.get("timeout", None)
        
        if not queue_id:
            return ToolResult(
                success=False,
                data={},
                error="Queue ID parameter is required for put operation"
            )
        
        if item is None:
            return ToolResult(
                success=False,
                data={},
                error="Item parameter is required for put operation"
            )
        
        # Check if queue exists
        if queue_id not in self.queues:
            return ToolResult(
                success=False,
                data={},
                error=f"Queue with ID '{queue_id}' does not exist"
            )
        
        queue_data = self.queues[queue_id]
        q = queue_data["queue"]
        
        # Put item in queue
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: q.put(item, block=block, timeout=timeout)
            )
            
            # Update queue data
            queue_data["item_count"] += 1
            
            return ToolResult(
                success=True,
                data={
                    "queue_id": queue_id,
                    "item": item,
                    "status": "added"
                }
            )
        except queue.Full:
            return ToolResult(
                success=False,
                data={
                    "queue_id": queue_id,
                    "item": item,
                    "status": "full"
                },
                error="Queue is full"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to put item in queue: {str(e)}"
            )
    
    async def _get_item(self, params: Dict[str, Any]) -> ToolResult:
        """
        Get an item from a queue.
        
        Args:
            params: Parameters for getting an item from a queue
            
        Returns:
            Tool execution result
        """
        queue_id = params.get("queue_id")
        block = params.get("block", True)
        timeout = params.get("timeout", self.default_timeout)
        
        if not queue_id:
            return ToolResult(
                success=False,
                data={},
                error="Queue ID parameter is required for get operation"
            )
        
        # Check if queue exists
        if queue_id not in self.queues:
            return ToolResult(
                success=False,
                data={},
                error=f"Queue with ID '{queue_id}' does not exist"
            )
        
        queue_data = self.queues[queue_id]
        q = queue_data["queue"]
        
        # Get item from queue
        try:
            loop = asyncio.get_event_loop()
            item = await loop.run_in_executor(
                None,
                lambda: q.get(block=block, timeout=timeout)
            )
            
            # Update queue data
            queue_data["item_count"] -= 1
            queue_data["total_items_processed"] += 1
            
            # Mark task as done
            q.task_done()
            
            return ToolResult(
                success=True,
                data={
                    "queue_id": queue_id,
                    "item": item,
                    "status": "retrieved"
                }
            )
        except queue.Empty:
            return ToolResult(
                success=False,
                data={
                    "queue_id": queue_id,
                    "status": "empty"
                },
                error="Queue is empty"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Failed to get item from queue: {str(e)}"
            )
    
    async def _list_queues(self, params: Dict[str, Any]) -> ToolResult:
        """
        List all queues.
        
        Args:
            params: Parameters for listing queues
            
        Returns:
            Tool execution result
        """
        queues = []
        
        for queue_id, queue_data in self.queues.items():
            q = queue_data["queue"]
            
            queues.append({
                "queue_id": queue_id,
                "size": queue_data["item_count"],
                "maxsize": queue_data["maxsize"],
                "total_items_processed": queue_data["total_items_processed"],
                "create_time": queue_data["create_time"],
                "is_empty": q.empty(),
                "is_full": q.full()
            })
        
        return ToolResult(
            success=True,
            data={
                "queues": queues,
                "count": len(queues)
            }
        )
    
    async def _delete_queue(self, params: Dict[str, Any]) -> ToolResult:
        """
        Delete a queue.
        
        Args:
            params: Parameters for deleting a queue
            
        Returns:
            Tool execution result
        """
        queue_id = params.get("queue_id")
        
        if not queue_id:
            return ToolResult(
                success=False,
                data={},
                error="Queue ID parameter is required for delete operation"
            )
        
        # Check if queue exists
        if queue_id not in self.queues:
            return ToolResult(
                success=False,
                data={},
                error=f"Queue with ID '{queue_id}' does not exist"
            )
        
        # Delete queue
        queue_data = self.queues.pop(queue_id)
        
        return ToolResult(
            success=True,
            data={
                "queue_id": queue_id,
                "status": "deleted",
                "total_items_processed": queue_data["total_items_processed"]
            }
        )
    
    async def _get_queue_size(self, params: Dict[str, Any]) -> ToolResult:
        """
        Get the size of a queue.
        
        Args:
            params: Parameters for getting queue size
            
        Returns:
            Tool execution result
        """
        queue_id = params.get("queue_id")
        
        if not queue_id:
            return ToolResult(
                success=False,
                data={},
                error="Queue ID parameter is required for size operation"
            )
        
        # Check if queue exists
        if queue_id not in self.queues:
            return ToolResult(
                success=False,
                data={},
                error=f"Queue with ID '{queue_id}' does not exist"
            )
        
        queue_data = self.queues[queue_id]
        q = queue_data["queue"]
        
        return ToolResult(
            success=True,
            data={
                "queue_id": queue_id,
                "size": queue_data["item_count"],
                "maxsize": queue_data["maxsize"],
                "is_empty": q.empty(),
                "is_full": q.full(),
                "total_items_processed": queue_data["total_items_processed"]
            }
        )
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities provided by this tool.
        
        Returns:
            List of capability descriptions"""
        return [
            "Create and manage queues for inter-process communication",
            "Add items to queues for processing",
            "Retrieve items from queues for consumption",
            "Monitor queue sizes and status",
            "Facilitate message passing between components"
        ]
