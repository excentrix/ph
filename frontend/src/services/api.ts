import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp?: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  sessionId: string;
  messages: ChatMessage[];
}

// Update this to match your FastAPI ChatRequest model
export interface ChatRequest {
  messages: ChatMessage[];
  student_id?: string;
}

// Update this to match your FastAPI ChatResponse model
export interface ChatResponse {
  message: ChatMessage;
  metadata?: Record<string, any>;
}

export const chatService = {
  sendMessage: async (message: string, previousMessages: ChatMessage[] = []): Promise<ChatResponse> => {
    // Create the messages array with all previous messages plus the new one
    const messages: ChatMessage[] = [
      ...previousMessages,
      {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      }
    ];
    
    // Format the request according to what FastAPI expects
    const request: ChatRequest = {
      messages: messages,
      // You can add student_id here if needed
      // student_id: "1234"
    };
    
    const response = await api.post<ChatResponse>('/chat', request);
    return response.data;
  },
  
  getChatHistory: async (sessionId: string): Promise<ChatMessage[]> => {
    const response = await api.get(`/chat/history/${sessionId}`);
    return response.data.data.messages;
  },
};

export default api;