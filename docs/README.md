# ECG Data Processing and Visualization Project

This project provides a complete setup for ingesting, storing, processing, and visualizing ECG data using TimescaleDB, FastAPI, and Grafana. It allows you to:

- **Ingest ECG data** from PhysioNet databases into TimescaleDB.
- **Retrieve ECG signals and annotations** through a RESTful API built with FastAPI.
- **Visualize ECG signals** in Grafana without downsampling.
- **Interact with the API** using Postman or other HTTP clients.

## Table of Contents

- [ECG Data Processing and Visualization Project](#ecg-data-processing-and-visualization-project)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
    - [Running the Application](#running-the-application)
    - [API Documentation](#api-documentation)
    - [Visualization with Grafana](#visualization-with-grafana)

## Project Structure

HealtAI/
├── README.md
├── LICENSE
├── docker-compose.yml
├── .env.example
├── init_db/
│ └── 01-init.sql
├── app/
│ ├── Dockerfile
│ ├── pyproject.toml
│ ├── poetry.lock
│ ├── main.py
│ ├── api/
│ │ ├── init.py
│ │ └── endpoints.py
│ ├── utils.py
└── docs/
├── INSTALLATION.md
├── USAGE.md
└── API_REFERENCE.md


- **docker-compose.yml**: Docker Compose configuration file to set up the services.
- **.env.example**: Example environment variables file.
- **init_db/**: Directory containing SQL scripts to initialize the TimescaleDB database.
- **app/**: Directory containing the FastAPI application and related code.
- **docs/**: Additional documentation files.

## Getting Started

### Prerequisites

- **Podman** (or Docker): Container engine to run the services.
- **Podman Compose**: To use `docker-compose.yml` with Podman.
- **Poetry**: Python dependency management tool.
- **Git**: Version control system.

### Installation

Please refer to the [Installation Guide](docs/INSTALLATION.md) for detailed instructions.

## Usage

### Running the Application

```bash
podman-compose up -d --build
```

### API Documentation
The FastAPI application provides interactive API documentation.

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
For detailed API usage, see the API Reference.

### Visualization with Grafana
Grafana is set up to visualize ECG signals from TimescaleDB.

Access Grafana: http://localhost:3000
Default Credentials:
Username: admin
Password: admin
Instructions for setting up Grafana dashboards are available in the Usage Guide.

