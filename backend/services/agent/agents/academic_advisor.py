from typing import Dict, Any
from services.agent.base import BaseAgent, AgentResponse, agent_registry
from backend.services.mcp.server import BasePattern, MCPResult
import logging

logger = logging.getLogger(__name__)

class AcademicAdvisorAgent(BaseAgent):
    """Agent specialized in academic advising and educational guidance."""
    
    def __init__(self):
        super().__init__(
            name="AcademicAdvisor",
            description="Specialized in academic advising, course selection, and educational guidance"
        )
    
    async def process_message(self, 
                             message: str, 
                             context: Dict[str, Any],
                             **kwargs) -> AgentResponse:
        """Process a message and generate an academic advisor response."""
        try:
            # Get the selected pattern from context if available
            pattern: BasePattern = context.get("selected_pattern")
            
            if pattern:
                # Execute the pattern with context
                mcp_result: MCPResult = await pattern.execute(context)
                
                if mcp_result.success:
                    # Use the MCP reasoning results to generate response
                    response_content = await self._generate_response_from_mcp(message, mcp_result, context)
                else:
                    # Handle MCP execution failure
                    logger.warning(f"MCP execution failed: {mcp_result.message}")
                    response_content = await self._generate_fallback_response(message, context)
            else:
                # No pattern available, generate response directly
                response_content = await self._generate_fallback_response(message, context)
            
            return AgentResponse(
                content=response_content,
                metadata={
                    "agent": self.name,
                    "pattern_used": pattern.name if pattern else None
                }
            )
            
        except Exception as e:
            logger.error(f"Error in AcademicAdvisorAgent: {str(e)}", exc_info=True)
            return AgentResponse(
                content="I apologize, but I encountered an issue while processing your academic query. "
                        "Please try rephrasing your question or contact academic support for assistance.",
                metadata={"error": str(e)}
            )
    
    async def _generate_response_from_mcp(self, 
                                         message: str, 
                                         mcp_result: MCPResult, 
                                         context: Dict[str, Any]) -> str:
        """Generate a response based on MCP reasoning results."""
        # In a real implementation, this would use an LLM to generate a natural response
        # For now, we'll implement a simple template-based approach
        
        result = mcp_result.result or {}
        
        if "action_plan" in result:
            # Create a response focusing on the action plan
            action_plan = result["action_plan"]
            strengths = result.get("strengths", [])
            weaknesses = result.get("weaknesses", [])
            
            response = f"Based on my analysis of your academic performance, "
            
            if strengths:
                response += f"I can see you're doing well in {', '.join([s.get('subject', 'some subjects') for s in strengths[:2]])}. "
            
            if weaknesses:
                response += f"You might want to focus more on {', '.join([w.get('subject', 'certain subjects') for w in weaknesses[:2]])}. "
            
            response += "\n\nHere's an action plan to help you improve:\n"
            
            weekly_actions = action_plan.get("weekly_actions", [])
            if weekly_actions:
                for action in weekly_actions:
                    response += f"- {action.get('day')}: Focus on {action.get('focus')} with activities like {', '.join(action.get('activities', []))}\n"
            
            resources = action_plan.get("resources", [])
            if resources:
                response += "\nRecommended resources:\n"
                for resource in resources:
                    response += f"- {resource.get('name')}: {resource.get('url')}\n"
            
            return response
        else:
            # Generic response if no specific action plan is available
            return (
                "I've analyzed your academic situation and have some insights to share. "
                "To provide more specific guidance, could you tell me more about your "
                "current courses, grades, and what specific academic goals you have?"
            )
    
    async def _generate_fallback_response(self, 
                                         message: str, 
                                         context: Dict[str, Any]) -> str:
        """Generate a fallback response when MCP execution fails or is unavailable."""
        return (
            "I'm here to help with your academic questions and concerns. "
            "Could you provide more details about your current academic situation, "
            "such as your courses, grades, and any specific challenges you're facing? "
            "This will help me provide more tailored advice."
        )

# Register the agent
agent_registry.register(AcademicAdvisorAgent())
