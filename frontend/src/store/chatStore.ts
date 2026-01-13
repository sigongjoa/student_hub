/**
 * Chat Store
 *
 * Zustand를 사용한 Chat 상태 관리
 */
import { create } from 'zustand';
import { ChatMessage, ChatSession } from '../types/chat';

interface ChatStore {
  // State
  currentSession: ChatSession | null;
  messages: ChatMessage[];
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  isChatPanelOpen: boolean;

  // Actions
  setCurrentSession: (session: ChatSession | null) => void;
  addMessage: (message: ChatMessage) => void;
  updateLastMessage: (content: string) => void;
  setLoading: (loading: boolean) => void;
  setStreaming: (streaming: boolean) => void;
  setError: (error: string | null) => void;
  toggleChatPanel: () => void;
  clearMessages: () => void;
  reset: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  // Initial state
  currentSession: null,
  messages: [],
  isLoading: false,
  isStreaming: false,
  error: null,
  isChatPanelOpen: true,

  // Actions
  setCurrentSession: (session) => set({ currentSession: session }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  updateLastMessage: (content) =>
    set((state) => {
      const messages = [...state.messages];
      const lastMessage = messages[messages.length - 1];

      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.content += content;
      }

      return { messages };
    }),

  setLoading: (loading) => set({ isLoading: loading }),

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  setError: (error) => set({ error }),

  toggleChatPanel: () =>
    set((state) => ({ isChatPanelOpen: !state.isChatPanelOpen })),

  clearMessages: () => set({ messages: [], error: null }),

  reset: () =>
    set({
      currentSession: null,
      messages: [],
      isLoading: false,
      isStreaming: false,
      error: null,
    }),
}));
