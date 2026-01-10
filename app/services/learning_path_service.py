"""
Learning Path Service

개인화 학습 경로 워크플로우를 구현합니다.
데이터 플로우: Node 0 → Node 4 (히트맵) → Node 1 (선수지식 그래프) → Node 2 (학습 시간 추정)
"""
from typing import List, Optional, Dict, Set
from datetime import datetime
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from collections import defaultdict, deque

from app.mcp.manager import MCPClientManager
from app.models.workflow_session import WorkflowSession

logger = logging.getLogger(__name__)


@dataclass
class LearningPathRequest:
    """학습 경로 생성 요청"""
    student_id: str
    target_concept: str
    days: int


@dataclass
class PathNode:
    """학습 경로의 각 노드"""
    concept: str
    order: int
    estimated_hours: int
    prerequisites: List[str]


@dataclass
class LearningPathResult:
    """학습 경로 생성 결과"""
    workflow_id: str
    learning_path: List[PathNode]
    total_estimated_hours: int
    daily_tasks: Dict[str, int]  # {"Day 1": 3, "Day 2": 4, ...}


class LearningPathService:
    """개인화 학습 경로 워크플로우 서비스"""

    def __init__(self, mcp: MCPClientManager, db: AsyncSession):
        self.mcp = mcp
        self.db = db

    async def generate_learning_path(
        self,
        request: LearningPathRequest
    ) -> LearningPathResult:
        """
        학습 경로 생성 워크플로우

        Steps:
        1. 학생 히트맵 가져오기 (Node 4)
        2. 선수지식 그래프 가져오기 (Node 1)
        3. Topological Sort로 학습 순서 결정
        4. 각 개념별 학습 시간 추정 (Node 2)
        5. 일일 태스크 할당
        6. 워크플로우 세션 생성
        """
        logger.info(f"Generating learning path for student {request.student_id}, target: {request.target_concept}")

        # 목표 개념이 여러 개일 수 있음 (쉼표로 구분)
        target_concepts = [c.strip() for c in request.target_concept.split(",")]

        # Step 1: 학생 히트맵 가져오기 (Node 4)
        heatmap_response = await self.mcp.call("lab-node", "get_concept_heatmap", {
            "student_id": request.student_id
        })
        heatmap = heatmap_response.get("heatmap", {})

        # 약점 개념 식별 (mastery < 0.6)
        weak_concepts = [concept for concept, score in heatmap.items() if score < 0.6]
        logger.info(f"Identified weak concepts: {weak_concepts}")

        # Step 2: 선수지식 그래프 가져오기 (Node 1)
        graph_response = await self.mcp.call("logic-engine", "get_prerequisite_graph", {
            "concepts": target_concepts + weak_concepts
        })
        graph = graph_response.get("graph", {})

        # Step 3: Topological Sort로 학습 순서 결정
        learning_sequence = self._topological_sort(graph, target_concepts, weak_concepts)
        logger.info(f"Learning sequence: {learning_sequence}")

        # Step 4: 각 개념별 학습 시간 추정 (Node 2)
        path_nodes = []
        for order, concept in enumerate(learning_sequence, start=1):
            current_mastery = heatmap.get(concept, 0.5)

            time_estimate = await self.mcp.call("q-dna", "estimate_learning_time", {
                "concept": concept,
                "current_mastery": current_mastery
            })

            prerequisites = graph.get(concept, {}).get("prerequisites", [])

            path_node = PathNode(
                concept=concept,
                order=order,
                estimated_hours=time_estimate.get("estimated_hours", 4),
                prerequisites=prerequisites
            )
            path_nodes.append(path_node)

        # 총 예상 시간 계산
        total_estimated_hours = sum(node.estimated_hours for node in path_nodes)

        # Step 5: 일일 태스크 할당
        daily_tasks = self._allocate_daily_tasks(path_nodes, request.days)

        # Step 6: 워크플로우 세션 생성
        workflow_session = WorkflowSession(
            student_id=request.student_id,
            workflow_type="learning_path",
            status="in_progress",
            workflow_metadata={
                "target_concept": request.target_concept,
                "weak_concepts": weak_concepts,
                "learning_path": [
                    {
                        "concept": node.concept,
                        "order": node.order,
                        "estimated_hours": node.estimated_hours
                    }
                    for node in path_nodes
                ],
                "total_estimated_hours": total_estimated_hours,
                "days": request.days,
                "created_at": datetime.now().isoformat()
            }
        )

        self.db.add(workflow_session)
        await self.db.commit()
        await self.db.refresh(workflow_session)

        logger.info(f"Created learning path workflow {workflow_session.workflow_id}")

        return LearningPathResult(
            workflow_id=workflow_session.workflow_id,
            learning_path=path_nodes,
            total_estimated_hours=total_estimated_hours,
            daily_tasks=daily_tasks
        )

    def _topological_sort(
        self,
        graph: Dict[str, Dict],
        target_concepts: List[str],
        weak_concepts: List[str]
    ) -> List[str]:
        """
        Topological Sort (Kahn's Algorithm)

        DAG에서 선수지식 순서를 지키면서 개념을 정렬합니다.
        약점 개념과 목표 개념만 포함합니다.
        """
        # 포함할 개념: 약점 개념 + 목표 개념
        included_concepts = set(weak_concepts + target_concepts)

        # 인접 리스트 및 진입 차수 계산
        adj_list = defaultdict(list)
        in_degree = defaultdict(int)

        # 그래프 초기화
        for concept in included_concepts:
            if concept not in in_degree:
                in_degree[concept] = 0

        # 간선 추가 (선수지식 → 개념)
        for concept in included_concepts:
            concept_data = graph.get(concept, {})
            prerequisites = concept_data.get("prerequisites", [])

            for prereq in prerequisites:
                if prereq in included_concepts:
                    adj_list[prereq].append(concept)
                    in_degree[concept] += 1

        # Kahn's Algorithm
        queue = deque([concept for concept in included_concepts if in_degree[concept] == 0])
        result = []

        while queue:
            # 진입 차수 0인 노드 중 약점 개념 우선
            current = None
            for node in queue:
                if node in weak_concepts:
                    current = node
                    break
            if current is None:
                current = queue.popleft()
            else:
                queue.remove(current)

            result.append(current)

            # 인접 노드의 진입 차수 감소
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 순환 참조 검증
        if len(result) != len(included_concepts):
            logger.warning("Cycle detected in prerequisite graph, using partial order")
            # 나머지 개념 추가 (순환이 있어도 최대한 포함)
            remaining = included_concepts - set(result)
            result.extend(sorted(remaining))

        return result

    def _allocate_daily_tasks(
        self,
        path_nodes: List[PathNode],
        total_days: int
    ) -> Dict[str, int]:
        """
        일일 태스크 할당

        전체 학습 시간을 지정된 날짜 수에 맞게 분배합니다.
        하루 최대 5시간을 넘지 않도록 조정합니다.
        """
        daily_tasks = {}
        current_day = 1
        day_hours = 0

        for node in path_nodes:
            concept_hours = node.estimated_hours

            while concept_hours > 0:
                if current_day > total_days:
                    # 날짜 초과 시 마지막 날에 추가
                    day_key = f"Day {total_days}"
                    daily_tasks[day_key] = daily_tasks.get(day_key, 0) + concept_hours
                    break

                # 현재 날에 남은 용량
                remaining_capacity = 5 - day_hours

                if remaining_capacity <= 0:
                    # 현재 날이 가득 찼으면 다음 날로
                    current_day += 1
                    day_hours = 0
                    continue

                # 할당할 시간 계산
                allocation = min(concept_hours, remaining_capacity)

                day_key = f"Day {current_day}"
                daily_tasks[day_key] = daily_tasks.get(day_key, 0) + int(allocation)

                concept_hours -= allocation
                day_hours += allocation

        return daily_tasks

    async def get_workflow_status(self, workflow_id: str) -> Optional[dict]:
        """워크플로우 상태 조회"""
        stmt = select(WorkflowSession).where(WorkflowSession.workflow_id == workflow_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            return None

        return {
            "workflow_id": session.workflow_id,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "metadata": session.workflow_metadata
        }
