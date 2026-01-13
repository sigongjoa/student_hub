/**
 * useChat Hook
 *
 * Chat API와 SSE 스트리밍을 처리하는 커스텀 훅
 */
import { useState, useCallback, useRef } from 'react';
import { useChatStore } from '../store/chatStore';
import { ChatMessage, SSEChunk } from '../types/chat';

const API_BASE_URL = 'http://localhost:8000';

export const useChat = () => {
  const {
    messages,
    addMessage,
    updateLastMessage,
    setLoading,
    setStreaming,
    setError,
    currentSession,
    setCurrentSession,
  } = useChatStore();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Send message with streaming
   */
  const sendMessage = useCallback(
    async (message: string) => {
      if (!message.trim()) return;

      // Add user message
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: message,
        timestamp: new Date(),
      };
      addMessage(userMessage);

      // Create assistant message placeholder
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };
      addMessage(assistantMessage);

      setLoading(true);
      setStreaming(true);
      setError(null);

      // Create abort controller for cancellation
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/chat/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message,
            session_id: sessionId,
            stream: true,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('No response body');
        }

        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');

          // Process all complete lines
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);

              try {
                const chunk: SSEChunk = JSON.parse(data);

                if (chunk.content) {
                  updateLastMessage(chunk.content);
                }

                if (chunk.session_id && !sessionId) {
                  setSessionId(chunk.session_id);
                }

                if (chunk.done) {
                  setStreaming(false);
                  setLoading(false);
                }

                if (chunk.error) {
                  throw new Error(chunk.error);
                }
              } catch (parseError) {
                console.error('Failed to parse SSE chunk:', parseError);
              }
            }
          }
        }
      } catch (error: any) {
        if (error.name === 'AbortError') {
          console.log('Request cancelled');
        } else {
          console.error('Chat error:', error);
          setError(error.message || 'Failed to send message');
        }
      } finally {
        setLoading(false);
        setStreaming(false);
      }
    },
    [
      sessionId,
      addMessage,
      updateLastMessage,
      setLoading,
      setStreaming,
      setError,
    ]
  );

  /**
   * Cancel ongoing streaming
   */
  const cancelStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setStreaming(false);
      setLoading(false);
    }
  }, [setStreaming, setLoading]);

  /**
   * Clear chat history
   */
  const clearHistory = useCallback(async () => {
    if (sessionId) {
      try {
        await fetch(`${API_BASE_URL}/api/v1/chat/history/${sessionId}`, {
          method: 'DELETE',
        });
      } catch (error) {
        console.error('Failed to delete history:', error);
      }
    }

    useChatStore.getState().clearMessages();
    setSessionId(null);
  }, [sessionId]);

  return {
    messages,
    sessionId,
    sendMessage,
    cancelStreaming,
    clearHistory,
    isLoading: useChatStore((state) => state.isLoading),
    isStreaming: useChatStore((state) => state.isStreaming),
    error: useChatStore((state) => state.error),
  };
};
