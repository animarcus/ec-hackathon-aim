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
    if 'cv' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['cv']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a PDF'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract text and store in session
        cv_text = extract_text_from_pdf(filepath)
        session['cv_context'] = cv_text

        os.remove(filepath)  # Clean up the uploaded file
        return jsonify({'success': True, 'message': 'CV processed successfully'})

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