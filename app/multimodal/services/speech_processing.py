"""
Speech Processing Service for TORONTO AI TEAM AGENT

This module provides integration with speech-to-text (Whisper) and text-to-speech
(Eleven Labs) services, enabling audio content creation and processing.

Features:
- Speech-to-text transcription with OpenAI's Whisper
- Text-to-speech synthesis with Eleven Labs
- Audio file handling and processing
- Voice customization options
- Support for multiple languages
"""

import os
import time
import json
import base64
import logging
import requests
from typing import Dict, List, Optional, Union, Any, BinaryIO
from enum import Enum
from dataclasses import dataclass
import io
import uuid

# Import auth utilities
from ...models.providers.auth_utils import get_api_key, APIKeyNotFoundError

# Set up logging
logger = logging.getLogger(__name__)


class WhisperModel(Enum):
    """Available Whisper models for speech-to-text."""
    WHISPER_1 = "whisper-1"


class ElevenLabsVoice(Enum):
    """Available Eleven Labs voices for text-to-speech."""
    ADAM = "Adam"
    ANTONI = "Antoni"
    ARNOLD = "Arnold"
    BELLA = "Bella"
    DOMI = "Domi"
    ELLI = "Elli"
    JOSH = "Josh"
    RACHEL = "Rachel"
    SAM = "Sam"
    CUSTOM = "custom"


class AudioFormat(Enum):
    """Available audio formats."""
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    FLAC = "flac"


@dataclass
class TranscriptionResult:
    """Represents a speech-to-text transcription result."""
    id: str
    text: str
    model: WhisperModel
    language: Optional[str]
    duration: float  # Duration in seconds
    created_at: float  # Unix timestamp
    segments: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "model": self.model.value,
            "language": self.language,
            "duration": self.duration,
            "created_at": self.created_at,
            "segments": self.segments
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranscriptionResult':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            text=data["text"],
            model=WhisperModel(data["model"]),
            language=data.get("language"),
            duration=data["duration"],
            created_at=data["created_at"],
            segments=data.get("segments")
        )


@dataclass
class SynthesizedSpeech:
    """Represents a text-to-speech synthesis result."""
    id: str
    audio_data: bytes
    text: str
    voice: ElevenLabsVoice
    format: AudioFormat
    duration: Optional[float] = None  # Duration in seconds
    created_at: float = time.time()  # Unix timestamp
    
    def save(self, path: str) -> str:
        """
        Save the audio to a file.
        
        Args:
            path: Directory path to save the audio
            
        Returns:
            Path to the saved audio file
        """
        os.makedirs(path, exist_ok=True)
        
        # Generate filename based on id and format
        filename = os.path.join(path, f"{self.id}.{self.format.value}")
        
        # Save audio data
        with open(filename, "wb") as f:
            f.write(self.audio_data)
        
        return filename
    
    def to_base64(self) -> str:
        """
        Convert audio to base64 string.
        
        Returns:
            Base64 encoded audio string
        """
        return base64.b64encode(self.audio_data).decode("utf-8")


class SpeechProcessingError(Exception):
    """Base exception for speech processing errors."""
    pass


class SpeechProcessingService:
    """
    Service for speech-to-text and text-to-speech processing.
    """
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 elevenlabs_api_key: Optional[str] = None,
                 storage_dir: Optional[str] = None):
        """
        Initialize the speech processing service.
        
        Args:
            openai_api_key: OpenAI API key for Whisper (if None, will try to load from environment)
            elevenlabs_api_key: Eleven Labs API key (if None, will try to load from environment)
            storage_dir: Directory for storing audio files (if None, will use a temporary directory)
        """
        # Initialize API keys
        self.openai_api_key = openai_api_key or get_api_key("OPENAI_API_KEY")
        self.elevenlabs_api_key = elevenlabs_api_key or get_api_key("ELEVENLABS_API_KEY", required=False)
        
        # Set storage directory
        if storage_dir:
            self.storage_dir = storage_dir
            os.makedirs(self.storage_dir, exist_ok=True)
        else:
            self.storage_dir = os.path.join(os.getcwd(), "audio_files")
            os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize API endpoints
        self.openai_api_url = "https://api.openai.com/v1/audio"
        self.elevenlabs_api_url = "https://api.elevenlabs.io/v1"
        
        # Check if at least one API key is available
        if not self.openai_api_key and not self.elevenlabs_api_key:
            raise APIKeyNotFoundError("No API keys found for any speech processing service")
    
    def transcribe(self, 
                  audio_file: Union[str, BinaryIO], 
                  model: WhisperModel = WhisperModel.WHISPER_1,
                  language: Optional[str] = None,
                  prompt: Optional[str] = None,
                  temperature: float = 0.0,
                  with_segments: bool = False) -> TranscriptionResult:
        """
        Transcribe speech to text using Whisper.
        
        Args:
            audio_file: Path to audio file or file-like object
            model: Whisper model to use
            language: Language code (e.g., "en", "fr", "de")
            prompt: Optional prompt to guide the transcription
            temperature: Sampling temperature (0.0 to 1.0)
            with_segments: Whether to include timestamps for each segment
            
        Returns:
            TranscriptionResult object
        """
        if not self.openai_api_key:
            raise APIKeyNotFoundError("OpenAI API key not found for Whisper")
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        # Prepare request data
        data = {
            "model": model.value,
            "temperature": temperature
        }
        
        if language:
            data["language"] = language
        
        if prompt:
            data["prompt"] = prompt
        
        if with_segments:
            data["response_format"] = "verbose_json"
        
        # Prepare file
        files = {}
        if isinstance(audio_file, str):
            files["file"] = open(audio_file, "rb")
            file_size = os.path.getsize(audio_file)
        else:
            # Get current position
            current_pos = audio_file.tell()
            
            # Go to end of file to get size
            audio_file.seek(0, 2)
            file_size = audio_file.tell()
            
            # Go back to original position
            audio_file.seek(current_pos)
            
            files["file"] = audio_file
        
        # Check file size (Whisper has a 25MB limit)
        if file_size > 25 * 1024 * 1024:
            raise ValueError("Audio file exceeds 25MB limit for Whisper API")
        
        # Make API request
        try:
            response = requests.post(
                f"{self.openai_api_url}/transcriptions",
                headers=headers,
                data=data,
                files=files
            )
            
            # Close file if it was opened here
            if isinstance(audio_file, str) and "file" in files:
                files["file"].close()
            
            if response.status_code != 200:
                raise SpeechProcessingError(f"Whisper API error: {response.text}")
            
            # Parse response
            result = response.json()
            
            # Create TranscriptionResult object
            if with_segments:
                text = result.get("text", "")
                segments = result.get("segments", [])
                duration = sum(segment.get("end", 0) - segment.get("start", 0) for segment in segments)
                
                return TranscriptionResult(
                    id=f"whisper_{int(time.time())}",
                    text=text,
                    model=model,
                    language=language or result.get("language"),
                    duration=duration,
                    created_at=time.time(),
                    segments=segments
                )
            else:
                text = result.get("text", "") if isinstance(result, dict) else result
                
                return TranscriptionResult(
                    id=f"whisper_{int(time.time())}",
                    text=text,
                    model=model,
                    language=language,
                    duration=0.0,  # Duration not available without segments
                    created_at=time.time()
                )
        
        except Exception as e:
            # Close file if it was opened here
            if isinstance(audio_file, str) and "file" in files:
                files["file"].close()
            
            raise SpeechProcessingError(f"Error transcribing audio: {str(e)}")
    
    def synthesize_speech(self, 
                         text: str, 
                         voice: ElevenLabsVoice = ElevenLabsVoice.RACHEL,
                         format: AudioFormat = AudioFormat.MP3,
                         stability: float = 0.5,
                         similarity_boost: float = 0.5,
                         custom_voice_id: Optional[str] = None) -> SynthesizedSpeech:
        """
        Synthesize text to speech using Eleven Labs.
        
        Args:
            text: Text to synthesize
            voice: Voice to use
            format: Audio format
            stability: Voice stability (0.0 to 1.0)
            similarity_boost: Voice similarity boost (0.0 to 1.0)
            custom_voice_id: Custom voice ID (required if voice is CUSTOM)
            
        Returns:
            SynthesizedSpeech object
        """
        if not self.elevenlabs_api_key:
            raise APIKeyNotFoundError("Eleven Labs API key not found")
        
        # Check if custom voice ID is provided when needed
        if voice == ElevenLabsVoice.CUSTOM and not custom_voice_id:
            raise ValueError("Custom voice ID is required when using CUSTOM voice")
        
        # Prepare headers
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        
        # Get voice ID
        voice_id = custom_voice_id if voice == ElevenLabsVoice.CUSTOM else self._get_voice_id(voice)
        
        # Prepare request data
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        # Make API request
        try:
            response = requests.post(
                f"{self.elevenlabs_api_url}/text-to-speech/{voice_id}",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise SpeechProcessingError(f"Eleven Labs API error: {response.text}")
            
            # Get audio data
            audio_data = response.content
            
            # Create SynthesizedSpeech object
            return SynthesizedSpeech(
                id=f"elevenlabs_{int(time.time())}",
                audio_data=audio_data,
                text=text,
                voice=voice,
                format=format
            )
        
        except Exception as e:
            raise SpeechProcessingError(f"Error synthesizing speech: {str(e)}")
    
    def _get_voice_id(self, voice: ElevenLabsVoice) -> str:
        """Get the voice ID for a predefined voice."""
        # These are example voice IDs - in a real implementation, these would be the actual IDs
        voice_ids = {
            ElevenLabsVoice.ADAM: "pNInz6obpgDQGcFmaJgB",
            ElevenLabsVoice.ANTONI: "ErXwobaYiN019PkySvjV",
            ElevenLabsVoice.ARNOLD: "VR6AewLTigWG4xSOukaG",
            ElevenLabsVoice.BELLA: "EXAVITQu4vr4xnSDxMaL",
            ElevenLabsVoice.DOMI: "AZnzlk1XvdvUeBnXmlld",
            ElevenLabsVoice.ELLI: "MF3mGyEYCl7XYWbV9V6O",
            ElevenLabsVoice.JOSH: "TxGEqnHWrfWFTfGW9XjX",
            ElevenLabsVoice.RACHEL: "21m00Tcm4TlvDq8ikWAM",
            ElevenLabsVoice.SAM: "yoZ06aMxZJJ28mfd3POQ"
        }
        
        return voice_ids.get(voice, "21m00Tcm4TlvDq8ikWAM")  # Default to Rachel if not found
    
    def transcribe_and_save(self, 
                           audio_file: Union[str, BinaryIO],
                           output_file: Optional[str] = None,
                           model: WhisperModel = WhisperModel.WHISPER_1,
                           language: Optional[str] = None,
                           prompt: Optional[str] = None) -> str:
        """
        Transcribe speech to text and save the result to a file.
        
        Args:
            audio_file: Path to audio file or file-like object
            output_file: Path to output file (if None, will generate a filename)
            model: Whisper model to use
            language: Language code
            prompt: Optional prompt to guide the transcription
            
        Returns:
            Path to the saved transcription file
        """
        # Transcribe audio
        result = self.transcribe(audio_file, model, language, prompt)
        
        # Generate output filename if not provided
        if not output_file:
            output_file = os.path.join(self.storage_dir, f"{result.id}.txt")
        
        # Save transcription
        with open(output_file, "w") as f:
            f.write(result.text)
        
        return output_file
    
    def synthesize_and_save(self, 
                           text: str, 
                           output_file: Optional[str] = None,
                           voice: ElevenLabsVoice = ElevenLabsVoice.RACHEL,
                           format: AudioFormat = AudioFormat.MP3) -> str:
        """
        Synthesize text to speech and save the result to a file.
        
        Args:
            text: Text to synthesize
            output_file: Path to output file (if None, will generate a filename)
            voice: Voice to use
            format: Audio format
            
        Returns:
            Path to the saved audio file
        """
        # Synthesize speech
        result = self.synthesize_speech(text, voice, format)
        
        # Generate output filename if not provided
        if not output_file:
            output_file = os.path.join(self.storage_dir, f"{result.id}.{format.value}")
        
        # Save audio
        with open(output_file, "wb") as f:
            f.write(result.audio_data)
        
        return output_file
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get a list of available voices from Eleven Labs.
        
        Returns:
            List of voice information dictionaries
        """
        if not self.elevenlabs_api_key:
            raise APIKeyNotFoundError("Eleven Labs API key not found")
        
        # Prepare headers
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        
        # Make API request
        try:
            response = requests.get(
                f"{self.elevenlabs_api_url}/voices",
                headers=headers
            )
            
            if response.status_code != 200:
                raise SpeechProcessingError(f"Eleven Labs API error: {response.text}")
            
            # Parse response
            result = response.json()
            
            return result.get("voices", [])
        
        except Exception as e:
            raise SpeechProcessingError(f"Error getting available voices: {str(e)}")
    
    def set_storage_dir(self, storage_dir: str) -> None:
        """
        Set the storage directory for audio files.
        
        Args:
            storage_dir: Directory path
        """
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
