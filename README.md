# Blood Pressure Monitoring System

## **Overview**

This project implements a system for real-time monitoring and analysis of blood pressure data. It generates, processes, and visualizes blood pressure readings to detect anomalies (e.g., hypertension or hypertensive crisis) and provides a dashboard for analysis. The system leverages Kafka, Elasticsearch, and Kibana to handle data ingestion, storage, and visualization.

---

## **System Architecture**

### **Components**

1. **Data Generation (Producer):**

   - Generates synthetic blood pressure readings.
   - Sends data to Kafka topics.

2. **Data Processing (Consumer):**

   - Reads messages from Kafka topics.
   - Classifies observations as normal or anomalous.
   - Saves normal observations to a local file.
   - Indexes anomalies into Elasticsearch.

3. **Data Visualization (Dashboard):**

   - Uses Kibana to create visualizations and dashboards.
   - Displays distributions, trends, and critical observations.

---

## **Project Setup**

### **Prerequisites**

- Docker
- Python (>=3.8)
- Kafka
- Elasticsearch
- Kibana

### **Installation**

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/blood-pressure-monitoring.git
   cd blood-pressure-monitoring
   ```

2. Start the Docker containers for Kafka, Elasticsearch, and Kibana:

   ```bash
   docker-compose up
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## **Usage**

### **1. Start the Kafka Producer**

- Generates 10,000 blood pressure observations and sends them to the Kafka topic.
- Run the producer:
  ```bash
  python src/kafka_producer.py
  ```

### **2. Start the Kafka Consumer**

- Processes incoming messages, classifies observations, and stores them appropriately.
- Run the consumer:
  ```bash
  python src/kafka_consumer.py
  ```

### **3. Access Kibana Dashboard**

- Open Kibana in your browser:
  ```
  http://localhost:5601
  ```
- Create visualizations and dashboards for the indexed anomalies.

---

## **Features**

### **Data Classification**

- **Normal Observations:**
  - Systolic < 120 and Diastolic < 80.
  - Saved in `normal_observations.json`.
- **Anomalies:**
  - Elevated, Hypertension, or Hypertensive Crisis.
  - Indexed into Elasticsearch (`anomalies_index`).

### **Visualizations**

1. **Vertical Bar Chart:** Distribution of blood pressure categories.
2. **Line Chart:** Trends of systolic and diastolic pressures over time.
3. **Pie Chart:** Proportion of observations by category.
4. **Gauge:** Count of critical cases (e.g., Hypertensive Crisis).
5. **Heat Map:** Distribution of systolic vs. diastolic pressures.

---

## **Configuration**

### **Kafka**

- Topic: `fhir_observations`

### **Elasticsearch**

- Index: `anomalies_index`

### **Kibana**

- Visualizations and dashboards are configured using the data from `anomalies_index`.

---

## **File Structure**

```
project-directory/
├── docker-compose.yml        # Docker configuration for Kafka, Elasticsearch, and Kibana
├── requirements.txt          # Python dependencies
├── src/
│   ├── kafka_producer.py     # Kafka producer script
│   ├── kafka_consumer.py     # Kafka consumer script
│   └── normal_observations.json  # File storing normal observations
└── README.md                 # Project documentation
```

---

## **Troubleshooting**

1. **Kafka Connection Issues:**

   - Ensure Kafka is running and reachable at `localhost:9092`.
   - Verify the topic `fhir_observations` exists.

2. **Elasticsearch Not Indexing:**

   - Ensure Elasticsearch is running and reachable at `localhost:9200`.
   - Check if the `anomalies_index` exists using:
     ```bash
     curl http://localhost:9200/_cat/indices?v
     ```

3. **Kibana Not Loading:**

   - Ensure Kibana is running and accessible at `http://localhost:5601`.

---

## **Future Improvements**

- Add real-time alerts for critical observations using Kibana Rules.
- Integrate additional health metrics (e.g., heart rate).
- Implement data encryption for secure transmission.
