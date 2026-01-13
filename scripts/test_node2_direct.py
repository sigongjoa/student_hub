#!/usr/bin/env python3
"""
Node 2 MCP 서버와 직접 통신 테스트
"""
import asyncio
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_node2_direct():
    """Node 2 MCP 서버와 직접 연결"""
    print("\n" + "="*80)
    print("🧪 Direct Node 2 (Q-DNA) MCP Connection Test")
    print("="*80)

    # Node 2 서버 경로
    server_path = Path("/mnt/d/progress/mathesis/node2_q_dna/backend/mcp_server.py")
    print(f"\n📁 Server path: {server_path}")
    print(f"✅ Exists: {server_path.exists()}")

    if not server_path.exists():
        print("❌ Server file not found!")
        return

    try:
        # stdio 서버 파라미터
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(server_path)],
        )

        print(f"\n🚀 Starting MCP client...")
        print(f"   Command: {server_params.command}")
        print(f"   Args: {server_params.args}")

        # stdio 클라이언트 시작 (async context manager)
        async with stdio_client(server_params) as (read, write):
            print("✅ stdio client started")

            # 세션 생성
            session = ClientSession(read, write)
            print("✅ Session created")

            # 초기화
            print("\n🔗 Initializing session...")
            init_result = await session.initialize()
            print(f"✅ Session initialized")

            # Tool 목록 조회
            print("\n📋 Listing available tools...")
            tools = await session.list_tools()
            print(f"✅ Available tools: {len(tools.tools)}")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description[:60]}...")

            # Test 1: get_student_mastery
            print("\n🧪 Test 1: get_student_mastery")
            result = await session.call_tool("get_student_mastery", {
                "student_id": "student_123"
            })
            print(f"✅ Result: {result.content[0].text[:200]}...")

            # Test 2: recommend_questions
            print("\n🧪 Test 2: recommend_questions")
            result = await session.call_tool("recommend_questions", {
                "student_id": "student_123",
                "concept": "도함수",
                "num_questions": 5
            })
            print(f"✅ Result: {result.content[0].text[:200]}...")

            # Test 3: get_question_dna
            print("\n🧪 Test 3: get_question_dna")
            result = await session.call_tool("get_question_dna", {
                "question_id": "q_001"
            })
            print(f"✅ Result: {result.content[0].text[:200]}...")

            # Test 4: estimate_learning_time
            print("\n🧪 Test 4: estimate_learning_time")
            result = await session.call_tool("estimate_learning_time", {
                "student_id": "student_123",
                "concept": "적분",
                "current_mastery": 0.45
            })
            print(f"✅ Result: {result.content[0].text[:200]}...")

            print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_node2_direct())
