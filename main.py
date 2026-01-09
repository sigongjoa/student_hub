from fastapi import FastAPI, HTTPException
from node0_student_hub.mcp_server import StudentHubMCPServer
from node0_student_hub.models.schemas import (
    GetUnifiedProfileInput, CreateInterventionInput, SchedulePeriodicTaskInput,
    GetClassAnalyticsInput, Student
)

app = FastAPI(title="Node 0: Student Hub")

# Initialize MCP Server logic (simulated singleton)
server = StudentHubMCPServer()

@app.get("/")
async def root():
    return {"message": "Node 0 Student Hub is running"}

# --- Student Management ---

@app.post("/api/v1/students", response_model=Student)
async def create_student(student: Student):
    # Convert Pydantic model to dict for repo
    data = student.dict()
    # In a real app we might handle ID generation here if not provided, or in repo
    result = await server.student_manager.create_student(data)
    return result

@app.get("/api/v1/students", response_model=list[Student])
async def get_students():
    return await server.student_manager.get_all_students()

@app.get("/api/v1/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    student = await server.student_manager.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# --- Profile & Tools ---

@app.post("/api/v1/profiles/unified")
async def get_unified_profile(input_data: GetUnifiedProfileInput):
    return await server.get_unified_profile(input_data)

@app.post("/api/v1/interventions")
async def create_intervention(input_data: CreateInterventionInput):
    return await server.create_learning_intervention(input_data)

@app.post("/api/v1/schedules")
async def schedule_task(input_data: SchedulePeriodicTaskInput):
    return await server.schedule_periodic_task(input_data)

@app.post("/api/v1/analytics")
async def get_analytics(input_data: GetClassAnalyticsInput):
    return await server.get_class_analytics(input_data)
