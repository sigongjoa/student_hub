#!/usr/bin/env python3
"""
Seed test student data for UI testing
"""
import asyncio
import httpx

API_BASE = "http://localhost:8000/api/v1"

STUDENTS = [
    {"name": "김민수", "grade": 10, "school_id": "school_001"},
    {"name": "이서연", "grade": 11, "school_id": "school_001"},
    {"name": "박지훈", "grade": 9, "school_id": "school_001"},
    {"name": "최유진", "grade": 10, "school_id": "school_001"},
    {"name": "정현우", "grade": 11, "school_id": "school_001"},
]

async def seed_students():
    """Create test students via API"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🌱 Seeding test student data...")

        for student in STUDENTS:
            try:
                response = await client.post(
                    f"{API_BASE}/students",
                    json=student
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Created: {student['name']} (ID: {data.get('id', 'N/A')})")
                else:
                    print(f"❌ Failed to create {student['name']}: {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"❌ Error creating {student['name']}: {e}")

        # Verify students exist
        print("\n📊 Verifying student list...")
        try:
            response = await client.get(f"{API_BASE}/students")
            if response.status_code == 200:
                students = response.json()
                print(f"✅ Total students in database: {len(students)}")
                for s in students:
                    print(f"   - {s['name']} (Grade {s['grade']})")
            else:
                print(f"❌ Failed to fetch students: {response.status_code}")
        except Exception as e:
            print(f"❌ Error fetching students: {e}")

if __name__ == "__main__":
    asyncio.run(seed_students())
