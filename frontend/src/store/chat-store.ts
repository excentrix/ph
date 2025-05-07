import { create } from 'zustand';
import { ChatMessage, chatService } from '@/services/api';

interface ChatState {
  messages: ChatMessage[];
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
  
  sendMessage: (message: string) => Promise<void>;
  resetChat: () => void;
  loadChatHistory: (sessionId: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  sessionId: null,
  isLoading: false,
  error: null,
  
  sendMessage: async (message: string) => {
    try {
      set({ isLoading: true, error: null });
      
      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      };
      
      set(state => ({
        messages: [...state.messages, userMessage],
      }));
      
      // Send message to API
      const response = await chatService.sendMessage({
        message,
        session_id: get().sessionId || undefined,
      });
      
      // Update session ID if not set
      if (!get().sessionId) {
        set({ sessionId: response.data.session_id });
      }
      
      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.message.content,
        timestamp: new Date().toISOString(),
        metadata: response.data.message.metadata,
      };
      
      set(state => ({
        messages: [...state.messages, assistantMessage],
        isLoading: false,
      }));
      
    } catch (error) {
      console.error('Error sending message:', error);
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'An error occurred sending your message' 
      });
    }
  },
  
  resetChat: () => {
    set({
      messages: [],
      sessionId: null,
      isLoading: false,
      error: null,
    });
  },
  
  loadChatHistory: async (sessionId: string) => {
    try {
      set({ isLoading: true, error: null });
      
      const messages = await chatService.getChatHistory(sessionId);
      
      set({
        messages,
        sessionId,
        isLoading: false,
      });
      
    } catch (error) {
      console.error('Error loading chat history:', error);
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'An error occurred loading chat history' 
      });
    }
  },
}));
