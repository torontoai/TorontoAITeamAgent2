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
import cv2
import numpy as np
from PIL import Image
import pytesseract
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class WireframeAnalysisResult(BaseModel):
    """Result of wireframe analysis."""
    components: List[Dict[str, Any]]
    layout: Dict[str, Any]
    style_guide: Dict[str, Any]
    interactions: List[Dict[str, Any]]
    text_content: Dict[str, Any]

class ProjectRequirement(BaseModel):
    """Project requirement extracted from specifications."""
    id: str
    type: str  # functional, non-functional, technical, business
    description: str
    priority: str  # high, medium, low
    dependencies: List[str] = []
    acceptance_criteria: List[str] = []

class ProjectSpecification(BaseModel):
    """Complete project specification."""
    title: str
    description: str
    requirements: List[ProjectRequirement]
    components: List[Dict[str, Any]]
    architecture: Dict[str, Any]
    timeline: Dict[str, Any]
    resources: Dict[str, Any]

class WireframeAnalyzer:
    """Wireframe analyzer for the multi-agent team system.
    Analyzes wireframes and mockups to extract components, layout, and interactions."""
    
    def __init__(self):
        """Initialize the wireframe analyzer."""
        # Initialize computer vision models
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize computer vision models."""
        # This would typically load pre-trained models for component detection
        # For now, we'll use basic OpenCV functionality
        pass
    
    async def analyze_wireframe(self, image_path: str) -> WireframeAnalysisResult:
        """
        Analyze a wireframe image.
        
        Args:
            image_path: Path to wireframe image
            
        Returns:
            WireframeAnalysisResult
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Extract text using OCR
        text_content = self._extract_text(image_path)
        
        # Detect UI components
        components = self._detect_components(gray)
        
        # Analyze layout
        layout = self._analyze_layout(components)
        
        # Extract style information
        style_guide = self._extract_style_guide(image)
        
        # Infer interactions
        interactions = self._infer_interactions(components, text_content)
        
        return WireframeAnalysisResult(
            components=components,
            layout=layout,
            style_guide=style_guide,
            interactions=interactions,
            text_content=text_content
        )
    
    def _extract_text(self, image_path: str) -> Dict[str, Any]:
        """Extract text from image using OCR.
        
        Args:
            image_path: Path to image
            
        Returns:
            Dictionary of extracted text"""
        # Use Tesseract OCR to extract text
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            
            # Process text into structured format
            lines = text.split('\n')
            
            # Categorize text (headings, paragraphs, labels, buttons)
            headings = []
            paragraphs = []
            labels = []
            buttons = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Simple heuristics for categorization
                if len(line) < 20 and line.isupper():
                    headings.append(line)
                elif len(line) < 15 and ':' in line:
                    labels.append(line)
                elif len(line) < 20 and any(btn in line.lower() for btn in ['submit', 'save', 'cancel', 'login', 'sign up', 'button']):
                    buttons.append(line)
                elif len(line) > 30:
                    paragraphs.append(line)
                else:
                    labels.append(line)
            
            return {
                "headings": headings,
                "paragraphs": paragraphs,
                "labels": labels,
                "buttons": buttons,
                "raw_text": text
            }
        except Exception as e:
            print(f"OCR error: {str(e)}")
            return {"error": str(e), "raw_text": ""}
    
    def _detect_components(self, gray_image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI components in grayscale image.
        
        Args:
            gray_image: Grayscale image
            
        Returns:
            List of detected components"""
        components = []
        
        # Detect edges
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process contours to identify UI components
        for i, contour in enumerate(contours):
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter out very small contours
            if w < 20 or h < 20:
                continue
            
            # Determine component type based on shape and size
            component_type = self._classify_component(gray_image[y:y+h, x:x+w], w, h)
            
            components.append({
                "id": f"component-{i}",
                "type": component_type,
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h)
            })
        
        return components
    
    def _classify_component(self, component_image: np.ndarray, width: int, height: int) -> str:
        """Classify a UI component based on its image and dimensions.
        
        Args:
            component_image: Component image
            width: Component width
            height: Component height
            
        Returns:
            Component type"""
        # Simple heuristics for component classification
        aspect_ratio = width / height if height > 0 else 0
        
        if aspect_ratio > 5:
            return "text_input"
        elif aspect_ratio > 3:
            return "progress_bar"
        elif aspect_ratio < 0.2:
            return "sidebar"
        elif width > 100 and height > 100:
            return "container"
        elif width < 50 and height < 50:
            return "button"
        elif width > 100 and height < 50:
            return "dropdown"
        else:
            return "unknown"
    
    def _analyze_layout(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze layout of components.
        
        Args:
            components: List of components
            
        Returns:
            Layout analysis"""
        if not components:
            return {"type": "unknown", "structure": "unknown"}
        
        # Sort components by y-coordinate
        sorted_by_y = sorted(components, key=lambda c: c["y"])
        
        # Group components by row
        rows = []
        current_row = [sorted_by_y[0]]
        
        for i in range(1, len(sorted_by_y)):
            current = sorted_by_y[i]
            previous = sorted_by_y[i-1]
            
            # If current component is significantly below previous, start a new row
            if current["y"] > previous["y"] + previous["height"] * 0.5:
                rows.append(current_row)
                current_row = [current]
            else:
                current_row.append(current)
        
        if current_row:
            rows.append(current_row)
        
        # Determine layout type
        if len(rows) == 1:
            layout_type = "single_row"
        elif all(len(row) == 1 for row in rows):
            layout_type = "single_column"
        elif len(rows) > 1 and any(len(row) > 1 for row in rows):
            layout_type = "grid"
        else:
            layout_type = "complex"
        
        # Check for common patterns
        has_header = any(c["y"] < 100 and c["width"] > 200 for c in components)
        has_footer = any(c["y"] > 500 and c["width"] > 200 for c in components)
        has_sidebar = any(c["x"] < 100 and c["height"] > 300 for c in components)
        
        return {
            "type": layout_type,
            "rows": len(rows),
            "has_header": has_header,
            "has_footer": has_footer,
            "has_sidebar": has_sidebar,
            "row_details": [{"components": len(row)} for row in rows]
        }
    
    def _extract_style_guide(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract style guide from image.
        
        Args:
            image: Image
            
        Returns:
            Style guide"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Get dominant colors
        colors = self._get_dominant_colors(image)
        
        # Analyze text styles (would require more sophisticated OCR)
        text_styles = {
            "heading_font": "default",
            "body_font": "default",
            "font_sizes": ["default"]
        }
        
        return {
            "colors": colors,
            "text_styles": text_styles,
            "spacing": "default",
            "border_radius": "default"
        }
    
    def _get_dominant_colors(self, image: np.ndarray, num_colors: int = 5) -> List[Dict[str, Any]]:
        """Get dominant colors from image.
        
        Args:
            image: Image
            num_colors: Number of dominant colors to extract
            
        Returns:
            List of dominant colors"""
        # Reshape image to be a list of pixels
        pixels = image.reshape((-1, 3))
        
        # Convert to float32
        pixels = np.float32(pixels)
        
        # Define criteria and apply kmeans
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert back to uint8
        centers = np.uint8(centers)
        
        # Count occurrences of each label
        unique_labels, counts = np.unique(labels, return_counts=True)
        
        # Sort by count
        sorted_indices = np.argsort(counts)[::-1]
        
        # Get colors and their percentages
        colors = []
        for i in sorted_indices:
            color = centers[i].tolist()
            percentage = counts[i] / len(labels) * 100
            
            # Convert BGR to hex
            hex_color = f"#{color[2]:02x}{color[1]:02x}{color[0]:02x}"
            
            colors.append({
                "hex": hex_color,
                "rgb": [color[2], color[1], color[0]],
                "percentage": float(percentage)
            })
        
        return colors
    
    def _infer_interactions(self, components: List[Dict[str, Any]], text_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Infer interactions from components and text.
        
        Args:
            components: List of components
            text_content: Extracted text content
            
        Returns:
            List of inferred interactions"""
        interactions = []
        
        # Look for buttons
        buttons = [c for c in components if c["type"] == "button"]
        for button in buttons:
            # Try to associate button with nearby text
            button_text = self._find_text_for_component(button, text_content)
            
            interaction_type = "click"
            if button_text:
                if any(s in button_text.lower() for s in ["submit", "save", "add"]):
                    action = "form_submit"
                elif any(s in button_text.lower() for s in ["cancel", "close", "back"]):
                    action = "navigation"
                else:
                    action = "generic_action"
            else:
                action = "generic_action"
            
            interactions.append({
                "component_id": button["id"],
                "type": interaction_type,
                "action": action,
                "text": button_text
            })
        
        # Look for inputs
        inputs = [c for c in components if c["type"] == "text_input"]
        for input_field in inputs:
            # Try to associate input with nearby label
            input_label = self._find_text_for_component(input_field, text_content)
            
            interactions.append({
                "component_id": input_field["id"],
                "type": "input",
                "action": "text_entry",
                "label": input_label
            })
        
        return interactions
    
    def _find_text_for_component(self, component: Dict[str, Any], text_content: Dict[str, Any]) -> Optional[str]:
        """Find text associated with a component.
        
        Args:
            component: Component
            text_content: Extracted text content
            
        Returns:
            Associated text or None"""
        # This is a simplified approach - in a real implementation, we would use
        # spatial relationships between text and components for better matching
        
        # For buttons, check button text
        if component["type"] == "button" and "buttons" in text_content:
            for button_text in text_content["buttons"]:
                return button_text  # Return first match for simplicity
        
        # For inputs, check labels
        if component["type"] == "text_input" and "labels" in text_content:
            for label in text_content["labels"]:
                return label  # Return first match for simplicity
        
        return None

class RequirementsExtractor:
    """Requirements extractor for the multi-agent team system.
    Extracts structured requirements from project specifications and wireframes."""
    
    def __init__(self):
        """Initialize the requirements extractor."""
        pass
    
    async def extract_requirements(self, specification_text: str, wireframe_analysis: Optional[WireframeAnalysisResult] = None) -> List[ProjectRequirement]:
        """
        Extract requirements from specification text and wireframe analysis.
        
        Args:
            specification_text: Project specification text
            wireframe_analysis: Optional wireframe analysis result
            
        Returns:
            List of project requirements
        """
        requirements = []
        
        # Extract requirements from text
        text_requirements = self._extract_from_text(specification_text)
        requirements.extend(text_requirements)
        
        # Extract requirements from wireframe if available
        if wireframe_analysis:
            wireframe_requirements = self._extract_from_wireframe(wireframe_analysis)
            requirements.extend(wireframe_requirements)
        
        # Deduplicate requirements
        unique_requirements = []
        descriptions = set()
        
        for req in requirements:
            if req.description not in descriptions:
                unique_requirements.append(req)
                descriptions.add(req.description)
        
        return unique_requirements
    
    def _extract_from_text(self, text: str) -> List[ProjectRequirement]:
        """Extract requirements from text.
        
        Args:
            text: Specification text
            
        Returns:
            List of requirements"""
        requirements = []
        
        # Split text into lines
        lines = text.split('\n')
        
        # Look for requirement patterns
        req_id = 1
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for common requirement indicators
            is_requirement = False
            req_type = "functional"
            priority = "medium"
            
            # Check for requirement keywords
            if any(kw in line.lower() for kw in ["must", "should", "shall", "will", "needs to", "required to"]):
                is_requirement = True
            
            # Check for non-functional indicators
            if any(kw in line.lower() for kw in ["performance", "security", "usability", "reliability", "scalability"]):
                req_type = "non-functional"
            
            # Check for priority indicators
            if any(kw in line.lower() for kw in ["critical", "highest", "essential"]):
                priority = "high"
            elif any(kw in line.lower() for kw in ["optional", "nice to have", "if possible"]):
                priority = "low"
            
            if is_requirement:
                requirement = ProjectRequirement(
                    id=f"REQ-{req_id:03d}",
                    type=req_type,
                    description=line,
                    priority=priority,
                    dependencies=[],
                    acceptance_criteria=[]
                )
                requirements.append(requirement)
                req_id += 1
        
        return requirements
    
    def _extract_from_wireframe(self, wireframe_analysis: WireframeAnalysisResult) -> List[ProjectRequirement]:
        """Extract requirements from wireframe analysis.
        
        Args:
            wireframe_analysis: Wireframe analysis result
            
        Returns:
            List of requirements"""
        requirements = []
        req_id = 1
        
        # Extract component requirements
        for component in wireframe_analysis.components:
            component_type = component["type"]
            
            if component_type == "button":
                description = f"The system must include a button component at position ({component['x']}, {component['y']})."
                requirements.append(ProjectRequirement(
                    id=f"WREQ-{req_id:03d}",
                    type="functional",
                    description=description,
                    priority="medium"
                ))
                req_id += 1
            
            elif component_type == "text_input":
                description = f"The system must include a text input field at position ({component['x']}, {component['y']})."
                requirements.append(ProjectRequirement(
                    id=f"WREQ-{req_id:03d}",
                    type="functional",
                    description=description,
                    priority="medium"
                ))
                req_id += 1
        
        # Extract layout requirements
        layout = wireframe_analysis.layout
        layout_type = layout["type"]
        
        description = f"The user interface must follow a {layout_type} layout structure."
        requirements.append(ProjectRequirement(
            id=f"WREQ-{req_id:03d}",
            type="non-functional",
            description=description,
            priority="high"
        ))
        req_id += 1
        
        if layout["has_header"]:
            description = "The user interface must include a header section."
            requirements.append(ProjectRequirement(
                id=f"WREQ-{req_id:03d}",
                type="functional",
                description=description,
                priority="medium"
            ))
            req_id += 1
        
        if layout["has_footer"]:
            description = "The user interface must include a footer section."
            requirements.append(ProjectRequirement(
                id=f"WREQ-{req_id:03d}",
                type="functional",
                description=description,
                priority="medium"
            ))
            req_id += 1
        
        if layout["has_sidebar"]:
            description = "The user interface must include a sidebar navigation."
            requirements.append(ProjectRequirement(
                id=f"WREQ-{req_id:03d}",
                type="functional",
                description=description,
                priority="medium"
            ))
            req_id += 1
        
        # Extract style requirements
        style_guide = wireframe_analysis.style_guide
        colors = style_guide["colors"]
        
        if colors:
            primary_color = colors[0]["hex"]
            description = f"The user interface must use {primary_color} as the primary color."
            requirements.append(ProjectRequirement(
                id=f"WREQ-{req_id:03d}",
                type="non-functional",
                description=description,
                priority="medium"
            ))
            req_id += 1
        
        # Extract interaction requirements
        for interaction in wireframe_analysis.interactions:
            interaction_type = interaction["type"]
            action = interaction["action"]
            
            description = f"The system must support {interaction_type} interaction with {action} action."
            requirements.append(ProjectRequirement(
                id=f"WREQ-{req_id:03d}",
                type="functional",
                description=description,
                priority="medium"
            ))
            req_id += 1
        
        return requirements

class ProjectSpecificationGenerator:
    """Project specification generator for the multi-agent team system.
    Generates complete project specifications from requirements and wireframes."""
    
    def __init__(self):
        """Initialize the project specification generator."""
        pass
    
    async def generate_specification(self, title: str, description: str, requirements: List[ProjectRequirement], wireframe_analysis: Optional[WireframeAnalysisResult] = None) -> ProjectSpecification:
        """
        Generate a complete project specification.
        
        Args:
            title: Project title
            description: Project description
            requirements: List of requirements
            wireframe_analysis: Optional wireframe analysis result
            
        Returns:
            Complete project specification
        """
        # Generate component specifications
        components = self._generate_component_specifications(requirements, wireframe_analysis)
        
        # Generate architecture specification
        architecture = self._generate_architecture_specification(requirements)
        
        # Generate timeline
        timeline = self._generate_timeline(requirements, components)
        
        # Generate resource requirements
        resources = self._generate_resource_requirements(requirements, components, architecture)
        
        return ProjectSpecification(
            title=title,
            description=description,
            requirements=requirements,
            components=components,
            architecture=architecture,
            timeline=timeline,
            resources=resources
        )
    
    def _generate_component_specifications(self, requirements: List[ProjectRequirement], wireframe_analysis: Optional[WireframeAnalysisResult] = None) -> List[Dict[str, Any]]:
        """Generate component specifications from requirements and wireframe analysis.
        
        Args:
            requirements: List of requirements
            wireframe_analysis: Optional wireframe analysis result
            
        Returns:
            List of component specifications"""
        components = []
        
        # If we have wireframe analysis, use it as the basis for components
        if wireframe_analysis:
            for component in wireframe_analysis.components:
                component_spec = {
                    "id": component["id"],
                    "type": component["type"],
                    "position": {
                        "x": component["x"],
                        "y": component["y"]
                    },
                    "size": {
                        "width": component["width"],
                        "height": component["height"]
                    },
                    "properties": {}
                }
                
                # Add additional properties based on component type
                if component["type"] == "button":
                    component_spec["properties"]["label"] = "Button"
                    component_spec["properties"]["action"] = "click"
                
                elif component["type"] == "text_input":
                    component_spec["properties"]["placeholder"] = "Enter text"
                    component_spec["properties"]["validation"] = None
                
                components.append(component_spec)
        
        # Extract additional components from requirements
        for requirement in requirements:
            # Look for component-related requirements
            if "component" in requirement.description.lower() or "interface" in requirement.description.lower():
                # This is a simplified approach - in a real implementation, we would use
                # NLP to better understand the requirement and extract component details
                
                # For now, just add a generic component if it's not already covered
                component_types = [c["type"] for c in components]
                
                if "button" in requirement.description.lower() and "button" not in component_types:
                    components.append({
                        "id": f"req-button-{requirement.id}",
                        "type": "button",
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 100, "height": 40},
                        "properties": {
                            "label": "Button",
                            "action": "click"
                        }
                    })
                
                elif "input" in requirement.description.lower() and "text_input" not in component_types:
                    components.append({
                        "id": f"req-input-{requirement.id}",
                        "type": "text_input",
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 200, "height": 40},
                        "properties": {
                            "placeholder": "Enter text",
                            "validation": None
                        }
                    })
        
        return components
    
    def _generate_architecture_specification(self, requirements: List[ProjectRequirement]) -> Dict[str, Any]:
        """Generate architecture specification from requirements.
        
        Args:
            requirements: List of requirements
            
        Returns:
            Architecture specification"""
        # Determine if we need a database
        needs_database = any("database" in req.description.lower() or "data" in req.description.lower() or "store" in req.description.lower() for req in requirements)
        
        # Determine if we need authentication
        needs_auth = any("login" in req.description.lower() or "authentication" in req.description.lower() or "user account" in req.description.lower() for req in requirements)
        
        # Determine if we need a backend API
        needs_api = needs_database or needs_auth or any("api" in req.description.lower() or "server" in req.description.lower() for req in requirements)
        
        # Determine frontend framework based on requirements
        frontend_framework = "React"  # Default
        if any("mobile" in req.description.lower() or "ios" in req.description.lower() or "android" in req.description.lower() for req in requirements):
            frontend_framework = "React Native"
        
        # Determine backend framework
        backend_framework = "Node.js/Express" if needs_api else None
        
        # Determine database
        database = "MongoDB" if needs_database else None
        
        # Create architecture specification
        architecture = {
            "type": "web_application" if frontend_framework == "React" else "mobile_application",
            "frontend": {
                "framework": frontend_framework,
                "state_management": "Redux",
                "routing": frontend_framework == "React"
            },
            "backend": {
                "required": needs_api,
                "framework": backend_framework,
                "api_type": "REST"
            },
            "database": {
                "required": needs_database,
                "type": database,
                "orm": database is not None
            },
            "authentication": {
                "required": needs_auth,
                "type": "JWT" if needs_auth else None
            },
            "deployment": {
                "frontend": "Vercel",
                "backend": "Heroku" if needs_api else None,
                "database": "MongoDB Atlas" if needs_database else None
            }
        }
        
        return architecture
    
    def _generate_timeline(self, requirements: List[ProjectRequirement], components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate project timeline from requirements and components.
        
        Args:
            requirements: List of requirements
            components: List of component specifications
            
        Returns:
            Project timeline"""
        # Calculate complexity based on requirements and components
        num_requirements = len(requirements)
        num_components = len(components)
        
        # Calculate high-priority requirements
        high_priority = len([r for r in requirements if r.priority == "high"])
        
        # Estimate phases and durations
        planning_days = max(3, num_requirements // 5)
        design_days = max(5, num_components // 3)
        development_days = max(10, (num_requirements + num_components) // 2)
        testing_days = max(5, development_days // 2)
        deployment_days = 3
        
        # Adjust for complexity
        complexity_factor = 1.0
        if num_requirements > 20 or num_components > 15:
            complexity_factor = 1.5
        elif num_requirements > 10 or num_components > 8:
            complexity_factor = 1.2
        
        planning_days = int(planning_days * complexity_factor)
        design_days = int(design_days * complexity_factor)
        development_days = int(development_days * complexity_factor)
        testing_days = int(testing_days * complexity_factor)
        
        # Create timeline
        timeline = {
            "total_duration_days": planning_days + design_days + development_days + testing_days + deployment_days,
            "phases": [
                {
                    "name": "Planning",
                    "duration_days": planning_days,
                    "tasks": [
                        {"name": "Requirements Analysis", "duration_days": planning_days // 2},
                        {"name": "Project Setup", "duration_days": planning_days // 2}
                    ]
                },
                {
                    "name": "Design",
                    "duration_days": design_days,
                    "tasks": [
                        {"name": "UI/UX Design", "duration_days": design_days // 2},
                        {"name": "Architecture Design", "duration_days": design_days // 2}
                    ]
                },
                {
                    "name": "Development",
                    "duration_days": development_days,
                    "tasks": [
                        {"name": "Frontend Development", "duration_days": development_days // 2},
                        {"name": "Backend Development", "duration_days": development_days // 2}
                    ]
                },
                {
                    "name": "Testing",
                    "duration_days": testing_days,
                    "tasks": [
                        {"name": "Unit Testing", "duration_days": testing_days // 3},
                        {"name": "Integration Testing", "duration_days": testing_days // 3},
                        {"name": "User Acceptance Testing", "duration_days": testing_days // 3}
                    ]
                },
                {
                    "name": "Deployment",
                    "duration_days": deployment_days,
                    "tasks": [
                        {"name": "Production Deployment", "duration_days": deployment_days}
                    ]
                }
            ],
            "milestones": [
                {"name": "Project Kickoff", "day": 0},
                {"name": "Design Approval", "day": planning_days + design_days},
                {"name": "Development Complete", "day": planning_days + design_days + development_days},
                {"name": "Testing Complete", "day": planning_days + design_days + development_days + testing_days},
                {"name": "Project Launch", "day": planning_days + design_days + development_days + testing_days + deployment_days}
            ]
        }
        
        return timeline
    
    def _generate_resource_requirements(self, requirements: List[ProjectRequirement], components: List[Dict[str, Any]], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resource requirements from project specifications.
        
        Args:
            requirements: List of requirements
            components: List of component specifications
            architecture: Architecture specification
            
        Returns:
            Resource requirements"""
        # Determine team size based on project complexity
        num_requirements = len(requirements)
        num_components = len(components)
        
        # Calculate base team size
        frontend_devs = 1
        backend_devs = 1 if architecture["backend"]["required"] else 0
        designers = 1
        qa_engineers = 1
        
        # Adjust for complexity
        if num_requirements > 20 or num_components > 15:
            frontend_devs = 2
            backend_devs = 2 if architecture["backend"]["required"] else 0
            designers = 2
            qa_engineers = 2
        
        # Create resource requirements
        resources = {
            "team": {
                "roles": [
                    {"title": "Project Manager", "count": 1},
                    {"title": "UI/UX Designer", "count": designers},
                    {"title": "Frontend Developer", "count": frontend_devs},
                    {"title": "Backend Developer", "count": backend_devs},
                    {"title": "QA Engineer", "count": qa_engineers}
                ],
                "total_headcount": 1 + designers + frontend_devs + backend_devs + qa_engineers
            },
            "infrastructure": {
                "development": {
                    "environments": ["development", "staging", "production"],
                    "services": []
                },
                "production": {
                    "hosting": architecture["deployment"]["frontend"],
                    "services": []
                }
            },
            "tools": {
                "design": ["Figma"],
                "development": ["VS Code", "Git"],
                "testing": ["Jest", "Cypress"],
                "deployment": ["GitHub Actions"]
            }
        }
        
        # Add backend services if needed
        if architecture["backend"]["required"]:
            resources["infrastructure"]["production"]["services"].append({
                "name": "Backend API",
                "provider": architecture["deployment"]["backend"],
                "tier": "Standard"
            })
        
        # Add database if needed
        if architecture["database"]["required"]:
            resources["infrastructure"]["production"]["services"].append({
                "name": "Database",
                "provider": architecture["deployment"]["database"],
                "tier": "Standard"
            })
        
        # Add authentication if needed
        if architecture["authentication"]["required"]:
            resources["infrastructure"]["production"]["services"].append({
                "name": "Authentication",
                "provider": "Auth0",
                "tier": "Free"
            })
        
        return resources

class ProjectUnderstandingModule:
    """Project understanding module for the multi-agent team system.
    Provides advanced capabilities for understanding project requirements and wireframes."""
    
    def __init__(self, app: FastAPI):
        """Initialize the project understanding module.
        
        Args:
            app: FastAPI application"""
        self.app = app
        self.wireframe_analyzer = WireframeAnalyzer()
        self.requirements_extractor = RequirementsExtractor()
        self.specification_generator = ProjectSpecificationGenerator()
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register routes with the FastAPI app."""
        
        @self.app.post("/api/project/analyze-wireframe", response_model=WireframeAnalysisResult)
        async def analyze_wireframe(file: UploadFile = File(...)):
            """
            Analyze a wireframe image.
            
            Args:
                file: Wireframe image file
                
            Returns:
                WireframeAnalysisResult
            """
            # Save uploaded file
            file_path = f"/tmp/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            # Analyze wireframe
            result = await self.wireframe_analyzer.analyze_wireframe(file_path)
            
            # Clean up
            os.remove(file_path)
            
            return result
        
        @self.app.post("/api/project/extract-requirements", response_model=List[ProjectRequirement])
        async def extract_requirements(specification_text: str = Form(...), wireframe_analysis_id: Optional[str] = Form(None)):
            """
            Extract requirements from specification text and wireframe analysis.
            
            Args:
                specification_text: Project specification text
                wireframe_analysis_id: Optional ID of wireframe analysis result
                
            Returns:
                List of project requirements
            """
            # Get wireframe analysis if provided
            wireframe_analysis = None
            # In a real implementation, we would retrieve the wireframe analysis from a database
            
            # Extract requirements
            requirements = await self.requirements_extractor.extract_requirements(specification_text, wireframe_analysis)
            
            return requirements
        
        @self.app.post("/api/project/generate-specification", response_model=ProjectSpecification)
        async def generate_specification(
            title: str = Form(...),
            description: str = Form(...),
            requirements: List[ProjectRequirement] = Form(...),
            wireframe_analysis_id: Optional[str] = Form(None)
        ):
            """
            Generate a complete project specification.
            
            Args:
                title: Project title
                description: Project description
                requirements: List of requirements
                wireframe_analysis_id: Optional ID of wireframe analysis result
                
            Returns:
                Complete project specification
            """
            # Get wireframe analysis if provided
            wireframe_analysis = None
            # In a real implementation, we would retrieve the wireframe analysis from a database
            
            # Generate specification
            specification = await self.specification_generator.generate_specification(
                title, description, requirements, wireframe_analysis
            )
            
            return specification

# Function to create project understanding module
def create_project_understanding_module(app: FastAPI) -> ProjectUnderstandingModule:
    """Create and initialize the project understanding module.
    
    Args:
        app: FastAPI application
        
    Returns:
        ProjectUnderstandingModule instance"""
    return ProjectUnderstandingModule(app)
