#!/usr/bin/env python3
"""
Web Dashboard untuk Active Defense Pandora
Author: @nanang55550-star
"""

import json
import threading
from flask import Flask, render_template, jsonify, request
from datetime import datetime

# Import core modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pandora_engine import PandoraEngine
from intelligence.attacker_tracker import AttackerTracker
from intelligence.broadcast_manager import BroadcastManager

app = Flask(__name__)

# Global engine instance (akan di-set saat startup)
engine = None
tracker = None
broadcaster = None

@app.route('/')
def index():
    """Halaman utama dashboard"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """API endpoint untuk statistik real-time"""
    if engine:
        data = engine.get_dashboard_data()
        return jsonify(data)
    return jsonify({'error': 'Engine not initialized'})

@app.route('/api/attacks/recent')
def get_recent_attacks():
    """Dapatkan serangan terbaru"""
    if tracker:
        attacks = tracker.get_attack_timeline(hours=24)
        return jsonify(attacks)
    return jsonify([])

@app.route('/api/attackers/top')
def get_top_attackers():
    """Dapatkan top attackers"""
    if tracker:
        attackers = tracker.get_top_attackers(limit=20)
        return jsonify(attackers)
    return jsonify([])

@app.route('/api/blacklist')
def get_blacklist():
    """Dapatkan daftar blacklist"""
    if broadcaster:
        blacklist = broadcaster.get_blacklist()
        return jsonify({'ips': blacklist})
    return jsonify({'ips': []})

@app.route('/api/attack/<ip>')
def get_attack_detail(ip):
    """Detail serangan dari IP tertentu"""
    if tracker:
        profile = tracker.get_attacker_profile(ip)
        return jsonify(profile)
    return jsonify({})

@app.route('/api/poison/send', methods=['POST'])
def send_poison():
    """Kirim poison manual ke IP (via API)"""
    data = request.json
    ip = data.get('ip')
    poison_type = data.get('type', 'random')
    
    if engine and ip:
        # Trigger poison delivery
        threat_data = {
            'ip': ip,
            'level': 'CRITICAL',
            'action': 'MANUAL_POISON'
        }
        result = engine._handle_critical_threat(threat_data)
        return jsonify({'status': 'success', 'message': f'Poison sent to {ip}'})
    
    return jsonify({'status': 'error', 'message': 'Invalid request'})

@app.route('/api/block/ip', methods=['POST'])
def block_ip():
    """Block IP manual"""
    data = request.json
    ip = data.get('ip')
    duration = data.get('duration', 3600)
    
    if engine and ip:
        success = engine.defender.block_ip(ip, duration)
        if success:
            return jsonify({'status': 'success', 'message': f'IP {ip} blocked for {duration}s'})
    
    return jsonify({'status': 'error', 'message': 'Failed to block IP'})

@app.route('/api/unblock/ip', methods=['POST'])
def unblock_ip():
    """Unblock IP manual"""
    data = request.json
    ip = data.get('ip')
    
    if engine and ip:
        success = engine.defender.unblock_ip(ip)
        if success:
            return jsonify({'status': 'success', 'message': f'IP {ip} unblocked'})
    
    return jsonify({'status': 'error', 'message': 'Failed to unblock IP'})

@app.route('/api/config')
def get_config():
    """Dapatkan konfigurasi sistem"""
    if engine:
        return jsonify(engine.config)
    return jsonify({})

@app.route('/api/stats/poison')
def get_poison_stats():
    """Dapatkan statistik poison"""
    if engine:
        stats = engine.poison_factory.get_stats()
        return jsonify(stats)
    return jsonify({})

@app.route('/api/broadcast/test', methods=['POST'])
def test_broadcast():
    """Test broadcast ke semua peer"""
    if broadcaster:
        data = request.json
        ip = data.get('ip', '127.0.0.1')
        broadcaster.broadcast_threat(ip, {'test': True})
        return jsonify({'status': 'success', 'message': f'Broadcast test sent for {ip}'})
    
    return jsonify({'status': 'error', 'message': 'Broadcaster not initialized'})

def run_dashboard(engine_instance, port=5000):
    """Jalankan web dashboard"""
    global engine, tracker, broadcaster
    engine = engine_instance
    tracker = engine.tracker
    broadcaster = engine.broadcaster
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == "__main__":
    # Untuk testing standalone
    engine = PandoraEngine()
    tracker = engine.tracker
    broadcaster = engine.broadcaster
    app.run(host='0.0.0.0', port=5000, debug=True)
