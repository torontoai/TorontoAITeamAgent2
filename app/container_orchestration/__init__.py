"""
Container Orchestration initialization module.

This module initializes the container orchestration components for the TORONTO AI TEAM AGENT.
"""

from .docker_integration import (
    DockerManager,
    DockerfileTemplate,
    DockerComposeServiceType
)

try:
    from .kubernetes_orchestration import (
        KubernetesManager,
        DeploymentType,
        ServiceType,
        IngressType
    )
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False

__all__ = [
    'DockerManager',
    'DockerfileTemplate',
    'DockerComposeServiceType'
]

if KUBERNETES_AVAILABLE:
    __all__.extend([
        'KubernetesManager',
        'DeploymentType',
        'ServiceType',
        'IngressType'
    ])
