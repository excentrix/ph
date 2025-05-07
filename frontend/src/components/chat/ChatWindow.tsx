import React, { useEffect, useRef } from 'react';
import { useChatStore } from '@/store/chat-store';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export const ChatWindow: React.FC = () => {
  const { messages, isLoading, error, sendMessage, resetChat } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  return (
    <Card className="w-full h-[600px] max-w-3xl mx-auto flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>AI Student Mentor</CardTitle>
        <Button variant="outline" size="sm" onClick={resetChat}>
          New Chat
        </Button>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 h-full flex flex-col justify-center">
            <p>Send a message to start chatting with your AI Mentor</p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && (
              <div className="text-center text-gray-500 py-2">
                <p>AI Mentor is thinking...</p>
              </div>
            )}
            {error && (
              <div className="text-center text-red-500 py-2">
                <p>Error: {error}</p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </CardContent>
      
      <CardFooter className="border-t p-4">
        <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
      </CardFooter>
    </Card>
  );
};

export default ChatWindow;
