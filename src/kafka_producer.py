from kafka import KafkaProducer
import json
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize messages as JSON
)

# Topic name
TOPIC = 'fhir_observations'

# Function to generate mixed observations
def generate_messages():
    for i in range(100):  # Number of messages to produce
        # Randomly generate blood pressure values
        if i % 5 == 0:  # Generate normal observations every 5th message
            systolic = random.randint(90, 119)  # Normal systolic range
            diastolic = random.randint(60, 79)  # Normal diastolic range
        else:  # Generate anomalous observations
            systolic = random.randint(120, 200)  # Elevated or hypertensive systolic
            diastolic = random.randint(50, 130)  # Elevated or hypertensive diastolic

        # Create the observation message
        message = {
            'patient_id': f'patient-{i}',
            'systolic_pressure': systolic,
            'diastolic_pressure': diastolic,
            'timestamp': time.time()
        }

        # Log and send the message
        logging.info(f"Producing message: {message}")
        producer.send(TOPIC, value=message)

        # Add a small delay to simulate real-time data generation
        time.sleep(0.1)

# Run the producer
if __name__ == "__main__":
    try:
        logging.info("Starting Kafka Producer...")
        generate_messages()
    except Exception as e:
        logging.error(f"Error in Kafka Producer: {e}")
    finally:
        producer.close()
        logging.info("Kafka Producer stopped.")
