#!/usr/bin/env python3
"""
Node 7 MCP 서버와 직접 통신 테스트
"""
import asyncio
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_node7_direct():
    """Node 7 MCP 서버와 직접 연결"""
    print("\n" + "="*80)
    print("🧪 Direct Node 7 MCP Connection Test")
    print("="*80)

    # Node 7 서버 경로
    server_path = Path("/mnt/d/progress/mathesis/node7_error_note/backend/mcp_server.py")
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
            print(f"✅ Session initialized: {init_result}")

            # Tool 목록 조회
            print("\n📋 Listing available tools...")
            tools = await session.list_tools()
            print(f"✅ Available tools: {len(tools.tools)}")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description}")

            # Tool 호출 테스트
            print("\n🧪 Calling tool: get_due_reviews")
            result = await session.call_tool("get_due_reviews", {
                "teacher_id": "teacher_001",
                "date": "2026-01-10"
            })
            print(f"✅ Result: {result.content[0].text if result.content else 'No content'}")

            print("\n✅ Test completed successfully")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_node7_direct())
