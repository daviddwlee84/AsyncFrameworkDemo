import os
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from backend.graphql.schema import schema
from backend.database.connection import db_manager
from dotenv import load_dotenv

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Async Framework Demo API",
    description="GraphQL API for async task processing with PostgreSQL triggers",
    version="1.0.0",
)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Include GraphQL router
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {
        "message": "Async Framework Demo API",
        "graphql_endpoint": "/graphql",
        "graphql_playground": "/graphql",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "async-framework-demo"}


@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    print("🚀 Starting Async Framework Demo API...")
    print(f"📊 GraphQL endpoint: http://127.0.0.1:8000/graphql")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    await db_manager.close_pool()
    print("💫 Async Framework Demo API shutdown complete")


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("GRAPHQL_HOST", "0.0.0.0")
    port = int(os.getenv("GRAPHQL_PORT", "8000"))

    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
