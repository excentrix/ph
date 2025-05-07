from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class MCPStep(BaseModel):
    """Represents a single step in an MCP reasoning process."""
    name: str
    description: str
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}

class MCPResult(BaseModel):
    """Result of an MCP execution with reasoning trace."""
    success: bool
    message: str = ""
    reasoning_trace: Dict[str, Any] = {}
    result: Optional[Dict[str, Any]] = None

class BasePattern(ABC):
    """Base class for all Modular Cognitive Patterns."""
    
    def __init__(self):
        self.name: str = self.__class__.__name__
        self.description: str = "Base cognitive pattern"
        self.steps: List[MCPStep] = []
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any], **kwargs) -> MCPResult:
        """Execute the pattern with given context and return result with reasoning trace."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get pattern metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "steps": [step.model_dump() for step in self.steps],
        }

class MCPRegistry:
    """Registry for MCP patterns."""
    
    def __init__(self):
        self.patterns: Dict[str, BasePattern] = {}
    
    def register(self, pattern: BasePattern) -> None:
        """Register a pattern in the registry."""
        self.patterns[pattern.name] = pattern
    
    def get(self, pattern_name: str) -> Optional[BasePattern]:
        """Get a pattern by name."""
        return self.patterns.get(pattern_name)
    
    def list_patterns(self) -> List[Dict[str, Any]]:
        """List all registered patterns with metadata."""
        return [pattern.get_metadata() for pattern in self.patterns.values()]

# Global registry instance
mcp_registry = MCPRegistry()
