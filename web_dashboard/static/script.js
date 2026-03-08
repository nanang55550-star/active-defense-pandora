// Pandora Dashboard - Interactive Script

let threatChart, levelChart;
let refreshInterval;

// Initialize on page load
$(document).ready(function() {
    loadData();
    refreshInterval = setInterval(loadData, 5000);
    
    // Setup charts
    setupCharts();
});

// Load all data from API
function loadData() {
    loadStats();
    loadRecentAttacks();
    loadTopAttackers();
    loadBlacklist();
}

// Load statistics
function loadStats() {
    $.get('/api/stats', function(data) {
        if (data.stats) {
            $('#total-attacks').text(data.stats.total_attacks || 0);
            $('#critical-threats').text(data.stats.critical_threats || 0);
            $('#poisons-sent').text(data.stats.poisons_sent || 0);
            $('#broadcasts-sent').text(data.stats.broadcasts_sent || 0);
            $('#uptime').text(`Uptime: ${data.stats.uptime_str || '00:00:00'}`);
            
            // Update charts
            updateCharts(data);
        }
    });
}

// Load recent attacks
function loadRecentAttacks() {
    $.get('/api/attacks/recent', function(attacks) {
        let tbody = $('#attacks-body');
        tbody.empty();
        
        attacks.slice(0, 10).forEach(function(attack) {
            let levelClass = `level-${attack.level || 'LOW'}`;
            tbody.append(`
                <tr onclick="showAttackDetail('${attack.ip}')">
                    <td>${attack.timestamp ? attack.timestamp.slice(11, 19) : 'N/A'}</td>
                    <td>${attack.ip || 'N/A'}</td>
                    <td>${attack.ja3 ? attack.ja3.slice(0, 8) + '...' : 'N/A'}</td>
                    <td>${attack.score || 0}</td>
                    <td class="${levelClass}">${attack.level || 'LOW'}</td>
                    <td>${attack.action || 'NONE'}</td>
                </tr>
            `);
        });
    });
}

// Load top attackers
function loadTopAttackers() {
    $.get('/api/attackers/top', function(attackers) {
        let tbody = $('#attackers-body');
        tbody.empty();
        
        attackers.forEach(function(attacker) {
            tbody.append(`
                <tr onclick="showAttackDetail('${attacker.ip}')">
                    <td>${attacker.ip || 'N/A'}</td>
                    <td>${attacker.total_attacks || 0}</td>
                    <td>${attacker.risk_score || 0}</td>
                    <td>${attacker.last_seen ? attacker.last_seen.slice(11, 19) : 'N/A'}</td>
                </tr>
            `);
        });
    });
}

// Load blacklist
function loadBlacklist() {
    $.get('/api/blacklist', function(data) {
        let grid = $('#blacklist-grid');
        grid.empty();
        
        (data.ips || []).forEach(function(ip) {
            grid.append(`
                <div class="blacklist-ip">
                    <span class="ip-address">${ip}</span>
                    <button class="unblock-btn" onclick="unblockIP('${ip}')">✕</button>
                </div>
            `);
        });
    });
}

// Setup charts
function setupCharts() {
    // Threat Timeline Chart
    let threatCtx = document.getElementById('threatChart').getContext('2d');
    threatChart = new Chart(threatCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Threats',
                data: [],
                borderColor: '#ff0000',
                backgroundColor: 'rgba(255,0,0,0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#003300' },
                    ticks: { color: '#00ff00' }
                },
                x: {
                    grid: { color: '#003300' },
                    ticks: { color: '#00ff00' }
                }
            },
            plugins: {
                legend: { labels: { color: '#00ff00' } }
            }
        }
    });
    
    // Level Distribution Chart
    let levelCtx = document.getElementById('levelChart').getContext('2d');
    levelChart = new Chart(levelCtx, {
        type: 'doughnut',
        data: {
            labels: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: ['#ff0000', '#ff6600', '#ffff00', '#00ff00'],
                borderColor: '#000000'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#00ff00' } }
            }
        }
    });
}

// Update charts with new data
function updateCharts(data) {
    if (!data.recent_attacks) return;
    
    // Update timeline
    let times = data.recent_attacks.slice(-10).map(a => 
        a.timestamp ? a.timestamp.slice(11, 16) : 'N/A'
    );
    let scores = data.recent_attacks.slice(-10).map(a => a.score || 0);
    
    threatChart.data.labels = times;
    threatChart.data.datasets[0].data = scores;
    threatChart.update();
    
    // Update level distribution
    if (data.threat_levels) {
        levelChart.data.datasets[0].data = [
            data.threat_levels.critical || 0,
            data.threat_levels.high || 0,
            data.threat_levels.medium || 0,
            data.threat_levels.low || 0
        ];
        levelChart.update();
    }
}

// Show attack detail
function showAttackDetail(ip) {
    window.open(`/api/attack/${ip}`, '_blank');
}

// Block IP
function blockIP() {
    let ip = $('#block-ip').val();
    if (!ip) {
        alert('Please enter an IP address');
        return;
    }
    
    $.post('/api/block/ip', {ip: ip}, function(data) {
        if (data.status === 'success') {
            alert(`✅ ${data.message}`);
            $('#block-ip').val('');
            loadData();
        } else {
            alert(`❌ ${data.message}`);
        }
    });
}

// Unblock IP
function unblockIP(ip) {
    if (!confirm(`Unblock ${ip}?`)) return;
    
    $.post('/api/unblock/ip', {ip: ip}, function(data) {
        if (data.status === 'success') {
            alert(`✅ ${data.message}`);
            loadData();
        } else {
            alert(`❌ ${data.message}`);
        }
    });
}

// Send poison
function sendPoison() {
    let ip = $('#poison-ip').val();
    let type = $('#poison-type').val();
    
    if (!ip) {
        alert('Please enter an IP address');
        return;
    }
    
    if (!confirm(`Send ${type} poison to ${ip}?`)) return;
    
    $.post('/api/poison/send', {ip: ip, type: type}, function(data) {
        if (data.status === 'success') {
            alert(`✅ ${data.message}`);
            $('#poison-ip').val('');
            loadData();
        } else {
            alert(`❌ ${data.message}`);
        }
    });
}

// Test broadcast
function testBroadcast() {
    $.post('/api/broadcast/test', {ip: '127.0.0.1'}, function(data) {
        if (data.status === 'success') {
            alert(`✅ ${data.message}`);
        } else {
            alert(`❌ ${data.message}`);
        }
    });
}

// Refresh data manually
function refreshData() {
    loadData();
}

// Export logs
function exportLogs() {
    window.location.href = '/api/attacks/recent?export=true';
}

// Clean up on page unload
$(window).on('unload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
