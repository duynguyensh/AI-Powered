#!/usr/bin/env python3
"""
Example usage of the AI-Powered Penetration Testing Agent

This script demonstrates how to use the agent for authorized security testing.
Remember to only test systems you own or have explicit permission to test.
"""

import os
import sys
from loguru import logger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agent import PentestAgent


def main():
    """Main example function"""
    logger.info("AI-Powered Penetration Testing Agent - Example Usage")
    
    try:
        agent = PentestAgent("config/config.yaml")
        logger.info("Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return
    
    logger.info("\n=== Example 1: Basic Reconnaissance ===")
    try:
        target = agent.set_target("example.com", scope=["web"])
        
        recon_results = agent.recon_engine.run_comprehensive_recon(target)
        
        logger.info(f"Reconnaissance completed:")
        logger.info(f"  - IP Address: {recon_results.get('ip_address', 'Not found')}")
        logger.info(f"  - Open Ports: {len(recon_results.get('ports', []))}")
        logger.info(f"  - Services: {len(recon_results.get('services', {}))}")
        logger.info(f"  - Web Pages: {len(recon_results.get('web_pages', []))}")
        
    except Exception as e:
        logger.error(f"Reconnaissance failed: {e}")
    
    # Example 2: Focused testing on specific areas
    logger.info("\n=== Example 2: Focused Testing ===")
    try:
        # Run focused reconnaissance
        focused_results = agent.recon_engine.run_focused_recon(
            target, 
            focus_areas=["dns", "web"]
        )
        
        logger.info(f"Focused reconnaissance completed:")
        logger.info(f"  - Focus Areas: {focused_results.get('focus_areas', [])}")
        logger.info(f"  - Success Rate: {focused_results.get('successful_attempts', 0)}/{focused_results.get('total_attempts', 1)}")
        
    except Exception as e:
        logger.error(f"Focused testing failed: {e}")
    
    # Example 3: Get AI agent performance stats
    logger.info("\n=== Example 3: AI Agent Statistics ===")
    try:
        stats = agent.rl_agent.get_performance_stats()
        if stats:
            logger.info(f"AI Agent Performance:")
            logger.info(f"  - Total Episodes: {stats.get('total_episodes', 0)}")
            logger.info(f"  - Success Rate: {stats.get('success_rate', 0):.2%}")
            logger.info(f"  - Average Reward: {stats.get('average_reward', 0):.2f}")
        else:
            logger.info("No training data available yet")
            
    except Exception as e:
        logger.error(f"Failed to get AI stats: {e}")
    
    # Example 4: Safety manager demonstration
    logger.info("\n=== Example 4: Safety Features ===")
    try:
        safety_summary = agent.safety_manager.get_safety_summary()
        logger.info(f"Safety Summary:")
        logger.info(f"  - Emergency Stop: {safety_summary.get('emergency_stop_active', False)}")
        logger.info(f"  - Rate Limiting: {safety_summary.get('rate_limiting_enabled', False)}")
        logger.info(f"  - Safe Mode: {safety_summary.get('safe_mode_enabled', False)}")
        logger.info(f"  - Authorization Required: {safety_summary.get('authorization_required', False)}")
        
    except Exception as e:
        logger.error(f"Failed to get safety summary: {e}")
    
    # Example 5: Generate a simple report
    logger.info("\n=== Example 5: Report Generation ===")
    try:
        # Create a mock test result for demonstration
        mock_results = {
            "target": "example.com",
            "timestamp": 1234567890,
            "reconnaissance": {
                "ip_address": "93.184.216.34",
                "ports": [80, 443],
                "services": {"80": "http", "443": "https"},
                "successful_attempts": 3,
                "total_attempts": 3
            },
            "vulnerabilities": {
                "found_vulnerabilities": [],
                "successful_attempts": 0,
                "total_attempts": 1
            },
            "exploitation": {
                "successful_exploits": [],
                "successful_attempts": 0,
                "total_attempts": 0
            },
            "privilege_escalation": {
                "escalation_successful": False,
                "successful_attempts": 0,
                "total_attempts": 0
            },
            "attack_path": [],
            "success_rate": 0.75
        }
        
        # Generate report
        report_path = agent.report_generator.generate_report(
            mock_results,
            [],
            "example_report.html"
        )
        
        logger.info(f"Example report generated: {report_path}")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
    
    logger.info("\n=== Example Usage Complete ===")
    logger.info("Remember to:")
    logger.info("  - Only test systems you own or have permission to test")
    logger.info("  - Follow responsible disclosure practices")
    logger.info("  - Comply with all applicable laws and regulations")


if __name__ == "__main__":
    # Set up logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    main() 
