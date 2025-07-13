"""
Report Generator for comprehensive penetration testing reports
"""

import os
import time
from typing import Dict, List, Any
from loguru import logger


class ReportGenerator:
    """Generate comprehensive penetration testing reports"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.reporting_config = config.get("reporting", {})
        self.logger = logger
    
    def generate_report(self, test_results: Dict[str, Any], attack_path: List[Dict[str, Any]], 
                       output_path: str = None) -> str:
        """Generate comprehensive penetration testing report"""
        
        if output_path is None:
            timestamp = int(time.time())
            target = test_results.get("target", "unknown")
            output_path = f"reports/pentest_report_{target}_{timestamp}.html"
        
        # Ensure reports directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate HTML report
        html_content = self._generate_html_report(test_results, attack_path)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Report generated: {output_path}")
        return output_path
    
    def _generate_html_report(self, test_results: Dict[str, Any], 
                            attack_path: List[Dict[str, Any]]) -> str:
        """Generate HTML report content"""
        
        target = test_results.get("target", "Unknown")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(test_results.get("timestamp", time.time())))
        success_rate = test_results.get("success_rate", 0) * 100
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Penetration Test Report - {target}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #007bff; margin: 0; }}
        .header p {{ color: #666; margin: 10px 0; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-left: 4px solid #007bff; padding-left: 15px; }}
        .summary-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .metric-label {{ color: #666; font-size: 14px; }}
        .vulnerability {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .vulnerability.high {{ background: #f8d7da; border-color: #f5c6cb; }}
        .vulnerability.medium {{ background: #fff3cd; border-color: #ffeaa7; }}
        .vulnerability.low {{ background: #d1ecf1; border-color: #bee5eb; }}
        .timeline {{ border-left: 3px solid #007bff; padding-left: 20px; margin: 20px 0; }}
        .timeline-item {{ margin-bottom: 15px; position: relative; }}
        .timeline-item::before {{ content: ''; position: absolute; left: -26px; top: 5px; width: 10px; height: 10px; background: #007bff; border-radius: 50%; }}
        .success-rate {{ font-size: 36px; font-weight: bold; color: #28a745; text-align: center; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI-Powered Penetration Test Report</h1>
            <p><strong>Target:</strong> {target}</p>
            <p><strong>Date:</strong> {timestamp}</p>
            <p><strong>Success Rate:</strong> <span class="success-rate">{success_rate:.1f}%</span></p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="summary-box">
                <p>This report presents the findings of an AI-powered penetration test conducted on {target}. 
                The test utilized advanced machine learning algorithms to autonomously discover vulnerabilities 
                and optimize attack strategies.</p>
                
                <div class="metric">
                    <div class="metric-value">{len(test_results.get('reconnaissance', {}).get('ports', []))}</div>
                    <div class="metric-label">Open Ports</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{len(test_results.get('vulnerabilities', {}).get('found_vulnerabilities', []))}</div>
                    <div class="metric-label">Vulnerabilities Found</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{len(test_results.get('exploitation', {}).get('successful_exploits', []))}</div>
                    <div class="metric-label">Successful Exploits</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Reconnaissance Results</h2>
            <div class="summary-box">
                <p><strong>IP Address:</strong> {test_results.get('reconnaissance', {}).get('ip_address', 'Not found')}</p>
                <p><strong>Open Ports:</strong> {', '.join(map(str, test_results.get('reconnaissance', {}).get('ports', []))) or 'None'}</p>
                <p><strong>Services Discovered:</strong> {len(test_results.get('reconnaissance', {}).get('services', {}))}</p>
                <p><strong>Web Pages Found:</strong> {len(test_results.get('reconnaissance', {}).get('web_pages', []))}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Vulnerabilities Discovered</h2>
            {self._generate_vulnerabilities_html(test_results)}
        </div>
        
        <div class="section">
            <h2>Exploitation Results</h2>
            <div class="summary-box">
                <p><strong>Successful Exploits:</strong> {len(test_results.get('exploitation', {}).get('successful_exploits', []))}</p>
                <p><strong>Privilege Escalation:</strong> {'Successful' if test_results.get('privilege_escalation', {}).get('escalation_successful', False) else 'Not attempted/Unsuccessful'}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Attack Timeline</h2>
            <div class="timeline">
                {self._generate_timeline_html(attack_path)}
            </div>
        </div>
        
        <div class="section">
            <h2>AI Insights</h2>
            <div class="summary-box">
                <p>The AI agent successfully learned and optimized its attack strategy throughout the testing process. 
                Key insights include:</p>
                <ul>
                    <li>Strategy optimization based on success rates</li>
                    <li>Adaptive reconnaissance techniques</li>
                    <li>Intelligent exploit selection</li>
                    <li>Dynamic privilege escalation attempts</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            <div class="summary-box">
                <p>Based on the findings, the following recommendations are provided:</p>
                <ul>
                    <li>Implement proper input validation and sanitization</li>
                    <li>Use strong authentication mechanisms</li>
                    <li>Keep software and systems updated</li>
                    <li>Implement network segmentation</li>
                    <li>Regular security assessments</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Report generated by AI-Powered Penetration Testing Agent</p>
            <p><em>This report is for authorized security testing purposes only.</em></p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def _generate_vulnerabilities_html(self, test_results: Dict[str, Any]) -> str:
        """Generate vulnerabilities section HTML"""
        vulnerabilities = test_results.get('vulnerabilities', {}).get('found_vulnerabilities', [])
        
        if not vulnerabilities:
            return '<div class="summary-box"><p>No vulnerabilities were discovered during this test.</p></div>'
        
        html = '<div class="summary-box">'
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'medium').lower()
            html += f'''
            <div class="vulnerability {severity}">
                <h4>{vuln.get('name', 'Unknown Vulnerability')}</h4>
                <p><strong>Severity:</strong> {vuln.get('severity', 'Unknown')}</p>
                <p><strong>Description:</strong> {vuln.get('description', 'No description available')}</p>
            </div>
            '''
        html += '</div>'
        return html
    
    def _generate_timeline_html(self, attack_path: List[Dict[str, Any]]) -> str:
        """Generate attack timeline HTML"""
        if not attack_path:
            return '<p>No attack steps recorded.</p>'
        
        html = ''
        for step in attack_path:
            phase = step.get('phase', 'Unknown')
            timestamp = time.strftime("%H:%M:%S", time.localtime(step.get('timestamp', 0)))
            html += f'''
            <div class="timeline-item">
                <strong>{timestamp}</strong> - {phase.replace('_', ' ').title()}
            </div>
            '''
        
        return html 