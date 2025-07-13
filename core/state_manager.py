"""
State Manager for tracking penetration testing state
"""

import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class PentestState:
    """Represents the current state of a penetration test"""
    target_hostname: str
    current_phase: str  # reconnaissance, vulnerability_scanning, exploitation, privilege_escalation
    discovered_ports: List[int]
    discovered_services: Dict[str, str]
    found_vulnerabilities: List[Dict[str, Any]]
    successful_exploits: List[Dict[str, Any]]
    current_access_level: str  # none, user, admin, root
    attack_path: List[Dict[str, Any]]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return asdict(self)


class StateManager:
    """
    Manages the state of the penetration testing process
    
    Tracks discovered information, vulnerabilities, exploits, and current access level
    to provide context for AI decision making.
    """
    
    def __init__(self):
        """Initialize the state manager"""
        self.current_state: Optional[PentestState] = None
        self.state_history: List[PentestState] = []
        self.logger = logger
    
    def initialize_state(self, target_hostname: str) -> PentestState:
        """Initialize state for a new target"""
        self.current_state = PentestState(
            target_hostname=target_hostname,
            current_phase="initialized",
            discovered_ports=[],
            discovered_services={},
            found_vulnerabilities=[],
            successful_exploits=[],
            current_access_level="none",
            attack_path=[],
            timestamp=time.time()
        )
        
        self.logger.info(f"State initialized for target: {target_hostname}")
        return self.current_state
    
    def update_phase(self, phase: str):
        """Update the current testing phase"""
        if self.current_state:
            self.current_state.current_phase = phase
            self.current_state.timestamp = time.time()
            self.logger.info(f"Phase updated to: {phase}")
    
    def add_discovered_ports(self, ports: List[int]):
        """Add discovered ports to the state"""
        if self.current_state:
            for port in ports:
                if port not in self.current_state.discovered_ports:
                    self.current_state.discovered_ports.append(port)
            self.logger.debug(f"Added {len(ports)} ports to state")
    
    def add_discovered_services(self, services: Dict[str, str]):
        """Add discovered services to the state"""
        if self.current_state:
            self.current_state.discovered_services.update(services)
            self.logger.debug(f"Added {len(services)} services to state")
    
    def add_vulnerability(self, vulnerability: Dict[str, Any]):
        """Add a discovered vulnerability to the state"""
        if self.current_state:
            self.current_state.found_vulnerabilities.append(vulnerability)
            self.logger.info(f"Added vulnerability: {vulnerability.get('name', 'Unknown')}")
    
    def add_successful_exploit(self, exploit: Dict[str, Any]):
        """Add a successful exploit to the state"""
        if self.current_state:
            self.current_state.successful_exploits.append(exploit)
            self.logger.info(f"Added successful exploit: {exploit.get('name', 'Unknown')}")
    
    def update_access_level(self, access_level: str):
        """Update the current access level"""
        if self.current_state:
            self.current_state.current_access_level = access_level
            self.logger.info(f"Access level updated to: {access_level}")
    
    def add_attack_step(self, step: Dict[str, Any]):
        """Add a step to the attack path"""
        if self.current_state:
            step["timestamp"] = time.time()
            self.current_state.attack_path.append(step)
            self.logger.debug(f"Added attack step: {step.get('action', 'Unknown')}")
    
    def get_current_state(self) -> Optional[PentestState]:
        """Get the current state"""
        return self.current_state
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get current state as dictionary"""
        if self.current_state:
            return self.current_state.to_dict()
        return {}
    
    def get_discovered_ports(self) -> List[int]:
        """Get list of discovered ports"""
        if self.current_state:
            return self.current_state.discovered_ports.copy()
        return []
    
    def get_discovered_services(self) -> Dict[str, str]:
        """Get dictionary of discovered services"""
        if self.current_state:
            return self.current_state.discovered_services.copy()
        return {}
    
    def get_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Get list of discovered vulnerabilities"""
        if self.current_state:
            return self.current_state.found_vulnerabilities.copy()
        return []
    
    def get_successful_exploits(self) -> List[Dict[str, Any]]:
        """Get list of successful exploits"""
        if self.current_state:
            return self.current_state.successful_exploits.copy()
        return []
    
    def get_current_access_level(self) -> str:
        """Get current access level"""
        if self.current_state:
            return self.current_state.current_access_level
        return "none"
    
    def get_attack_path(self) -> List[Dict[str, Any]]:
        """Get the complete attack path"""
        if self.current_state:
            return self.current_state.attack_path.copy()
        return []
    
    def save_state(self, filepath: str = None):
        """Save current state to file"""
        if not self.current_state:
            self.logger.warning("No current state to save")
            return
        
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"data/state_{self.current_state.target_hostname}_{timestamp}.json"
        
        try:
            state_dict = self.current_state.to_dict()
            with open(filepath, 'w') as f:
                json.dump(state_dict, f, indent=2)
            self.logger.info(f"State saved to: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def load_state(self, filepath: str) -> bool:
        """Load state from file"""
        try:
            with open(filepath, 'r') as f:
                state_dict = json.load(f)
            
            self.current_state = PentestState(**state_dict)
            self.logger.info(f"State loaded from: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return False
    
    def create_state_snapshot(self) -> PentestState:
        """Create a snapshot of the current state"""
        if self.current_state:
            snapshot = PentestState(
                target_hostname=self.current_state.target_hostname,
                current_phase=self.current_state.current_phase,
                discovered_ports=self.current_state.discovered_ports.copy(),
                discovered_services=self.current_state.discovered_services.copy(),
                found_vulnerabilities=self.current_state.found_vulnerabilities.copy(),
                successful_exploits=self.current_state.successful_exploits.copy(),
                current_access_level=self.current_state.current_access_level,
                attack_path=self.current_state.attack_path.copy(),
                timestamp=time.time()
            )
            self.state_history.append(snapshot)
            return snapshot
        return None
    
    def get_state_history(self) -> List[PentestState]:
        """Get the state history"""
        return self.state_history.copy()
    
    def reset_state(self):
        """Reset the current state"""
        if self.current_state:
            self.state_history.append(self.current_state)
        self.current_state = None
        self.logger.info("State reset")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state"""
        if not self.current_state:
            return {}
        
        return {
            "target": self.current_state.target_hostname,
            "phase": self.current_state.current_phase,
            "ports_discovered": len(self.current_state.discovered_ports),
            "services_discovered": len(self.current_state.discovered_services),
            "vulnerabilities_found": len(self.current_state.found_vulnerabilities),
            "successful_exploits": len(self.current_state.successful_exploits),
            "access_level": self.current_state.current_access_level,
            "attack_steps": len(self.current_state.attack_path)
        } 