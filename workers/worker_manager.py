import asyncio
import logging
from typing import List
from workers.stripe_worker import StripeWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkerManager:
    def __init__(self):
        self.workers = []
        self.running = False

    def add_worker(self, worker):
        """Add a worker to the manager"""
        self.workers.append(worker)
        logger.info(f"➕ Added worker: {worker.worker_name}")

    async def start_all_workers(self):
        """Start all registered workers"""
        if not self.workers:
            logger.warning("⚠️ No workers registered")
            return

        self.running = True
        logger.info(f"🚀 Starting {len(self.workers)} workers...")

        # Start all workers concurrently
        tasks = [worker.start() for worker in self.workers]

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("🛑 Received shutdown signal")
            await self.stop_all_workers()

    async def stop_all_workers(self):
        """Stop all workers"""
        self.running = False
        logger.info("🔴 Stopping all workers...")

        for worker in self.workers:
            await worker.stop()

        logger.info("✅ All workers stopped")


async def main():
    """Main function to run the worker system"""
    logger.info("🎬 Starting Async Framework Demo Workers")

    # Create worker manager
    manager = WorkerManager()

    # Add workers
    stripe_worker = StripeWorker()
    manager.add_worker(stripe_worker)

    # You can add more workers here
    # manager.add_worker(OtherWorker())

    # Start all workers
    await manager.start_all_workers()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        raise
