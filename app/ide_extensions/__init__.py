"""
IDE Extensions initialization module.

This module initializes the IDE extensions components for the TORONTO AI TEAM AGENT.
"""

from .ide_extensions import (
    IDEExtensionManager,
    VSCodeExtensionManager,
    JetBrainsPluginManager,
    IDEType
)

__all__ = [
    'IDEExtensionManager',
    'VSCodeExtensionManager',
    'JetBrainsPluginManager',
    'IDEType'
]
