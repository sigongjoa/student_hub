"""
FastAPI Application

REST API 서버 (gRPC와 별도)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.routers import mastery, attempts, workflows, chat, workflows_templates, diagnosis

# FastAPI 앱 생성
app = FastAPI(
    title="Student Hub API",
    description="Node 0 - Student Hub REST API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(mastery.router)
app.include_router(attempts.router)
app.include_router(workflows.router)
app.include_router(chat.router)  # Chat API (Conversational System)
app.include_router(workflows_templates.router)  # Workflow Templates (Phase 3)
app.include_router(diagnosis.router)  # Cognitive Diagnosis (Node4 → Node0 → Node2)

# 정적 파일 경로
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# 정적 파일 서빙 (CSS, JS, images 등)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """홈 페이지"""
    if os.path.exists(os.path.join(STATIC_DIR, "index.html")):
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
    return {
        "service": "Student Hub API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/mastery/{student_id}/{concept}")
async def mastery_page(student_id: str, concept: str):
    """개별 숙련도 페이지"""
    return FileResponse(os.path.join(STATIC_DIR, "mastery.html"))


@app.get("/profile/{student_id}")
async def profile_page(student_id: str):
    """학생 프로파일 페이지"""
    return FileResponse(os.path.join(STATIC_DIR, "profile.html"))


@app.get("/weak-concepts/{student_id}")
async def weak_concepts_page(student_id: str):
    """약점 개념 페이지"""
    return FileResponse(os.path.join(STATIC_DIR, "weak-concepts.html"))


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


@app.get("/chat-test")
async def chat_test_page():
    """Chat 테스트 페이지"""
    return FileResponse(os.path.join(STATIC_DIR, "chat_test.html"))


@app.get("/workflow-builder")
async def workflow_builder_page():
    """Workflow Builder 페이지"""
    return FileResponse(os.path.join(STATIC_DIR, "workflow_builder.html"))


@app.get("/diagnosis-events")
async def diagnosis_events_page():
    """인지 진단 이벤트 로그 페이지"""
    return FileResponse(os.path.join(STATIC_DIR, "diagnosis_events.html"))
