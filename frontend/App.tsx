import React from 'react';
import { ThemeProvider } from './context/ThemeContext.tsx';
import Header from './components/layout/Header.tsx';
import ChatWindow from './components/chat/ChatWindow.tsx';
import ChatInput from './components/chat/ChatInput.tsx';
import { useChat } from './hooks/useChat.ts';

const App: React.FC = () => {
  const { messages, loading, ask, clearChat } = useChat();

  const handleSuggestionClick = (suggestion: string) => {
    ask(suggestion);
  };

  return (
    <ThemeProvider>
      <div className="flex flex-col h-[100dvh] max-h-[100dvh] bg-white dark:bg-slate-950 transition-colors duration-300 overflow-hidden">
        <Header onClearChat={clearChat} />
        
        <main className="flex-1 flex flex-col relative overflow-hidden">
          <ChatWindow 
            messages={messages} 
            loading={loading} 
            onSuggestionClick={handleSuggestionClick} 
          />
          
          <div className="w-full max-w-4xl mx-auto px-4 pb-4 md:pb-8 relative z-20">
            {/* Gradient shadow to fade message bottom */}
            <div className="absolute -top-12 left-0 right-0 h-12 bg-gradient-to-t from-white dark:from-slate-950 to-transparent pointer-events-none" />
            
            <div className="relative">
              <ChatInput onSend={ask} disabled={loading} />
              <p className="text-[10px] md:text-xs text-center mt-2 text-slate-400 dark:text-slate-500 font-medium pb-[env(safe-area-inset-bottom,0px)]">
                CricketIQ can make mistakes. Verify important stats.
              </p>
            </div>
          </div>
        </main>
      </div>
    </ThemeProvider>
  );
};

export default App;