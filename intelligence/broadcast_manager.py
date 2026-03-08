"""
Broadcast Manager - Distribusi ancaman ke seluruh ekosistem
Author: @nanang55550-star
"""

import json
import requests
import threading
import time
from typing import Dict, List, Set, Optional
from queue import Queue

class BroadcastManager:
    """
    Mengelola penyebaran informasi ancaman ke semua instance
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.peer_instances = self.config.get('broadcast', {}).get('peer_instances', [
            "http://instance1.local:8080",
            "http://instance2.local:8080",
            "https://api.nanang55550-star.repl.co"
        ])
        
        self.protocol = self.config.get('broadcast', {}).get('protocol', 'http')
        self.timeout = self.config.get('broadcast', {}).get('timeout', 2)
        self.retry_count = self.config.get('broadcast', {}).get('retry_count', 3)
        
        self.blacklist: Set[str] = set()
        self.pending_broadcasts = Queue()
        self.broadcast_history = []
        self.lock = threading.Lock()
        
        # Start broadcast worker
        self.running = True
        self.worker = threading.Thread(target=self._broadcast_worker, daemon=True)
        self.worker.start()
        
    def broadcast_threat(self, ip: str, threat_data: Optional[Dict] = None):
        """
        Broadcast IP penyerang ke semua peer
        
        Args:
            ip: IP address to broadcast
            threat_data: Additional threat data
        """
        with self.lock:
            self.blacklist.add(ip)
        
        broadcast_data = {
            'type': 'THREAT_BROADCAST',
            'ip': ip,
            'timestamp': time.time(),
            'data': threat_data or {}
        }
        
        self.pending_broadcasts.put(broadcast_data)
        self._log_broadcast(ip, 'queued', threat_data)
    
    def _broadcast_worker(self):
        """Worker thread untuk mengirim broadcast"""
        while self.running:
            try:
                # Ambil dari queue dengan timeout
                data = self.pending_broadcasts.get(timeout=1)
                
                # Kirim ke semua peer
                success = self._send_to_peers(data)
                
                if success:
                    self._log_broadcast(data['ip'], 'sent', data['data'])
                else:
                    # Retry jika gagal
                    for attempt in range(self.retry_count):
                        time.sleep(2 ** attempt)  # Exponential backoff
                        if self._send_to_peers(data):
                            self._log_broadcast(data['ip'], 'retry_success', data['data'])
                            break
                    else:
                        self._log_broadcast(data['ip'], 'failed', data['data'])
                        
            except Queue.Empty:
                continue
            except Exception as e:
                print(f"Broadcast worker error: {e}")
    
    def _send_to_peers(self, data: Dict) -> bool:
        """
        Kirim data ke semua peer
        
        Args:
            data: Data to broadcast
            
        Returns:
            True if at least one peer received
        """
        success = False
        
        for peer in self.peer_instances:
            try:
                if self.protocol == 'http':
                    response = requests.post(
                        f"{peer}/api/broadcast",
                        json=data,
                        timeout=self.timeout
                    )
                    if response.status_code == 200:
                        success = True
                else:
                    # TODO: Implement other protocols (grpc, websocket)
                    pass
                    
            except Exception as e:
                print(f"Failed to broadcast to {peer}: {e}")
        
        return success
    
    def receive_broadcast(self, ip: str, data: Dict = None) -> Dict:
        """
        Terima broadcast dari peer lain
        
        Args:
            ip: IP address that was broadcasted
            data: Additional data
            
        Returns:
            Response dict
        """
        with self.lock:
            self.blacklist.add(ip)
            self._log_broadcast(ip, 'received', data)
        
        return {"status": "added", "ip": ip}
    
    def is_blacklisted(self, ip: str) -> bool:
        """Cek apakah IP ada di blacklist global"""
        return ip in self.blacklist
    
    def get_blacklist(self) -> List[str]:
        """Dapatkan semua blacklist"""
        with self.lock:
            return list(self.blacklist)
    
    def _log_broadcast(self, ip: str, status: str, data: Optional[Dict]):
        """Log broadcast activity"""
        log_entry = {
            'timestamp': time.time(),
            'ip': ip,
            'status': status,
            'data': data
        }
        
        with self.lock:
            self.broadcast_history.append(log_entry)
            if len(self.broadcast_history) > 1000:
                self.broadcast_history = self.broadcast_history[-1000:]
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik broadcast"""
        with self.lock:
            return {
                'blacklist_size': len(self.blacklist),
                'pending_broadcasts': self.pending_broadcasts.qsize(),
                'total_broadcasts': len(self.broadcast_history),
                'peers': len(self.peer_instances)
            }
    
    def add_peer(self, peer_url: str):
        """Tambah peer baru"""
        if peer_url not in self.peer_instances:
            self.peer_instances.append(peer_url)
    
    def remove_peer(self, peer_url: str):
        """Hapus peer"""
        if peer_url in self.peer_instances:
            self.peer_instances.remove(peer_url)
    
    def start_listener(self):
        """Start broadcast listener (untuk API mode)"""
        # Ini akan diimplementasikan di web_dashboard/app.py
        pass
    
    def stop(self):
        """Stop broadcast manager"""
        self.running = False
