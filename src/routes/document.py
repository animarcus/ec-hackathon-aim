from flask import jsonify, request, session, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
import os
from src.utils.file_helpers import allowed_file


def register_document_routes(app, storage, doc_processor):
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

            session['session_id'] = session_id

            # Clean up
            os.remove(filepath)
            return jsonify({'success': True})

        except Exception as e:
            app.logger.error(f"Error processing CV: {str(e)}")
            return jsonify({'error': 'Error processing CV'}), 500
