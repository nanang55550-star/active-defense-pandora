#!/usr/bin/env python3
"""
Attack Simulation - Contoh untuk testing sistem Pandora
Author: @nanang55550-star
Version: 1.0.0

File ini berisi simulasi berbagai tipe serangan untuk menguji
Active Defense Pandora system. Bisa digunakan untuk stress test
dan validasi deteksi.
"""

import time
import random
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ========================================
# DATABASE SERANGAN
# ========================================

# Daftar JA3 fingerprint untuk simulasi
JA3_FINGERPRINTS = {
    # Browser normal (harusnya LOW risk)
    'chrome': 'cd08e31494f13d058c4f4a31675465b2',
    'firefox': '451996847a976f62660143896dfa2845',
    'safari': '89596695273f5569420061917f8582d1',
    'edge': '2b9e8b5e8c5e4c5a8b7e6f5d4c3b2a1f',
    
    # Tools pentest (MEDIUM/HIGH risk)
    'python': 'b32309a26951912be7dba376398abc3b',
    'curl': '3039129e12019446d0a777651a376512',
    'go': 'f5973d463d12d46e38abc36713840612',
    'java': '4637b4269d123d46e29abc3671239012',
    
    # Attacker tools (CRITICAL risk)
    'burp': '132b490d1d2938164b391786576d1209',
    'sqlmap': 'a1b2c3d4e5f67890123456789abcdef0',
    'nmap': '0987654321fedcba9876543210fedcba',
    'metasploit': 'abcdef1234567890abcdef1234567890',
}

# Daftar payload untuk simulasi
PAYLOADS = {
    # Normal requests
    'normal': "GET /index.html HTTP/1.1\nHost: example.com\nUser-Agent: Mozilla/5.0",
    'api': "GET /api/v1/users HTTP/1.1\nAuthorization: Bearer token123",
    
    # COBOL attacks
    'cobol_basic': """
        IDENTIFICATION DIVISION.
        PROGRAM-ID. ATTACK.
        DATA DIVISION.
        WORKING-STORAGE SECTION.
        01 WS-DATA PIC X(100).
        PROCEDURE DIVISION.
            DISPLAY "HACKING MAINFRAME".
    """,
    'cobol_advanced': """
        IDENTIFICATION DIVISION.
        PROGRAM-ID. INJECT.
        ENVIRONMENT DIVISION.
        DATA DIVISION.
        WORKING-STORAGE SECTION.
        01 WS-USERID PIC 9(10).
        01 WS-PASSWD PIC X(20).
        PROCEDURE DIVISION.
            MOVE 999999 TO WS-USERID
            MOVE "hacked" TO WS-PASSWD
            DISPLAY "ACCESS GRANTED".
    """,
    'cobol_file': """
        IDENTIFICATION DIVISION.
        PROGRAM-ID. FILE-HACK.
        ENVIRONMENT DIVISION.
        INPUT-OUTPUT SECTION.
        FILE-CONTROL.
            SELECT FILE-ASSIGN TO "passwords.txt".
        PROCEDURE DIVISION.
            OPEN INPUT FILE.
            READ FILE.
            DISPLAY "DATA EXPORTED".
    """,
    
    # SQL injections
    'sql_basic': "SELECT * FROM users WHERE username = 'admin' OR 1=1--",
    'sql_union': "SELECT username, password FROM users UNION SELECT 'admin', 'hacked'--",
    'sql_drop': "'; DROP TABLE users; --",
    'sql_error': "SELECT * FROM users WHERE id = 1 AND 1=CONVERT(int, @@version)--",
    'sql_time': "SELECT * FROM users WHERE id = 1; WAITFOR DELAY '0:0:5'--",
    'sql_xp': "EXEC xp_cmdshell 'whoami'--",
    
    # Legacy/mainframe
    'legacy_ibm': "IBM-Z15 MAINFRAME TRANSACTION ID: 12345",
    'legacy_cics': "CICS TRANSACTION: PAYMENT AMOUNT: 10000",
    'legacy_ims': "IMS DATABASE QUERY: GET UNIQUE WHERE ACCT=12345",
    'legacy_jcl': "//JOBNAME JOB (ACCT),'HACKER',CLASS=A",
    
    # Mixed attacks
    'cobol_sql': """
        IDENTIFICATION DIVISION.
        PROGRAM-ID. SQL-INJECT.
        PROCEDURE DIVISION.
            EXEC SQL
                SELECT * FROM accounts
                WHERE username = 'admin' OR 1=1
            END-EXEC.
    """,
    'legacy_sql': """
        CICS TRANSACTION
        EXEC SQL
            DELETE FROM users
            WHERE userid = 'admin'
        END-EXEC
    """,
    
    # Malicious payloads
    'malicious_php': "<?php system($_GET['cmd']); ?>",
    'malicious_js': "<script>alert('XSS')</script>",
    'malicious_cmd': "| cat /etc/passwd; id; whoami",
    'malicious_path': "../../../etc/passwd",
    
    # Encoded attacks
    'base64_sql': "U0VMRUNUICogRlJPTSB1c2VycyBXSEVSRSB1c2VybmFtZSA9ICdhZG1pbicgT1IgMT0xLS0=",
    'hex_sql': "53454c454354202a2046524f4d20757365727320574845524520757365726e616d65203d202761646d696e27204f5220313d312d2d",
    
    # CoAP IoT attacks
    'coap_get': "CON GET coap://[::1]/.well-known/core",
    'coap_post': "CON POST coap://[::1]/light (payload: \"on\")",
    
    # MQTT attacks
    'mqtt_connect': "CONNECT MQTT clientId=attacker",
    'mqtt_publish': "PUBLISH topic/+/status payload=\"hacked\"",
}

# Daftar IP untuk simulasi
IP_RANGES = {
    'internal': [
        '10.0.0.1', '10.0.0.2', '10.0.0.5', '10.0.0.10', '10.0.0.50',
        '172.16.0.1', '172.16.0.10', '172.16.0.100',
        '192.168.1.1', '192.168.1.10', '192.168.1.50', '192.168.1.100',
    ],
    'external': [
        '45.33.22.11', '103.56.78.90', '185.130.5.133', '202.51.70.15',
        '1.2.3.4', '5.6.7.8', '9.10.11.12', '13.14.15.16',
        '100.64.0.1', '172.16.0.1', '192.0.2.1',
    ],
    'tor': [
        '185.220.101.1', '185.220.101.2', '185.220.101.3',
        '199.249.230.1', '199.249.230.2',
    ],
    'vpn': [
        '103.28.53.1', '103.28.53.2', '45.32.67.1', '45.32.67.2',
    ],
}


class AttackSimulator:
    """
    Simulasi berbagai tipe serangan untuk testing Pandora system
    
    Fitur:
    - Simulasi berbagai tipe JA3 fingerprint
    - Beragam payload serangan
    - IP dari berbagai kategori
    - Reporting otomatis
    - Stress test capabilities
    """
    
    def __init__(self, target_url: str = "http://localhost:8080"):
        """
        Inisialisasi attack simulator
        
        Args:
            target_url: URL dari Pandora API endpoint
        """
        self.target = target_url.rstrip('/')
        self.results: List[Dict] = []
        self.session = requests.Session()
        
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║     PANDORA ATTACK SIMULATOR v1.0                          ║
║     Target: {self.target}                                       
╚═══════════════════════════════════════════════════════════╝
        """)
    
    def simulate_attack(self, ja3_type: str, payload_type: str, 
                        ip: Optional[str] = None, verbose: bool = True) -> Optional[Dict]:
        """
        Simulasi satu serangan
        
        Args:
            ja3_type: Tipe JA3 (chrome, firefox, python, dll)
            payload_type: Tipe payload (normal, cobol, sql, dll)
            ip: IP address (random jika None)
            verbose: Tampilkan output detail
            
        Returns:
            Dictionary hasil serangan atau None jika gagal
        """
        # Get JA3 dan payload
        ja3 = JA3_FINGERPRINTS.get(ja3_type, 'unknown')
        payload = PAYLOADS.get(payload_type, '')
        
        if not payload:
            print(f"❌ Invalid payload type: {payload_type}")
            return None
        
        # Generate IP jika tidak disediakan
        if not ip:
            ip = self._random_ip()
        
        if verbose:
            print(f"\n{'─'*60}")
            print(f"🔥 SIMULATING ATTACK")
            print(f"{'─'*60}")
            print(f"   IP      : {ip}")
            print(f"   JA3     : {ja3_type} ({ja3[:16]}...)")
            print(f"   Payload : {payload_type}")
            print(f"   Length  : {len(payload)} chars")
        
        # Kirim ke Pandora system
        try:
            response = self.session.post(
                f"{self.target}/analyze",
                json={
                    'ja3': ja3,
                    'payload': payload,
                    'ip': ip,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if verbose:
                    print(f"\n   📊 RESULT:")
                    print(f"      Level     : {result.get('level', 'UNKNOWN')}")
                    print(f"      Score     : {result.get('score', 0)}")
                    print(f"      Action    : {result.get('action', 'NONE')}")
                    
                    if 'matched_patterns' in result and result['matched_patterns']:
                        print(f"      Patterns  : {len(result['matched_patterns'])} matched")
                
                # Simpan hasil
                attack_result = {
                    'timestamp': datetime.now().isoformat(),
                    'ip': ip,
                    'ja3_type': ja3_type,
                    'ja3_hash': ja3[:16],
                    'payload_type': payload_type,
                    'payload_preview': payload[:50] + '...' if len(payload) > 50 else payload,
                    'score': result.get('score', 0),
                    'level': result.get('level', 'UNKNOWN'),
                    'action': result.get('action', 'NONE'),
                    'patterns_matched': len(result.get('matched_patterns', []))
                }
                self.results.append(attack_result)
                
                return attack_result
            else:
                if verbose:
                    print(f"\n   ❌ ERROR: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            if verbose:
                print(f"\n   ❌ ERROR: Cannot connect to {self.target}")
            return None
        except Exception as e:
            if verbose:
                print(f"\n   ❌ ERROR: {e}")
            return None
    
    def _random_ip(self) -> str:
        """Generate random IP address"""
        if random.random() < 0.3:  # 30% internal
            return random.choice(IP_RANGES['internal'])
        elif random.random() < 0.5:  # 20% tor/vpn
            return random.choice(IP_RANGES['tor'] + IP_RANGES['vpn'])
        else:  # 50% external
            return random.choice(IP_RANGES['external'])
    
    def simulate_mixed_attacks(self, count: int = 15) -> List[Dict]:
        """
        Simulasi campuran berbagai serangan
        
        Args:
            count: Jumlah serangan
            
        Returns:
            List hasil serangan
        """
        print(f"\n{'='*70}")
        print(f"🎯 MIXED ATTACKS SIMULATION ({count} attacks)")
        print(f"{'='*70}")
        
        results = []
        
        # Kombinasi serangan
        for i in range(count):
            # Pilih tipe serangan secara random dengan bobot
            ja3_type = random.choices(
                population=list(JA3_FINGERPRINTS.keys()),
                weights=[5, 5, 3, 2,   # browser
                        3, 3, 2, 2,    # tools
                        1, 1, 1, 1],   # attacker tools
                k=1
            )[0]
            
            # Pilih payload sesuai probabilitas
            if ja3_type in ['chrome', 'firefox', 'safari', 'edge']:
                # Browser cenderung normal
                payload_type = random.choices(
                    ['normal', 'api', 'sql', 'cobol'],
                    weights=[80, 15, 3, 2],
                    k=1
                )[0]
            elif ja3_type in ['python', 'curl', 'go', 'java']:
                # Tools cenderung mencurigakan
                payload_type = random.choices(
                    ['normal', 'sql', 'cobol', 'legacy', 'cobol_sql'],
                    weights=[20, 30, 25, 15, 10],
                    k=1
                )[0]
            else:
                # Attacker tools cenderung jahat
                payload_type = random.choices(
                    ['sql', 'cobol', 'cobol_sql', 'legacy_sql', 'malicious_php'],
                    weights=[30, 30, 20, 10, 10],
                    k=1
                )[0]
            
            result = self.simulate_attack(ja3_type, payload_type, verbose=True)
            if result:
                results.append(result)
            
            time.sleep(0.5)  # Jeda antar serangan
        
        return results
    
    def simulate_brute_force(self, count: int = 20) -> List[Dict]:
        """
        Simulasi brute force attack dari satu IP
        
        Args:
            count: Jumlah attempts
            
        Returns:
            List hasil serangan
        """
        print(f"\n{'='*70}")
        print(f"🔥 BRUTE FORCE SIMULATION ({count} attempts)")
        print(f"{'='*70}")
        
        # Gunakan IP yang sama untuk brute force
        ip = '45.33.22.11'
        ja3_type = 'python'
        
        results = []
        for i in range(count):
            # Variasi payload untuk tiap attempt
            if i % 3 == 0:
                payload_type = 'sql_basic'
            elif i % 3 == 1:
                payload_type = 'sql_union'
            else:
                payload_type = 'sql_time'
            
            print(f"\n[*] Attempt {i+1}/{count}")
            result = self.simulate_attack(ja3_type, payload_type, ip=ip, verbose=False)
            if result:
                results.append(result)
            
            time.sleep(0.3)
        
        # Tampilkan ringkasan
        print(f"\n{'─'*60}")
        print(f"📊 BRUTE FORCE SUMMARY")
        print(f"{'─'*60}")
        print(f"   IP        : {ip}")
        print(f"   JA3       : {ja3_type}")
        print(f"   Attempts  : {count}")
        print(f"   Detected  : {len([r for r in results if r['level'] != 'LOW'])}")
        print(f"   Critical  : {len([r for r in results if r['level'] == 'CRITICAL'])}")
        
        return results
    
    def simulate_distributed_attack(self, count: int = 30) -> List[Dict]:
        """
        Simulasi distributed attack dari banyak IP
        
        Args:
            count: Jumlah IP penyerang
            
        Returns:
            List hasil serangan
        """
        print(f"\n{'='*70}")
        print(f"🌍 DISTRIBUTED ATTACK SIMULATION ({count} attackers)")
        print(f"{'='*70}")
        
        results = []
        
        for i in range(count):
            # Random IP dari berbagai kategori
            ip_category = random.choice(list(IP_RANGES.keys()))
            ip = random.choice(IP_RANGES[ip_category])
            
            # Random JA3 dengan bobot
            ja3_type = random.choice(list(JA3_FINGERPRINTS.keys()))
            
            # Random payload
            payload_type = random.choice(list(PAYLOADS.keys()))
            
            if i % 5 == 0:  # Tampilkan progress
                print(f"\n[*] Attacker {i+1}/{count} from {ip_category}")
            
            result = self.simulate_attack(ja3_type, payload_type, ip=ip, verbose=False)
            if result:
                results.append(result)
            
            time.sleep(0.1)
        
        # Tampilkan ringkasan
        print(f"\n{'─'*60}")
        print(f"📊 DISTRIBUTED ATTACK SUMMARY")
        print(f"{'─'*60}")
        print(f"   Total Attackers : {count}")
        print(f"   Detected        : {len([r for r in results if r['level'] != 'LOW'])}")
        print(f"   Critical        : {len([r for r in results if r['level'] == 'CRITICAL'])}")
        
        # Breakdown per IP category
        print(f"\n   Breakdown per IP category:")
        for category in IP_RANGES:
            cat_attacks = [r for r in results if r['ip'] in IP_RANGES[category]]
            cat_critical = [r for r in cat_attacks if r['level'] == 'CRITICAL']
            print(f"      {category:10}: {len(cat_attacks)} attacks, {len(cat_critical)} critical")
        
        return results
    
    def simulate_persistence_test(self, duration: int = 60) -> List[Dict]:
        """
        Simulasi serangan berkelanjutan selama durasi tertentu
        
        Args:
            duration: Durasi dalam detik
            
        Returns:
            List hasil serangan
        """
        print(f"\n{'='*70}")
        print(f"⏱️  PERSISTENCE TEST ({duration} seconds)")
        print(f"{'='*70}")
        
        results = []
        start_time = time.time()
        attack_count = 0
        
        while time.time() - start_time < duration:
            attack_count += 1
            elapsed = int(time.time() - start_time)
            
            if attack_count % 10 == 0:
                print(f"\n[*] Second {elapsed}/{duration} - Attacks: {attack_count}")
            
            # Random attack
            ja3_type = random.choice(list(JA3_FINGERPRINTS.keys()))
            payload_type = random.choice(list(PAYLOADS.keys()))
            ip = self._random_ip()
            
            result = self.simulate_attack(ja3_type, payload_type, ip=ip, verbose=False)
            if result:
                results.append(result)
            
            time.sleep(random.uniform(0.5, 1.5))
        
        # Tampilkan ringkasan
        print(f"\n{'─'*60}")
        print(f"📊 PERSISTENCE TEST SUMMARY")
        print(f"{'─'*60}")
        print(f"   Duration    : {duration} seconds")
        print(f"   Total Attacks: {attack_count}")
        print(f"   Avg Rate    : {attack_count/duration:.1f} attacks/second")
        print(f"   Critical    : {len([r for r in results if r['level'] == 'CRITICAL'])}")
        
        return results
    
    def generate_report(self) -> Dict:
        """
        Generate laporan lengkap hasil simulasi
        
        Returns:
            Dictionary laporan
        """
        print(f"\n{'='*70}")
        print(f"📊 SIMULATION REPORT")
        print(f"{'='*70}")
        
        if not self.results:
            print("No results to report")
            return {}
        
        # Hitung statistik
        total = len(self.results)
        levels = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        actions = {}
        ja3_stats = {}
        payload_stats = {}
        
        for r in self.results:
            # Level
            level = r.get('level', 'UNKNOWN')
            levels[level] = levels.get(level, 0) + 1
            
            # Action
            action = r.get('action', 'UNKNOWN')
            actions[action] = actions.get(action, 0) + 1
            
            # JA3 type
            ja3 = r.get('ja3_type', 'unknown')
            ja3_stats[ja3] = ja3_stats.get(ja3, 0) + 1
            
            # Payload type
            payload = r.get('payload_type', 'unknown')
            payload_stats[payload] = payload_stats.get(payload, 0) + 1
        
        # Tampilkan report
        print(f"\n   Total Attacks: {total}")
        print(f"\n   Threat Levels:")
        for level, count in levels.items():
            pct = (count / total) * 100 if total > 0 else 0
            print(f"      {level:8}: {count:3} ({pct:.1f}%)")
        
        print(f"\n   Actions Taken:")
        for action, count in actions.items():
            print(f"      {action:10}: {count}")
        
        print(f"\n   Top 5 JA3 Types:")
        top_ja3 = sorted(ja3_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        for ja3, count in top_ja3:
            print(f"      {ja3:10}: {count}")
        
        print(f"\n   Top 5 Payload Types:")
        top_payload = sorted(payload_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        for payload, count in top_payload:
            print(f"      {payload:15}: {count}")
        
        # Return data
        return {
            'total': total,
            'levels': levels,
            'actions': actions,
            'ja3_stats': ja3_stats,
            'payload_stats': payload_stats,
            'results': self.results[-20:]  # Last 20 results
        }
    
    def export_results(self, filename: str = "simulation_results.json"):
        """
        Export hasil simulasi ke file JSON
        
        Args:
            filename: Nama file output
        """
        data = {
            'timestamp': datetime.now().isoformat(),
            'target': self.target,
            'total_attacks': len(self.results),
            'results': self.results
        }
  
