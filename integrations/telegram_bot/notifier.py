"""
Telegram Notifier - Kirim alert ke Telegram
Author: @nanang55550-star
"""

import requests
from typing import Dict, Optional
from datetime import datetime

class TelegramNotifier:
    """
    Kirim notifikasi serangan ke Telegram
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.token = self.config.get('telegram', {}).get('token', '')
        self.chat_id = self.config.get('telegram', {}).get('chat_id', '')
        self.enabled = self.config.get('telegram', {}).get('enabled', False)
        
    def send_alert(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Kirim alert ke Telegram
        
        Args:
            message: Pesan yang dikirim
            parse_mode: Format pesan (HTML/Markdown)
            
        Returns:
            True jika berhasil
        """
        if not self.enabled or not self.token or not self.chat_id:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Telegram send error: {e}")
            return False
    
    def send_threat_alert(self, threat_data: Dict) -> bool:
        """
        Kirim alert khusus threat
        
        Args:
            threat_data: Data ancaman
            
        Returns:
            True jika berhasil
        """
        level = threat_data.get('level', 'UNKNOWN')
        
        # Pilih icon berdasarkan level
        icons = {
            'CRITICAL': '💀',
            'HIGH': '🔥',
            'MEDIUM': '⚠️',
            'LOW': 'ℹ️'
        }
        icon = icons.get(level, '❓')
        
        message = f"""
{icon} <b>PANDORA THREAT ALERT</b> {icon}

<b>Level:</b> {level}
<b>IP:</b> <code>{threat_data.get('ip', 'N/A')}</code>
<b>Score:</b> {threat_data.get('score', 0)}
<b>JA3:</b> <code>{threat_data.get('ja3_hash', 'N/A')}</code>
<b>Action:</b> {threat_data.get('action', 'NONE')}
<b>Time:</b> {threat_data.get('timestamp', datetime.now().isoformat())}

<b>Payload Preview:</b>
<pre>{threat_data.get('payload_preview', 'N/A')[:200]}</pre>
"""
        
        return self.send_alert(message)
    
    def send_daily_report(self, stats: Dict) -> bool:
        """
        Kirim laporan harian
        
        Args:
            stats: Statistik sistem
            
        Returns:
            True jika berhasil
        """
        message = f"""
📊 <b>PANDORA DAILY REPORT</b> 📊

<b>Total Attacks:</b> {stats.get('total_attacks', 0)}
<b>Critical Threats:</b> {stats.get('critical_threats', 0)}
<b>Poisons Sent:</b> {stats.get('poisons_sent', 0)}
<b>Broadcasts Sent:</b> {stats.get('broadcasts_sent', 0)}
<b>Uptime:</b> {stats.get('uptime_str', 'N/A')}

<b>Blacklisted IPs:</b> {len(stats.get('blacklist', []))}

<i>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_alert(message)
