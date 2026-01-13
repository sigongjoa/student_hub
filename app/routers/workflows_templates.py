"""
Workflow Templates API Router

워크플로우 템플릿 CRUD 및 실행 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import json
import logging

from app.db.session import get_db
from app.models.workflow_template import WorkflowTemplate
from app.services.workflow_engine import WorkflowEngine
from app.mcp.tools import TOOL_REGISTRY

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workflows/templates", tags=["workflow-templates"])

# Global workflow engine
workflow_engine = WorkflowEngine()

# Register MCP tools with workflow engine
for name, tool in TOOL_REGISTRY.items():
    async def tool_wrapper(config, tool_instance=tool):
        return await tool_instance.safe_execute(config)
    workflow_engine.register_tool(name, tool_wrapper)


class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    definition: Dict[str, Any]
    is_public: bool = False


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class TemplateExecute(BaseModel):
    input_variables: Dict[str, Any] = {}


@router.post("/")
async def create_template(
    template: TemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    워크플로우 템플릿 생성
    
    Args:
        template: 템플릿 정보
        db: Database session
        
    Returns:
        생성된 템플릿
    """
    try:
        db_template = WorkflowTemplate(
            id=str(uuid.uuid4()),
            name=template.name,
            description=template.description,
            definition=template.definition,
            is_public=template.is_public,
            created_by="system"  # TODO: 실제 사용자 ID
        )
        
        db.add(db_template)
        await db.commit()
        await db.refresh(db_template)
        
        return {
            "id": db_template.id,
            "name": db_template.name,
            "description": db_template.description,
            "definition": db_template.definition,
            "is_public": db_template.is_public,
            "created_at": db_template.created_at.isoformat(),
            "execution_count": db_template.execution_count
        }
        
    except Exception as e:
        logger.error(f"Template creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    워크플로우 템플릿 목록 조회
    
    Args:
        skip: 건너뛸 개수
        limit: 최대 개수
        db: Database session
        
    Returns:
        템플릿 목록
    """
    try:
        from sqlalchemy import select
        
        query = select(WorkflowTemplate).where(
            WorkflowTemplate.is_active == True
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        templates = result.scalars().all()
        
        return {
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "is_public": t.is_public,
                    "created_at": t.created_at.isoformat(),
                    "execution_count": t.execution_count
                }
                for t in templates
            ],
            "total": len(templates)
        }
        
    except Exception as e:
        logger.error(f"List templates error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    워크플로우 템플릿 상세 조회
    
    Args:
        template_id: 템플릿 ID
        db: Database session
        
    Returns:
        템플릿 상세 정보
    """
    try:
        template = await db.get(WorkflowTemplate, template_id)
        
        if not template or not template.is_active:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "definition": template.definition,
            "is_public": template.is_public,
            "created_by": template.created_by,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat() if template.updated_at else None,
            "execution_count": template.execution_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get template error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}")
async def update_template(
    template_id: str,
    template: TemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    워크플로우 템플릿 수정
    
    Args:
        template_id: 템플릿 ID
        template: 수정할 정보
        db: Database session
        
    Returns:
        수정된 템플릿
    """
    try:
        db_template = await db.get(WorkflowTemplate, template_id)
        
        if not db_template or not db_template.is_active:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # 수정
        if template.name is not None:
            db_template.name = template.name
        if template.description is not None:
            db_template.description = template.description
        if template.definition is not None:
            db_template.definition = template.definition
        if template.is_public is not None:
            db_template.is_public = template.is_public
        
        await db.commit()
        await db.refresh(db_template)
        
        return {
            "id": db_template.id,
            "name": db_template.name,
            "description": db_template.description,
            "definition": db_template.definition,
            "is_public": db_template.is_public,
            "updated_at": db_template.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update template error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    워크플로우 템플릿 삭제 (soft delete)
    
    Args:
        template_id: 템플릿 ID
        db: Database session
        
    Returns:
        성공 메시지
    """
    try:
        template = await db.get(WorkflowTemplate, template_id)
        
        if not template or not template.is_active:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Soft delete
        template.is_active = False
        await db.commit()
        
        return {"success": True, "message": f"Template {template_id} deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete template error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{template_id}/execute")
async def execute_template(
    template_id: str,
    execute_req: TemplateExecute,
    db: AsyncSession = Depends(get_db)
):
    """
    워크플로우 템플릿 실행
    
    Args:
        template_id: 템플릿 ID
        execute_req: 실행 요청 (입력 변수)
        db: Database session
        
    Returns:
        실행 결과
    """
    try:
        template = await db.get(WorkflowTemplate, template_id)
        
        if not template or not template.is_active:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # 실행
        result = await workflow_engine.execute(
            workflow=template.definition,
            input_vars=execute_req.input_variables
        )
        
        # 실행 카운트 증가
        template.execution_count += 1
        await db.commit()
        
        return {
            "template_id": template_id,
            "status": result["status"],
            "outputs": result.get("outputs", {}),
            "error": result.get("error")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Execute template error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
