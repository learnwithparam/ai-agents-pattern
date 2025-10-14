#!/usr/bin/env python3
"""
45 - Cellular Automata Pattern
Decentralized agents with local interactions producing emergent behavior.

The Cellular Automata pattern implements a system of many simple, decentralized
grid-based agents whose local interactions produce complex, emergent global behavior.
This approach is particularly effective for spatial reasoning, logistics, complex
system simulation, and any domain where global patterns emerge from local rules.

This demonstrates:
1. Grid-based agent system with local interactions
2. Simple rules leading to complex emergent behavior
3. Self-organizing patterns and structures
4. Decentralized decision making
5. Emergent problem-solving capabilities
"""

import sys
import os
import json
import random
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class CellState(Enum):
    EMPTY = "empty"
    AGENT = "agent"
    RESOURCE = "resource"
    OBSTACLE = "obstacle"

@dataclass
class Cell:
    """Represents a single cell in the grid."""
    x: int
    y: int
    state: CellState
    agent_id: Optional[str] = None
    resource_count: int = 0
    energy: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Agent:
    """Represents an agent in the cellular automata."""
    agent_id: str
    x: int
    y: int
    energy: float
    state: str
    memory: List[Dict[str, Any]]
    goals: List[str]
    rules: List[str]
    
    def __post_init__(self):
        if self.memory is None:
            self.memory = []
        if self.goals is None:
            self.goals = []
        if self.rules is None:
            self.rules = []

class CellularAutomata:
    """Main cellular automata system."""
    
    def __init__(self, width: int, height: int, llm):
        self.width = width
        self.height = height
        self.llm = llm
        self.grid = self._initialize_grid()
        self.agents = {}
        self.tick = 0
        self.rules = {
            "movement": self._movement_rule,
            "resource_collection": self._resource_collection_rule,
            "agent_interaction": self._agent_interaction_rule,
            "energy_consumption": self._energy_consumption_rule
        }
    
    def _initialize_grid(self) -> List[List[Cell]]:
        """Initialize the grid with random cells."""
        grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                rand = random.random()
                if rand < 0.1:
                    state = CellState.RESOURCE
                    resource_count = random.randint(1, 5)
                elif rand < 0.15:
                    state = CellState.OBSTACLE
                    resource_count = 0
                else:
                    state = CellState.EMPTY
                    resource_count = 0
                
                cell = Cell(
                    x=x, y=y, state=state, resource_count=resource_count,
                    energy=random.uniform(0.0, 1.0)
                )
                row.append(cell)
            grid.append(row)
        return grid
    
    def add_agent(self, x: int, y: int, agent_id: str = None) -> Agent:
        """Add an agent to the grid."""
        if agent_id is None:
            agent_id = f"agent_{len(self.agents)}"
        
        if not self._is_valid_position(x, y) or self.grid[y][x].state != CellState.EMPTY:
            x, y = self._find_empty_position()
        
        agent = Agent(
            agent_id=agent_id, x=x, y=y, energy=random.uniform(50.0, 100.0),
            state="active", memory=[], goals=["survive", "collect_resources", "explore"],
            rules=["move_towards_resources", "avoid_obstacles", "interact_with_agents"]
        )
        
        self.agents[agent_id] = agent
        self.grid[y][x].state = CellState.AGENT
        self.grid[y][x].agent_id = agent_id
        
        return agent
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is valid."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def _find_empty_position(self) -> Tuple[int, int]:
        """Find an empty position for an agent."""
        for _ in range(100):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y][x].state == CellState.EMPTY:
                return x, y
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].state == CellState.EMPTY:
                    return x, y
        
        return 0, 0
    
    def _movement_rule(self, agent: Agent) -> Tuple[int, int]:
        """Rule for agent movement."""
        x, y = agent.x, agent.y
        best_dx, best_dy = 0, 0
        best_score = -1
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                if not self._is_valid_position(nx, ny):
                    continue
                
                cell = self.grid[ny][nx]
                score = self._calculate_movement_score(agent, cell, dx, dy)
                
                if score > best_score:
                    best_score = score
                    best_dx, best_dy = dx, dy
        
        return best_dx, best_dy
    
    def _calculate_movement_score(self, agent: Agent, cell: Cell, dx: int, dy: int) -> float:
        """Calculate score for moving to a cell."""
        score = 0.0
        
        if cell.state == CellState.RESOURCE:
            score += cell.resource_count * 10
        if cell.state == CellState.OBSTACLE:
            score -= 100
        if cell.state == CellState.AGENT:
            score -= 5
        if cell.state == CellState.EMPTY:
            score += 1
        
        score += random.uniform(-2, 2)
        return score
    
    def _resource_collection_rule(self, agent: Agent) -> bool:
        """Rule for resource collection."""
        cell = self.grid[agent.y][agent.x]
        
        if cell.state == CellState.RESOURCE and cell.resource_count > 0:
            collected = min(cell.resource_count, 2)
            cell.resource_count -= collected
            agent.energy += collected * 10
            
            agent.memory.append({
                "action": "collect_resource", "amount": collected, "tick": self.tick
            })
            
            if cell.resource_count == 0:
                cell.state = CellState.EMPTY
            
            return True
        
        return False
    
    def _agent_interaction_rule(self, agent: Agent) -> None:
        """Rule for agent interactions."""
        neighbors = self._get_neighbors(agent.x, agent.y)
        nearby_agents = [cell for cell in neighbors if cell.state == CellState.AGENT]
        
        if nearby_agents:
            for cell in nearby_agents:
                other_agent = self.agents[cell.agent_id]
                if other_agent.energy < agent.energy:
                    shared = min(5.0, agent.energy * 0.1)
                    agent.energy -= shared
                    other_agent.energy += shared
                    
                    agent.memory.append({
                        "action": "share_energy", "amount": shared,
                        "target": other_agent.agent_id, "tick": self.tick
                    })
    
    def _get_neighbors(self, x: int, y: int, radius: int = 1) -> List[Cell]:
        """Get neighboring cells."""
        neighbors = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self._is_valid_position(nx, ny):
                    neighbors.append(self.grid[ny][nx])
        return neighbors
    
    def _energy_consumption_rule(self, agent: Agent) -> None:
        """Rule for energy consumption."""
        agent.energy -= 1.0
        
        if len(agent.memory) > 0 and agent.memory[-1].get("action") == "move":
            agent.energy -= 0.5
        
        if agent.energy <= 0:
            agent.state = "dead"
            self.grid[agent.y][agent.x].state = CellState.EMPTY
            self.grid[agent.y][agent.x].agent_id = None
    
    def update(self) -> Dict[str, Any]:
        """Update the cellular automata for one tick."""
        self.tick += 1
        updates = []
        
        for agent in self.agents.values():
            if agent.state != "active":
                continue
            
            old_x, old_y = agent.x, agent.y
            
            # Movement
            dx, dy = self._movement_rule(agent)
            new_x, new_y = agent.x + dx, agent.y + dy
            
            if self._is_valid_position(new_x, new_y) and self.grid[new_y][new_x].state == CellState.EMPTY:
                self.grid[old_y][old_x].state = CellState.EMPTY
                self.grid[old_y][old_x].agent_id = None
                
                agent.x, agent.y = new_x, new_y
                self.grid[new_y][new_x].state = CellState.AGENT
                self.grid[new_y][new_x].agent_id = agent.agent_id
                
                agent.memory.append({
                    "action": "move", "from": (old_x, old_y),
                    "to": (new_x, new_y), "tick": self.tick
                })
            
            # Resource collection
            self._resource_collection_rule(agent)
            
            # Agent interaction
            self._agent_interaction_rule(agent)
            
            # Energy consumption
            self._energy_consumption_rule(agent)
            
            updates.append({
                "agent_id": agent.agent_id, "position": (agent.x, agent.y),
                "energy": agent.energy, "state": agent.state
            })
        
        return {
            "tick": self.tick, "updates": updates,
            "active_agents": len([a for a in self.agents.values() if a.state == "active"]),
            "total_agents": len(self.agents)
        }
    
    def print_grid(self) -> None:
        """Print the current state of the grid."""
        print("  " + "".join(f"{i:2}" for i in range(self.width)))
        for y in range(self.height):
            row = f"{y:2}"
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell.state == CellState.AGENT:
                    row += "🤖"
                elif cell.state == CellState.RESOURCE:
                    row += "💎"
                elif cell.state == CellState.OBSTACLE:
                    row += "🚧"
                else:
                    row += "⬜"
            print(row)

def main():
    print("🔬 Cellular Automata Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create cellular automata
    ca = CellularAutomata(width=8, height=8, llm=llm)
    
    # Add agents
    print("\n🤖 Adding agents...")
    for i in range(3):
        agent = ca.add_agent(0, 0)
        print(f"Added agent {agent.agent_id} at ({agent.x}, {agent.y})")
    
    # Run simulation
    print("\n🚀 Running simulation...")
    
    for tick in range(20):
        print(f"\n--- Tick {tick + 1} ---")
        
        update_result = ca.update()
        
        # Show agent updates
        for update in update_result['updates']:
            agent_id = update['agent_id']
            position = update['position']
            energy = update['energy']
            state = update['state']
            print(f"  {agent_id}: pos=({position[0]},{position[1]}) energy={energy:.1f} state={state}")
        
        print(f"Active agents: {update_result['active_agents']}")
        print(f"Total agents: {update_result['total_agents']}")
        
        # Show grid every 5 ticks
        if tick % 5 == 0:
            print("\nGrid state:")
            ca.print_grid()
        
        if update_result['active_agents'] == 0:
            print("\n💀 All agents have died!")
            break
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()
