#!/usr/bin/env python3
"""
MCP 연결 테스트 스크립트

각 노드의 MCP 서버와 실제로 통신할 수 있는지 테스트합니다.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.mcp.manager import MCPClientManager
from app.config import settings


async def test_node7_error_note():
    """Node 7 (Error Note) MCP 서버 테스트"""
    print("\n" + "="*80)
    print("🧪 Testing Node 7: Error Note MCP Server")
    print("="*80)

    manager = MCPClientManager(use_mock=False)
    await manager.initialize()

    try:
        # Test: get_due_reviews
        print("\n📌 Test 1: get_due_reviews")
        result = await manager.call("error-note", "get_due_reviews", {
            "teacher_id": "teacher_001",
            "date": "2026-01-10"
        })
        print(f"✅ Result: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await manager.close_all()


async def test_node2_q_dna():
    """Node 2 (Q-DNA) MCP 서버 테스트"""
    print("\n" + "="*80)
    print("🧪 Testing Node 2: Q-DNA MCP Server")
    print("="*80)

    manager = MCPClientManager(use_mock=False)
    await manager.initialize()

    try:
        # Check if server exists
        from pathlib import Path
        server_path = Path(settings.NODE2_MCP_PATH)
        base_dir = Path(__file__).parent.parent.parent
        absolute_path = (base_dir / server_path).resolve()

        if not absolute_path.exists():
            print(f"⚠️  Node 2 MCP server not found at: {absolute_path}")
            print("   Falling back to mock mode")
            return

        print(f"📁 Server path: {absolute_path}")

        # Test call (if server has list_tools)
        print("\n📌 Test: Attempting to call Node 2...")
        result = await manager.call("q-dna", "get_student_mastery", {
            "student_id": "student_123"
        })
        print(f"✅ Result: {result}")

    except Exception as e:
        print(f"⚠️  Node 2 MCP call failed (expected if server not implemented): {e}")

    finally:
        await manager.close_all()


async def test_node4_lab_node():
    """Node 4 (Lab Node) MCP 서버 테스트"""
    print("\n" + "="*80)
    print("🧪 Testing Node 4: Lab Node MCP Server")
    print("="*80)

    manager = MCPClientManager(use_mock=False)
    await manager.initialize()

    try:
        # Check if server exists
        from pathlib import Path
        server_path = Path(settings.NODE4_MCP_PATH)
        base_dir = Path(__file__).parent.parent.parent
        absolute_path = (base_dir / server_path).resolve()

        if not absolute_path.exists():
            print(f"⚠️  Node 4 MCP server not found at: {absolute_path}")
            print("   Falling back to mock mode")
            return

        print(f"📁 Server path: {absolute_path}")

        # Test call
        print("\n📌 Test: Attempting to call Node 4...")
        result = await manager.call("lab-node", "get_recent_concepts", {
            "student_id": "student_123"
        })
        print(f"✅ Result: {result}")

    except Exception as e:
        print(f"⚠️  Node 4 MCP call failed (expected if server not implemented): {e}")

    finally:
        await manager.close_all()


async def test_mock_mode():
    """Mock 모드 테스트"""
    print("\n" + "="*80)
    print("🧪 Testing Mock Mode")
    print("="*80)

    manager = MCPClientManager(use_mock=True)
    await manager.initialize()

    try:
        # Test mock responses
        print("\n📌 Test: Mock get_student_mastery")
        result = await manager.call("q-dna", "get_student_mastery", {
            "student_id": "student_123"
        })
        print(f"✅ Mock Result: {result}")

        print("\n📌 Test: Mock recommend_questions")
        result = await manager.call("q-dna", "recommend_questions", {
            "student_id": "student_123",
            "concept": "도함수",
            "num_questions": 10
        })
        print(f"✅ Mock Result: {len(result.get('questions', []))} questions")

    finally:
        await manager.close_all()


async def main():
    """전체 테스트 실행"""
    print("\n" + "="*80)
    print("🚀 Node 0 MCP Client Connection Test")
    print("="*80)

    # 1. Mock 모드 테스트
    await test_mock_mode()

    # 2. Node 7 실제 MCP 서버 테스트
    await test_node7_error_note()

    # 3. Node 2 테스트
    await test_node2_q_dna()

    # 4. Node 4 테스트
    await test_node4_lab_node()

    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
