import uuid
import json
import time
import random
import os
import pika
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import List, Dict, Any

# User IDs from seed-dev script
USER_IDS = [
    "11111111-1111-1111-1111-111111111111",  # USER_1_ID
    "22222222-2222-2222-2222-222222222222",  # USER_2_ID
    "33333333-3333-3333-3333-333333333333",  # USER_3_ID - no events of any kind
    "44444444-4444-4444-4444-444444444444",  # USER_4_ID - transactions only
    "55555555-5555-5555-5555-555555555555",  # USER_5_ID - emotions only
    "66666666-6666-6666-6666-666666666666",  # USER_6_ID - mixed + accepted offer/account
    "77777777-7777-7777-7777-777777777777",  # USER_7_ID - expired assessment + expired offer
    "88888888-8888-8888-8888-888888888888",  # USER_8_ID - assessment only, no offer
]

# Emotion types (must match PrimaryEmotion enum exactly)
PRIMARY_EMOTIONS = ["happiness", "sadness", "fear", "anger", "surprise", "disgust"]

class EmotionalEventFactory:
    """Factory for generating realistic emotional events"""
    
    @staticmethod
    def create_event(user_id: str) -> Dict[str, Any]:
        """Create a single emotional event for the given user"""
        # Select primary emotion
        emotion_primary = random.choice(PRIMARY_EMOTIONS)
        
        # Generate confidence level (higher for more extreme emotions)
        emotion_confidence = round(random.uniform(0.5, 1.0), 2)
        
        # Generate valence (negative for negative emotions, positive for positive)
        if emotion_primary in ["sadness", "fear", "anger", "disgust"]:
            valence = round(random.uniform(0.0, 0.4), 2)  # Negative emotions
        elif emotion_primary == "surprise":
            valence = round(random.uniform(0.2, 0.8), 2)  # Surprise can be positive or negative
        else:
            valence = round(random.uniform(0.6, 1.0), 2)  # Positive emotions
        
        # Generate arousal (higher for more intense emotions)
        if emotion_primary in ["fear", "anger", "surprise"]:
            arousal = round(random.uniform(0.6, 1.0), 2)  # High arousal
        else:
            arousal = round(random.uniform(0.2, 0.8), 2)  # Moderate arousal
        
        # The event needs to match the schema in ecs/models/schemas/emotion.py
        return {
            "event_id": str(uuid.uuid4()),  # UUID in JSON
            "user_id": user_id,             # UUID in JSON
            "captured_at": datetime.now(timezone.utc).isoformat(), # ISO format for datetime
            "emotion_primary": emotion_primary, # Must match enum values
            "emotion_confidence": emotion_confidence,
            "arousal": arousal,
            "valence": valence
        }
    
    @staticmethod
    def create_batch(num_events: int = 5) -> List[Dict[str, Any]]:
        """Create a batch of random emotional events"""
        events = []
        
        # Focus on users that should have emotional data
        emotional_users = [
            USER_IDS[0],  # USER_1_ID
            USER_IDS[1],  # USER_2_ID
            USER_IDS[4],  # USER_5_ID - emotions only
            USER_IDS[5],  # USER_6_ID - mixed
        ]
        
        for _ in range(num_events):
            user_id = random.choice(emotional_users)
            events.append(EmotionalEventFactory.create_event(user_id))
            
        return events

# Try to load environment variables from .env file
def load_env_from_file():
    """Try to load environment variables from .env file"""
    # Look for .env file in the current directory and parent directories
    current_dir = Path.cwd()
    
    # Check current directory and up to 3 parent directories
    for _ in range(4):
        env_file = current_dir / ".env"
        if env_file.exists():
            print(f"Loading environment from: {env_file}")
            load_dotenv(env_file)
            return True
        current_dir = current_dir.parent
    
    # Check if we're in a subdirectory of the project
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"Loading environment from: {env_file}")
        load_dotenv(env_file)
        return True
        
    return False

def connect_rabbitmq():
    """Establish connection to RabbitMQ and return channel"""
    try:
        # Try to load from .env file first
        loaded = load_env_from_file()
        
        # Check if we're running locally or in Docker
        running_in_docker = os.path.exists('/.dockerenv')
        
        # Get connection details from environment variables or use defaults
        # for local development
        host = os.environ.get('RABBITMQ_HOST', 'localhost')
        
        # If we're running on the host machine (not in Docker) and the host is set to a Docker service name,
        # override it to use localhost
        if not running_in_docker and host not in ['localhost', '127.0.0.1']:
            print(f"Detected Docker service name '{host}' while running on host machine.")
            print("Overriding to 'localhost' for local development.")
            host = 'localhost'
            
        user = os.environ.get('RABBITMQ_USER', 'guest') 
        password = os.environ.get('RABBITMQ_PASS', 'guest')
        port = int(os.environ.get('RABBITMQ_PORT', '5672'))
        
        print(f"Connecting to RabbitMQ at {host}:{port} as user '{user}'...")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(user, password)
            )
        )
        channel = connection.channel()
        
        # Declare queue - use the same name and properties as the consumer (ecs:ingest)
        channel.queue_declare(queue='ecs:ingest', durable=True)
        
        return connection, channel
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        raise

def main():
    print("Starting emotional event producer...")
    
    connection = None
    try:
        connection, channel = connect_rabbitmq()
        
        # Run indefinitely, sending events every few seconds
        batch_count = 0
        while True:
            batch_count += 1
            
            # Create a batch of events
            batch_size = random.randint(1, 10)  # Random batch size
            events = EmotionalEventFactory.create_batch(batch_size)
            
            # Convert to JSON
            message = json.dumps(events)
            
            # Send to queue - use the correct queue name 'ecs:ingest'
            channel.basic_publish(
                exchange='',
                routing_key='ecs:ingest',
                body=message
            )
            
            print(f"Batch #{batch_count}: Sent {len(events)} events")
            
            # Sleep for a random interval (1-5 seconds)
            sleep_time = random.uniform(1, 5)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nStopping event producer")
    except Exception as e:
        print(f"Error in event producer: {e}")
    finally:
        if connection is not None and connection.is_open:
            connection.close()
            print("Connection closed")

if __name__ == "__main__":
    main()