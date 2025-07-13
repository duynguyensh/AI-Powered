"""
Main PentestAgent class - orchestrates the entire penetration testing process
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger
import yaml

from .state_manager import StateManager
from .action_executor import ActionExecutor
from modules.reconnaissance.recon_engine import ReconnaissanceEngine
from modules.vulnerability.scanner import VulnerabilityScanner
from modules.exploitation.exploit_engine import ExploitEngine
from modules.privilege.escalation import PrivilegeEscalation
from ai.rl_agent.rl_agent import RLAgent
from ai.strategy.strategy_optimizer import StrategyOptimizer
from reporting.report_generator import ReportGenerator
from config.safety_manager import SafetyManager


@dataclass
class TestTarget:
    """Represents a target for penetration testing"""
    hostname: str
    ip_address: Optional[str] = None
    ports: List[int] = None
    services: Dict[str, str] = None
    scope: List[str] = None
    
    def __post_init__(self):
        if self.ports is None:
            self.ports = []
        if self.services is None:
            self.services = {}
        if self.scope is None:
            self.scope = ["web", "network"]


class PentestAgent:
    """
    Main AI-Powered Penetration Testing Agent
    
    Orchestrates reconnaissance, vulnerability scanning, exploitation,
    and privilege escalation using reinforcement learning for strategy optimization.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the penetration testing agent"""
        self.config = self._load_config(config_path)
        self.safety_manager = SafetyManager(self.config)
        
        # Initialize core components
        self.state_manager = StateManager()
        self.action_executor = ActionExecutor()
        
        # Initialize testing modules
        self.recon_engine = ReconnaissanceEngine(self.config)
        self.vuln_scanner = VulnerabilityScanner(self.config)
        self.exploit_engine = ExploitEngine(self.config)
        self.privilege_escalation = PrivilegeEscalation(self.config)
        
        # Initialize AI components
        self.rl_agent = RLAgent(self.config)
        self.strategy_optimizer = StrategyOptimizer(self.config)
        
        # Initialize reporting
        self.report_generator = ReportGenerator(self.config)
        
        # Test state
        self.current_target: Optional[TestTarget] = None
        self.test_results: Dict[str, Any] = {}
        self.attack_path: List[Dict[str, Any]] = []
        
        logger.info("AI-Powered Penetration Testing Agent initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def set_target(self, target: str, scope: List[str] = None) -> TestTarget:
        """Set the target for penetration testing"""
        if scope is None:
            scope = ["web", "network"]
        
        self.current_target = TestTarget(
            hostname=target,
            scope=scope
        )
        
        logger.info(f"Target set: {target} with scope: {scope}")
        return self.current_target
    
    def run_autonomous_test(self, target: str = None, scope: List[str] = None) -> Dict[str, Any]:
        """
        Run a complete autonomous penetration test
        
        Args:
            target: Target hostname/IP
            scope: List of testing scopes
            
        Returns:
            Dictionary containing test results
        """
        if target:
            self.set_target(target, scope)
        
        if not self.current_target:
            raise ValueError("No target specified. Use set_target() first.")
        
        # Safety check
        if not self.safety_manager.verify_authorization(self.current_target.hostname):
            raise PermissionError("Authorization required for target testing")
        
        logger.info(f"Starting autonomous penetration test on {self.current_target.hostname}")
        
        try:
            # Phase 1: Reconnaissance
            recon_results = self._run_reconnaissance()
            
            # Phase 2: Vulnerability Assessment
            vuln_results = self._run_vulnerability_scanning()
            
            # Phase 3: Exploitation
            exploit_results = self._run_exploitation()
            
            # Phase 4: Privilege Escalation
            privilege_results = self._run_privilege_escalation()
            
            # Compile results
            self.test_results = {
                "target": self.current_target.hostname,
                "timestamp": time.time(),
                "reconnaissance": recon_results,
                "vulnerabilities": vuln_results,
                "exploitation": exploit_results,
                "privilege_escalation": privilege_results,
                "attack_path": self.attack_path,
                "success_rate": self._calculate_success_rate()
            }
            
            # Update AI model with results
            self._update_ai_model()
            
            logger.info("Autonomous penetration test completed successfully")
            return self.test_results
            
        except Exception as e:
            logger.error(f"Penetration test failed: {e}")
            raise
    
    def _run_reconnaissance(self) -> Dict[str, Any]:
        """Execute reconnaissance phase"""
        logger.info("Starting reconnaissance phase")
        
        recon_results = self.recon_engine.run_comprehensive_recon(self.current_target)
        
        # Update target with discovered information
        if recon_results.get("ip_address"):
            self.current_target.ip_address = recon_results["ip_address"]
        if recon_results.get("ports"):
            self.current_target.ports = recon_results["ports"]
        if recon_results.get("services"):
            self.current_target.services = recon_results["services"]
        
        # Record in attack path
        self.attack_path.append({
            "phase": "reconnaissance",
            "timestamp": time.time(),
            "results": recon_results
        })
        
        return recon_results
    
    def _run_vulnerability_scanning(self) -> Dict[str, Any]:
        """Execute vulnerability scanning phase"""
        logger.info("Starting vulnerability scanning phase")
        
        vuln_results = self.vuln_scanner.scan_target(self.current_target)
        
        # Record in attack path
        self.attack_path.append({
            "phase": "vulnerability_scanning",
            "timestamp": time.time(),
            "results": vuln_results
        })
        
        return vuln_results
    
    def _run_exploitation(self) -> Dict[str, Any]:
        """Execute exploitation phase"""
        logger.info("Starting exploitation phase")
        
        # Get current state for AI decision making
        current_state = self.state_manager.get_current_state()
        
        # Use RL agent to select optimal exploitation strategy
        exploit_strategy = self.rl_agent.select_action(current_state)
        
        exploit_results = self.exploit_engine.execute_exploits(
            self.current_target,
            exploit_strategy
        )
        
        # Record in attack path
        self.attack_path.append({
            "phase": "exploitation",
            "timestamp": time.time(),
            "strategy": exploit_strategy,
            "results": exploit_results
        })
        
        return exploit_results
    
    def _run_privilege_escalation(self) -> Dict[str, Any]:
        """Execute privilege escalation phase"""
        logger.info("Starting privilege escalation phase")
        
        privilege_results = self.privilege_escalation.attempt_escalation(
            self.current_target
        )
        
        # Record in attack path
        self.attack_path.append({
            "phase": "privilege_escalation",
            "timestamp": time.time(),
            "results": privilege_results
        })
        
        return privilege_results
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate of the test"""
        total_attempts = 0
        successful_attempts = 0
        
        for phase_result in self.attack_path:
            results = phase_result.get("results", {})
            if "successful_attempts" in results and "total_attempts" in results:
                total_attempts += results["total_attempts"]
                successful_attempts += results["successful_attempts"]
        
        if total_attempts == 0:
            return 0.0
        
        return successful_attempts / total_attempts
    
    def _update_ai_model(self):
        """Update the reinforcement learning model with test results"""
        try:
            # Prepare training data from test results
            state = self.state_manager.get_current_state()
            reward = self._calculate_reward()
            
            # Update the RL agent
            self.rl_agent.update_model(state, reward)
            
            # Optimize strategy
            self.strategy_optimizer.optimize_strategy(self.test_results)
            
            logger.info("AI model updated with test results")
        except Exception as e:
            logger.error(f"Failed to update AI model: {e}")
    
    def _calculate_reward(self) -> float:
        """Calculate reward for the RL agent based on test results"""
        reward = 0.0
        
        # Base reward for completing the test
        reward += 10.0
        
        # Reward for successful reconnaissance
        if self.test_results.get("reconnaissance", {}).get("successful_attempts", 0) > 0:
            reward += 5.0
        
        # Reward for finding vulnerabilities
        vuln_count = len(self.test_results.get("vulnerabilities", {}).get("found_vulnerabilities", []))
        reward += vuln_count * 2.0
        
        # Reward for successful exploitation
        if self.test_results.get("exploitation", {}).get("successful_exploits", 0) > 0:
            reward += 20.0
        
        # Reward for privilege escalation
        if self.test_results.get("privilege_escalation", {}).get("escalation_successful", False):
            reward += 30.0
        
        # Penalty for failures
        total_failures = sum([
            self.test_results.get("reconnaissance", {}).get("failed_attempts", 0),
            self.test_results.get("vulnerability_scanning", {}).get("failed_scans", 0),
            self.test_results.get("exploitation", {}).get("failed_exploits", 0)
        ])
        reward -= total_failures * 1.0
        
        return reward
    
    def generate_report(self, output_path: str = None) -> str:
        """Generate comprehensive penetration test report"""
        if not self.test_results:
            raise ValueError("No test results available. Run a test first.")
        
        if output_path is None:
            output_path = f"reports/pentest_report_{self.current_target.hostname}_{int(time.time())}.html"
        
        report_path = self.report_generator.generate_report(
            self.test_results,
            self.attack_path,
            output_path
        )
        
        logger.info(f"Report generated: {report_path}")
        return report_path
    
    def get_attack_path(self) -> List[Dict[str, Any]]:
        """Get the complete attack path"""
        return self.attack_path
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get a summary of the test results"""
        if not self.test_results:
            return {}
        
        return {
            "target": self.test_results.get("target"),
            "timestamp": self.test_results.get("timestamp"),
            "success_rate": self.test_results.get("success_rate"),
            "vulnerabilities_found": len(self.test_results.get("vulnerabilities", {}).get("found_vulnerabilities", [])),
            "successful_exploits": self.test_results.get("exploitation", {}).get("successful_exploits", 0),
            "privilege_escalation_successful": self.test_results.get("privilege_escalation", {}).get("escalation_successful", False)
        }
    
    def emergency_stop(self):
        """Emergency stop the current test"""
        logger.warning("Emergency stop initiated")
        
        # Stop all running processes
        self.action_executor.stop_all_processes()
        
        # Save current state
        self.state_manager.save_state()
        
        logger.info("Emergency stop completed") 