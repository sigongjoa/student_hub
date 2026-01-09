from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, update, delete # Commented out as we are using Mock for now
from node0_student_hub.app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """
    Base Repository (Mock Implementation for now)
    """

    def __init__(self, model: type[ModelType], db: AsyncSession = None):
        self.model = model
        self.db = db # In real impl this would be AsyncSession
        self._mock_storage = {} # Simulating DB table

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        return self._mock_storage.get(str(id))

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return list(self._mock_storage.values())[skip:skip+limit]

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        # Create instance from dictionary
        # In real DB this handled by SQLAlchemy
        import uuid
        if "id" not in obj_in:
            obj_in["id"] = uuid.uuid4()
        
        db_obj = self.model()
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        
        self._mock_storage[str(db_obj.id)] = db_obj
        return db_obj

    async def update(self, id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        obj = self._mock_storage.get(str(id))
        if obj:
            for key, value in obj_in.items():
                setattr(obj, key, value)
        return obj

    async def delete(self, id: Any) -> bool:
        if str(id) in self._mock_storage:
            del self._mock_storage[str(id)]
            return True
        return False
