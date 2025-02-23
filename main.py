import os
from pathlib import Path

from flask import Flask

from src.routes.chat import register_chat_routes
from src.routes.document import register_document_routes
from src.services.document_processor import DocumentProcessor
from src.storage.storage import Storage
from src.utils.file_helpers import process_initial_documents


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Base directory for all storage
    base_dir = Path(__file__).resolve().parent

    # Configuration
    app.config.update(
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        UPLOAD_FOLDER=str(base_dir / 'uploads'),
        OLLAMA_API_URL=os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
    )

    # Ensure directories exist
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    # Initialize services
    storage = Storage()
    doc_processor = DocumentProcessor()

    # Process initial documents
    initial_session, initial_context = process_initial_documents(storage, doc_processor, base_dir)
    app.config['INITIAL_SESSION'] = initial_session
    app.config['INITIAL_CONTEXT'] = initial_context

    # Register routes
    register_chat_routes(app, storage)
    register_document_routes(app, storage, doc_processor)

    return app


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=int(os.getenv('PORT', 8000)))
    args = parser.parse_args()

    app = create_app()
    app.run(
        host="0.0.0.0",
        port=args.port,
        debug=os.getenv('FLASK_ENV') == 'development'
    )


if __name__ == "__main__":
    main()
