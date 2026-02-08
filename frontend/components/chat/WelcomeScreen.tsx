import React from 'react';
import { BarChart3, TrendingUp, Target, Users, Award } from 'lucide-react';
import Container from '../layout/Container.tsx';

interface WelcomeScreenProps {
  onSuggestionClick: (suggestion: string) => void;
}

const suggestions = [
  { icon: TrendingUp, text: "Who scored the most runs in 2023?", color: "text-blue-500" },
  { icon: Target, text: "Which bowler took the most wickets?", color: "text-red-500" },
  { icon: Users, text: "Show me the top 5 run scorers", color: "text-green-500" },
  { icon: Award, text: "Who won the most Player of the Match awards?", color: "text-purple-500" },
];

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSuggestionClick }) => {
  return (
    <Container className="flex flex-col items-center justify-center min-h-[60vh] text-center px-6">
      <div className="w-20 h-20 bg-brand-50 dark:bg-brand-900/20 rounded-3xl flex items-center justify-center mb-6 border border-brand-100 dark:border-brand-900/30">
        <BarChart3 className="w-10 h-10 text-brand-500" />
      </div>
      
      <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-3">
        Welcome to CricketIQ
      </h2>
      <p className="text-slate-500 dark:text-slate-400 max-w-lg mb-10 leading-relaxed">
        Your AI-powered companion for T20I cricket statistics. Ask questions and get instant analysis with data visualizations.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
        {suggestions.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSuggestionClick(item.text)}
            className="flex items-center gap-4 p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-left hover:border-brand-500 dark:hover:border-brand-500 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all group"
          >
            <item.icon className={`w-5 h-5 ${item.color} group-hover:scale-110 transition-transform`} />
            <span className="text-sm font-medium text-slate-700 dark:text-slate-200">
              {item.text}
            </span>
          </button>
        ))}
      </div>
    </Container>
  );
};

export default WelcomeScreen;