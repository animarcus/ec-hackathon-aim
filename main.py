import os
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import time

from config import DEFAULT_EMBEDDER, DEFAULT_MODEL
from pdf_processor import DocumentProcessor
from llm_client import CVAnalyzer
from storage import Storage

# Load environment variables
load_dotenv()

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# File type validation
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_initial_documents(storage: Storage, doc_processor: DocumentProcessor, base_dir: Path):
    """Process all documents in the uploads folder at startup."""
    uploads_dir = base_dir / 'uploads'
    uploads_dir.mkdir(exist_ok=True)

    logger.info(f"=== Starting initial document processing from {uploads_dir} ===")
    start_time = time.time()

    # Create a special session for initial documents
    initial_session = storage.create_session()
    all_chunks = []
    all_embeddings = []

    # Process all supported files
    for ext in ALLOWED_EXTENSIONS:
        for file in uploads_dir.glob(f'*.{ext}'):
            logger.info(f"Processing initial document: {file}")
            try:
                if file.suffix == '.pdf':
                    result = doc_processor.process_pdf(str(file))
                else:
                    result = doc_processor.process_text(str(file))

                logger.info(f"Got {len(result['chunks'])} chunks and {len(result['embeddings'])} embeddings")
                all_chunks.extend(result['chunks'])
                all_embeddings.extend(result['embeddings'])
            except Exception as e:
                logger.error(f"Error processing initial document {file}: {e}")

    # Store combined results
    data = {
        'chunks': all_chunks,
        'embeddings': all_embeddings,
        'source': 'initial_documents'
    }
    storage.store_data(initial_session, data)

    processing_time = time.time() - start_time
    logger.info(f"Initial processing complete. Processed {len(all_chunks)} chunks in {processing_time:.2f} seconds")
    return initial_session, data

def create_app():
    app = Flask(__name__)
    logger.info("=== Initializing application ===")

    # Base directory for all storage
    base_dir = Path(__file__).resolve().parent

    # Configuration
    app.config.update(
        SECRET_KEY=os.getenv('SESSION_SECRET', 'dev_secret_key'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
        UPLOAD_FOLDER=str(base_dir / 'uploads'),  # Convert Path to string
        STORAGE_PATH=str(base_dir / 'storage'),
        OLLAMA_API_URL=os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
    )

    # Ensure directories exist
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(app.config['STORAGE_PATH']).mkdir(parents=True, exist_ok=True)

    # Initialize services
    logger.info("Initializing services...")
    storage = Storage(app.config['STORAGE_PATH'])
    doc_processor = DocumentProcessor()
    llm_client = CVAnalyzer()

    # Process initial documents
    initial_session, initial_context = process_initial_documents(storage, doc_processor, base_dir)
    app.config['INITIAL_SESSION'] = initial_session
    app.config['INITIAL_CONTEXT'] = initial_context
    logger.info(f"Initial document session created: {initial_session}")

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload_cv', methods=['POST'])
    def upload_cv():
        if 'cv' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['cv']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400

        try:
            filename = secure_filename(file.filename)
            filepath = str(Path(app.config['UPLOAD_FOLDER']) / filename)

            logger.info(f"Processing uploaded CV: {filepath}")
            start_time = time.time()
            file.save(filepath)

            # Process document
            result = doc_processor.process_pdf(filepath)
            processing_time = time.time() - start_time
            logger.info(f"CV processed in {processing_time:.2f} seconds")

            # Create session and store data
            session_id = storage.create_session()
            storage.store_data(session_id, {
                'chunks': result['chunks'],
                'embeddings': result['embeddings'],
                'full_text': result['full_text']
            })

            # Store only session_id in cookie
            session['session_id'] = session_id
            logger.info(f"CV data stored in session: {session_id}")

            # Clean up
            os.remove(filepath)
            return jsonify({'success': True})

        except Exception as e:
            logger.error(f"Error processing CV: {str(e)}")
            return jsonify({'error': 'Error processing CV'}), 500

    @app.route('/send_message', methods=['POST'])
    def send_message():
        try:
            data = request.json
            user_message = data.get('message', '')

            if not user_message:
                return jsonify({'error': 'Empty message'}), 400

            session_id = session.get('session_id')
            if not session_id:
                return jsonify({'error': 'No session found'}), 400

            cv_data = storage.get_data(session_id)
            if not cv_data:
                return jsonify({'error': 'No CV data found'}), 400

            # Get initial context from app config
            initial_context = app.config.get('INITIAL_CONTEXT', {
                'chunks': [],
                'embeddings': []
            })

            logger.info(f"Processing message: {user_message[:50]}...")
            logger.info(f"Using {len(initial_context['chunks'])} initial context chunks")
            start_time = time.time()

            # Get response from LLM
            response = llm_client.get_llm_response(
                user_message,
                cv_data['chunks'],
                cv_data['embeddings'],
                initial_context=initial_context
            )

            inference_time = time.time() - start_time
            logger.info(f"LLM response generated in {inference_time:.2f} seconds")

            return jsonify({'response': response})

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return jsonify({'error': 'Error processing message'}), 500

    @app.route('/chat')
    def chat():
        session_id = session.get('session_id')
        if not session_id or not storage.get_data(session_id):
            return render_template('index.html', error="Please upload a CV first")
        return render_template('chat.html')

    return app

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=int(os.getenv('PORT', 8000)))
    args = parser.parse_args()

    logger.info("=== Starting Application ===")
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=args.port,
        debug=os.getenv('FLASK_ENV') == 'development'
    )

if __name__ == "__main__":
    main()
