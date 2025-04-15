"""
Hugging Face Transformers integration for TORONTO AI TEAM AGENT.

This module provides integration with Hugging Face Transformers library
for enhanced multimodal processing capabilities.
"""

import os
from typing import Any, Dict, List, Optional, Union
import logging

import torch
from transformers import (
    AutoTokenizer, 
    AutoModel, 
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoModelForQuestionAnswering,
    AutoModelForImageClassification,
    AutoModelForAudioClassification,
    AutoFeatureExtractor,
    AutoProcessor,
    pipeline
)

from app.core.error_handling import ErrorHandler, ErrorCategory, ErrorSeverity, safe_execute
from app.multimodal.models.content_models import (
    TextContent, 
    ImageContent, 
    AudioContent, 
    VideoContent,
    MultimodalContent
)

logger = logging.getLogger(__name__)

class ModelCache:
    """Cache for Hugging Face models to avoid reloading."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelCache, cls).__new__(cls)
            cls._instance._models = {}
            cls._instance._tokenizers = {}
            cls._instance._processors = {}
            cls._instance._pipelines = {}
        return cls._instance
    
    def get_model(self, model_name: str, task_type: Optional[str] = None) -> Any:
        """Get a model from cache or load it."""
        key = f"{model_name}_{task_type}" if task_type else model_name
        
        if key not in self._models:
            with ErrorHandler(
                error_category=ErrorCategory.MULTIMODAL,
                error_message=f"Error loading model {model_name} for task {task_type}",
                severity=ErrorSeverity.HIGH
            ):
                if task_type == "causal_lm":
                    self._models[key] = AutoModelForCausalLM.from_pretrained(model_name)
                elif task_type == "sequence_classification":
                    self._models[key] = AutoModelForSequenceClassification.from_pretrained(model_name)
                elif task_type == "question_answering":
                    self._models[key] = AutoModelForQuestionAnswering.from_pretrained(model_name)
                elif task_type == "image_classification":
                    self._models[key] = AutoModelForImageClassification.from_pretrained(model_name)
                elif task_type == "audio_classification":
                    self._models[key] = AutoModelForAudioClassification.from_pretrained(model_name)
                else:
                    self._models[key] = AutoModel.from_pretrained(model_name)
                
        return self._models[key]
    
    def get_tokenizer(self, model_name: str) -> Any:
        """Get a tokenizer from cache or load it."""
        if model_name not in self._tokenizers:
            with ErrorHandler(
                error_category=ErrorCategory.MULTIMODAL,
                error_message=f"Error loading tokenizer for {model_name}",
                severity=ErrorSeverity.MEDIUM
            ):
                self._tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
                
        return self._tokenizers[model_name]
    
    def get_processor(self, model_name: str) -> Any:
        """Get a processor from cache or load it."""
        if model_name not in self._processors:
            with ErrorHandler(
                error_category=ErrorCategory.MULTIMODAL,
                error_message=f"Error loading processor for {model_name}",
                severity=ErrorSeverity.MEDIUM
            ):
                self._processors[model_name] = AutoProcessor.from_pretrained(model_name)
                
        return self._processors[model_name]
    
    def get_pipeline(self, task: str, model_name: Optional[str] = None) -> Any:
        """Get a pipeline from cache or create it."""
        key = f"{task}_{model_name}" if model_name else task
        
        if key not in self._pipelines:
            with ErrorHandler(
                error_category=ErrorCategory.MULTIMODAL,
                error_message=f"Error creating pipeline for task {task} with model {model_name}",
                severity=ErrorSeverity.MEDIUM
            ):
                if model_name:
                    self._pipelines[key] = pipeline(task, model=model_name)
                else:
                    self._pipelines[key] = pipeline(task)
                
        return self._pipelines[key]
    
    def clear_cache(self) -> None:
        """Clear the model cache to free memory."""
        self._models.clear()
        self._tokenizers.clear()
        self._processors.clear()
        self._pipelines.clear()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class HuggingFaceClient:
    """Client for interacting with Hugging Face models."""
    
    def __init__(self, cache_models: bool = True):
        """
        Initialize the Hugging Face client.
        
        Args:
            cache_models: Whether to cache models for reuse
        """
        self.cache_models = cache_models
        self.model_cache = ModelCache() if cache_models else None
        
        # Check for CUDA availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
    
    def process_text(
        self, 
        text: str, 
        task: str = "text-classification", 
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process text using a Hugging Face model.
        
        Args:
            text: The text to process
            task: The task to perform (e.g., text-classification, question-answering)
            model_name: The name of the model to use (optional)
            
        Returns:
            Dict containing the processing results
        """
        with ErrorHandler(
            error_category=ErrorCategory.MULTIMODAL,
            error_message=f"Error processing text with task {task}",
            severity=ErrorSeverity.MEDIUM
        ):
            if self.cache_models:
                pipeline_instance = self.model_cache.get_pipeline(task, model_name)
            else:
                pipeline_instance = pipeline(task, model=model_name) if model_name else pipeline(task)
            
            result = pipeline_instance(text)
            return self._format_result(result, task)
    
    def process_image(
        self, 
        image_path: str, 
        task: str = "image-classification", 
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an image using a Hugging Face model.
        
        Args:
            image_path: Path to the image file
            task: The task to perform (e.g., image-classification, object-detection)
            model_name: The name of the model to use (optional)
            
        Returns:
            Dict containing the processing results
        """
        with ErrorHandler(
            error_category=ErrorCategory.MULTIMODAL,
            error_message=f"Error processing image with task {task}",
            severity=ErrorSeverity.MEDIUM
        ):
            if self.cache_models:
                pipeline_instance = self.model_cache.get_pipeline(task, model_name)
            else:
                pipeline_instance = pipeline(task, model=model_name) if model_name else pipeline(task)
            
            result = pipeline_instance(image_path)
            return self._format_result(result, task)
    
    def process_audio(
        self, 
        audio_path: str, 
        task: str = "automatic-speech-recognition", 
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process audio using a Hugging Face model.
        
        Args:
            audio_path: Path to the audio file
            task: The task to perform (e.g., automatic-speech-recognition, audio-classification)
            model_name: The name of the model to use (optional)
            
        Returns:
            Dict containing the processing results
        """
        with ErrorHandler(
            error_category=ErrorCategory.MULTIMODAL,
            error_message=f"Error processing audio with task {task}",
            severity=ErrorSeverity.MEDIUM
        ):
            if self.cache_models:
                pipeline_instance = self.model_cache.get_pipeline(task, model_name)
            else:
                pipeline_instance = pipeline(task, model=model_name) if model_name else pipeline(task)
            
            result = pipeline_instance(audio_path)
            return self._format_result(result, task)
    
    def generate_text(
        self, 
        prompt: str, 
        model_name: str = "gpt2", 
        max_length: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        num_return_sequences: int = 1
    ) -> Dict[str, Any]:
        """
        Generate text using a Hugging Face model.
        
        Args:
            prompt: The prompt to generate text from
            model_name: The name of the model to use
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            num_return_sequences: Number of sequences to generate
            
        Returns:
            Dict containing the generated text
        """
        with ErrorHandler(
            error_category=ErrorCategory.MULTIMODAL,
            error_message=f"Error generating text with model {model_name}",
            severity=ErrorSeverity.MEDIUM
        ):
            if self.cache_models:
                tokenizer = self.model_cache.get_tokenizer(model_name)
                model = self.model_cache.get_model(model_name, "causal_lm")
            else:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Move model to appropriate device
            model = model.to(self.device)
            
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate text
            outputs = model.generate(
                inputs["input_ids"],
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                num_return_sequences=num_return_sequences,
                do_sample=True
            )
            
            # Decode output
            generated_texts = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
            
            return {
                "generated_texts": generated_texts,
                "model": model_name,
                "prompt": prompt
            }
    
    def embed_text(
        self, 
        text: Union[str, List[str]], 
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> Dict[str, Any]:
        """
        Generate embeddings for text using a Hugging Face model.
        
        Args:
            text: The text to embed (string or list of strings)
            model_name: The name of the model to use
            
        Returns:
            Dict containing the embeddings
        """
        with ErrorHandler(
            error_category=ErrorCategory.MULTIMODAL,
            error_message=f"Error embedding text with model {model_name}",
            severity=ErrorSeverity.MEDIUM
        ):
            if self.cache_models:
                tokenizer = self.model_cache.get_tokenizer(model_name)
                model = self.model_cache.get_model(model_name)
            else:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModel.from_pretrained(model_name)
            
            # Move model to appropriate device
            model = model.to(self.device)
            
            # Prepare input
            if isinstance(text, str):
                texts = [text]
            else:
                texts = text
            
            # Tokenize input
            encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors="pt").to(self.device)
            
            # Get model output
            with torch.no_grad():
                model_output = model(**encoded_input)
            
            # Mean pooling
            attention_mask = encoded_input["attention_mask"]
            token_embeddings = model_output.last_hidden_state
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            
            # Convert to numpy for easier handling
            embeddings = embeddings.cpu().numpy()
            
            return {
                "embeddings": embeddings,
                "model": model_name,
                "dimension": embeddings.shape[1]
            }
    
    def embed_image(
        self, 
        image_path: str, 
        model_name: str = "google/vit-base-patch16-224"
    ) -> Dict[str, Any]:
        """
        Generate embeddings for an image using a Hugging Face model.
        
        Args:
            image_path: Path to the image file
            model_name: The name of the model to use
            
        Returns:
            Dict containing the embeddings
        """
        with ErrorHandler(
            error_category=ErrorCategory.MULTIMODAL,
            error_message=f"Error embedding image with model {model_name}",
            severity=ErrorSeverity.MEDIUM
        ):
            from PIL import Image
            
            if self.cache_models:
                feature_extractor = self.model_cache.get_processor(model_name)
                model = self.model_cache.get_model(model_name)
            else:
                feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
                model = AutoModel.from_pretrained(model_name)
            
            # Move model to appropriate device
            model = model.to(self.device)
            
            # Load and preprocess image
            image = Image.open(image_path)
            inputs = feature_extractor(images=image, return_tensors="pt").to(self.device)
            
            # Get model output
            with torch.no_grad():
                outputs = model(**inputs)
            
            # Get embeddings (use pooler output if available, otherwise use mean of last hidden state)
            if hasattr(outputs, "pooler_output"):
                embeddings = outputs.pooler_output
            else:
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            # Convert to numpy for easier handling
            embeddings = embeddings.cpu().numpy()
            
            return {
                "embeddings": embeddings,
                "model": model_name,
                "dimension": embeddings.shape[1]
            }
    
    def _format_result(self, result: Any, task: str) -> Dict[str, Any]:
        """Format the result based on the task type."""
        if task == "text-classification":
            return {"labels": [item["label"] for item in result], "scores": [item["score"] for item in result]}
        
        elif task == "token-classification":
            entities = {}
            for item in result:
                entity_type = item["entity"]
                if entity_type not in entities:
                    entities[entity_type] = []
                entities[entity_type].append({"word": item["word"], "score": item["score"]})
            return {"entities": entities}
        
        elif task == "question-answering":
            return {"answer": result["answer"], "score": result["score"], "start": result["start"], "end": result["end"]}
        
        elif task == "summarization":
            return {"summary": result[0]["summary_text"]}
        
        elif task == "translation":
            return {"translation": result[0]["translation_text"]}
        
        elif task == "image-classification":
            return {"labels": [item["label"] for item in result], "scores": [item["score"] for item in result]}
        
        elif task == "object-detection":
            objects = []
            for item in result:
                objects.append({
                    "label": item["label"],
                    "score": item["score"],
                    "box": {"xmin": item["box"]["xmin"], "ymin": item["box"]["ymin"], 
                           "xmax": item["box"]["xmax"], "ymax": item["box"]["ymax"]}
                })
            return {"objects": objects}
        
        elif task == "automatic-speech-recognition":
            return {"text": result["text"]}
        
        elif task == "audio-classification":
            return {"labels": [item["label"] for item in result], "scores": [item["score"] for item in result]}
        
        # Default case: return the raw result
        return {"result": result}
    
    def clear_cache(self) -> None:
        """Clear the model cache to free memory."""
        if self.cache_models and self.model_cache:
            self.model_cache.clear_cache()


class TransformersService:
    """Service for integrating Hugging Face Transformers with the multimodal system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Transformers service.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.cache_models = self.config.get("cache_models", True)
        self.client = HuggingFaceClient(cache_models=self.cache_models)
    
    def process_text_content(self, content: TextContent) -> Dict[str, Any]:
        """
        Process text content using appropriate models.
        
        Args:
            content: TextContent object
            
        Returns:
            Dict containing processing results
        """
        results = {}
        
        # Analyze sentiment
        sentiment_result = self.client.process_text(
            content.text,
            task="sentiment-analysis",
            model_name=self.config.get("sentiment_model")
        )
        results["sentiment"] = sentiment_result
        
        # Extract entities
        entities_result = self.client.process_text(
            content.text,
            task="token-classification",
            model_name=self.config.get("ner_model")
        )
        results["entities"] = entities_result
        
        # Generate embeddings
        embedding_result = self.client.embed_text(
            content.text,
            model_name=self.config.get("text_embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        )
        results["embedding"] = embedding_result
        
        return results
    
    def process_image_content(self, content: ImageContent) -> Dict[str, Any]:
        """
        Process image content using appropriate models.
        
        Args:
            content: ImageContent object
            
        Returns:
            Dict containing processing results
        """
        results = {}
        
        # Classify image
        classification_result = self.client.process_image(
            content.path,
            task="image-classification",
            model_name=self.config.get("image_classification_model")
        )
        results["classification"] = classification_result
        
        # Detect objects
        detection_result = self.client.process_image(
            content.path,
            task="object-detection",
            model_name=self.config.get("object_detection_model")
        )
        results["objects"] = detection_result
        
        # Generate embeddings
        embedding_result = self.client.embed_image(
            content.path,
            model_name=self.config.get("image_embedding_model", "google/vit-base-patch16-224")
        )
        results["embedding"] = embedding_result
        
        return results
    
    def process_audio_content(self, content: AudioContent) -> Dict[str, Any]:
        """
        Process audio content using appropriate models.
        
        Args:
            content: AudioContent object
            
        Returns:
            Dict containing processing results
        """
        results = {}
        
        # Transcribe audio
        transcription_result = self.client.process_audio(
            content.path,
            task="automatic-speech-recognition",
            model_name=self.config.get("speech_recognition_model")
        )
        results["transcription"] = transcription_result
        
        # Classify audio
        classification_result = self.client.process_audio(
            content.path,
            task="audio-classification",
            model_name=self.config.get("audio_classification_model")
        )
        results["classification"] = classification_result
        
        return results
    
    def process_multimodal_content(self, content: MultimodalContent) -> Dict[str, Any]:
        """
        Process multimodal content using appropriate models.
        
        Args:
            content: MultimodalContent object
            
        Returns:
            Dict containing processing results
        """
        results = {}
        
        # Process each content type
        if content.text:
            results["text"] = self.process_text_content(content.text)
        
        if content.images:
            results["images"] = [self.process_image_content(image) for image in content.images]
        
        if content.audio:
            results["audio"] = [self.process_audio_content(audio) for audio in content.audio]
        
        # TODO: Add video processing when available
        
        return results
    
    def generate_text_from_multimodal(self, content: MultimodalContent, prompt: str) -> Dict[str, Any]:
        """
        Generate text based on multimodal content and a prompt.
        
        Args:
            content: MultimodalContent object
            prompt: Text prompt to guide generation
            
        Returns:
            Dict containing generated text
        """
        # Process the multimodal content first
        content_results = self.process_multimodal_content(content)
        
        # Extract key information from the content results
        context = self._extract_context_from_results(content_results)
        
        # Combine the context with the prompt
        enhanced_prompt = f"Context:\n{context}\n\nPrompt: {prompt}"
        
        # Generate text using the enhanced prompt
        generation_result = self.client.generate_text(
            enhanced_prompt,
            model_name=self.config.get("text_generation_model", "gpt2-xl"),
            max_length=self.config.get("max_generation_length", 200),
            temperature=self.config.get("temperature", 0.7),
            top_p=self.config.get("top_p", 0.9),
            num_return_sequences=self.config.get("num_return_sequences", 1)
        )
        
        return generation_result
    
    def _extract_context_from_results(self, results: Dict[str, Any]) -> str:
        """Extract a textual context from processing results."""
        context_parts = []
        
        # Extract text information
        if "text" in results:
            text_results = results["text"]
            
            # Add sentiment
            if "sentiment" in text_results and "labels" in text_results["sentiment"]:
                sentiment = text_results["sentiment"]["labels"][0]
                context_parts.append(f"Text sentiment: {sentiment}")
            
            # Add entities
            if "entities" in text_results and "entities" in text_results["entities"]:
                entities = text_results["entities"]["entities"]
                entity_strings = []
                for entity_type, items in entities.items():
                    entity_words = [item["word"] for item in items]
                    entity_strings.append(f"{entity_type}: {', '.join(entity_words)}")
                if entity_strings:
                    context_parts.append(f"Entities: {'; '.join(entity_strings)}")
        
        # Extract image information
        if "images" in results:
            for i, image_results in enumerate(results["images"]):
                image_context_parts = []
                
                # Add classification
                if "classification" in image_results and "labels" in image_results["classification"]:
                    top_labels = image_results["classification"]["labels"][:3]  # Top 3 labels
                    image_context_parts.append(f"Image content: {', '.join(top_labels)}")
                
                # Add objects
                if "objects" in image_results and "objects" in image_results["objects"]:
                    objects = image_results["objects"]["objects"]
                    object_labels = [obj["label"] for obj in objects]
                    if object_labels:
                        image_context_parts.append(f"Objects: {', '.join(object_labels)}")
                
                if image_context_parts:
                    context_parts.append(f"Image {i+1}: {' | '.join(image_context_parts)}")
        
        # Extract audio information
        if "audio" in results:
            for i, audio_results in enumerate(results["audio"]):
                audio_context_parts = []
                
                # Add transcription
                if "transcription" in audio_results and "text" in audio_results["transcription"]:
                    transcription = audio_results["transcription"]["text"]
                    audio_context_parts.append(f"Transcription: {transcription}")
                
                # Add classification
                if "classification" in audio_results and "labels" in audio_results["classification"]:
                    top_labels = audio_results["classification"]["labels"][:3]  # Top 3 labels
                    audio_context_parts.append(f"Audio type: {', '.join(top_labels)}")
                
                if audio_context_parts:
                    context_parts.append(f"Audio {i+1}: {' | '.join(audio_context_parts)}")
        
        return "\n".join(context_parts)
