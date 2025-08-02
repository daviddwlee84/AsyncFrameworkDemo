from typing import List, Optional, Dict, Any
import json
from backend.models.task import Task, TaskStatus, CreateTaskInput, TaskResponse
from backend.database.connection import db_manager
from datetime import datetime


class TaskRepository:
    def __init__(self):
        self.supabase = db_manager.get_supabase_client()

    async def create_task(self, task_input: CreateTaskInput) -> TaskResponse:
        """Create a new task using Supabase client"""
        task_data = {
            "type": task_input.type,
            "payload": task_input.payload,
            "status": TaskStatus.PENDING,
        }

        result = self.supabase.table("tasks").insert(task_data).execute()

        if result.data:
            task_record = result.data[0]
            return TaskResponse(
                id=task_record["id"],
                type=task_record["type"],
                status=task_record["status"],
                payload=task_record["payload"],
                result=task_record.get("result"),
                error_message=task_record.get("error_message"),
                created_at=datetime.fromisoformat(
                    task_record["created_at"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    task_record["updated_at"].replace("Z", "+00:00")
                ),
                retries=task_record["retries"],
                max_retries=task_record["max_retries"],
            )
        else:
            raise Exception("Failed to create task")

    async def get_task_by_id(self, task_id: str) -> Optional[TaskResponse]:
        """Get task by ID"""
        result = self.supabase.table("tasks").select("*").eq("id", task_id).execute()

        if result.data:
            task_record = result.data[0]
            return TaskResponse(
                id=task_record["id"],
                type=task_record["type"],
                status=task_record["status"],
                payload=task_record["payload"],
                result=task_record.get("result"),
                error_message=task_record.get("error_message"),
                created_at=datetime.fromisoformat(
                    task_record["created_at"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    task_record["updated_at"].replace("Z", "+00:00")
                ),
                retries=task_record["retries"],
                max_retries=task_record["max_retries"],
            )
        return None

    async def get_tasks(
        self, limit: int = 50, status: Optional[str] = None
    ) -> List[TaskResponse]:
        """Get tasks with optional filtering"""
        query = (
            self.supabase.table("tasks")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
        )

        if status:
            query = query.eq("status", status)

        result = query.execute()

        tasks = []
        for task_record in result.data:
            tasks.append(
                TaskResponse(
                    id=task_record["id"],
                    type=task_record["type"],
                    status=task_record["status"],
                    payload=task_record["payload"],
                    result=task_record.get("result"),
                    error_message=task_record.get("error_message"),
                    created_at=datetime.fromisoformat(
                        task_record["created_at"].replace("Z", "+00:00")
                    ),
                    updated_at=datetime.fromisoformat(
                        task_record["updated_at"].replace("Z", "+00:00")
                    ),
                    retries=task_record["retries"],
                    max_retries=task_record["max_retries"],
                )
            )

        return tasks

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> Optional[TaskResponse]:
        """Update task status and result"""
        update_data = {"status": status}

        if result is not None:
            update_data["result"] = result

        if error_message is not None:
            update_data["error_message"] = error_message

        result = (
            self.supabase.table("tasks").update(update_data).eq("id", task_id).execute()
        )

        if result.data:
            task_record = result.data[0]
            return TaskResponse(
                id=task_record["id"],
                type=task_record["type"],
                status=task_record["status"],
                payload=task_record["payload"],
                result=task_record.get("result"),
                error_message=task_record.get("error_message"),
                created_at=datetime.fromisoformat(
                    task_record["created_at"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    task_record["updated_at"].replace("Z", "+00:00")
                ),
                retries=task_record["retries"],
                max_retries=task_record["max_retries"],
            )
        return None


# Global repository instance
task_repository = TaskRepository()
