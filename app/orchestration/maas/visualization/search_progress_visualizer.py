"""
Search progress visualizer for Multi-agent Architecture Search (MaAS).

This module provides tools for visualizing the progress of architecture search.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
from datetime import datetime

from ..models import ArchitectureModel, SearchResult


class SearchProgressVisualizer:
    """Visualizes the progress of architecture search."""
    
    def __init__(self, output_format="svg", theme="light"):
        """Initialize the search progress visualizer.
        
        Args:
            output_format: Format for output files (svg, png, html)
            theme: Visual theme (light, dark)
        """
        self.output_format = output_format
        self.theme = theme
        
        # Define color schemes based on theme
        if theme == "dark":
            self.background_color = "#222222"
            self.primary_color = "#3498DB"
            self.secondary_color = "#2ECC71"
            self.accent_color = "#E74C3C"
            self.text_color = "#FFFFFF"
            self.grid_color = "#444444"
            self.colorscale = "Viridis"
        else:  # light theme
            self.background_color = "#FFFFFF"
            self.primary_color = "#2980B9"
            self.secondary_color = "#27AE60"
            self.accent_color = "#C0392B"
            self.text_color = "#333333"
            self.grid_color = "#DDDDDD"
            self.colorscale = "Plasma"
    
    def visualize_search_progress(self, search_results: Union[SearchResult, List[Dict[str, Any]]], 
                                 output_path: Optional[str] = None) -> str:
        """Generate a visualization of search progress over time.
        
        Args:
            search_results: SearchResult object or list of fitness history dictionaries
                If list of dictionaries, each should have 'generation', 'best_fitness', 
                'avg_fitness', and optionally 'timestamp' keys
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file or HTML content
        """
        # Extract fitness history from SearchResult if needed
        if isinstance(search_results, SearchResult):
            fitness_history = search_results.fitness_history
        else:
            fitness_history = search_results
        
        if not fitness_history:
            raise ValueError("No search progress data provided")
        
        if self.output_format == "html":
            return self._visualize_progress_interactive(fitness_history, output_path)
        else:
            return self._visualize_progress_static(fitness_history, output_path)
    
    def visualize_population_diversity(self, population: List[ArchitectureModel], 
                                      output_path: Optional[str] = None) -> str:
        """Generate a visualization of population diversity.
        
        Args:
            population: List of ArchitectureModel objects in the population
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file or HTML content
        """
        if not population:
            raise ValueError("No population data provided")
        
        if self.output_format == "html":
            return self._visualize_diversity_interactive(population, output_path)
        else:
            return self._visualize_diversity_static(population, output_path)
    
    def _visualize_progress_static(self, fitness_history: List[Dict[str, Any]], 
                                  output_path: Optional[str] = None) -> str:
        """Generate a static visualization of search progress over time.
        
        Args:
            fitness_history: List of fitness history dictionaries
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file
        """
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle("Architecture Search Progress", fontsize=16, color=self.text_color)
        
        # Extract data
        generations = [entry.get('generation', i) for i, entry in enumerate(fitness_history)]
        best_fitness = [entry.get('best_fitness', 0) for entry in fitness_history]
        avg_fitness = [entry.get('avg_fitness', 0) for entry in fitness_history]
        
        # Plot best and average fitness over generations
        ax1.plot(generations, best_fitness, 'o-', color=self.primary_color, label='Best Fitness')
        ax1.plot(generations, avg_fitness, 'o-', color=self.secondary_color, label='Average Fitness')
        ax1.set_xlabel('Generation', color=self.text_color)
        ax1.set_ylabel('Fitness', color=self.text_color)
        ax1.set_title('Fitness Evolution', color=self.text_color)
        ax1.grid(True, color=self.grid_color, linestyle='--', alpha=0.7)
        ax1.legend()
        
        # Plot improvement rate (derivative of best fitness)
        if len(best_fitness) > 1:
            improvements = [best_fitness[i] - best_fitness[i-1] for i in range(1, len(best_fitness))]
            ax2.bar(generations[1:], improvements, color=self.accent_color, alpha=0.7)
            ax2.set_xlabel('Generation', color=self.text_color)
            ax2.set_ylabel('Improvement', color=self.text_color)
            ax2.set_title('Fitness Improvement per Generation', color=self.text_color)
            ax2.grid(True, color=self.grid_color, linestyle='--', alpha=0.7)
        else:
            ax2.text(0.5, 0.5, "Not enough data to calculate improvements", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes, color=self.text_color)
        
        # Set background color
        fig.patch.set_facecolor(self.background_color)
        ax1.set_facecolor(self.background_color)
        ax2.set_facecolor(self.background_color)
        
        # Set text color for axes
        for ax in [ax1, ax2]:
            ax.tick_params(colors=self.text_color)
            ax.xaxis.label.set_color(self.text_color)
            ax.yaxis.label.set_color(self.text_color)
            ax.title.set_color(self.text_color)
            for spine in ax.spines.values():
                spine.set_color(self.text_color)
        
        plt.tight_layout()
        
        # Save or show the visualization
        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Add extension if not provided
            if not output_path.endswith(f".{self.output_format}"):
                output_path = f"{output_path}.{self.output_format}"
                
            plt.savefig(output_path, format=self.output_format, 
                        facecolor=self.background_color, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            # Generate a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=f".{self.output_format}", delete=False) as tmp:
                tmp_path = tmp.name
            
            plt.savefig(tmp_path, format=self.output_format, 
                        facecolor=self.background_color, bbox_inches='tight')
            plt.close()
            return tmp_path
    
    def _visualize_progress_interactive(self, fitness_history: List[Dict[str, Any]], 
                                       output_path: Optional[str] = None) -> str:
        """Generate an interactive visualization of search progress over time.
        
        Args:
            fitness_history: List of fitness history dictionaries
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated HTML file or HTML content
        """
        # Extract data
        generations = [entry.get('generation', i) for i, entry in enumerate(fitness_history)]
        best_fitness = [entry.get('best_fitness', 0) for entry in fitness_history]
        avg_fitness = [entry.get('avg_fitness', 0) for entry in fitness_history]
        
        # Check if timestamps are available
        has_timestamps = all('timestamp' in entry for entry in fitness_history)
        
        # Create figure with subplots
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=2, 
            cols=1, 
            subplot_titles=['Fitness Evolution', 'Fitness Improvement per Generation']
        )
        
        # Add traces for best and average fitness
        fig.add_trace(
            go.Scatter(x=generations, y=best_fitness, mode='lines+markers', 
                      name='Best Fitness', line=dict(color=self.primary_color)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=generations, y=avg_fitness, mode='lines+markers', 
                      name='Average Fitness', line=dict(color=self.secondary_color)),
            row=1, col=1
        )
        
        # Add trace for improvement rate
        if len(best_fitness) > 1:
            improvements = [best_fitness[i] - best_fitness[i-1] for i in range(1, len(best_fitness))]
            fig.add_trace(
                go.Bar(x=generations[1:], y=improvements, name='Improvement', 
                      marker=dict(color=self.accent_color)),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title='Architecture Search Progress',
            plot_bgcolor=self.background_color,
            paper_bgcolor=self.background_color,
            font=dict(color=self.text_color),
            height=800
        )
        
        fig.update_xaxes(title_text='Generation', row=1, col=1, 
                        gridcolor=self.grid_color)
        fig.update_xaxes(title_text='Generation', row=2, col=1, 
                        gridcolor=self.grid_color)
        
        fig.update_yaxes(title_text='Fitness', row=1, col=1, 
                        gridcolor=self.grid_color)
        fig.update_yaxes(title_text='Improvement', row=2, col=1, 
                        gridcolor=self.grid_color)
        
        # Add time-based visualization if timestamps are available
        if has_timestamps:
            # Extract timestamps
            timestamps = [entry.get('timestamp') for entry in fitness_history]
            
            # Convert to datetime objects if they're strings
            if isinstance(timestamps[0], str):
                timestamps = [datetime.fromisoformat(ts) for ts in timestamps]
            
            # Create a new figure for time-based visualization
            time_fig = go.Figure()
            
            time_fig.add_trace(
                go.Scatter(x=timestamps, y=best_fitness, mode='lines+markers', 
                          name='Best Fitness', line=dict(color=self.primary_color))
            )
            
            time_fig.add_trace(
                go.Scatter(x=timestamps, y=avg_fitness, mode='lines+markers', 
                          name='Average Fitness', line=dict(color=self.secondary_color))
            )
            
            time_fig.update_layout(
                title='Fitness Evolution Over Time',
                xaxis_title='Time',
                yaxis_title='Fitness',
                plot_bgcolor=self.background_color,
                paper_bgcolor=self.background_color,
                font=dict(color=self.text_color)
            )
            
            # Combine both figures
            from plotly.subplots import make_subplots
            combined_fig = make_subplots(
                rows=3, 
                cols=1, 
                subplot_titles=['Fitness Evolution by Generation', 
                               'Fitness Improvement per Generation',
                               'Fitness Evolution Over Time']
            )
            
            # Add traces from the first figure
            for trace in fig.data[:2]:  # First two traces (best and avg fitness)
                combined_fig.add_trace(trace, row=1, col=1)
            
            if len(fig.data) > 2:  # Improvement trace
                combined_fig.add_trace(fig.data[2], row=2, col=1)
            
            # Add traces from the time figure
            for trace in time_fig.data:
                combined_fig.add_trace(trace, row=3, col=1)
            
            # Update layout
            combined_fig.update_layout(
                title='Architecture Search Progress',
                plot_bgcolor=self.background_color,
                paper_bgcolor=self.background_color,
                font=dict(color=self.text_color),
                height=1200
            )
            
            combined_fig.update_xaxes(title_text='Generation', row=1, col=1, 
                                     gridcolor=self.grid_color)
            combined_fig.update_xaxes(title_text='Generation', row=2, col=1, 
                                     gridcolor=self.grid_color)
            combined_fig.update_xaxes(title_text='Time', row=3, col=1, 
                                     gridcolor=self.grid_color)
            
            combined_fig.update_yaxes(title_text='Fitness', row=1, col=1, 
                                     gridcolor=self.grid_color)
            combined_fig.update_yaxes(title_text='Improvement', row=2, col=1, 
                                     gridcolor=self.grid_color)
            combined_fig.update_yaxes(title_text='Fitness', row=3, col=1, 
                                     gridcolor=self.grid_color)
            
            # Use the combined figure
            fig = combined_fig
        
        # Save or return the visualization
        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Add extension if not provided
            if not output_path.endswith(".html"):
                output_path = f"{output_path}.html"
                
            fig.write_html(output_path)
            return output_path
        else:
            # Return HTML content
            return fig.to_html()
    
    def _visualize_diversity_static(self, population: List[ArchitectureModel], 
                                   output_path: Optional[str] = None) -> str:
        """Generate a static visualization of population diversity.
        
        Args:
            population: List of ArchitectureModel objects in the population
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file
        """
        # Create figure with multiple subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle("Population Diversity Analysis", fontsize=16, color=self.text_color)
        
        # 1. Agent count distribution
        agent_counts = [len(arch.agents) for arch in population]
        ax1.hist(agent_counts, bins=max(5, min(20, len(set(agent_counts)))), 
                color=self.primary_color, alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Number of Agents', color=self.text_color)
        ax1.set_ylabel('Frequency', color=self.text_color)
        ax1.set_title('Agent Count Distribution', color=self.text_color)
        ax1.grid(True, color=self.grid_color, linestyle='--', alpha=0.7)
        
        # 2. Connection density distribution
        connection_densities = []
        for arch in population:
            n_agents = len(arch.agents)
            if n_agents > 1:  # Avoid division by zero
                max_connections = n_agents * (n_agents - 1)  # Maximum possible directed connections
                actual_connections = len(arch.connections)
                density = actual_connections / max_connections
                connection_densities.append(density)
        
        if connection_densities:
            ax2.hist(connection_densities, bins=max(5, min(20, len(set(connection_densities)))), 
                    color=self.secondary_color, alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Connection Density', color=self.text_color)
            ax2.set_ylabel('Frequency', color=self.text_color)
            ax2.set_title('Connection Density Distribution', color=self.text_color)
            ax2.grid(True, color=self.grid_color, linestyle='--', alpha=0.7)
        else:
            ax2.text(0.5, 0.5, "No connection density data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes, color=self.text_color)
        
        # 3. Role distribution
        role_counts = {}
        for arch in population:
            for agent in arch.agents:
                role = agent.role.value
                if role not in role_counts:
                    role_counts[role] = 0
                role_counts[role] += 1
        
        if role_counts:
            roles = list(role_counts.keys())
            counts = list(role_counts.values())
            
            # Sort by count
            sorted_indices = np.argsort(counts)[::-1]
            roles = [roles[i] for i in sorted_indices]
            counts = [counts[i] for i in sorted_indices]
            
            ax3.bar(roles, counts, color=self.accent_color, alpha=0.7)
            ax3.set_xlabel('Agent Role', color=self.text_color)
            ax3.set_ylabel('Count', color=self.text_color)
            ax3.set_title('Role Distribution', color=self.text_color)
            ax3.tick_params(axis='x', rotation=45)
            ax3.grid(True, color=self.grid_color, linestyle='--', alpha=0.7)
        else:
            ax3.text(0.5, 0.5, "No role data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax3.transAxes, color=self.text_color)
        
        # 4. Capability distribution
        capability_counts = {}
        for arch in population:
            for agent in arch.agents:
                for capability in agent.capabilities:
                    cap_value = capability.value
                    if cap_value not in capability_counts:
                        capability_counts[cap_value] = 0
                    capability_counts[cap_value] += 1
        
        if capability_counts:
            capabilities = list(capability_counts.keys())
            counts = list(capability_counts.values())
            
            # Sort by count
            sorted_indices = np.argsort(counts)[::-1]
            capabilities = [capabilities[i] for i in sorted_indices]
            counts = [counts[i] for i in sorted_indices]
            
            # Take top 10 for readability
            if len(capabilities) > 10:
                capabilities = capabilities[:10]
                counts = counts[:10]
            
            ax4.bar(capabilities, counts, color=self.primary_color, alpha=0.7)
            ax4.set_xlabel('Agent Capability', color=self.text_color)
            ax4.set_ylabel('Count', color=self.text_color)
            ax4.set_title('Top Capability Distribution', color=self.text_color)
            ax4.tick_params(axis='x', rotation=45)
            ax4.grid(True, color=self.grid_color, linestyle='--', alpha=0.7)
        else:
            ax4.text(0.5, 0.5, "No capability data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax4.transAxes, color=self.text_color)
        
        # Set background color
        fig.patch.set_facecolor(self.background_color)
        for ax in [ax1, ax2, ax3, ax4]:
            ax.set_facecolor(self.background_color)
            ax.tick_params(colors=self.text_color)
            ax.xaxis.label.set_color(self.text_color)
            ax.yaxis.label.set_color(self.text_color)
            ax.title.set_color(self.text_color)
            for spine in ax.spines.values():
                spine.set_color(self.text_color)
        
        plt.tight_layout()
        
        # Save or show the visualization
        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Add extension if not provided
            if not output_path.endswith(f".{self.output_format}"):
                output_path = f"{output_path}.{self.output_format}"
                
            plt.savefig(output_path, format=self.output_format, 
                        facecolor=self.background_color, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            # Generate a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=f".{self.output_format}", delete=False) as tmp:
                tmp_path = tmp.name
            
            plt.savefig(tmp_path, format=self.output_format, 
                        facecolor=self.background_color, bbox_inches='tight')
            plt.close()
            return tmp_path
    
    def _visualize_diversity_interactive(self, population: List[ArchitectureModel], 
                                        output_path: Optional[str] = None) -> str:
        """Generate an interactive visualization of population diversity.
        
        Args:
            population: List of ArchitectureModel objects in the population
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated HTML file or HTML content
        """
        # Create a figure with subplots
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=2, 
            cols=2,
            subplot_titles=[
                'Agent Count Distribution',
                'Connection Density Distribution',
                'Role Distribution',
                'Top Capability Distribution'
            ]
        )
        
        # 1. Agent count distribution
        agent_counts = [len(arch.agents) for arch in population]
        fig.add_trace(
            go.Histogram(x=agent_counts, name='Agent Count', 
                        marker=dict(color=self.primary_color)),
            row=1, col=1
        )
        
        # 2. Connection density distribution
        connection_densities = []
        for arch in population:
            n_agents = len(arch.agents)
            if n_agents > 1:  # Avoid division by zero
                max_connections = n_agents * (n_agents - 1)  # Maximum possible directed connections
                actual_connections = len(arch.connections)
                density = actual_connections / max_connections
                connection_densities.append(density)
        
        if connection_densities:
            fig.add_trace(
                go.Histogram(x=connection_densities, name='Connection Density', 
                            marker=dict(color=self.secondary_color)),
                row=1, col=2
            )
        
        # 3. Role distribution
        role_counts = {}
        for arch in population:
            for agent in arch.agents:
                role = agent.role.value
                if role not in role_counts:
                    role_counts[role] = 0
                role_counts[role] += 1
        
        if role_counts:
            roles = list(role_counts.keys())
            counts = list(role_counts.values())
            
            # Sort by count
            sorted_indices = np.argsort(counts)[::-1]
            roles = [roles[i] for i in sorted_indices]
            counts = [counts[i] for i in sorted_indices]
            
            fig.add_trace(
                go.Bar(x=roles, y=counts, name='Role Count', 
                      marker=dict(color=self.accent_color)),
                row=2, col=1
            )
        
        # 4. Capability distribution
        capability_counts = {}
        for arch in population:
            for agent in arch.agents:
                for capability in agent.capabilities:
                    cap_value = capability.value
                    if cap_value not in capability_counts:
                        capability_counts[cap_value] = 0
                    capability_counts[cap_value] += 1
        
        if capability_counts:
            capabilities = list(capability_counts.keys())
            counts = list(capability_counts.values())
            
            # Sort by count
            sorted_indices = np.argsort(counts)[::-1]
            capabilities = [capabilities[i] for i in sorted_indices]
            counts = [counts[i] for i in sorted_indices]
            
            # Take top 10 for readability
            if len(capabilities) > 10:
                capabilities = capabilities[:10]
                counts = counts[:10]
            
            fig.add_trace(
                go.Bar(x=capabilities, y=counts, name='Capability Count', 
                      marker=dict(color=self.primary_color)),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title='Population Diversity Analysis',
            plot_bgcolor=self.background_color,
            paper_bgcolor=self.background_color,
            font=dict(color=self.text_color),
            height=800,
            showlegend=False
        )
        
        # Update axes
        fig.update_xaxes(title_text='Number of Agents', row=1, col=1, 
                        gridcolor=self.grid_color)
        fig.update_xaxes(title_text='Connection Density', row=1, col=2, 
                        gridcolor=self.grid_color)
        fig.update_xaxes(title_text='Agent Role', row=2, col=1, 
                        gridcolor=self.grid_color)
        fig.update_xaxes(title_text='Agent Capability', row=2, col=2, 
                        gridcolor=self.grid_color)
        
        fig.update_yaxes(title_text='Frequency', row=1, col=1, 
                        gridcolor=self.grid_color)
        fig.update_yaxes(title_text='Frequency', row=1, col=2, 
                        gridcolor=self.grid_color)
        fig.update_yaxes(title_text='Count', row=2, col=1, 
                        gridcolor=self.grid_color)
        fig.update_yaxes(title_text='Count', row=2, col=2, 
                        gridcolor=self.grid_color)
        
        # Save or return the visualization
        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Add extension if not provided
            if not output_path.endswith(".html"):
                output_path = f"{output_path}.html"
                
            fig.write_html(output_path)
            return output_path
        else:
            # Return HTML content
            return fig.to_html()
