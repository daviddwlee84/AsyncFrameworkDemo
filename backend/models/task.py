from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid
from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    STRIPE_CREATE_CUSTOMER = "stripe_create_customer"
    STRIPE_CREATE_PAYMENT = "stripe_create_payment"
    STRIPE_REFUND_PAYMENT = "stripe_refund_payment"


class Task(BaseModel):
    id: Optional[str] = None
    type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    retries: int = 0
    max_retries: int = 3

    class Config:
        use_enum_values = True


class CreateTaskInput(BaseModel):
    type: TaskType
    payload: Dict[str, Any]

    class Config:
        use_enum_values = True


class TaskResponse(BaseModel):
    id: str
    type: str
    status: str
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    retries: int
    max_retries: int
