import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="Async Framework Demo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Constants
GRAPHQL_ENDPOINT = "http://127.0.0.1:8000/graphql"


def send_graphql_query(
    query: str, variables: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Send GraphQL query to the backend"""
    payload = {"query": query, "variables": variables or {}}

    try:
        response = requests.post(GRAPHQL_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {e}")
        return {"errors": [{"message": str(e)}]}


def create_stripe_customer_task(email: str, name: str) -> Dict[str, Any]:
    """Create a Stripe customer creation task"""
    query = """
    mutation CreateStripeCustomerTask($email: String!, $name: String!) {
        createStripeCustomerTask(email: $email, name: $name) {
            id
            type
            status
            payload
            createdAt
        }
    }
    """
    variables = {"email": email, "name": name}
    return send_graphql_query(query, variables)


def create_stripe_payment_task(
    amount: int, currency: str, customer_id: str
) -> Dict[str, Any]:
    """Create a Stripe payment task"""
    query = """
    mutation CreateStripePaymentTask($amount: Int!, $currency: String!, $customerId: String!) {
        createStripePaymentTask(amount: $amount, currency: $currency, customerId: $customerId) {
            id
            type
            status
            payload
            createdAt
        }
    }
    """
    variables = {"amount": amount, "currency": currency, "customerId": customer_id}
    return send_graphql_query(query, variables)


def get_tasks(limit: int = 20, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get list of tasks"""
    query = """
    query GetTasks($limit: Int!, $status: String) {
        getTasks(limit: $limit, status: $status) {
            id
            type
            status
            payload
            result
            errorMessage
            createdAt
            updatedAt
            retries
            maxRetries
        }
    }
    """
    variables = {"limit": limit}
    if status:
        variables["status"] = status

    response = send_graphql_query(query, variables)
    if "data" in response and response["data"]["getTasks"]:
        return response["data"]["getTasks"]
    return []


def get_task_by_id(task_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific task by ID"""
    query = """
    query GetTask($taskId: String!) {
        getTask(taskId: $taskId) {
            id
            type
            status
            payload
            result
            errorMessage
            createdAt
            updatedAt
            retries
            maxRetries
        }
    }
    """
    variables = {"taskId": task_id}
    response = send_graphql_query(query, variables)
    if "data" in response and response["data"]["getTask"]:
        return response["data"]["getTask"]
    return None


def main():
    st.title("⚡ Async Framework Demo")
    st.markdown("### GraphQL → PostgreSQL → Workers → Stripe API")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        [
            "🏠 Home",
            "👤 Create Customer",
            "💳 Create Payment",
            "📋 View Tasks",
            "🔍 Task Details",
        ],
    )

    if page == "🏠 Home":
        show_home_page()
    elif page == "👤 Create Customer":
        show_create_customer_page()
    elif page == "💳 Create Payment":
        show_create_payment_page()
    elif page == "📋 View Tasks":
        show_tasks_page()
    elif page == "🔍 Task Details":
        show_task_details_page()


def show_home_page():
    st.header("Welcome to the Async Framework Demo")

    st.markdown(
        """
    This demo showcases an asynchronous task processing framework with the following architecture:
    
    1. **Frontend (Streamlit)** → Submits tasks via GraphQL
    2. **GraphQL API** → Stores tasks in PostgreSQL  
    3. **PostgreSQL Triggers** → Send notifications to workers
    4. **Workers** → Process tasks and call Stripe API
    
    ### Features:
    - ✅ GraphQL API with Strawberry
    - ✅ PostgreSQL with triggers and notifications  
    - ✅ Async workers listening to database events
    - ✅ Stripe API integration
    - ✅ Real-time task status updates
    """
    )

    st.markdown("### Quick Start")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("**Step 1:** Create a Stripe customer")
    with col2:
        st.info("**Step 2:** Create a payment for the customer")
    with col3:
        st.info("**Step 3:** View task status and results")

    # Show recent tasks
    st.markdown("### Recent Tasks")
    tasks = get_tasks(limit=5)
    if tasks:
        for task in tasks:
            status_color = {
                "pending": "🟡",
                "processing": "🔵",
                "completed": "🟢",
                "failed": "🔴",
            }.get(task["status"], "⚪")

            st.markdown(
                f"{status_color} **{task['type']}** - {task['status']} - {task['id'][:8]}..."
            )
    else:
        st.info("No tasks found. Create some tasks to see them here!")


def show_create_customer_page():
    st.header("👤 Create Stripe Customer")
    st.markdown("Create a new Stripe customer asynchronously")

    with st.form("create_customer_form"):
        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input("Email Address", placeholder="customer@example.com")
        with col2:
            name = st.text_input("Customer Name", placeholder="John Doe")

        submitted = st.form_submit_button("🚀 Create Customer Task")

        if submitted:
            if not email or not name:
                st.error("Please fill in all fields")
                return

            with st.spinner("Creating customer task..."):
                response = create_stripe_customer_task(email, name)

                if "errors" in response:
                    st.error(f"Error: {response['errors'][0]['message']}")
                else:
                    task = response["data"]["createStripeCustomerTask"]
                    st.success(f"✅ Task created successfully!")
                    st.json(task)

                    # Auto-refresh to show task progress
                    time.sleep(2)
                    st.rerun()


def show_create_payment_page():
    st.header("💳 Create Stripe Payment")
    st.markdown("Create a payment intent for an existing customer")

    with st.form("create_payment_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            amount = st.number_input(
                "Amount (cents)", min_value=1, value=2000, step=100
            )
        with col2:
            currency = st.selectbox("Currency", ["usd", "eur", "gbp"], index=0)
        with col3:
            customer_id = st.text_input("Customer ID", placeholder="cus_...")

        submitted = st.form_submit_button("💳 Create Payment Task")

        if submitted:
            if not customer_id:
                st.error("Please enter a customer ID")
                return

            with st.spinner("Creating payment task..."):
                response = create_stripe_payment_task(amount, currency, customer_id)

                if "errors" in response:
                    st.error(f"Error: {response['errors'][0]['message']}")
                else:
                    task = response["data"]["createStripePaymentTask"]
                    st.success(f"✅ Payment task created successfully!")
                    st.json(task)

                    # Auto-refresh to show task progress
                    time.sleep(2)
                    st.rerun()


def show_tasks_page():
    st.header("📋 Task Dashboard")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status", ["All", "pending", "processing", "completed", "failed"]
        )
    with col2:
        limit = st.number_input("Number of tasks", min_value=5, max_value=100, value=20)
    with col3:
        auto_refresh = st.checkbox("Auto refresh (5s)", value=False)

    # Get tasks
    status = None if status_filter == "All" else status_filter
    tasks = get_tasks(limit=limit, status=status)

    if tasks:
        st.markdown(f"### Found {len(tasks)} tasks")

        for task in tasks:
            with st.expander(
                f"{task['type']} - {task['status']} - {task['id'][:8]}..."
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Task Info:**")
                    st.write(f"ID: `{task['id']}`")
                    st.write(f"Type: {task['type']}")
                    st.write(f"Status: {task['status']}")
                    st.write(f"Created: {task['createdAt']}")
                    st.write(f"Updated: {task['updatedAt']}")
                    st.write(f"Retries: {task['retries']}/{task['maxRetries']}")

                with col2:
                    st.markdown("**Payload:**")
                    st.json(task["payload"])

                    if task["result"]:
                        st.markdown("**Result:**")
                        st.json(task["result"])

                    if task["errorMessage"]:
                        st.markdown("**Error:**")
                        st.error(task["errorMessage"])
    else:
        st.info("No tasks found with the current filters")

    # Auto refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()


def show_task_details_page():
    st.header("🔍 Task Details")

    task_id = st.text_input(
        "Enter Task ID", placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    )

    if st.button("🔍 Get Task Details") and task_id:
        with st.spinner("Fetching task details..."):
            task = get_task_by_id(task_id)

            if task:
                st.success("✅ Task found!")

                # Task overview
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Status", task["status"])
                with col2:
                    st.metric("Type", task["type"])
                with col3:
                    st.metric("Retries", f"{task['retries']}/{task['maxRetries']}")
                with col4:
                    created_time = datetime.fromisoformat(
                        task["createdAt"].replace("Z", "+00:00")
                    )
                    st.metric("Created", created_time.strftime("%H:%M:%S"))

                # Detailed information
                st.markdown("### Task Details")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Payload:**")
                    st.json(task["payload"])

                with col2:
                    if task["result"]:
                        st.markdown("**Result:**")
                        st.json(task["result"])
                    else:
                        st.info("No result yet")

                if task["errorMessage"]:
                    st.markdown("**Error Message:**")
                    st.error(task["errorMessage"])

                # Timeline
                st.markdown("### Timeline")
                st.write(f"**Created:** {task['createdAt']}")
                st.write(f"**Last Updated:** {task['updatedAt']}")

            else:
                st.error("Task not found")


if __name__ == "__main__":
    main()
