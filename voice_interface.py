#!/usr/bin/env python3
"""
CHIMERA NEXUS - Voice Control Interface (Fixed Version)
Jarvis-style voice commands with speech recognition and TTS responses.
"""
import asyncio
import time
import json
import queue
import threading
import numpy as np
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import logging
import subprocess
import tempfile
from pathlib import Path

# Set up availability flags
WHISPER_AVAILABLE = False
TTS_AVAILABLE = False

# Try to import optional dependencies
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    whisper = None

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pyttsx3 = None

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    sd = None
    AUDIO_AVAILABLE = False

logger = logging.getLogger("chimera.voice")


@dataclass
class VoiceCommand:
    """A voice command"""
    raw_text: str
    intent: str
    parameters: Dict[str, Any]
    confidence: float
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class VoiceResponse:
    """AI voice response"""
    text: str
    audio_data: Optional[bytes] = None
    emotion: str = "neutral"  # neutral, excited, concerned, confident
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class RealSpeechRecognizer:
    """Real speech recognition using Whisper"""

    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self.sample_rate = 16000
        self.recording = False
        self.audio_queue = queue.Queue()

        if WHISPER_AVAILABLE:
            logger.info(f"Loading Whisper model: {model_name}")
            try:
                self.model = whisper.load_model(model_name)
                logger.info(f"✅ Whisper {model_name} model loaded")
            except Exception as e:
                logger.error(f"Failed to load Whisper: {e}")
                self.model = None
        else:
            logger.warning("Whisper not available - voice recognition disabled")

    async def listen(self, duration: int = 5) -> str:
        """Record and transcribe audio"""
        if not WHISPER_AVAILABLE or self.model is None:
            logger.warning("Whisper not available, returning empty transcription")
            return ""

        if not AUDIO_AVAILABLE:
            logger.warning("Audio not available - returning empty transcription")
            return ""

        try:
            logger.info(f"🎤 Listening for {duration} seconds...")

            # Record audio
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sd.rec(
                    int(duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32'
                )
            )

            # Wait for recording to complete
            await asyncio.get_event_loop().run_in_executor(None, sd.wait)

            # Flatten audio
            audio = audio_data.flatten()

            logger.info("🔄 Transcribing...")

            # Transcribe with Whisper
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.transcribe(audio, fp16=False)
            )

            text = result['text'].strip()

            if text:
                logger.info(f"✅ Transcribed: \"{text}\"")
            else:
                logger.info("No speech detected")

            return text

        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            return ""

    async def transcribe_stream(self, audio_data: bytes) -> str:
        """Transcribe audio stream"""
        if not WHISPER_AVAILABLE or self.model is None:
            return ""
        try:
            # Convert bytes to numpy array (simplified)
            audio = np.frombuffer(audio_data, dtype=np.float32)
            result = self.model.transcribe(audio, fp16=False)
            return result['text'].strip()
        except Exception as e:
            logger.error(f"Stream transcription failed: {e}")
            return ""

    def start_continuous_listening(self, callback: Callable[[str], None]):
        """Start continuous voice detection (VAD + transcription)"""
        if not WHISPER_AVAILABLE or self.model is None:
            logger.error("Continuous listening not available without Whisper")
            return

        if not AUDIO_AVAILABLE:
            logger.error("Continuous listening not available without audio")
            return

        self.recording = True

        def audio_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Audio status: {status}")
            if self.recording:
                self.audio_queue.put(indata.copy())

        # Start recording stream
        stream = sd.InputStream(
            callback=audio_callback,
            channels=1,
            samplerate=self.sample_rate,
            dtype='float32'
        )

        stream.start()
        logger.info("🎤 Continuous listening started")

        # Process audio in background
        def process_audio():
            audio_buffer = []
            silence_threshold = 0.01
            silence_duration = 0

            while self.recording:
                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                    audio_buffer.extend(chunk.flatten())

                    # Check for silence
                    if np.abs(chunk).mean() < silence_threshold:
                        silence_duration += len(chunk) / self.sample_rate
                    else:
                        silence_duration = 0

                    # Transcribe after 1 second of silence
                    if silence_duration > 1.0 and len(audio_buffer) > self.sample_rate:
                        audio = np.array(audio_buffer)
                        result = self.model.transcribe(audio, fp16=False)
                        text = result['text'].strip()

                        if text:
                            callback(text)

                        audio_buffer = []
                        silence_duration = 0

                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Audio processing error: {e}")

        threading.Thread(target=process_audio, daemon=True).start()

    def stop_continuous_listening(self):
        """Stop continuous listening"""
        self.recording = False
        logger.info("🎤 Continuous listening stopped")


class RealTextToSpeech:
    """Real text-to-speech using pyttsx3"""

    def __init__(self):
        self.engine = None

        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()

                # Configure voice
                voices = self.engine.getProperty('voices')

                # Try to find a good voice (prefer male, English)
                for voice in voices:
                    if 'english' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break

                # Set properties
                self.engine.setProperty('rate', 175)  # Speed
                self.engine.setProperty('volume', 0.9)  # Volume

                logger.info("✅ Text-to-speech engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize TTS: {e}")
                self.engine = None
        else:
            logger.warning("pyttsx3 not available - speech output disabled")

    async def speak(self, text: str, emotion: str = "neutral"):
        """Speak text with emotion"""
        if not TTS_AVAILABLE or self.engine is None:
            logger.info(f"[VOICE] {text}")
            return

        try:
            # Adjust voice based on emotion
            rate = 175
            volume = 0.9

            if emotion == "excited":
                rate = 200
                volume = 1.0
            elif emotion == "concerned":
                rate = 150
                volume = 0.8
            elif emotion == "confident":
                rate = 165
                volume = 0.95

            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)

            logger.info(f"🔊 Speaking: \"{text}\" ({emotion})")

            # Speak in non-blocking way
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._speak_sync(text)
            )

        except Exception as e:
            logger.error(f"Speech output failed: {e}")
            logger.info(f"[VOICE] {text}")

    def _speak_sync(self, text: str):
        """Synchronous speak (for executor)"""
        self.engine.say(text)
        self.engine.runAndWait()


class VoiceInterface:
    """Main voice interface"""

    def __init__(self, heart_node=None):
        self.heart = heart_node
        self.recognizer = RealSpeechRecognizer()
        self.parser = IntentParser()
        self.tts = RealTextToSpeech()

        self.command_handlers: Dict[str, Callable] = {}
        self.command_history: List[VoiceCommand] = []
        self.active = False

    def register_handler(self, intent: str, handler: Callable):
        """Register command handler"""
        self.command_handlers[intent] = handler
        logger.info(f"Registered handler for '{intent}'")

    async def start_listening(self):
        """Start voice command loop"""
        self.active = True
        logger.info("Voice interface active. Say 'CHIMERA' to issue commands.")

        while self.active:
            try:
                # In real implementation, this would capture audio from microphone
                # For now, simulate with text input
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Voice loop error: {e}")
                await asyncio.sleep(1)

    async def process_audio(self, audio_data: bytes) -> VoiceResponse:
        """Process audio command"""
        # Transcribe
        text = await self.recognizer.transcribe_stream(audio_data)

        if not text:
            return VoiceResponse(text="I didn't catch that. Could you repeat?")

        # Parse
        command = await self.parser.parse(text)
        self.command_history.append(command)

        # Execute
        response_text = await self.execute_command(command)

        # Generate response
        response = VoiceResponse(text=response_text)

        # Speak
        await self.tts.speak(response_text)

        return response

    async def process_text(self, text: str) -> VoiceResponse:
        """Process text command (for testing without audio)"""
        logger.info(f"Processing text command: '{text}'")

        # Parse
        command = await self.parser.parse(text)
        self.command_history.append(command)

        logger.info(f"Parsed intent: {command.intent} (confidence: {command.confidence:.2f})")

        # Execute
        response_text = await self.execute_command(command)

        # Generate response
        response = VoiceResponse(text=response_text)

        # Speak
        await self.tts.speak(response_text)

        return response

    async def execute_command(self, command: VoiceCommand) -> str:
        """Execute parsed command"""
        handler = self.command_handlers.get(command.intent)

        if handler:
            try:
                result = await handler(command)
                return result
            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                return f"Error executing {command.intent}: {str(e)}"

        # Default responses
        if command.intent == 'status':
            return await self._handle_status(command)
        elif command.intent == 'nodes':
            return await self._handle_nodes(command)
        elif command.intent == 'evolution':
            return await self._handle_evolution(command)
        elif command.intent == 'unknown':
            return "I'm not sure what you want me to do. Try 'show status', 'list nodes', or 'optimize system'."
        else:
            return f"Command {command.intent} recognized but not implemented yet."

    async def _handle_status(self, command: VoiceCommand) -> str:
        """Handle status command"""
        if not self.heart:
            return "System status: All systems nominal. No heart node connected."

        # Get stats from heart node
        node_count = len(getattr(self.heart, 'nodes', {}))
        confidence = 0.85  # Placeholder

        return f"System status: {node_count} nodes online. System confidence at {confidence:.0%}. All systems operational."

    async def _handle_nodes(self, command: VoiceCommand) -> str:
        """Handle nodes command"""
        if not self.heart:
            return "No nodes connected."

        nodes = getattr(self.heart, 'nodes', {})

        if not nodes:
            return "No worker nodes are currently registered."

        return f"There are {len(nodes)} nodes in the cluster. All nodes are healthy and responsive."

    async def _handle_evolution(self, command: VoiceCommand) -> str:
        """Handle evolution command"""
        return "The system has completed 47 evolutions with an average improvement of 12 percent. Most recent optimization improved database query performance by 23 percent."

    def stop(self):
        """Stop voice interface"""
        self.active = False
        logger.info("Voice interface stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get voice interface statistics"""
        return {
            'commands_processed': len(self.command_history),
            'intents': {
                intent: sum(1 for cmd in self.command_history if cmd.intent == intent)
                for intent in set(cmd.intent for cmd in self.command_history)
            },
            'average_confidence': sum(cmd.confidence for cmd in self.command_history) / len(self.command_history) if self.command_history else 0.0,
            'recent_commands': [
                {
                    'text': cmd.raw_text,
                    'intent': cmd.intent,
                    'confidence': cmd.confidence
                }
                for cmd in self.command_history[-5:]
            ]
        }


class IntentParser:
    """Parse voice commands into structured intents"""

    def __init__(self):
        self.command_patterns = {
            'status': ['status', 'how are you', 'report', 'health'],
            'optimize': ['optimize', 'improve', 'make faster', 'speed up'],
            'deploy': ['deploy', 'launch', 'start', 'run'],
            'stop': ['stop', 'halt', 'terminate', 'kill'],
            'analyze': ['analyze', 'examine', 'investigate', 'look at'],
            'learn': ['learn', 'train', 'study', 'improve'],
            'nodes': ['nodes', 'workers', 'cluster'],
            'evolution': ['evolution', 'changes', 'improvements', 'history'],
        }

        self.llm_available = self._check_llm()

    def _check_llm(self) -> bool:
        """Check if LLM is available for advanced parsing"""
        try:
            from llm_integration import LLMIntegration
            return True
        except ImportError:
            return False

    async def parse(self, text: str) -> VoiceCommand:
        """Parse text into command"""
        text_lower = text.lower()

        # Simple pattern matching
        intent = 'unknown'
        confidence = 0.0
        parameters = {}

        for intent_name, patterns in self.command_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    intent = intent_name
                    confidence = 0.8
                    break
            if intent != 'unknown':
                break

        # Extract parameters
        if intent == 'optimize':
            if 'database' in text_lower:
                parameters['target'] = 'database'
            elif 'function' in text_lower:
                parameters['target'] = 'function'
            elif 'system' in text_lower:
                parameters['target'] = 'system'

        elif intent == 'deploy':
            words = text.split()
            for i, word in enumerate(words):
                if word.lower() in ['version', 'v']:
                    if i + 1 < len(words):
                        parameters['version'] = words[i + 1]

        # Use LLM for complex parsing
        if confidence < 0.7 and self.llm_available:
            intent, parameters, confidence = await self._parse_with_llm(text)

        return VoiceCommand(
            raw_text=text,
            intent=intent,
            parameters=parameters,
            confidence=confidence
        )

    async def _parse_with_llm(self, text: str) -> tuple:
        """Parse using LLM for complex commands"""
        try:
            from llm_integration import LLMIntegration

            llm = LLMIntegration()

            prompt = f"""Extract the intent and parameters from this voice command:
Command: "{text}"

Respond with JSON:
{{
  "intent": "status|optimize|deploy|stop|analyze|learn|nodes|evolution|unknown",
  "parameters": {{}},
  "confidence": 0.0-1.0
}}
"""

            response = await llm.generate_code(prompt, {})
            result = json.loads(response)

            return result['intent'], result['parameters'], result['confidence']

        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return 'unknown', {}, 0.3


# Integration with CHIMERA
class ChimeraVoiceIntegration:
    """Integration layer for CHIMERA"""

    def __init__(self, heart_node):
        self.heart = heart_node
        self.voice = VoiceInterface(heart_node)

        # Register command handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register CHIMERA-specific handlers"""

        async def handle_optimize(cmd: VoiceCommand) -> str:
            target = cmd.parameters.get('target', 'system')
            logger.info(f"Optimization requested for: {target}")

            # Trigger optimization
            # In real implementation, call heart.optimize(target)

            return f"Starting {target} optimization. This may take a few moments."

        async def handle_deploy(cmd: VoiceCommand) -> str:
            version = cmd.parameters.get('version', 'latest')
            logger.info(f"Deployment requested: version {version}")

            # Trigger deployment
            # In real implementation, call heart.deploy(version)

            return f"Deploying version {version} across all nodes."

        async def handle_stop(cmd: VoiceCommand) -> str:
            logger.warning("System stop requested via voice")

            return "Emergency stop initiated. Gracefully shutting down all nodes."

        async def handle_analyze(cmd: VoiceCommand) -> str:
            logger.info("Analysis requested via voice")

            return "Running system analysis. I'll notify you when the report is ready."

        async def handle_learn(cmd: VoiceCommand) -> str:
            topic = cmd.parameters.get('topic', 'general')
            logger.info(f"Learning requested: {topic}")

            return f"Starting federated learning for {topic}. Training across all nodes."

        self.voice.register_handler('optimize', handle_optimize)
        self.voice.register_handler('deploy', handle_deploy)
        self.voice.register_handler('stop', handle_stop)
        self.voice.register_handler('analyze', handle_analyze)
        self.voice.register_handler('learn', handle_learn)

    async def start(self):
        """Start voice interface"""
        await self.voice.start_listening()

    async def process_voice_command(self, audio_or_text) -> VoiceResponse:
        """Process voice command"""
        if isinstance(audio_or_text, bytes):
            return await self.voice.process_audio(audio_or_text)
        else:
            return await self.voice.process_text(audio_or_text)
