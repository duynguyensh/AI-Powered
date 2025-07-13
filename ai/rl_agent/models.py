"""
Neural Network Models for Reinforcement Learning Agent
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class PentestPolicyNetwork(nn.Module):
    """
    Policy network for penetration testing actions
    
    Takes state as input and outputs action probabilities
    """
    
    def __init__(self, state_size: int, action_size: int, hidden_size: int = 128):
        super(PentestPolicyNetwork, self).__init__()
        
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, action_size)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network"""
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.softmax(self.fc3(x), dim=-1)
        return x


class PentestValueNetwork(nn.Module):
    """
    Value network for estimating state values
    
    Takes state as input and outputs value estimate
    """
    
    def __init__(self, state_size: int, hidden_size: int = 128):
        super(PentestValueNetwork, self).__init__()
        
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network"""
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x


class PentestActorCritic(nn.Module):
    """
    Actor-Critic network combining policy and value functions
    """
    
    def __init__(self, state_size: int, action_size: int, hidden_size: int = 128):
        super(PentestActorCritic, self).__init__()
        
        # Shared layers
        self.shared_fc1 = nn.Linear(state_size, hidden_size)
        self.shared_fc2 = nn.Linear(hidden_size, hidden_size)
        
        # Actor (policy) head
        self.actor_fc = nn.Linear(hidden_size, action_size)
        
        # Critic (value) head
        self.critic_fc = nn.Linear(hidden_size, 1)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass through the network"""
        # Shared layers
        x = F.relu(self.shared_fc1(x))
        x = self.dropout(x)
        x = F.relu(self.shared_fc2(x))
        x = self.dropout(x)
        
        # Actor head
        actor_output = F.softmax(self.actor_fc(x), dim=-1)
        
        # Critic head
        critic_output = self.critic_fc(x)
        
        return actor_output, critic_output
    
    def get_action_probs(self, x: torch.Tensor) -> torch.Tensor:
        """Get action probabilities only"""
        actor_output, _ = self.forward(x)
        return actor_output
    
    def get_value(self, x: torch.Tensor) -> torch.Tensor:
        """Get value estimate only"""
        _, critic_output = self.forward(x)
        return critic_output 