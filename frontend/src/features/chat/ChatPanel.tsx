/**
 * ChatPanel Component
 *
 * 우측 사이드바 Chat 패널
 */
import React, { useEffect, useRef } from 'react';
import { X, MessageCircle, Trash2 } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useChat } from '../../hooks/useChat';
import { useChatStore } from '../../store/chatStore';

export const ChatPanel: React.FC = () => {
  const { messages, sendMessage, clearHistory, isLoading, isStreaming, error } =
    useChat();
  const { isChatPanelOpen, toggleChatPanel } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new message arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isChatPanelOpen) {
    // Minimized state - floating button
    return (
      <button
        onClick={toggleChatPanel}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600 transition-all flex items-center justify-center z-50"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div className="w-[400px] h-screen flex flex-col bg-white border-l border-gray-200 fixed right-0 top-0 z-40">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-blue-500 to-blue-600">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-white" />
          <h2 className="text-lg font-semibold text-white">AI 어시스턴트</h2>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={clearHistory}
            className="p-2 hover:bg-blue-700 rounded-lg transition-colors"
            title="대화 내역 삭제"
          >
            <Trash2 className="w-4 h-4 text-white" />
          </button>
          <button
            onClick={toggleChatPanel}
            className="p-2 hover:bg-blue-700 rounded-lg transition-colors"
            title="채팅 닫기"
          >
            <X className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <MessageCircle className="w-16 h-16 mb-4 text-gray-300" />
            <p className="text-sm">
              안녕하세요! 학생 관리 시스템 AI 어시스턴트입니다.
            </p>
            <p className="text-xs mt-2">
              학생 분석, 워크플로우 실행 등을 도와드립니다.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            <strong>오류:</strong> {error}
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={false} isLoading={isLoading} />

      {/* Streaming Indicator */}
      {isStreaming && (
        <div className="absolute top-20 right-4 bg-blue-100 border border-blue-300 rounded-lg px-3 py-2 text-xs text-blue-700 flex items-center gap-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          AI가 응답 중입니다...
        </div>
      )}
    </div>
  );
};
