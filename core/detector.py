"""
Anomaly Detector Module - Mendeteksi ancaman berdasarkan JA3 dan payload
Author: @nanang55550-star
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class AnomalyDetector:
    """
    Mendeteksi anomali dengan menganalisis JA3 fingerprint dan payload
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.thresholds = self.config.get('threat_levels', {
            'low': 0,
            'medium': 30,
            'high': 60,
            'critical': 80
        })
        
        # Load patterns
        self.ja3_blacklist = self.config.get('detection', {}).get('ja3_blacklist', [
            'b32309a26951912be7dba376398abc3b',  # Python requests
            '3039129e12019446d0a777651a376512',  # curl
            'f5973d463d12d46e38abc36713840612',  # Go HTTP
            '132b490d1d2938164b391786576d1209',  # Burp Suite
        ])
        
        self.payload_patterns = self._load_payload_patterns()
        
    def _load_payload_patterns(self) -> Dict[str, List[str]]:
        """Load pattern dari file signatures"""
        patterns = {
            'cobol': [
                r'IDENTIFICATION\s+DIVISION',
                r'DATA\s+DIVISION',
                r'PROCEDURE\s+DIVISION',
                r'PROGRAM-ID',
                r'WORKING-STORAGE',
                r'PIC\s+9\([0-9]+\)',
                r'PIC\s+X\([0-9]+\)',
                r'MOVE\s+SPACES\s+TO',
                r'DISPLAY\s+"[^"]*"'
            ],
            'sql': [
                r'SELECT.*FROM',
                r'INSERT.*INTO',
                r'UPDATE.*SET',
                r'DELETE.*FROM',
                r'DROP\s+TABLE',
                r'UNION.*SELECT',
                r'OR\s+1=1',
                r'OR\s+\'1\'=\'1\'',
                r'WAITFOR\s+DELAY',
                r'BENCHMARK\s*\(',
                r'SLEEP\s*\(',
                r'EXEC\s+xp_cmdshell'
            ],
            'legacy': [
                r'IBM-Z15',
                r'IBM-Z14',
                r'MAINFRAME',
                r'VT100',
                r'VT220',
                r'3270',
                r'5250',
                r'AS400',
                r'CICS',
                r'IMS',
                r'DB2',
                r'VSAM',
                r'JCL',
                r'PROC'
            ]
        }
        
        # Override dari config jika ada
        config_patterns = self.config.get('detection', {}).get('payload_patterns', {})
        for category, enabled in config_patterns.items():
            if not enabled and category in patterns:
                patterns[category] = []
        
        return patterns
    
    def calculate_threat_score(self, ja3: str, payload: str, ip: str = None) -> int:
        """
        Hitung threat score berdasarkan berbagai faktor
        
        Args:
            ja3: JA3 fingerprint
            payload: Request payload
            ip: Source IP address (opsional)
            
        Returns:
            Threat score (0-100)
        """
        score = 0
        
        # 1. JA3 Blacklist Check (30 points)
        if ja3 in self.ja3_blacklist:
            score += 30
        
        # 2. Payload Pattern Check (40 points max)
        payload_score = self._check_payload_patterns(payload)
        score += min(payload_score, 40)
        
        # 3. JA3-Payload Consistency Check (30 points)
        consistency_score = self._check_ja3_payload_consistency(ja3, payload)
        score += consistency_score
        
        # 4. IP Reputation Check (bonus)
        if ip and self._is_suspicious_ip(ip):
            score += 10
        
        return min(score, 100)  # Max 100
    
    def _check_payload_patterns(self, payload: str) -> int:
        """Cek payload terhadap pattern database"""
        score = 0
        matches = []
        
        for category, patterns in self.payload_patterns.items():
            for pattern in patterns:
                if re.search(pattern, payload, re.IGNORECASE):
                    matches.append((category, pattern))
                    
                    # Bobot score per kategori
                    if category == 'sql':
                        score += 15
                    elif category == 'cobol':
                        score += 10
                    elif category == 'legacy':
                        score += 5
        
        return min(score, 40)  # Max 40 dari payload
    
    def _check_ja3_payload_consistency(self, ja3: str, payload: str) -> int:
        """
        Cek konsistensi antara JA3 dan payload
        Contoh: JA3 browser normal tapi payload COBOL = anomali
        """
        score = 0
        
        # Identifikasi tipe JA3
        is_browser = ja3 in [
            'cd08e31494f13d058c4f4a31675465b2',  # Chrome
            '451996847a976f62660143896dfa2845',  # Firefox
            '89596695273f5569420061917f8582d1'   # Safari
        ]
        
        is_tool = ja3 in self.ja3_blacklist
        
        # Cek apakah payload mengandung pattern tertentu
        has_cobol = any(re.search(p, payload, re.IGNORECASE) 
                       for p in self.payload_patterns.get('cobol', []))
        has_sql = any(re.search(p, payload, re.IGNORECASE) 
                     for p in self.payload_patterns.get('sql', []))
        
        # Inconsistency detection
        if is_browser and (has_cobol or has_sql):
            score += 30  # Browser ngirim COBOL/SQL = suspicious
        elif is_tool and not (has_cobol or has_sql):
            score += 10  # Tool ngirim request normal = sedikit suspicious
        elif not is_browser and not is_tool and has_cobol:
            score += 20  # Unknown JA3 + COBOL = suspicious
        
        return score
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Cek reputasi IP (simplified)"""
        # TODO: Integrasi dengan threat intelligence feed
        suspicious_ranges = [
            '10.', '172.16.', '192.168.'  # Internal IPs
        ]
        
        for prefix in suspicious_ranges:
            if ip.startswith(prefix):
                return True
        
        return False
    
    def get_threat_level(self, score: int) -> str:
        """Konversi score ke threat level"""
        if score >= self.thresholds.get('critical', 80):
            return 'CRITICAL'
        elif score >= self.thresholds.get('high', 60):
            return 'HIGH'
        elif score >= self.thresholds.get('medium', 30):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def add_custom_pattern(self, category: str, pattern: str):
        """Tambah pattern kustom"""
        if category in self.payload_patterns:
            self.payload_patterns[category].append(pattern)
        else:
            self.payload_patterns[category] = [pattern]
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik detector"""
        return {
            'ja3_blacklist_count': len(self.ja3_blacklist),
            'payload_patterns': {
                k: len(v) for k, v in self.payload_patterns.items()
            }
      }
