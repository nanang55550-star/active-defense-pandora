"""
Utility functions untuk Active Defense Pandora
Author: @nanang55550-star
"""

import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup logger dengan format standar
    
    Args:
        name: Nama logger
        level: Level logging
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler (opsional)
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(log_dir / f"{name}.log")
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        except:
            pass
    
    return logger

def get_timestamp() -> str:
    """Dapatkan timestamp sekarang"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def hash_data(data: str, algorithm: str = "sha256") -> str:
    """
    Buat hash dari data
    
    Args:
        data: String to hash
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hash string
    """
    if algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data.encode()).hexdigest()
    else:
        return hashlib.sha256(data.encode()).hexdigest()

def format_alert(threat_data: Dict) -> str:
    """
    Format hasil analisis jadi alert yang mudah dibaca
    
    Args:
        threat_data: Dictionary hasil analisis
        
    Returns:
        String alert terformat
    """
    timestamp = threat_data.get('timestamp', get_timestamp())
    
    alert = f"""
╔═══════════════════════════════════════════════════════════
║ 💀 PANDORA ALERT - {threat_data.get('level', 'UNKNOWN')}
╠═══════════════════════════════════════════════════════════
║ Time: {timestamp}
║ IP: {threat_data.get('ip', 'N/A')}
║ JA3: {threat_data.get('ja3_hash', 'N/A')}
║ Score: {threat_data.get('score', 0)}
║ Action: {threat_data.get('action', 'NONE')}
╚═══════════════════════════════════════════════════════════
"""
    
    return alert

def save_json(data: Any, filename: str, pretty: bool = True):
    """
    Simpan data ke file JSON
    
    Args:
        data: Data to save
        filename: Output filename
        pretty: Pretty print JSON
    """
    with open(filename, 'w') as f:
        if pretty:
            json.dump(data, f, indent=2, default=str)
        else:
            json.dump(data, f, default=str)

def load_json(filename: str) -> Any:
    """
    Load data dari file JSON
    
    Args:
        filename: Input filename
        
    Returns:
        Loaded data
    """
    with open(filename, 'r') as f:
        return json.load(f)

def validate_ip(ip: str) -> bool:
    """
    Validasi format IP address
    
    Args:
        ip: IP address string
        
    Returns:
        True if valid
    """
    import re
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    # Cek setiap oktet
    octets = ip.split('.')
    for octet in octets:
        if int(octet) > 255:
            return False
    
    return True

def get_mac_vendor(mac: str) -> str:
    """
    Dapatkan vendor dari MAC address (simplified)
    
    Args:
        mac: MAC address
        
    Returns:
        Vendor name
    """
    vendors = {
        '00:11:22': 'Cisco',
        'AA:BB:CC': 'Samsung',
        '11:22:33': 'TP-Link',
        '22:33:44': 'Intel',
    }
    
    prefix = mac[:8].upper()
    return vendors.get(prefix, 'Unknown')

def bytes_to_human(size_bytes: int) -> str:
    """
    Convert bytes to human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human readable string (e.g., "1.23 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def print_banner():
    """Print banner keren"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║  ██████╗  █████╗ ███╗   ██╗██████╗  ██████╗ ██████╗  █████╗ ║
    ║  ██╔══██╗██╔══██╗████╗  ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗║
    ║  ██████╔╝███████║██╔██╗ ██║██║  ██║██████╔╝██████╔╝███████║║
    ║  ██╔═══╝ ██╔══██║██║╚██╗██║██║  ██║██╔══██╗██╔══██╗██╔══██║║
    ║  ██║     ██║  ██║██║ ╚████║██████╔╝██║  ██║██║  ██║██║  ██║║
    ║  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝║
    ║                                                           ║
    ║           ACTIVE DEFENSE SYSTEM - by @nanang55550-star   ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
