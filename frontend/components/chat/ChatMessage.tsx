import React, { useMemo } from 'react';
import { User, Bot, Info } from 'lucide-react';
import { Message } from '../../types.ts';
import ChartRenderer from '../charts/ChartRenderer.tsx';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = React.memo(({ message }) => {
  const isUser = message.role === 'user';
  const showChart = useMemo(() => message.chartData && message.chartData.type, [message.chartData]);

  return (
    <div className={`flex w-full group animate-slide-up ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex gap-3 max-w-[85%] md:max-w-[75%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
          isUser 
            ? 'bg-brand-100 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400' 
            : 'bg-brand-500 text-white'
        }`}>
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
        </div>

        <div className="flex flex-col gap-2">
          <div className={`px-4 py-3 rounded-2xl shadow-sm ${
            isUser 
              ? 'bg-brand-500 text-white rounded-tr-none' 
              : message.error 
                ? 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200 border border-red-100 dark:border-red-900/30' 
                : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-tl-none border border-slate-200 dark:border-slate-700'
          }`}>
            <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">{message.text}</p>
          </div>

          {showChart && message.chartData && (
            <div className="mt-2 w-full">
              <ChartRenderer chartData={message.chartData} />
            </div>
          )}

          {!isUser && message.query_executed && (
            <details className="mt-2">
              <summary className="text-[10px] text-slate-500 dark:text-slate-400 cursor-pointer hover:underline flex items-center gap-1 list-none">
                <Info className="w-3 h-3" /> Show technical query
              </summary>
              <div className="mt-2 p-2 bg-slate-900 rounded border border-slate-700">
                <code className="text-[11px] font-mono text-brand-300 break-all">
                  {message.query_executed}
                </code>
              </div>
            </details>
          )}
        </div>
      </div>
    </div>
  );
});

export default ChatMessage;