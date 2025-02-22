import os
import logging
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from pdf_processor import extract_text_from_pdf
from llm_client import get_llm_response

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp'

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    logger.debug("Upload CV endpoint called")
    if 'cv' not in request.files:
        logger.warning("No file provided in request")
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['cv']
    if file.filename == '':
        logger.warning("Empty filename provided")
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        logger.warning(f"Invalid file type: {file.filename}")
        return jsonify({'error': 'Invalid file type. Please upload a PDF'}), 400

    try:
        logger.debug(f"Processing file: {file.filename}")
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.debug(f"Saving file to: {filepath}")
        file.save(filepath)

        logger.debug("Extracting text from PDF")
        cv_text = extract_text_from_pdf(filepath)
        logger.debug(f"Extracted text length: {len(cv_text)}")

        session['cv_context'] = cv_text
        logger.debug("CV text stored in session")

        os.remove(filepath)  # Clean up the uploaded file
        logger.debug("Temporary file removed")

        return jsonify({'success': True, 'message': 'CV processed successfully'})

    except Exception as e:
        logger.error(f"Error processing CV: {str(e)}")
        logger.exception("Full traceback:")
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.debug("Cleaned up temporary file after error")
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

        response = get_llm_response(user_message, cv_context)
        return jsonify({'response': response})

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': 'Error processing message'}), 500