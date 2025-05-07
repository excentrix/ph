from services.agent.base import agent_registry, BaseAgent, AgentResponse
from services.agent.coordinator import AgentCoordinator

# Import all agents to register them
from services.agent.agents.academic_advisor import AcademicAdvisorAgent

__all__ = ["agent_registry", "BaseAgent", "AgentResponse", "AgentCoordinator"]
