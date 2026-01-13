# Node 0 Student Hub - Quick Start Guide

**현재 상태**: ✅ Phase 1 Week 2 완료 - 모든 서비스 실행 중

---

## 🚀 실행 중인 서비스

모든 서비스가 현재 실행 중이며 정상 작동합니다:

| 서비스 | 포트 | 상태 | 설명 |
|--------|------|------|------|
| FastAPI Server | 8000 | ✅ Running | Chat API (SSE Streaming) |
| Ollama Server | 11434 | ✅ Running | LLM (llama3:latest) |
| Node 0 MCP Server | 50051 | ✅ Running | 5 Built-in MCP Tools |
| Node 2 Q-DNA | 50052 | ✅ Running | BKT Mastery + IRT Questions |
| Node 4 Lab Node | 50053 | ✅ Running | Student Activity Analytics |
| Node 7 Error Note | 50054 | ✅ Running | Error Analysis + Anki SM-2 |

---

## 🧪 테스트 방법

### 1. Health Check
```bash
curl http://localhost:8000/health
```
**예상 출력**:
```json
{"status":"healthy","ollama_url":"http://localhost:11434"}
```

### 2. Ollama 연결 확인
```bash
curl -X POST http://localhost:8000/api/v1/chat/test
```
**예상 출력**:
```json
{
  "status":"connected",
  "models":["llama3:latest",...],
  "current_model":"llama3:latest"
}
```

### 3. Chat API 테스트 (Non-streaming)
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요! 이 시스템에 대해 간단히 설명해주세요.",
    "stream": false
  }' | python3 -m json.tool
```

### 4. Chat API 테스트 (Streaming)
```bash
curl -N -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "간단히 답변해주세요: 주요 기능은?",
    "stream": true
  }'
```
**예상 출력**: SSE 스트리밍 응답
```
data: {"content": "학생"}
data: {"content": "의"}
data: {"content": " 약점"}
...
data: {"done": true, "session_id": "..."}
```

---

## 📝 Chat API 사용 예시

### Python 예시 (Non-streaming)
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/api/v1/chat/",
    json={
        "message": "학생 관리 시스템의 주요 기능을 설명해주세요.",
        "stream": False
    }
)

data = response.json()
print(f"AI 응답: {data['message']}")
print(f"Session ID: {data['session_id']}")
```

### Python 예시 (Streaming)
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/api/v1/chat/",
    json={
        "message": "안녕하세요!",
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data = json.loads(line_str[6:])
            if 'content' in data:
                print(data['content'], end='', flush=True)
            elif data.get('done'):
                print(f"\n\nSession ID: {data['session_id']}")
                break
```

### JavaScript 예시 (Streaming with EventSource)
```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/v1/chat/',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: '안녕하세요!',
      stream: true
    })
  }
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.content) {
    console.log(data.content);
  }

  if (data.done) {
    console.log('Session ID:', data.session_id);
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('EventSource error:', error);
  eventSource.close();
};
```

---

## 🔧 서비스 관리

### 모든 서비스 상태 확인
```bash
ps aux | grep -E "(ollama|grpc_services|uvicorn)" | grep -v grep
```

### 개별 서비스 로그 확인
```bash
# FastAPI 서버 로그
tail -f logs/api_server.log

# Node 2 (Q-DNA) 로그
tail -f logs/node2_qdna.log

# Node 4 (Lab Node) 로그
tail -f logs/node4_labnode.log

# Node 7 (Error Note) 로그
tail -f logs/node7_errornote.log

# Node 0 MCP 로그
tail -f logs/node0_mcp.log
```

### 서비스 재시작

#### FastAPI 서버 재시작
```bash
pkill -f "uvicorn app.api_server"
PYTHONPATH=/mnt/d/progress/mathesis/node0_student_hub \
  nohup uvicorn app.api_server:app --host 0.0.0.0 --port 8000 --reload \
  > logs/api_server.log 2>&1 &
```

#### Ollama 서버 재시작
```bash
pkill -f "ollama serve"
nohup ollama serve > /tmp/ollama.log 2>&1 &
```

#### gRPC MCP 서버들 재시작
```bash
pkill -f "grpc_services"
cd /mnt/d/progress/mathesis/node0_student_hub

PYTHONPATH=$PWD nohup python3 app/grpc_services/node2_qdna_server.py > logs/node2_qdna.log 2>&1 &
PYTHONPATH=$PWD nohup python3 app/grpc_services/node4_labnode_server.py > logs/node4_labnode.log 2>&1 &
PYTHONPATH=$PWD nohup python3 app/grpc_services/node7_errornote_server.py > logs/node7_errornote.log 2>&1 &
PYTHONPATH=$PWD nohup python3 app/grpc_services/node0_mcp_server.py > logs/node0_mcp.log 2>&1 &
```

---

## 🧪 통합 테스트 실행

### Chat API 테스트
```bash
pytest tests/integration/test_chat_api.py -v
```
**예상 결과**: 7 passed, 2 skipped

### gRPC MCP 서버 테스트
```bash
pytest tests/integration/test_weekly_diagnostic_service.py -v
```
**예상 결과**: 5 passed

### 모든 테스트 실행
```bash
pytest tests/ -v
```

---

## 📚 API 문서

FastAPI 서버를 실행한 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎯 다음 단계

### Phase 3 Week 1: React Frontend (예정)
1. React + Vite + TypeScript 프로젝트 생성
2. Tailwind CSS + shadcn/ui 설정
3. Chat 인터페이스 구현
   - ChatMessage 컴포넌트
   - ChatInput 컴포넌트
   - ChatHistory 컴포넌트
4. SSE 스트리밍 클라이언트 구현
5. Dashboard 레이아웃 구현

### Phase 3 Week 2: E2E Browser Tests (예정)
1. Playwright 설정
2. E2E 테스트 시나리오 작성
3. CI/CD 파이프라인 구성

---

## 🐛 트러블슈팅

### Q: Chat API가 응답하지 않습니다
**A**: Ollama 서버가 실행 중인지 확인하세요
```bash
curl http://localhost:11434/api/tags
```
실행 중이 아니면:
```bash
ollama serve &
```

### Q: "ModuleNotFoundError: No module named 'app'" 에러
**A**: PYTHONPATH를 설정하세요
```bash
export PYTHONPATH=/mnt/d/progress/mathesis/node0_student_hub
```

### Q: gRPC 서버가 응답하지 않습니다
**A**: 서버 로그를 확인하세요
```bash
tail -f logs/node*.log
```

### Q: Port already in use 에러
**A**: 이미 실행 중인 프로세스를 종료하세요
```bash
lsof -ti:8000 | xargs kill -9
```

---

## 📞 지원

- **프로젝트 문서**: `docs/CONVERSATIONAL_SYSTEM_DESIGN.md`
- **구현 상태**: `STATUS.md`
- **API 문서**: http://localhost:8000/docs

---

**작성일**: 2026-01-13
**버전**: 1.0.0-phase1-week2
**상태**: ✅ Production Ready (Phase 1)
