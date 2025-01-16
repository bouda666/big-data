from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# File to store normal observations
NORMAL_DATA_FILE = 'normal_observations.json'

# Elasticsearch index name
INDEX_NAME = "bp_fhir_index"

# Initialize Elasticsearch client
es = Elasticsearch(hosts=["http://localhost:9200"])
if not es.ping():
    logging.error("Cannot connect to Elasticsearch. Exiting...")
    exit(1)

# Ensure the index exists
if not es.indices.exists(index=INDEX_NAME):
    logging.info(f"Creating Elasticsearch index: {INDEX_NAME}")
    es.indices.create(index=INDEX_NAME)
logging.info(f"Connected to Elasticsearch and index {INDEX_NAME} is ready.")

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'fhir_observations',  # Replace with your topic name
    bootstrap_servers='localhost:9092',
    group_id='fhir_consumer_group',
    auto_offset_reset='earliest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Function to classify blood pressure categories based on FHIR data
def classify_bp(observation):
    systolic = None
    diastolic = None

    # Extract systolic and diastolic pressures from FHIR structure
    for component in observation.get("component", []):
        code = component.get("code", {}).get("coding", [{}])[0].get("code")
        if code == "8480-6":  # Systolic blood pressure
            systolic = component.get("valueQuantity", {}).get("value")
        elif code == "8462-4":  # Diastolic blood pressure
            diastolic = component.get("valueQuantity", {}).get("value")

    if systolic is None or diastolic is None:
        logging.warning(f"Missing systolic or diastolic values in observation: {observation}")
        return "unknown"

    # Classify based on blood pressure values
    if systolic < 120 and diastolic < 80:
        return "normal"
    elif 120 <= systolic <= 129 and diastolic < 80:
        return "elevated"
    elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return "hypertension_stage_1"
    elif 140 <= systolic <= 180 or 90 <= diastolic <= 120:
        return "hypertension_stage_2"
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
                es.index(index=INDEX_NAME, document=observation)
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
