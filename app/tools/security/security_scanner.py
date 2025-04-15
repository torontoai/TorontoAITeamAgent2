"""
Snyk security integration for TORONTO AI TEAM AGENT.

This module provides integration with Snyk for continuous security scanning
of code and dependencies.
"""

import os
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional, Union
import requests

from app.core.error_handling import ErrorHandler, ErrorCategory, ErrorSeverity, safe_execute

logger = logging.getLogger(__name__)

class SnykClient:
    """Client for interacting with Snyk API and CLI."""
    
    def __init__(self, api_key: Optional[str] = None, organization_id: Optional[str] = None):
        """
        Initialize the Snyk client.
        
        Args:
            api_key: Snyk API key (defaults to SNYK_API_KEY environment variable)
            organization_id: Snyk organization ID (defaults to SNYK_ORGANIZATION_ID environment variable)
        """
        self.api_key = api_key or os.environ.get("SNYK_API_KEY")
        if not self.api_key:
            logger.warning("Snyk API key not provided. Some functionality may be limited.")
            
        self.organization_id = organization_id or os.environ.get("SNYK_ORGANIZATION_ID")
        if not self.organization_id:
            logger.warning("Snyk organization ID not provided. Some functionality may be limited.")
            
        self.base_url = "https://snyk.io/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Check if Snyk CLI is installed
        self.cli_available = self._check_cli_available()
        if not self.cli_available:
            logger.warning("Snyk CLI not found. CLI-based scanning will not be available.")
    
    def _check_cli_available(self) -> bool:
        """Check if Snyk CLI is available."""
        try:
            subprocess.run(["snyk", "--version"], capture_output=True, check=False)
            return True
        except FileNotFoundError:
            return False
    
    def install_cli(self) -> bool:
        """Install Snyk CLI if not already installed."""
        if self.cli_available:
            logger.info("Snyk CLI is already installed.")
            return True
            
        try:
            logger.info("Installing Snyk CLI...")
            subprocess.run(["npm", "install", "-g", "snyk"], check=True)
            
            # Authenticate with Snyk
            if self.api_key:
                subprocess.run(["snyk", "auth", self.api_key], check=True)
                
            self.cli_available = True
            logger.info("Snyk CLI installed successfully.")
            return True
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to install Snyk CLI: {str(e)}")
            return False
    
    def scan_project(
        self, 
        project_path: str, 
        scan_type: str = "all",
        severity_threshold: str = "medium",
        json_output: bool = True
    ) -> Dict[str, Any]:
        """
        Scan a project for vulnerabilities using Snyk CLI.
        
        Args:
            project_path: Path to the project to scan
            scan_type: Type of scan to perform (all, code, oss, container)
            severity_threshold: Minimum severity to report (low, medium, high, critical)
            json_output: Whether to return results in JSON format
            
        Returns:
            Dict containing the scan results
        """
        if not self.cli_available:
            return {"error": "Snyk CLI not available. Install CLI first."}
            
        with ErrorHandler(
            error_category=ErrorCategory.SECURITY,
            error_message=f"Error scanning project with Snyk CLI: {project_path}",
            severity=ErrorSeverity.MEDIUM
        ):
            cmd = ["snyk"]
            
            # Add scan type
            if scan_type == "code":
                cmd.append("code")
            elif scan_type == "container":
                cmd.append("container")
            elif scan_type == "oss" or scan_type == "all":
                cmd.append("test")
            
            # Add project path
            cmd.append(project_path)
            
            # Add severity threshold
            cmd.extend(["--severity-threshold", severity_threshold])
            
            # Add JSON output flag
            if json_output:
                cmd.append("--json")
            
            # Run the scan
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            # Parse the output
            if json_output and result.stdout:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse JSON output", "output": result.stdout}
            
            return {"output": result.stdout, "errors": result.stderr, "exit_code": result.returncode}
    
    def get_vulnerabilities(
        self, 
        project_id: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get vulnerabilities for a project or organization using Snyk API.
        
        Args:
            project_id: ID of the project to get vulnerabilities for
            org_id: Organization ID (defaults to self.organization_id)
            
        Returns:
            Dict containing the vulnerabilities
        """
        with ErrorHandler(
            error_category=ErrorCategory.SECURITY,
            error_message="Error getting vulnerabilities from Snyk API",
            severity=ErrorSeverity.MEDIUM
        ):
            org_id = org_id or self.organization_id
            
            if not org_id:
                return {"error": "Organization ID not provided"}
            
            if project_id:
                endpoint = f"{self.base_url}/org/{org_id}/project/{project_id}/issues"
            else:
                endpoint = f"{self.base_url}/org/{org_id}/issues"
            
            response = self.session.post(endpoint, json={})
            response.raise_for_status()
            
            return response.json()
    
    def get_projects(self, org_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all projects for an organization using Snyk API.
        
        Args:
            org_id: Organization ID (defaults to self.organization_id)
            
        Returns:
            Dict containing the projects
        """
        with ErrorHandler(
            error_category=ErrorCategory.SECURITY,
            error_message="Error getting projects from Snyk API",
            severity=ErrorSeverity.MEDIUM
        ):
            org_id = org_id or self.organization_id
            
            if not org_id:
                return {"error": "Organization ID not provided"}
            
            endpoint = f"{self.base_url}/org/{org_id}/projects"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def monitor_project(
        self, 
        project_path: str,
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Monitor a project for vulnerabilities using Snyk CLI.
        
        Args:
            project_path: Path to the project to monitor
            project_name: Name of the project (optional)
            
        Returns:
            Dict containing the monitoring results
        """
        if not self.cli_available:
            return {"error": "Snyk CLI not available. Install CLI first."}
            
        with ErrorHandler(
            error_category=ErrorCategory.SECURITY,
            error_message=f"Error monitoring project with Snyk CLI: {project_path}",
            severity=ErrorSeverity.MEDIUM
        ):
            cmd = ["snyk", "monitor"]
            
            # Add project path
            cmd.append(project_path)
            
            # Add project name if provided
            if project_name:
                cmd.extend(["--project-name", project_name])
            
            # Add JSON output flag
            cmd.append("--json")
            
            # Run the monitor command
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            # Parse the output
            if result.stdout:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse JSON output", "output": result.stdout}
            
            return {"output": result.stdout, "errors": result.stderr, "exit_code": result.returncode}
    
    def fix_vulnerabilities(
        self, 
        project_path: str,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Fix vulnerabilities in a project using Snyk CLI.
        
        Args:
            project_path: Path to the project to fix
            dry_run: Whether to perform a dry run (no actual changes)
            
        Returns:
            Dict containing the fix results
        """
        if not self.cli_available:
            return {"error": "Snyk CLI not available. Install CLI first."}
            
        with ErrorHandler(
            error_category=ErrorCategory.SECURITY,
            error_message=f"Error fixing vulnerabilities with Snyk CLI: {project_path}",
            severity=ErrorSeverity.MEDIUM
        ):
            cmd = ["snyk", "fix"]
            
            # Add project path
            cmd.append(project_path)
            
            # Add dry run flag if needed
            if dry_run:
                cmd.append("--dry-run")
            
            # Add JSON output flag
            cmd.append("--json")
            
            # Run the fix command
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            # Parse the output
            if result.stdout:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse JSON output", "output": result.stdout}
            
            return {"output": result.stdout, "errors": result.stderr, "exit_code": result.returncode}


class SecurityScannerService:
    """Service for integrating Snyk security scanning with the system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Security Scanner service.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        api_key = self.config.get("api_key") or os.environ.get("SNYK_API_KEY")
        organization_id = self.config.get("organization_id") or os.environ.get("SNYK_ORGANIZATION_ID")
        
        self.client = SnykClient(api_key=api_key, organization_id=organization_id)
        
        # Install CLI if auto_install is enabled
        if self.config.get("auto_install_cli", False) and not self.client.cli_available:
            self.client.install_cli()
    
    def scan_project_dependencies(
        self, 
        project_path: str,
        severity_threshold: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scan project dependencies for vulnerabilities.
        
        Args:
            project_path: Path to the project to scan
            severity_threshold: Minimum severity to report (low, medium, high, critical)
            
        Returns:
            Dict containing the scan results
        """
        severity = severity_threshold or self.config.get("severity_threshold", "medium")
        
        scan_result = self.client.scan_project(
            project_path=project_path,
            scan_type="oss",
            severity_threshold=severity,
            json_output=True
        )
        
        # Process and format the results
        return self._process_scan_results(scan_result, "dependencies")
    
    def scan_project_code(
        self, 
        project_path: str,
        severity_threshold: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scan project code for security issues.
        
        Args:
            project_path: Path to the project to scan
            severity_threshold: Minimum severity to report (low, medium, high, critical)
            
        Returns:
            Dict containing the scan results
        """
        severity = severity_threshold or self.config.get("severity_threshold", "medium")
        
        scan_result = self.client.scan_project(
            project_path=project_path,
            scan_type="code",
            severity_threshold=severity,
            json_output=True
        )
        
        # Process and format the results
        return self._process_scan_results(scan_result, "code")
    
    def scan_project_complete(
        self, 
        project_path: str,
        severity_threshold: Optional[str] = None,
        monitor: bool = False
    ) -> Dict[str, Any]:
        """
        Perform a complete security scan of a project.
        
        Args:
            project_path: Path to the project to scan
            severity_threshold: Minimum severity to report (low, medium, high, critical)
            monitor: Whether to also monitor the project
            
        Returns:
            Dict containing the scan results
        """
        severity = severity_threshold or self.config.get("severity_threshold", "medium")
        
        # Scan dependencies
        dependencies_result = self.client.scan_project(
            project_path=project_path,
            scan_type="oss",
            severity_threshold=severity,
            json_output=True
        )
        
        # Scan code
        code_result = self.client.scan_project(
            project_path=project_path,
            scan_type="code",
            severity_threshold=severity,
            json_output=True
        )
        
        # Monitor project if requested
        monitor_result = None
        if monitor:
            monitor_result = self.client.monitor_project(
                project_path=project_path,
                project_name=os.path.basename(project_path)
            )
        
        # Combine and process results
        combined_results = {
            "dependencies": self._process_scan_results(dependencies_result, "dependencies"),
            "code": self._process_scan_results(code_result, "code")
        }
        
        if monitor_result:
            combined_results["monitoring"] = monitor_result
        
        # Add summary
        combined_results["summary"] = self._generate_summary(combined_results)
        
        return combined_results
    
    def fix_vulnerabilities(
        self, 
        project_path: str,
        auto_fix: bool = False
    ) -> Dict[str, Any]:
        """
        Fix vulnerabilities in a project.
        
        Args:
            project_path: Path to the project to fix
            auto_fix: Whether to automatically apply fixes
            
        Returns:
            Dict containing the fix results
        """
        # First do a dry run to see what would be fixed
        dry_run_result = self.client.fix_vulnerabilities(
            project_path=project_path,
            dry_run=True
        )
        
        # If auto_fix is enabled, apply the fixes
        applied_result = None
        if auto_fix:
            applied_result = self.client.fix_vulnerabilities(
                project_path=project_path,
                dry_run=False
            )
        
        return {
            "dry_run": dry_run_result,
            "applied": applied_result if auto_fix else None,
            "auto_fix": auto_fix
        }
    
    def _process_scan_results(self, scan_result: Dict[str, Any], scan_type: str) -> Dict[str, Any]:
        """Process and format scan results."""
        if "error" in scan_result:
            return scan_result
        
        # Extract vulnerabilities by severity
        vulnerabilities = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        # Process different result formats based on scan type
        if scan_type == "dependencies" and "vulnerabilities" in scan_result:
            for vuln in scan_result.get("vulnerabilities", []):
                severity = vuln.get("severity", "").lower()
                if severity in vulnerabilities:
                    vulnerabilities[severity].append({
                        "id": vuln.get("id", ""),
                        "name": vuln.get("name", ""),
                        "package": vuln.get("packageName", ""),
                        "version": vuln.get("version", ""),
                        "description": vuln.get("description", ""),
                        "fix_available": vuln.get("isUpgradable", False),
                        "fix_version": vuln.get("fixedIn", []),
                        "url": vuln.get("url", "")
                    })
        elif scan_type == "code" and "runs" in scan_result:
            for run in scan_result.get("runs", []):
                for result in run.get("results", []):
                    severity = result.get("level", "").lower()
                    if severity in vulnerabilities:
                        vulnerabilities[severity].append({
                            "id": result.get("ruleId", ""),
                            "name": result.get("message", {}).get("text", ""),
                            "file": result.get("locations", [{}])[0].get("physicalLocation", {}).get("artifactLocation", {}).get("uri", ""),
                            "line": result.get("locations", [{}])[0].get("physicalLocation", {}).get("region", {}).get("startLine", 0),
                            "description": result.get("message", {}).get("text", ""),
                            "fix_available": False,
                            "url": ""
                        })
        
        # Count vulnerabilities by severity
        counts = {
            "critical": len(vulnerabilities["critical"]),
            "high": len(vulnerabilities["high"]),
            "medium": len(vulnerabilities["medium"]),
            "low": len(vulnerabilities["low"]),
            "total": sum(len(vulnerabilities[sev]) for sev in vulnerabilities)
        }
        
        return {
            "vulnerabilities": vulnerabilities,
            "counts": counts,
            "scan_type": scan_type,
            "raw_result": scan_result if self.config.get("include_raw_results", False) else None
        }
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of scan results."""
        dependencies_counts = results.get("dependencies", {}).get("counts", {})
        code_counts = results.get("code", {}).get("counts", {})
        
        total_vulnerabilities = {
            "critical": (dependencies_counts.get("critical", 0) + code_counts.get("critical", 0)),
            "high": (dependencies_counts.get("high", 0) + code_counts.get("high", 0)),
            "medium": (dependencies_counts.get("medium", 0) + code_counts.get("medium", 0)),
            "low": (dependencies_counts.get("low", 0) + code_counts.get("low", 0)),
            "total": (dependencies_counts.get("total", 0) + code_counts.get("total", 0))
        }
        
        return {
            "total_vulnerabilities": total_vulnerabilities,
            "dependencies_vulnerabilities": dependencies_counts,
            "code_vulnerabilities": code_counts,
            "has_critical": total_vulnerabilities["critical"] > 0,
            "has_high": total_vulnerabilities["high"] > 0,
            "risk_level": self._determine_risk_level(total_vulnerabilities)
        }
    
    def _determine_risk_level(self, counts: Dict[str, int]) -> str:
        """Determine the overall risk level based on vulnerability counts."""
        if counts.get("critical", 0) > 0:
            return "critical"
        elif counts.get("high", 0) > 0:
            return "high"
        elif counts.get("medium", 0) > 0:
            return "medium"
        elif counts.get("low", 0) > 0:
            return "low"
        else:
            return "none"
