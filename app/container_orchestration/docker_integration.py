"""
Docker Integration for TORONTO AI TEAM AGENT.

This module provides functionality to build, test, and deploy containerized applications
with proper isolation and dependency management using Docker.
"""

import os
import subprocess
import json
import yaml
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import tempfile
import shutil


class DockerfileTemplate(Enum):
    """Enum representing predefined Dockerfile templates."""
    PYTHON = "python"
    NODE = "node"
    JAVA = "java"
    GO = "go"
    RUBY = "ruby"
    CUSTOM = "custom"


class DockerComposeServiceType(Enum):
    """Enum representing types of services in Docker Compose."""
    WEB = "web"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    WORKER = "worker"
    CUSTOM = "custom"


class DockerManager:
    """
    Manager class for Docker integration.
    
    This class provides functionality to build, test, and deploy containerized applications
    with proper isolation and dependency management using Docker.
    """
    
    def __init__(self, project_dir: str):
        """
        Initialize the Docker Manager.
        
        Args:
            project_dir: Path to the project directory
        """
        self.project_dir = project_dir
        self._validate_docker_installation()
    
    def _validate_docker_installation(self):
        """
        Validate that Docker is installed and accessible.
        
        Raises:
            RuntimeError: If Docker is not installed or not accessible
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Docker is installed: {result.stdout.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise RuntimeError("Docker is not installed or not accessible") from e
    
    def create_dockerfile(self, template: DockerfileTemplate, options: Dict[str, Any] = None) -> str:
        """
        Create a Dockerfile based on a template.
        
        Args:
            template: The Dockerfile template to use
            options: Additional options for customizing the Dockerfile
            
        Returns:
            Path to the created Dockerfile
        """
        if options is None:
            options = {}
        
        dockerfile_path = os.path.join(self.project_dir, "Dockerfile")
        
        if template == DockerfileTemplate.PYTHON:
            content = self._create_python_dockerfile(options)
        elif template == DockerfileTemplate.NODE:
            content = self._create_node_dockerfile(options)
        elif template == DockerfileTemplate.JAVA:
            content = self._create_java_dockerfile(options)
        elif template == DockerfileTemplate.GO:
            content = self._create_go_dockerfile(options)
        elif template == DockerfileTemplate.RUBY:
            content = self._create_ruby_dockerfile(options)
        elif template == DockerfileTemplate.CUSTOM:
            if "content" not in options:
                raise ValueError("Custom Dockerfile template requires 'content' option")
            content = options["content"]
        else:
            raise ValueError(f"Unsupported Dockerfile template: {template}")
        
        with open(dockerfile_path, 'w') as f:
            f.write(content)
        
        return dockerfile_path
    
    def _create_python_dockerfile(self, options: Dict[str, Any]) -> str:
        """
        Create a Dockerfile for a Python application.
        
        Args:
            options: Options for customizing the Dockerfile
            
        Returns:
            Dockerfile content as a string
        """
        python_version = options.get("python_version", "3.9")
        app_port = options.get("port", 8000)
        include_dev_dependencies = options.get("include_dev_dependencies", False)
        
        content = f"""FROM python:{python_version}-slim

WORKDIR /app

COPY requirements.txt .
"""
        
        if include_dev_dependencies and os.path.exists(os.path.join(self.project_dir, "requirements-dev.txt")):
            content += "COPY requirements-dev.txt .\n"
            content += "RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt\n"
        else:
            content += "RUN pip install --no-cache-dir -r requirements.txt\n"
        
        content += """
COPY . .

EXPOSE {port}

CMD ["python", "app.py"]
""".format(port=app_port)
        
        return content
    
    def _create_node_dockerfile(self, options: Dict[str, Any]) -> str:
        """
        Create a Dockerfile for a Node.js application.
        
        Args:
            options: Options for customizing the Dockerfile
            
        Returns:
            Dockerfile content as a string
        """
        node_version = options.get("node_version", "16")
        app_port = options.get("port", 3000)
        use_yarn = options.get("use_yarn", False)
        
        content = f"""FROM node:{node_version}-slim

WORKDIR /app

COPY package*.json ./
"""
        
        if use_yarn:
            content += """
RUN yarn install
"""
        else:
            content += """
RUN npm ci
"""
        
        content += """
COPY . .

EXPOSE {port}

CMD ["npm", "start"]
""".format(port=app_port)
        
        return content
    
    def _create_java_dockerfile(self, options: Dict[str, Any]) -> str:
        """
        Create a Dockerfile for a Java application.
        
        Args:
            options: Options for customizing the Dockerfile
            
        Returns:
            Dockerfile content as a string
        """
        java_version = options.get("java_version", "11")
        app_port = options.get("port", 8080)
        build_tool = options.get("build_tool", "maven")
        
        if build_tool.lower() == "maven":
            content = f"""FROM maven:{java_version}-jdk-slim AS build

WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN mvn package -DskipTests

FROM openjdk:{java_version}-jre-slim

WORKDIR /app

COPY --from=build /app/target/*.jar app.jar

EXPOSE {app_port}

CMD ["java", "-jar", "app.jar"]
"""
        elif build_tool.lower() == "gradle":
            content = f"""FROM gradle:{java_version}-jdk AS build

WORKDIR /app

COPY build.gradle .
COPY src ./src

RUN gradle build --no-daemon -x test

FROM openjdk:{java_version}-jre-slim

WORKDIR /app

COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE {app_port}

CMD ["java", "-jar", "app.jar"]
"""
        else:
            raise ValueError(f"Unsupported build tool: {build_tool}")
        
        return content
    
    def _create_go_dockerfile(self, options: Dict[str, Any]) -> str:
        """
        Create a Dockerfile for a Go application.
        
        Args:
            options: Options for customizing the Dockerfile
            
        Returns:
            Dockerfile content as a string
        """
        go_version = options.get("go_version", "1.17")
        app_port = options.get("port", 8080)
        
        content = f"""FROM golang:{go_version}-alpine AS build

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server

FROM alpine:latest

WORKDIR /app

COPY --from=build /app/server .

EXPOSE {app_port}

CMD ["./server"]
"""
        
        return content
    
    def _create_ruby_dockerfile(self, options: Dict[str, Any]) -> str:
        """
        Create a Dockerfile for a Ruby application.
        
        Args:
            options: Options for customizing the Dockerfile
            
        Returns:
            Dockerfile content as a string
        """
        ruby_version = options.get("ruby_version", "3.0")
        app_port = options.get("port", 3000)
        
        content = f"""FROM ruby:{ruby_version}-slim

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

EXPOSE {app_port}

CMD ["ruby", "app.rb"]
"""
        
        return content
    
    def create_docker_compose(self, services: List[Dict[str, Any]]) -> str:
        """
        Create a Docker Compose file with specified services.
        
        Args:
            services: List of service configurations
            
        Returns:
            Path to the created Docker Compose file
        """
        compose_path = os.path.join(self.project_dir, "docker-compose.yml")
        
        compose_config = {
            "version": "3",
            "services": {}
        }
        
        for service in services:
            service_name = service.get("name")
            service_type = service.get("type", DockerComposeServiceType.CUSTOM)
            
            if service_type == DockerComposeServiceType.WEB:
                compose_config["services"][service_name] = self._create_web_service(service)
            elif service_type == DockerComposeServiceType.DATABASE:
                compose_config["services"][service_name] = self._create_database_service(service)
            elif service_type == DockerComposeServiceType.CACHE:
                compose_config["services"][service_name] = self._create_cache_service(service)
            elif service_type == DockerComposeServiceType.QUEUE:
                compose_config["services"][service_name] = self._create_queue_service(service)
            elif service_type == DockerComposeServiceType.WORKER:
                compose_config["services"][service_name] = self._create_worker_service(service)
            elif service_type == DockerComposeServiceType.CUSTOM:
                compose_config["services"][service_name] = service.get("config", {})
            else:
                raise ValueError(f"Unsupported service type: {service_type}")
        
        with open(compose_path, 'w') as f:
            yaml.dump(compose_config, f, sort_keys=False)
        
        return compose_path
    
    def _create_web_service(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a web service configuration for Docker Compose.
        
        Args:
            service: Service configuration
            
        Returns:
            Docker Compose service configuration
        """
        config = {
            "build": {
                "context": ".",
                "dockerfile": service.get("dockerfile", "Dockerfile")
            },
            "ports": [f"{service.get('port', 8000)}:{service.get('container_port', 8000)}"],
            "environment": service.get("environment", []),
            "depends_on": service.get("depends_on", [])
        }
        
        if "volumes" in service:
            config["volumes"] = service["volumes"]
        
        return config
    
    def _create_database_service(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a database service configuration for Docker Compose.
        
        Args:
            service: Service configuration
            
        Returns:
            Docker Compose service configuration
        """
        db_type = service.get("db_type", "postgres")
        
        if db_type == "postgres":
            config = {
                "image": service.get("image", "postgres:13"),
                "environment": {
                    "POSTGRES_USER": service.get("user", "postgres"),
                    "POSTGRES_PASSWORD": service.get("password", "postgres"),
                    "POSTGRES_DB": service.get("db_name", "postgres")
                },
                "ports": [f"{service.get('port', 5432)}:5432"],
                "volumes": [
                    f"{service.get('name')}-data:/var/lib/postgresql/data"
                ]
            }
        elif db_type == "mysql":
            config = {
                "image": service.get("image", "mysql:8"),
                "environment": {
                    "MYSQL_ROOT_PASSWORD": service.get("root_password", "root"),
                    "MYSQL_DATABASE": service.get("db_name", "mysql"),
                    "MYSQL_USER": service.get("user", "mysql"),
                    "MYSQL_PASSWORD": service.get("password", "mysql")
                },
                "ports": [f"{service.get('port', 3306)}:3306"],
                "volumes": [
                    f"{service.get('name')}-data:/var/lib/mysql"
                ]
            }
        elif db_type == "mongodb":
            config = {
                "image": service.get("image", "mongo:4"),
                "environment": {
                    "MONGO_INITDB_ROOT_USERNAME": service.get("user", "mongo"),
                    "MONGO_INITDB_ROOT_PASSWORD": service.get("password", "mongo"),
                    "MONGO_INITDB_DATABASE": service.get("db_name", "mongo")
                },
                "ports": [f"{service.get('port', 27017)}:27017"],
                "volumes": [
                    f"{service.get('name')}-data:/data/db"
                ]
            }
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        return config
    
    def _create_cache_service(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a cache service configuration for Docker Compose.
        
        Args:
            service: Service configuration
            
        Returns:
            Docker Compose service configuration
        """
        cache_type = service.get("cache_type", "redis")
        
        if cache_type == "redis":
            config = {
                "image": service.get("image", "redis:6"),
                "ports": [f"{service.get('port', 6379)}:6379"]
            }
            
            if "command" in service:
                config["command"] = service["command"]
            
            if "volumes" in service:
                config["volumes"] = service["volumes"]
        elif cache_type == "memcached":
            config = {
                "image": service.get("image", "memcached:1"),
                "ports": [f"{service.get('port', 11211)}:11211"]
            }
        else:
            raise ValueError(f"Unsupported cache type: {cache_type}")
        
        return config
    
    def _create_queue_service(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a queue service configuration for Docker Compose.
        
        Args:
            service: Service configuration
            
        Returns:
            Docker Compose service configuration
        """
        queue_type = service.get("queue_type", "rabbitmq")
        
        if queue_type == "rabbitmq":
            config = {
                "image": service.get("image", "rabbitmq:3-management"),
                "ports": [
                    f"{service.get('port', 5672)}:5672",
                    f"{service.get('management_port', 15672)}:15672"
                ]
            }
        elif queue_type == "kafka":
            config = {
                "image": service.get("image", "confluentinc/cp-kafka:latest"),
                "ports": [f"{service.get('port', 9092)}:9092"],
                "environment": {
                    "KAFKA_ADVERTISED_LISTENERS": "PLAINTEXT://localhost:9092",
                    "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": "1"
                },
                "depends_on": ["zookeeper"]
            }
            
            # Add Zookeeper service if not already defined
            if "zookeeper" not in service.get("depends_on", []):
                config["depends_on"] = ["zookeeper"]
        else:
            raise ValueError(f"Unsupported queue type: {queue_type}")
        
        return config
    
    def _create_worker_service(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a worker service configuration for Docker Compose.
        
        Args:
            service: Service configuration
            
        Returns:
            Docker Compose service configuration
        """
        config = {
            "build": {
                "context": ".",
                "dockerfile": service.get("dockerfile", "Dockerfile")
            },
            "command": service.get("command", "worker"),
            "depends_on": service.get("depends_on", [])
        }
        
        if "volumes" in service:
            config["volumes"] = service["volumes"]
        
        if "environment" in service:
            config["environment"] = service["environment"]
        
        return config
    
    def build_image(self, tag: str, dockerfile: str = "Dockerfile", build_args: Dict[str, str] = None) -> str:
        """
        Build a Docker image.
        
        Args:
            tag: Tag for the built image
            dockerfile: Path to the Dockerfile
            build_args: Build arguments
            
        Returns:
            ID of the built image
        """
        cmd = ["docker", "build", "-t", tag, "-f", dockerfile, "."]
        
        if build_args:
            for key, value in build_args.items():
                cmd.extend(["--build-arg", f"{key}={value}"])
        
        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract image ID from the output
        for line in result.stdout.splitlines():
            if "Successfully built" in line:
                image_id = line.split("Successfully built")[1].strip()
                return image_id
        
        return tag
    
    def run_container(self, image: str, name: str = None, ports: List[str] = None, 
                     volumes: List[str] = None, environment: Dict[str, str] = None,
                     command: str = None, detach: bool = True) -> str:
        """
        Run a Docker container.
        
        Args:
            image: Image to run
            name: Name for the container
            ports: Port mappings
            volumes: Volume mappings
            environment: Environment variables
            command: Command to run
            detach: Whether to run in detached mode
            
        Returns:
            ID of the created container
        """
        cmd = ["docker", "run"]
        
        if detach:
            cmd.append("-d")
        
        if name:
            cmd.extend(["--name", name])
        
        if ports:
            for port in ports:
                cmd.extend(["-p", port])
        
        if volumes:
            for volume in volumes:
                cmd.extend(["-v", volume])
        
        if environment:
            for key, value in environment.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        cmd.append(image)
        
        if command:
            cmd.extend(command.split())
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout.strip()
    
    def stop_container(self, container_id: str) -> None:
        """
        Stop a Docker container.
        
        Args:
            container_id: ID of the container to stop
        """
        subprocess.run(
            ["docker", "stop", container_id],
            capture_output=True,
            text=True,
            check=True
        )
    
    def remove_container(self, container_id: str, force: bool = False) -> None:
        """
        Remove a Docker container.
        
        Args:
            container_id: ID of the container to remove
            force: Whether to force removal
        """
        cmd = ["docker", "rm"]
        
        if force:
            cmd.append("-f")
        
        cmd.append(container_id)
        
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    
    def push_image(self, tag: str, registry: str = None) -> None:
        """
        Push a Docker image to a registry.
        
        Args:
            tag: Tag of the image to push
            registry: Registry to push to
        """
        if registry:
            # Retag the image for the registry
            new_tag = f"{registry}/{tag}"
            subprocess.run(
                ["docker", "tag", tag, new_tag],
                capture_output=True,
                text=True,
                check=True
            )
            tag = new_tag
        
        subprocess.run(
            ["docker", "push", tag],
            capture_output=True,
            text=True,
            check=True
        )
    
    def compose_up(self, services: List[str] = None, detach: bool = True) -> None:
        """
        Start services defined in docker-compose.yml.
        
        Args:
            services: List of services to start (None for all)
            detach: Whether to run in detached mode
        """
        cmd = ["docker-compose", "up"]
        
        if detach:
            cmd.append("-d")
        
        if services:
            cmd.extend(services)
        
        subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            check=True
        )
    
    def compose_down(self, volumes: bool = False) -> None:
        """
        Stop services defined in docker-compose.yml.
        
        Args:
            volumes: Whether to remove volumes
        """
        cmd = ["docker-compose", "down"]
        
        if volumes:
            cmd.append("-v")
        
        subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            check=True
        )
    
    def create_multi_stage_dockerfile(self, stages: List[Dict[str, Any]]) -> str:
        """
        Create a multi-stage Dockerfile.
        
        Args:
            stages: List of stage configurations
            
        Returns:
            Path to the created Dockerfile
        """
        dockerfile_path = os.path.join(self.project_dir, "Dockerfile")
        content = ""
        
        for i, stage in enumerate(stages):
            stage_name = stage.get("name", f"stage{i}")
            base_image = stage.get("base_image")
            
            if not base_image:
                raise ValueError(f"Base image is required for stage {stage_name}")
            
            # Start stage definition
            content += f"FROM {base_image}"
            if i > 0:
                content += f" AS {stage_name}"
            content += "\n\n"
            
            # Add working directory
            if "workdir" in stage:
                content += f"WORKDIR {stage['workdir']}\n\n"
            
            # Add commands
            if "commands" in stage:
                for cmd in stage["commands"]:
                    content += f"{cmd}\n"
                content += "\n"
            
            # Add copy from previous stage
            if "copy_from" in stage:
                for copy_item in stage["copy_from"]:
                    from_stage = copy_item.get("from", stages[i-1].get("name", f"stage{i-1}"))
                    src = copy_item.get("src")
                    dest = copy_item.get("dest", src)
                    content += f"COPY --from={from_stage} {src} {dest}\n"
                content += "\n"
        
        # Add final instructions
        final_stage = stages[-1]
        
        if "expose" in final_stage:
            content += f"EXPOSE {final_stage['expose']}\n"
        
        if "entrypoint" in final_stage:
            entrypoint = final_stage["entrypoint"]
            if isinstance(entrypoint, list):
                entrypoint_json = json.dumps(entrypoint)
                content += f"ENTRYPOINT {entrypoint_json}\n"
            else:
                content += f"ENTRYPOINT {entrypoint}\n"
        
        if "cmd" in final_stage:
            cmd = final_stage["cmd"]
            if isinstance(cmd, list):
                cmd_json = json.dumps(cmd)
                content += f"CMD {cmd_json}\n"
            else:
                content += f"CMD {cmd}\n"
        
        with open(dockerfile_path, 'w') as f:
            f.write(content)
        
        return dockerfile_path
    
    def create_dockerignore(self, patterns: List[str]) -> str:
        """
        Create a .dockerignore file.
        
        Args:
            patterns: List of patterns to ignore
            
        Returns:
            Path to the created .dockerignore file
        """
        dockerignore_path = os.path.join(self.project_dir, ".dockerignore")
        
        with open(dockerignore_path, 'w') as f:
            for pattern in patterns:
                f.write(f"{pattern}\n")
        
        return dockerignore_path
    
    def scan_image_for_vulnerabilities(self, image: str) -> Dict[str, Any]:
        """
        Scan a Docker image for vulnerabilities using Trivy.
        
        Args:
            image: Image to scan
            
        Returns:
            Scan results
        """
        # Check if Trivy is installed
        try:
            subprocess.run(
                ["trivy", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Trivy is not installed. Installing...")
            # Install Trivy
            subprocess.run(
                ["apt-get", "update"],
                capture_output=True,
                text=True,
                check=True
            )
            subprocess.run(
                ["apt-get", "install", "-y", "wget", "apt-transport-https", "gnupg", "lsb-release"],
                capture_output=True,
                text=True,
                check=True
            )
            subprocess.run(
                ["wget", "-qO", "-", "https://aquasecurity.github.io/trivy-repo/deb/public.key", "|", "apt-key", "add", "-"],
                capture_output=True,
                text=True,
                shell=True,
                check=True
            )
            subprocess.run(
                ["echo", "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main", "|", "tee", "-a", "/etc/apt/sources.list.d/trivy.list"],
                capture_output=True,
                text=True,
                shell=True,
                check=True
            )
            subprocess.run(
                ["apt-get", "update"],
                capture_output=True,
                text=True,
                check=True
            )
            subprocess.run(
                ["apt-get", "install", "-y", "trivy"],
                capture_output=True,
                text=True,
                check=True
            )
        
        # Create a temporary file for the scan results
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Run Trivy scan
            subprocess.run(
                ["trivy", "image", "--format", "json", "--output", tmp_path, image],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Read scan results
            with open(tmp_path, 'r') as f:
                scan_results = json.load(f)
            
            return scan_results
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def optimize_dockerfile(self, dockerfile_path: str) -> str:
        """
        Optimize a Dockerfile for better performance and smaller image size.
        
        Args:
            dockerfile_path: Path to the Dockerfile
            
        Returns:
            Path to the optimized Dockerfile
        """
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Create a backup of the original Dockerfile
        backup_path = f"{dockerfile_path}.bak"
        shutil.copy2(dockerfile_path, backup_path)
        
        # Apply optimizations
        optimized_content = self._apply_dockerfile_optimizations(content)
        
        # Write optimized Dockerfile
        with open(dockerfile_path, 'w') as f:
            f.write(optimized_content)
        
        return dockerfile_path
    
    def _apply_dockerfile_optimizations(self, content: str) -> str:
        """
        Apply optimizations to Dockerfile content.
        
        Args:
            content: Original Dockerfile content
            
        Returns:
            Optimized Dockerfile content
        """
        lines = content.splitlines()
        optimized_lines = []
        
        # Combine RUN commands
        run_commands = []
        
        for line in lines:
            stripped_line = line.strip()
            
            if stripped_line.startswith("RUN "):
                run_commands.append(stripped_line[4:])
            else:
                # If we have collected RUN commands, combine them
                if run_commands:
                    optimized_lines.append("RUN " + " && \\\n    ".join(run_commands))
                    run_commands = []
                
                # Add non-RUN line
                optimized_lines.append(line)
        
        # Add any remaining RUN commands
        if run_commands:
            optimized_lines.append("RUN " + " && \\\n    ".join(run_commands))
        
        # Add .dockerignore recommendation
        optimized_lines.insert(0, "# Recommended: Use .dockerignore to exclude files from the build context")
        
        # Add layer optimization recommendation
        optimized_lines.insert(1, "# Recommended: Order instructions from least to most frequently changing")
        
        return "\n".join(optimized_lines)
    
    def create_docker_registry(self, name: str = "registry", port: int = 5000) -> str:
        """
        Create a local Docker registry.
        
        Args:
            name: Name for the registry container
            port: Port to expose the registry on
            
        Returns:
            ID of the created container
        """
        return self.run_container(
            image="registry:2",
            name=name,
            ports=[f"{port}:5000"]
        )
    
    def tag_for_local_registry(self, image: str, port: int = 5000) -> str:
        """
        Tag an image for a local registry.
        
        Args:
            image: Image to tag
            port: Port of the local registry
            
        Returns:
            New tag
        """
        new_tag = f"localhost:{port}/{image}"
        
        subprocess.run(
            ["docker", "tag", image, new_tag],
            capture_output=True,
            text=True,
            check=True
        )
        
        return new_tag
