import { useTheme } from '../../context/ThemeContext';
import { Moon, Sun, BarChart3 } from 'lucide-react';

export default function Header() {
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
                    {theme === 'dark' ? (
                        <Sun className="w-5 h-5" />
                    ) : (
                        <Moon className="w-5 h-5" />
                    )}
                </button>
            </div>
        </header>
    );
}
