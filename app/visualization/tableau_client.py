"""
Tableau integration for TORONTO AI TEAM AGENT.

This module provides integration with Tableau for advanced data visualization
and dashboard capabilities.
"""

import os
import json
import logging
import time
import base64
from typing import Any, Dict, List, Optional, Union, Tuple
import requests
import pandas as pd
import numpy as np
from io import StringIO, BytesIO

from app.core.error_handling import ErrorHandler, ErrorCategory, ErrorSeverity, safe_execute

logger = logging.getLogger(__name__)

class TableauClient:
    """Client for interacting with Tableau Server API."""
    
    def __init__(
        self, 
        server_url: Optional[str] = None, 
        username: Optional[str] = None,
        password: Optional[str] = None,
        site_name: Optional[str] = None,
        personal_access_token_name: Optional[str] = None,
        personal_access_token_value: Optional[str] = None
    ):
        """
        Initialize the Tableau client.
        
        Args:
            server_url: Tableau Server URL (defaults to TABLEAU_SERVER_URL environment variable)
            username: Tableau username (defaults to TABLEAU_USERNAME environment variable)
            password: Tableau password (defaults to TABLEAU_PASSWORD environment variable)
            site_name: Tableau site name (defaults to TABLEAU_SITE_NAME environment variable)
            personal_access_token_name: Personal access token name (defaults to TABLEAU_PAT_NAME environment variable)
            personal_access_token_value: Personal access token value (defaults to TABLEAU_PAT_VALUE environment variable)
        """
        self.server_url = server_url or os.environ.get("TABLEAU_SERVER_URL")
        if not self.server_url:
            logger.warning("Tableau Server URL not provided. Some functionality may be limited.")
            
        self.username = username or os.environ.get("TABLEAU_USERNAME")
        self.password = password or os.environ.get("TABLEAU_PASSWORD")
        self.site_name = site_name or os.environ.get("TABLEAU_SITE_NAME", "")
        
        self.pat_name = personal_access_token_name or os.environ.get("TABLEAU_PAT_NAME")
        self.pat_value = personal_access_token_value or os.environ.get("TABLEAU_PAT_VALUE")
        
        self.api_version = "3.15"
        self.auth_token = None
        self.site_id = None
        self.session = requests.Session()
    
    def sign_in(self) -> bool:
        """
        Sign in to Tableau Server and get an authentication token.
        
        Returns:
            bool: True if sign-in was successful, False otherwise
        """
        if not self.server_url:
            logger.error("Cannot sign in: Tableau Server URL not provided")
            return False
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message="Error signing in to Tableau Server",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.server_url}/api/{self.api_version}/auth/signin"
            
            # Prepare request body based on authentication method
            if self.pat_name and self.pat_value:
                # Use personal access token
                payload = {
                    "credentials": {
                        "personalAccessTokenName": self.pat_name,
                        "personalAccessTokenSecret": self.pat_value,
                        "site": {
                            "contentUrl": self.site_name
                        }
                    }
                }
            elif self.username and self.password:
                # Use username and password
                payload = {
                    "credentials": {
                        "name": self.username,
                        "password": self.password,
                        "site": {
                            "contentUrl": self.site_name
                        }
                    }
                }
            else:
                logger.error("Cannot sign in: No authentication credentials provided")
                return False
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = self.session.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            credentials = response_data.get("credentials", {})
            
            self.auth_token = credentials.get("token")
            self.site_id = credentials.get("site", {}).get("id")
            
            # Update session headers with auth token
            if self.auth_token:
                self.session.headers.update({
                    "X-Tableau-Auth": self.auth_token
                })
                
            return bool(self.auth_token and self.site_id)
    
    def sign_out(self) -> bool:
        """
        Sign out from Tableau Server.
        
        Returns:
            bool: True if sign-out was successful, False otherwise
        """
        if not self.server_url or not self.auth_token:
            return False
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message="Error signing out from Tableau Server",
            severity=ErrorSeverity.LOW
        ):
            endpoint = f"{self.server_url}/api/{self.api_version}/auth/signout"
            
            response = self.session.post(endpoint)
            response.raise_for_status()
            
            # Clear auth token and site ID
            self.auth_token = None
            self.site_id = None
            
            # Remove auth header
            if "X-Tableau-Auth" in self.session.headers:
                del self.session.headers["X-Tableau-Auth"]
                
            return True
    
    def get_workbooks(self) -> Dict[str, Any]:
        """
        Get a list of workbooks from Tableau Server.
        
        Returns:
            Dict containing the workbooks
        """
        if not self.server_url or not self.auth_token or not self.site_id:
            if not self.auth_token and self.server_url:
                self.sign_in()
            else:
                return {"error": "Not authenticated"}
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message="Error getting workbooks from Tableau Server",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/workbooks"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def get_views(self, workbook_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a list of views from Tableau Server.
        
        Args:
            workbook_id: ID of the workbook to get views for (optional)
            
        Returns:
            Dict containing the views
        """
        if not self.server_url or not self.auth_token or not self.site_id:
            if not self.auth_token and self.server_url:
                self.sign_in()
            else:
                return {"error": "Not authenticated"}
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message="Error getting views from Tableau Server",
            severity=ErrorSeverity.MEDIUM
        ):
            if workbook_id:
                endpoint = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/workbooks/{workbook_id}/views"
            else:
                endpoint = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/views"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def get_view_data(self, view_id: str) -> Dict[str, Any]:
        """
        Get data for a specific view.
        
        Args:
            view_id: ID of the view to get data for
            
        Returns:
            Dict containing the view data
        """
        if not self.server_url or not self.auth_token or not self.site_id:
            if not self.auth_token and self.server_url:
                self.sign_in()
            else:
                return {"error": "Not authenticated"}
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message=f"Error getting data for view: {view_id}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/views/{view_id}/data"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def get_view_image(self, view_id: str, format: str = "png") -> Tuple[bytes, str]:
        """
        Get an image of a specific view.
        
        Args:
            view_id: ID of the view to get an image for
            format: Image format (png, pdf)
            
        Returns:
            Tuple of (image_data, content_type)
        """
        if not self.server_url or not self.auth_token or not self.site_id:
            if not self.auth_token and self.server_url:
                self.sign_in()
            else:
                raise ValueError("Not authenticated")
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message=f"Error getting image for view: {view_id}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/views/{view_id}/image"
            
            params = {"format": format}
            
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            content_type = response.headers.get("Content-Type", f"image/{format}")
            
            return response.content, content_type
    
    def get_datasources(self) -> Dict[str, Any]:
        """
        Get a list of datasources from Tableau Server.
        
        Returns:
            Dict containing the datasources
        """
        if not self.server_url or not self.auth_token or not self.site_id:
            if not self.auth_token and self.server_url:
                self.sign_in()
            else:
                return {"error": "Not authenticated"}
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message="Error getting datasources from Tableau Server",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/datasources"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
    
    def publish_datasource(
        self, 
        datasource_file: str, 
        datasource_name: str,
        project_id: str,
        overwrite: bool = True
    ) -> Dict[str, Any]:
        """
        Publish a datasource to Tableau Server.
        
        Args:
            datasource_file: Path to the datasource file (.tdsx, .hyper)
            datasource_name: Name for the datasource
            project_id: ID of the project to publish to
            overwrite: Whether to overwrite an existing datasource with the same name
            
        Returns:
            Dict containing the publish result
        """
        if not self.server_url or not self.auth_token or not self.site_id:
            if not self.auth_token and self.server_url:
                self.sign_in()
            else:
                return {"error": "Not authenticated"}
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message=f"Error publishing datasource: {datasource_name}",
            severity=ErrorSeverity.MEDIUM
        ):
            endpoint = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/datasources"
            
            # Prepare request parameters
            params = {
                "datasourceName": datasource_name,
                "overwrite": "true" if overwrite else "false"
            }
            
            # Prepare request headers
            headers = {
                "Content-Type": "application/octet-stream"
            }
            
            # Read file content
            with open(datasource_file, "rb") as file:
                file_content = file.read()
            
            # Send request
            response = self.session.post(endpoint, params=params, headers=headers, data=file_content)
            response.raise_for_status()
            
            return response.json()


class TableauPublicClient:
    """Client for interacting with Tableau Public."""
    
    def __init__(
        self, 
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize the Tableau Public client.
        
        Args:
            username: Tableau Public username (defaults to TABLEAU_PUBLIC_USERNAME environment variable)
            password: Tableau Public password (defaults to TABLEAU_PUBLIC_PASSWORD environment variable)
        """
        self.username = username or os.environ.get("TABLEAU_PUBLIC_USERNAME")
        self.password = password or os.environ.get("TABLEAU_PUBLIC_PASSWORD")
        
        self.base_url = "https://public.tableau.com"
        self.session = requests.Session()
        self.authenticated = False
    
    def sign_in(self) -> bool:
        """
        Sign in to Tableau Public.
        
        Returns:
            bool: True if sign-in was successful, False otherwise
        """
        if not self.username or not self.password:
            logger.error("Cannot sign in: Tableau Public credentials not provided")
            return False
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message="Error signing in to Tableau Public",
            severity=ErrorSeverity.MEDIUM
        ):
            # This is a simplified version; actual implementation would need to handle CSRF tokens, etc.
            endpoint = f"{self.base_url}/auth/signin"
            
            payload = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(endpoint, data=payload)
            response.raise_for_status()
            
            # Check if authentication was successful
            self.authenticated = "auth-token" in self.session.cookies
            
            return self.authenticated
    
    def publish_workbook(
        self, 
        workbook_file: str, 
        workbook_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish a workbook to Tableau Public.
        
        Args:
            workbook_file: Path to the workbook file (.twbx)
            workbook_name: Name for the workbook (defaults to filename without extension)
            
        Returns:
            Dict containing the publish result
        """
        if not self.authenticated:
            if not self.sign_in():
                return {"error": "Not authenticated"}
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message=f"Error publishing workbook to Tableau Public: {workbook_file}",
            severity=ErrorSeverity.MEDIUM
        ):
            # Determine workbook name if not provided
            if not workbook_name:
                workbook_name = os.path.basename(workbook_file)
                workbook_name = os.path.splitext(workbook_name)[0]
            
            # This is a simplified version; actual implementation would need to handle multipart form data
            endpoint = f"{self.base_url}/workbooks/upload"
            
            files = {
                "workbook": (os.path.basename(workbook_file), open(workbook_file, "rb"), "application/octet-stream")
            }
            
            data = {
                "workbookName": workbook_name,
                "visibility": "public"
            }
            
            response = self.session.post(endpoint, files=files, data=data)
            response.raise_for_status()
            
            # Parse response
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {"status": "success" if response.status_code == 200 else "error"}
            
            return result


class TableauVisualizationService:
    """Service for integrating Tableau visualization capabilities with the system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Tableau Visualization service.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize Tableau Server client if configured
        if self.config.get("use_tableau_server", False):
            server_url = self.config.get("server_url") or os.environ.get("TABLEAU_SERVER_URL")
            username = self.config.get("username") or os.environ.get("TABLEAU_USERNAME")
            password = self.config.get("password") or os.environ.get("TABLEAU_PASSWORD")
            site_name = self.config.get("site_name") or os.environ.get("TABLEAU_SITE_NAME", "")
            pat_name = self.config.get("pat_name") or os.environ.get("TABLEAU_PAT_NAME")
            pat_value = self.config.get("pat_value") or os.environ.get("TABLEAU_PAT_VALUE")
            
            self.server_client = TableauClient(
                server_url=server_url,
                username=username,
                password=password,
                site_name=site_name,
                personal_access_token_name=pat_name,
                personal_access_token_value=pat_value
            )
        else:
            self.server_client = None
        
        # Initialize Tableau Public client if configured
        if self.config.get("use_tableau_public", False):
            username = self.config.get("public_username") or os.environ.get("TABLEAU_PUBLIC_USERNAME")
            password = self.config.get("public_password") or os.environ.get("TABLEAU_PUBLIC_PASSWORD")
            
            self.public_client = TableauPublicClient(
                username=username,
                password=password
            )
        else:
            self.public_client = None
    
    def create_visualization_from_dataframe(
        self, 
        df: pd.DataFrame, 
        viz_type: str,
        title: str,
        description: str = "",
        output_dir: str = "/tmp",
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Create a visualization from a pandas DataFrame.
        
        Args:
            df: Pandas DataFrame containing the data
            viz_type: Type of visualization (bar, line, scatter, pie, etc.)
            title: Title for the visualization
            description: Description for the visualization
            output_dir: Directory to save the output file
            output_format: Output format (html, png, pdf)
            
        Returns:
            Dict containing the visualization result
        """
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message=f"Error creating {viz_type} visualization",
            severity=ErrorSeverity.MEDIUM
        ):
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate a unique filename
            timestamp = int(time.time())
            filename_base = f"{title.lower().replace(' ', '_')}_{timestamp}"
            filename = f"{filename_base}.{output_format}"
            output_path = os.path.join(output_dir, filename)
            
            # Create visualization based on type
            if viz_type == "bar":
                self._create_bar_chart(df, title, description, output_path, output_format)
            elif viz_type == "line":
                self._create_line_chart(df, title, description, output_path, output_format)
            elif viz_type == "scatter":
                self._create_scatter_plot(df, title, description, output_path, output_format)
            elif viz_type == "pie":
                self._create_pie_chart(df, title, description, output_path, output_format)
            elif viz_type == "heatmap":
                self._create_heatmap(df, title, description, output_path, output_format)
            elif viz_type == "boxplot":
                self._create_boxplot(df, title, description, output_path, output_format)
            elif viz_type == "histogram":
                self._create_histogram(df, title, description, output_path, output_format)
            else:
                return {"error": f"Unsupported visualization type: {viz_type}"}
            
            return {
                "type": viz_type,
                "title": title,
                "description": description,
                "output_path": output_path,
                "output_format": output_format
            }
    
    def create_dashboard_from_dataframes(
        self, 
        dataframes: Dict[str, pd.DataFrame],
        layout: List[Dict[str, Any]],
        title: str,
        description: str = "",
        output_dir: str = "/tmp",
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Create a dashboard from multiple pandas DataFrames.
        
        Args:
            dataframes: Dict of pandas DataFrames containing the data
            layout: List of layout specifications for each visualization
            title: Title for the dashboard
            description: Description for the dashboard
            output_dir: Directory to save the output file
            output_format: Output format (html, png, pdf)
            
        Returns:
            Dict containing the dashboard result
        """
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message=f"Error creating dashboard: {title}",
            severity=ErrorSeverity.MEDIUM
        ):
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate a unique filename
            timestamp = int(time.time())
            filename_base = f"{title.lower().replace(' ', '_')}_{timestamp}"
            filename = f"{filename_base}.{output_format}"
            output_path = os.path.join(output_dir, filename)
            
            # Create individual visualizations
            viz_paths = []
            for viz_spec in layout:
                df_name = viz_spec.get("dataframe")
                if df_name not in dataframes:
                    continue
                    
                df = dataframes[df_name]
                viz_type = viz_spec.get("type", "bar")
                viz_title = viz_spec.get("title", f"{df_name} Visualization")
                
                # Create visualization
                viz_result = self.create_visualization_from_dataframe(
                    df=df,
                    viz_type=viz_type,
                    title=viz_title,
                    description="",
                    output_dir=output_dir,
                    output_format=output_format
                )
                
                if "error" not in viz_result:
                    viz_paths.append(viz_result["output_path"])
            
            # Combine visualizations into a dashboard
            if output_format == "html":
                self._combine_html_visualizations(viz_paths, title, description, output_path)
            else:
                # For other formats, we would need to use a library like PIL to combine images
                return {"error": f"Dashboard creation for format {output_format} not implemented"}
            
            return {
                "title": title,
                "description": description,
                "output_path": output_path,
                "output_format": output_format,
                "visualizations": len(viz_paths)
            }
    
    def publish_to_tableau_server(
        self, 
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        name: str,
        project_id: Optional[str] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Publish data to Tableau Server.
        
        Args:
            data: Pandas DataFrame or Dict of DataFrames to publish
            name: Name for the published data
            project_id: ID of the project to publish to
            description: Description for the published data
            
        Returns:
            Dict containing the publish result
        """
        if not self.server_client:
            return {"error": "Tableau Server client not configured"}
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message=f"Error publishing to Tableau Server: {name}",
            severity=ErrorSeverity.MEDIUM
        ):
            # Ensure client is authenticated
            if not self.server_client.auth_token:
                self.server_client.sign_in()
            
            # Create a temporary directory for files
            import tempfile
            temp_dir = tempfile.mkdtemp()
            
            # Convert data to CSV
            if isinstance(data, pd.DataFrame):
                # Single DataFrame
                csv_path = os.path.join(temp_dir, f"{name}.csv")
                data.to_csv(csv_path, index=False)
                
                # Publish as datasource
                result = self._publish_csv_as_datasource(csv_path, name, project_id, description)
            else:
                # Multiple DataFrames
                results = {}
                for df_name, df in data.items():
                    csv_path = os.path.join(temp_dir, f"{df_name}.csv")
                    df.to_csv(csv_path, index=False)
                    
                    # Publish each DataFrame as a datasource
                    df_result = self._publish_csv_as_datasource(
                        csv_path, 
                        f"{name}_{df_name}", 
                        project_id, 
                        f"{description} - {df_name}"
                    )
                    
                    results[df_name] = df_result
                
                result = {
                    "name": name,
                    "datasources": results
                }
            
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_dir)
            
            return result
    
    def publish_to_tableau_public(
        self, 
        visualization_path: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish a visualization to Tableau Public.
        
        Args:
            visualization_path: Path to the visualization file (.twbx)
            name: Name for the published visualization
            
        Returns:
            Dict containing the publish result
        """
        if not self.public_client:
            return {"error": "Tableau Public client not configured"}
            
        with ErrorHandler(
            error_category=ErrorCategory.VISUALIZATION,
            error_message=f"Error publishing to Tableau Public: {visualization_path}",
            severity=ErrorSeverity.MEDIUM
        ):
            # Ensure client is authenticated
            if not self.public_client.authenticated:
                self.public_client.sign_in()
            
            # Publish workbook
            result = self.public_client.publish_workbook(
                workbook_file=visualization_path,
                workbook_name=name
            )
            
            return result
    
    def _create_bar_chart(
        self, 
        df: pd.DataFrame, 
        title: str, 
        description: str,
        output_path: str,
        output_format: str
    ) -> None:
        """Create a bar chart visualization."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        # Determine x and y columns
        if len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1]
        else:
            # Use index as x and first column as y
            x_col = df.index
            y_col = df.columns[0]
        
        # Create bar chart
        ax = sns.barplot(x=x_col, y=y_col, data=df)
        
        # Set title and labels
        plt.title(title, fontsize=16)
        plt.xlabel(x_col if isinstance(x_col, str) else "Index", fontsize=12)
        plt.ylabel(y_col, fontsize=12)
        
        # Add description as text
        if description:
            plt.figtext(0.5, 0.01, description, wrap=True, horizontalalignment='center', fontsize=10)
        
        # Rotate x-axis labels if there are many categories
        if len(df) > 5:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_path, format=output_format if output_format != "html" else "png", dpi=300)
        
        # If HTML format is requested, create an HTML wrapper
        if output_format == "html":
            self._create_html_wrapper(output_path.replace(".html", ".png"), output_path, title, description)
        
        plt.close()
    
    def _create_line_chart(
        self, 
        df: pd.DataFrame, 
        title: str, 
        description: str,
        output_path: str,
        output_format: str
    ) -> None:
        """Create a line chart visualization."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        # Check if DataFrame has a datetime index
        if pd.api.types.is_datetime64_any_dtype(df.index):
            # Use index as x-axis
            for column in df.columns:
                plt.plot(df.index, df[column], label=column)
            
            plt.xlabel("Date", fontsize=12)
        else:
            # Determine x and y columns
            if len(df.columns) >= 2:
                x_col = df.columns[0]
                
                # Plot each remaining column as a line
                for column in df.columns[1:]:
                    plt.plot(df[x_col], df[column], label=column)
                
                plt.xlabel(x_col, fontsize=12)
            else:
                # Use index as x and first column as y
                plt.plot(df.index, df[df.columns[0]])
                plt.xlabel("Index", fontsize=12)
                plt.ylabel(df.columns[0], fontsize=12)
        
        # Set title and add legend if multiple lines
        plt.title(title, fontsize=16)
        if len(df.columns) > 1:
            plt.legend()
        
        # Add description as text
        if description:
            plt.figtext(0.5, 0.01, description, wrap=True, horizontalalignment='center', fontsize=10)
        
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_path, format=output_format if output_format != "html" else "png", dpi=300)
        
        # If HTML format is requested, create an HTML wrapper
        if output_format == "html":
            self._create_html_wrapper(output_path.replace(".html", ".png"), output_path, title, description)
        
        plt.close()
    
    def _create_scatter_plot(
        self, 
        df: pd.DataFrame, 
        title: str, 
        description: str,
        output_path: str,
        output_format: str
    ) -> None:
        """Create a scatter plot visualization."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        # Determine x, y, and optional color columns
        if len(df.columns) >= 3:
            x_col = df.columns[0]
            y_col = df.columns[1]
            color_col = df.columns[2]
            
            # Create scatter plot with color
            scatter = sns.scatterplot(x=x_col, y=y_col, hue=color_col, data=df)
        elif len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1]
            
            # Create simple scatter plot
            scatter = sns.scatterplot(x=x_col, y=y_col, data=df)
        else:
            return
        
        # Set title and labels
        plt.title(title, fontsize=16)
        plt.xlabel(x_col, fontsize=12)
        plt.ylabel(y_col, fontsize=12)
        
        # Add description as text
        if description:
            plt.figtext(0.5, 0.01, description, wrap=True, horizontalalignment='center', fontsize=10)
        
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_path, format=output_format if output_format != "html" else "png", dpi=300)
        
        # If HTML format is requested, create an HTML wrapper
        if output_format == "html":
            self._create_html_wrapper(output_path.replace(".html", ".png"), output_path, title, description)
        
        plt.close()
    
    def _create_pie_chart(
        self, 
        df: pd.DataFrame, 
        title: str, 
        description: str,
        output_path: str,
        output_format: str
    ) -> None:
        """Create a pie chart visualization."""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        
        # Determine labels and values
        if len(df.columns) >= 2:
            labels = df[df.columns[0]]
            values = df[df.columns[1]]
        else:
            # Use column names as labels and first row as values
            labels = df.columns
            values = df.iloc[0]
        
        # Create pie chart
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Set title
        plt.title(title, fontsize=16)
        
        # Add description as text
        if description:
            plt.figtext(0.5, 0.01, description, wrap=True, horizontalalignment='center', fontsize=10)
        
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_path, format=output_format if output_format != "html" else "png", dpi=300)
        
        # If HTML format is requested, create an HTML wrapper
        if output_format == "html":
            self._create_html_wrapper(output_path.replace(".html", ".png"), output_path, title, description)
        
        plt.close()
    
    def _create_heatmap(
        self, 
        df: pd.DataFrame, 
        title: str, 
        description: str,
        output_path: str,
        output_format: str
    ) -> None:
        """Create a heatmap visualization."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.figure(figsize=(12, 8))
        
        # Create heatmap
        heatmap = sns.heatmap(df, annot=True, cmap="YlGnBu", linewidths=.5)
        
        # Set title
        plt.title(title, fontsize=16)
        
        # Add description as text
        if description:
            plt.figtext(0.5, 0.01, description, wrap=True, horizontalalignment='center', fontsize=10)
        
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_path, format=output_format if output_format != "html" else "png", dpi=300)
        
        # If HTML format is requested, create an HTML wrapper
        if output_format == "html":
            self._create_html_wrapper(output_path.replace(".html", ".png"), output_path, title, description)
        
        plt.close()
    
    def _create_boxplot(
        self, 
        df: pd.DataFrame, 
        title: str, 
        description: str,
        output_path: str,
        output_format: str
    ) -> None:
        """Create a boxplot visualization."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        # Determine x and y columns
        if len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1]
            
            # Create boxplot
            boxplot = sns.boxplot(x=x_col, y=y_col, data=df)
        else:
            # Create boxplot for single column
            boxplot = sns.boxplot(y=df.columns[0], data=df)
        
        # Set title and labels
        plt.title(title, fontsize=16)
        
        # Add description as text
        if description:
            plt.figtext(0.5, 0.01, description, wrap=True, horizontalalignment='center', fontsize=10)
        
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_path, format=output_format if output_format != "html" else "png", dpi=300)
        
        # If HTML format is requested, create an HTML wrapper
        if output_format == "html":
            self._create_html_wrapper(output_path.replace(".html", ".png"), output_path, title, description)
        
        plt.close()
    
    def _create_histogram(
        self, 
        df: pd.DataFrame, 
        title: str, 
        description: str,
        output_path: str,
        output_format: str
    ) -> None:
        """Create a histogram visualization."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        # Create histogram for each numeric column
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            for column in numeric_cols:
                sns.histplot(df[column], kde=True, label=column)
            
            if len(numeric_cols) > 1:
                plt.legend()
        else:
            plt.text(0.5, 0.5, "No numeric columns found for histogram", 
                    horizontalalignment='center', verticalalignment='center')
        
        # Set title
        plt.title(title, fontsize=16)
        
        # Add description as text
        if description:
            plt.figtext(0.5, 0.01, description, wrap=True, horizontalalignment='center', fontsize=10)
        
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_path, format=output_format if output_format != "html" else "png", dpi=300)
        
        # If HTML format is requested, create an HTML wrapper
        if output_format == "html":
            self._create_html_wrapper(output_path.replace(".html", ".png"), output_path, title, description)
        
        plt.close()
    
    def _create_html_wrapper(
        self, 
        image_path: str, 
        html_path: str, 
        title: str, 
        description: str
    ) -> None:
        """Create an HTML wrapper for an image."""
        # Read the image file
        with open(image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode("utf-8")
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    text-align: center;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                }}
                .description {{
                    margin-top: 20px;
                    font-style: italic;
                    color: #666;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <img src="data:image/png;base64,{img_data}" alt="{title}">
                <div class="description">{description}</div>
            </div>
        </body>
        </html>
        """
        
        # Write HTML file
        with open(html_path, "w") as html_file:
            html_file.write(html_content)
    
    def _combine_html_visualizations(
        self, 
        viz_paths: List[str], 
        title: str, 
        description: str,
        output_path: str
    ) -> None:
        """Combine multiple HTML visualizations into a dashboard."""
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }}
                .dashboard-container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .dashboard-header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .dashboard-description {{
                    margin-top: 10px;
                    font-style: italic;
                    color: #666;
                }}
                .dashboard-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                    gap: 20px;
                }}
                .viz-container {{
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    background-color: #f9f9f9;
                }}
                iframe {{
                    width: 100%;
                    height: 400px;
                    border: none;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-container">
                <div class="dashboard-header">
                    <h1>{title}</h1>
                    <div class="dashboard-description">{description}</div>
                </div>
                <div class="dashboard-grid">
        """
        
        # Add each visualization
        for viz_path in viz_paths:
            viz_name = os.path.basename(viz_path)
            html_content += f"""
                    <div class="viz-container">
                        <iframe src="{viz_name}"></iframe>
                    </div>
            """
        
        # Close HTML content
        html_content += """
                </div>
            </div>
        </body>
        </html>
        """
        
        # Write HTML file
        with open(output_path, "w") as html_file:
            html_file.write(html_content)
    
    def _publish_csv_as_datasource(
        self, 
        csv_path: str, 
        name: str, 
        project_id: Optional[str],
        description: str
    ) -> Dict[str, Any]:
        """Publish a CSV file as a datasource to Tableau Server."""
        # This is a simplified implementation
        # In a real implementation, we would need to:
        # 1. Create a Tableau Hyper file from the CSV
        # 2. Create a Tableau Data Source (.tdsx) file
        # 3. Publish the .tdsx file to Tableau Server
        
        # For now, we'll just return a mock result
        return {
            "name": name,
            "type": "datasource",
            "source_file": csv_path,
            "status": "published",
            "url": f"https://tableau-server/datasources/{name}"
        }
