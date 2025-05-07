# AIMANDIAO Private Enterprise LLM

**AI Desktop App** is a Python-based desktop application that integrates a Flask backend and a modern Vue.js frontend, wrapped into a desktop app using PyQt6. The app primarily supports processing PDF documents, extracting contextual information, and enabling chat-based conversations through a large language model.

## Features

- **AI Chat**  
  Utilizes a Retrieval-Augmented Generation (RAG) mechanism to answer questions by combining user queries with contextual information extracted from PDFs.

- **PDF Document Processing**  
  Supports uploading PDF files, automatically parsing and splitting them into text chunks, which are then stored in a SQLite database for semantic search.

- **Vector Retrieval**  
  Uses an embedding model provided by Ollama to convert text into vector representations and retrieves relevant document chunks using cosine similarity.

- **Model Management**  
  Automatically installs and manages AI models (e.g., `deepseek-r1:1.5b`) through the Ollama framework, including starting the necessary services.

- **Desktop Execution**  
  Launches a Flask server via PyQt6 and loads the frontend in a QWebEngineView to deliver a seamless desktop experience.

## Project Directory Structure
```bash
rag_pipeline/
├── backend/
│   ├── init.py               # Optional: Backend package initializer
│   ├── server.py             # Main Flask app, registers API endpoints (e.g., /api/chat, /health)
│   ├── ollama/
│   │   ├── ollama_manager.py # Manages Ollama installation, startup, and model pulling
│   │   ├── models_config.py  # Stores model names and configurations
│   ├── pdf_helper/
│   │   ├── init.py           # Marks pdf_helper as a package
│   │   ├── embed_model.py    # Embedding model (calls Ollama /api/embed endpoint)
│   │   ├── parse.py          # PDF parsing and text splitting
│   │   ├── store.py          # Handles SQLite connections, creates virtual tables, stores PDF chunks
│   │   └── retrieval.py      # Embedding queries, text chunk retrieval, and prompt construction
│   └── routes/
│       └── sqlite_routes.py  # Endpoints for PDF upload and database clearing (/sqlite/upload, /sqlite/clear)
├── frontend/
│   ├── dist/                 # Vue.js build output
│   └── src/                  # Frontend source code
│       ├── views/
│       │   ├── Home.vue      # System status and PDF upload page
│       │   └── Chat.vue      # Chat interface (calls /api/chat endpoint)
│       └── App.vue           # Main Vue application component
├── main.py                   # Desktop launcher: starts Flask server and loads frontend with PyQt6
└── packaging/
    └── build.py              # Packaging script: uses PyInstaller and npm to create a single-file executable
