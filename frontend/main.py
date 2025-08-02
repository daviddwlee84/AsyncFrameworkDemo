import streamlit as st
import requests
import json

st.title("Async Task Creator")

st.header("Create a new Stripe Customer")

name = st.text_input("Customer Name")
email = st.text_input("Customer Email")

if st.button("Create Customer"):
    if name and email:
        payload = {
            "query": """
                mutation CreateTask($taskType: String!, $payload: String!) {
                    createTask(taskType: $taskType, payload: $payload) {
                        id
                        taskType
                    }
                }
            """,
            "variables": {
                "taskType": "create_stripe_customer",
                "payload": json.dumps({"name": name, "email": email}),
            },
        }

        try:
            response = requests.post("http://127.0.0.1:8000/graphql", json=payload)
            response.raise_for_status()
            st.success("Task created successfully!")
            st.json(response.json())
        except requests.exceptions.RequestException as e:
            st.error(f"Error creating task: {e}")
            st.error(response.text)
    else:
        st.warning("Please enter both name and email.")
