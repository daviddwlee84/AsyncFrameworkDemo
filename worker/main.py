import os
import asyncpg
import asyncio
import json
import stripe
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

stripe.api_key = STRIPE_API_KEY


async def create_stripe_customer(task_payload):
    try:
        customer = stripe.Customer.create(
            email=task_payload["email"], name=task_payload["name"]
        )
        print(f"Successfully created Stripe customer: {customer.id}")
        return customer
    except Exception as e:
        print(f"Error creating Stripe customer: {e}")
        return None


async def handle_task(payload):
    print(f"Received task: {payload}")
    task_data = json.loads(payload)

    if task_data["task_type"] == "create_stripe_customer":
        task_payload = json.loads(task_data["payload"])
        await create_stripe_customer(task_payload)

    # Update the task as processed in the database
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(
            "UPDATE tasks SET processed_at = NOW() WHERE id = $1", task_data["id"]
        )
    finally:
        await conn.close()

    print(f"Finished processing task {task_data['id']}")


async def listen_for_notifications():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.add_listener(
            "new_task",
            lambda conn, pid, channel, payload: asyncio.create_task(
                handle_task(payload)
            ),
        )
        print("Worker started, waiting for new tasks...")
        while True:
            await asyncio.sleep(3600)  # Keep the listener alive
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(listen_for_notifications())
