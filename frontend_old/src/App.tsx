import { ThemeProvider } from './context/ThemeContext';
import Header from './components/layout/Header';
import ChatWindow from './components/chat/ChatWindow';
import ChatInput from './components/chat/ChatInput';
import { useChat } from './hooks/useChat';

function ChatApp() {
  const { messages, loading, ask } = useChat();

  return (
    <div className="flex flex-col h-screen bg-[rgb(var(--bg-primary))] transition-colors duration-200">
      <Header />

      <main className="flex-1 overflow-hidden">
        <ChatWindow
          messages={messages}
          loading={loading}
          onSuggestionClick={ask}
        />
      </main>

      <footer className="border-t border-[rgb(var(--border))] bg-[rgb(var(--bg-secondary))]">
        <div className="max-w-4xl mx-auto">
          <ChatInput onSend={ask} disabled={loading} />
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <ChatApp />
    </ThemeProvider>
  );
}

export default App;
