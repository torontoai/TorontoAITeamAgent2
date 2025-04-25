"""
Image Generation Service for TORONTO AI TEAM AGENT

This module provides integration with multiple image generation models including
Midjourney, DALL-E 3, and Stable Diffusion, enabling the creation of high-quality
images, diagrams, mockups, and visual assets.

Features:
- Support for multiple image generation models
- Unified interface for all providers
- Image customization options (size, style, quality)
- Image storage and retrieval
- Prompt optimization for better results
"""

import os
import time
import json
import base64
import logging
import requests
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import io
from PIL import Image
import uuid

# Import auth utilities
from ...models.providers.auth_utils import get_api_key, APIKeyNotFoundError

# Set up logging
logger = logging.getLogger(__name__)


class ImageGenerationModel(Enum):
    """Available image generation models."""
    DALLE_3 = "dall-e-3"
    DALLE_2 = "dall-e-2"
    MIDJOURNEY = "midjourney"
    STABLE_DIFFUSION_XL = "stable-diffusion-xl"
    STABLE_DIFFUSION_3 = "stable-diffusion-3"


class ImageSize(Enum):
    """Available image sizes."""
    SMALL = "256x256"
    MEDIUM = "512x512"
    LARGE = "1024x1024"
    WIDE = "1024x576"
    TALL = "576x1024"
    SQUARE = "1024x1024"
    CUSTOM = "custom"


class ImageQuality(Enum):
    """Image quality options."""
    STANDARD = "standard"
    HD = "hd"


class ImageStyle(Enum):
    """Image style options."""
    NATURAL = "natural"
    VIVID = "vivid"
    ARTISTIC = "artistic"
    PHOTOGRAPHIC = "photographic"
    CINEMATIC = "cinematic"
    ANIME = "anime"
    DIGITAL_ART = "digital_art"
    SKETCH = "sketch"
    PAINTING = "painting"
    ABSTRACT = "abstract"
    REALISTIC = "realistic"


@dataclass
class GeneratedImage:
    """Represents a generated image."""
    id: str
    url: Optional[str]
    data: Optional[bytes]
    prompt: str
    model: ImageGenerationModel
    width: int
    height: int
    created_at: float  # Unix timestamp
    
    def save(self, path: str) -> str:
        """
        Save the image to a file.
        
        Args:
            path: Directory path to save the image
            
        Returns:
            Path to the saved image file
        """
        os.makedirs(path, exist_ok=True)
        
        # Generate filename based on id
        filename = os.path.join(path, f"{self.id}.png")
        
        # Save from URL if available
        if self.url:
            response = requests.get(self.url)
            with open(filename, "wb") as f:
                f.write(response.content)
        # Save from data if available
        elif self.data:
            with open(filename, "wb") as f:
                f.write(self.data)
        else:
            raise ValueError("No image data or URL available")
        
        return filename
    
    def to_pil_image(self) -> Image.Image:
        """
        Convert to PIL Image object.
        
        Returns:
            PIL Image object
        """
        if self.data:
            return Image.open(io.BytesIO(self.data))
        elif self.url:
            response = requests.get(self.url)
            return Image.open(io.BytesIO(response.content))
        else:
            raise ValueError("No image data or URL available")
    
    def to_base64(self) -> str:
        """
        Convert image to base64 string.
        
        Returns:
            Base64 encoded image string
        """
        if self.data:
            return base64.b64encode(self.data).decode("utf-8")
        elif self.url:
            response = requests.get(self.url)
            return base64.b64encode(response.content).decode("utf-8")
        else:
            raise ValueError("No image data or URL available")


class ImageGenerationError(Exception):
    """Base exception for image generation errors."""
    pass


class ImageGenerationService:
    """
    Service for generating images using various AI models.
    """
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 midjourney_api_key: Optional[str] = None,
                 stability_api_key: Optional[str] = None,
                 default_model: ImageGenerationModel = ImageGenerationModel.DALLE_3,
                 storage_dir: Optional[str] = None):
        """
        Initialize the image generation service.
        
        Args:
            openai_api_key: OpenAI API key for DALL-E (if None, will try to load from environment)
            midjourney_api_key: Midjourney API key (if None, will try to load from environment)
            stability_api_key: Stability AI API key for Stable Diffusion (if None, will try to load from environment)
            default_model: Default image generation model to use
            storage_dir: Directory for storing generated images (if None, will use a temporary directory)
        """
        # Initialize API keys
        self.openai_api_key = openai_api_key or get_api_key("OPENAI_API_KEY")
        self.midjourney_api_key = midjourney_api_key or get_api_key("MIDJOURNEY_API_KEY", required=False)
        self.stability_api_key = stability_api_key or get_api_key("STABILITY_API_KEY", required=False)
        
        # Set default model
        self.default_model = default_model
        
        # Set storage directory
        if storage_dir:
            self.storage_dir = storage_dir
            os.makedirs(self.storage_dir, exist_ok=True)
        else:
            self.storage_dir = os.path.join(os.getcwd(), "generated_images")
            os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize API endpoints
        self.openai_api_url = "https://api.openai.com/v1/images/generations"
        self.midjourney_api_url = "https://api.midjourney.com/v1/generations"  # Example URL
        self.stability_api_url = "https://api.stability.ai/v1/generation"
        
        # Check if at least one API key is available
        if not self.openai_api_key and not self.midjourney_api_key and not self.stability_api_key:
            raise APIKeyNotFoundError("No API keys found for any image generation service")
    
    def generate_image(self, 
                      prompt: str, 
                      model: Optional[ImageGenerationModel] = None,
                      size: ImageSize = ImageSize.LARGE,
                      quality: ImageQuality = ImageQuality.STANDARD,
                      style: Optional[ImageStyle] = None,
                      num_images: int = 1) -> List[GeneratedImage]:
        """
        Generate images based on a prompt.
        
        Args:
            prompt: Text description of the desired image
            model: Image generation model to use (defaults to self.default_model)
            size: Size of the generated image
            quality: Quality of the generated image
            style: Style of the generated image
            num_images: Number of images to generate
            
        Returns:
            List of GeneratedImage objects
        """
        # Use default model if not specified
        model = model or self.default_model
        
        # Check if the selected model is available
        if model in [ImageGenerationModel.DALLE_3, ImageGenerationModel.DALLE_2] and not self.openai_api_key:
            raise APIKeyNotFoundError("OpenAI API key not found for DALL-E")
        elif model == ImageGenerationModel.MIDJOURNEY and not self.midjourney_api_key:
            raise APIKeyNotFoundError("Midjourney API key not found")
        elif model in [ImageGenerationModel.STABLE_DIFFUSION_XL, ImageGenerationModel.STABLE_DIFFUSION_3] and not self.stability_api_key:
            raise APIKeyNotFoundError("Stability AI API key not found for Stable Diffusion")
        
        # Optimize prompt if needed
        optimized_prompt = self._optimize_prompt(prompt, model)
        
        # Generate images using the appropriate model
        if model in [ImageGenerationModel.DALLE_3, ImageGenerationModel.DALLE_2]:
            return self._generate_dalle_image(optimized_prompt, model, size, quality, style, num_images)
        elif model == ImageGenerationModel.MIDJOURNEY:
            return self._generate_midjourney_image(optimized_prompt, size, quality, style, num_images)
        elif model in [ImageGenerationModel.STABLE_DIFFUSION_XL, ImageGenerationModel.STABLE_DIFFUSION_3]:
            return self._generate_stable_diffusion_image(optimized_prompt, model, size, quality, style, num_images)
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def _optimize_prompt(self, prompt: str, model: ImageGenerationModel) -> str:
        """
        Optimize a prompt for better results with a specific model.
        
        Args:
            prompt: Original prompt
            model: Target model
            
        Returns:
            Optimized prompt
        """
        # Add model-specific optimizations
        if model == ImageGenerationModel.DALLE_3:
            # DALL-E 3 works well with detailed prompts
            if len(prompt) < 20:
                prompt = f"Create a detailed, high-quality image of {prompt}"
        elif model == ImageGenerationModel.MIDJOURNEY:
            # Midjourney works well with style descriptors
            if "style" not in prompt.lower() and "quality" not in prompt.lower():
                prompt = f"{prompt}, high quality, detailed"
        elif model in [ImageGenerationModel.STABLE_DIFFUSION_XL, ImageGenerationModel.STABLE_DIFFUSION_3]:
            # Stable Diffusion works well with detailed composition descriptions
            if "composition" not in prompt.lower() and len(prompt) < 30:
                prompt = f"{prompt}, detailed composition, high resolution"
        
        return prompt
    
    def _generate_dalle_image(self, 
                             prompt: str, 
                             model: ImageGenerationModel,
                             size: ImageSize,
                             quality: ImageQuality,
                             style: Optional[ImageStyle],
                             num_images: int) -> List[GeneratedImage]:
        """Generate images using DALL-E."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        # Convert model name to OpenAI format
        model_name = "dall-e-3" if model == ImageGenerationModel.DALLE_3 else "dall-e-2"
        
        # Prepare request data
        data = {
            "prompt": prompt,
            "model": model_name,
            "n": min(num_images, 4 if model == ImageGenerationModel.DALLE_3 else 10),  # DALL-E 3 has a limit of 4 images
            "size": size.value,
            "quality": quality.value
        }
        
        # Add style for DALL-E 3
        if model == ImageGenerationModel.DALLE_3 and style:
            if style in [ImageStyle.NATURAL, ImageStyle.VIVID]:
                data["style"] = style.value
        
        # Make API request
        response = requests.post(self.openai_api_url, headers=headers, json=data)
        
        if response.status_code != 200:
            raise ImageGenerationError(f"DALL-E API error: {response.text}")
        
        # Parse response
        result = response.json()
        generated_images = []
        
        for i, image_data in enumerate(result.get("data", [])):
            # Parse size from response
            width, height = map(int, size.value.split("x"))
            
            # Create GeneratedImage object
            image = GeneratedImage(
                id=f"dalle_{int(time.time())}_{i}",
                url=image_data.get("url"),
                data=None,  # DALL-E API returns URLs, not raw data
                prompt=prompt,
                model=model,
                width=width,
                height=height,
                created_at=time.time()
            )
            
            generated_images.append(image)
        
        return generated_images
    
    def _generate_midjourney_image(self, 
                                  prompt: str, 
                                  size: ImageSize,
                                  quality: ImageQuality,
                                  style: Optional[ImageStyle],
                                  num_images: int) -> List[GeneratedImage]:
        """Generate images using Midjourney."""
        # Note: This is a placeholder implementation as Midjourney doesn't have a public API
        # In a real implementation, this would use the Midjourney API or a third-party service
        
        # For demonstration purposes, we'll simulate the API call
        logger.warning("Using simulated Midjourney API (not a real implementation)")
        
        # Parse size
        width, height = map(int, size.value.split("x"))
        
        # Create simulated images
        generated_images = []
        for i in range(num_images):
            image_id = f"midjourney_{uuid.uuid4()}"
            
            # In a real implementation, this would be the URL or data from the API
            image = GeneratedImage(
                id=image_id,
                url=None,
                data=None,  # In a real implementation, this would be the image data
                prompt=prompt,
                model=ImageGenerationModel.MIDJOURNEY,
                width=width,
                height=height,
                created_at=time.time()
            )
            
            generated_images.append(image)
        
        return generated_images
    
    def _generate_stable_diffusion_image(self, 
                                        prompt: str, 
                                        model: ImageGenerationModel,
                                        size: ImageSize,
                                        quality: ImageQuality,
                                        style: Optional[ImageStyle],
                                        num_images: int) -> List[GeneratedImage]:
        """Generate images using Stable Diffusion."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.stability_api_key}"
        }
        
        # Convert model name to Stability AI format
        engine_id = "stable-diffusion-xl-1024-v1-0" if model == ImageGenerationModel.STABLE_DIFFUSION_XL else "stable-diffusion-v3"
        
        # Parse size
        width, height = map(int, size.value.split("x"))
        
        # Prepare request data
        data = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7.0,
            "height": height,
            "width": width,
            "samples": num_images,
            "steps": 50 if quality == ImageQuality.HD else 30
        }
        
        # Add style guidance if provided
        if style:
            style_preset = None
            if style == ImageStyle.CINEMATIC:
                style_preset = "cinematic"
            elif style == ImageStyle.ANIME:
                style_preset = "anime"
            elif style == ImageStyle.DIGITAL_ART:
                style_preset = "digital-art"
            elif style == ImageStyle.PHOTOGRAPHIC:
                style_preset = "photographic"
            
            if style_preset:
                data["style_preset"] = style_preset
        
        # Make API request
        api_url = f"{self.stability_api_url}/{engine_id}/text-to-image"
        response = requests.post(api_url, headers=headers, json=data)
        
        if response.status_code != 200:
            raise ImageGenerationError(f"Stability AI API error: {response.text}")
        
        # Parse response
        result = response.json()
        generated_images = []
        
        for i, image_data in enumerate(result.get("artifacts", [])):
            # Get image data
            image_bytes = base64.b64decode(image_data.get("base64"))
            
            # Create GeneratedImage object
            image = GeneratedImage(
                id=image_data.get("id", f"sd_{int(time.time())}_{i}"),
                url=None,  # Stability AI returns raw data, not URLs
                data=image_bytes,
                prompt=prompt,
                model=model,
                width=width,
                height=height,
                created_at=time.time()
            )
            
            generated_images.append(image)
        
        return generated_images
    
    def generate_and_save(self, 
                         prompt: str, 
                         model: Optional[ImageGenerationModel] = None,
                         size: ImageSize = ImageSize.LARGE,
                         quality: ImageQuality = ImageQuality.STANDARD,
                         style: Optional[ImageStyle] = None,
                         num_images: int = 1) -> List[str]:
        """
        Generate images and save them to the storage directory.
        
        Args:
            prompt: Text description of the desired image
            model: Image generation model to use
            size: Size of the generated image
            quality: Quality of the generated image
            style: Style of the generated image
            num_images: Number of images to generate
            
        Returns:
            List of paths to the saved images
        """
        # Generate images
        images = self.generate_image(prompt, model, size, quality, style, num_images)
        
        # Save images
        saved_paths = []
        for image in images:
            path = image.save(self.storage_dir)
            saved_paths.append(path)
        
        return saved_paths
    
    def generate_diagram(self, 
                        description: str, 
                        diagram_type: str = "flowchart",
                        size: ImageSize = ImageSize.LARGE) -> GeneratedImage:
        """
        Generate a diagram based on a description.
        
        Args:
            description: Description of the diagram content
            diagram_type: Type of diagram (flowchart, sequence, etc.)
            size: Size of the generated diagram
            
        Returns:
            GeneratedImage object
        """
        # Optimize prompt for diagram generation
        prompt = f"Create a clear, professional {diagram_type} diagram showing {description}. Use appropriate symbols, colors, and layout for a {diagram_type}. Include clear labels and arrows. Make it easy to understand and visually appealing."
        
        # Generate diagram using DALL-E 3 (best for diagrams)
        images = self.generate_image(
            prompt=prompt,
            model=ImageGenerationModel.DALLE_3,
            size=size,
            quality=ImageQuality.HD,
            style=ImageStyle.NATURAL,
            num_images=1
        )
        
        return images[0] if images else None
    
    def generate_mockup(self, 
                       description: str, 
                       mockup_type: str = "website",
                       style: ImageStyle = ImageStyle.NATURAL,
                       size: ImageSize = ImageSize.LARGE) -> GeneratedImage:
        """
        Generate a mockup based on a description.
        
        Args:
            description: Description of the mockup content
            mockup_type: Type of mockup (website, mobile app, etc.)
            style: Style of the mockup
            size: Size of the generated mockup
            
        Returns:
            GeneratedImage object
        """
        # Optimize prompt for mockup generation
        prompt = f"Create a professional {mockup_type} mockup with {description}. Make it modern, clean, and visually appealing. Include appropriate UI elements, typography, and layout for a {mockup_type}."
        
        # Generate mockup using DALL-E 3 (best for UI mockups)
        images = self.generate_image(
            prompt=prompt,
            model=ImageGenerationModel.DALLE_3,
            size=size,
            quality=ImageQuality.HD,
            style=style,
            num_images=1
        )
        
        return images[0] if images else None
    
    def get_available_models(self) -> List[ImageGenerationModel]:
        """
        Get a list of available image generation models.
        
        Returns:
            List of available models
        """
        available_models = []
        
        if self.openai_api_key:
            available_models.extend([ImageGenerationModel.DALLE_3, ImageGenerationModel.DALLE_2])
        
        if self.midjourney_api_key:
            available_models.append(ImageGenerationModel.MIDJOURNEY)
        
        if self.stability_api_key:
            available_models.extend([ImageGenerationModel.STABLE_DIFFUSION_XL, ImageGenerationModel.STABLE_DIFFUSION_3])
        
        return available_models
    
    def set_default_model(self, model: ImageGenerationModel) -> None:
        """
        Set the default image generation model.
        
        Args:
            model: Default model to use
        """
        if model not in self.get_available_models():
            raise ValueError(f"Model {model} is not available")
        
        self.default_model = model
    
    def set_storage_dir(self, storage_dir: str) -> None:
        """
        Set the storage directory for generated images.
        
        Args:
            storage_dir: Directory path
        """
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
