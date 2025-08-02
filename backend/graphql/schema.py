import strawberry
from typing import List, Optional, Dict, Any
from backend.models.task import TaskType, TaskStatus, CreateTaskInput, TaskResponse
from backend.database.task_repository import task_repository


# GraphQL Types
@strawberry.type
class TaskType_GQL:
    id: str
    type: str
    status: str
    payload: strawberry.scalars.JSON
    result: Optional[strawberry.scalars.JSON] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
    retries: int
    max_retries: int


@strawberry.input
class CreateTaskInput_GQL:
    type: str
    payload: strawberry.scalars.JSON


# Queries
@strawberry.type
class Query:
    @strawberry.field
    async def get_task(self, task_id: str) -> Optional[TaskType_GQL]:
        """Get a specific task by ID"""
        task = await task_repository.get_task_by_id(task_id)
        if task:
            return TaskType_GQL(
                id=task.id,
                type=task.type,
                status=task.status,
                payload=task.payload,
                result=task.result,
                error_message=task.error_message,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat(),
                retries=task.retries,
                max_retries=task.max_retries,
            )
        return None

    @strawberry.field
    async def get_tasks(
        self, limit: int = 50, status: Optional[str] = None
    ) -> List[TaskType_GQL]:
        """Get list of tasks with optional status filter"""
        tasks = await task_repository.get_tasks(limit=limit, status=status)
        return [
            TaskType_GQL(
                id=task.id,
                type=task.type,
                status=task.status,
                payload=task.payload,
                result=task.result,
                error_message=task.error_message,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat(),
                retries=task.retries,
                max_retries=task.max_retries,
            )
            for task in tasks
        ]


# Mutations
@strawberry.type
class Mutation:
    @strawberry.field
    async def create_task(self, input: CreateTaskInput_GQL) -> TaskType_GQL:
        """Create a new async task"""
        task_input = CreateTaskInput(type=input.type, payload=input.payload)
        task = await task_repository.create_task(task_input)

        return TaskType_GQL(
            id=task.id,
            type=task.type,
            status=task.status,
            payload=task.payload,
            result=task.result,
            error_message=task.error_message,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            retries=task.retries,
            max_retries=task.max_retries,
        )

    @strawberry.field
    async def create_stripe_customer_task(self, email: str, name: str) -> TaskType_GQL:
        """Convenience mutation to create a Stripe customer creation task"""
        task_input = CreateTaskInput(
            type=TaskType.STRIPE_CREATE_CUSTOMER, payload={"email": email, "name": name}
        )
        task = await task_repository.create_task(task_input)

        return TaskType_GQL(
            id=task.id,
            type=task.type,
            status=task.status,
            payload=task.payload,
            result=task.result,
            error_message=task.error_message,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            retries=task.retries,
            max_retries=task.max_retries,
        )

    @strawberry.field
    async def create_stripe_payment_task(
        self, amount: int, currency: str, customer_id: str
    ) -> TaskType_GQL:
        """Convenience mutation to create a Stripe payment task"""
        task_input = CreateTaskInput(
            type=TaskType.STRIPE_CREATE_PAYMENT,
            payload={
                "amount": amount,
                "currency": currency,
                "customer_id": customer_id,
            },
        )
        task = await task_repository.create_task(task_input)

        return TaskType_GQL(
            id=task.id,
            type=task.type,
            status=task.status,
            payload=task.payload,
            result=task.result,
            error_message=task.error_message,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            retries=task.retries,
            max_retries=task.max_retries,
        )


# Create the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
