# AI Model Integrations Documentation

This document provides comprehensive documentation for the AI model integrations implemented in the TORONTO AI TEAM AGENT system, including Anthropic Claude 3 Opus, Image Generation (Midjourney/DALL-E 3/Stable Diffusion), Speech Processing (Whisper/Eleven Labs), and Google Gemini Pro/Ultra.

## Table of Contents

1. [Anthropic Claude 3 Opus Integration](#anthropic-claude-3-opus-integration)
2. [Image Generation Services](#image-generation-services)
3. [Speech Processing Services](#speech-processing-services)
4. [Google Gemini Pro/Ultra Integration](#google-gemini-proultra-integration)
5. [Integration with Other Components](#integration-with-other-components)
6. [Usage Examples](#usage-examples)

## Anthropic Claude 3 Opus Integration

The Anthropic Claude 3 Opus integration adds Claude's strongest model for complex reasoning and nuanced understanding to the TORONTO AI TEAM AGENT system.

### Core Components

#### ClaudeProvider

The `ClaudeProvider` class is the low-level interface to the Claude API.

```python
from app.models.providers.claude_provider import ClaudeProvider, ClaudeModel

# Create a provider
provider = ClaudeProvider(api_key="your_api_key")

# Generate text
response = provider.generate_text(
    prompt="Explain the concept of quantum computing in simple terms.",
    model=ClaudeModel.CLAUDE_3_OPUS,
    max_tokens=500,
    temperature=0.7
)

print(response)
```

#### ClaudeAdapter

The `ClaudeAdapter` class provides a higher-level interface for working with Claude models.

```python
from app.models.adapters.claude_adapter import ClaudeAdapter

# Create an adapter
adapter = ClaudeAdapter(api_key="your_api_key")

# Generate a response
response = adapter.generate_response(
    prompt="Explain the concept of quantum computing in simple terms.",
    max_tokens=500,
    temperature=0.7
)

print(response)
```

#### ClaudeThinkAdapter

The `ClaudeThinkAdapter` class is a specialized adapter that uses Claude's "think" reasoning mode for complex problems.

```python
from app.models.adapters.claude_adapter import ClaudeThinkAdapter

# Create a think adapter
think_adapter = ClaudeThinkAdapter(api_key="your_api_key")

# Generate a thoughtful response
response = think_adapter.generate_response(
    prompt="What are the ethical implications of artificial general intelligence?",
    max_tokens=1000,
    temperature=0.5
)

print(response)
```

### Key Features

- **Advanced Reasoning Modes**: Access to Claude's specialized reasoning modes for different types of tasks
- **Large Context Window**: Utilize Claude's 200K token context window for processing large documents
- **Nuanced Understanding**: Leverage Claude's ability to understand complex instructions and nuanced content
- **Multimodal Capabilities**: Process both text and images with Claude's multimodal capabilities
- **Streaming Responses**: Support for streaming responses for real-time interaction
- **System Instructions**: Ability to set system instructions to guide Claude's behavior

## Image Generation Services

The Image Generation Services integration adds capabilities for creating mockups, diagrams, and visual assets using Midjourney, DALL-E 3, and Stable Diffusion.

### Core Components

#### ImageGenerationService

The `ImageGenerationService` class is the main entry point for generating images.

```python
from app.multimodal.services.image_generation import ImageGenerationService, ImageGenerationModel, ImageSize

# Create a service
service = ImageGenerationService()

# Generate an image with DALL-E 3
images = service.generate_image(
    prompt="A futuristic city with flying cars and tall glass buildings",
    model=ImageGenerationModel.DALLE_3,
    size=ImageSize.LARGE,
    num_images=1
)

# Save the image
for image in images:
    image.save("futuristic_city.png")
```

#### ImageGenerationModel

The `ImageGenerationModel` enum defines the available image generation models.

**Values:**
- `DALLE_3`: OpenAI's DALL-E 3 model
- `MIDJOURNEY`: Midjourney's image generation model
- `STABLE_DIFFUSION`: Stability AI's Stable Diffusion model

#### GeneratedImage

The `GeneratedImage` class represents a generated image.

**Properties:**
- `data`: Image data as bytes
- `url`: URL of the image (if available)
- `prompt`: Prompt used to generate the image
- `model`: Model used to generate the image
- `created_at`: Creation timestamp

### Key Features

- **Multiple Models**: Support for multiple image generation models
- **Prompt Engineering**: Advanced prompt engineering for better results
- **Image Variations**: Generate variations of existing images
- **Diagram Generation**: Specialized support for generating diagrams
- **Mockup Creation**: Tools for creating UI/UX mockups
- **Style Control**: Control over artistic style and visual attributes
- **Image Editing**: Ability to edit and modify generated images

## Speech Processing Services

The Speech Processing Services integration adds advanced speech-to-text and text-to-speech capabilities for audio content creation and processing using Whisper and Eleven Labs.

### Core Components

#### SpeechProcessingService

The `SpeechProcessingService` class is the main entry point for speech processing.

```python
from app.multimodal.services.speech_processing import SpeechProcessingService, WhisperModel, ElevenLabsVoice

# Create a service
service = SpeechProcessingService()

# Transcribe audio with Whisper
transcription = service.transcribe(
    audio_file="recording.mp3",
    model=WhisperModel.WHISPER_1
)

print(f"Transcription: {transcription.text}")

# Synthesize speech with Eleven Labs
speech = service.synthesize_speech(
    text="Hello, this is a test of the speech synthesis system.",
    voice=ElevenLabsVoice.RACHEL
)

# Save the audio
speech.save("synthesized_speech.mp3")
```

#### WhisperModel

The `WhisperModel` enum defines the available speech-to-text models.

**Values:**
- `WHISPER_1`: OpenAI's Whisper v1 model
- `WHISPER_LARGE`: OpenAI's Whisper large model

#### ElevenLabsVoice

The `ElevenLabsVoice` enum defines the available text-to-speech voices.

**Values:**
- `RACHEL`: Female voice with American accent
- `ADAM`: Male voice with American accent
- `EMILY`: Female voice with British accent
- `JOSH`: Male voice with British accent
- `CUSTOM`: Custom voice (requires voice ID)

#### Transcription

The `Transcription` class represents a transcribed audio.

**Properties:**
- `text`: Transcribed text
- `segments`: List of time-stamped segments
- `language`: Detected language
- `model`: Model used for transcription
- `audio_duration`: Duration of the audio in seconds

#### SynthesizedSpeech

The `SynthesizedSpeech` class represents synthesized speech.

**Properties:**
- `audio_data`: Audio data as bytes
- `text`: Text used to generate the speech
- `voice`: Voice used for synthesis
- `created_at`: Creation timestamp

### Key Features

- **High-Quality Transcription**: Accurate transcription of audio files
- **Multilingual Support**: Support for multiple languages
- **Natural-Sounding Voices**: High-quality, natural-sounding voices for speech synthesis
- **Voice Customization**: Ability to customize voice characteristics
- **Emotion and Emphasis**: Control over emotional tone and emphasis
- **Audio Processing**: Tools for processing and enhancing audio
- **Real-Time Processing**: Support for real-time transcription and synthesis

## Google Gemini Pro/Ultra Integration

The Google Gemini Pro/Ultra integration adds Google's multimodal models for additional reasoning capabilities to the TORONTO AI TEAM AGENT system.

### Core Components

#### GeminiProvider

The `GeminiProvider` class is the low-level interface to the Gemini API.

```python
from app.models.providers.gemini_provider import GeminiProvider, GeminiModel

# Create a provider
provider = GeminiProvider(api_key="your_api_key")

# Generate text
response = provider.generate_text(
    prompt="Explain the concept of quantum computing in simple terms.",
    model=GeminiModel.GEMINI_PRO,
    max_tokens=500,
    temperature=0.7
)

print(response)
```

#### GeminiAdapter

The `GeminiAdapter` class provides a higher-level interface for working with Gemini models.

```python
from app.models.adapters.gemini_adapter import GeminiAdapter

# Create an adapter
adapter = GeminiAdapter(api_key="your_api_key")

# Generate a response
response = adapter.generate_response(
    prompt="Explain the concept of quantum computing in simple terms.",
    max_tokens=500,
    temperature=0.7
)

print(response)
```

#### GeminiMultimodalAdapter

The `GeminiMultimodalAdapter` class is a specialized adapter for working with Gemini's multimodal capabilities.

```python
from app.models.adapters.gemini_adapter import GeminiMultimodalAdapter

# Create a multimodal adapter
multimodal_adapter = GeminiMultimodalAdapter(api_key="your_api_key")

# Analyze an image
response = multimodal_adapter.analyze_image(
    image=open("image.jpg", "rb").read(),
    prompt="Describe what you see in this image."
)

print(response)
```

### Key Features

- **Multimodal Understanding**: Process and understand both text and images
- **Advanced Reasoning**: Powerful reasoning capabilities for complex tasks
- **Code Generation**: Strong code generation and analysis capabilities
- **Multiple Models**: Support for both Gemini Pro and Gemini Ultra
- **Streaming Responses**: Support for streaming responses for real-time interaction
- **Function Calling**: Support for function calling capabilities

## Integration with Other Components

The AI model integrations work seamlessly with other components of the TORONTO AI TEAM AGENT system:

### Integration with Project Management Features

The AI model integrations can enhance project management capabilities:

```python
from app.models.adapters.claude_adapter import ClaudeAdapter
from app.project_management.gantt_chart import GanttChartGenerator, Task, Dependency

# Use Claude to analyze project requirements
claude_adapter = ClaudeAdapter(api_key="your_api_key")
project_description = "Build a web application for inventory management with user authentication, product catalog, and reporting features."

analysis = claude_adapter.generate_response(
    prompt=f"Analyze the following project description and break it down into tasks with estimated durations (in days):\n\n{project_description}",
    max_tokens=1000
)

# Parse the analysis to extract tasks
# (This would require more sophisticated parsing in a real implementation)
tasks_data = [
    {"name": "Requirements Analysis", "duration": 5},
    {"name": "Database Design", "duration": 3},
    {"name": "User Authentication", "duration": 7},
    {"name": "Product Catalog", "duration": 10},
    {"name": "Reporting Features", "duration": 8},
    {"name": "Testing", "duration": 5},
    {"name": "Deployment", "duration": 2}
]

# Create tasks for Gantt chart
tasks = []
dependencies = []
start_date = "2025-05-01"
current_date = datetime.strptime(start_date, "%Y-%m-%d")

for i, task_data in enumerate(tasks_data):
    end_date = current_date + timedelta(days=task_data["duration"])
    
    task = Task(
        id=str(i+1),
        name=task_data["name"],
        start_date=current_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        progress=0
    )
    tasks.append(task)
    
    if i > 0:
        dependencies.append(Dependency(
            from_task_id=str(i),
            to_task_id=str(i+1)
        ))
    
    current_date = end_date

# Create Gantt chart
generator = GanttChartGenerator()
gantt = generator.create_gantt_chart(
    title="Inventory Management System",
    tasks=tasks,
    dependencies=dependencies
)
```

### Integration with Task Estimation Framework

The AI model integrations can improve task estimation accuracy:

```python
from app.models.adapters.gemini_adapter import GeminiAdapter
from app.orchestration.task_estimation import TaskEstimationFramework, TaskType, TaskComplexity

# Use Gemini to analyze task complexity
gemini_adapter = GeminiAdapter(api_key="your_api_key")
task_description = "Implement a secure authentication system with OAuth 2.0 and multi-factor authentication"

analysis = gemini_adapter.generate_response(
    prompt=f"Analyze the following task and rate its complexity on a scale of 1-5, where 1 is trivial and 5 is very complex. Also suggest what type of task it is (coding, research, documentation, etc.):\n\n{task_description}",
    max_tokens=500
)

# Parse the analysis to extract complexity and type
# (This would require more sophisticated parsing in a real implementation)
complexity = TaskComplexity.COMPLEX  # Assuming the analysis suggests complexity level 4
task_type = TaskType.CODING  # Assuming the analysis suggests it's a coding task

# Create and estimate task
estimation_framework = TaskEstimationFramework()
task = estimation_framework.create_task(
    title="Implement Authentication System",
    description=task_description,
    task_type=task_type,
    complexity=complexity,
    assigned_agent_id="developer1"
)

estimate = estimation_framework.estimate_task(
    task_id=task.id,
    agent_id="developer1"
)

print(f"Estimated duration: {estimate.estimated_duration} hours")
print(f"Confidence interval: {estimate.lower_bound} - {estimate.upper_bound} hours")
```

### Integration with Multimodal Services

The AI model integrations can work together with multimodal services:

```python
from app.models.adapters.claude_adapter import ClaudeAdapter
from app.multimodal.services.image_generation import ImageGenerationService, ImageGenerationModel
from app.multimodal.services.speech_processing import SpeechProcessingService, ElevenLabsVoice

# Create services
claude_adapter = ClaudeAdapter(api_key="your_claude_api_key")
image_service = ImageGenerationService()
speech_service = SpeechProcessingService()

# Generate content with Claude
content = claude_adapter.generate_response(
    prompt="Write a short story about a robot that learns to paint.",
    max_tokens=1000
)

# Generate an image based on the content
image_prompt = claude_adapter.generate_response(
    prompt=f"Based on the following story, create a detailed prompt for an image generation model to visualize the main scene:\n\n{content}",
    max_tokens=300
)

image = image_service.generate_image(
    prompt=image_prompt,
    model=ImageGenerationModel.DALLE_3,
    num_images=1
)[0]

# Generate speech narration of the content
speech = speech_service.synthesize_speech(
    text=content,
    voice=ElevenLabsVoice.EMILY
)

# Save the results
image.save("robot_painter.png")
speech.save("robot_painter_narration.mp3")
```

## Usage Examples

### Example 1: Complex Problem Solving with Claude

```python
from app.models.adapters.claude_adapter import ClaudeThinkAdapter

# Create a think adapter
think_adapter = ClaudeThinkAdapter(api_key="your_api_key")

# Define a complex problem
problem = """
A company is trying to optimize their delivery routes. They have 5 warehouses and 20 delivery locations.
Each warehouse has different inventory levels and each delivery location has different demand requirements.
The goal is to minimize the total distance traveled while ensuring all demands are met.
How would you approach this problem?
"""

# Generate a solution
solution = think_adapter.generate_response(
    prompt=problem,
    max_tokens=2000,
    temperature=0.5
)

print(solution)
```

### Example 2: Creating Visual Assets for a Project

```python
from app.multimodal.services.image_generation import ImageGenerationService, ImageGenerationModel, ImageSize

# Create a service
service = ImageGenerationService()

# Generate a logo
logo = service.generate_image(
    prompt="A minimalist logo for a tech company called 'Quantum Leap' that specializes in AI solutions. The logo should incorporate elements of technology and innovation.",
    model=ImageGenerationModel.DALLE_3,
    size=ImageSize.MEDIUM,
    num_images=3
)

# Generate UI mockups
mockups = service.generate_image(
    prompt="A modern, clean user interface for a dashboard showing analytics data with charts and graphs. The color scheme should be blue and white.",
    model=ImageGenerationModel.DALLE_3,
    size=ImageSize.LARGE,
    num_images=2
)

# Generate a diagram
diagram = service.generate_diagram(
    description="A system architecture diagram showing a web application with frontend, backend, database, and third-party API integrations.",
    diagram_type="architecture"
)

# Save the images
for i, img in enumerate(logo):
    img.save(f"logo_option_{i+1}.png")

for i, img in enumerate(mockups):
    img.save(f"dashboard_mockup_{i+1}.png")

diagram.save("system_architecture.png")
```

### Example 3: Creating Audio Content

```python
from app.multimodal.services.speech_processing import SpeechProcessingService, ElevenLabsVoice
from app.models.adapters.gemini_adapter import GeminiAdapter

# Create services
speech_service = SpeechProcessingService()
gemini_adapter = GeminiAdapter(api_key="your_api_key")

# Generate script content
script = gemini_adapter.generate_response(
    prompt="Write a 30-second introduction for a podcast about emerging technologies.",
    max_tokens=500
)

# Synthesize speech for different voices
voices = [ElevenLabsVoice.RACHEL, ElevenLabsVoice.ADAM]
audio_files = []

for i, voice in enumerate(voices):
    speech = speech_service.synthesize_speech(
        text=script,
        voice=voice
    )
    
    filename = f"podcast_intro_voice_{i+1}.mp3"
    speech.save(filename)
    audio_files.append(filename)

print(f"Generated audio files: {audio_files}")
```

### Example 4: Multimodal Analysis with Gemini

```python
from app.models.adapters.gemini_adapter import GeminiMultimodalAdapter
from PIL import Image
import requests
from io import BytesIO

# Create a multimodal adapter
multimodal_adapter = GeminiMultimodalAdapter(api_key="your_api_key")

# Load an image
image_url = "https://example.com/chart.png"
response = requests.get(image_url)
image = Image.open(BytesIO(response.content))

# Convert image to bytes
img_byte_arr = BytesIO()
image.save(img_byte_arr, format=image.format)
image_bytes = img_byte_arr.getvalue()

# Analyze the image
analysis = multimodal_adapter.analyze_image(
    image=image_bytes,
    prompt="Analyze this chart and provide insights about the data trends. What are the key takeaways?"
)

print(analysis)
```
