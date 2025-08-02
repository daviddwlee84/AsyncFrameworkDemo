import os
import stripe
import logging
from typing import Dict, Any
from workers.base_worker import BaseWorker
from backend.models.task import TaskType
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class StripeWorker(BaseWorker):
    def __init__(self):
        super().__init__("StripeWorker")

        # Initialize Stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe.api_key:
            logger.warning(
                "⚠️ STRIPE_SECRET_KEY not set. Stripe operations will be simulated."
            )
            self.stripe_enabled = False
        else:
            self.stripe_enabled = True
            logger.info("🔑 Stripe API key configured")

    def can_handle_task(self, task_type: str) -> bool:
        """Check if this worker can handle Stripe-related tasks"""
        stripe_tasks = [
            TaskType.STRIPE_CREATE_CUSTOMER,
            TaskType.STRIPE_CREATE_PAYMENT,
            TaskType.STRIPE_REFUND_PAYMENT,
        ]
        return task_type in stripe_tasks

    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Stripe-related tasks"""
        task_type = task_data.get("type")
        payload = task_data.get("payload", {})

        if task_type == TaskType.STRIPE_CREATE_CUSTOMER:
            return await self._create_customer(payload)
        elif task_type == TaskType.STRIPE_CREATE_PAYMENT:
            return await self._create_payment(payload)
        elif task_type == TaskType.STRIPE_REFUND_PAYMENT:
            return await self._refund_payment(payload)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _create_customer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Stripe customer"""
        email = payload.get("email")
        name = payload.get("name")

        if not email:
            raise ValueError("Email is required for customer creation")

        if not self.stripe_enabled:
            # Simulate Stripe customer creation
            logger.info(f"🧪 Simulating Stripe customer creation for {email}")
            return {
                "customer_id": f"cus_simulated_{email.replace('@', '_').replace('.', '_')}",
                "email": email,
                "name": name,
                "simulated": True,
            }

        try:
            customer = stripe.Customer.create(
                email=email, name=name, metadata={"created_by": "async_framework_demo"}
            )

            logger.info(f"✅ Created Stripe customer: {customer.id}")
            return {
                "customer_id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": customer.created,
            }

        except stripe.error.StripeError as e:
            logger.error(f"❌ Stripe error: {e}")
            raise Exception(f"Stripe API error: {e}")

    async def _create_payment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Stripe payment intent"""
        amount = payload.get("amount")
        currency = payload.get("currency", "usd")
        customer_id = payload.get("customer_id")

        if not amount:
            raise ValueError("Amount is required for payment creation")

        if not self.stripe_enabled:
            # Simulate payment creation
            logger.info(f"🧪 Simulating Stripe payment of {amount} {currency}")
            return {
                "payment_intent_id": f"pi_simulated_{amount}_{currency}",
                "amount": amount,
                "currency": currency,
                "customer_id": customer_id,
                "status": "succeeded",
                "simulated": True,
            }

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                automatic_payment_methods={"enabled": True},
                metadata={"created_by": "async_framework_demo"},
            )

            logger.info(f"✅ Created Stripe payment intent: {payment_intent.id}")
            return {
                "payment_intent_id": payment_intent.id,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "customer_id": payment_intent.customer,
                "status": payment_intent.status,
                "client_secret": payment_intent.client_secret,
            }

        except stripe.error.StripeError as e:
            logger.error(f"❌ Stripe error: {e}")
            raise Exception(f"Stripe API error: {e}")

    async def _refund_payment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Refund a Stripe payment"""
        payment_intent_id = payload.get("payment_intent_id")
        amount = payload.get("amount")  # Optional: partial refund

        if not payment_intent_id:
            raise ValueError("Payment intent ID is required for refund")

        if not self.stripe_enabled:
            # Simulate refund
            logger.info(f"🧪 Simulating Stripe refund for {payment_intent_id}")
            return {
                "refund_id": f"re_simulated_{payment_intent_id}",
                "payment_intent_id": payment_intent_id,
                "amount": amount,
                "status": "succeeded",
                "simulated": True,
            }

        try:
            refund_data = {"payment_intent": payment_intent_id}
            if amount:
                refund_data["amount"] = amount

            refund = stripe.Refund.create(**refund_data)

            logger.info(f"✅ Created Stripe refund: {refund.id}")
            return {
                "refund_id": refund.id,
                "payment_intent_id": refund.payment_intent,
                "amount": refund.amount,
                "status": refund.status,
            }

        except stripe.error.StripeError as e:
            logger.error(f"❌ Stripe error: {e}")
            raise Exception(f"Stripe API error: {e}")
