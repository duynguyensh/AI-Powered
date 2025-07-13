"""
Main Reconnaissance Engine for comprehensive target discovery
"""

import socket
import dns.resolver
import requests
from typing import Dict, List, Any, Optional
from loguru import logger
from urllib.parse import urljoin, urlparse

from .port_scanner import PortScanner
from .service_detector import ServiceDetector
from .web_crawler import WebCrawler
from .dns_enumeration import DNSEnumerator


class ReconnaissanceEngine:
    """
    Comprehensive reconnaissance engine
    
    Performs target discovery, port scanning, service detection,
    web crawling, and DNS enumeration to gather maximum information
    about the target.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the reconnaissance engine"""
        self.config = config
        self.port_scanner = PortScanner(config)
        self.service_detector = ServiceDetector(config)
        self.web_crawler = WebCrawler(config)
        self.dns_enumerator = DNSEnumerator(config)
        
        self.logger = logger
    
    def run_comprehensive_recon(self, target) -> Dict[str, Any]:
        """
        Run comprehensive reconnaissance on target
        
        Args:
            target: TestTarget object
            
        Returns:
            Dictionary with all reconnaissance results
        """
        self.logger.info(f"Starting comprehensive reconnaissance on {target.hostname}")
        
        results = {
            "target": target.hostname,
            "ip_address": None,
            "ports": [],
            "services": {},
            "web_pages": [],
            "subdomains": [],
            "dns_records": {},
            "whois_info": {},
            "successful_attempts": 0,
            "total_attempts": 0,
            "errors": []
        }
        
        try:
            # Step 1: Basic DNS resolution
            results["ip_address"] = self._resolve_ip(target.hostname)
            results["total_attempts"] += 1
            if results["ip_address"]:
                results["successful_attempts"] += 1
            
            # Step 2: DNS enumeration
            dns_results = self.dns_enumerator.enumerate_dns(target.hostname)
            results["dns_records"] = dns_results.get("records", {})
            results["subdomains"] = dns_results.get("subdomains", [])
            results["total_attempts"] += dns_results.get("total_attempts", 0)
            results["successful_attempts"] += dns_results.get("successful_attempts", 0)
            
            # Step 3: Port scanning
            if results["ip_address"]:
                port_results = self.port_scanner.scan_ports(results["ip_address"])
                results["ports"] = port_results.get("open_ports", [])
                results["total_attempts"] += port_results.get("total_attempts", 0)
                results["successful_attempts"] += port_results.get("successful_attempts", 0)
            
            # Step 4: Service detection
            if results["ports"]:
                service_results = self.service_detector.detect_services(
                    results["ip_address"], 
                    results["ports"]
                )
                results["services"] = service_results.get("services", {})
                results["total_attempts"] += service_results.get("total_attempts", 0)
                results["successful_attempts"] += service_results.get("successful_attempts", 0)
            
            # Step 5: Web crawling (if web services found)
            if self._has_web_services(results["services"]):
                web_results = self.web_crawler.crawl_target(target.hostname)
                results["web_pages"] = web_results.get("pages", [])
                results["total_attempts"] += web_results.get("total_attempts", 0)
                results["successful_attempts"] += web_results.get("successful_attempts", 0)
            
            # Step 6: WHOIS lookup
            whois_results = self._get_whois_info(target.hostname)
            results["whois_info"] = whois_results
            results["total_attempts"] += 1
            if whois_results:
                results["successful_attempts"] += 1
            
            self.logger.info(f"Reconnaissance completed. Found {len(results['ports'])} open ports, "
                           f"{len(results['services'])} services, {len(results['web_pages'])} web pages")
            
        except Exception as e:
            self.logger.error(f"Reconnaissance failed: {e}")
            results["errors"].append(str(e))
        
        return results
    
    def _resolve_ip(self, hostname: str) -> Optional[str]:
        """Resolve hostname to IP address"""
        try:
            ip_address = socket.gethostbyname(hostname)
            self.logger.debug(f"Resolved {hostname} to {ip_address}")
            return ip_address
        except socket.gaierror as e:
            self.logger.warning(f"Failed to resolve {hostname}: {e}")
            return None
    
    def _has_web_services(self, services: Dict[str, str]) -> bool:
        """Check if target has web services"""
        web_ports = [80, 443, 8080, 8443, 3000, 8000]
        for port, service in services.items():
            if int(port) in web_ports or "http" in service.lower():
                return True
        return False
    
    def _get_whois_info(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information for domain"""
        try:
            import whois
            w = whois.whois(domain)
            return {
                "registrar": w.registrar,
                "creation_date": str(w.creation_date),
                "expiration_date": str(w.expiration_date),
                "name_servers": w.name_servers,
                "status": w.status
            }
        except Exception as e:
            self.logger.warning(f"WHOIS lookup failed for {domain}: {e}")
            return {}
    
    def run_focused_recon(self, target, focus_areas: List[str]) -> Dict[str, Any]:
        """
        Run focused reconnaissance on specific areas
        
        Args:
            target: TestTarget object
            focus_areas: List of areas to focus on
            
        Returns:
            Dictionary with focused reconnaissance results
        """
        self.logger.info(f"Starting focused reconnaissance on {target.hostname} for areas: {focus_areas}")
        
        results = {
            "target": target.hostname,
            "focus_areas": focus_areas,
            "results": {},
            "successful_attempts": 0,
            "total_attempts": 0
        }
        
        for area in focus_areas:
            if area == "ports":
                ip = self._resolve_ip(target.hostname)
                if ip:
                    port_results = self.port_scanner.scan_ports(ip)
                    results["results"]["ports"] = port_results
                    results["total_attempts"] += port_results.get("total_attempts", 0)
                    results["successful_attempts"] += port_results.get("successful_attempts", 0)
            
            elif area == "dns":
                dns_results = self.dns_enumerator.enumerate_dns(target.hostname)
                results["results"]["dns"] = dns_results
                results["total_attempts"] += dns_results.get("total_attempts", 0)
                results["successful_attempts"] += dns_results.get("successful_attempts", 0)
            
            elif area == "web":
                web_results = self.web_crawler.crawl_target(target.hostname)
                results["results"]["web"] = web_results
                results["total_attempts"] += web_results.get("total_attempts", 0)
                results["successful_attempts"] += web_results.get("successful_attempts", 0)
        
        return results
    
    def get_recon_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of reconnaissance results"""
        return {
            "target": results.get("target"),
            "ip_resolved": bool(results.get("ip_address")),
            "open_ports": len(results.get("ports", [])),
            "services_discovered": len(results.get("services", {})),
            "web_pages_found": len(results.get("web_pages", [])),
            "subdomains_found": len(results.get("subdomains", [])),
            "success_rate": (results.get("successful_attempts", 0) / 
                           max(results.get("total_attempts", 1), 1)) * 100
        } 