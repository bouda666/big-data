from kafka import KafkaProducer
import json
import logging
import time
import random
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize messages as JSON
)

# Topic name
TOPIC = 'fhir_observations'

# Function to generate mixed observations in FHIR format
def generate_messages():
    for i in range(100):  # Number of messages to produce
        # Randomly generate blood pressure values
        if i % 5 == 0:  # Generate normal observations every 5th message
            systolic = random.randint(90, 119)  # Normal systolic range
            diastolic = random.randint(60, 79)  # Normal diastolic range
        else:  # Generate anomalous observations
            systolic = random.randint(120, 200)  # Elevated or hypertensive systolic
            diastolic = random.randint(50, 130)  # Elevated or hypertensive diastolic

        # Create the observation message in FHIR format
        message = {
            "resourceType": "Observation",
            "id": f"blood-pressure-{i}",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure panel with all children optional"
                    }
                ],
                "text": "Blood pressure systolic & diastolic"
            },
            "subject": {
                "reference": f"Patient/{i}"
            },
            "effectiveDateTime": datetime.now().isoformat(),
            "component": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": systolic,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                },
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": diastolic,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                }
            ]
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
