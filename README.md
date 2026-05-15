# Autonomous Building RAG Chatbot

A modular, AI-powered Retrieval-Augmented Generation (RAG) chatbot developed for the "Autonomous Building Project". It retrieves information from a pre-loaded knowledge base of PDF documents while allowing for dynamic, session-based PDF uploads.

## Architecture

![Architecture](architecture.png)

## Features

- **RAG Architecture**: Provides grounded, context-aware answers to user queries, strictly adhering to hallucination-prevention rules.
- **Tech Stack**: Built using Python, Flask, LangChain, ChromaDB, and Ollama.
- **Pre-loaded Knowledge**: Ingests default PDF documents for foundational knowledge base context.
- **Dynamic Uploads**: Allows dynamic, session-based PDF uploads for targeted document chat.
- **Modern UI**: Frontend interface designed for a seamless user experience.

## Getting Started


### Installation

1. Navigate to the project directory:
   ```bash
   cd AB_Chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in the `.env` file (if required).

### Running the Application

Start the Flask application:

```bash
python app.py
```

Then, navigate to the local URL provided by Flask (usually `http://127.0.0.1:5000/`) in your web browser.
