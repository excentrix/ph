from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class AgentResponse(BaseModel):
    """Response from an agent."""
    content: str
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def process_message(self, 
                              message: str, 
                              context: Dict[str, Any],
                              **kwargs) -> AgentResponse:
        """Process a message and generate a response."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "name": self.name,
            "description": self.description,
        }

class AgentRegistry:
    """Registry for agents."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def register(self, agent: BaseAgent) -> None:
        """Register an agent in the registry."""
        self.agents[agent.name] = agent
    
    def get(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents with metadata."""
        return [agent.get_metadata() for agent in self.agents.values()]

# Global registry instance
agent_registry = AgentRegistry()
