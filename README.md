# AI-Powered Radio Interception and Semantic Analysis System

An AI-powered system for automated transcription and semantic analysis of noisy radio broadcasts. This project is designed to process audio streams, convert them to text, and extract meaningful information using Named Entity Recognition (NER).

## 🚀 Features

* **Asynchronous Processing:** Handles multiple audio files concurrently using a message broker (RabbitMQ).
* **Offline Capabilities:** The entire system can be run locally without internet access.
* **Microservices Architecture:** The system is composed of an API Gateway, a Speech-to-Text (STT) worker, and a Natural Language Processing (NLP) worker.
* **Military Slang Normalization:** Includes a custom NLP model trained to normalize military slang.
* **GPU Acceleration:** Supports CUDA for faster AI model inference.

## 📋 Prerequisites

Before you begin, ensure you have met the following requirements:
* Python 3.8+
* Docker & Docker Compose
* NVIDIA Container Toolkit (for GPU support)
* **Pre-trained NLP Model:** Must be placed in the `nlp/models` directory.

## ⚙️ Environment Variables

Create a `.env` file in the root of the project. You can copy the content below:

````env
# MongoDB
MONGO_CONNECTION_STRING=mongodb://admin:password@localhost:27017/
MONGO_DB_NAME=analysis_db

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=user
RABBITMQ_PASSWORD=password
RABBITMQ_STT_QUEUE=stt_queue
RABBITMQ_NLP_QUEUE=nlp_queue
````

## Local Setup & Execution (Without Docker)

1.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate # On Windows use: .venv\Scripts\activate
    ```

2.  **Install dependencies and the project as a local library:**
    This step uses `pyproject.toml` to install the system packages (`api`, `nlp`, `stt`) in editable mode.
    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

3.  **Start infrastructure:**
    You need to have MongoDB and RabbitMQ running locally. You can use Docker for this:
    ```bash
    docker-compose up -d rabbitmq mongodb
    ```

4.  **Run the services:**
    - **API Gateway:**
      ```bash
      uvicorn api.main:app --host 0.0.0.0 --port 8000
      ```
    - **STT Worker:**
      ```bash
      python stt/stt_main.py
      ```
    - **NLP Worker:**
      ```bash
      python nlp/nlp_main.py
      ```

## Docker Setup & Execution (Recommended)

1.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```
    The services will be available at `http://localhost:8000`.

2.  **GPU Configuration:**
    If you have an NVIDIA GPU and the NVIDIA Container Toolkit installed, the `stt` and `nlp` services will automatically use the GPU for faster processing, as configured in the `docker-compose.yml` file.

## API Documentation

Once the server is running, you can access the Swagger UI for API documentation at `http://localhost:8000/docs`.

## Project Structure

```
.
├── .dockerignore
├── .gitignore
├── config.env
├── config.py
├── docker-compose.yml
├── nlp
│   ├── data_generation
│   ├── Dockerfile
│   ├── model_training
│   ├── models.py
│   ├── nlp_main.py
│   ├── nlp.py
│   └── requirements.txt
├── README.md
├── requirements.txt
├── api
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── rabbit.py
│   ├── repository.py
│   └── requirements.txt
└── stt
    ├── Dockerfile
    ├── download_model.py
    ├── models.py
    ├── requirements.txt
    ├── stt_main.py
    └── stt.py
````