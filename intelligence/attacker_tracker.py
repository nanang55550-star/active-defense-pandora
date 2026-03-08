"""
Attacker Tracker - Melacak dan memprofil penyerang
Author: @nanang55550-star
"""

import time
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from pathlib import Path

class AttackerTracker:
    """
    Melacak aktivitas penyerang dan membangun profil
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.db_path = Path(self.config.get('database', {}).get('path', 'data/threat_intel.db'))
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.attackers = defaultdict(lambda: {
            'first_seen': None,
            'last_seen': None,
            'total_attacks': 0,
            'ja3_profiles': [],
            'attack_patterns': [],
            'risk_score': 0
        })
        
        self._init_database()
        
    def _init_database(self):
        """Inisialisasi database SQLite"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        # Tabel attackers
        c.execute('''
            CREATE TABLE IF NOT EXISTS attackers (
                ip TEXT PRIMARY KEY,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                total_attacks INTEGER,
                ja3_profiles TEXT,
                attack_patterns TEXT,
                risk_score INTEGER,
                country TEXT,
                asn TEXT
            )
        ''')
        
        # Tabel attack_logs
        c.execute('''
            CREATE TABLE IF NOT EXISTS attack_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                ip TEXT,
                ja3 TEXT,
                score INTEGER,
                level TEXT,
                payload_preview TEXT,
                action TEXT
            )
        ''')
        
        # Tabel blacklist
        c.execute('''
            CREATE TABLE IF NOT EXISTS blacklist (
                ip TEXT PRIMARY KEY,
                added TIMESTAMP,
                reason TEXT,
                expires TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_attack(self, threat_data: Dict):
        """Rekam serangan baru"""
        ip = threat_data.get('ip')
        timestamp = threat_data.get('timestamp')
        
        # Update memory
        attacker = self.attackers[ip]
        if not attacker['first_seen']:
            attacker['first_seen'] = timestamp
        attacker['last_seen'] = timestamp
        attacker['total_attacks'] += 1
        
        # Add JA3 profile
        ja3 = threat_data.get('ja3', '')
        if ja3 and ja3 not in attacker['ja3_profiles']:
            attacker['ja3_profiles'].append(ja3)
        
        # Update risk score
        attacker['risk_score'] = max(
            attacker['risk_score'],
            threat_data.get('score', 0)
        )
        
        # Simpan ke database
        self._save_to_db(threat_data)
    
    def _save_to_db(self, threat_data: Dict):
        """Simpan data ke database"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        # Insert attack log
        c.execute('''
            INSERT INTO attack_logs 
            (timestamp, ip, ja3, score, level, payload_preview, action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            threat_data.get('timestamp'),
            threat_data.get('ip'),
            threat_data.get('ja3'),
            threat_data.get('score'),
            threat_data.get('level'),
            threat_data.get('payload_preview', '')[:200],
            threat_data.get('action')
        ))
        
        # Update/Insert attacker
        ip = threat_data.get('ip')
        c.execute('SELECT * FROM attackers WHERE ip = ?', (ip,))
        existing = c.fetchone()
        
        if existing:
            c.execute('''
                UPDATE attackers 
                SET last_seen = ?,
                    total_attacks = total_attacks + 1,
                    ja3_profiles = ?,
                    risk_score = ?
                WHERE ip = ?
            ''', (
                threat_data.get('timestamp'),
                json.dumps(self.attackers[ip]['ja3_profiles']),
                self.attackers[ip]['risk_score'],
                ip
            ))
        else:
            c.execute('''
                INSERT INTO attackers 
                (ip, first_seen, last_seen, total_attacks, ja3_profiles, risk_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                ip,
                threat_data.get('timestamp'),
                threat_data.get('timestamp'),
                1,
                json.dumps([threat_data.get('ja3')]),
                threat_data.get('score')
            ))
        
        conn.commit()
        conn.close()
    
    def get_attacker_profile(self, ip: str) -> Dict:
        """Dapatkan profil lengkap penyerang"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        c.execute('SELECT * FROM attackers WHERE ip = ?', (ip,))
        row = c.fetchone()
        
        if row:
            profile = {
                'ip': row[0],
                'first_seen': row[1],
                'last_seen': row[2],
                'total_attacks': row[3],
                'ja3_profiles': json.loads(row[4]) if row[4] else [],
                'risk_score': row[5]
            }
        else:
            profile = self.attackers.get(ip, {})
        
        conn.close()
        return profile
    
    def get_top_attackers(self, limit: int = 10) -> List[Dict]:
        """Dapatkan daftar penyerang teratas"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        c.execute('''
            SELECT ip, total_attacks, risk_score, last_seen 
            FROM attackers 
            ORDER BY total_attacks DESC 
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in c.fetchall():
            results.append({
                'ip': row[0],
                'total_attacks': row[1],
                'risk_score': row[2],
                'last_seen': row[3]
            })
        
        conn.close()
        return results
    
    def get_attack_timeline(self, hours: int = 24) -> List[Dict]:
        """Dapatkan timeline serangan"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        c.execute('''
            SELECT timestamp, ip, level, score 
            FROM attack_logs 
            WHERE timestamp > datetime('now', ? || ' hours')
            ORDER BY timestamp DESC
        ''', (f'-{hours}',))
        
        results = []
        for row in c.fetchall():
            results.append({
                'timestamp': row[0],
                'ip': row[1],
                'level': row[2],
                'score': row[3]
            })
        
        conn.close()
        return results
    
    def blacklist_ip(self, ip: str, reason: str = "manual", expires: int = 86400):
        """Tambah IP ke blacklist"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        import datetime
        expires_time = (datetime.datetime.now() + 
                       datetime.timedelta(seconds=expires)).isoformat()
        
        c.execute('''
            INSERT OR REPLACE INTO blacklist (ip, added, reason, expires)
            VALUES (?, ?, ?, ?)
        ''', (ip, datetime.datetime.now().isoformat(), reason, expires_time))
        
        conn.commit()
        conn.close()
    
    def is_blacklisted(self, ip: str) -> bool:
        """Cek apakah IP di blacklist"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        c.execute('SELECT expires FROM blacklist WHERE ip = ?', (ip,))
        row = c.fetchone()
        
        if row:
            import datetime
            expires = datetime.datetime.fromisoformat(row[0])
            if expires > datetime.datetime.now():
                conn.close()
                return True
        
        conn.close()
        return False
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik tracker"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM attackers')
        total_attackers = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM attack_logs')
        total_attacks = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM blacklist')
        total_blacklisted = c.fetchone()[0]
        
        c.execute('SELECT AVG(score) FROM attack_logs')
        avg_score = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_attackers': total_attackers,
            'total_attacks': total_attacks,
            'total_blacklisted': total_blacklisted,
            'average_score': round(avg_score, 2)
      }
