"""
WorkflowEngine

워크플로우 템플릿 실행 엔진
n8n 스타일의 노드 기반 워크플로우 실행
"""
from typing import Dict, Any, List, Callable, Optional
import asyncio
import logging
import re
from dataclasses import dataclass
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class WorkflowNode:
    """워크플로우 노드"""
    id: str
    type: str  # tool, trigger, condition
    tool_name: Optional[str] = None
    config: Dict[str, Any] = None


@dataclass
class WorkflowEdge:
    """워크플로우 엣지 (연결)"""
    from_node: str
    to_node: str


class WorkflowEngine:
    """워크플로우 실행 엔진"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        
    def register_tool(self, name: str, tool_func: Callable):
        """도구 등록"""
        self.tools[name] = tool_func
        logger.info(f"Registered workflow tool: {name}")
    
    async def execute(
        self,
        workflow: Dict[str, Any],
        input_vars: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        워크플로우 실행
        
        Args:
            workflow: 워크플로우 정의 (nodes, edges)
            input_vars: 입력 변수
            
        Returns:
            실행 결과 (status, outputs, error)
        """
        try:
            nodes = workflow.get("nodes", [])
            edges = workflow.get("edges", [])
            
            # 실행 컨텍스트 초기화
            context = {
                "input": input_vars,
                "outputs": {}
            }
            
            # 실행 순서 결정 (Topological Sort)
            execution_plan = self._plan_execution(nodes, edges)
            
            # 각 레벨별로 실행 (병렬 가능한 노드는 동시 실행)
            for level_nodes in execution_plan:
                await self._execute_level(level_nodes, nodes, context)
            
            return {
                "status": "completed",
                "outputs": context["outputs"]
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _plan_execution(
        self,
        nodes: List[Dict],
        edges: List[Dict]
    ) -> List[List[str]]:
        """
        실행 계획 수립 (Topological Sort + Levels)
        
        Returns:
            레벨별 노드 ID 리스트 (각 레벨은 병렬 실행 가능)
        """
        # 그래프 구축
        graph = defaultdict(list)  # node_id -> [dependent_node_ids]
        in_degree = defaultdict(int)  # node_id -> 들어오는 엣지 수
        
        # 모든 노드 초기화
        all_node_ids = {node["id"] for node in nodes}
        for node_id in all_node_ids:
            in_degree[node_id] = 0
        
        # 엣지 추가
        for edge in edges:
            from_id = edge["from"]
            to_id = edge["to"]
            graph[from_id].append(to_id)
            in_degree[to_id] += 1
        
        # Level-wise Topological Sort
        levels = []
        current_level = deque([node_id for node_id in all_node_ids if in_degree[node_id] == 0])
        
        while current_level:
            levels.append(list(current_level))
            next_level = deque()
            
            for node_id in current_level:
                for dependent in graph[node_id]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_level.append(dependent)
            
            current_level = next_level
        
        return levels
    
    async def _execute_level(
        self,
        node_ids: List[str],
        all_nodes: List[Dict],
        context: Dict[str, Any]
    ):
        """레벨(병렬 실행 가능한 노드들)을 실행"""
        tasks = []
        
        for node_id in node_ids:
            node = next((n for n in all_nodes if n["id"] == node_id), None)
            if node:
                tasks.append(self._execute_node(node, context))
        
        # 병렬 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        for node_id, result in zip(node_ids, results):
            if isinstance(result, Exception):
                raise result
            context["outputs"][node_id] = result
    
    async def _execute_node(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """단일 노드 실행"""
        node_id = node["id"]
        node_type = node["type"]
        
        if node_type == "tool":
            tool_name = node.get("tool_name")
            config = node.get("config", {})
            
            # 변수 치환
            resolved_config = self._resolve_variables(config, context)
            
            # 도구 실행
            if tool_name not in self.tools:
                raise ValueError(f"Tool not found: {tool_name}")
            
            tool_func = self.tools[tool_name]
            result = await tool_func(resolved_config)
            
            logger.info(f"Node {node_id} ({tool_name}) executed successfully")
            return result
        
        else:
            raise ValueError(f"Unsupported node type: {node_type}")
    
    def _resolve_variables(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        변수 치환
        
        {{input.var}} -> context["input"]["var"]
        {{node_id.field}} -> context["outputs"]["node_id"]["field"]
        """
        resolved = {}
        
        for key, value in config.items():
            if isinstance(value, str):
                resolved[key] = self._resolve_string(value, context)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_variables(value, context)
            elif isinstance(value, list):
                resolved[key] = [
                    self._resolve_string(item, context) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                resolved[key] = value
        
        return resolved
    
    def _resolve_string(
        self,
        value: str,
        context: Dict[str, Any]
    ) -> Any:
        """문자열에서 변수 치환"""
        # {{input.var}} 또는 {{node_id.field}} 패턴 찾기
        pattern = r'\{\{([^}]+)\}\}'

        def replacer(match):
            var_path = match.group(1).strip()
            parts = var_path.split(".")

            # 변수 경로 결정
            if parts[0] == "input":
                # {{input.var}} -> context["input"]["var"]
                current = context.get("input", {})
                remaining_parts = parts[1:]
            else:
                # {{node_id.field}} -> context["outputs"]["node_id"]["field"]
                node_id = parts[0]
                current = context.get("outputs", {}).get(node_id, {})
                remaining_parts = parts[1:]

            # 나머지 경로 탐색
            for part in remaining_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return match.group(0)  # 변수를 찾을 수 없으면 원본 반환

            return str(current) if not isinstance(current, (dict, list)) else current

        # 전체 문자열이 하나의 변수인 경우
        full_match = re.fullmatch(pattern, value)
        if full_match:
            var_path = full_match.group(1).strip()
            parts = var_path.split(".")

            # 변수 경로 결정
            if parts[0] == "input":
                current = context.get("input", {})
                remaining_parts = parts[1:]
            else:
                node_id = parts[0]
                current = context.get("outputs", {}).get(node_id, {})
                remaining_parts = parts[1:]

            # 나머지 경로 탐색
            for part in remaining_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return value

            return current  # 타입 유지

        # 문자열 내 일부가 변수인 경우
        return re.sub(pattern, replacer, value)
