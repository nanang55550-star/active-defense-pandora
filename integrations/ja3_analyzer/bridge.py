"""
JA3 Analyzer Bridge - Koneksi ke JA3-Payload-Analyzer
Author: @nanang55550-star
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional

class JA3Bridge:
    """
    Jembatan ke repository JA3-Payload-Analyzer
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.analyzer_path = self.config.get('integrations', {})\
                                   .get('ja3_payload_analyzer', {})\
                                   .get('path', '../ja3-payload-analyzer')
        
        self.analyzer = None
        self._try_import_analyzer()
    
    def _try_import_analyzer(self):
        """Coba import analyzer dari path eksternal"""
        try:
            # Tambahkan path ke sys.path
            analyzer_path = Path(self.analyzer_path).absolute()
            if analyzer_path.exists():
                sys.path.insert(0, str(analyzer_path))
                
                from core.analyzer import PayloadAnalyzer
                self.analyzer = PayloadAnalyzer()
                print(f"[+] JA3-Payload-Analyzer loaded from {analyzer_path}")
            else:
                print(f"[-] Analyzer not found at {analyzer_path}")
        except Exception as e:
            print(f"[-] Failed to load analyzer: {e}")
    
    def analyze(self, ja3: str, payload: str) -> Dict:
        """
        Analisis menggunakan JA3-Payload-Analyzer
        
        Args:
            ja3: JA3 fingerprint
            payload: Request payload
            
        Returns:
            Dictionary hasil analisis
        """
        if self.analyzer:
            try:
                result = self.analyzer.analyze(payload, ja3)
                return {
                    'score': result.get('risk_score', 0),
                    'level': result.get('risk_level', 'LOW'),
                    'patterns': result.get('matched_patterns', []),
                    'source': 'ja3_payload_analyzer'
                }
            except Exception as e:
                return {
                    'score': 50,
                    'level': 'MEDIUM',
                    'error': str(e),
                    'source': 'fallback'
                }
        else:
            # Fallback sederhana
            return {
                'score': 50,
                'level': 'MEDIUM',
                'source': 'fallback'
            }
    
    def is_available(self) -> bool:
        """Cek apakah analyzer tersedia"""
        return self.analyzer is not None
