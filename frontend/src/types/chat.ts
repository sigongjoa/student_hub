/**
 * Chat Types
 *
 * 대화형 Chat 인터페이스 타입 정의
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    workflow_id?: string;
    tools_used?: string[];
    execution_time?: number;
  };
}

export interface ChatSession {
  id: string;
  title?: string;
  messages: ChatMessage[];
  created_at: Date;
  updated_at: Date;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  stream?: boolean;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  metadata?: Record<string, any>;
}

export interface SSEChunk {
  content?: string;
  done?: boolean;
  session_id?: string;
  error?: string;
}
