from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio
from fastmcp import Client
from services.mcp import mcp_server
import logging
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings

logger = logging.getLogger(__name__)

import getpass
import os

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
# Create router
router = APIRouter()

# Initialize LangChain LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    # other parameters as needed
)

class ChatMessage(BaseModel):
    """Chat message model"""
    role: str
    content: str

class ChatRequest(BaseModel):
    """Chat request model"""
    messages: List[ChatMessage]
    student_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    message: ChatMessage
    metadata: Optional[Dict[str, Any]] = None
    
@router.get("/test")
async def test():
    """Test endpoint"""
    return {"message": "Hello, this is a test endpoint!"}

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return a response"""
    try:
        # Extract the latest user message
        if not request.messages or len(request.messages) == 0:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        latest_message = request.messages[-1]
        if latest_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")
        
        # Create context with student information if provided
        context = {}
        if request.student_id:
            # Use in-memory client to access student data
            async with Client(mcp_server) as client:
                # Retrieve student profile
                try:
                    profile_response = await client.read_resource(f"student://{request.student_id}/profile")
                    if profile_response and profile_response.content:
                        context["student_profile"] = profile_response.content
                    
                    # Retrieve student courses
                    courses_response = await client.read_resource(f"student://{request.student_id}/courses")
                    if courses_response and courses_response.content:
                        context["student_courses"] = courses_response.content
                except Exception as e:
                    logger.error(f"Error retrieving student data: {str(e)}")
        
        # Create conversation history
        conversation_history = []
        for msg in request.messages[:-1]:  # Exclude the latest message
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Determine which MCP pattern to use based on message content
        pattern_to_use = await determine_pattern(latest_message.content)
        
        # Process message using appropriate MCP pattern
        async with Client(mcp_server) as client:
            response = None
            
            # Try to process with identified pattern
            if pattern_to_use == "academic_progress":
                # If student courses are available, use them
                if "student_courses" in context:
                    response = await client.call_tool(
                        "analyze_academic_performance", 
                        {
                            "courses": context.get("student_courses", []),
                            "goals": context.get("student_profile", {}).get("career_goals", [])
                        }
                    )
            elif pattern_to_use == "career_guidance" and "student_profile" in context:
                # Use student profile for career guidance
                profile = context.get("student_profile", {})
                response = await client.call_tool(
                    "analyze_career_path",
                    {
                        "interests": profile.get("interests", []),
                        "skills": [],  # No skills in mock data
                        "courses": context.get("student_courses", []),
                        "career_goals": profile.get("career_goals", [])
                    }
                )
            
            # If pattern-specific processing failed or wasn't applicable, use LangChain
            if not response or not getattr(response, "text", None):
                # System message for LLM
                system_message_text = """
                You are an AI student mentor that provides academic advice, career guidance, 
                and educational support. Be helpful, encouraging, and provide specific, 
                actionable advice to students.
                """
                
                # Prepare a prompt that includes context if available
                prompt = latest_message.content
                if context:
                    # Add relevant context to help the LLM
                    context_str = json.dumps(context, indent=2)
                    full_prompt = f"""
                    Student message: {prompt}
                    
                    Context information:
                    {context_str}
                    
                    Provide a helpful, encouraging response that addresses the student's question
                    and incorporates relevant information from their profile and courses if appropriate.
                    """
                else:
                    full_prompt = prompt
                
                # Use LangChain to generate a response
                langchain_messages = [
                    SystemMessage(content=system_message_text),
                    HumanMessage(content=full_prompt)
                ]
                
                # Add conversation history if available
                # This would need more processing to convert to LangChain message format
                
                llm_response = await llm.ainvoke(langchain_messages)
                content = llm_response.content
            else:
                # Extract content from the MCP response
                if hasattr(response, "text"):
                    content = response.text
                elif hasattr(response, "content"):
                    # If it's a tool response with JSON content
                    if isinstance(response.content, dict):
                        # Use LangChain to format the JSON content into a natural language response
                        json_str = json.dumps(response.content, indent=2)
                        natural_prompt = f"""
                        I need to convert this JSON result into a natural, helpful response for a student:
                        
                        {json_str}
                        
                        Write a friendly, conversational response that includes the key insights and 
                        recommendations from this data.
                        """
                        
                        langchain_messages = [
                            SystemMessage(content="You are a helpful assistant that converts JSON data into natural language."),
                            HumanMessage(content=natural_prompt)
                        ]
                        
                        natural_response = await llm.ainvoke(langchain_messages)
                        content = natural_response.content
                    else:
                        content = str(response.content)
                else:
                    # Fallback response
                    content = "I'm sorry, I wasn't able to process your request properly. Could you please try again or rephrase your question?"
        
        return ChatResponse(
            message=ChatMessage(role="assistant", content=content),
            metadata={"pattern": pattern_to_use}
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Update your WebSocket endpoint similarly
@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat interactions"""
    await websocket.accept()
    
    try:
        async with Client(mcp_server) as client:
            while True:
                # Receive and parse message
                data = await websocket.receive_text()
                request_data = json.loads(data)
                
                message = request_data.get("message", "")
                student_id = request_data.get("student_id")
                
                # Create context with student information if provided
                context = {}
                if student_id:
                    # Retrieve student profile
                    try:
                        profile_response = await client.read_resource(f"student://{student_id}/profile")
                        if profile_response and profile_response.content:
                            context["student_profile"] = profile_response.content
                        
                        # Retrieve student courses
                        courses_response = await client.read_resource(f"student://{student_id}/courses")
                        if courses_response and courses_response.content:
                            context["student_courses"] = courses_response.content
                    except Exception as e:
                        logger.error(f"Error retrieving student data: {str(e)}")
                
                # Determine which MCP pattern to use based on message content
                pattern_to_use = await determine_pattern(message)
                
                # Process message with appropriate pattern
                response = None
                
                # Try to process with identified pattern
                if pattern_to_use == "academic_progress" and "student_courses" in context:
                    response = await client.call_tool(
                        "analyze_academic_performance", 
                        {
                            "courses": context.get("student_courses", []),
                            "goals": context.get("student_profile", {}).get("career_goals", [])
                        }
                    )
                elif pattern_to_use == "career_guidance" and "student_profile" in context:
                    profile = context.get("student_profile", {})
                    response = await client.call_tool(
                        "analyze_career_path",
                        {
                            "interests": profile.get("interests", []),
                            "skills": [],
                            "courses": context.get("student_courses", []),
                            "career_goals": profile.get("career_goals", [])
                        }
                    )
                
                # If pattern-specific processing failed or wasn't applicable, use LangChain
                if not response or not getattr(response, "text", None):
                    # System message for LLM
                    system_message_text = """
                    You are an AI student mentor that provides academic advice, career guidance, 
                    and educational support. Be helpful, encouraging, and provide specific, 
                    actionable advice to students.
                    """
                    
                    # Add context to prompt if available
                    if context:
                        context_str = json.dumps(context, indent=2)
                        full_prompt = f"""
                        Student message: {message}
                        
                        Context information:
                        {context_str}
                        
                        Provide a helpful, encouraging response that addresses the student's question
                        and incorporates relevant information from their profile and courses if appropriate.
                        """
                    else:
                        full_prompt = message
                    
                    # Use LangChain to generate a response
                    langchain_messages = [
                        SystemMessage(content=system_message_text),
                        HumanMessage(content=full_prompt)
                    ]
                    
                    llm_response = await llm.ainvoke(langchain_messages)
                    content = llm_response.content
                else:
                    # Extract content from the MCP response
                    if hasattr(response, "text"):
                        content = response.text
                    elif hasattr(response, "content"):
                        if isinstance(response.content, dict):
                            # Format JSON into natural language using LangChain
                            json_str = json.dumps(response.content, indent=2)
                            natural_prompt = f"""
                            I need to convert this JSON result into a natural, helpful response for a student:
                            
                            {json_str}
                            
                            Write a friendly, conversational response that includes the key insights and 
                            recommendations from this data.
                            """
                            
                            langchain_messages = [
                                SystemMessage(content="You are a helpful assistant that converts JSON data into natural language."),
                                HumanMessage(content=natural_prompt)
                            ]
                            
                            natural_response = await llm.ainvoke(langchain_messages)
                            content = natural_response.content
                        else:
                            content = str(response.content)
                    else:
                        content = "I'm sorry, I wasn't able to process your request properly. Could you please try again or rephrase your question?"
                
                # Send response
                await websocket.send_json({
                    "message": content,
                    "metadata": {"pattern": pattern_to_use}
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket endpoint: {str(e)}", exc_info=True)
        await websocket.close(code=1011, reason=f"Error: {str(e)}")

async def determine_pattern(message: str) -> str:
    """
    Determine which MCP pattern to use based on message content.
    
    Args:
        message: The user's message
        
    Returns:
        The name of the pattern to use
    """
    message_lower = message.lower()
    
    if any(keyword in message_lower for keyword in ["grade", "gpa", "performance", "academic", "study plan"]):
        print("Academic Progress Pattern")
        return "academic_progress"
    elif any(keyword in message_lower for keyword in ["career", "job", "profession", "future", "industry"]):
        print("Career Guidance Pattern")
        return "career_guidance"
    elif any(keyword in message_lower for keyword in ["schedule", "plan", "semester", "degree"]):
        print("Planning Pattern")
        return "planning"
    else:
        print("General Pattern")
        return "general"