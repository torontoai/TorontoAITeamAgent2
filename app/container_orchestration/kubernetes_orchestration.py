"""
Kubernetes Orchestration for TORONTO AI TEAM AGENT.

This module provides functionality to deploy and manage containerized applications
across Kubernetes clusters, ensuring high availability and scalability.
"""

import os
import subprocess
import json
import yaml
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import tempfile
import base64
import time


class DeploymentType(Enum):
    """Enum representing types of Kubernetes deployments."""
    BASIC = "basic"
    STATEFUL = "stateful"
    DAEMON = "daemon"
    JOB = "job"
    CRONJOB = "cronjob"


class ServiceType(Enum):
    """Enum representing types of Kubernetes services."""
    CLUSTER_IP = "ClusterIP"
    NODE_PORT = "NodePort"
    LOAD_BALANCER = "LoadBalancer"
    EXTERNAL_NAME = "ExternalName"


class IngressType(Enum):
    """Enum representing types of Kubernetes ingress."""
    BASIC = "basic"
    TLS = "tls"
    PATH_BASED = "path-based"
    HOST_BASED = "host-based"


class KubernetesManager:
    """
    Manager class for Kubernetes orchestration.
    
    This class provides functionality to deploy and manage containerized applications
    across Kubernetes clusters, ensuring high availability and scalability.
    """
    
    def __init__(self, kubeconfig: str = None):
        """
        Initialize the Kubernetes Manager.
        
        Args:
            kubeconfig: Path to kubeconfig file (None for default)
        """
        self.kubeconfig = kubeconfig
        self._validate_kubectl_installation()
    
    def _validate_kubectl_installation(self):
        """
        Validate that kubectl is installed and accessible.
        
        Raises:
            RuntimeError: If kubectl is not installed or not accessible
        """
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"],
                capture_output=True,
                text=True,
                check=True,
                env=self._get_env()
            )
            print(f"kubectl is installed: {result.stdout.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise RuntimeError("kubectl is not installed or not accessible") from e
    
    def _get_env(self) -> Dict[str, str]:
        """
        Get environment variables for kubectl commands.
        
        Returns:
            Environment variables dictionary
        """
        env = os.environ.copy()
        if self.kubeconfig:
            env["KUBECONFIG"] = self.kubeconfig
        return env
    
    def _run_kubectl(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run a kubectl command.
        
        Args:
            args: Arguments for kubectl
            check: Whether to check for errors
            
        Returns:
            Completed process
        """
        cmd = ["kubectl"]
        cmd.extend(args)
        
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            env=self._get_env()
        )
    
    def get_current_context(self) -> str:
        """
        Get the current Kubernetes context.
        
        Returns:
            Current context name
        """
        result = self._run_kubectl(["config", "current-context"])
        return result.stdout.strip()
    
    def list_contexts(self) -> List[str]:
        """
        List available Kubernetes contexts.
        
        Returns:
            List of context names
        """
        result = self._run_kubectl(["config", "get-contexts", "-o", "name"])
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    
    def switch_context(self, context: str) -> None:
        """
        Switch to a different Kubernetes context.
        
        Args:
            context: Context to switch to
        """
        self._run_kubectl(["config", "use-context", context])
    
    def list_namespaces(self) -> List[str]:
        """
        List namespaces in the current cluster.
        
        Returns:
            List of namespace names
        """
        result = self._run_kubectl(["get", "namespaces", "-o", "jsonpath={.items[*].metadata.name}"])
        return result.stdout.strip().split()
    
    def create_namespace(self, name: str) -> None:
        """
        Create a namespace.
        
        Args:
            name: Name of the namespace
        """
        self._run_kubectl(["create", "namespace", name])
    
    def delete_namespace(self, name: str) -> None:
        """
        Delete a namespace.
        
        Args:
            name: Name of the namespace
        """
        self._run_kubectl(["delete", "namespace", name])
    
    def create_deployment(self, name: str, image: str, namespace: str = "default",
                         replicas: int = 1, deployment_type: DeploymentType = DeploymentType.BASIC,
                         ports: List[int] = None, env_vars: Dict[str, str] = None,
                         resources: Dict[str, Dict[str, str]] = None) -> str:
        """
        Create a Kubernetes deployment.
        
        Args:
            name: Name of the deployment
            image: Container image
            namespace: Namespace to deploy to
            replicas: Number of replicas
            deployment_type: Type of deployment
            ports: Container ports
            env_vars: Environment variables
            resources: Resource requests and limits
            
        Returns:
            Path to the created deployment YAML file
        """
        if ports is None:
            ports = [80]
        
        if env_vars is None:
            env_vars = {}
        
        if resources is None:
            resources = {
                "requests": {
                    "cpu": "100m",
                    "memory": "128Mi"
                },
                "limits": {
                    "cpu": "500m",
                    "memory": "512Mi"
                }
            }
        
        # Create deployment configuration
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": image,
                                "ports": [{"containerPort": port} for port in ports],
                                "resources": resources
                            }
                        ]
                    }
                }
            }
        }
        
        # Add environment variables if provided
        if env_vars:
            env_list = []
            for key, value in env_vars.items():
                env_list.append({
                    "name": key,
                    "value": value
                })
            deployment["spec"]["template"]["spec"]["containers"][0]["env"] = env_list
        
        # Modify deployment based on type
        if deployment_type == DeploymentType.STATEFUL:
            # Convert to StatefulSet
            deployment["apiVersion"] = "apps/v1"
            deployment["kind"] = "StatefulSet"
            deployment["spec"]["serviceName"] = name
        elif deployment_type == DeploymentType.DAEMON:
            # Convert to DaemonSet
            deployment["apiVersion"] = "apps/v1"
            deployment["kind"] = "DaemonSet"
            if "replicas" in deployment["spec"]:
                del deployment["spec"]["replicas"]
        elif deployment_type == DeploymentType.JOB:
            # Convert to Job
            deployment["apiVersion"] = "batch/v1"
            deployment["kind"] = "Job"
            if "replicas" in deployment["spec"]:
                del deployment["spec"]["replicas"]
            if "selector" in deployment["spec"]:
                del deployment["spec"]["selector"]
            deployment["spec"]["template"]["spec"]["restartPolicy"] = "Never"
            deployment["spec"]["backoffLimit"] = 4
        elif deployment_type == DeploymentType.CRONJOB:
            # Convert to CronJob
            deployment["apiVersion"] = "batch/v1"
            deployment["kind"] = "CronJob"
            job_template = {
                "spec": {
                    "template": deployment["spec"]["template"],
                    "backoffLimit": 4
                }
            }
            deployment["spec"] = {
                "schedule": "*/5 * * * *",  # Default: every 5 minutes
                "jobTemplate": job_template
            }
            if "replicas" in deployment["spec"]:
                del deployment["spec"]["replicas"]
            if "selector" in deployment["spec"]:
                del deployment["spec"]["selector"]
            deployment["spec"]["jobTemplate"]["spec"]["template"]["spec"]["restartPolicy"] = "Never"
        
        # Write deployment to YAML file
        deployment_file = f"{name}-deployment.yaml"
        with open(deployment_file, 'w') as f:
            yaml.dump(deployment, f)
        
        # Apply deployment
        self._run_kubectl(["apply", "-f", deployment_file])
        
        return deployment_file
    
    def create_service(self, name: str, namespace: str = "default",
                      service_type: ServiceType = ServiceType.CLUSTER_IP,
                      ports: List[Dict[str, int]] = None) -> str:
        """
        Create a Kubernetes service.
        
        Args:
            name: Name of the service
            namespace: Namespace to deploy to
            service_type: Type of service
            ports: Port mappings
            
        Returns:
            Path to the created service YAML file
        """
        if ports is None:
            ports = [{"port": 80, "targetPort": 80}]
        
        # Create service configuration
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "app": name
                },
                "type": service_type.value,
                "ports": []
            }
        }
        
        # Add ports
        for i, port_mapping in enumerate(ports):
            port_config = {
                "port": port_mapping["port"],
                "targetPort": port_mapping["targetPort"]
            }
            
            if "name" in port_mapping:
                port_config["name"] = port_mapping["name"]
            else:
                port_config["name"] = f"port-{i}"
            
            if service_type == ServiceType.NODE_PORT and "nodePort" in port_mapping:
                port_config["nodePort"] = port_mapping["nodePort"]
            
            service["spec"]["ports"].append(port_config)
        
        # Write service to YAML file
        service_file = f"{name}-service.yaml"
        with open(service_file, 'w') as f:
            yaml.dump(service, f)
        
        # Apply service
        self._run_kubectl(["apply", "-f", service_file])
        
        return service_file
    
    def create_ingress(self, name: str, namespace: str = "default",
                      ingress_type: IngressType = IngressType.BASIC,
                      rules: List[Dict[str, Any]] = None,
                      tls: List[Dict[str, Any]] = None) -> str:
        """
        Create a Kubernetes ingress.
        
        Args:
            name: Name of the ingress
            namespace: Namespace to deploy to
            ingress_type: Type of ingress
            rules: Ingress rules
            tls: TLS configuration
            
        Returns:
            Path to the created ingress YAML file
        """
        if rules is None:
            rules = [{
                "host": "example.com",
                "http": {
                    "paths": [{
                        "path": "/",
                        "pathType": "Prefix",
                        "backend": {
                            "service": {
                                "name": name,
                                "port": {
                                    "number": 80
                                }
                            }
                        }
                    }]
                }
            }]
        
        # Create ingress configuration
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "annotations": {}
            },
            "spec": {
                "rules": rules
            }
        }
        
        # Add TLS if needed
        if ingress_type == IngressType.TLS and tls:
            ingress["spec"]["tls"] = tls
        
        # Add annotations based on ingress type
        if ingress_type == IngressType.PATH_BASED:
            ingress["metadata"]["annotations"]["nginx.ingress.kubernetes.io/rewrite-target"] = "/$1"
        
        # Write ingress to YAML file
        ingress_file = f"{name}-ingress.yaml"
        with open(ingress_file, 'w') as f:
            yaml.dump(ingress, f)
        
        # Apply ingress
        self._run_kubectl(["apply", "-f", ingress_file])
        
        return ingress_file
    
    def create_config_map(self, name: str, namespace: str = "default",
                         data: Dict[str, str] = None, from_file: Dict[str, str] = None) -> str:
        """
        Create a Kubernetes ConfigMap.
        
        Args:
            name: Name of the ConfigMap
            namespace: Namespace to deploy to
            data: Key-value data
            from_file: File data
            
        Returns:
            Path to the created ConfigMap YAML file
        """
        if data is None and from_file is None:
            raise ValueError("Either data or from_file must be provided")
        
        # Create ConfigMap configuration
        config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name,
                "namespace": namespace
            }
        }
        
        if data:
            config_map["data"] = data
        
        # Write ConfigMap to YAML file
        config_map_file = f"{name}-configmap.yaml"
        with open(config_map_file, 'w') as f:
            yaml.dump(config_map, f)
        
        # Apply ConfigMap
        if from_file:
            cmd = ["create", "configmap", name, "--namespace", namespace]
            for key, file_path in from_file.items():
                cmd.extend(["--from-file", f"{key}={file_path}"])
            self._run_kubectl(cmd)
        else:
            self._run_kubectl(["apply", "-f", config_map_file])
        
        return config_map_file
    
    def create_secret(self, name: str, namespace: str = "default",
                     secret_type: str = "Opaque", data: Dict[str, str] = None) -> str:
        """
        Create a Kubernetes Secret.
        
        Args:
            name: Name of the Secret
            namespace: Namespace to deploy to
            secret_type: Type of Secret
            data: Key-value data
            
        Returns:
            Path to the created Secret YAML file
        """
        if data is None:
            raise ValueError("Data must be provided")
        
        # Encode data in base64
        encoded_data = {}
        for key, value in data.items():
            encoded_data[key] = base64.b64encode(value.encode()).decode()
        
        # Create Secret configuration
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "type": secret_type,
            "data": encoded_data
        }
        
        # Write Secret to YAML file
        secret_file = f"{name}-secret.yaml"
        with open(secret_file, 'w') as f:
            yaml.dump(secret, f)
        
        # Apply Secret
        self._run_kubectl(["apply", "-f", secret_file])
        
        return secret_file
    
    def create_persistent_volume(self, name: str, storage_class: str = "standard",
                               size: str = "1Gi", access_modes: List[str] = None) -> str:
        """
        Create a Kubernetes PersistentVolumeClaim.
        
        Args:
            name: Name of the PVC
            storage_class: Storage class
            size: Size of the volume
            access_modes: Access modes
            
        Returns:
            Path to the created PVC YAML file
        """
        if access_modes is None:
            access_modes = ["ReadWriteOnce"]
        
        # Create PVC configuration
        pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": name
            },
            "spec": {
                "accessModes": access_modes,
                "resources": {
                    "requests": {
                        "storage": size
                    }
                },
                "storageClassName": storage_class
            }
        }
        
        # Write PVC to YAML file
        pvc_file = f"{name}-pvc.yaml"
        with open(pvc_file, 'w') as f:
            yaml.dump(pvc, f)
        
        # Apply PVC
        self._run_kubectl(["apply", "-f", pvc_file])
        
        return pvc_file
    
    def get_pod_logs(self, pod_name: str, namespace: str = "default",
                   container: str = None, tail: int = None) -> str:
        """
        Get logs from a pod.
        
        Args:
            pod_name: Name of the pod
            namespace: Namespace of the pod
            container: Container name (if multiple containers)
            tail: Number of lines to show
            
        Returns:
            Pod logs
        """
        cmd = ["logs", pod_name, "--namespace", namespace]
        
        if container:
            cmd.extend(["--container", container])
        
        if tail:
            cmd.extend(["--tail", str(tail)])
        
        result = self._run_kubectl(cmd)
        return result.stdout
    
    def port_forward(self, resource: str, local_port: int, remote_port: int,
                   namespace: str = "default", resource_type: str = "pod") -> subprocess.Popen:
        """
        Forward a local port to a pod.
        
        Args:
            resource: Name of the resource
            local_port: Local port
            remote_port: Remote port
            namespace: Namespace of the resource
            resource_type: Type of resource
            
        Returns:
            Process object for the port-forward command
        """
        cmd = ["kubectl", "port-forward", f"{resource_type}/{resource}",
              f"{local_port}:{remote_port}", "--namespace", namespace]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._get_env()
        )
        
        # Wait a moment for the port-forward to establish
        time.sleep(2)
        
        return process
    
    def exec_command(self, pod_name: str, command: List[str], namespace: str = "default",
                   container: str = None) -> str:
        """
        Execute a command in a pod.
        
        Args:
            pod_name: Name of the pod
            command: Command to execute
            namespace: Namespace of the pod
            container: Container name (if multiple containers)
            
        Returns:
            Command output
        """
        cmd = ["exec", pod_name, "--namespace", namespace]
        
        if container:
            cmd.extend(["--container", container])
        
        cmd.extend(["--", *command])
        
        result = self._run_kubectl(cmd)
        return result.stdout
    
    def scale_deployment(self, name: str, replicas: int, namespace: str = "default") -> None:
        """
        Scale a deployment.
        
        Args:
            name: Name of the deployment
            replicas: Number of replicas
            namespace: Namespace of the deployment
        """
        self._run_kubectl(["scale", "deployment", name, "--replicas", str(replicas), "--namespace", namespace])
    
    def rollout_restart(self, resource_type: str, name: str, namespace: str = "default") -> None:
        """
        Restart a resource.
        
        Args:
            resource_type: Type of resource
            name: Name of the resource
            namespace: Namespace of the resource
        """
        self._run_kubectl(["rollout", "restart", resource_type, name, "--namespace", namespace])
    
    def rollout_status(self, resource_type: str, name: str, namespace: str = "default") -> str:
        """
        Get rollout status.
        
        Args:
            resource_type: Type of resource
            name: Name of the resource
            namespace: Namespace of the resource
            
        Returns:
            Rollout status
        """
        result = self._run_kubectl(["rollout", "status", resource_type, name, "--namespace", namespace])
        return result.stdout
    
    def rollout_history(self, resource_type: str, name: str, namespace: str = "default",
                      revision: int = None) -> str:
        """
        Get rollout history.
        
        Args:
            resource_type: Type of resource
            name: Name of the resource
            namespace: Namespace of the resource
            revision: Specific revision to show
            
        Returns:
            Rollout history
        """
        cmd = ["rollout", "history", resource_type, name, "--namespace", namespace]
        
        if revision:
            cmd.extend(["--revision", str(revision)])
        
        result = self._run_kubectl(cmd)
        return result.stdout
    
    def rollout_undo(self, resource_type: str, name: str, namespace: str = "default",
                   to_revision: int = None) -> None:
        """
        Undo a rollout.
        
        Args:
            resource_type: Type of resource
            name: Name of the resource
            namespace: Namespace of the resource
            to_revision: Revision to roll back to
        """
        cmd = ["rollout", "undo", resource_type, name, "--namespace", namespace]
        
        if to_revision:
            cmd.extend(["--to-revision", str(to_revision)])
        
        self._run_kubectl(cmd)
    
    def create_horizontal_pod_autoscaler(self, name: str, resource: str, namespace: str = "default",
                                       min_replicas: int = 1, max_replicas: int = 10,
                                       cpu_percent: int = 80) -> str:
        """
        Create a Horizontal Pod Autoscaler.
        
        Args:
            name: Name of the HPA
            resource: Resource to scale
            namespace: Namespace
            min_replicas: Minimum replicas
            max_replicas: Maximum replicas
            cpu_percent: CPU utilization target
            
        Returns:
            Path to the created HPA YAML file
        """
        # Create HPA configuration
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": resource
                },
                "minReplicas": min_replicas,
                "maxReplicas": max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": cpu_percent
                            }
                        }
                    }
                ]
            }
        }
        
        # Write HPA to YAML file
        hpa_file = f"{name}-hpa.yaml"
        with open(hpa_file, 'w') as f:
            yaml.dump(hpa, f)
        
        # Apply HPA
        self._run_kubectl(["apply", "-f", hpa_file])
        
        return hpa_file
    
    def create_network_policy(self, name: str, namespace: str = "default",
                            pod_selector: Dict[str, Dict[str, str]] = None,
                            ingress_rules: List[Dict[str, Any]] = None,
                            egress_rules: List[Dict[str, Any]] = None) -> str:
        """
        Create a Network Policy.
        
        Args:
            name: Name of the Network Policy
            namespace: Namespace
            pod_selector: Pod selector
            ingress_rules: Ingress rules
            egress_rules: Egress rules
            
        Returns:
            Path to the created Network Policy YAML file
        """
        if pod_selector is None:
            pod_selector = {"matchLabels": {"app": name}}
        
        # Create Network Policy configuration
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "podSelector": pod_selector,
                "policyTypes": []
            }
        }
        
        if ingress_rules:
            network_policy["spec"]["policyTypes"].append("Ingress")
            network_policy["spec"]["ingress"] = ingress_rules
        
        if egress_rules:
            network_policy["spec"]["policyTypes"].append("Egress")
            network_policy["spec"]["egress"] = egress_rules
        
        # Write Network Policy to YAML file
        network_policy_file = f"{name}-network-policy.yaml"
        with open(network_policy_file, 'w') as f:
            yaml.dump(network_policy, f)
        
        # Apply Network Policy
        self._run_kubectl(["apply", "-f", network_policy_file])
        
        return network_policy_file
    
    def create_role_and_binding(self, name: str, namespace: str = "default",
                              rules: List[Dict[str, Any]] = None,
                              service_account: str = None) -> Dict[str, str]:
        """
        Create a Role and RoleBinding.
        
        Args:
            name: Name of the Role and RoleBinding
            namespace: Namespace
            rules: Role rules
            service_account: Service account to bind to
            
        Returns:
            Dictionary with paths to the created YAML files
        """
        if rules is None:
            rules = [
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["get", "list", "watch"]
                }
            ]
        
        if service_account is None:
            service_account = "default"
        
        # Create Role configuration
        role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "rules": rules
        }
        
        # Create RoleBinding configuration
        role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": service_account,
                    "namespace": namespace
                }
            ],
            "roleRef": {
                "kind": "Role",
                "name": name,
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }
        
        # Write Role to YAML file
        role_file = f"{name}-role.yaml"
        with open(role_file, 'w') as f:
            yaml.dump(role, f)
        
        # Write RoleBinding to YAML file
        role_binding_file = f"{name}-role-binding.yaml"
        with open(role_binding_file, 'w') as f:
            yaml.dump(role_binding, f)
        
        # Apply Role and RoleBinding
        self._run_kubectl(["apply", "-f", role_file])
        self._run_kubectl(["apply", "-f", role_binding_file])
        
        return {
            "role": role_file,
            "role_binding": role_binding_file
        }
    
    def create_service_account(self, name: str, namespace: str = "default") -> str:
        """
        Create a Service Account.
        
        Args:
            name: Name of the Service Account
            namespace: Namespace
            
        Returns:
            Path to the created Service Account YAML file
        """
        # Create Service Account configuration
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": name,
                "namespace": namespace
            }
        }
        
        # Write Service Account to YAML file
        service_account_file = f"{name}-service-account.yaml"
        with open(service_account_file, 'w') as f:
            yaml.dump(service_account, f)
        
        # Apply Service Account
        self._run_kubectl(["apply", "-f", service_account_file])
        
        return service_account_file
    
    def create_complete_application(self, name: str, image: str, namespace: str = "default",
                                  replicas: int = 1, ports: List[int] = None,
                                  env_vars: Dict[str, str] = None,
                                  config_data: Dict[str, str] = None,
                                  secret_data: Dict[str, str] = None,
                                  expose: bool = True) -> Dict[str, str]:
        """
        Create a complete application with all necessary resources.
        
        Args:
            name: Name of the application
            image: Container image
            namespace: Namespace
            replicas: Number of replicas
            ports: Container ports
            env_vars: Environment variables
            config_data: ConfigMap data
            secret_data: Secret data
            expose: Whether to expose the application
            
        Returns:
            Dictionary with paths to the created YAML files
        """
        result = {}
        
        # Create namespace if it doesn't exist
        if namespace != "default":
            try:
                self.create_namespace(namespace)
                result["namespace"] = namespace
            except subprocess.CalledProcessError:
                # Namespace already exists
                pass
        
        # Create ConfigMap if needed
        if config_data:
            config_map_file = self.create_config_map(
                name=f"{name}-config",
                namespace=namespace,
                data=config_data
            )
            result["config_map"] = config_map_file
        
        # Create Secret if needed
        if secret_data:
            secret_file = self.create_secret(
                name=f"{name}-secret",
                namespace=namespace,
                data=secret_data
            )
            result["secret"] = secret_file
        
        # Create Deployment
        deployment_file = self.create_deployment(
            name=name,
            image=image,
            namespace=namespace,
            replicas=replicas,
            ports=ports,
            env_vars=env_vars
        )
        result["deployment"] = deployment_file
        
        # Create Service if needed
        if expose:
            service_file = self.create_service(
                name=name,
                namespace=namespace,
                ports=[{"port": port, "targetPort": port} for port in ports] if ports else None
            )
            result["service"] = service_file
        
        return result
    
    def deploy_from_kustomize(self, directory: str) -> None:
        """
        Deploy resources from a Kustomize directory.
        
        Args:
            directory: Path to the Kustomize directory
        """
        self._run_kubectl(["apply", "-k", directory])
    
    def deploy_from_helm_chart(self, release_name: str, chart: str, namespace: str = "default",
                             values_file: str = None, set_values: Dict[str, str] = None) -> None:
        """
        Deploy resources from a Helm chart.
        
        Args:
            release_name: Name of the Helm release
            chart: Helm chart to deploy
            namespace: Namespace
            values_file: Path to values file
            set_values: Values to set
        """
        cmd = ["helm", "upgrade", "--install", release_name, chart, "--namespace", namespace]
        
        if values_file:
            cmd.extend(["-f", values_file])
        
        if set_values:
            for key, value in set_values.items():
                cmd.extend(["--set", f"{key}={value}"])
        
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            env=self._get_env()
        )
    
    def get_resource_yaml(self, resource_type: str, name: str, namespace: str = "default") -> str:
        """
        Get YAML representation of a resource.
        
        Args:
            resource_type: Type of resource
            name: Name of the resource
            namespace: Namespace of the resource
            
        Returns:
            YAML representation of the resource
        """
        result = self._run_kubectl(["get", resource_type, name, "--namespace", namespace, "-o", "yaml"])
        return result.stdout
    
    def apply_yaml(self, yaml_content: str) -> None:
        """
        Apply YAML content.
        
        Args:
            yaml_content: YAML content to apply
        """
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp:
            tmp.write(yaml_content.encode())
            tmp_path = tmp.name
        
        try:
            self._run_kubectl(["apply", "-f", tmp_path])
        finally:
            os.remove(tmp_path)
    
    def delete_resource(self, resource_type: str, name: str, namespace: str = "default") -> None:
        """
        Delete a resource.
        
        Args:
            resource_type: Type of resource
            name: Name of the resource
            namespace: Namespace of the resource
        """
        self._run_kubectl(["delete", resource_type, name, "--namespace", namespace])
    
    def wait_for_resource(self, resource_type: str, name: str, condition: str,
                        namespace: str = "default", timeout: str = "60s") -> bool:
        """
        Wait for a resource to reach a condition.
        
        Args:
            resource_type: Type of resource
            name: Name of the resource
            condition: Condition to wait for
            namespace: Namespace of the resource
            timeout: Timeout
            
        Returns:
            Whether the condition was met
        """
        try:
            self._run_kubectl([
                "wait", f"{resource_type}/{name}",
                "--for", f"condition={condition}",
                "--namespace", namespace,
                "--timeout", timeout
            ])
            return True
        except subprocess.CalledProcessError:
            return False
