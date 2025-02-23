# AIM4Productivity: Proof of Concept of an AI Onboarding assistant

This prototype was developed in the context of a 24h Market-Validation hackathon at the [2025 Founder's Retreat of the Entrepreneur Club association at EPFL/UNIL](https://www.ec-epfl-unil.org/founders-retreat). It is far from perfect and was developed over a short period of time to have something to demonstrate the direction of our idea.

## How this project came to be

The task was to think of some problems one faces, and try to go further into each one and iterating until you come into a niche where a solution might appear.

Our idea came from the challenges we faced during internships where onboarding wasted more time than it should because of lack of resources to assign full-time mentors and the bureaucracy in-place.
We realized that although the ideal would be to have a mentor that can be there to help us get settled into a company's codeabase, this is rarely the case since said mentor can very well be busy with other tasks, and might only be able to answer a small subset of questions.

This prototype shows how one can use RAG Retrieval Augmentated Generation (RAG) to run an LLM chatbot which bases its responses off of pre-loaded documents. This can be documentation on the current codebase, but it can also be expanded to utilize many more resources.
In this first iteration, the user's CV is requested so that the chatbot can get an idea of their level of expertise in certain topics, and it can adapt its explanations accordingly. In practice, this might be replaced by pre-loading the user's job description, or a technical assessment by hiring managers so that it can be further specialized.

The overall Founder's retreat was an absolutely amazing experience, and it pushed me and my fellow participants to go forward with finding new ideas and contacting people for complementing said ideas. Being a BsC Computer Science student, I have experience as a developer but I now realize how I can possibly grow my projects if the chance shows itself.

## Prerequisites

- Python 3.11 or higher
- Ollama installed and running locally
- Required Ollama models (can be changed through `.env`)
- hf.co/bartowski/Qwen2.5-7B-Instruct-GGUF:Q5_K_M (or alternative like qwen2.5:3b)
- nomic-embed-text:latest (for embeddings)

## Setup & Installation

### Using Poetry (Recommended)

#### Install dependencies

```bash
poetry install
```

#### Run the application

```bash
poetry run python main.py
```

### Without Poetry

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Configuration

The application uses the following environment variables:

| Variable           | Description                  | Default                               |
| ------------------ | ---------------------------- | ------------------------------------- |
| FLASK_ENV          | Application environment      | development                           |
| PORT               | Port to run the application  | 8000                                  |
| UPLOAD_FOLDER_PATH | Path to store uploaded files | ./uploads                             |
| OLLAMA_API_URL     | URL for Ollama API           | [http://localhost:11434/api/generate] |

You can set these values in a `.env` file in the project root:

```.env
FLASK_ENV=development
PORT=8000
UPLOAD_FOLDER_PATH=./uploads
OLLAMA_API_URL=http://localhost:11434/api/generate
```

## Ollama Configuration

This project uses Ollama as an LLM provider. This means you need to have the model already downloaded before running the application. For the default models used (inference and embedding), you can do so with the following command in the terminal:

```bash
ollama pull hf.co/bartowski/Qwen2.5-7B-Instruct-GGUF:Q5_K_M nomic-embed-text:latest
```

## Running the Application

1. Start your Ollama server, having pulled the right model beforehand.
2. Run the application using one of the methods above
3. Open your browser to [http://localhost:8000]
4. Upload a CV/resume to start chatting

Note that the responses in the chat app can take time to load depending on where the server is being run. There is no loading indicator, but once a message is sent, it *will* respond.
