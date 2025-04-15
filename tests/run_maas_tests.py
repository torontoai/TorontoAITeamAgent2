"""
Test runner for MaAS integration tests.

This script runs the MaAS integration tests and handles dependency setup.
"""

import os
import sys
import unittest
import logging
import importlib
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install required dependencies for testing."""
    logger.info("Installing required dependencies...")
    
    dependencies = [
        "pydantic",
        "matplotlib",
        "networkx",
        "plotly",
        "numpy",
        "pytest"
    ]
    
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            logger.info(f"Dependency {dep} already installed")
        except ImportError:
            logger.info(f"Installing dependency: {dep}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

def create_test_directories():
    """Create directories needed for tests."""
    logger.info("Creating test directories...")
    
    test_dirs = [
        os.path.join(os.path.dirname(__file__), "test_output"),
        os.path.join(os.path.dirname(__file__), "test_output", "evaluation_results")
    ]
    
    for directory in test_dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def fix_import_paths():
    """Fix common import path issues in the codebase."""
    logger.info("Fixing import paths...")
    
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.info(f"Added {project_root} to Python path")

def run_tests():
    """Run the MaAS integration tests."""
    logger.info("Running MaAS integration tests...")
    
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), pattern="test_maas_*.py")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    logger.info("Starting MaAS integration test runner...")
    
    # Setup for tests
    install_dependencies()
    create_test_directories()
    fix_import_paths()
    
    # Run tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
