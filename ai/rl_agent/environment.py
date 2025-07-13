"""
Reinforcement Learning Environment for Penetration Testing
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from loguru import logger


class PentestEnvironment:
    """
    Reinforcement Learning Environment for Penetration Testing
    
    Simulates a penetration testing scenario where the agent must
    discover vulnerabilities and exploit them to gain access.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the environment"""
        self.config = config
        self.rl_config = config.get("rl_environment", {})
        
        # Environment parameters
        self.max_steps = self.rl_config.get("max_steps", 1000)
        self.reward_success = self.rl_config.get("reward_success", 100)
        self.reward_failure = self.rl_config.get("reward_failure", -10)
        self.reward_discovery = self.rl_config.get("reward_discovery", 5)
        self.reward_escalation = self.rl_config.get("reward_escalation", 50)
        
        # State and action spaces
        self.state_size = 15  # Fixed state size
        self.action_size = 10  # Fixed action size
        
        # Action space definition
        self.action_space = [
            {"name": "port_scan", "type": "reconnaissance", "cost": 1},
            {"name": "service_detection", "type": "reconnaissance", "cost": 1},
            {"name": "web_crawl", "type": "reconnaissance", "cost": 2},
            {"name": "dns_enumeration", "type": "reconnaissance", "cost": 1},
            {"name": "vulnerability_scan", "type": "vulnerability", "cost": 3},
            {"name": "sql_injection_test", "type": "exploitation", "cost": 5},
            {"name": "xss_test", "type": "exploitation", "cost": 4},
            {"name": "weak_credentials", "type": "exploitation", "cost": 3},
            {"name": "privilege_escalation", "type": "privilege", "cost": 8},
            {"name": "data_exfiltration", "type": "post_exploitation", "cost": 10}
        ]
        
        # Environment state
        self.current_step = 0
        self.current_state = None
        self.target_info = {}
        self.discovered_vulnerabilities = []
        self.successful_exploits = []
        self.current_access_level = "none"
        
        self.logger = logger
    
    def reset(self) -> Dict[str, Any]:
        """Reset the environment to initial state"""
        self.current_step = 0
        self.discovered_vulnerabilities = []
        self.successful_exploits = []
        self.current_access_level = "none"
        
        # Initialize target with random properties
        self.target_info = self._generate_random_target()
        
        # Create initial state
        self.current_state = self._create_state()
        
        self.logger.debug("Environment reset")
        return self.current_state
    
    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Execute an action in the environment
        
        Args:
            action: Action to execute
            
        Returns:
            Tuple of (next_state, reward, done, info)
        """
        self.current_step += 1
        
        # Execute action and get results
        success, reward, info = self._execute_action(action)
        
        # Update environment state
        self._update_state(action, success, info)
        
        # Create new state
        next_state = self._create_state()
        self.current_state = next_state
        
        # Check if episode is done
        done = self._is_episode_done()
        
        return next_state, reward, done, info
    
    def _generate_random_target(self) -> Dict[str, Any]:
        """Generate a random target with vulnerabilities"""
        target = {
            "hostname": f"target-{np.random.randint(1000, 9999)}.example.com",
            "ip_address": f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}",
            "open_ports": np.random.choice([21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080], 
                                         size=np.random.randint(3, 8), replace=False).tolist(),
            "services": {},
            "vulnerabilities": []
        }
        
        # Add random vulnerabilities
        possible_vulns = [
            {"name": "SQL Injection", "severity": "high", "port": 80},
            {"name": "XSS", "severity": "medium", "port": 80},
            {"name": "Weak Passwords", "severity": "medium", "port": 22},
            {"name": "Outdated Software", "severity": "low", "port": 80},
            {"name": "Open Port", "severity": "low", "port": 23}
        ]
        
        num_vulns = np.random.randint(1, 4)
        target["vulnerabilities"] = np.random.choice(possible_vulns, size=num_vulns, replace=False).tolist()
        
        return target
    
    def _execute_action(self, action: Dict[str, Any]) -> Tuple[bool, float, Dict[str, Any]]:
        """Execute an action and return results"""
        action_name = action.get("name", "")
        success = False
        reward = 0
        info = {"action": action_name}
        
        if action_name == "port_scan":
            success = True
            reward = self.reward_discovery
            info["discovered_ports"] = len(self.target_info["open_ports"])
            
        elif action_name == "service_detection":
            success = True
            reward = self.reward_discovery
            info["discovered_services"] = len(self.target_info["services"])
            
        elif action_name == "web_crawl":
            if 80 in self.target_info["open_ports"] or 443 in self.target_info["open_ports"]:
                success = True
                reward = self.reward_discovery
                info["web_pages_found"] = np.random.randint(1, 10)
            else:
                success = False
                reward = self.reward_failure
                
        elif action_name == "vulnerability_scan":
            success = True
            reward = self.reward_discovery
            info["vulnerabilities_found"] = len(self.target_info["vulnerabilities"])
            
        elif action_name == "sql_injection_test":
            # Check if SQL injection vulnerability exists
            sql_vuln = next((v for v in self.target_info["vulnerabilities"] 
                           if v["name"] == "SQL Injection"), None)
            if sql_vuln:
                success = True
                reward = self.reward_success
                self.successful_exploits.append("SQL Injection")
                self.current_access_level = "user"
                info["exploit_successful"] = True
            else:
                success = False
                reward = self.reward_failure
                
        elif action_name == "xss_test":
            xss_vuln = next((v for v in self.target_info["vulnerabilities"] 
                           if v["name"] == "XSS"), None)
            if xss_vuln:
                success = True
                reward = self.reward_success
                self.successful_exploits.append("XSS")
                info["exploit_successful"] = True
            else:
                success = False
                reward = self.reward_failure
                
        elif action_name == "weak_credentials":
            weak_pass_vuln = next((v for v in self.target_info["vulnerabilities"] 
                                 if v["name"] == "Weak Passwords"), None)
            if weak_pass_vuln:
                success = True
                reward = self.reward_success
                self.successful_exploits.append("Weak Passwords")
                self.current_access_level = "user"
                info["exploit_successful"] = True
            else:
                success = False
                reward = self.reward_failure
                
        elif action_name == "privilege_escalation":
            if self.current_access_level in ["user", "admin"]:
                success = np.random.random() > 0.7  # 30% success rate
                if success:
                    reward = self.reward_escalation
                    self.current_access_level = "root"
                    info["escalation_successful"] = True
                else:
                    reward = self.reward_failure
            else:
                success = False
                reward = self.reward_failure
                
        elif action_name == "data_exfiltration":
            if self.current_access_level in ["admin", "root"]:
                success = True
                reward = self.reward_success * 2
                info["data_exfiltrated"] = True
            else:
                success = False
                reward = self.reward_failure
        
        info["success"] = success
        return success, reward, info
    
    def _update_state(self, action: Dict[str, Any], success: bool, info: Dict[str, Any]):
        """Update environment state based on action results"""
        if success and "vulnerabilities_found" in info:
            self.discovered_vulnerabilities.extend(self.target_info["vulnerabilities"])
    
    def _create_state(self) -> Dict[str, Any]:
        """Create current state representation"""
        return {
            "ip_resolved": bool(self.target_info.get("ip_address")),
            "discovered_ports": len(self.target_info.get("open_ports", [])),
            "discovered_services": len(self.target_info.get("services", {})),
            "found_vulnerabilities": len(self.discovered_vulnerabilities),
            "successful_exploits": len(self.successful_exploits),
            "current_access_level": self.current_access_level,
            "current_phase": self._get_current_phase(),
            "step": self.current_step
        }
    
    def _get_current_phase(self) -> str:
        """Get current testing phase"""
        if len(self.discovered_vulnerabilities) == 0:
            return "reconnaissance"
        elif len(self.successful_exploits) == 0:
            return "vulnerability_scanning"
        elif self.current_access_level in ["none", "user"]:
            return "exploitation"
        else:
            return "privilege_escalation"
    
    def _is_episode_done(self) -> bool:
        """Check if episode should end"""
        # Episode ends if:
        # 1. Maximum steps reached
        # 2. Root access achieved
        # 3. All vulnerabilities exploited
        # 4. No more useful actions possible
        
        if self.current_step >= self.max_steps:
            return True
        
        if self.current_access_level == "root":
            return True
        
        if len(self.successful_exploits) >= len(self.target_info["vulnerabilities"]):
            return True
        
        return False
    
    def get_state_size(self) -> int:
        """Get state space size"""
        return self.state_size
    
    def get_action_size(self) -> int:
        """Get action space size"""
        return self.action_size
    
    def get_action_space(self) -> List[Dict[str, Any]]:
        """Get action space"""
        return self.action_space.copy()
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get information about the environment"""
        return {
            "max_steps": self.max_steps,
            "state_size": self.state_size,
            "action_size": self.action_size,
            "reward_success": self.reward_success,
            "reward_failure": self.reward_failure,
            "reward_discovery": self.reward_discovery,
            "reward_escalation": self.reward_escalation
        } 