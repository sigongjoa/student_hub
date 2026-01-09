import asyncio
import sys
import os
from datetime import datetime

# Add mathesis-common to pythonpath
# Current: node0/tests/test_flow.py -> ../../ -> root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
COMMON_DIR = os.path.join(ROOT_DIR, 'mathesis-common')
sys.path.append(ROOT_DIR)
sys.path.append(COMMON_DIR)

from node0_student_hub.mcp_server import StudentHubMCPServer
from node0_student_hub.app.schemas.intervention import CreateInterventionInput, InterventionType
from node0_student_hub.app.schemas.profile import GetUnifiedProfileInput
# Lazy import to ensure path is added first
try:
    from mathesis_core.export.pdf_generator import GenericTypstPDFGenerator
except ImportError as e:
    print(f"Warning: Could not import GenericTypstPDFGenerator: {e}")
    GenericTypstPDFGenerator = None

async def main():
    print("--- Starting Node 0 Flow Verification ---")
    server = StudentHubMCPServer()

    # Data collection for report
    report_data = {
        "run_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "student": {},
        "profile": {},
        "intervention": {}
    }

    # 1. Create a Student
    print("\n1. Creating Student...")
    import uuid
    student_id = str(uuid.uuid4())
    student_data = {
        "id": student_id,
        "name": "Test Student",
        "grade": 10,
        "school_code": "SCH_001",
        "created_at": datetime.now()
    }
    student = await server.student_manager.create_student(student_data)
    print(f"Created Student: {student.name} ({student.id})")
    
    report_data["student"] = {
        "id": student.id,
        "name": student.name,
        "grade": student.grade,
        "school_code": student.school_code
    }

    # 2. Get Unified Profile
    print("\n2. Fetching Unified Profile...")
    profile_input = GetUnifiedProfileInput(
        student_id=student_id,
        include_sections=["basic", "mastery", "activities"]
    )
    profile = await server.get_unified_profile(profile_input)
    print("Unified Profile Summary:")
    print(f"- Name: {profile.get('name')}")
    print(f"- Mastery Average: {profile.get('mastery_summary', {}).get('average')}")
    
    report_data["profile"] = profile

    # 3. Create Intervention
    print("\n3. Creating Intervention...")
    intervention_input = CreateInterventionInput(
        student_id=student_id,
        trigger="manual",
        intervention_type=InterventionType.CONCEPT_REVIEW,
        reason="Testing intervention creation",
        metadata={"weak_concepts": ["concept_A"]}
    )
    intervention = await server.create_learning_intervention(intervention_input)
    print("Intervention Created:")
    print(f"- ID: {intervention.id}")

    # Serialize SQLAlchemy model for report
    intervention_dict = {
        "id": str(intervention.id),
        "student_id": str(intervention.student_id),
        "intervention_type": intervention.type,
        "type": intervention.type, # Keep both for safety
        "weak_areas": intervention.weak_areas,
        "learning_path": intervention.learning_path,
        "status": intervention.status,
        "created_at": str(intervention.created_at)
    }
    # For compatibility/extra fields that are not in DB columns but might be attached dynamically or need to be added
    # In my Service impl, I passed 'trigger'/'reason'/'actions' to repo.create, and my mock repo sets attributes.
    # So I can access them from the object if they were set.
    intervention_dict['trigger'] = getattr(intervention, 'trigger', intervention_input.trigger)
    intervention_dict['reason'] = getattr(intervention, 'reason', intervention_input.reason)
    intervention_dict['actions'] = getattr(intervention, 'actions', [])
    
    # Stringify params for report rendering
    if 'actions' in intervention_dict:
        for action in intervention_dict['actions']:
            if 'params' in action:
                action['params'] = str(action['params'])
    
    report_data["intervention"] = intervention_dict

    print("\n--- Verification Completed Successfully ---")

    # 4. Generate PDF Report
    if GenericTypstPDFGenerator:
        print("\n4. Generating PDF Report (via Common Module)...")
        try:
            generator = GenericTypstPDFGenerator()
            template_path = os.path.join(os.path.dirname(__file__), "report_template.typ")
            output_path = os.path.join(os.path.dirname(__file__), "test_report.pdf")
            
            # Use await as the new interface is async
            pdf_path = await generator.generate(template_path, report_data, output_path)
            print(f"PDF Report Generated: {pdf_path}")
        except Exception as e:
            print(f"Failed to generate PDF report: {e}")
    else:
        print("Skipping PDF generation (GenericTypstPDFGenerator not available)")

if __name__ == "__main__":
    asyncio.run(main())
