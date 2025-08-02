import os
import strawberry
import asyncpg
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)


@strawberry.type
class Task:
    id: int
    task_type: str
    payload: str


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, world!"


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_task(self, task_type: str, payload: str) -> Task:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow(
                "INSERT INTO tasks (task_type, payload) VALUES ($1, $2) RETURNING id, task_type, payload",
                task_type,
                payload,
            )
            return Task(
                id=row["id"], task_type=row["task_type"], payload=str(row["payload"])
            )
        finally:
            await conn.close()


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def read_root():
    return {"Hello": "World"}
