"""
Performance visualizer for Multi-agent Architecture Search (MaAS).

This module provides tools for visualizing performance metrics for agent architectures.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

from ..models import ArchitectureModel, EvaluationResult, MetricType


class PerformanceVisualizer:
    """Visualizes performance metrics for agent architectures."""
    
    def __init__(self, output_format="svg", theme="light"):
        """Initialize the performance visualizer.
        
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
    
    def visualize_metrics(self, evaluation_results: List[EvaluationResult], 
                          output_path: Optional[str] = None) -> str:
        """Generate visualizations of performance metrics.
        
        Args:
            evaluation_results: List of EvaluationResult objects
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file or HTML content
        """
        if not evaluation_results:
            raise ValueError("No evaluation results provided")
        
        if self.output_format == "html":
            return self._visualize_metrics_interactive(evaluation_results, output_path)
        else:
            return self._visualize_metrics_static(evaluation_results, output_path)
    
    def visualize_comparison(self, evaluation_results: List[EvaluationResult], 
                             metrics: Optional[List[str]] = None, 
                             output_path: Optional[str] = None) -> str:
        """Generate a comparison of performance metrics across architectures.
        
        Args:
            evaluation_results: List of EvaluationResult objects to compare
            metrics: Specific metrics to include in the comparison
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file or HTML content
        """
        if not evaluation_results:
            raise ValueError("No evaluation results provided")
        
        if self.output_format == "html":
            return self._visualize_comparison_interactive(evaluation_results, metrics, output_path)
        else:
            return self._visualize_comparison_static(evaluation_results, metrics, output_path)
    
    def _visualize_metrics_static(self, evaluation_results: List[EvaluationResult], 
                                 output_path: Optional[str] = None) -> str:
        """Generate static visualizations of performance metrics.
        
        Args:
            evaluation_results: List of EvaluationResult objects
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file
        """
        # Create a figure with subplots for different metric types
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle("Performance Metrics", fontsize=16)
        
        # Group metrics by type
        accuracy_metrics = {}
        resource_metrics = {}
        latency_metrics = {}
        other_metrics = {}
        
        for result in evaluation_results:
            arch_name = result.architecture_name
            
            for metric_name, metric_value in result.metrics.items():
                metric_type = self._get_metric_type(metric_name)
                
                if metric_type == MetricType.ACCURACY:
                    if metric_name not in accuracy_metrics:
                        accuracy_metrics[metric_name] = {}
                    accuracy_metrics[metric_name][arch_name] = metric_value
                elif metric_type == MetricType.RESOURCE:
                    if metric_name not in resource_metrics:
                        resource_metrics[metric_name] = {}
                    resource_metrics[metric_name][arch_name] = metric_value
                elif metric_type == MetricType.LATENCY:
                    if metric_name not in latency_metrics:
                        latency_metrics[metric_name] = {}
                    latency_metrics[metric_name][arch_name] = metric_value
                else:
                    if metric_name not in other_metrics:
                        other_metrics[metric_name] = {}
                    other_metrics[metric_name][arch_name] = metric_value
        
        # Plot accuracy metrics
        self._plot_metric_group(axes[0, 0], accuracy_metrics, "Accuracy Metrics", higher_is_better=True)
        
        # Plot resource metrics
        self._plot_metric_group(axes[0, 1], resource_metrics, "Resource Metrics", higher_is_better=False)
        
        # Plot latency metrics
        self._plot_metric_group(axes[1, 0], latency_metrics, "Latency Metrics", higher_is_better=False)
        
        # Plot other metrics
        self._plot_metric_group(axes[1, 1], other_metrics, "Other Metrics", higher_is_better=None)
        
        # Set background color
        fig.patch.set_facecolor(self.background_color)
        for ax in axes.flatten():
            ax.set_facecolor(self.background_color)
            ax.tick_params(colors=self.text_color)
            ax.spines['bottom'].set_color(self.text_color)
            ax.spines['top'].set_color(self.text_color)
            ax.spines['left'].set_color(self.text_color)
            ax.spines['right'].set_color(self.text_color)
            ax.xaxis.label.set_color(self.text_color)
            ax.yaxis.label.set_color(self.text_color)
            ax.title.set_color(self.text_color)
        
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
    
    def _visualize_metrics_interactive(self, evaluation_results: List[EvaluationResult], 
                                      output_path: Optional[str] = None) -> str:
        """Generate interactive visualizations of performance metrics.
        
        Args:
            evaluation_results: List of EvaluationResult objects
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated HTML file or HTML content
        """
        # Prepare data for visualization
        data = []
        for result in evaluation_results:
            arch_name = result.architecture_name
            
            for metric_name, metric_value in result.metrics.items():
                metric_type = self._get_metric_type(metric_name)
                
                data.append({
                    "Architecture": arch_name,
                    "Metric": metric_name,
                    "Value": metric_value,
                    "Type": metric_type.value
                })
        
        df = pd.DataFrame(data)
        
        # Create a subplot figure
        fig = go.Figure()
        
        # Add traces for each metric type
        for metric_type in MetricType:
            type_df = df[df["Type"] == metric_type.value]
            
            if not type_df.empty:
                for metric in type_df["Metric"].unique():
                    metric_df = type_df[type_df["Metric"] == metric]
                    
                    fig.add_trace(go.Bar(
                        x=metric_df["Architecture"],
                        y=metric_df["Value"],
                        name=metric,
                        text=metric_df["Value"].round(3),
                        textposition="auto",
                        hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>"
                    ))
        
        # Create buttons for metric type selection
        buttons = []
        
        # All metrics button
        buttons.append(dict(
            label="All Metrics",
            method="update",
            args=[{"visible": [True] * len(fig.data)},
                  {"title": "All Performance Metrics"}]
        ))
        
        # Buttons for each metric type
        for metric_type in MetricType:
            visibility = []
            for i, trace in enumerate(fig.data):
                metric_name = trace.name
                trace_type = self._get_metric_type(metric_name)
                visibility.append(trace_type == metric_type)
            
            buttons.append(dict(
                label=f"{metric_type.value} Metrics",
                method="update",
                args=[{"visible": visibility},
                      {"title": f"{metric_type.value} Performance Metrics"}]
            ))
        
        # Add dropdown menu
        fig.update_layout(
            updatemenus=[
                dict(
                    active=0,
                    buttons=buttons,
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                )
            ]
        )
        
        # Set layout
        fig.update_layout(
            title="All Performance Metrics",
            xaxis_title="Architecture",
            yaxis_title="Value",
            barmode="group",
            plot_bgcolor=self.background_color,
            paper_bgcolor=self.background_color,
            font=dict(color=self.text_color, size=12)  # Changed from titlefont_size to font
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
    
    def _visualize_comparison_static(self, evaluation_results: List[EvaluationResult], 
                                    metrics: Optional[List[str]] = None, 
                                    output_path: Optional[str] = None) -> str:
        """Generate a static comparison of performance metrics across architectures.
        
        Args:
            evaluation_results: List of EvaluationResult objects to compare
            metrics: Specific metrics to include in the comparison
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization file
        """
        # Extract all metrics if not specified
        if metrics is None:
            metrics = set()
            for result in evaluation_results:
                metrics.update(result.metrics.keys())
            metrics = list(metrics)
        
        # Prepare data for radar chart
        arch_names = [result.architecture_name for result in evaluation_results]
        n_metrics = len(metrics)
        n_architectures = len(evaluation_results)
        
        # Normalize metric values for radar chart
        normalized_values = np.zeros((n_architectures, n_metrics))
        
        for i, metric in enumerate(metrics):
            # Extract values for this metric
            values = []
            for result in evaluation_results:
                values.append(result.metrics.get(metric, 0))
            
            # Normalize values
            min_val = min(values)
            max_val = max(values)
            
            if max_val > min_val:
                # Check if higher is better for this metric
                metric_type = self._get_metric_type(metric)
                higher_is_better = (metric_type == MetricType.ACCURACY)
                
                for j, val in enumerate(values):
                    if higher_is_better:
                        # Higher values are better, normalize to [0, 1]
                        normalized_values[j, i] = (val - min_val) / (max_val - min_val)
                    else:
                        # Lower values are better, normalize to [0, 1] and invert
                        normalized_values[j, i] = 1 - (val - min_val) / (max_val - min_val)
        
        # Create radar chart
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        # Set background color
        fig.patch.set_facecolor(self.background_color)
        ax.set_facecolor(self.background_color)
        
        # Compute angle for each metric
        angles = np.linspace(0, 2*np.pi, n_metrics, endpoint=False).tolist()
        angles += angles[:1]  # Close the loop
        
        # Plot each architecture
        for i, arch_name in enumerate(arch_names):
            values = normalized_values[i].tolist()
            values += values[:1]  # Close the loop
            
            ax.plot(angles, values, linewidth=2, label=arch_name)
            ax.fill(angles, values, alpha=0.1)
        
        # Set labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        
        # Set title and legend
        ax.set_title("Architecture Performance Comparison", color=self.text_color)
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), facecolor=self.background_color, edgecolor=self.text_color)
        
        # Customize appearance
        ax.tick_params(colors=self.text_color)
        ax.grid(color=self.grid_color)
        
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
    
    def _visualize_comparison_interactive(self, evaluation_results: List[EvaluationResult], 
                                         metrics: Optional[List[str]] = None, 
                                         output_path: Optional[str] = None) -> str:
        """Generate an interactive comparison of performance metrics across architectures.
        
        Args:
            evaluation_results: List of EvaluationResult objects to compare
            metrics: Specific metrics to include in the comparison
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated HTML file or HTML content
        """
        # Extract all metrics if not specified
        if metrics is None:
            metrics = set()
            for result in evaluation_results:
                metrics.update(result.metrics.keys())
            metrics = list(metrics)
        
        # Prepare data for radar chart
        arch_names = [result.architecture_name for result in evaluation_results]
        n_metrics = len(metrics)
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each architecture
        for i, result in enumerate(evaluation_results):
            arch_name = result.architecture_name
            
            # Extract values for this architecture
            values = []
            for metric in metrics:
                values.append(result.metrics.get(metric, 0))
            
            # Close the loop
            values.append(values[0])
            metric_names = metrics + [metrics[0]]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metric_names,
                fill='toself',
                name=arch_name
            ))
        
        # Set layout
        fig.update_layout(
            title="Architecture Performance Comparison",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([max(result.metrics.values()) for result in evaluation_results]) * 1.1]
                )
            ),
            showlegend=True,
            plot_bgcolor=self.background_color,
            paper_bgcolor=self.background_color,
            font=dict(color=self.text_color, size=12)  # Changed from titlefont_size to font
        )
        
        # Create a second visualization: parallel coordinates
        # Prepare data
        data = []
        for result in evaluation_results:
            row = {"Architecture": result.architecture_name}
            for metric in metrics:
                row[metric] = result.metrics.get(metric, 0)
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Create parallel coordinates plot
        fig2 = px.parallel_coordinates(
            df, 
            color="Architecture",
            dimensions=["Architecture"] + metrics,
            color_continuous_scale=self.colorscale
        )
        
        # Update layout
        fig2.update_layout(
            title="Parallel Coordinates Comparison",
            plot_bgcolor=self.background_color,
            paper_bgcolor=self.background_color,
            font=dict(color=self.text_color, size=12)  # Changed from titlefont_size to font
        )
        
        # Combine both visualizations
        from plotly.subplots import make_subplots
        combined_fig = make_subplots(rows=2, cols=1, 
                                     specs=[[{"type": "polar"}], [{"type": "xy"}]],
                                     subplot_titles=("Radar Chart", "Parallel Coordinates"))
        
        # Add radar chart traces
        for trace in fig.data:
            combined_fig.add_trace(trace, row=1, col=1)
        
        # Add parallel coordinates traces
        for trace in fig2.data:
            combined_fig.add_trace(trace, row=2, col=1)
        
        # Update layout
        combined_fig.update_layout(
            title="Architecture Performance Comparison",
            height=1000,
            plot_bgcolor=self.background_color,
            paper_bgcolor=self.background_color,
            font=dict(color=self.text_color, size=12)  # Changed from titlefont_size to font
        )
        
        # Save or return the visualization
        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Add extension if not provided
            if not output_path.endswith(".html"):
                output_path = f"{output_path}.html"
                
            combined_fig.write_html(output_path)
            return output_path
        else:
            # Return HTML content
            return combined_fig.to_html()
    
    def _plot_metric_group(self, ax, metrics_dict, title, higher_is_better=None):
        """Plot a group of metrics on a given axis.
        
        Args:
            ax: Matplotlib axis to plot on
            metrics_dict: Dictionary of metrics {metric_name: {arch_name: value}}
            title: Title for the plot
            higher_is_better: Whether higher values are better (True/False/None)
        """
        if not metrics_dict:
            ax.text(0.5, 0.5, f"No {title} Available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, color=self.text_color)
            ax.set_title(title, color=self.text_color)
            return
        
        # Prepare data for grouped bar chart
        metrics = list(metrics_dict.keys())
        architectures = set()
        for metric_values in metrics_dict.values():
            architectures.update(metric_values.keys())
        architectures = list(architectures)
        
        # Set up bar positions
        x = np.arange(len(metrics))
        width = 0.8 / len(architectures)
        
        # Plot bars for each architecture
        for i, arch in enumerate(architectures):
            values = []
            for metric in metrics:
                values.append(metrics_dict[metric].get(arch, 0))
            
            offset = width * i - width * (len(architectures) - 1) / 2
            bars = ax.bar(x + offset, values, width, label=arch)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom',
                            color=self.text_color,
                            fontsize=8)
        
        # Set labels and title
        ax.set_xlabel('Metrics', color=self.text_color)
        ax.set_ylabel('Value', color=self.text_color)
        ax.set_title(title, color=self.text_color)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        
        # Add legend
        ax.legend()
        
        # Add a note about interpretation if specified
        if higher_is_better is not None:
            note = "Higher is better" if higher_is_better else "Lower is better"
            ax.annotate(note, xy=(0.5, 0.97), xycoords='axes fraction',
                        ha='center', va='top', color=self.text_color,
                        bbox=dict(boxstyle="round,pad=0.3", fc=self.background_color, 
                                  ec=self.primary_color, alpha=0.7))
    
    def _get_metric_type(self, metric_name: str) -> MetricType:
        """Determine the type of a metric based on its name.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            MetricType enum value
        """
        metric_name = metric_name.lower()
        
        # Accuracy metrics
        if any(term in metric_name for term in ['accuracy', 'precision', 'recall', 'f1', 'auc', 'success']):
            return MetricType.ACCURACY
        
        # Resource metrics
        if any(term in metric_name for term in ['memory', 'cpu', 'gpu', 'resource', 'cost', 'token', 'call']):
            return MetricType.RESOURCE
        
        # Latency metrics
        if any(term in metric_name for term in ['latency', 'time', 'speed', 'duration', 'delay']):
            return MetricType.LATENCY
        
        # Default to OTHER
        return MetricType.OTHER
