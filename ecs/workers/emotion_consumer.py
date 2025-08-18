import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from ecs.core.config import settings
from ecs.services.consumers import EmotionQueueConsumer
from ecs.services.emotion_service import EmotionService
from ecs.repositories.implementations.emotion_repository import EmotionalEventsRepository

# Emotional events consumer process entrypoint

async def main():
    engine = create_async_engine(settings.DB_URL)
    SessionLocal = async_sessionmaker(
        bind=engine, 
        autoflush=False, 
        autocommit=False, 
        expire_on_commit=False
    )
    session = SessionLocal()

    try:
        # Initialize repositories and services manually
        emotion_repo = EmotionalEventsRepository()
        emotion_service = EmotionService(emotion_repo, session)
        
        # Create consumer
        consumer = EmotionQueueConsumer(
            emotion_service=emotion_service,
            connection_params={
                "host": settings.RABBITMQ_HOST,
                "port": settings.RABBITMQ_PORT,
                "username": settings.RABBITMQ_USER,
                "password": settings.RABBITMQ_PASS
            }
        )
        
        # Start consuming
        await consumer.start_consuming()
    finally:
        await session.close()
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())