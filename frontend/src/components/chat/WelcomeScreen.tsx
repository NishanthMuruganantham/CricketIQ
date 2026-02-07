import { BarChart3, TrendingUp, Users, Target } from 'lucide-react';

interface WelcomeScreenProps {
    onSuggestionClick?: (question: string) => void;
}

const suggestions = [
    { icon: TrendingUp, text: 'Who scored the most runs in 2023?' },
    { icon: Target, text: 'Which bowler took the most wickets?' },
    { icon: Users, text: 'Show me the top 5 run scorers' },
    { icon: BarChart3, text: 'Who bowled the most dot balls?' },
];

export default function WelcomeScreen({ onSuggestionClick }: WelcomeScreenProps) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <BarChart3 className="w-16 h-16 text-[rgb(var(--accent))] mb-4" />
            <h2 className="text-3xl font-bold mb-2">Welcome to CricketIQ</h2>
            <p className="text-[rgb(var(--text-secondary))] mb-8 max-w-md">
                Ask any question about T20I cricket stats. Get instant, accurate answers
                powered by AI.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl w-full">
                {suggestions.map((suggestion, i) => (
                    <button
                        key={i}
                        onClick={() => onSuggestionClick?.(suggestion.text)}
                        className="flex items-center gap-3 p-4 rounded-xl bg-[rgb(var(--bg-secondary))]
                       border border-[rgb(var(--border))] hover:border-[rgb(var(--accent))]
                       transition-all text-left group"
                    >
                        <suggestion.icon className="w-5 h-5 text-[rgb(var(--text-secondary))] group-hover:text-[rgb(var(--accent))]" />
                        <span className="text-sm">{suggestion.text}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}
