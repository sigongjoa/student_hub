/**
 * ChatInput Component
 *
 * 채팅 입력 필드
 */
import React, { useState, KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  disabled = false,
  isLoading = false,
  placeholder = '학생 분석, 워크플로우 실행, 질문하기...',
}) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled && !isLoading) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      {/* Suggestions */}
      <div className="mb-3 flex flex-wrap gap-2">
        {[
          '김철수의 약점 개념 알려줘',
          '이번 주 진단 문제 10개 추천해줘',
          '3반 전체 위험군 학생 찾아줘',
        ].map((suggestion, idx) => (
          <button
            key={idx}
            onClick={() => setMessage(suggestion)}
            className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors text-gray-700"
            disabled={disabled || isLoading}
          >
            {suggestion}
          </button>
        ))}
      </div>

      {/* Input Field */}
      <div className="flex gap-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          rows={3}
          className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed text-sm"
        />

        <button
          onClick={handleSend}
          disabled={disabled || isLoading || !message.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Hint */}
      <div className="mt-2 text-xs text-gray-500">
        <kbd className="px-2 py-0.5 bg-gray-100 border border-gray-300 rounded">
          Enter
        </kbd>{' '}
        to send,{' '}
        <kbd className="px-2 py-0.5 bg-gray-100 border border-gray-300 rounded">
          Shift + Enter
        </kbd>{' '}
        for new line
      </div>
    </div>
  );
};
