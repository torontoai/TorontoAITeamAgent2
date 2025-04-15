"""
Architecture visualizer for Multi-agent Architecture Search (MaAS).

This module provides tools for visualizing agent architectures as interactive graphs.
"""

import os
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
import json

from ..models import ArchitectureModel, AgentModel, ConnectionModel, AgentRole


class ArchitectureVisualizer:
    """Visualizes agent architectures as interactive graphs."""
    
    def __init__(self, output_format="svg", theme="light"):
        """Initialize the architecture visualizer.
        
        Args:
            output_format: Format for output files (svg, png, html)
            theme: Visual theme (light, dark)
        """
        self.output_format = output_format
        self.theme = theme
        
        # Define color schemes based on theme
        if theme == "dark":
            self.background_color = "#222222"
            self.node_colors = {
                AgentRole.COORDINATOR: "#FF5733",
                AgentRole.EXECUTOR: "#33FF57",
                AgentRole.PLANNER: "#3357FF",
                AgentRole.RESEARCHER: "#FF33F5",
                AgentRole.CRITIC: "#F5FF33",
                AgentRole.MEMORY: "#33FFF5",
                AgentRole.REASONER: "#F533FF",
                AgentRole.GENERATOR: "#33F5FF",
                AgentRole.EVALUATOR: "#FFF533",
                AgentRole.COMMUNICATOR: "#FF3333",
                AgentRole.SPECIALIST: "#33FFFF",
                AgentRole.CUSTOM: "#AAAAAA"
            }
            self.edge_color = "#AAAAAA"
            self.text_color = "#FFFFFF"
        else:  # light theme
            self.background_color = "#FFFFFF"
            self.node_colors = {
                AgentRole.COORDINATOR: "#D35400",
                AgentRole.EXECUTOR: "#27AE60",
                AgentRole.PLANNER: "#2980B9",
                AgentRole.RESEARCHER: "#8E44AD",
                AgentRole.CRITIC: "#F1C40F",
                AgentRole.MEMORY: "#16A085",
                AgentRole.REASONER: "#9B59B6",
                AgentRole.GENERATOR: "#3498DB",
                AgentRole.EVALUATOR: "#F39C12",
                AgentRole.COMMUNICATOR: "#E74C3C",
                AgentRole.SPECIALIST: "#1ABC9C",
                AgentRole.CUSTOM: "#95A5A6"
            }
            self.edge_color = "#7F8C8D"
            self.text_color = "#000000"
    
    def visualize_architecture(self, architecture: ArchitectureModel, output_path: Optional[str] = None) -> str:
        """Generate a visualization of an agent architecture.
        
        Args:
            architecture: ArchitectureModel to visualize
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file or HTML content
        """
        if self.output_format == "html":
            return self._visualize_interactive(architecture, output_path)
        else:
            return self._visualize_static(architecture, output_path)
    
    def visualize_comparison(self, architectures: List[ArchitectureModel], 
                             metrics: Optional[Dict[str, Dict[str, float]]] = None, 
                             output_path: Optional[str] = None) -> str:
        """Generate a comparison visualization of multiple architectures.
        
        Args:
            architectures: List of ArchitectureModel objects to compare
            metrics: Optional metrics to include in the comparison
                     Format: {architecture_id: {metric_name: value}}
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file or HTML content
        """
        if len(architectures) == 0:
            raise ValueError("No architectures provided for comparison")
        
        # Create a figure with subplots
        n_architectures = len(architectures)
        n_cols = min(3, n_architectures)
        n_rows = (n_architectures + n_cols - 1) // n_cols
        
        if self.output_format == "html":
            return self._visualize_interactive_comparison(architectures, metrics, output_path)
        else:
            return self._visualize_static_comparison(architectures, metrics, output_path)
    
    def _visualize_static(self, architecture: ArchitectureModel, output_path: Optional[str] = None) -> str:
        """Generate a static visualization of an agent architecture.
        
        Args:
            architecture: ArchitectureModel to visualize
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes (agents)
        for agent in architecture.agents:
            G.add_node(agent.id, 
                       name=agent.name, 
                       role=agent.role.value, 
                       model=agent.model_name,
                       capabilities=[cap.value for cap in agent.capabilities])
        
        # Add edges (connections)
        for conn in architecture.connections:
            G.add_edge(conn.source_id, conn.target_id, 
                       weight=conn.weight, 
                       bidirectional=conn.bidirectional)
            if conn.bidirectional:
                G.add_edge(conn.target_id, conn.source_id, 
                           weight=conn.weight, 
                           bidirectional=True)
        
        # Create the plot
        plt.figure(figsize=(12, 10))
        plt.title(f"Architecture: {architecture.name}", fontsize=16)
        
        # Use a layout that works well for directed graphs
        if len(architecture.agents) <= 10:
            pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.kamada_kawai_layout(G)
        
        # Draw nodes with role-based colors
        node_colors = [self.node_colors.get(architecture.get_agent_by_id(node).role, "#AAAAAA") 
                       for node in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color=self.edge_color, width=1.5, 
                               arrowsize=15, alpha=0.7)
        
        # Add labels with agent names
        labels = {node: architecture.get_agent_by_id(node).name for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color=self.text_color)
        
        # Set background color
        plt.gca().set_facecolor(self.background_color)
        plt.gcf().set_facecolor(self.background_color)
        
        # Remove axis
        plt.axis('off')
        
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
    
    def _visualize_interactive(self, architecture: ArchitectureModel, output_path: Optional[str] = None) -> str:
        """Generate an interactive visualization of an agent architecture.
        
        Args:
            architecture: ArchitectureModel to visualize
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated HTML file or HTML content
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes (agents)
        for agent in architecture.agents:
            G.add_node(agent.id, 
                       name=agent.name, 
                       role=agent.role.value, 
                       model=agent.model_name,
                       capabilities=[cap.value for cap in agent.capabilities])
        
        # Add edges (connections)
        for conn in architecture.connections:
            G.add_edge(conn.source_id, conn.target_id, 
                       weight=conn.weight, 
                       bidirectional=conn.bidirectional)
            if conn.bidirectional:
                G.add_edge(conn.target_id, conn.source_id, 
                           weight=conn.weight, 
                           bidirectional=True)
        
        # Use a layout that works well for directed graphs
        if len(architecture.agents) <= 10:
            pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.kamada_kawai_layout(G)
        
        # Create node trace
        node_x = []
        node_y = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                colorscale='YlGnBu',
                size=15,
                line_width=2))
        
        # Set node colors based on role
        node_colors = []
        node_text = []
        for node in G.nodes():
            agent = architecture.get_agent_by_id(node)
            color = self.node_colors.get(agent.role, "#AAAAAA")
            node_colors.append(color)
            
            # Create hover text with agent details
            capabilities = ", ".join([cap.value for cap in agent.capabilities])
            hover_text = f"Name: {agent.name}<br>Role: {agent.role.value}<br>Model: {agent.model_name}<br>Capabilities: {capabilities}"
            node_text.append(hover_text)
        
        node_trace.marker.color = node_colors
        node_trace.text = node_text
        
        # Create edge trace
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color=self.edge_color),
            hoverinfo='none',
            mode='lines')
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title=f"Architecture: {architecture.name}",
                            font=dict(size=16, color=self.text_color),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            annotations=[],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            plot_bgcolor=self.background_color,
                            paper_bgcolor=self.background_color
                        ))
        
        # Add agent names as annotations
        for node in G.nodes():
            x, y = pos[node]
            agent = architecture.get_agent_by_id(node)
            fig.add_annotation(
                x=x,
                y=y,
                text=agent.name,
                showarrow=False,
                font=dict(color=self.text_color, size=10),
                xanchor="center",
                yanchor="bottom",
                yshift=10
            )
        
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
    
    def _visualize_static_comparison(self, architectures: List[ArchitectureModel], 
                                    metrics: Optional[Dict[str, Dict[str, float]]] = None, 
                                    output_path: Optional[str] = None) -> str:
        """Generate a static comparison visualization of multiple architectures.
        
        Args:
            architectures: List of ArchitectureModel objects to compare
            metrics: Optional metrics to include in the comparison
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file
        """
        n_architectures = len(architectures)
        n_cols = min(3, n_architectures)
        n_rows = (n_architectures + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6*n_cols, 5*n_rows))
        fig.suptitle("Architecture Comparison", fontsize=16)
        
        # Flatten axes array if necessary
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        elif n_rows == 1 or n_cols == 1:
            axes = axes.flatten()
        
        for i, architecture in enumerate(architectures):
            if n_rows > 1 and n_cols > 1:
                ax = axes[i // n_cols, i % n_cols]
            else:
                ax = axes[i]
            
            # Create a directed graph
            G = nx.DiGraph()
            
            # Add nodes (agents)
            for agent in architecture.agents:
                G.add_node(agent.id, 
                           name=agent.name, 
                           role=agent.role.value)
            
            # Add edges (connections)
            for conn in architecture.connections:
                G.add_edge(conn.source_id, conn.target_id, 
                           weight=conn.weight, 
                           bidirectional=conn.bidirectional)
                if conn.bidirectional:
                    G.add_edge(conn.target_id, conn.source_id, 
                               weight=conn.weight, 
                               bidirectional=True)
            
            # Use a layout that works well for directed graphs
            if len(architecture.agents) <= 10:
                pos = nx.spring_layout(G, seed=42)
            else:
                pos = nx.kamada_kawai_layout(G)
            
            # Draw nodes with role-based colors
            node_colors = [self.node_colors.get(architecture.get_agent_by_id(node).role, "#AAAAAA") 
                           for node in G.nodes()]
            
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.8, ax=ax)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, edge_color=self.edge_color, width=1.0, 
                                   arrowsize=10, alpha=0.7, ax=ax)
            
            # Add labels with agent names
            labels = {node: architecture.get_agent_by_id(node).name for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color=self.text_color, ax=ax)
            
            # Set title with architecture name and metrics if available
            title = f"{architecture.name}\n({len(architecture.agents)} agents, {len(architecture.connections)} connections)"
            if metrics and architecture.id in metrics:
                arch_metrics = metrics[architecture.id]
                if "fitness" in arch_metrics:
                    title += f"\nFitness: {arch_metrics['fitness']:.3f}"
            
            ax.set_title(title)
            ax.set_facecolor(self.background_color)
            ax.axis('off')
        
        # Hide empty subplots
        for i in range(n_architectures, n_rows * n_cols):
            if n_rows > 1 and n_cols > 1:
                axes[i // n_cols, i % n_cols].axis('off')
                axes[i // n_cols, i % n_cols].set_facecolor(self.background_color)
            else:
                axes[i].axis('off')
                axes[i].set_facecolor(self.background_color)
        
        # Set background color
        fig.patch.set_facecolor(self.background_color)
        
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
    
    def _visualize_interactive_comparison(self, architectures: List[ArchitectureModel], 
                                         metrics: Optional[Dict[str, Dict[str, float]]] = None, 
                                         output_path: Optional[str] = None) -> str:
        """Generate an interactive comparison visualization of multiple architectures.
        
        Args:
            architectures: List of ArchitectureModel objects to compare
            metrics: Optional metrics to include in the comparison
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated HTML file or HTML content
        """
        # Create a subplot figure
        from plotly.subplots import make_subplots
        
        n_architectures = len(architectures)
        n_cols = min(3, n_architectures)
        n_rows = (n_architectures + n_cols - 1) // n_cols
        
        subplot_titles = [arch.name for arch in architectures]
        fig = make_subplots(rows=n_rows, cols=n_cols, 
                           subplot_titles=subplot_titles,
                           specs=[[{"type": "scatter"} for _ in range(n_cols)] for _ in range(n_rows)])
        
        for i, architecture in enumerate(architectures):
            row = i // n_cols + 1
            col = i % n_cols + 1
            
            # Create a directed graph
            G = nx.DiGraph()
            
            # Add nodes (agents)
            for agent in architecture.agents:
                G.add_node(agent.id, 
                           name=agent.name, 
                           role=agent.role.value)
            
            # Add edges (connections)
            for conn in architecture.connections:
                G.add_edge(conn.source_id, conn.target_id, 
                           weight=conn.weight, 
                           bidirectional=conn.bidirectional)
                if conn.bidirectional:
                    G.add_edge(conn.target_id, conn.source_id, 
                               weight=conn.weight, 
                               bidirectional=True)
            
            # Use a layout that works well for directed graphs
            if len(architecture.agents) <= 10:
                pos = nx.spring_layout(G, seed=42)
            else:
                pos = nx.kamada_kawai_layout(G)
            
            # Create node trace
            node_x = []
            node_y = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                marker=dict(
                    showscale=False,
                    colorscale='YlGnBu',
                    size=12,
                    line_width=1))
            
            # Set node colors based on role
            node_colors = []
            node_text = []
            for node in G.nodes():
                agent = architecture.get_agent_by_id(node)
                color = self.node_colors.get(agent.role, "#AAAAAA")
                node_colors.append(color)
                
                # Create hover text with agent details
                capabilities = ", ".join([cap.value for cap in agent.capabilities])
                hover_text = f"Name: {agent.name}<br>Role: {agent.role.value}"
                if hasattr(agent, 'model_name') and agent.model_name:
                    hover_text += f"<br>Model: {agent.model_name}"
                if hasattr(agent, 'capabilities') and agent.capabilities:
                    hover_text += f"<br>Capabilities: {capabilities}"
                node_text.append(hover_text)
            
            node_trace.marker.color = node_colors
            node_trace.text = node_text
            
            # Create edge trace
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.8, color=self.edge_color),
                hoverinfo='none',
                mode='lines')
            
            # Add traces to subplot
            fig.add_trace(edge_trace, row=row, col=col)
            fig.add_trace(node_trace, row=row, col=col)
            
            # Add agent names as annotations
            for node in G.nodes():
                x, y = pos[node]
                agent = architecture.get_agent_by_id(node)
                fig.add_annotation(
                    x=x,
                    y=y,
                    text=agent.name,
                    showarrow=False,
                    font=dict(color=self.text_color, size=8),
                    xanchor="center",
                    yanchor="bottom",
                    yshift=8,
                    row=row,
                    col=col
                )
            
            # Add metrics if available
            if metrics and architecture.id in metrics:
                arch_metrics = metrics[architecture.id]
                if "fitness" in arch_metrics:
                    fig.add_annotation(
                        x=0.5,
                        y=-0.15,
                        text=f"Fitness: {arch_metrics['fitness']:.3f}",
                        showarrow=False,
                        font=dict(color=self.text_color),
                        xref=f"x{i+1} domain",
                        yref=f"y{i+1} domain",
                        xanchor="center",
                        row=row,
                        col=col
                    )
            
            # Update axes
            fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, row=row, col=col)
            fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, row=row, col=col)
        
        # Update layout
        fig.update_layout(
            title="Architecture Comparison",
            showlegend=False,
            plot_bgcolor=self.background_color,
            paper_bgcolor=self.background_color,
            font=dict(color=self.text_color),
            margin=dict(t=50, b=20, l=20, r=20),
            height=300 * n_rows
        )
        
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
    
    def _get_role_color(self, role: AgentRole) -> str:
        """Get the color for a specific agent role."""
        return self.node_colors.get(role, "#AAAAAA")
