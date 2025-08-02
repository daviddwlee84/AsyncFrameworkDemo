import asyncio
import asyncpg
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.database.connection import db_manager
from backend.models.task import TaskStatus
from backend.database.task_repository import task_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    def __init__(self, worker_name: str):
        self.worker_name = worker_name
        self.connection: Optional[asyncpg.Connection] = None
        self.running = False

    async def start(self):
        """Start the worker and listen for notifications"""
        logger.info(f"🔄 Starting worker: {self.worker_name}")

        # Get database connection pool
        pool = await db_manager.get_db_pool()
        self.connection = await pool.acquire()

        # Listen to new_task notifications
        await self.connection.add_listener("new_task", self._handle_notification)

        self.running = True
        logger.info(f"✅ Worker {self.worker_name} is now listening for tasks...")

        # Keep the worker running
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info(f"🛑 Stopping worker: {self.worker_name}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the worker and cleanup connections"""
        self.running = False
        if self.connection:
            await self.connection.remove_listener("new_task", self._handle_notification)
            pool = await db_manager.get_db_pool()
            await pool.release(self.connection)
            self.connection = None
        logger.info(f"🔴 Worker {self.worker_name} stopped")

    async def _handle_notification(self, connection, pid, channel, payload):
        """Handle incoming task notifications"""
        try:
            task_data = json.loads(payload)
            task_id = task_data.get("id")
            task_type = task_data.get("type")

            logger.info(f"📥 Received task {task_id} of type {task_type}")

            # Check if this worker can handle this task type
            if self.can_handle_task(task_type):
                await self._process_task(task_data)
            else:
                logger.debug(
                    f"⏭️ Skipping task {task_id} - not handled by {self.worker_name}"
                )

        except Exception as e:
            logger.error(f"❌ Error handling notification: {e}")

    async def _process_task(self, task_data: Dict[str, Any]):
        """Process a task with error handling and status updates"""
        task_id = task_data.get("id")

        try:
            # Update task status to processing
            await task_repository.update_task_status(task_id, TaskStatus.PROCESSING)
            logger.info(f"🔄 Processing task {task_id}")

            # Execute the task
            result = await self.execute_task(task_data)

            # Update task status to completed with result
            await task_repository.update_task_status(
                task_id, TaskStatus.COMPLETED, result=result
            )
            logger.info(f"✅ Task {task_id} completed successfully")

        except Exception as e:
            error_message = str(e)
            logger.error(f"❌ Task {task_id} failed: {error_message}")

            # Update task status to failed with error message
            await task_repository.update_task_status(
                task_id, TaskStatus.FAILED, error_message=error_message
            )

    @abstractmethod
    def can_handle_task(self, task_type: str) -> bool:
        """Check if this worker can handle the given task type"""
        pass

    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual task logic"""
        pass
