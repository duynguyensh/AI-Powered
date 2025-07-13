"""
Reinforcement Learning Agent for Penetration Testing

Uses PPO (Proximal Policy Optimization) to learn optimal attack strategies
based on success rates, discovered vulnerabilities, and privilege escalation.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import time
from typing import Dict, List, Any, Tuple, Optional
from collections import deque
import random
from loguru import logger

from .models import PentestPolicyNetwork
from .environment import PentestEnvironment


class RLAgent:
    """
    Reinforcement Learning Agent for penetration testing strategy optimization
    
    Uses PPO algorithm to learn optimal sequences of reconnaissance, vulnerability
    scanning, exploitation, and privilege escalation actions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the RL agent"""
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Environment
        self.env = PentestEnvironment(config)
        
        # Networks
        self.policy_net = PentestPolicyNetwork(
            state_size=self.env.state_size,
            action_size=self.env.action_size,
            hidden_size=128
        ).to(self.device)
        
        self.value_net = PentestPolicyNetwork(
            state_size=self.env.state_size,
            action_size=1,  # Value function outputs single value
            hidden_size=128
        ).to(self.device)
        
        # Optimizers
        self.policy_optimizer = optim.Adam(
            self.policy_net.parameters(),
            lr=config["ai"]["rl_learning_rate"]
        )
        self.value_optimizer = optim.Adam(
            self.value_net.parameters(),
            lr=config["ai"]["rl_learning_rate"]
        )
        
        # Memory
        self.memory = deque(maxlen=config["ai"]["memory_size"])
        
        # Training parameters
        self.gamma = config["ai"]["gamma"]
        self.tau = config["ai"]["tau"]
        self.batch_size = config["ai"]["batch_size"]
        self.exploration_rate = config["ai"]["exploration_rate"]
        
        # Statistics
        self.episode_rewards = []
        self.successful_episodes = 0
        self.total_episodes = 0
        
        self.logger = logger
        self.logger.info(f"RL Agent initialized on device: {self.device}")
    
    def select_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select action based on current state
        
        Args:
            state: Current environment state
            
        Returns:
            Selected action dictionary
        """
        # Convert state to tensor
        state_tensor = self._state_to_tensor(state)
        
        # Get action probabilities from policy network
        with torch.no_grad():
            action_probs = self.policy_net(state_tensor)
        
        # Apply exploration
        if random.random() < self.exploration_rate:
            # Random action
            action_idx = random.randint(0, self.env.action_size - 1)
        else:
            # Greedy action
            action_idx = torch.argmax(action_probs).item()
        
        # Convert to action dictionary
        action = self.env.action_space[action_idx]
        
        self.logger.debug(f"Selected action: {action.get('name', 'Unknown')}")
        return action
    
    def update_model(self, state: Dict[str, Any], reward: float):
        """
        Update the model with new experience
        
        Args:
            state: Current state
            reward: Received reward
        """
        # Store experience in memory
        experience = {
            "state": state,
            "reward": reward,
            "timestamp": time.time()
        }
        self.memory.append(experience)
        
        # Train if enough samples
        if len(self.memory) >= self.batch_size:
            self._train_step()
    
    def _train_step(self):
        """Perform one training step"""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample batch from memory
        batch = random.sample(self.memory, self.batch_size)
        
        # Prepare training data
        states = []
        rewards = []
        
        for experience in batch:
            states.append(self._state_to_tensor(experience["state"]))
            rewards.append(experience["reward"])
        
        states = torch.stack(states).to(self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32).to(self.device)
        
        # Normalize rewards
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-8)
        
        # Update policy network
        self.policy_optimizer.zero_grad()
        action_probs = self.policy_net(states)
        
        # Calculate policy loss (simplified PPO)
        log_probs = torch.log(action_probs + 1e-8)
        policy_loss = -(log_probs * rewards.unsqueeze(1)).mean()
        policy_loss.backward()
        self.policy_optimizer.step()
        
        # Update value network
        self.value_optimizer.zero_grad()
        values = self.value_net(states).squeeze()
        value_loss = nn.MSELoss()(values, rewards)
        value_loss.backward()
        self.value_optimizer.step()
        
        self.logger.debug(f"Training step completed. Policy loss: {policy_loss.item():.4f}, "
                         f"Value loss: {value_loss.item():.4f}")
    
    def _state_to_tensor(self, state: Dict[str, Any]) -> torch.Tensor:
        """Convert state dictionary to tensor"""
        # Extract relevant features from state
        features = []
        
        # Target information
        features.append(1.0 if state.get("ip_resolved") else 0.0)
        features.append(len(state.get("discovered_ports", [])) / 100.0)  # Normalize
        features.append(len(state.get("discovered_services", {})) / 50.0)  # Normalize
        
        # Vulnerability information
        features.append(len(state.get("found_vulnerabilities", [])) / 20.0)  # Normalize
        
        # Exploitation status
        features.append(len(state.get("successful_exploits", [])) / 10.0)  # Normalize
        
        # Access level (one-hot encoding)
        access_level = state.get("current_access_level", "none")
        access_levels = ["none", "user", "admin", "root"]
        for level in access_levels:
            features.append(1.0 if access_level == level else 0.0)
        
        # Phase information (one-hot encoding)
        current_phase = state.get("current_phase", "initialized")
        phases = ["initialized", "reconnaissance", "vulnerability_scanning", 
                 "exploitation", "privilege_escalation"]
        for phase in phases:
            features.append(1.0 if current_phase == phase else 0.0)
        
        return torch.tensor(features, dtype=torch.float32).to(self.device)
    
    def train_episode(self, max_steps: int = 1000) -> Dict[str, Any]:
        """
        Train the agent for one episode
        
        Args:
            max_steps: Maximum steps per episode
            
        Returns:
            Episode results
        """
        state = self.env.reset()
        total_reward = 0
        steps = 0
        episode_actions = []
        
        for step in range(max_steps):
            # Select action
            action = self.select_action(state)
            episode_actions.append(action)
            
            # Execute action
            next_state, reward, done, info = self.env.step(action)
            
            # Update model
            self.update_model(state, reward)
            
            total_reward += reward
            state = next_state
            steps = step + 1
            
            if done:
                break
        
        # Update statistics
        self.episode_rewards.append(total_reward)
        self.total_episodes += 1
        
        if total_reward > 50:  # Threshold for successful episode
            self.successful_episodes += 1
        
        # Calculate success rate
        success_rate = self.successful_episodes / max(self.total_episodes, 1)
        
        episode_results = {
            "total_reward": total_reward,
            "steps": steps,
            "success": total_reward > 50,
            "success_rate": success_rate,
            "actions": episode_actions
        }
        
        self.logger.info(f"Episode {self.total_episodes}: Reward={total_reward:.2f}, "
                        f"Steps={steps}, Success Rate={success_rate:.2%}")
        
        return episode_results
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        torch.save({
            "policy_net_state_dict": self.policy_net.state_dict(),
            "value_net_state_dict": self.value_net.state_dict(),
            "policy_optimizer_state_dict": self.policy_optimizer.state_dict(),
            "value_optimizer_state_dict": self.value_optimizer.state_dict(),
            "episode_rewards": self.episode_rewards,
            "successful_episodes": self.successful_episodes,
            "total_episodes": self.total_episodes
        }, filepath)
        
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.policy_net.load_state_dict(checkpoint["policy_net_state_dict"])
        self.value_net.load_state_dict(checkpoint["value_net_state_dict"])
        self.policy_optimizer.load_state_dict(checkpoint["policy_optimizer_state_dict"])
        self.value_optimizer.load_state_dict(checkpoint["value_optimizer_state_dict"])
        
        self.episode_rewards = checkpoint.get("episode_rewards", [])
        self.successful_episodes = checkpoint.get("successful_episodes", 0)
        self.total_episodes = checkpoint.get("total_episodes", 0)
        
        self.logger.info(f"Model loaded from {filepath}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.episode_rewards:
            return {}
        
        recent_rewards = self.episode_rewards[-100:]  # Last 100 episodes
        
        return {
            "total_episodes": self.total_episodes,
            "successful_episodes": self.successful_episodes,
            "success_rate": self.successful_episodes / max(self.total_episodes, 1),
            "average_reward": np.mean(recent_rewards),
            "max_reward": max(self.episode_rewards),
            "min_reward": min(self.episode_rewards),
            "recent_avg_reward": np.mean(recent_rewards)
        }
    
    def adjust_exploration_rate(self, success_rate: float):
        """Adjust exploration rate based on success rate"""
        if success_rate > 0.8:
            # High success rate, reduce exploration
            self.exploration_rate = max(0.05, self.exploration_rate * 0.9)
        elif success_rate < 0.2:
            # Low success rate, increase exploration
            self.exploration_rate = min(0.5, self.exploration_rate * 1.1)
        
        self.logger.debug(f"Exploration rate adjusted to: {self.exploration_rate:.3f}")
    
    def get_action_confidence(self, state: Dict[str, Any]) -> float:
        """Get confidence level for the selected action"""
        state_tensor = self._state_to_tensor(state)
        
        with torch.no_grad():
            action_probs = self.policy_net(state_tensor)
            confidence = torch.max(action_probs).item()
        
        return confidence 