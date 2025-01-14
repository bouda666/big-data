from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# File to store normal observations
NORMAL_DATA_FILE = 'normal_observations.json'

# Initialize Elasticsearch client
es = Elasticsearch(hosts=["http://localhost:9200"])
if not es.ping():
    logging.error("Cannot connect to Elasticsearch. Exiting...")
    exit(1)
logging.info("Connected to Elasticsearch.")

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'fhir_observations',  # Replace with your topic name
    bootstrap_servers='localhost:9092',
    group_id='fhir_consumer_group',
    auto_offset_reset='earliest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Function to classify blood pressure categories
def classify_bp(observation):
    systolic = observation.get('systolic_pressure', 0)
    diastolic = observation.get('diastolic_pressure', 0)

    # Normal blood pressure
    if systolic < 120 and diastolic < 80:
        return "normal"
    # Elevated blood pressure
    elif 120 <= systolic <= 129 and diastolic < 80:
        return "elevated"
    # High blood pressure (Hypertension Stage 1)
    elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return "hypertension_stage_1"
    # High blood pressure (Hypertension Stage 2)
    elif systolic >= 140 or diastolic >= 90:
        return "hypertension_stage_2"
    # Hypertensive Crisis
    elif systolic > 180 or diastolic > 120:
        return "hypertensive_crisis"
    return "unknown"

# Save normal observations to a local file
def save_to_file(observation):
    try:
        with open(NORMAL_DATA_FILE, 'a') as file:
            file.write(json.dumps(observation) + '\n')
        logging.info("Normal observation saved to file.")
    except Exception as e:
        logging.error(f"Error saving observation to file: {e}")

# Consume messages and process them
def consume_and_process():
    try:
        logging.info("Starting Kafka Consumer...")
        for message in consumer:
            observation = message.value
            logging.info(f"Consumed message: {observation}")

            # Classify the observation
            category = classify_bp(observation)
            observation['bp_category'] = category  # Add category to the observation

            if category == "normal":
                # Save normal observations to a file
                save_to_file(observation)
            else:
                # Index non-normal observations into Elasticsearch
                es.index(index="anomalies_index", document=observation)
                logging.info(f"Anomaly ({category}) indexed into Elasticsearch.")
    except Exception as e:
        logging.error(f"Error while consuming messages: {e}")
    finally:
        consumer.close()
        logging.info("Kafka Consumer stopped.")

if __name__ == "__main__":
    # Ensure the file for normal observations exists
    if not os.path.exists(NORMAL_DATA_FILE):
        open(NORMAL_DATA_FILE, 'w').close()
        logging.info(f"Created file: {NORMAL_DATA_FILE}")
    # Start consuming messages
    consume_and_process()
