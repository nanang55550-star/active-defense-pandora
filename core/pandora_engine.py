#!/usr/bin/env python3
"""
Active Defense Pandora - Core Engine
Author: @nanang55550-star
Version: 1.0.0
"""

import os
import sys
import time
import json
import yaml
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.detector import AnomalyDetector
from core.poison_factory import PoisonFactory
from core.defender import Defender
from core.utils import setup_logger, format_alert, get_timestamp
from intelligence.broadcast_manager import BroadcastManager
from intelligence.attacker_tracker import AttackerTracker
from integrations.telegram_bot.notifier import TelegramNotifier
from integrations.deepfake.voice_responder import DeepfakeVoice
from integrations.ja3_analyzer.bridge import JA3Bridge
from integrations.cobol.connector import COBOLConnector

console = Console()

class PandoraEngine:
    """
    The Main Engine of Active Defense Pandora
    Mendeteksi, meracuni, dan mendistribusikan ancaman secara real-time
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Inisialisasi Pandora Engine
        
        Args:
            config_path: Path ke file konfigurasi
        """
        self.logger = setup_logger('pandora_engine')
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.detector = AnomalyDetector(self.config)
        self.poison_factory = PoisonFactory(self.config)
        self.defender = Defender(self.config)
        self.tracker = AttackerTracker(self.config)
        self.broadcaster = BroadcastManager(self.config)
        self.notifier = TelegramNotifier(self.config)
        self.voice = DeepfakeVoice(self.config)
        self.ja3_bridge = JA3Bridge(self.config)
        self.cobol_connector = COBOLConnector(self.config)
        
        # Runtime data
        self.attack_log = []
        self.global_blacklist = set()
        self.active_threats = {}
        self.stats = {
            'total_attacks': 0,
            'critical_threats': 0,
            'poisons_sent': 0,
            'broadcasts_sent': 0,
            'start_time': time.time()
        }
        
        self.running = False
        self.lock = threading.Lock()
        
        self.logger.info("Pandora Engine initialized")
        console.print(Panel.fit(
            "[bold red]💀 ACTIVE DEFENSE PANDORA 💀[/bold red]\n"
            f"[yellow]Version: {__version__}[/yellow]\n"
            f"[green]Started at: {get_timestamp()}[/green]",
            border_style="red"
        ))
    
    def _load_config(self, config_path: str) -> dict:
        """Load konfigurasi dari file YAML"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"Config loaded from {config_path}")
            return config
        except FileNotFoundError:
            self.logger.warning(f"Config not found, using defaults")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
    
    def analyze_threat(self, ja3: str, payload: str, ip: str, 
                      metadata: Optional[Dict] = None) -> Dict:
        """
        Analisis threat level dari request masuk
        
        Args:
            ja3: JA3 fingerprint
            payload: Request payload
            ip: Source IP address
            metadata: Additional metadata
            
        Returns:
            Dictionary hasil analisis
        """
        with self.lock:
            self.stats['total_attacks'] += 1
        
        # Hitung threat score
        score = self.detector.calculate_threat_score(ja3, payload, ip)
        
        threat_data = {
            'id': f"THR-{int(time.time())}-{ip}",
            'timestamp': get_timestamp(),
            'ip': ip,
            'ja3': ja3,
            'ja3_hash': self._hash_ja3(ja3),
            'payload_hash': self._hash_payload(payload),
            'payload_preview': payload[:100] + "..." if len(payload) > 100 else payload,
            'score': score,
            'level': self._get_threat_level(score),
            'action': None,
            'metadata': metadata or {}
        }
        
        # Tentukan aksi berdasarkan score
        if score >= self.config.get('threat_levels', {}).get('critical', 80):
            threat_data['action'] = 'POISON_AND_BROADCAST'
            self._handle_critical_threat(threat_data)
        elif score >= self.config.get('threat_levels', {}).get('high', 60):
            threat_data['action'] = 'BROADCAST_ONLY'
            self._handle_high_threat(threat_data)
        elif score >= self.config.get('threat_levels', {}).get('medium', 30):
            threat_data['action'] = 'LOG_ONLY'
            self._handle_medium_threat(threat_data)
        else:
            threat_data['action'] = 'IGNORE'
        
        # Simpan ke log
        with self.lock:
            self.attack_log.append(threat_data)
            if len(self.attack_log) > 1000:
                self.attack_log = self.attack_log[-1000:]
        
        # Track attacker
        self.tracker.record_attack(threat_data)
        
        # Log ke file
        self._log_attack(threat_data)
        
        return threat_data
    
    def _handle_critical_threat(self, threat: Dict):
        """Handle ancaman kritis - BALIK SERANG!"""
        with self.lock:
            self.stats['critical_threats'] += 1
            self.global_blacklist.add(threat['ip'])
        
        self.logger.warning(f"[🔥] CRITICAL THREAT: {threat['ip']} (Score: {threat['score']})")
        console.print(f"[bold red][🔥] CRITICAL THREAT DETECTED: {threat['ip']}[/bold red]")
        
        # 1. Generate dan kirim poison
        poison = self.poison_factory.get_poison_for_threat(threat)
        if poison:
            with self.lock:
                self.stats['poisons_sent'] += 1
            self._send_poison(threat['ip'], poison)
            console.print(f"[yellow][*] Poison sent: {poison['name']}[/yellow]")
        
        # 2. Broadcast ke semua peer
        if self.config.get('broadcast', {}).get('enabled', True):
            self.broadcaster.broadcast_threat(threat['ip'], threat)
            with self.lock:
                self.stats['broadcasts_sent'] += 1
            console.print(f"[cyan][*] Threat broadcasted to all peers[/cyan]")
        
        # 3. Kirim notifikasi Telegram
        if self.config.get('telegram', {}).get('enabled', False):
            self.notifier.send_alert(
                f"🔥 CRITICAL THREAT\n"
                f"IP: {threat['ip']}\n"
                f"JA3: {threat['ja3'][:16]}...\n"
                f"Score: {threat['score']}\n"
                f"Action: POISON_SENT"
            )
        
        # 4. Mainkan suara deepfake (opsional)
        if self.config.get('deepfake', {}).get('enabled', True):
            self.voice.say_random()
    
    def _handle_high_threat(self, threat: Dict):
        """Handle ancaman tinggi - broadcast dan log"""
        self.logger.info(f"[!] HIGH THREAT: {threat['ip']} (Score: {threat['score']})")
        console.print(f"[yellow][!] HIGH THREAT: {threat['ip']} (Score: {threat['score']})[/yellow]")
        
        # Broadcast ke semua peer
        if self.config.get('broadcast', {}).get('enabled', True):
            self.broadcaster.broadcast_threat(threat['ip'], threat)
            with self.lock:
                self.stats['broadcasts_sent'] += 1
    
    def _handle_medium_threat(self, threat: Dict):
        """Handle ancaman medium - log saja"""
        self.logger.info(f"[*] MEDIUM THREAT: {threat['ip']} (Score: {threat['score']})")
        console.print(f"[dim][*] MEDIUM THREAT: {threat['ip']} (Score: {threat['score']})[/dim]")
    
    def _send_poison(self, ip: str, poison: Dict) -> bool:
        """
        Kirim poison ke attacker
        
        Args:
            ip: Target IP
            poison: Poison payload
            
        Returns:
            True jika berhasil
        """
        # TODO: Implement actual poison delivery
        # Ini bisa berupa HTTP response, TCP packet, dll
        self.logger.info(f"Poison sent to {ip}: {poison['name']}")
        return True
    
    def _get_threat_level(self, score: int) -> str:
        """Konversi score ke threat level"""
        if score >= self.config.get('threat_levels', {}).get('critical', 80):
            return 'CRITICAL'
        elif score >= self.config.get('threat_levels', {}).get('high', 60):
            return 'HIGH'
        elif score >= self.config.get('threat_levels', {}).get('medium', 30):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _hash_ja3(self, ja3: str) -> str:
        """Buat hash dari JA3 fingerprint"""
        import hashlib
        return hashlib.md5(ja3.encode()).hexdigest()[:16]
    
    def _hash_payload(self, payload: str) -> str:
        """Buat hash dari payload"""
        import hashlib
        return hashlib.sha256(payload.encode()).hexdigest()[:16]
    
    def _log_attack(self, threat: Dict):
        """Simpan attack ke file log"""
        log_file = self.config.get('logging', {}).get('file', 'logs/attack_logs.json')
        
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Baca log existing
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            # Tambah log baru
            logs.append(threat)
            
            # Simpan (max 1000 entries)
            with open(log_file, 'w') as f:
                json.dump(logs[-1000:], f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to log attack: {e}")
    
    def get_dashboard_data(self) -> Dict:
        """Generate data buat web dashboard"""
        with self.lock:
            uptime = int(time.time() - self.stats['start_time'])
            
            return {
                'stats': {
                    'total_attacks': self.stats['total_attacks'],
                    'critical_threats': self.stats['critical_threats'],
                    'poisons_sent': self.stats['poisons_sent'],
                    'broadcasts_sent': self.stats['broadcasts_sent'],
                    'uptime': uptime,
                    'uptime_str': self._format_uptime(uptime)
                },
                'blacklist': list(self.global_blacklist)[:100],
                'recent_attacks': self.attack_log[-20:],
                'threat_levels': {
                    'low': self.stats['total_attacks'] - self.stats['critical_threats'],
                    'critical': self.stats['critical_threats']
                }
            }
    
    def _format_uptime(self, seconds: int) -> str:
        """Format uptime ke HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def run_dashboard(self):
        """Tampilkan live dashboard di terminal"""
        with Live(auto_refresh=True, refresh_per_second=1) as live:
            while self.running:
                layout = self._create_layout()
                live.update(layout)
                time.sleep(1)
    
    def _create_layout(self) -> Layout:
        """Buat layout dashboard"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="stats", size=3),
            Layout(name="content", size=10),
            Layout(name="footer", size=3)
        )
        
        # Header
        layout["header"].update(Panel(
            Text("💀 ACTIVE DEFENSE PANDORA - REAL-TIME MONITOR 💀", 
                 style="bold red"),
            border_style="red"
        ))
        
        # Stats
        data = self.get_dashboard_data()
        stats_text = (
            f"Total Attacks: {data['stats']['total_attacks']} | "
            f"Critical: {data['stats']['critical_threats']} | "
            f"Poisons Sent: {data['stats']['poisons_sent']} | "
            f"Broadcasts: {data['stats']['broadcasts_sent']} | "
            f"Uptime: {data['stats']['uptime_str']}"
        )
        layout["stats"].update(Panel(stats_text, border_style="cyan"))
        
        # Recent attacks table
        table = Table(title="Recent Attacks", border_style="red")
        table.add_column("Time", style="dim")
        table.add_column("IP", style="yellow")
        table.add_column("JA3", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Level", style="bold")
        table.add_column("Action", style="red")
        
        for attack in data['recent_attacks'][::-1]:
            level_style = {
                'CRITICAL': 'bold red',
                'HIGH': 'yellow',
                'MEDIUM': 'cyan',
                'LOW': 'green'
            }.get(attack['level'], 'white')
            
            table.add_row(
                attack['timestamp'][11:19],
                attack['ip'],
                attack['ja3_hash'],
                str(attack['score']),
                f"[{level_style}]{attack['level']}[/{level_style}]",
                attack['action']
            )
        
        layout["content"].update(Panel(table, border_style="blue"))
        
        # Footer
        footer_text = (
            f"Blacklisted IPs: {len(data['blacklist'])} | "
            f"Press Ctrl+C to shutdown"
        )
        layout["footer"].update(Panel(footer_text, border_style="green"))
        
        return layout
    
    def start(self):
        """Start Pandora Engine"""
        self.running = True
        self.logger.info("Pandora Engine started")
        
        # Start broadcast listener
        if self.config.get('broadcast', {}).get('enabled', True):
            threading.Thread(target=self.broadcaster.start_listener, daemon=True).start()
        
        # Start dashboard
        try:
            self.run_dashboard()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop Pandora Engine"""
        self.running = False
        self.logger.info("Pandora Engine stopped")
        
        # Save final stats
        self._save_stats()
        
        console.print("\n[bold red]💀 PANDORA SYSTEM SHUTDOWN 💀[/bold red]")
    
    def _save_stats(self):
        """Save statistics to file"""
        stats_file = "logs/pandora_stats.json"
        try:
            os.makedirs("logs", exist_ok=True)
            with open(stats_file, 'w') as f:
                json.dump({
                    'timestamp': get_timestamp(),
                    'stats': self.stats,
                    'blacklist': list(self.global_blacklist)
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save stats: {e}")


def main():
    """Main entry point"""
    engine = PandoraEngine()
    
    # Test dengan beberapa simulasi
    test_attacks = [
        # Python requests dengan COBOL payload (CRITICAL)
        ("b32309a26951912be7dba376398abc3b", 
         "IDENTIFICATION DIVISION. PROGRAM-ID. HACK.", 
         "192.168.1.666"),
        
        # Chrome asli dengan request normal (LOW)
        ("cd08e31494f13d058c4f4a31675465b2", 
         "GET /index.html HTTP/1.1", 
         "192.168.1.100"),
        
        # Burp Suite dengan SQL injection (HIGH)
        ("132b490d1d2938164b391786576d1209", 
         "SELECT * FROM users WHERE id=1 OR 1=1--", 
         "10.0.0.5"),
        
        # Firefox dengan payload COBOL (MEDIUM)
        ("451996847a976f62660143896dfa2845",
         "IDENTIFICATION DIVISION.",
         "172.16.1.50"),
    ]
    
    # Jalankan simulasi
    console.print("[*] Running attack simulation...\n")
    for ja3, payload, ip in test_attacks:
        engine.analyze_threat(ja3, payload, ip)
        time.sleep(2)
    
    # Start actual engine
    engine.start()


if __name__ == "__main__":
    main()
