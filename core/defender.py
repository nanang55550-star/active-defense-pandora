"""
Defender Module - Logika pertahanan aktif
Author: @nanang55550-star
"""

import time
import threading
import subprocess
from typing import Dict, List, Optional
from datetime import datetime

class Defender:
    """
    Mengelola tindakan pertahanan aktif terhadap penyerang
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.active_defenses = {}
        self.blocked_ips = set()
        self.defense_history = []
        self.lock = threading.Lock()
        
    def block_ip(self, ip: str, duration: int = 3600) -> bool:
        """
        Blokir IP address (iptables)
        
        Args:
            ip: IP address to block
            duration: Block duration in seconds
            
        Returns:
            True if blocked successfully
        """
        try:
            # Simulasi iptables block
            # Dalam implementasi nyata: subprocess.run(['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
            
            with self.lock:
                self.blocked_ips.add(ip)
                self.active_defenses[ip] = {
                    'action': 'block',
                    'start_time': time.time(),
                    'duration': duration
                }
            
            # Schedule unblock
            if duration > 0:
                threading.Timer(duration, self.unblock_ip, args=[ip]).start()
            
            self._log_defense('block', ip, f'Blocked for {duration}s')
            return True
            
        except Exception as e:
            self._log_defense('block', ip, f'Failed: {e}')
            return False
    
    def unblock_ip(self, ip: str) -> bool:
        """
        Unblock IP address
        
        Args:
            ip: IP address to unblock
            
        Returns:
            True if unblocked successfully
        """
        try:
            # Simulasi iptables unblock
            with self.lock:
                if ip in self.blocked_ips:
                    self.blocked_ips.remove(ip)
                if ip in self.active_defenses:
                    del self.active_defenses[ip]
            
            self._log_defense('unblock', ip, 'Unblocked')
            return True
            
        except Exception as e:
            self._log_defense('unblock', ip, f'Failed: {e}')
            return False
    
    def rate_limit_ip(self, ip: str, limit: int = 100) -> bool:
        """
        Terapkan rate limiting untuk IP
        
        Args:
            ip: IP address
            limit: Max requests per minute
            
        Returns:
            True if rate limited
        """
        try:
            with self.lock:
                self.active_defenses[ip] = {
                    'action': 'rate_limit',
                    'limit': limit,
                    'start_time': time.time(),
                    'requests': 0
                }
            
            self._log_defense('rate_limit', ip, f'Limited to {limit}/min')
            return True
            
        except Exception as e:
            self._log_defense('rate_limit', ip, f'Failed: {e}')
            return False
    
    def redirect_to_honeypot(self, ip: str) -> bool:
        """
        Redirect attacker ke honeypot
        
        Args:
            ip: IP address
            
        Returns:
            True if redirected
        """
        try:
            # Simulasi redirect ke honeypot server
            with self.lock:
                self.active_defenses[ip] = {
                    'action': 'honeypot',
                    'start_time': time.time(),
                    'honeypot': 'pandora-honeypot.local'
                }
            
            self._log_defense('honeypot', ip, 'Redirected to honeypot')
            return True
            
        except Exception as e:
            self._log_defense('honeypot', ip, f'Failed: {e}')
            return False
    
    def inject_latency(self, ip: str, delay: float = 5.0) -> bool:
        """
        Inject latency ke koneksi attacker
        
        Args:
            ip: IP address
            delay: Additional delay in seconds
            
        Returns:
            True if injected
        """
        try:
            # Simulasi packet delay
            with self.lock:
                self.active_defenses[ip] = {
                    'action': 'latency',
                    'delay': delay,
                    'start_time': time.time()
                }
            
            self._log_defense('latency', ip, f'Injected {delay}s delay')
            return True
            
        except Exception as e:
            self._log_defense('latency', ip, f'Failed: {e}')
            return False
    
    def get_active_defenses(self) -> Dict:
        """Dapatkan daftar pertahanan aktif"""
        current_time = time.time()
        active = {}
        
        with self.lock:
            for ip, defense in self.active_defenses.items():
                elapsed = current_time - defense.get('start_time', current_time)
                duration = defense.get('duration', 0)
                
                if duration == 0 or elapsed < duration:
                    active[ip] = defense
        
        return active
    
    def get_blocked_ips(self) -> List[str]:
        """Dapatkan daftar IP yang diblokir"""
        with self.lock:
            return list(self.blocked_ips)
    
    def is_blocked(self, ip: str) -> bool:
        """Cek apakah IP diblokir"""
        return ip in self.blocked_ips
    
    def _log_defense(self, action: str, ip: str, details: str):
        """Log tindakan pertahanan"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'ip': ip,
            'details': details
        }
        
        with self.lock:
            self.defense_history.append(log_entry)
            if len(self.defense_history) > 1000:
                self.defense_history = self.defense_history[-1000:]
    
    def get_defense_history(self, limit: int = 100) -> List[Dict]:
        """Dapatkan history pertahanan"""
        with self.lock:
            return self.defense_history[-limit:]
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik pertahanan"""
        return {
            'blocked_ips_count': len(self.blocked_ips),
            'active_defenses_count': len(self.active_defenses),
            'total_actions': len(self.defense_history),
            'actions_by_type': {
                'block': sum(1 for d in self.defense_history if d['action'] == 'block'),
                'unblock': sum(1 for d in self.defense_history if d['action'] == 'unblock'),
                'rate_limit': sum(1 for d in self.defense_history if d['action'] == 'rate_limit'),
                'honeypot': sum(1 for d in self.defense_history if d['action'] == 'honeypot'),
                'latency': sum(1 for d in self.defense_history if d['action'] == 'latency')
            }
      }
