import json
import asyncio
from typing import TYPE_CHECKING

import aio_pika
import structlog

from ecs.models.schemas import EmotionalEvent

if TYPE_CHECKING:
    from ecs.services.emotion_service import EmotionService

logger = structlog.get_logger()

class EmotionQueueConsumer:
    def __init__(
        self,
        emotion_service: "EmotionService",
        connection_params: dict[str, str]
    ):
        self.emotion_service = emotion_service
        self.connection_params = connection_params
        self.connection = None
        self.channel = None
        
    async def start_consuming(self):
        """Start consuming messages from the queue using aio_pika"""
        try:
            # Create connection string
            host = self.connection_params.get("host", "rabbitmq")
            port = self.connection_params.get("port", 5672)
            username = self.connection_params.get("username", "guest")
            password = self.connection_params.get("password", "guest")
            
            connection_string = f"amqp://{username}:{password}@{host}:{port}/"
            logger.info(f"Connecting to RabbitMQ at {host}:{port}")
            
            # Connect to RabbitMQ
            self.connection = await aio_pika.connect_robust(connection_string)
            
            # Create channel
            self.channel = await self.connection.channel()
            
            # Declare queue
            queue = await self.channel.declare_queue('ecs:ingest', durable=True)
            
            # Start consuming
            logger.info("Started consuming emotional data from queue")
            await queue.consume(self._process_message)
            
            # Create future to keep the consumer running indefinitely
            future = asyncio.Future()
            
            # Wait until future is done (set by shutdown method)
            await future
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
        
    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage):
        """Process message asynchronously"""
        async with message.process():
            try:
                # Parse message body
                body = message.body.decode()
                data = json.loads(body)
                
                # Validate events
                events = [EmotionalEvent.model_validate(event) for event in data]
                
                # Process using existing service
                await self.emotion_service.ingest(events)
                
                logger.info("Successfully processed emotional data batch", count=len(events))
                
            except Exception as e:
                logger.error("Error processing emotional data", error=str(e))
                # Message will be rejected due to exception in context manager
                raise