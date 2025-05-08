from typing import Dict, Any, List
from services.agent.base import BaseAgent, AgentResponse, agent_registry
from backend.services.mcp.server import mcp_registry, BasePattern
import logging

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """Coordinates interactions between agents and manages conversation flow."""
    
    def __init__(self):
        self.agent_registry = agent_registry
    
    async def classify_intent(self, message: str, context: Dict[str, Any]) -> str:
        """Classify the intent of a message to determine appropriate agent."""
        # This would be implemented with an intent classification model
        # For now, use a simple keyword-based approach
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ["grade", "course", "class", "study", "academic"]):
            return "AcademicAdvisor"
        elif any(keyword in message_lower for keyword in ["career", "job", "profession", "employment"]):
            return "CareerCounselor"
        elif any(keyword in message_lower for keyword in ["sad", "happy", "anxious", "stressed", "emotion", "feel"]):
            return "EmotionalSupport"
        elif any(keyword in message_lower for keyword in ["project", "assignment", "thesis", "research"]):
            return "ProjectMentor"
        else:
            return "AcademicAdvisor"  # Default to academic advisor
    
    async def select_agent(self, message: str, context: Dict[str, Any]) -> BaseAgent:
        """Select the appropriate agent based on message intent and context."""
        intent = await self.classify_intent(message, context)
        agent = self.agent_registry.get(intent)
        
        if not agent:
            logger.warning(f"No agent found for intent {intent}, falling back to default")
            # Fallback to first available agent
            agent = next(iter(self.agent_registry.agents.values()), None)
            
            if not agent:
                raise ValueError("No agents registered in the system")
        
        return agent
    
    async def select_mcp_pattern(self, message: str, context: Dict[str, Any], agent: BaseAgent) -> BasePattern:
        """Select appropriate MCP pattern based on message and agent."""
        # For now, we'll use a simple mapping approach
        # This would be enhanced with more sophisticated selection logic
        
        # Get available patterns
        patterns = mcp_registry.patterns
        
        # Default pattern selection logic based on agent type
        if agent.name == "AcademicAdvisor":
            pattern = patterns.get("AcademicProgressAnalysis")
        else:
            # Default to first available pattern if no specific match
            pattern = next(iter(patterns.values()), None)
            
        if not pattern:
            raise ValueError("No MCP patterns registered in the system")
            
        return pattern
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> AgentResponse:
        """Process message by selecting and using appropriate agent and MCP pattern."""
        try:
            # Select appropriate agent
            agent = await self.select_agent(message, context)
            logger.info(f"Selected agent: {agent.name}")
            
            # Select appropriate MCP pattern
            pattern = await self.select_mcp_pattern(message, context, agent)
            logger.info(f"Selected MCP pattern: {pattern.name}")
            
            # Add pattern to context for agent to use
            context["selected_pattern"] = pattern
            
            # Process message with selected agent
            response = await agent.process_message(message, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return AgentResponse(
                content=f"I'm sorry, I encountered an error while processing your message. "
                        f"Please try again or contact support if the issue persists.",
                metadata={"error": str(e)}
            )
