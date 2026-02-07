import { ThemeProvider } from "./context/ThemeContext";
import { useTheme } from "./context/ThemeContext";
import { Moon, Sun, BarChart3 } from "lucide-react";

function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="border-b border-[rgb(var(--border))] bg-[rgb(var(--bg-secondary))] px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-[rgb(var(--accent))]" />
          <h1 className="text-xl font-bold">CricketIQ</h1>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-[rgb(var(--bg-tertiary))] transition-colors"
          aria-label="Toggle theme"
        >
          {theme === "dark" ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </button>
      </div>
    </header>
  );
}

function App() {
  return (
    <ThemeProvider>
      <div className="flex flex-col h-screen bg-[rgb(var(--bg-primary))] transition-colors duration-200">
        <Header />

        <main className="flex-1 overflow-hidden flex items-center justify-center">
          <div className="text-center">
            <BarChart3 className="w-16 h-16 text-[rgb(var(--accent))] mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-2">Welcome to CricketIQ</h2>
            <p className="text-[rgb(var(--text-secondary))] max-w-md">
              Ask any question about T20I cricket stats. Get instant, accurate answers
              powered by AI.
            </p>
          </div>
        </main>
      </div>
    </ThemeProvider>
  );
}

export default App;
