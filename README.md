# AIM4Productivity: Proof of Concept of an AI Onboarding assistant

An AI assistant that helps new employees get up to speed faster by answering questions about company codebase and documentation. This prototype was developed in the context of a 24h Market-Validation hackathon at the [2025 Founder's Retreat of the Entrepreneur Club association at EPFL/UNIL](https://www.ec-epfl-unil.org/founders-retreat).

We were three participants in our group, and together we worked through the problems to come to a possible solution. While this shiny prototype does a lot, this wouldn't have been possible without their help.

![Screenshot from our presentation slides which includes one of our demo](docs/screenshot-slide-demo.png)

## How this project came to be

The task was to think of some problems one faces, and try to go further into each one and iterating until you come into a niche where a solution might appear.
Our idea came from the challenges we faced during internships where onboarding wasted more time than it should because of lack of resources to assign full-time mentors and the bureaucracy in-place. We realized that although the ideal would be to have a mentor that can be there to help us get settled into a company's codeabase, this is rarely the case since said mentor can very well be busy with other tasks, and might only be able to answer a small subset of questions.
This prototype shows how one can use RAG Retrieval Augmentated Generation (RAG) to run an LLM chatbot which bases its responses off of pre-loaded documents. This can be documentation on the current codebase, but it can also be expanded to utilize many more resources. In this first iteration, the user's CV is requested so that the chatbot can get an idea of their level of expertise in certain topics, and it can adapt its explanations accordingly. In practice, this might be replaced by pre-loading the user's job description, or a technical assessment by hiring managers so that it can be further specialized.
The overall Founder's retreat was an absolutely amazing experience, and it pushed me and my fellow participants to go forward with finding new ideas and contacting people for complementing said ideas. Being a BsC Computer Science student, I have experience as a developer but I now realize how I can possibly grow my projects if the opportunity presents itself.

## Key Features

- CV-aware responses that adapt to the user's technical knowledge level
- RAG-based approach that grounds responses in company documentation
- Local deployment for data privacy and security

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

Note: Response generation may take some time depending on your hardware. The application will respond eventually, but there's currently no loading indicator.

## Limitations and Future Work

- Current version is a proof of concept with limited features
- Future versions could incorporate more data sources beyond documentation
- UI improvements including response loading indicators are planned if I pursue this project further
- Integration with version control systems

## Final thoughts

This project demonstrates how AI can be leveraged to solve real workplace challenges like onboarding. While it's a proof of concept developed in a few hours, it showcases the potential of RAG techniques in such domains.

The possibilities to expand this are endless, and if I were to further develop this project, I would go beyond just the CV, but make the usage of RAG much more prominent and reliable.
