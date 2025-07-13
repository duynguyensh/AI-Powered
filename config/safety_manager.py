"""
Safety Manager for ensuring ethical and authorized penetration testing
"""

import time
import hashlib
from typing import Dict, List, Any, Optional
from loguru import logger


class SafetyManager:
    """
    Safety Manager for ethical penetration testing
    
    Ensures proper authorization, rate limiting, and safety measures
    are in place before allowing any testing activities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the safety manager"""
        self.config = config
        self.safety_config = config.get("safety", {})
        
        self.authorized_targets = set()
        self.authorization_tokens = {}
        
        self.request_counts = {}
        self.last_request_time = {}
        
        self.emergency_stop_active = False
        self.emergency_stop_time = None
        
        self.audit_log = []
        
        self.logger = logger
        self.logger.info("Safety Manager initialized")
    
    def verify_authorization(self, target: str) -> bool:
        """
        Verify authorization for testing a target
        
        Args:
            target: Target hostname/IP
            
        Returns:
            True if authorized, False otherwise
        """
        if self.emergency_stop_active:
            self.logger.warning("Emergency stop active - authorization denied")
            return False
        
        if target in self.authorized_targets:
            self._log_audit_event("authorization_verified", target, "Target in authorized list")
            return True
        
        # Check for authorization token
        if target in self.authorization_tokens:
            token = self.authorization_tokens[target]
            if self._verify_token(token):
                self._log_audit_event("authorization_verified", target, "Valid token provided")
                return True
        
        # If authorization is required, deny access
        if self.safety_config.get("require_authorization", True):
            self.logger.warning(f"Authorization required for target: {target}")
            self._log_audit_event("authorization_denied", target, "No valid authorization")
            return False
        
        # If authorization not required, allow with warning
        self.logger.warning(f"No authorization provided for target: {target} - proceeding with caution")
        self._log_audit_event("authorization_bypassed", target, "Authorization not required")
        return True
    
    def add_authorized_target(self, target: str, reason: str = ""):
        """Add target to authorized list"""
        self.authorized_targets.add(target)
        self._log_audit_event("target_authorized", target, reason)
        self.logger.info(f"Target {target} added to authorized list")
    
    def remove_authorized_target(self, target: str):
        """Remove target from authorized list"""
        self.authorized_targets.discard(target)
        self._log_audit_event("target_deauthorized", target, "Removed from authorized list")
        self.logger.info(f"Target {target} removed from authorized list")
    
    def generate_authorization_token(self, target: str, expiry_hours: int = 24) -> str:
        """Generate authorization token for target"""
        import secrets
        
        token = secrets.token_urlsafe(32)
        expiry_time = time.time() + (expiry_hours * 3600)
        
        self.authorization_tokens[target] = {
            "token": token,
            "expiry": expiry_time,
            "created": time.time()
        }
        
        self._log_audit_event("token_generated", target, f"Expires in {expiry_hours} hours")
        self.logger.info(f"Authorization token generated for {target}")
        
        return token
    
    def _verify_token(self, token_info: Dict[str, Any]) -> bool:
        """Verify authorization token"""
        if time.time() > token_info["expiry"]:
            return False
        return True
    
    def check_rate_limit(self, target: str) -> bool:
        """
        Check if request is within rate limits
        
        Args:
            target: Target hostname/IP
            
        Returns:
            True if within limits, False otherwise
        """
        if not self.safety_config.get("rate_limiting", True):
            return True
        
        current_time = time.time()
        max_requests = self.safety_config.get("max_requests_per_minute", 60)
        
        # Initialize counters if not present
        if target not in self.request_counts:
            self.request_counts[target] = 0
            self.last_request_time[target] = current_time
        
        # Reset counter if minute has passed
        if current_time - self.last_request_time[target] >= 60:
            self.request_counts[target] = 0
            self.last_request_time[target] = current_time
        
        # Check if limit exceeded
        if self.request_counts[target] >= max_requests:
            self.logger.warning(f"Rate limit exceeded for target: {target}")
            self._log_audit_event("rate_limit_exceeded", target, f"Limit: {max_requests}/min")
            return False
        
        # Increment counter
        self.request_counts[target] += 1
        return True
    
    def emergency_stop(self, reason: str = ""):
        """Activate emergency stop"""
        self.emergency_stop_active = True
        self.emergency_stop_time = time.time()
        
        self._log_audit_event("emergency_stop", "SYSTEM", reason)
        self.logger.critical(f"EMERGENCY STOP ACTIVATED: {reason}")
    
    def emergency_stop_reset(self):
        """Reset emergency stop"""
        self.emergency_stop_active = False
        self.emergency_stop_time = None
        
        self._log_audit_event("emergency_stop_reset", "SYSTEM", "Emergency stop deactivated")
        self.logger.info("Emergency stop reset")
    
    def is_emergency_stop_active(self) -> bool:
        """Check if emergency stop is active"""
        return self.emergency_stop_active
    
    def check_safe_mode(self) -> bool:
        """Check if safe mode is enabled"""
        return self.safety_config.get("safe_mode", True)
    
    def validate_target(self, target: str) -> Dict[str, Any]:
        """
        Validate target for safety
        
        Args:
            target: Target hostname/IP
            
        Returns:
            Validation results
        """
        validation_results = {
            "target": target,
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check for localhost/private IPs
        if target in ["localhost", "127.0.0.1", "::1"]:
            validation_results["warnings"].append("Testing localhost - ensure this is intended")
        
        # Check for common private IP ranges
        if target.startswith(("192.168.", "10.", "172.")):
            validation_results["warnings"].append("Private IP range detected")
        
        # Check for common test domains
        test_domains = ["example.com", "test.com", "localhost", "127.0.0.1"]
        if target in test_domains:
            validation_results["warnings"].append("Test domain detected")
        
        # Check for potentially dangerous targets
        dangerous_patterns = ["prod", "production", "live", "critical"]
        if any(pattern in target.lower() for pattern in dangerous_patterns):
            validation_results["warnings"].append("Potentially production target detected")
        
        return validation_results
    
    def _log_audit_event(self, event_type: str, target: str, details: str):
        """Log audit event"""
        audit_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "target": target,
            "details": details
        }
        
        self.audit_log.append(audit_entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        return self.audit_log[-limit:]
    
    def get_safety_summary(self) -> Dict[str, Any]:
        """Get safety summary"""
        return {
            "emergency_stop_active": self.emergency_stop_active,
            "authorized_targets_count": len(self.authorized_targets),
            "rate_limiting_enabled": self.safety_config.get("rate_limiting", True),
            "safe_mode_enabled": self.safety_config.get("safe_mode", True),
            "audit_log_entries": len(self.audit_log),
            "authorization_required": self.safety_config.get("require_authorization", True)
        }
    
    def export_audit_log(self, filepath: str):
        """Export audit log to file"""
        import json
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.audit_log, f, indent=2)
            self.logger.info(f"Audit log exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to export audit log: {e}")
    
    def clear_audit_log(self):
        """Clear audit log"""
        self.audit_log.clear()
        self.logger.info("Audit log cleared") 
