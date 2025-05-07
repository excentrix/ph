from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from services.agent import AgentCoordinator
from core.schemas.base import StandardResponse

router = APIRouter()
agent_coordinator = AgentCoordinator()

class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Role of the message sender (system, user, assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Chat session ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the message")

class ChatResponse(StandardResponse):
    """Chat response model."""
    data: Dict[str, Any] = {
        "message": None,
        "session_id": None
    }

class ChatHistoryResponse(StandardResponse):
    """Chat history response model."""
    data: Dict[str, Any] = {
        "session_id": None,
        "messages": []
    }

# In-memory message storage (would be replaced with database in production)
chat_sessions: Dict[str, List[ChatMessage]] = {}

async def update_context_from_history(session_id: str) -> Dict[str, Any]:
    """Update context from chat history."""
    if session_id not in chat_sessions:
        return {}
    
    context = {
        "chat_history": [
            {"role": msg.role, "content": msg.content}
            for msg in chat_sessions[session_id][-10:]  # Last 10 messages
        ]
    }
    
    return context

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks
) -> ChatResponse:
    """Send a message to the AI mentor."""
    try:
        # Initialize session if needed
        if request.session_id not in chat_sessions:
            chat_sessions[request.session_id] = []
        
        # Add user message to history
        user_message = ChatMessage(
            role="user",
            content=request.message,
            metadata={"session_id": request.session_id}
        )
        chat_sessions[request.session_id].append(user_message)
        
        # Update context with chat history
        context = await update_context_from_history(request.session_id)
        
        # Add user-provided context
        context.update(request.context)
        
        # Process message with agent coordinator
        response = await agent_coordinator.process_message(request.message, context)
        
        # Add assistant message to history
        assistant_message = ChatMessage(
            role="assistant",
            content=response.content,
            metadata=response.metadata
        )
        chat_sessions[request.session_id].append(assistant_message)
        
        # Schedule background tasks (e.g., updating memory, analytics)
        background_tasks.add_task(update_memory, request.session_id, user_message, assistant_message)
        
        return ChatResponse(
            success=True,
            message="Message processed successfully",
            data={
                "message": {
                    "content": response.content,
                    "metadata": response.metadata
                },
                "session_id": request.session_id
            }
        )
    
    except Exception as e:
        return ChatResponse(
            success=False,
            message=f"Error processing message: {str(e)}",
            data={
                "message": {
                    "content": "I apologize, but I encountered an error. Please try again.",
                    "metadata": {"error": str(e)}
                },
                "session_id": request.session_id
            }
        )

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str) -> ChatHistoryResponse:
    """Get chat history for a session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
    
    return ChatHistoryResponse(
        success=True,
        message="Chat history retrieved successfully",
        data={
            "session_id": session_id,
            "messages": [msg.model_dump() for msg in chat_sessions[session_id]]
        }
    )

async def update_memory(
    session_id: str, 
    user_message: ChatMessage, 
    assistant_message: ChatMessage
) -> None:
    """Background task to update memory systems."""
    # This would integrate with the memory service in a full implementation
    # For now, just a placeholder
    pass
