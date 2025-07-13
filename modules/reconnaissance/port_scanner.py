"""
Port Scanner Module
"""

import socket
import threading
from typing import Dict, List, Any
from loguru import logger


class PortScanner:
    """Basic port scanner for reconnaissance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logger
    
    def scan_ports(self, target: str, ports: List[int] = None) -> Dict[str, Any]:
        """Scan ports on target"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995, 1723, 3306, 3389, 5900, 8080]
        
        results = {
            "target": target,
            "open_ports": [],
            "total_attempts": len(ports),
            "successful_attempts": 0
        }
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))
                if result == 0:
                    results["open_ports"].append(port)
                    results["successful_attempts"] += 1
                sock.close()
            except Exception as e:
                self.logger.debug(f"Port {port} scan failed: {e}")
        
        return results 