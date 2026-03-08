"""
COBOL Connector - Simulasi koneksi ke mainframe COBOL
Author: @nanang55550-star
"""

import socket
import struct
from typing import Optional, Dict
from datetime import datetime

class COBOLConnector:
    """
    Simulasi koneksi ke mainframe COBOL
    Mengirim dan menerima data dengan format fixed-length
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.host = self.config.get('integrations', {})\
                               .get('cobol_mainframe', {})\
                               .get('host', 'localhost')
        self.port = self.config.get('integrations', {})\
                               .get('cobol_mainframe', {})\
                               .get('port', 9876)
        self.timeout = self.config.get('integrations', {})\
                                  .get('cobol_mainframe', {})\
                                  .get('timeout', 10)
    
    def create_transaction(self, account_id: str, amount: float, 
                          transaction_type: str = "TRF") -> bytes:
        """
        Buat transaksi COBOL format fixed-length
        
        Args:
            account_id: Nomor rekening (10 digit)
            amount: Jumlah transaksi
            transaction_type: Tipe transaksi (3 char)
            
        Returns:
            Bytes packet
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Format COBOL fixed-length
        # [10: account][3: type][14: timestamp][8: amount]
        account_field = f"{account_id:0>10}".encode('ascii')
        type_field = transaction_type.ljust(3)[:3].encode('ascii')
        timestamp_field = timestamp.encode('ascii')
        amount_field = f"{amount:015.2f}".replace('.', '').encode('ascii')
        
        return account_field + type_field + timestamp_field + amount_field
    
    def parse_response(self, response: bytes) -> Dict:
        """
        Parse response dari mainframe
        
        Args:
            response: Bytes response
            
        Returns:
            Dictionary hasil parse
        """
        if len(response) < 20:
            return {'status': 'ERROR', 'message': 'Invalid response'}
        
        try:
            status = response[0:2].decode('ascii')
            balance = int(response[2:17].decode('ascii')) / 100
            message = response[17:].decode('ascii').strip('\x00')
            
            return {
                'status': status,
                'balance': balance,
                'message': message,
                'success': status == 'OK'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': str(e),
                'success': False
            }
    
    def send_transaction(self, account_id: str, amount: float,
                        transaction_type: str = "TRF") -> Optional[Dict]:
        """
        Kirim transaksi ke mainframe
        
        Args:
            account_id: Nomor rekening
            amount: Jumlah transaksi
            transaction_type: Tipe transaksi
            
        Returns:
            Response dictionary atau None jika gagal
        """
        packet = self.create_transaction(account_id, amount, transaction_type)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            
            sock.send(packet)
            response = sock.recv(1024)
            sock.close()
            
            return self.parse_response(response)
            
        except Exception as e:
            print(f"COBOL connection error: {e}")
            return None
    
    def simulate_mainframe(self):
        """Simulasi mainframe server (untuk testing)"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        
        print(f"[*] COBOL Mainframe simulator listening on port {self.port}")
        
        while True:
            client, addr = server.accept()
            data = client.recv(1024)
            
            # Parse request
            if len(data) >= 35:
                account = data[0:10].decode('ascii')
                amount = int(data[18:33].decode('ascii')) / 100
                
                # Generate response
                response = f"OK{0:015d}TRANSACTION COMPLETE".encode('ascii')
                client.send(response)
            
            client.close()
