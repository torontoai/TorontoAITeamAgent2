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


import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DeploymentConfig(BaseModel):
    """Deployment configuration model."""
    id: Optional[str] = None
    name: str
    description: str
    environment: str  # dev, staging, prod
    infrastructure: str  # aws, gcp, azure, docker, etc.
    resources: Dict[str, Any] = {}
    
class DeploymentPipeline(BaseModel):
    """Deployment pipeline model."""
    id: Optional[str] = None
    name: str
    description: str
    stages: List[Dict[str, Any]] = []
    
class DeploymentJob(BaseModel):
    """Deployment job model."""
    id: Optional[str] = None
    pipeline_id: str
    environment: str
    status: str = "pending"  # pending, running, success, failed
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    logs: List[str] = []
    
class Monitoring(BaseModel):
    """Monitoring configuration model."""
    id: Optional[str] = None
    name: str
    description: str
    metrics: List[str] = []
    alerts: List[Dict[str, Any]] = []

class DeploymentPipelineModule:
    """Deployment pipeline module for the multi-agent team system.
    Provides CI/CD pipeline capabilities for deploying applications."""
    
    def __init__(self):
        """Initialize the deployment pipeline module."""
        self.configs = {}
        self.pipelines = {}
        self.jobs = {}
        self.monitoring = {}
        
    async def create_deployment_config(self, config: DeploymentConfig) -> str:
        """
        Create a new deployment configuration.
        
        Args:
            config: Deployment configuration data
            
        Returns:
            Configuration ID
        """
        # Generate config ID if not provided
        if not config.id:
            config.id = f"config_{len(self.configs) + 1}"
        
        # Store config
        self.configs[config.id] = config.dict()
        
        return config.id
    
    async def get_deployment_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get deployment configuration by ID.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Deployment configuration or None if not found
        """
        return self.configs.get(config_id)
    
    async def update_deployment_config(self, config_id: str, config_data: Dict[str, Any]) -> bool:
        """
        Update deployment configuration.
        
        Args:
            config_id: Configuration ID
            config_data: Updated configuration data
            
        Returns:
            True if configuration was updated successfully, False otherwise
        """
        if config_id not in self.configs:
            return False
        
        # Update config
        self.configs[config_id].update(config_data)
        
        return True
    
    async def delete_deployment_config(self, config_id: str) -> bool:
        """
        Delete a deployment configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            True if configuration was deleted successfully, False otherwise
        """
        if config_id not in self.configs:
            return False
        
        # Delete config
        del self.configs[config_id]
        
        return True
    
    async def create_deployment_pipeline(self, pipeline: DeploymentPipeline) -> str:
        """
        Create a new deployment pipeline.
        
        Args:
            pipeline: Deployment pipeline data
            
        Returns:
            Pipeline ID
        """
        # Generate pipeline ID if not provided
        if not pipeline.id:
            pipeline.id = f"pipeline_{len(self.pipelines) + 1}"
        
        # Store pipeline
        self.pipelines[pipeline.id] = pipeline.dict()
        
        return pipeline.id
    
    async def get_deployment_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """
        Get deployment pipeline by ID.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Deployment pipeline or None if not found
        """
        return self.pipelines.get(pipeline_id)
    
    async def update_deployment_pipeline(self, pipeline_id: str, pipeline_data: Dict[str, Any]) -> bool:
        """
        Update deployment pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            pipeline_data: Updated pipeline data
            
        Returns:
            True if pipeline was updated successfully, False otherwise
        """
        if pipeline_id not in self.pipelines:
            return False
        
        # Update pipeline
        self.pipelines[pipeline_id].update(pipeline_data)
        
        return True
    
    async def delete_deployment_pipeline(self, pipeline_id: str) -> bool:
        """
        Delete a deployment pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            True if pipeline was deleted successfully, False otherwise
        """
        if pipeline_id not in self.pipelines:
            return False
        
        # Delete pipeline
        del self.pipelines[pipeline_id]
        
        return True
    
    async def create_deployment_job(self, job: DeploymentJob) -> str:
        """
        Create a new deployment job.
        
        Args:
            job: Deployment job data
            
        Returns:
            Job ID
        """
        # Check if pipeline exists
        if job.pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {job.pipeline_id} not found")
        
        # Generate job ID if not provided
        if not job.id:
            job.id = f"job_{len(self.jobs) + 1}"
        
        # Store job
        self.jobs[job.id] = job.dict()
        
        return job.id
    
    async def get_deployment_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get deployment job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Deployment job or None if not found
        """
        return self.jobs.get(job_id)
    
    async def update_deployment_job(self, job_id: str, job_data: Dict[str, Any]) -> bool:
        """
        Update deployment job.
        
        Args:
            job_id: Job ID
            job_data: Updated job data
            
        Returns:
            True if job was updated successfully, False otherwise
        """
        if job_id not in self.jobs:
            return False
        
        # Update job
        self.jobs[job_id].update(job_data)
        
        return True
    
    async def delete_deployment_job(self, job_id: str) -> bool:
        """
        Delete a deployment job.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if job was deleted successfully, False otherwise
        """
        if job_id not in self.jobs:
            return False
        
        # Delete job
        del self.jobs[job_id]
        
        return True
    
    async def run_deployment_job(self, job_id: str) -> Dict[str, Any]:
        """
        Run a deployment job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job result
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        
        # Check if pipeline exists
        if job["pipeline_id"] not in self.pipelines:
            raise ValueError(f"Pipeline {job['pipeline_id']} not found")
        
        pipeline = self.pipelines[job["pipeline_id"]]
        
        # Update job status
        job["status"] = "running"
        job["start_time"] = datetime.datetime.now().isoformat()
        job["logs"] = []
        
        # Run each stage in the pipeline
        for i, stage in enumerate(pipeline["stages"]):
            # Log stage start
            job["logs"].append(f"Starting stage {i+1}: {stage['name']}")
            
            # Simulate stage execution
            # In a real implementation, this would execute the actual stage
            import random
            import time
            
            # Simulate stage duration
            duration = random.uniform(1, 5)
            time.sleep(duration)
            
            # Simulate stage success/failure
            success = random.random() > 0.1  # 90% chance of success
            
            if not success:
                # Log stage failure
                job["logs"].append(f"Stage {i+1} failed: {stage['name']}")
                job["status"] = "failed"
                job["end_time"] = datetime.datetime.now().isoformat()
                return job
            
            # Log stage success
            job["logs"].append(f"Stage {i+1} completed successfully: {stage['name']}")
        
        # All stages completed successfully
        job["status"] = "success"
        job["end_time"] = datetime.datetime.now().isoformat()
        
        return job
    
    async def create_monitoring_config(self, config: Monitoring) -> str:
        """
        Create a new monitoring configuration.
        
        Args:
            config: Monitoring configuration data
            
        Returns:
            Configuration ID
        """
        # Generate config ID if not provided
        if not config.id:
            config.id = f"monitoring_{len(self.monitoring) + 1}"
        
        # Store config
        self.monitoring[config.id] = config.dict()
        
        return config.id
    
    async def get_monitoring_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get monitoring configuration by ID.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Monitoring configuration or None if not found
        """
        return self.monitoring.get(config_id)
    
    async def update_monitoring_config(self, config_id: str, config_data: Dict[str, Any]) -> bool:
        """
        Update monitoring configuration.
        
        Args:
            config_id: Configuration ID
            config_data: Updated configuration data
            
        Returns:
            True if configuration was updated successfully, False otherwise
        """
        if config_id not in self.monitoring:
            return False
        
        # Update config
        self.monitoring[config_id].update(config_data)
        
        return True
    
    async def delete_monitoring_config(self, config_id: str) -> bool:
        """
        Delete a monitoring configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            True if configuration was deleted successfully, False otherwise
        """
        if config_id not in self.monitoring:
            return False
        
        # Delete config
        del self.monitoring[config_id]
        
        return True
    
    async def generate_infrastructure_code(self, config_id: str) -> Dict[str, str]:
        """
        Generate infrastructure-as-code for a deployment configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Dictionary of generated code files
        """
        if config_id not in self.configs:
            raise ValueError(f"Configuration {config_id} not found")
        
        config = self.configs[config_id]
        
        # Generate infrastructure code based on configuration
        # In a real implementation, this would generate actual infrastructure code
        
        code_files = {}
        
        if config["infrastructure"] == "aws":
            # Generate AWS CloudFormation template
            code_files["cloudformation.yaml"] = """
AWSTemplateFormatVersion: '2010-09-09'
Description: Infrastructure for {name}

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: {name}-vpc
          
  # Add more resources as needed
""".format(name=config["name"])
        
        elif config["infrastructure"] == "gcp":
            # Generate Google Cloud Deployment Manager template
            code_files["deployment.yaml"] = """
resources:
- name: {name}-network
  type: compute.v1.network
  properties:
    autoCreateSubnetworks: true
    
# Add more resources as needed
""".format(name=config["name"])
        
        elif config["infrastructure"] == "azure":
            # Generate Azure Resource Manager template
            code_files["azuredeploy.json"] = """
{{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {{}},
  "variables": {{}},
  "resources": [
    {{
      "type": "Microsoft.Network/virtualNetworks",
      "apiVersion": "2020-11-01",
      "name": "{name}-vnet",
      "location": "[resourceGroup().location]",
      "properties": {{
        "addressSpace": {{
          "addressPrefixes": [
            "10.0.0.0/16"
          ]
        }}
      }}
    }}
    
    // Add more resources as needed
  ]
}}
""".format(name=config["name"])
        
        elif config["infrastructure"] == "docker":
            # Generate Docker Compose file
            code_files["docker-compose.yml"] = """
version: '3'

services:
  app:
    image: {name}
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
    
  # Add more services as needed
""".format(name=config["name"])
        
        else:
            # Generate generic deployment script
            code_files["deploy.sh"] = """
#!/bin/bash

echo "Deploying {name} to {environment}..."

# Add deployment commands here

echo "Deployment complete!"
""".format(name=config["name"], environment=config["environment"])
        
        return code_files
    
    async def generate_ci_cd_config(self, pipeline_id: str) -> Dict[str, str]:
        """
        Generate CI/CD configuration for a deployment pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Dictionary of generated configuration files
        """
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        pipeline = self.pipelines[pipeline_id]
        
        # Generate CI/CD configuration based on pipeline
        # In a real implementation, this would generate actual CI/CD configuration
        
        config_files = {}
        
        # Generate GitHub Actions workflow
        stages_yaml = ""
        for stage in pipeline["stages"]:
            stages_yaml += f"""
      - name: {stage['name']}
        run: {stage.get('command', 'echo "Running {0}"'.format(stage['name']))}
"""
        
        config_files["github-actions.yml"] = f"""
name: {pipeline['name']}

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
{stages_yaml}
"""
        
        # Generate GitLab CI configuration
        stages_list = ", ".join([f'"{stage["name"]}"' for stage in pipeline["stages"]])
        stages_config = ""
        
        for stage in pipeline["stages"]:
            stages_config += f"""
{stage['name']}:
  stage: {stage['name']}
  script:
    - {stage.get('command', 'echo "Running {0}"'.format(stage['name']))}
"""
        
        config_files["gitlab-ci.yml"] = f"""
stages: [{stages_list}]

{stages_config}
"""
        
        # Generate Jenkins pipeline
        jenkins_stages = ""
        for stage in pipeline["stages"]:
            jenkins_stages += f"""
        stage('{stage['name']}') {{
            steps {{
                sh '{stage.get('command', 'echo "Running {0}"'.format(stage['name']))}'
            }}
        }}
"""
        
        config_files["Jenkinsfile"] = f"""
pipeline {{
    agent any
    
    stages {{{jenkins_stages}
    }}
}}
"""
        
        return config_files
    
    async def generate_monitoring_config_files(self, config_id: str) -> Dict[str, str]:
        """
        Generate monitoring configuration files.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Dictionary of generated configuration files
        """
        if config_id not in self.monitoring:
            raise ValueError(f"Monitoring configuration {config_id} not found")
        
        config = self.monitoring[config_id]
        
        # Generate monitoring configuration based on config
        # In a real implementation, this would generate actual monitoring configuration
        
        config_files = {}
        
        # Generate Prometheus configuration
        metrics_config = ""
        for metric in config["metrics"]:
            metrics_config += f"""
  - job_name: '{metric}'
    static_configs:
      - targets: ['localhost:9090']
"""
        
        config_files["prometheus.yml"] = f"""
global:
  scrape_interval: 15s

scrape_configs:{metrics_config}
"""
        
        # Generate Grafana dashboard
        config_files["grafana-dashboard.json"] = f"""
{{
  "annotations": {{
    "list": []
  }},
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [],
  "refresh": "5s",
  "schemaVersion": 27,
  "style": "dark",
  "tags": [],
  "templating": {{
    "list": []
  }},
  "time": {{
    "from": "now-6h",
    "to": "now"
  }},
  "timepicker": {{
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ]
  }},
  "timezone": "",
  "title": "{config['name']}",
  "uid": null,
  "version": 0
}}
"""
        
        # Generate alert configuration
        alerts_config = ""
        for alert in config["alerts"]:
            alerts_config += f"""
  - alert: {alert['name']}
    expr: {alert.get('expression', 'up == 0')}
    for: {alert.get('duration', '5m')}
    labels:
      severity: {alert.get('severity', 'warning')}
    annotations:
      summary: "{alert.get('summary', 'Alert triggered')}"
      description: "{alert.get('description', 'Alert description')}"
"""
        
        config_files["alerts.yml"] = f"""
groups:
- name: {config['name']}
  rules:{alerts_config}
"""
        
        return config_files
    
    async def create_rollback_plan(self, job_id: str) -> Dict[str, Any]:
        """
        Create a rollback plan for a deployment job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Rollback plan
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        
        # Create rollback plan
        # In a real implementation, this would create an actual rollback plan
        
        rollback_plan = {
            "job_id": job_id,
            "steps": [
                {
                    "name": "Stop new version",
                    "command": f"kubectl scale deployment {job['pipeline_id']} --replicas=0"
                },
                {
                    "name": "Restore previous version",
                    "command": f"kubectl rollout undo deployment {job['pipeline_id']}"
                },
                {
                    "name": "Verify rollback",
                    "command": f"kubectl rollout status deployment {job['pipeline_id']}"
                }
            ],
            "created_at": datetime.datetime.now().isoformat()
        }
        
        return rollback_plan

class DeploymentPipelineAPIModule:
    """Deployment pipeline API module for the multi-agent team system.
    Provides FastAPI routes for deployment pipeline capabilities."""
    
    def __init__(self, app: FastAPI):
        """Initialize the deployment pipeline API module.
        
        Args:
            app: FastAPI application"""
        self.app = app
        self.deployment_pipeline = DeploymentPipelineModule()
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register routes with the FastAPI app."""
        
        @self.app.post("/api/deployment/configs", response_model=Dict[str, str])
        async def create_deployment_config(config: DeploymentConfig):
            """
            Create a new deployment configuration.
            
            Args:
                config: Deployment configuration data
                
            Returns:
                Configuration ID
            """
            try:
                config_id = await self.deployment_pipeline.create_deployment_config(config)
                return {"config_id": config_id}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/deployment/configs/{config_id}", response_model=Dict[str, Any])
        async def get_deployment_config(config_id: str):
            """
            Get deployment configuration by ID.
            
            Args:
                config_id: Configuration ID
                
            Returns:
                Deployment configuration
            """
            config = await self.deployment_pipeline.get_deployment_config(config_id)
            if not config:
                raise HTTPException(status_code=404, detail=f"Deployment configuration {config_id} not found")
            return config
        
        @self.app.put("/api/deployment/configs/{config_id}", response_model=Dict[str, bool])
        async def update_deployment_config(config_id: str, config_data: Dict[str, Any]):
            """
            Update deployment configuration.
            
            Args:
                config_id: Configuration ID
                config_data: Updated configuration data
                
            Returns:
                Success status
            """
            success = await self.deployment_pipeline.update_deployment_config(config_id, config_data)
            if not success:
                raise HTTPException(status_code=404, detail=f"Deployment configuration {config_id} not found")
            return {"success": success}
        
        @self.app.delete("/api/deployment/configs/{config_id}", response_model=Dict[str, bool])
        async def delete_deployment_config(config_id: str):
            """
            Delete a deployment configuration.
            
            Args:
                config_id: Configuration ID
                
            Returns:
                Success status
            """
            success = await self.deployment_pipeline.delete_deployment_config(config_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Deployment configuration {config_id} not found")
            return {"success": success}
        
        @self.app.post("/api/deployment/pipelines", response_model=Dict[str, str])
        async def create_deployment_pipeline(pipeline: DeploymentPipeline):
            """
            Create a new deployment pipeline.
            
            Args:
                pipeline: Deployment pipeline data
                
            Returns:
                Pipeline ID
            """
            try:
                pipeline_id = await self.deployment_pipeline.create_deployment_pipeline(pipeline)
                return {"pipeline_id": pipeline_id}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/deployment/pipelines/{pipeline_id}", response_model=Dict[str, Any])
        async def get_deployment_pipeline(pipeline_id: str):
            """
            Get deployment pipeline by ID.
            
            Args:
                pipeline_id: Pipeline ID
                
            Returns:
                Deployment pipeline
            """
            pipeline = await self.deployment_pipeline.get_deployment_pipeline(pipeline_id)
            if not pipeline:
                raise HTTPException(status_code=404, detail=f"Deployment pipeline {pipeline_id} not found")
            return pipeline
        
        @self.app.put("/api/deployment/pipelines/{pipeline_id}", response_model=Dict[str, bool])
        async def update_deployment_pipeline(pipeline_id: str, pipeline_data: Dict[str, Any]):
            """
            Update deployment pipeline.
            
            Args:
                pipeline_id: Pipeline ID
                pipeline_data: Updated pipeline data
                
            Returns:
                Success status
            """
            success = await self.deployment_pipeline.update_deployment_pipeline(pipeline_id, pipeline_data)
            if not success:
                raise HTTPException(status_code=404, detail=f"Deployment pipeline {pipeline_id} not found")
            return {"success": success}
        
        @self.app.delete("/api/deployment/pipelines/{pipeline_id}", response_model=Dict[str, bool])
        async def delete_deployment_pipeline(pipeline_id: str):
            """
            Delete a deployment pipeline.
            
            Args:
                pipeline_id: Pipeline ID
                
            Returns:
                Success status
            """
            success = await self.deployment_pipeline.delete_deployment_pipeline(pipeline_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Deployment pipeline {pipeline_id} not found")
            return {"success": success}
        
        @self.app.post("/api/deployment/jobs", response_model=Dict[str, str])
        async def create_deployment_job(job: DeploymentJob):
            """
            Create a new deployment job.
            
            Args:
                job: Deployment job data
                
            Returns:
                Job ID
            """
            try:
                job_id = await self.deployment_pipeline.create_deployment_job(job)
                return {"job_id": job_id}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/deployment/jobs/{job_id}", response_model=Dict[str, Any])
        async def get_deployment_job(job_id: str):
            """
            Get deployment job by ID.
            
            Args:
                job_id: Job ID
                
            Returns:
                Deployment job
            """
            job = await self.deployment_pipeline.get_deployment_job(job_id)
            if not job:
                raise HTTPException(status_code=404, detail=f"Deployment job {job_id} not found")
            return job
        
        @self.app.put("/api/deployment/jobs/{job_id}", response_model=Dict[str, bool])
        async def update_deployment_job(job_id: str, job_data: Dict[str, Any]):
            """
            Update deployment job.
            
            Args:
                job_id: Job ID
                job_data: Updated job data
                
            Returns:
                Success status
            """
            success = await self.deployment_pipeline.update_deployment_job(job_id, job_data)
            if not success:
                raise HTTPException(status_code=404, detail=f"Deployment job {job_id} not found")
            return {"success": success}
        
        @self.app.delete("/api/deployment/jobs/{job_id}", response_model=Dict[str, bool])
        async def delete_deployment_job(job_id: str):
            """
            Delete a deployment job.
            
            Args:
                job_id: Job ID
                
            Returns:
                Success status
            """
            success = await self.deployment_pipeline.delete_deployment_job(job_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Deployment job {job_id} not found")
            return {"success": success}
        
        @self.app.post("/api/deployment/jobs/{job_id}/run", response_model=Dict[str, Any])
        async def run_deployment_job(job_id: str):
            """
            Run a deployment job.
            
            Args:
                job_id: Job ID
                
            Returns:
                Job result
            """
            try:
                result = await self.deployment_pipeline.run_deployment_job(job_id)
                return result
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/deployment/monitoring", response_model=Dict[str, str])
        async def create_monitoring_config(config: Monitoring):
            """
            Create a new monitoring configuration.
            
            Args:
                config: Monitoring configuration data
                
            Returns:
                Configuration ID
            """
            try:
                config_id = await self.deployment_pipeline.create_monitoring_config(config)
                return {"config_id": config_id}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/deployment/monitoring/{config_id}", response_model=Dict[str, Any])
        async def get_monitoring_config(config_id: str):
            """
            Get monitoring configuration by ID.
            
            Args:
                config_id: Configuration ID
                
            Returns:
                Monitoring configuration
            """
            config = await self.deployment_pipeline.get_monitoring_config(config_id)
            if not config:
                raise HTTPException(status_code=404, detail=f"Monitoring configuration {config_id} not found")
            return config
        
        @self.app.put("/api/deployment/monitoring/{config_id}", response_model=Dict[str, bool])
        async def update_monitoring_config(config_id: str, config_data: Dict[str, Any]):
            """
            Update monitoring configuration.
            
            Args:
                config_id: Configuration ID
                config_data: Updated configuration data
                
            Returns:
                Success status
            """
            success = await self.deployment_pipeline.update_monitoring_config(config_id, config_data)
            if not success:
                raise HTTPException(status_code=404, detail=f"Monitoring configuration {config_id} not found")
            return {"success": success}
        
        @self.app.delete("/api/deployment/monitoring/{config_id}", response_model=Dict[str, bool])
        async def delete_monitoring_config(config_id: str):
            """
            Delete a monitoring configuration.
            
            Args:
                config_id: Configuration ID
                
            Returns:
                Success status
            """
            success = await self.deployment_pipeline.delete_monitoring_config(config_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Monitoring configuration {config_id} not found")
            return {"success": success}
        
        @self.app.post("/api/deployment/configs/{config_id}/generate-infrastructure", response_model=Dict[str, str])
        async def generate_infrastructure_code(config_id: str):
            """
            Generate infrastructure-as-code for a deployment configuration.
            
            Args:
                config_id: Configuration ID
                
            Returns:
                Dictionary of generated code files
            """
            try:
                code_files = await self.deployment_pipeline.generate_infrastructure_code(config_id)
                return code_files
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/deployment/pipelines/{pipeline_id}/generate-ci-cd", response_model=Dict[str, str])
        async def generate_ci_cd_config(pipeline_id: str):
            """
            Generate CI/CD configuration for a deployment pipeline.
            
            Args:
                pipeline_id: Pipeline ID
                
            Returns:
                Dictionary of generated configuration files
            """
            try:
                config_files = await self.deployment_pipeline.generate_ci_cd_config(pipeline_id)
                return config_files
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/deployment/monitoring/{config_id}/generate-config", response_model=Dict[str, str])
        async def generate_monitoring_config_files(config_id: str):
            """
            Generate monitoring configuration files.
            
            Args:
                config_id: Configuration ID
                
            Returns:
                Dictionary of generated configuration files
            """
            try:
                config_files = await self.deployment_pipeline.generate_monitoring_config_files(config_id)
                return config_files
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/deployment/jobs/{job_id}/rollback", response_model=Dict[str, Any])
        async def create_rollback_plan(job_id: str):
            """
            Create a rollback plan for a deployment job.
            
            Args:
                job_id: Job ID
                
            Returns:
                Rollback plan
            """
            try:
                rollback_plan = await self.deployment_pipeline.create_rollback_plan(job_id)
                return rollback_plan
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

# Function to create deployment pipeline API module
def create_deployment_pipeline_api_module(app: FastAPI) -> DeploymentPipelineAPIModule:
    """Create and initialize the deployment pipeline API module.
    
    Args:
        app: FastAPI application
        
    Returns:
        DeploymentPipelineAPIModule instance"""
    return DeploymentPipelineAPIModule(app)
