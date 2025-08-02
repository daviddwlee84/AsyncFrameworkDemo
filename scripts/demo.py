#!/usr/bin/env python3
"""
Demo script to test the async framework
"""
import asyncio
import aiohttp
import json
import time
from datetime import datetime

GRAPHQL_ENDPOINT = "http://127.0.0.1:8000/graphql"


async def send_graphql_query(session, query, variables=None):
    """Send GraphQL query"""
    payload = {"query": query, "variables": variables or {}}

    try:
        async with session.post(GRAPHQL_ENDPOINT, json=payload) as response:
            return await response.json()
    except Exception as e:
        return {"errors": [{"message": str(e)}]}


async def create_customer_task(session, email, name):
    """Create a Stripe customer creation task"""
    query = """
    mutation CreateCustomer($email: String!, $name: String!) {
        createStripeCustomerTask(email: $email, name: $name) {
            id
            type
            status
            payload
            createdAt
        }
    }
    """
    return await send_graphql_query(session, query, {"email": email, "name": name})


async def create_payment_task(session, amount, currency, customer_id):
    """Create a Stripe payment task"""
    query = """
    mutation CreatePayment($amount: Int!, $currency: String!, $customerId: String!) {
        createStripePaymentTask(amount: $amount, currency: $currency, customerId: $customerId) {
            id
            type
            status
            payload
            createdAt
        }
    }
    """
    return await send_graphql_query(
        session,
        query,
        {"amount": amount, "currency": currency, "customerId": customer_id},
    )


async def get_task_status(session, task_id):
    """Get task status"""
    query = """
    query GetTask($taskId: String!) {
        getTask(taskId: $taskId) {
            id
            type
            status
            result
            errorMessage
            updatedAt
        }
    }
    """
    return await send_graphql_query(session, query, {"taskId": task_id})


async def wait_for_task_completion(session, task_id, max_wait=30):
    """Wait for task to complete"""
    print(f"⏳ Waiting for task {task_id[:8]}... to complete")

    for i in range(max_wait):
        response = await get_task_status(session, task_id)

        if "errors" in response:
            print(f"❌ Error checking task status: {response['errors'][0]['message']}")
            return None

        task = response["data"]["getTask"]
        if not task:
            print(f"❌ Task {task_id} not found")
            return None

        status = task["status"]
        print(f"📊 Task status: {status}")

        if status in ["completed", "failed"]:
            return task

        await asyncio.sleep(1)

    print(f"⏰ Timeout waiting for task {task_id}")
    return None


async def run_demo():
    """Run the complete demo"""
    print("🎬 Starting Async Framework Demo")
    print("=" * 50)

    async with aiohttp.ClientSession() as session:
        # Test 1: Create a customer
        print("\n📝 Test 1: Creating a Stripe customer")
        customer_response = await create_customer_task(
            session, "demo@example.com", "Demo Customer"
        )

        if "errors" in customer_response:
            print(
                f"❌ Failed to create customer task: {customer_response['errors'][0]['message']}"
            )
            return

        customer_task = customer_response["data"]["createStripeCustomerTask"]
        customer_task_id = customer_task["id"]
        print(f"✅ Customer task created: {customer_task_id[:8]}...")

        # Wait for customer creation to complete
        completed_customer_task = await wait_for_task_completion(
            session, customer_task_id
        )

        if not completed_customer_task:
            print("❌ Customer task failed or timed out")
            return

        if completed_customer_task["status"] == "failed":
            print(f"❌ Customer task failed: {completed_customer_task['errorMessage']}")
            return

        print("✅ Customer created successfully!")
        if completed_customer_task["result"]:
            customer_id = completed_customer_task["result"].get("customer_id")
            print(f"📋 Customer ID: {customer_id}")
        else:
            print("⚠️ No customer ID in result, using simulated ID")
            customer_id = "cus_simulated_demo"

        # Test 2: Create a payment
        print(f"\n💳 Test 2: Creating a payment for customer {customer_id}")
        payment_response = await create_payment_task(
            session, 2000, "usd", customer_id  # $20.00
        )

        if "errors" in payment_response:
            print(
                f"❌ Failed to create payment task: {payment_response['errors'][0]['message']}"
            )
            return

        payment_task = payment_response["data"]["createStripePaymentTask"]
        payment_task_id = payment_task["id"]
        print(f"✅ Payment task created: {payment_task_id[:8]}...")

        # Wait for payment to complete
        completed_payment_task = await wait_for_task_completion(
            session, payment_task_id
        )

        if not completed_payment_task:
            print("❌ Payment task failed or timed out")
            return

        if completed_payment_task["status"] == "failed":
            print(f"❌ Payment task failed: {completed_payment_task['errorMessage']}")
            return

        print("✅ Payment created successfully!")
        if completed_payment_task["result"]:
            payment_intent_id = completed_payment_task["result"].get(
                "payment_intent_id"
            )
            print(f"📋 Payment Intent ID: {payment_intent_id}")

        print("\n🎉 Demo completed successfully!")
        print("📊 Both tasks processed asynchronously via PostgreSQL triggers")


def main():
    try:
        print("🔌 Testing connection to GraphQL endpoint...")

        # Test if backend is running
        import requests

        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is running")
            else:
                print("❌ Backend is not responding correctly")
                return
        except requests.exceptions.RequestException:
            print(
                "❌ Backend is not running. Please start it with: python scripts/start_backend.py"
            )
            return

        # Run the async demo
        asyncio.run(run_demo())

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
