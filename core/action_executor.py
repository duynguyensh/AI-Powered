"""
Action Executor for handling penetration testing actions
"""

import subprocess
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger


class ActionExecutor:
    """
    Executes various penetration testing actions
    
    Handles command execution, process management, and result collection
    with proper error handling and timeout management.
    """
    
    def __init__(self, max_workers: int = 5):
        """Initialize the action executor"""
        self.max_workers = max_workers
        self.active_processes: Dict[int, subprocess.Popen] = {}
        self.process_lock = threading.Lock()
        self.logger = logger
    
    def execute_command(self, command: List[str], timeout: int = 300, 
                       capture_output: bool = True) -> Dict[str, Any]:
        """
        Execute a shell command
        
        Args:
            command: List of command arguments
            timeout: Maximum execution time in seconds
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Dictionary with execution results
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"Executing command: {' '.join(command)}")
            
            if capture_output:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                process = subprocess.Popen(command)
            
            with self.process_lock:
                self.active_processes[process.pid] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                exit_code = -1
            
            # Remove from active processes
            with self.process_lock:
                self.active_processes.pop(process.pid, None)
            
            execution_time = time.time() - start_time
            
            result = {
                "command": command,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time,
                "success": exit_code == 0,
                "timed_out": exit_code == -1
            }
            
            if result["success"]:
                self.logger.debug(f"Command executed successfully in {execution_time:.2f}s")
            else:
                self.logger.warning(f"Command failed with exit code {exit_code}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute command: {e}")
            return {
                "command": command,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": time.time() - start_time,
                "success": False,
                "error": str(e)
            }
    
    def execute_parallel_commands(self, commands: List[List[str]], 
                                timeout: int = 300) -> List[Dict[str, Any]]:
        """
        Execute multiple commands in parallel
        
        Args:
            commands: List of command lists
            timeout: Maximum execution time per command
            
        Returns:
            List of execution results
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all commands
            future_to_command = {
                executor.submit(self.execute_command, cmd, timeout): cmd 
                for cmd in commands
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_command):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    command = future_to_command[future]
                    self.logger.error(f"Failed to execute parallel command: {e}")
                    results.append({
                        "command": command,
                        "exit_code": -1,
                        "stdout": "",
                        "stderr": str(e),
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    def execute_with_callback(self, command: List[str], 
                            callback: Callable[[Dict[str, Any]], None],
                            timeout: int = 300) -> None:
        """
        Execute command and call callback with result
        
        Args:
            command: Command to execute
            callback: Function to call with result
            timeout: Maximum execution time
        """
        def execute_and_callback():
            result = self.execute_command(command, timeout)
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"Callback failed: {e}")
        
        thread = threading.Thread(target=execute_and_callback)
        thread.daemon = True
        thread.start()
    
    def execute_web_request(self, url: str, method: str = "GET", 
                          headers: Dict[str, str] = None,
                          data: str = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute HTTP request
        
        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            data: Request data
            timeout: Request timeout
            
        Returns:
            Dictionary with response details
        """
        import requests
        
        start_time = time.time()
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=timeout,
                verify=False  # For testing purposes
            )
            
            execution_time = time.time() - start_time
            
            result = {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "execution_time": execution_time,
                "success": 200 <= response.status_code < 300
            }
            
            self.logger.debug(f"Request completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return {
                "url": url,
                "method": method,
                "status_code": None,
                "headers": {},
                "content": "",
                "execution_time": time.time() - start_time,
                "success": False,
                "error": str(e)
            }
    
    def execute_port_scan(self, target: str, ports: List[int] = None) -> Dict[str, Any]:
        """
        Execute port scan using nmap
        
        Args:
            target: Target hostname/IP
            ports: List of ports to scan (None for common ports)
            
        Returns:
            Dictionary with scan results
        """
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995, 1723, 3306, 3389, 5900, 8080]
        
        port_list = ",".join(map(str, ports))
        command = ["nmap", "-sS", "-sV", "-O", "-p", port_list, target]
        
        result = self.execute_command(command, timeout=600)
        
        # Parse nmap output
        if result["success"]:
            result["parsed_ports"] = self._parse_nmap_output(result["stdout"])
        
        return result
    
    def _parse_nmap_output(self, nmap_output: str) -> List[Dict[str, Any]]:
        """Parse nmap output to extract port information"""
        ports = []
        lines = nmap_output.split('\n')
        
        for line in lines:
            if '/tcp' in line and 'open' in line:
                parts = line.strip().split()
                if len(parts) >= 3:
                    port_info = parts[0].split('/')
                    port_num = int(port_info[0])
                    protocol = port_info[1]
                    state = parts[1]
                    service = parts[2] if len(parts) > 2 else "unknown"
                    
                    ports.append({
                        "port": port_num,
                        "protocol": protocol,
                        "state": state,
                        "service": service
                    })
        
        return ports
    
    def execute_vulnerability_scan(self, target: str, scan_type: str = "basic") -> Dict[str, Any]:
        """
        Execute vulnerability scan
        
        Args:
            target: Target hostname/IP
            scan_type: Type of scan (basic, full, web)
            
        Returns:
            Dictionary with scan results
        """
        if scan_type == "web":
            # Web application vulnerability scan
            command = ["nikto", "-h", target]
        else:
            # Basic network vulnerability scan
            command = ["nmap", "--script", "vuln", target]
        
        result = self.execute_command(command, timeout=900)
        
        if result["success"]:
            result["vulnerabilities"] = self._parse_vulnerability_output(result["stdout"], scan_type)
        
        return result
    
    def _parse_vulnerability_output(self, output: str, scan_type: str) -> List[Dict[str, Any]]:
        """Parse vulnerability scan output"""
        vulnerabilities = []
        
        if scan_type == "web":
            # Parse nikto output
            lines = output.split('\n')
            for line in lines:
                if '+ ' in line and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        vulnerabilities.append({
                            "type": "web",
                            "description": parts[1].strip(),
                            "severity": "medium"  # Default severity
                        })
        else:
            # Parse nmap vuln script output
            lines = output.split('\n')
            for line in lines:
                if 'VULNERABLE' in line:
                    vulnerabilities.append({
                        "type": "network",
                        "description": line.strip(),
                        "severity": "high"
                    })
        
        return vulnerabilities
    
    def get_active_processes(self) -> List[int]:
        """Get list of active process PIDs"""
        with self.process_lock:
            return list(self.active_processes.keys())
    
    def stop_process(self, pid: int) -> bool:
        """Stop a specific process"""
        with self.process_lock:
            if pid in self.active_processes:
                process = self.active_processes[pid]
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    del self.active_processes[pid]
                    self.logger.info(f"Process {pid} stopped")
                    return True
                except subprocess.TimeoutExpired:
                    process.kill()
                    del self.active_processes[pid]
                    self.logger.warning(f"Process {pid} killed")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to stop process {pid}: {e}")
                    return False
            return False
    
    def stop_all_processes(self):
        """Stop all active processes"""
        with self.process_lock:
            pids = list(self.active_processes.keys())
        
        for pid in pids:
            self.stop_process(pid)
        
        self.logger.info("All active processes stopped")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for the current environment"""
        import platform
        import psutil
        
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "cpu_count": psutil.cpu_count(),
            "python_version": platform.python_version()
        } 
