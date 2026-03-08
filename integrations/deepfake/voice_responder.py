"""
Deepfake Voice Responder - Balas penyerang dengan suara AI
Author: @nanang55550-star
"""

import random
import base64
from typing import Optional
from pathlib import Path

class DeepfakeVoice:
    """
    Menghasilkan respons suara untuk penyerang
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.enabled = self.config.get('deepfake', {}).get('enabled', True)
        self.voice_type = self.config.get('deepfake', {}).get('voice_type', 'gtts')
        self.api_key = self.config.get('deepfake', {}).get('api_key', '')
        
        self.messages = self.config.get('deepfake', {}).get('messages', [
            "Nice try, Nanang is watching you.",
            "You just stepped into the wrong territory.",
            "Your IP has been logged and broadcasted.",
            "Project Pandora sends its regards.",
            "The Architect knows you're here.",
            "Your attack has been neutralized.",
            "We've poisoned your response. Good luck.",
            "This is not a game. You've been countered.",
            "Pandora's box is now open. For you.",
            "Your tools are useless here."
        ])
    
    def generate_audio(self, text: str) -> Optional[bytes]:
        """
        Generate audio dari text
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio bytes or None
        """
        if not self.enabled:
            return None
        
        try:
            if self.voice_type == 'gtts':
                from gtts import gTTS
                import io
                
                tts = gTTS(text=text, lang='en')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                return audio_bytes.getvalue()
                
            elif self.voice_type == 'pyttsx3':
                import pyttsx3
                import io
                
                engine = pyttsx3.init()
                engine.save_to_file(text, 'temp_audio.wav')
                engine.runAndWait()
                
                with open('temp_audio.wav', 'rb') as f:
                    return f.read()
                    
            else:
                # Simulasi audio untuk testing
                return base64.b64encode(text.encode())
                
        except Exception as e:
            print(f"Voice generation error: {e}")
            return None
    
    def say(self, message: Optional[str] = None) -> Dict:
        """
        "Ucapkan" pesan ke penyerang
        
        Args:
            message: Custom message
            
        Returns:
            Response dict
        """
        if not self.enabled:
            return {'status': 'disabled'}
        
        if not message:
            message = random.choice(self.messages)
        
        audio = self.generate_audio(message)
        
        return {
            'text': message,
            'audio_available': audio is not None,
            'audio_base64': base64.b64encode(audio).decode()[:50] + "..." if audio else None
        }
    
    def say_random(self) -> Dict:
        """Ucapkan pesan random"""
        return self.say()
    
    def add_custom_message(self, message: str):
        """Tambah pesan kustom"""
        self.messages.append(message)
