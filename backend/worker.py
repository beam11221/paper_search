from confluent_kafka import Consumer, Producer
import multiprocessing
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models

from backend.app.core.config import settings
from backend.app.services.openai_handler import OpenAIHandler

class WorkerService:

    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.consumer = Consumer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'paper_processing_group',
            'auto.offset.reset': 'earliest',
            'partition.assignment.strategy': 'roundrobin',
        })
        
        self.consumer.subscribe(
            [settings.KAFKA_PROCESSING_TOPIC],
            on_assign=self._on_assign,
            on_revoke=self._on_revoke
        )

        #Initialize Kafka producer for status updates
        # self.producer = Producer({
        #     'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS
        # })
        
        self.openai_handler = OpenAIHandler()
        self.qdrant = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )

        self.initialize_collection()

    def _on_assign(self, consumer, partitions):
        partition_info = [f"{p.topic}-{p.partition}" for p in partitions]
        print(f"Worker {self.worker_id} assigned partitions: {partition_info}")

    def _on_revoke(self, consumer, partitions):
        partition_info = [f"{p.topic}-{p.partition}" for p in partitions]
        print(f"Worker {self.worker_id} lost partitions: {partition_info}")

    def initialize_collection(self):
        """Initialize Qdrant collection for papers"""
        try:
            self.qdrant.get_collection(settings.VECTOR_DB_COLLECTION_NAME)
        except:
            self.qdrant.create_collection(
                collection_name=settings.VECTOR_DB_COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=settings.EMBEDDING_DIM,  # OpenAI embedding dimension
                    distance=models.Distance.COSINE
                )
            )

    def delivery_report(self, err, msg):
        """Callback for producer message delivery"""
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def process_papers(self):
        """Process papers from Kafka and store in Qdrant"""
        try:
            print("Starting paper processing worker...")
            while True:
                msg = self.consumer.poll(0.5)

                if msg is None:
                    continue
                if msg.error():
                    print(f'Consumer error: {msg.error()}')
                    continue
                
                print(f"Processing message from partition {msg.partition()}")
                try:
                    # Parse message
                    paper_data = json.loads(msg.value().decode('utf-8'))
                    paper_id = paper_data['paper_id']
                    
                    print(f"Processing paper: {paper_id}")
                    
                    # Combine title and abstract for embedding
                    full_text = f"{paper_data['title']} {paper_data['abstract']}"
                    
                    # Generate embedding
                    embedding = OpenAIHandler.generate_embedding(full_text)
                    
                    # Store in Qdrant
                    self.qdrant.upsert(
                        collection_name=settings.VECTOR_DB_COLLECTION_NAME,
                        points=[
                            models.PointStruct(
                                id=paper_id,
                                vector=embedding,
                                payload={
                                    "paper_id": paper_id,
                                    "title": paper_data["title"],
                                    "authors": paper_data["authors"].split(","),
                                    "abstract": paper_data["abstract"],
                                    "published": paper_data["published"],
                                    "link": paper_data["link"]
                                }
                            )
                        ]
                    )
                    
                    # Send success status
                    status_update = {
                        'paper_id': paper_id,
                        'status': 'completed'
                    }
                    # self.producer.produce(
                    #     settings.KAFKA_STATUS_TOPIC,
                    #     json.dumps(status_update).encode('utf-8'),
                    #     callback=self.delivery_report
                    # )
                    # self.producer.poll(0)
                    
                    print(f"Successfully processed paper: {paper_id}")
                    
                except Exception as e:
                    print(f"Error processing paper: {str(e)}")
                    if 'paper_id' in locals():
                        status_update = {
                            'paper_id': paper_id,
                            'status': 'error',
                            'error': str(e)
                        }
                        # self.producer.produce(
                        #     settings.KAFKA_STATUS_TOPIC,
                        #     json.dumps(status_update).encode('utf-8'),
                        #     callback=self.delivery_report
                        # )
                        # self.producer.poll(0)

        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.consumer.close()
            # self.producer.flush()

def run_worker(worker_id):
    """Function to create and run a worker"""
    worker = WorkerService(worker_id)
    worker.process_papers()

if __name__ == "__main__":
    num_workers = settings.KAFKA_NUM_PARTITIONS
    
    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(
            target=run_worker,
            args=(i,),
            name=f"worker-{i}"
        )
        processes.append(p)
        p.start()
        print(f"Started process for worker {i}")
    
    for p in processes:
        p.join()