import React, { useEffect, useRef } from 'react';
import { Message } from '../../types.ts';
import ChatMessage from './ChatMessage.tsx';
import TypingIndicator from './TypingIndicator.tsx';
import WelcomeScreen from './WelcomeScreen.tsx';
import Container from '../layout/Container.tsx';

interface ChatWindowProps {
  messages: Message[];
  loading: boolean;
  onSuggestionClick: (suggestion: string) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, loading, onSuggestionClick }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto pt-4 pb-32">
      {messages.length === 0 ? (
        <WelcomeScreen onSuggestionClick={onSuggestionClick} />
      ) : (
        <Container className="space-y-6">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} className="h-4" />
        </Container>
      )}
    </div>
  );
};

export default ChatWindow;