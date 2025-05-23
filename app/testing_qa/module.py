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
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCase(BaseModel):
    """Test case model."""
    id: Optional[str] = None
    name: str
    description: str
    test_type: str  # unit, integration, e2e, etc.
    expected_result: str
    actual_result: Optional[str] = None
    status: str = "pending"  # pending, passed, failed
    
class TestSuite(BaseModel):
    """Test suite model."""
    id: Optional[str] = None
    name: str
    description: str
    test_cases: List[str] = []  # List of test case IDs
    
class CodeQualityReport(BaseModel):
    """Code quality report model."""
    id: Optional[str] = None
    project_id: str
    timestamp: str
    metrics: Dict[str, Any]
    issues: List[Dict[str, Any]] = []
    
class SecurityScan(BaseModel):
    """Security scan model."""
    id: Optional[str] = None
    project_id: str
    timestamp: str
    vulnerabilities: List[Dict[str, Any]] = []
    risk_level: str = "low"  # low, medium, high, critical
    
class PerformanceTest(BaseModel):
    """Performance test model."""
    id: Optional[str] = None
    name: str
    description: str
    metrics: Dict[str, Any]
    status: str = "pending"  # pending, passed, failed
    
class UserAcceptanceTest(BaseModel):
    """User acceptance test model."""
    id: Optional[str] = None
    name: str
    description: str
    steps: List[str]
    expected_result: str
    actual_result: Optional[str] = None
    status: str = "pending"  # pending, passed, failed

class TestingQAModule:
    """Testing and QA module for the multi-agent team system.
    Provides comprehensive testing and quality assurance capabilities."""
    
    def __init__(self):
        """Initialize the testing and QA module."""
        self.test_cases = {}
        self.test_suites = {}
        self.code_quality_reports = {}
        self.security_scans = {}
        self.performance_tests = {}
        self.user_acceptance_tests = {}
        
    async def create_test_case(self, test_case: TestCase) -> str:
        """
        Create a new test case.
        
        Args:
            test_case: Test case data
            
        Returns:
            Test case ID
        """
        # Generate test case ID if not provided
        if not test_case.id:
            test_case.id = f"tc_{len(self.test_cases) + 1}"
        
        # Store test case
        self.test_cases[test_case.id] = test_case.dict()
        
        return test_case.id
    
    async def get_test_case(self, test_case_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test case by ID.
        
        Args:
            test_case_id: Test case ID
            
        Returns:
            Test case data or None if not found
        """
        return self.test_cases.get(test_case_id)
    
    async def update_test_case(self, test_case_id: str, test_case_data: Dict[str, Any]) -> bool:
        """
        Update test case data.
        
        Args:
            test_case_id: Test case ID
            test_case_data: Updated test case data
            
        Returns:
            True if test case was updated successfully, False otherwise
        """
        if test_case_id not in self.test_cases:
            return False
        
        # Update test case data
        self.test_cases[test_case_id].update(test_case_data)
        
        return True
    
    async def delete_test_case(self, test_case_id: str) -> bool:
        """
        Delete a test case.
        
        Args:
            test_case_id: Test case ID
            
        Returns:
            True if test case was deleted successfully, False otherwise
        """
        if test_case_id not in self.test_cases:
            return False
        
        # Delete test case
        del self.test_cases[test_case_id]
        
        # Remove test case from test suites
        for test_suite in self.test_suites.values():
            if test_case_id in test_suite["test_cases"]:
                test_suite["test_cases"].remove(test_case_id)
        
        return True
    
    async def create_test_suite(self, test_suite: TestSuite) -> str:
        """
        Create a new test suite.
        
        Args:
            test_suite: Test suite data
            
        Returns:
            Test suite ID
        """
        # Generate test suite ID if not provided
        if not test_suite.id:
            test_suite.id = f"ts_{len(self.test_suites) + 1}"
        
        # Validate test cases
        for test_case_id in test_suite.test_cases:
            if test_case_id not in self.test_cases:
                raise ValueError(f"Test case {test_case_id} not found")
        
        # Store test suite
        self.test_suites[test_suite.id] = test_suite.dict()
        
        return test_suite.id
    
    async def get_test_suite(self, test_suite_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test suite by ID.
        
        Args:
            test_suite_id: Test suite ID
            
        Returns:
            Test suite data or None if not found
        """
        return self.test_suites.get(test_suite_id)
    
    async def update_test_suite(self, test_suite_id: str, test_suite_data: Dict[str, Any]) -> bool:
        """
        Update test suite data.
        
        Args:
            test_suite_id: Test suite ID
            test_suite_data: Updated test suite data
            
        Returns:
            True if test suite was updated successfully, False otherwise
        """
        if test_suite_id not in self.test_suites:
            return False
        
        # Validate test cases if provided
        if "test_cases" in test_suite_data:
            for test_case_id in test_suite_data["test_cases"]:
                if test_case_id not in self.test_cases:
                    raise ValueError(f"Test case {test_case_id} not found")
        
        # Update test suite data
        self.test_suites[test_suite_id].update(test_suite_data)
        
        return True
    
    async def delete_test_suite(self, test_suite_id: str) -> bool:
        """
        Delete a test suite.
        
        Args:
            test_suite_id: Test suite ID
            
        Returns:
            True if test suite was deleted successfully, False otherwise
        """
        if test_suite_id not in self.test_suites:
            return False
        
        # Delete test suite
        del self.test_suites[test_suite_id]
        
        return True
    
    async def run_test_case(self, test_case_id: str) -> Dict[str, Any]:
        """
        Run a test case.
        
        Args:
            test_case_id: Test case ID
            
        Returns:
            Test case result
        """
        if test_case_id not in self.test_cases:
            raise ValueError(f"Test case {test_case_id} not found")
        
        test_case = self.test_cases[test_case_id]
        
        # Simulate test execution
        # In a real implementation, this would execute the actual test
        import random
        success = random.random() > 0.2  # 80% chance of success
        
        # Update test case with result
        test_case["status"] = "passed" if success else "failed"
        test_case["actual_result"] = test_case["expected_result"] if success else "Test failed"
        
        return test_case
    
    async def run_test_suite(self, test_suite_id: str) -> Dict[str, Any]:
        """
        Run a test suite.
        
        Args:
            test_suite_id: Test suite ID
            
        Returns:
            Test suite result
        """
        if test_suite_id not in self.test_suites:
            raise ValueError(f"Test suite {test_suite_id} not found")
        
        test_suite = self.test_suites[test_suite_id]
        
        # Run all test cases in the suite
        results = []
        for test_case_id in test_suite["test_cases"]:
            try:
                result = await self.run_test_case(test_case_id)
                results.append(result)
            except ValueError as e:
                # Skip test cases that don't exist
                continue
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for result in results if result["status"] == "passed")
        failed_tests = total_tests - passed_tests
        
        return {
            "test_suite_id": test_suite_id,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "results": results
        }
    
    async def generate_code_quality_report(self, project_id: str, code_path: str) -> CodeQualityReport:
        """
        Generate a code quality report.
        
        Args:
            project_id: Project ID
            code_path: Path to the code to analyze
            
        Returns:
            Code quality report
        """
        # In a real implementation, this would run code quality tools like ESLint, Pylint, etc.
        # For now, we'll simulate a report
        
        import datetime
        
        metrics = {
            "maintainability_index": 85,  # 0-100, higher is better
            "cyclomatic_complexity": 15,  # Lower is better
            "code_duplication": 5,  # Percentage, lower is better
            "comment_ratio": 20,  # Percentage, higher is better
            "test_coverage": 75  # Percentage, higher is better
        }
        
        issues = [
            {
                "type": "code_style",
                "severity": "low",
                "message": "Line exceeds maximum length",
                "file": f"{code_path}/example.py",
                "line": 42
            },
            {
                "type": "maintainability",
                "severity": "medium",
                "message": "Function is too complex (cyclomatic complexity 15)",
                "file": f"{code_path}/complex.py",
                "line": 10
            },
            {
                "type": "duplication",
                "severity": "medium",
                "message": "Duplicated code found",
                "file": f"{code_path}/util.py",
                "line": 25
            }
        ]
        
        report = CodeQualityReport(
            id=f"cqr_{len(self.code_quality_reports) + 1}",
            project_id=project_id,
            timestamp=datetime.datetime.now().isoformat(),
            metrics=metrics,
            issues=issues
        )
        
        # Store report
        self.code_quality_reports[report.id] = report.dict()
        
        return report
    
    async def get_code_quality_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        Get code quality report by ID.
        
        Args:
            report_id: Report ID
            
        Returns:
            Code quality report or None if not found
        """
        return self.code_quality_reports.get(report_id)
    
    async def run_security_scan(self, project_id: str, code_path: str) -> SecurityScan:
        """
        Run a security scan.
        
        Args:
            project_id: Project ID
            code_path: Path to the code to scan
            
        Returns:
            Security scan result
        """
        # In a real implementation, this would run security scanning tools
        # For now, we'll simulate a scan
        
        import datetime
        
        vulnerabilities = [
            {
                "type": "sql_injection",
                "severity": "high",
                "message": "Possible SQL injection vulnerability",
                "file": f"{code_path}/database.py",
                "line": 57,
                "cve": "CVE-2021-12345"
            },
            {
                "type": "xss",
                "severity": "medium",
                "message": "Possible XSS vulnerability",
                "file": f"{code_path}/frontend.js",
                "line": 123,
                "cve": None
            },
            {
                "type": "dependency",
                "severity": "low",
                "message": "Outdated dependency with known vulnerabilities",
                "file": f"{code_path}/package.json",
                "line": 15,
                "cve": "CVE-2022-67890"
            }
        ]
        
        # Determine overall risk level
        risk_level = "low"
        for vuln in vulnerabilities:
            if vuln["severity"] == "critical":
                risk_level = "critical"
                break
            elif vuln["severity"] == "high" and risk_level != "critical":
                risk_level = "high"
            elif vuln["severity"] == "medium" and risk_level not in ["critical", "high"]:
                risk_level = "medium"
        
        scan = SecurityScan(
            id=f"ss_{len(self.security_scans) + 1}",
            project_id=project_id,
            timestamp=datetime.datetime.now().isoformat(),
            vulnerabilities=vulnerabilities,
            risk_level=risk_level
        )
        
        # Store scan
        self.security_scans[scan.id] = scan.dict()
        
        return scan
    
    async def get_security_scan(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get security scan by ID.
        
        Args:
            scan_id: Scan ID
            
        Returns:
            Security scan or None if not found
        """
        return self.security_scans.get(scan_id)
    
    async def run_performance_test(self, name: str, description: str, endpoint: str) -> PerformanceTest:
        """
        Run a performance test.
        
        Args:
            name: Test name
            description: Test description
            endpoint: Endpoint to test
            
        Returns:
            Performance test result
        """
        # In a real implementation, this would run performance testing tools
        # For now, we'll simulate a test
        
        # Simulate test execution
        import random
        
        metrics = {
            "requests_per_second": random.uniform(50, 200),
            "average_response_time": random.uniform(50, 500),  # ms
            "p95_response_time": random.uniform(100, 1000),  # ms
            "p99_response_time": random.uniform(200, 2000),  # ms
            "error_rate": random.uniform(0, 0.05),  # 0-1
            "cpu_usage": random.uniform(10, 90),  # percentage
            "memory_usage": random.uniform(100, 1000)  # MB
        }
        
        # Determine test status
        status = "passed"
        if metrics["average_response_time"] > 300 or metrics["error_rate"] > 0.01:
            status = "failed"
        
        test = PerformanceTest(
            id=f"pt_{len(self.performance_tests) + 1}",
            name=name,
            description=description,
            metrics=metrics,
            status=status
        )
        
        # Store test
        self.performance_tests[test.id] = test.dict()
        
        return test
    
    async def get_performance_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get performance test by ID.
        
        Args:
            test_id: Test ID
            
        Returns:
            Performance test or None if not found
        """
        return self.performance_tests.get(test_id)
    
    async def create_user_acceptance_test(self, test: UserAcceptanceTest) -> str:
        """
        Create a new user acceptance test.
        
        Args:
            test: User acceptance test data
            
        Returns:
            Test ID
        """
        # Generate test ID if not provided
        if not test.id:
            test.id = f"uat_{len(self.user_acceptance_tests) + 1}"
        
        # Store test
        self.user_acceptance_tests[test.id] = test.dict()
        
        return test.id
    
    async def get_user_acceptance_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user acceptance test by ID.
        
        Args:
            test_id: Test ID
            
        Returns:
            User acceptance test or None if not found
        """
        return self.user_acceptance_tests.get(test_id)
    
    async def update_user_acceptance_test(self, test_id: str, test_data: Dict[str, Any]) -> bool:
        """
        Update user acceptance test data.
        
        Args:
            test_id: Test ID
            test_data: Updated test data
            
        Returns:
            True if test was updated successfully, False otherwise
        """
        if test_id not in self.user_acceptance_tests:
            return False
        
        # Update test data
        self.user_acceptance_tests[test_id].update(test_data)
        
        return True
    
    async def run_user_acceptance_test(self, test_id: str) -> Dict[str, Any]:
        """
        Run a user acceptance test.
        
        Args:
            test_id: Test ID
            
        Returns:
            Test result
        """
        if test_id not in self.user_acceptance_tests:
            raise ValueError(f"User acceptance test {test_id} not found")
        
        test = self.user_acceptance_tests[test_id]
        
        # Simulate test execution
        # In a real implementation, this would execute the actual test
        import random
        success = random.random() > 0.1  # 90% chance of success
        
        # Update test with result
        test["status"] = "passed" if success else "failed"
        test["actual_result"] = test["expected_result"] if success else "Test failed"
        
        return test
    
    async def generate_test_report(self, project_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive test report for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Test report
        """
        # Collect all test results for the project
        # In a real implementation, this would filter tests by project ID
        
        # For now, we'll use all tests
        test_cases = list(self.test_cases.values())
        test_suites = list(self.test_suites.values())
        code_quality_reports = [r for r in self.code_quality_reports.values() if r["project_id"] == project_id]
        security_scans = [s for s in self.security_scans.values() if s["project_id"] == project_id]
        performance_tests = list(self.performance_tests.values())
        user_acceptance_tests = list(self.user_acceptance_tests.values())
        
        # Calculate summary statistics
        total_test_cases = len(test_cases)
        passed_test_cases = sum(1 for tc in test_cases if tc["status"] == "passed")
        failed_test_cases = sum(1 for tc in test_cases if tc["status"] == "failed")
        pending_test_cases = sum(1 for tc in test_cases if tc["status"] == "pending")
        
        # Get latest code quality report
        latest_code_quality = code_quality_reports[-1] if code_quality_reports else None
        
        # Get latest security scan
        latest_security_scan = security_scans[-1] if security_scans else None
        
        # Calculate performance test summary
        performance_passed = sum(1 for pt in performance_tests if pt["status"] == "passed")
        performance_failed = sum(1 for pt in performance_tests if pt["status"] == "failed")
        
        # Calculate UAT summary
        uat_passed = sum(1 for uat in user_acceptance_tests if uat["status"] == "passed")
        uat_failed = sum(1 for uat in user_acceptance_tests if uat["status"] == "failed")
        uat_pending = sum(1 for uat in user_acceptance_tests if uat["status"] == "pending")
        
        # Generate report
        report = {
            "project_id": project_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": {
                "test_cases": {
                    "total": total_test_cases,
                    "passed": passed_test_cases,
                    "failed": failed_test_cases,
                    "pending": pending_test_cases,
                    "pass_rate": passed_test_cases / total_test_cases if total_test_cases > 0 else 0
                },
                "code_quality": latest_code_quality["metrics"] if latest_code_quality else None,
                "security": {
                    "risk_level": latest_security_scan["risk_level"] if latest_security_scan else None,
                    "vulnerabilities_count": len(latest_security_scan["vulnerabilities"]) if latest_security_scan else 0
                },
                "performance": {
                    "total": len(performance_tests),
                    "passed": performance_passed,
                    "failed": performance_failed,
                    "pass_rate": performance_passed / len(performance_tests) if performance_tests else 0
                },
                "user_acceptance": {
                    "total": len(user_acceptance_tests),
                    "passed": uat_passed,
                    "failed": uat_failed,
                    "pending": uat_pending,
                    "pass_rate": uat_passed / (uat_passed + uat_failed) if (uat_passed + uat_failed) > 0 else 0
                }
            },
            "details": {
                "test_cases": test_cases,
                "test_suites": test_suites,
                "code_quality_reports": code_quality_reports,
                "security_scans": security_scans,
                "performance_tests": performance_tests,
                "user_acceptance_tests": user_acceptance_tests
            }
        }
        
        return report

class TestingQAAPIModule:
    """Testing and QA API module for the multi-agent team system.
    Provides FastAPI routes for testing and quality assurance capabilities."""
    
    def __init__(self, app: FastAPI):
        """Initialize the testing and QA API module.
        
        Args:
            app: FastAPI application"""
        self.app = app
        self.testing_qa = TestingQAModule()
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register routes with the FastAPI app."""
        
        @self.app.post("/api/testing/test-cases", response_model=Dict[str, str])
        async def create_test_case(test_case: TestCase):
            """
            Create a new test case.
            
            Args:
                test_case: Test case data
                
            Returns:
                Test case ID
            """
            try:
                test_case_id = await self.testing_qa.create_test_case(test_case)
                return {"test_case_id": test_case_id}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/testing/test-cases/{test_case_id}", response_model=Dict[str, Any])
        async def get_test_case(test_case_id: str):
            """
            Get test case by ID.
            
            Args:
                test_case_id: Test case ID
                
            Returns:
                Test case data
            """
            test_case = await self.testing_qa.get_test_case(test_case_id)
            if not test_case:
                raise HTTPException(status_code=404, detail=f"Test case {test_case_id} not found")
            return test_case
        
        @self.app.put("/api/testing/test-cases/{test_case_id}", response_model=Dict[str, bool])
        async def update_test_case(test_case_id: str, test_case_data: Dict[str, Any]):
            """
            Update test case data.
            
            Args:
                test_case_id: Test case ID
                test_case_data: Updated test case data
                
            Returns:
                Success status
            """
            success = await self.testing_qa.update_test_case(test_case_id, test_case_data)
            if not success:
                raise HTTPException(status_code=404, detail=f"Test case {test_case_id} not found")
            return {"success": success}
        
        @self.app.delete("/api/testing/test-cases/{test_case_id}", response_model=Dict[str, bool])
        async def delete_test_case(test_case_id: str):
            """
            Delete a test case.
            
            Args:
                test_case_id: Test case ID
                
            Returns:
                Success status
            """
            success = await self.testing_qa.delete_test_case(test_case_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Test case {test_case_id} not found")
            return {"success": success}
        
        @self.app.post("/api/testing/test-suites", response_model=Dict[str, str])
        async def create_test_suite(test_suite: TestSuite):
            """
            Create a new test suite.
            
            Args:
                test_suite: Test suite data
                
            Returns:
                Test suite ID
            """
            try:
                test_suite_id = await self.testing_qa.create_test_suite(test_suite)
                return {"test_suite_id": test_suite_id}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/testing/test-suites/{test_suite_id}", response_model=Dict[str, Any])
        async def get_test_suite(test_suite_id: str):
            """
            Get test suite by ID.
            
            Args:
                test_suite_id: Test suite ID
                
            Returns:
                Test suite data
            """
            test_suite = await self.testing_qa.get_test_suite(test_suite_id)
            if not test_suite:
                raise HTTPException(status_code=404, detail=f"Test suite {test_suite_id} not found")
            return test_suite
        
        @self.app.put("/api/testing/test-suites/{test_suite_id}", response_model=Dict[str, bool])
        async def update_test_suite(test_suite_id: str, test_suite_data: Dict[str, Any]):
            """
            Update test suite data.
            
            Args:
                test_suite_id: Test suite ID
                test_suite_data: Updated test suite data
                
            Returns:
                Success status
            """
            try:
                success = await self.testing_qa.update_test_suite(test_suite_id, test_suite_data)
                if not success:
                    raise HTTPException(status_code=404, detail=f"Test suite {test_suite_id} not found")
                return {"success": success}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.delete("/api/testing/test-suites/{test_suite_id}", response_model=Dict[str, bool])
        async def delete_test_suite(test_suite_id: str):
            """
            Delete a test suite.
            
            Args:
                test_suite_id: Test suite ID
                
            Returns:
                Success status
            """
            success = await self.testing_qa.delete_test_suite(test_suite_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Test suite {test_suite_id} not found")
            return {"success": success}
        
        @self.app.post("/api/testing/test-cases/{test_case_id}/run", response_model=Dict[str, Any])
        async def run_test_case(test_case_id: str):
            """
            Run a test case.
            
            Args:
                test_case_id: Test case ID
                
            Returns:
                Test case result
            """
            try:
                result = await self.testing_qa.run_test_case(test_case_id)
                return result
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/testing/test-suites/{test_suite_id}/run", response_model=Dict[str, Any])
        async def run_test_suite(test_suite_id: str):
            """
            Run a test suite.
            
            Args:
                test_suite_id: Test suite ID
                
            Returns:
                Test suite result
            """
            try:
                result = await self.testing_qa.run_test_suite(test_suite_id)
                return result
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/testing/code-quality", response_model=Dict[str, Any])
        async def generate_code_quality_report(project_id: str, code_path: str):
            """
            Generate a code quality report.
            
            Args:
                project_id: Project ID
                code_path: Path to the code to analyze
                
            Returns:
                Code quality report
            """
            try:
                report = await self.testing_qa.generate_code_quality_report(project_id, code_path)
                return report.dict()
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/testing/code-quality/{report_id}", response_model=Dict[str, Any])
        async def get_code_quality_report(report_id: str):
            """
            Get code quality report by ID.
            
            Args:
                report_id: Report ID
                
            Returns:
                Code quality report
            """
            report = await self.testing_qa.get_code_quality_report(report_id)
            if not report:
                raise HTTPException(status_code=404, detail=f"Code quality report {report_id} not found")
            return report
        
        @self.app.post("/api/testing/security-scan", response_model=Dict[str, Any])
        async def run_security_scan(project_id: str, code_path: str):
            """
            Run a security scan.
            
            Args:
                project_id: Project ID
                code_path: Path to the code to scan
                
            Returns:
                Security scan result
            """
            try:
                scan = await self.testing_qa.run_security_scan(project_id, code_path)
                return scan.dict()
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/testing/security-scan/{scan_id}", response_model=Dict[str, Any])
        async def get_security_scan(scan_id: str):
            """
            Get security scan by ID.
            
            Args:
                scan_id: Scan ID
                
            Returns:
                Security scan
            """
            scan = await self.testing_qa.get_security_scan(scan_id)
            if not scan:
                raise HTTPException(status_code=404, detail=f"Security scan {scan_id} not found")
            return scan
        
        @self.app.post("/api/testing/performance-test", response_model=Dict[str, Any])
        async def run_performance_test(name: str, description: str, endpoint: str):
            """
            Run a performance test.
            
            Args:
                name: Test name
                description: Test description
                endpoint: Endpoint to test
                
            Returns:
                Performance test result
            """
            try:
                test = await self.testing_qa.run_performance_test(name, description, endpoint)
                return test.dict()
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/testing/performance-test/{test_id}", response_model=Dict[str, Any])
        async def get_performance_test(test_id: str):
            """
            Get performance test by ID.
            
            Args:
                test_id: Test ID
                
            Returns:
                Performance test
            """
            test = await self.testing_qa.get_performance_test(test_id)
            if not test:
                raise HTTPException(status_code=404, detail=f"Performance test {test_id} not found")
            return test
        
        @self.app.post("/api/testing/user-acceptance-test", response_model=Dict[str, str])
        async def create_user_acceptance_test(test: UserAcceptanceTest):
            """
            Create a new user acceptance test.
            
            Args:
                test: User acceptance test data
                
            Returns:
                Test ID
            """
            try:
                test_id = await self.testing_qa.create_user_acceptance_test(test)
                return {"test_id": test_id}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/testing/user-acceptance-test/{test_id}", response_model=Dict[str, Any])
        async def get_user_acceptance_test(test_id: str):
            """
            Get user acceptance test by ID.
            
            Args:
                test_id: Test ID
                
            Returns:
                User acceptance test
            """
            test = await self.testing_qa.get_user_acceptance_test(test_id)
            if not test:
                raise HTTPException(status_code=404, detail=f"User acceptance test {test_id} not found")
            return test
        
        @self.app.put("/api/testing/user-acceptance-test/{test_id}", response_model=Dict[str, bool])
        async def update_user_acceptance_test(test_id: str, test_data: Dict[str, Any]):
            """
            Update user acceptance test data.
            
            Args:
                test_id: Test ID
                test_data: Updated test data
                
            Returns:
                Success status
            """
            success = await self.testing_qa.update_user_acceptance_test(test_id, test_data)
            if not success:
                raise HTTPException(status_code=404, detail=f"User acceptance test {test_id} not found")
            return {"success": success}
        
        @self.app.post("/api/testing/user-acceptance-test/{test_id}/run", response_model=Dict[str, Any])
        async def run_user_acceptance_test(test_id: str):
            """
            Run a user acceptance test.
            
            Args:
                test_id: Test ID
                
            Returns:
                Test result
            """
            try:
                result = await self.testing_qa.run_user_acceptance_test(test_id)
                return result
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/testing/report/{project_id}", response_model=Dict[str, Any])
        async def generate_test_report(project_id: str):
            """
            Generate a comprehensive test report for a project.
            
            Args:
                project_id: Project ID
                
            Returns:
                Test report
            """
            try:
                report = await self.testing_qa.generate_test_report(project_id)
                return report
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

# Function to create testing and QA API module
def create_testing_qa_api_module(app: FastAPI) -> TestingQAAPIModule:
    """Create and initialize the testing and QA API module.
    
    Args:
        app: FastAPI application
        
    Returns:
        TestingQAAPIModule instance"""
    return TestingQAAPIModule(app)
