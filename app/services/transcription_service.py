"""
Transcription service client for calling a remote Whisper API server.
Compatible with the /transcribe_audio endpoint that accepts multipart/form-data.

Note: This version acts as an API client rather than running models locally.
Device-specific code (CUDA/MPS/CPU) has been removed as processing happens on the server.
The API response format {"transcript": "..."} is automatically converted to {"text": "..."}
for backward compatibility with the original interface.
"""
import os
import io
import subprocess
import tempfile
from typing import Optional, Dict, Any
import requests


class TranscriptionService:
    """Client for transcribing audio via API server."""
    
    def __init__(self, api_url: str = "http://localhost:8001/transcribe_audio", timeout: int = 30):
        """
        Initialize the transcription service client.
        
        Args:
            api_url: URL of the transcription API endpoint
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.timeout = timeout
        print(f"TranscriptionService initialized with API: {self.api_url}")
        
    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file by sending it to the API server.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dict with 'text' key containing the transcription
            
        Raises:
            FileNotFoundError: If audio_path does not exist
            Exception: If API request fails or response is invalid
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        try:
            with open(audio_path, 'rb') as f:
                files = {'audio_file': f}
                response = requests.post(
                    self.api_url,
                    files=files,
                    headers={"Accept": "application/json"},
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                print(f"Transcription API response: {data}")
                
                if "error" in data:
                    raise Exception(f"Transcription API error: {data['error']}")
                
                # Map API response {"transcript": "..."} to expected {"text": "..."}
                transcript = data.get("transcript")
                if transcript is None:
                    raise KeyError("Response missing 'transcript' field")
                    
                return {"text": transcript}
        except requests.exceptions.Timeout as e:
            print(f"Transcription timeout: {str(e)}")
            raise Exception(f"Transcription API request timed out after {self.timeout}s: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            print(f"Transcription connection error: {str(e)}")
            raise Exception(f"Could not connect to transcription API at {self.api_url}: {str(e)}")
        except requests.exceptions.HTTPError as e:
            print(f"Transcription HTTP error: {str(e)}")
            raise Exception(f"Transcription API returned HTTP error: {str(e)}")
        except (KeyError, ValueError) as e:
            print(f"Transcription response error: {str(e)}")
            raise Exception(f"Invalid API response format: {str(e)}")
    
    def _convert_to_wav(self, audio_bytes: bytes, source_format: str) -> bytes:
        """Convert audio to WAV format using ffmpeg."""
        with tempfile.NamedTemporaryFile(suffix=f'.{source_format}', delete=False) as input_file:
            input_file.write(audio_bytes)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            subprocess.run([
                'ffmpeg', '-i', input_path, '-ar', '16000', '-ac', '1', '-y', output_path
            ], check=True, capture_output=True)
            
            with open(output_path, 'rb') as f:
                return f.read()
        finally:
            os.unlink(input_path)
            os.unlink(output_path)
    
    def transcribe_bytes(self, audio_bytes: bytes, audio_format: str = "webm") -> Dict[str, Any]:
        """
        Transcribe audio from bytes by sending it to the API server.
        
        Args:
            audio_bytes: Audio file content as bytes
            audio_format: Audio format (webm, wav, mp3, etc.)
            
        Returns:
            Dict with 'transcript' key containing the transcription
            
        Raises:
            Exception: If API request fails or response is invalid
        """
        try:
            print(f"Original audio format: {audio_format}, size: {len(audio_bytes)} bytes")
            
            # Convert webm to wav for better compatibility with librosa
            if audio_format == "webm":
                print("Converting webm to wav...")
                audio_bytes = self._convert_to_wav(audio_bytes, audio_format)
                audio_format = "wav"
                print(f"Converted to wav, size: {len(audio_bytes)} bytes")
            
            audio_file = io.BytesIO(audio_bytes)
            filename = f"audio.{audio_format}"
            files = {'audio_file': (filename, audio_file, f'audio/{audio_format}')}
            
            print(f"Sending transcription request to {self.api_url}")
            response = requests.post(
                self.api_url,
                files=files,
                headers={"Accept": "application/json"},
                timeout=self.timeout
            )
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            print(f"Response content: {response.text[:500]}")
            data = response.json()
            print(f"Transcription API response: {data}")
            
            if "error" in data:
                raise Exception(f"Transcription API error: {data['error']}")
            
            transcript = data.get("transcript")
            if transcript is None:
                raise KeyError(f"Response missing 'transcript' field. Got: {data}")
                
            return {"transcript": transcript}
        except requests.exceptions.Timeout as e:
            print(f"Transcription timeout: {str(e)}")
            raise Exception(f"Transcription API request timed out after {self.timeout}s: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            print(f"Transcription connection error: {str(e)}")
            raise Exception(f"Could not connect to transcription API at {self.api_url}: {str(e)}")
        except requests.exceptions.HTTPError as e:
            print(f"Transcription HTTP error: {str(e)}")
            raise Exception(f"Transcription API returned HTTP error: {str(e)}")
        except (KeyError, ValueError) as e:
            print(f"Transcription response error: {str(e)}")
            raise Exception(f"Invalid API response format: {str(e)}")
        except subprocess.CalledProcessError as e:
            print(f"Audio conversion error: {e.stderr.decode() if e.stderr else str(e)}")
            raise Exception(f"Failed to convert audio format: {str(e)}")
        finally:
            if 'audio_file' in locals():
                audio_file.close()
    
    def detect_language(self, audio_path: str) -> Optional[str]:
        """
        Detect the language from audio.
        
        Note: This method is not implemented for the API client.
        It would require a separate API endpoint for language detection.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            None
        """
        print("Warning: Language detection not implemented for API client")
        return None


# Singleton instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get or create the singleton transcription service client instance."""
    global _transcription_service
    if _transcription_service is None:
        api_url = os.getenv("WHISPER_API_URL", "http://localhost:8001/transcribe_audio")
        timeout_str = os.getenv("WHISPER_API_TIMEOUT", "30")
        try:
            timeout = int(timeout_str)
        except ValueError:
            print(f"Warning: Invalid WHISPER_API_TIMEOUT '{timeout_str}', using default 30")
            timeout = 30
            
        _transcription_service = TranscriptionService(api_url=api_url, timeout=timeout)
    return _transcription_service