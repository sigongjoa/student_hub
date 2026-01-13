"""
gRPC-based MCP Client

Connects to real gRPC MCP servers (Node 2, 4, 7).
"""
import grpc
import logging
from typing import Dict, Any, Optional
import json

from generated import node2_qdna_pb2, node2_qdna_pb2_grpc
from generated import node4_labnode_pb2, node4_labnode_pb2_grpc
from generated import node7_errornote_pb2, node7_errornote_pb2_grpc

logger = logging.getLogger(__name__)


class GRPCMCPClient:
    """gRPC-based MCP Client for real servers"""
    
    def __init__(self, server_name: str, host: str, port: int):
        self.server_name = server_name
        self.host = host
        self.port = port
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub = None
    
    async def connect(self):
        """Connect to gRPC server"""
        target = f"{self.host}:{self.port}"
        logger.info(f"Connecting to {self.server_name} at {target}...")
        
        self.channel = grpc.aio.insecure_channel(target)
        
        # Create appropriate stub based on server name
        if self.server_name == "q-dna":
            self.stub = node2_qdna_pb2_grpc.QDNAServiceStub(self.channel)
        elif self.server_name == "lab-node":
            self.stub = node4_labnode_pb2_grpc.LabNodeServiceStub(self.channel)
        elif self.server_name == "error-note":
            self.stub = node7_errornote_pb2_grpc.ErrorNoteServiceStub(self.channel)
        else:
            raise ValueError(f"Unknown server: {self.server_name}")
        
        logger.info(f"✅ Connected to {self.server_name}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call gRPC method"""
        logger.info(f"Calling {self.server_name}.{tool_name} with {arguments}")
        
        try:
            if self.server_name == "q-dna":
                return await self._call_qdna(tool_name, arguments)
            elif self.server_name == "lab-node":
                return await self._call_labnode(tool_name, arguments)
            elif self.server_name == "error-note":
                return await self._call_errornote(tool_name, arguments)
            else:
                raise ValueError(f"Unknown server: {self.server_name}")
        
        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e}")
            raise
    
    async def _call_qdna(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call Q-DNA service"""
        if tool_name == "get_student_mastery":
            request = node2_qdna_pb2.GetStudentMasteryRequest(
                student_id=arguments["student_id"],
                concepts=arguments.get("concepts", []),
                skill_ids=arguments.get("skill_ids", [])
            )
            response = await self.stub.GetStudentMastery(request)
            return dict(response.mastery)
        
        elif tool_name == "recommend_questions":
            request = node2_qdna_pb2.RecommendQuestionsRequest(
                student_id=arguments["student_id"],
                concept=arguments.get("concept", ""),
                difficulty=arguments.get("difficulty", "medium"),
                count=arguments.get("count", 10),
                curriculum_path=arguments.get("curriculum_path", ""),
                weak_concepts=arguments.get("weak_concepts", []),
                weak_ratio=arguments.get("weak_ratio", 0.0)
            )
            response = await self.stub.RecommendQuestions(request)
            return {
                "questions": [
                    {
                        "id": q.id,
                        "content": q.content,
                        "difficulty": q.difficulty,
                        "concepts": list(q.concepts),
                        "estimated_time_minutes": q.estimated_time_minutes
                    }
                    for q in response.questions
                ],
                "student_id": response.student_id,
                "count": response.count
            }
        
        elif tool_name == "get_question_dna":
            request = node2_qdna_pb2.GetQuestionDNARequest(
                question_id=arguments["question_id"]
            )
            response = await self.stub.GetQuestionDNA(request)
            return {
                "question_id": response.question_id,
                "difficulty": response.difficulty,
                "concepts": list(response.concepts),
                "bloom_level": response.bloom_level
            }
        
        elif tool_name == "estimate_learning_time":
            request = node2_qdna_pb2.EstimateLearningTimeRequest(
                concept=arguments["concept"],
                current_mastery=arguments.get("current_mastery", 0.5),
                target_mastery=arguments.get("target_mastery", 0.8)
            )
            response = await self.stub.EstimateLearningTime(request)
            return {
                "concept": response.concept,
                "estimated_hours": response.estimated_hours,
                "current_mastery": response.current_mastery
            }
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _call_labnode(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call Lab Node service"""
        if tool_name == "get_recent_concepts":
            request = node4_labnode_pb2.GetRecentConceptsRequest(
                student_id=arguments["student_id"],
                days=arguments.get("days", 7),
                curriculum_path=arguments.get("curriculum_path", "")
            )
            response = await self.stub.GetRecentConcepts(request)
            return {
                "concepts": list(response.concepts),
                "student_id": response.student_id,
                "period_days": response.period_days
            }
        
        elif tool_name == "get_concept_heatmap":
            request = node4_labnode_pb2.GetConceptHeatmapRequest(
                student_id=arguments["student_id"],
                curriculum_path=arguments.get("curriculum_path", "")
            )
            response = await self.stub.GetConceptHeatmap(request)
            return {
                "student_id": response.student_id,
                "heatmap": dict(response.heatmap),
                "timestamp": response.timestamp
            }
        
        elif tool_name == "get_weak_concepts":
            request = node4_labnode_pb2.GetWeakConceptsRequest(
                student_id=arguments["student_id"],
                threshold=arguments.get("threshold", 0.6),
                limit=arguments.get("limit", 10)
            )
            response = await self.stub.GetWeakConcepts(request)
            return {
                "weak_concepts": [
                    {
                        "concept": wc.concept,
                        "accuracy": wc.accuracy,
                        "attempts": wc.attempts
                    }
                    for wc in response.weak_concepts
                ]
            }
        
        elif tool_name == "get_activity_summary":
            request = node4_labnode_pb2.GetActivitySummaryRequest(
                student_id=arguments["student_id"],
                days=arguments.get("days", 7)
            )
            response = await self.stub.GetActivitySummary(request)
            return {
                "student_id": response.student_id,
                "period_days": response.period_days,
                "total_attempts": response.total_attempts,
                "average_accuracy": response.average_accuracy,
                "concepts_practiced": response.concepts_practiced,
                "last_activity": response.last_activity,
                "timestamp": response.timestamp
            }
        
        elif tool_name == "get_class_analytics":
            request = node4_labnode_pb2.GetClassAnalyticsRequest(
                class_id=arguments["class_id"],
                start_date=arguments.get("start_date", ""),
                end_date=arguments.get("end_date", "")
            )
            response = await self.stub.GetClassAnalytics(request)
            return {
                "total_students": response.total_students,
                "active_students": response.active_students,
                "average_accuracy": response.average_accuracy,
                "at_risk_students": response.at_risk_students,
                "common_weak_concepts": [
                    {
                        "concept": cwc.concept,
                        "struggling_count": cwc.struggling_count
                    }
                    for cwc in response.common_weak_concepts
                ]
            }
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _call_errornote(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call Error Note service"""
        if tool_name == "create_error_note":
            request = node7_errornote_pb2.CreateErrorNoteRequest(
                student_id=arguments["student_id"],
                question_id=arguments["question_id"],
                student_answer=arguments["student_answer"],
                correct_answer=arguments["correct_answer"]
            )
            response = await self.stub.CreateErrorNote(request)
            return {
                "id": response.id,
                "created_at": response.created_at,
                "analysis": {
                    "misconception": response.analysis.misconception,
                    "root_cause": response.analysis.root_cause,
                    "related_concepts": list(response.analysis.related_concepts)
                },
                "anki_data": {
                    "ease_factor": response.anki_data.ease_factor,
                    "interval_days": response.anki_data.interval_days,
                    "next_review": response.anki_data.next_review
                }
            }
        
        elif tool_name == "calculate_anki_schedule":
            request = node7_errornote_pb2.CalculateAnkiScheduleRequest(
                error_note_id=arguments["error_note_id"],
                quality=arguments.get("quality", 3)
            )
            response = await self.stub.CalculateAnkiSchedule(request)
            return {
                "ease_factor": response.ease_factor,
                "interval_days": response.interval_days,
                "next_review_date": response.next_review_date
            }
        
        elif tool_name == "list_error_notes_by_student":
            request = node7_errornote_pb2.ListErrorNotesByStudentRequest(
                student_id=arguments["student_id"]
            )
            response = await self.stub.ListErrorNotesByStudent(request)
            return {
                "error_notes": [
                    {
                        "id": note.id,
                        "question_id": note.question_id,
                        "created_at": note.created_at
                    }
                    for note in response.error_notes
                ]
            }
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def close(self):
        """Close gRPC channel"""
        if self.channel:
            await self.channel.close()
            logger.info(f"Closed connection to {self.server_name}")
