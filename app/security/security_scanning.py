"""
Security Scanning Tools integration for TORONTO AI TEAM AGENT.

This module provides functionality to integrate with security scanning tools like
Snyk, SonarQube, and others for secure development.
"""

import os
import json
import subprocess
import tempfile
import logging
import requests
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import re
import time


class SecurityScannerType(Enum):
    """Enum representing different security scanner types."""
    SNYK = "snyk"
    SONARQUBE = "sonarqube"
    OWASP_ZAP = "owasp_zap"
    TRIVY = "trivy"
    BANDIT = "bandit"
    DEPENDENCY_CHECK = "dependency_check"
    SEMGREP = "semgrep"


class VulnerabilitySeverity(Enum):
    """Enum representing vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    """Class representing a security vulnerability."""
    id: str
    title: str
    description: str
    severity: VulnerabilitySeverity
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    scanner_type: Optional[SecurityScannerType] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    remediation: Optional[str] = None
    references: List[str] = field(default_factory=list)
    discovered_at: float = field(default_factory=time.time)
    
    @property
    def is_critical(self) -> bool:
        """Check if the vulnerability is critical."""
        return self.severity == VulnerabilitySeverity.CRITICAL
    
    @property
    def is_high(self) -> bool:
        """Check if the vulnerability is high severity."""
        return self.severity == VulnerabilitySeverity.HIGH
    
    @property
    def location_str(self) -> str:
        """Get a string representation of the vulnerability location."""
        if self.file_path and self.line_number:
            return f"{self.file_path}:{self.line_number}"
        elif self.file_path:
            return self.file_path
        else:
            return "Unknown location"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the vulnerability to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "scanner_type": self.scanner_type.value if self.scanner_type else None,
            "cve_id": self.cve_id,
            "cwe_id": self.cwe_id,
            "remediation": self.remediation,
            "references": self.references,
            "discovered_at": self.discovered_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vulnerability':
        """Create a vulnerability from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            severity=VulnerabilitySeverity(data["severity"]),
            file_path=data.get("file_path"),
            line_number=data.get("line_number"),
            scanner_type=SecurityScannerType(data["scanner_type"]) if data.get("scanner_type") else None,
            cve_id=data.get("cve_id"),
            cwe_id=data.get("cwe_id"),
            remediation=data.get("remediation"),
            references=data.get("references", []),
            discovered_at=data.get("discovered_at", time.time())
        )


@dataclass
class ScanResult:
    """Class representing a security scan result."""
    scanner_type: SecurityScannerType
    vulnerabilities: List[Vulnerability]
    scan_time: float
    scan_duration: float
    target: str
    success: bool
    error_message: Optional[str] = None
    raw_output: Optional[str] = None
    
    @property
    def vulnerability_count(self) -> int:
        """Get the total number of vulnerabilities."""
        return len(self.vulnerabilities)
    
    @property
    def critical_count(self) -> int:
        """Get the number of critical vulnerabilities."""
        return sum(1 for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL)
    
    @property
    def high_count(self) -> int:
        """Get the number of high severity vulnerabilities."""
        return sum(1 for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.HIGH)
    
    @property
    def medium_count(self) -> int:
        """Get the number of medium severity vulnerabilities."""
        return sum(1 for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.MEDIUM)
    
    @property
    def low_count(self) -> int:
        """Get the number of low severity vulnerabilities."""
        return sum(1 for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.LOW)
    
    @property
    def info_count(self) -> int:
        """Get the number of info vulnerabilities."""
        return sum(1 for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.INFO)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the scan result to a dictionary."""
        return {
            "scanner_type": self.scanner_type.value,
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "scan_time": self.scan_time,
            "scan_duration": self.scan_duration,
            "target": self.target,
            "success": self.success,
            "error_message": self.error_message,
            "vulnerability_count": self.vulnerability_count,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "info_count": self.info_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScanResult':
        """Create a scan result from a dictionary."""
        return cls(
            scanner_type=SecurityScannerType(data["scanner_type"]),
            vulnerabilities=[Vulnerability.from_dict(v) for v in data["vulnerabilities"]],
            scan_time=data["scan_time"],
            scan_duration=data["scan_duration"],
            target=data["target"],
            success=data["success"],
            error_message=data.get("error_message"),
            raw_output=data.get("raw_output")
        )


class SecurityScanner:
    """Base class for security scanners."""
    
    def __init__(self, scanner_type: SecurityScannerType):
        """
        Initialize the security scanner.
        
        Args:
            scanner_type: Type of security scanner
        """
        self.scanner_type = scanner_type
        self.logger = logging.getLogger(__name__)
    
    def scan(self, target: str, options: Dict[str, Any] = None) -> ScanResult:
        """
        Scan a target for security vulnerabilities.
        
        Args:
            target: Target to scan (file path, directory path, URL, etc.)
            options: Scanner-specific options
            
        Returns:
            Scan result
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def _create_scan_result(self, target: str, vulnerabilities: List[Vulnerability],
                          scan_time: float, scan_duration: float, success: bool,
                          error_message: Optional[str] = None, raw_output: Optional[str] = None) -> ScanResult:
        """
        Create a scan result.
        
        Args:
            target: Target that was scanned
            vulnerabilities: List of vulnerabilities found
            scan_time: Time when the scan was performed
            scan_duration: Duration of the scan in seconds
            success: Whether the scan was successful
            error_message: Error message if the scan failed
            raw_output: Raw output from the scanner
            
        Returns:
            Scan result
        """
        return ScanResult(
            scanner_type=self.scanner_type,
            vulnerabilities=vulnerabilities,
            scan_time=scan_time,
            scan_duration=scan_duration,
            target=target,
            success=success,
            error_message=error_message,
            raw_output=raw_output
        )


class SnykScanner(SecurityScanner):
    """
    Snyk security scanner integration.
    
    This class provides functionality to scan for vulnerabilities using Snyk.
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Snyk scanner.
        
        Args:
            api_token: Snyk API token
        """
        super().__init__(SecurityScannerType.SNYK)
        self.api_token = api_token
    
    def scan(self, target: str, options: Dict[str, Any] = None) -> ScanResult:
        """
        Scan a target for security vulnerabilities using Snyk.
        
        Args:
            target: Target to scan (file path, directory path)
            options: Scanner-specific options
            
        Returns:
            Scan result
        """
        if options is None:
            options = {}
        
        start_time = time.time()
        scan_time = start_time
        
        try:
            # Check if Snyk CLI is installed
            self._check_snyk_cli()
            
            # Prepare command
            cmd = ["snyk", "test", "--json"]
            
            # Add API token if provided
            if self.api_token:
                cmd.extend(["--api-token", self.api_token])
            
            # Add target
            cmd.append(target)
            
            # Add options
            for key, value in options.items():
                if isinstance(value, bool) and value:
                    cmd.append(f"--{key}")
                elif not isinstance(value, bool):
                    cmd.append(f"--{key}={value}")
            
            # Run Snyk scan
            self.logger.info(f"Running Snyk scan on {target}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit code
            )
            
            # Parse output
            if result.returncode == 0:
                # No vulnerabilities found
                self.logger.info(f"No vulnerabilities found in {target}")
                return self._create_scan_result(
                    target=target,
                    vulnerabilities=[],
                    scan_time=scan_time,
                    scan_duration=time.time() - start_time,
                    success=True,
                    raw_output=result.stdout
                )
            elif result.returncode == 1:
                # Vulnerabilities found
                self.logger.warning(f"Vulnerabilities found in {target}")
                vulnerabilities = self._parse_snyk_output(result.stdout, target)
                return self._create_scan_result(
                    target=target,
                    vulnerabilities=vulnerabilities,
                    scan_time=scan_time,
                    scan_duration=time.time() - start_time,
                    success=True,
                    raw_output=result.stdout
                )
            else:
                # Error
                self.logger.error(f"Snyk scan failed: {result.stderr}")
                return self._create_scan_result(
                    target=target,
                    vulnerabilities=[],
                    scan_time=scan_time,
                    scan_duration=time.time() - start_time,
                    success=False,
                    error_message=result.stderr,
                    raw_output=result.stdout
                )
        
        except Exception as e:
            self.logger.error(f"Error running Snyk scan: {e}")
            return self._create_scan_result(
                target=target,
                vulnerabilities=[],
                scan_time=scan_time,
                scan_duration=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def _check_snyk_cli(self):
        """
        Check if Snyk CLI is installed.
        
        Raises:
            RuntimeError: If Snyk CLI is not installed
        """
        try:
            subprocess.run(
                ["snyk", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError("Snyk CLI is not installed")
    
    def _parse_snyk_output(self, output: str, target: str) -> List[Vulnerability]:
        """
        Parse Snyk output to extract vulnerabilities.
        
        Args:
            output: Snyk output in JSON format
            target: Target that was scanned
            
        Returns:
            List of vulnerabilities
        """
        vulnerabilities = []
        
        try:
            data = json.loads(output)
            
            # Process vulnerabilities
            if "vulnerabilities" in data:
                for vuln_data in data["vulnerabilities"]:
                    severity = vuln_data.get("severity", "").lower()
                    if severity == "critical":
                        severity_enum = VulnerabilitySeverity.CRITICAL
                    elif severity == "high":
                        severity_enum = VulnerabilitySeverity.HIGH
                    elif severity == "medium":
                        severity_enum = VulnerabilitySeverity.MEDIUM
                    elif severity == "low":
                        severity_enum = VulnerabilitySeverity.LOW
                    else:
                        severity_enum = VulnerabilitySeverity.INFO
                    
                    vuln = Vulnerability(
                        id=vuln_data.get("id", "unknown"),
                        title=vuln_data.get("title", "Unknown vulnerability"),
                        description=vuln_data.get("description", "No description available"),
                        severity=severity_enum,
                        file_path=vuln_data.get("packageName", target),
                        scanner_type=SecurityScannerType.SNYK,
                        cve_id=vuln_data.get("identifiers", {}).get("CVE", [None])[0],
                        cwe_id=vuln_data.get("identifiers", {}).get("CWE", [None])[0],
                        remediation=vuln_data.get("remediation", {}).get("advice", "No remediation advice available"),
                        references=[vuln_data.get("url", "")]
                    )
                    
                    vulnerabilities.append(vuln)
        
        except json.JSONDecodeError:
            self.logger.error("Failed to parse Snyk output as JSON")
        except Exception as e:
            self.logger.error(f"Error parsing Snyk output: {e}")
        
        return vulnerabilities


class SonarQubeScanner(SecurityScanner):
    """
    SonarQube security scanner integration.
    
    This class provides functionality to scan for vulnerabilities using SonarQube.
    """
    
    def __init__(self, server_url: str, token: Optional[str] = None,
               username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the SonarQube scanner.
        
        Args:
            server_url: SonarQube server URL
            token: SonarQube authentication token
            username: SonarQube username (alternative to token)
            password: SonarQube password (alternative to token)
        """
        super().__init__(SecurityScannerType.SONARQUBE)
        self.server_url = server_url
        self.token = token
        self.username = username
        self.password = password
    
    def scan(self, target: str, options: Dict[str, Any] = None) -> ScanResult:
        """
        Scan a target for security vulnerabilities using SonarQube.
        
        Args:
            target: Target to scan (directory path)
            options: Scanner-specific options
            
        Returns:
            Scan result
        """
        if options is None:
            options = {}
        
        start_time = time.time()
        scan_time = start_time
        
        try:
            # Check if SonarScanner is installed
            self._check_sonar_scanner()
            
            # Create a temporary properties file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".properties", delete=False) as f:
                properties_file = f.name
                
                # Write basic properties
                f.write(f"sonar.projectKey={options.get('project_key', 'toronto-ai-scan')}\n")
                f.write(f"sonar.projectName={options.get('project_name', 'Toronto AI Scan')}\n")
                f.write(f"sonar.projectVersion={options.get('project_version', '1.0')}\n")
                f.write(f"sonar.sources={target}\n")
                f.write(f"sonar.host.url={self.server_url}\n")
                
                # Add authentication
                if self.token:
                    f.write(f"sonar.login={self.token}\n")
                elif self.username and self.password:
                    f.write(f"sonar.login={self.username}\n")
                    f.write(f"sonar.password={self.password}\n")
                
                # Add additional properties
                for key, value in options.items():
                    if key not in ["project_key", "project_name", "project_version"]:
                        f.write(f"sonar.{key}={value}\n")
            
            # Run SonarScanner
            self.logger.info(f"Running SonarQube scan on {target}")
            result = subprocess.run(
                ["sonar-scanner", f"-Dproject.settings={properties_file}"],
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit code
            )
            
            # Clean up properties file
            os.unlink(properties_file)
            
            # Check result
            if result.returncode == 0:
                # Scan completed successfully
                self.logger.info(f"SonarQube scan completed for {target}")
                
                # Fetch issues from SonarQube API
                project_key = options.get("project_key", "toronto-ai-scan")
                vulnerabilities = self._fetch_issues(project_key)
                
                return self._create_scan_result(
                    target=target,
                    vulnerabilities=vulnerabilities,
                    scan_time=scan_time,
                    scan_duration=time.time() - start_time,
                    success=True,
                    raw_output=result.stdout
                )
            else:
                # Error
                self.logger.error(f"SonarQube scan failed: {result.stderr}")
                return self._create_scan_result(
                    target=target,
                    vulnerabilities=[],
                    scan_time=scan_time,
                    scan_duration=time.time() - start_time,
                    success=False,
                    error_message=result.stderr,
                    raw_output=result.stdout
                )
        
        except Exception as e:
            self.logger.error(f"Error running SonarQube scan: {e}")
            return self._create_scan_result(
                target=target,
                vulnerabilities=[],
                scan_time=scan_time,
                scan_duration=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def _check_sonar_scanner(self):
        """
        Check if SonarScanner is installed.
        
        Raises:
            RuntimeError: If SonarScanner is not installed
        """
        try:
            subprocess.run(
                ["sonar-scanner", "-v"],
                capture_output=True,
                text=True,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError("SonarScanner is not installed")
    
    def _fetch_issues(self, project_key: str) -> List[Vulnerability]:
        """
        Fetch issues from SonarQube API.
        
        Args:
            project_key: SonarQube project key
            
        Returns:
            List of vulnerabilities
        """
        vulnerabilities = []
        
        try:
            # Prepare authentication
            auth = None
            if self.token:
                auth = (self.token, "")
            elif self.username and self.password:
                auth = (self.username, self.password)
            
            # Fetch issues
            url = f"{self.server_url}/api/issues/search"
            params = {
                "componentKeys": project_key,
                "types": "VULNERABILITY",
                "ps": 500  # Page size
            }
            
            response = requests.get(url, params=params, auth=auth)
            response.raise_for_status()
            
            data = response.json()
            
            # Process issues
            if "issues" in data:
                for issue in data["issues"]:
                    severity = issue.get("severity", "").lower()
                    if severity == "blocker":
                        severity_enum = VulnerabilitySeverity.CRITICAL
                    elif severity == "critical":
                        severity_enum = VulnerabilitySeverity.HIGH
                    elif severity == "major":
                        severity_enum = VulnerabilitySeverity.MEDIUM
                    elif severity == "minor":
                        severity_enum = VulnerabilitySeverity.LOW
                    else:
                        severity_enum = VulnerabilitySeverity.INFO
                    
                    vuln = Vulnerability(
                        id=issue.get("key", "unknown"),
                        title=issue.get("message", "Unknown vulnerability"),
                        description=issue.get("message", "No description available"),
                        severity=severity_enum,
                        file_path=issue.get("component", ""),
                        line_number=issue.get("line"),
                        scanner_type=SecurityScannerType.SONARQUBE,
                        cwe_id=None,  # SonarQube doesn't provide CWE IDs directly
                        remediation=None,  # SonarQube doesn't provide remediation advice directly
                        references=[f"{self.server_url}/project/issues?id={project_key}&issues={issue.get('key', '')}"]
                    )
                    
                    vulnerabilities.append(vuln)
        
        except Exception as e:
            self.logger.error(f"Error fetching issues from SonarQube: {e}")
        
        return vulnerabilities


class SemgrepScanner(SecurityScanner):
    """
    Semgrep security scanner integration.
    
    This class provides functionality to scan for vulnerabilities using Semgrep.
    """
    
    def __init__(self):
        """Initialize the Semgrep scanner."""
        super().__init__(SecurityScannerType.SEMGREP)
    
    def scan(self, target: str, options: Dict[str, Any] = None) -> ScanResult:
        """
        Scan a target for security vulnerabilities using Semgrep.
        
        Args:
            target: Target to scan (file path, directory path)
            options: Scanner-specific options
            
        Returns:
            Scan result
        """
        if options is None:
            options = {}
        
        start_time = time.time()
        scan_time = start_time
        
        try:
            # Check if Semgrep is installed
            self._check_semgrep()
            
            # Prepare command
            cmd = ["semgrep", "--json", "--config", options.get("config", "auto")]
            
            # Add target
            cmd.append(target)
            
            # Add options
            for key, value in options.items():
                if key != "config":
                    if isinstance(value, bool) and value:
                        cmd.append(f"--{key}")
                    elif not isinstance(value, bool):
                        cmd.append(f"--{key}")
                        cmd.append(str(value))
            
            # Run Semgrep scan
            self.logger.info(f"Running Semgrep scan on {target}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit code
            )
            
            # Parse output
            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                self.logger.info(f"Semgrep scan completed for {target}")
                vulnerabilities = self._parse_semgrep_output(result.stdout, target)
                return self._create_scan_result(
                    target=target,
                    vulnerabilities=vulnerabilities,
                    scan_time=scan_time,
                    scan_duration=time.time() - start_time,
                    success=True,
                    raw_output=result.stdout
                )
            else:
                # Error
                self.logger.error(f"Semgrep scan failed: {result.stderr}")
                return self._create_scan_result(
                    target=target,
                    vulnerabilities=[],
                    scan_time=scan_time,
                    scan_duration=time.time() - start_time,
                    success=False,
                    error_message=result.stderr,
                    raw_output=result.stdout
                )
        
        except Exception as e:
            self.logger.error(f"Error running Semgrep scan: {e}")
            return self._create_scan_result(
                target=target,
                vulnerabilities=[],
                scan_time=scan_time,
                scan_duration=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def _check_semgrep(self):
        """
        Check if Semgrep is installed.
        
        Raises:
            RuntimeError: If Semgrep is not installed
        """
        try:
            subprocess.run(
                ["semgrep", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError("Semgrep is not installed")
    
    def _parse_semgrep_output(self, output: str, target: str) -> List[Vulnerability]:
        """
        Parse Semgrep output to extract vulnerabilities.
        
        Args:
            output: Semgrep output in JSON format
            target: Target that was scanned
            
        Returns:
            List of vulnerabilities
        """
        vulnerabilities = []
        
        try:
            data = json.loads(output)
            
            # Process results
            if "results" in data:
                for result in data["results"]:
                    # Map Semgrep severity to our severity enum
                    severity_str = result.get("extra", {}).get("severity", "").lower()
                    if severity_str == "error":
                        severity_enum = VulnerabilitySeverity.HIGH
                    elif severity_str == "warning":
                        severity_enum = VulnerabilitySeverity.MEDIUM
                    elif severity_str == "info":
                        severity_enum = VulnerabilitySeverity.LOW
                    else:
                        severity_enum = VulnerabilitySeverity.INFO
                    
                    # Extract CWE if available
                    cwe_id = None
                    metadata = result.get("extra", {}).get("metadata", {})
                    if "cwe" in metadata:
                        cwe_id = f"CWE-{metadata['cwe']}"
                    
                    vuln = Vulnerability(
                        id=result.get("check_id", "unknown"),
                        title=result.get("extra", {}).get("message", "Unknown vulnerability"),
                        description=result.get("extra", {}).get("message", "No description available"),
                        severity=severity_enum,
                        file_path=result.get("path", ""),
                        line_number=result.get("start", {}).get("line"),
                        scanner_type=SecurityScannerType.SEMGREP,
                        cwe_id=cwe_id,
                        remediation=None,  # Semgrep doesn't provide remediation advice directly
                        references=[result.get("extra", {}).get("metadata", {}).get("references", [])]
                    )
                    
                    vulnerabilities.append(vuln)
        
        except json.JSONDecodeError:
            self.logger.error("Failed to parse Semgrep output as JSON")
        except Exception as e:
            self.logger.error(f"Error parsing Semgrep output: {e}")
        
        return vulnerabilities


class SecurityScanningManager:
    """
    Manager class for security scanning tools.
    
    This class provides a unified interface for scanning with different security tools.
    """
    
    def __init__(self):
        """Initialize the security scanning manager."""
        self.scanners: Dict[SecurityScannerType, SecurityScanner] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_scanner(self, scanner: SecurityScanner):
        """
        Register a security scanner.
        
        Args:
            scanner: Security scanner to register
        """
        self.scanners[scanner.scanner_type] = scanner
        self.logger.info(f"Registered {scanner.scanner_type.value} scanner")
    
    def unregister_scanner(self, scanner_type: SecurityScannerType):
        """
        Unregister a security scanner.
        
        Args:
            scanner_type: Type of security scanner to unregister
        """
        if scanner_type in self.scanners:
            self.scanners.pop(scanner_type)
            self.logger.info(f"Unregistered {scanner_type.value} scanner")
    
    def get_scanner(self, scanner_type: SecurityScannerType) -> Optional[SecurityScanner]:
        """
        Get a security scanner by type.
        
        Args:
            scanner_type: Type of security scanner to get
            
        Returns:
            Security scanner, or None if not found
        """
        return self.scanners.get(scanner_type)
    
    def scan(self, target: str, scanner_type: SecurityScannerType,
           options: Dict[str, Any] = None) -> ScanResult:
        """
        Scan a target for security vulnerabilities.
        
        Args:
            target: Target to scan
            scanner_type: Type of security scanner to use
            options: Scanner-specific options
            
        Returns:
            Scan result
        """
        scanner = self.get_scanner(scanner_type)
        if not scanner:
            self.logger.error(f"Scanner {scanner_type.value} not registered")
            return ScanResult(
                scanner_type=scanner_type,
                vulnerabilities=[],
                scan_time=time.time(),
                scan_duration=0.0,
                target=target,
                success=False,
                error_message=f"Scanner {scanner_type.value} not registered"
            )
        
        return scanner.scan(target, options)
    
    def scan_with_all(self, target: str, options: Dict[SecurityScannerType, Dict[str, Any]] = None) -> Dict[SecurityScannerType, ScanResult]:
        """
        Scan a target with all registered scanners.
        
        Args:
            target: Target to scan
            options: Scanner-specific options for each scanner type
            
        Returns:
            Dictionary mapping scanner types to scan results
        """
        if options is None:
            options = {}
        
        results = {}
        
        for scanner_type, scanner in self.scanners.items():
            scanner_options = options.get(scanner_type, {})
            results[scanner_type] = scanner.scan(target, scanner_options)
        
        return results
    
    def get_aggregate_vulnerabilities(self, scan_results: Dict[SecurityScannerType, ScanResult]) -> List[Vulnerability]:
        """
        Get an aggregated list of vulnerabilities from multiple scan results.
        
        Args:
            scan_results: Dictionary mapping scanner types to scan results
            
        Returns:
            Aggregated list of vulnerabilities
        """
        vulnerabilities = []
        
        for scanner_type, result in scan_results.items():
            if result.success:
                vulnerabilities.extend(result.vulnerabilities)
        
        return vulnerabilities
    
    def get_vulnerability_summary(self, scan_results: Dict[SecurityScannerType, ScanResult]) -> Dict[str, int]:
        """
        Get a summary of vulnerabilities from multiple scan results.
        
        Args:
            scan_results: Dictionary mapping scanner types to scan results
            
        Returns:
            Dictionary with vulnerability counts by severity
        """
        summary = {
            "total": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        }
        
        for scanner_type, result in scan_results.items():
            if result.success:
                summary["total"] += result.vulnerability_count
                summary["critical"] += result.critical_count
                summary["high"] += result.high_count
                summary["medium"] += result.medium_count
                summary["low"] += result.low_count
                summary["info"] += result.info_count
        
        return summary
