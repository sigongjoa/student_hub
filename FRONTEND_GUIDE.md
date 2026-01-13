# Frontend Guide - Chat Interface

**작성일**: 2026-01-13
**상태**: ✅ Phase 3 Week 1 - Chat UI 구현 완료

---

## 🎨 구현된 기능

### 1. Chat UI Components
- ✅ **ChatPanel** - 우측 사이드바 (400px, 토글 가능)
- ✅ **ChatMessage** - 메시지 표시 (사용자/AI 구분, 타임스탬프)
- ✅ **ChatInput** - 메시지 입력 (Suggestions, Enter to send)

### 2. State Management
- ✅ **Zustand Store** - Chat 상태 관리
  - 메시지 히스토리
  - 로딩/스트리밍 상태
  - Chat Panel 토글

### 3. SSE Streaming Client
- ✅ **useChat Hook** - Chat API 통신
  - Server-Sent Events (SSE) 스트리밍
  - 메시지 전송/수신
  - 에러 핸들링
  - 대화 히스토리 삭제

---

## 🚀 실행 방법

### 1. Backend 서버 확인
```bash
# FastAPI 서버 확인 (Port 8000)
curl http://localhost:8000/health

# Ollama 서버 확인
curl -X POST http://localhost:8000/api/v1/chat/test
```

### 2. Frontend 서버 시작
```bash
cd frontend
npm run dev
```

**서버 주소**: http://localhost:5173

### 3. 브라우저에서 접속
```
http://localhost:5173
```

우측 하단 또는 우측 사이드바에 **Chat Panel**이 표시됩니다.

---

## 🖥️ Chat UI 사용법

### Chat Panel 위치
- **Desktop (>1024px)**: 우측 사이드바 (400px)
- **최소화 상태**: 우측 하단 플로팅 버튼

### Chat 기능

#### 1. 메시지 전송
1. Chat Panel의 입력 필드에 메시지 입력
2. **Enter** 키로 전송 (Shift + Enter로 줄바꿈)
3. 또는 **Send 버튼** 클릭

#### 2. Suggestions 사용
Chat Panel 하단에 제안 메시지 버튼이 표시됩니다:
- "김철수의 약점 개념 알려줘"
- "이번 주 진단 문제 10개 추천해줘"
- "3반 전체 위험군 학생 찾아줘"

버튼 클릭 시 입력 필드에 자동으로 채워집니다.

#### 3. 실시간 스트리밍
AI 응답은 **SSE 스트리밍**으로 실시간 표시됩니다:
- 응답 중: "AI가 응답 중입니다..." 표시
- 글자 단위로 실시간 렌더링
- 자동 스크롤

#### 4. 대화 히스토리 관리
- **삭제**: Header의 휴지통 아이콘 클릭
- **닫기**: Header의 X 아이콘 클릭

---

## 📁 파일 구조

```
frontend/src/
├── features/chat/
│   ├── ChatPanel.tsx          # 메인 Chat UI
│   ├── ChatMessage.tsx        # 개별 메시지 컴포넌트
│   ├── ChatInput.tsx          # 입력 필드 컴포넌트
│   └── index.ts               # Exports
│
├── hooks/
│   └── useChat.ts             # Chat API & SSE 스트리밍 Hook
│
├── store/
│   └── chatStore.ts           # Zustand 상태 관리
│
├── types/
│   └── chat.ts                # Chat 타입 정의
│
└── App.tsx                    # ChatPanel 통합
```

---

## 🔧 주요 코드

### ChatPanel (우측 사이드바)
```tsx
// frontend/src/features/chat/ChatPanel.tsx
export const ChatPanel: React.FC = () => {
  const { messages, sendMessage, clearHistory, isLoading, isStreaming, error } =
    useChat();
  const { isChatPanelOpen, toggleChatPanel } = useChatStore();

  // Auto-scroll to bottom when new message arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="w-[400px] h-screen flex flex-col bg-white border-l border-gray-200 fixed right-0 top-0 z-40">
      {/* Header, Messages, Input */}
    </div>
  );
};
```

### useChat Hook (SSE 스트리밍)
```tsx
// frontend/src/hooks/useChat.ts
export const useChat = () => {
  const sendMessage = useCallback(async (message: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        stream: true,
      }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Parse SSE chunks
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const chunk: SSEChunk = JSON.parse(line.slice(6));
          if (chunk.content) {
            updateLastMessage(chunk.content);
          }
        }
      }
    }
  }, [sessionId, ...]);

  return { messages, sendMessage, isLoading, isStreaming, error };
};
```

### Chat Store (Zustand)
```tsx
// frontend/src/store/chatStore.ts
export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  isLoading: false,
  isStreaming: false,
  isChatPanelOpen: true,

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

  toggleChatPanel: () =>
    set((state) => ({ isChatPanelOpen: !state.isChatPanelOpen })),
}));
```

---

## 🧪 테스트 시나리오

### 1. 기본 메시지 전송 테스트
1. Frontend 접속: http://localhost:5173
2. Chat Panel 열기 (우측 사이드바 또는 플로팅 버튼)
3. 입력 필드에 "안녕하세요!" 입력
4. Enter 키 또는 Send 버튼 클릭
5. **예상 결과**:
   - 사용자 메시지 표시 (파란색 배경)
   - AI 응답 스트리밍 (회색 배경)
   - 자동 스크롤

### 2. Suggestions 버튼 테스트
1. "김철수의 약점 개념 알려줘" 버튼 클릭
2. 입력 필드에 자동 입력 확인
3. Send 클릭
4. **예상 결과**: AI 응답 수신

### 3. 스트리밍 테스트
1. "학생 관리 시스템의 주요 기능을 상세히 설명해주세요" 입력
2. **예상 결과**:
   - "AI가 응답 중입니다..." 표시
   - 글자 단위 실시간 렌더링
   - 응답 완료 후 표시 사라짐

### 4. 대화 히스토리 테스트
1. 여러 메시지 전송
2. Header의 휴지통 아이콘 클릭
3. **예상 결과**: 모든 메시지 삭제

### 5. Chat Panel 토글 테스트
1. Header의 X 아이콘 클릭
2. **예상 결과**: Chat Panel 최소화 (플로팅 버튼 표시)
3. 플로팅 버튼 클릭
4. **예상 결과**: Chat Panel 다시 열림

---

## 🎨 UI/UX 특징

### 반응형 디자인
- **Desktop (>1024px)**: 우측 사이드바 (400px)
- **최소화**: 우측 하단 플로팅 버튼

### 메시지 구분
- **사용자 메시지**: 파란색 배경, User 아이콘
- **AI 메시지**: 회색 배경, Bot 아이콘

### 타임스탬프
- 모든 메시지에 시간 표시 (HH:MM)

### 자동 스크롤
- 새 메시지 도착 시 자동으로 하단 스크롤

### 에러 표시
- API 에러 발생 시 빨간색 알림 표시

---

## 🔧 개발자 도구

### React Developer Tools
브라우저에서 React DevTools로 상태 확인:
- **Zustand Store**: `useChatStore` 상태
- **Component Tree**: ChatPanel → ChatMessage, ChatInput

### Network 탭
- **SSE 스트리밍**: `event-stream` 타입 확인
- **Payload**: 전송된 메시지 확인

### Console 로그
```javascript
// SSE 청크 파싱 실패 시 로그 출력
console.error('Failed to parse SSE chunk:', parseError);

// 에러 발생 시 로그 출력
console.error('Chat error:', error);
```

---

## 📊 성능 최적화

### 1. Auto-scroll 최적화
```tsx
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
}, [messages]);
```

### 2. Streaming 최적화
- **버퍼링**: 불완전한 라인은 다음 청크와 합침
- **Decoder 재사용**: TextDecoder stream 모드

### 3. State 최적화
- **Zustand**: 필요한 부분만 리렌더링
- **useCallback**: 함수 재생성 방지

---

## 🐛 트러블슈팅

### Q: Chat Panel이 표시되지 않습니다
**A**:
1. Frontend 서버가 실행 중인지 확인
2. 브라우저 콘솔에서 에러 확인
3. ChatPanel의 `z-index: 40` 확인

### Q: 메시지 전송이 안됩니다
**A**:
1. Backend API 서버 확인 (http://localhost:8000/health)
2. Network 탭에서 요청 확인
3. CORS 에러 확인

### Q: 스트리밍이 작동하지 않습니다
**A**:
1. Ollama 서버 확인 (`curl -X POST http://localhost:8000/api/v1/chat/test`)
2. Network 탭에서 `event-stream` 타입 확인
3. SSE 청크 파싱 에러 로그 확인

### Q: 자동 스크롤이 작동하지 않습니다
**A**:
1. `messagesEndRef`가 DOM에 렌더링되었는지 확인
2. useEffect dependencies 확인 (`[messages]`)

---

## 🎯 다음 단계

### Phase 3 Week 2: E2E Browser Tests
- [ ] Playwright 설정
- [ ] Chat UI E2E 테스트 작성
  - 메시지 전송 테스트
  - 스트리밍 테스트
  - Chat Panel 토글 테스트
  - 대화 히스토리 테스트
- [ ] CI/CD 통합

---

## 📚 참고 문서

- **설계 문서**: `docs/CONVERSATIONAL_SYSTEM_DESIGN.md`
- **Backend API**: `QUICKSTART.md`
- **Status**: `STATUS.md`

---

**작성자**: Claude Sonnet 4.5
**프로젝트**: Mathesis Node 0 Student Hub
**버전**: 1.0.0-phase3-week1
**Frontend URL**: http://localhost:5173
