# Academic Paper Search and Visualization System

A system for searching and visualizing academic papers using vector embeddings and graph-based visualization. The system processes academic papers, generates embeddings using OpenAI's API, and provides an interactive interface for exploring paper relationships.

## Architecture

The system consists of three main components:

1. **Backend API Service (FastAPI)**
   - Handles paper submissions and search queries
   - Interfaces with OpenAI API for embedding generation
   - Communicates with Qdrant for vector similarity search

2. **Worker Service**
   - Processes papers from Kafka queue
   - Generates embeddings using OpenAI API
   - Stores vectors and metadata in Qdrant

3. **Frontend (Streamlit)**
   - Provides user interface for paper submission and search
   - Visualizes paper relationships using interactive graphs
   - Displays search results and paper details

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Python 3.9+

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Application

1. Start all services using Docker Compose:
```bash
docker-compose up -d
```

2. Access the services:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:7890
   - Qdrant UI: http://localhost:6333/dashboard

## Project Structure

```
├── backend/                 # Backend API and Worker services
│   ├── app/                # Main application code
│   │   ├── api/           # API routes and endpoints
│   │   ├── core/          # Core configurations
│   │   ├── models/        # Data models
│   │   └── services/      # Business logic services
│   ├── Dockerfile         # Backend API Dockerfile
│   └── Dockerfile.worker  # Worker service Dockerfile
├── frontend/              # Streamlit frontend application
│   ├── api/              # API client
│   ├── core/             # Core configurations
│   ├── ui/               # UI components
│   └── utils/            # Utility functions
└── scripts/              # Utility scripts and notebooks
```

## Development

### Backend Development

1. Set up a Conda environment:

2. Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Run the FastAPI server:
```bash
python -m backend.main
```

### Frontend Development

1. Install frontend dependencies:
```bash
pip install -r frontend/requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run frontend/app.py
```

### Worker
```bash
python -m backend.worker
```


## Features

- **Paper Submission**: Submit academic papers with metadata
- **Vector Search**: Search papers using natural language queries
- **Graph Visualization**: Explore paper relationships through interactive graphs
- **Real-time Processing**: Asynchronous processing using Kafka
- **Scalable Architecture**: Distributed system design for handling large datasets

## API Documentation

Once the backend is running, access the API documentation at:
- Swagger UI: http://localhost:7890/docs
- ReDoc: http://localhost:7890/redoc
