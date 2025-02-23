import os
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from pdf_processor import DocumentProcessor
from llm_client import get_llm_response
from storage import Storage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File type validation
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app():
    app = Flask(__name__)

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
    storage = Storage(app.config['STORAGE_PATH'])
    doc_processor = DocumentProcessor()

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

            logger.info(f"Saving file to: {filepath}")
            file.save(filepath)

            # Process document
            result = doc_processor.process_pdf(filepath)

            # Create session and store data
            session_id = storage.create_session()
            storage.store_data(session_id, {
                'chunks': result['chunks'],
                'embeddings': result['embeddings'],
                'full_text': result['full_text']
            })

            # Store only session_id in cookie
            session['session_id'] = session_id

            # Clean up
            os.remove(filepath)
            return jsonify({'success': True})

        except Exception as e:
            logger.error(f"Error processing CV: {str(e)}")
            return jsonify({'error': 'Error processing CV'}), 500

    @app.route('/chat')
    def chat():
        if 'cv_context' not in session:
            return render_template('index.html', error="Please upload a CV first")
        return render_template('chat.html')

    @app.route('/send_message', methods=['POST'])
    def send_message():
        try:
            data = request.json
            user_message = data.get('message', '')
            cv_context = session.get('cv_context', '')

            if not user_message:
                return jsonify({'error': 'Empty message'}), 400

            # For now, just send a simple response acknowledging the message
            response = f"Received your message. CV context has {len(cv_context)} characters."
            return jsonify({'response': response})

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return jsonify({'error': 'Error processing message'}), 500


def doc_processor():
    return None
