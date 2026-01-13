/**
 * ChatMessage Component
 *
 * 개별 채팅 메시지 표시
 */
import React from 'react';
import { ChatMessage as ChatMessageType } from '../../types/chat';
import { User, Bot } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex gap-3 p-4 ${
        isUser ? 'bg-blue-50' : 'bg-gray-50'
      } rounded-lg`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-500' : 'bg-gray-700'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-sm text-gray-900">
            {isUser ? '선생님' : 'AI 어시스턴트'}
          </span>
          <span className="text-xs text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString('ko-KR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        <div className="text-sm text-gray-800 whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {/* Metadata (optional) */}
        {message.metadata && (
          <div className="mt-2 text-xs text-gray-500">
            {message.metadata.workflow_id && (
              <div>Workflow ID: {message.metadata.workflow_id}</div>
            )}
            {message.metadata.tools_used && (
              <div>Tools: {message.metadata.tools_used.join(', ')}</div>
            )}
            {message.metadata.execution_time && (
              <div>Execution time: {message.metadata.execution_time}ms</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
