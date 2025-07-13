"""
Web Crawler Module
"""

import requests
from typing import Dict, List, Any
from loguru import logger


class WebCrawler:
    """Basic web crawler for reconnaissance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logger
    
    def crawl_target(self, target: str) -> Dict[str, Any]:
        """Crawl web pages on target"""
        results = {
            "target": target,
            "pages": [],
            "total_attempts": 1,
            "successful_attempts": 0
        }
        
        try:
            # Try HTTP
            response = requests.get(f"http://{target}", timeout=5, verify=False)
            if response.status_code == 200:
                results["pages"].append({
                    "url": f"http://{target}",
                    "status_code": response.status_code,
                    "title": self._extract_title(response.text)
                })
                results["successful_attempts"] += 1
            
            # Try HTTPS
            response = requests.get(f"https://{target}", timeout=5, verify=False)
            if response.status_code == 200:
                results["pages"].append({
                    "url": f"https://{target}",
                    "status_code": response.status_code,
                    "title": self._extract_title(response.text)
                })
                results["successful_attempts"] += 1
                
        except Exception as e:
            self.logger.debug(f"Web crawling failed for {target}: {e}")
        
        return results
    
    def _extract_title(self, html: str) -> str:
        """Extract title from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title')
            return title.text if title else "No title"
        except:
            return "No title" 