# setup_kafka.py
from confluent_kafka.admin import AdminClient, NewTopic
from backend.app.core.config import settings

def setup_partitioned_topic():
    try:
        admin_client = AdminClient({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS
        })
        
        # Check if topic exists
        metadata = admin_client.list_topics(timeout=10)
        if settings.KAFKA_PROCESSING_TOPIC not in metadata.topics:
            # Create topic with multiple partitions
            topic = NewTopic(
                settings.KAFKA_PROCESSING_TOPIC,
                num_partitions=settings.KAFKA_NUM_PARTITIONS,  # Adjust based on your needs
                replication_factor=1
            )
            
            admin_client.create_topics([topic])
            print(f"Created topic {settings.KAFKA_PROCESSING_TOPIC} with {settings.KAFKA_NUM_PARTITIONS} partitions")
        else:
            print(f"Topic {settings.KAFKA_PROCESSING_TOPIC} already exists")
            
    except Exception as e:
        print(f"Error setting up Kafka topic: {str(e)}")

if __name__ == "__main__":
    setup_partitioned_topic()