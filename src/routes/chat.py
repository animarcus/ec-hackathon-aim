from flask import jsonify, request, session, render_template
from src.services.llm_client import CVAnalyzer


def register_chat_routes(app, storage):
    @app.route('/chat')
    def chat():
        session_id = session.get('session_id')
        if not session_id or not storage.get_data(session_id):
            return render_template('index.html', error="Please upload a CV first")
        return render_template('chat.html')

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

            llm_client = CVAnalyzer()
            response = llm_client.get_llm_response(
                user_message,
                cv_data['chunks'],
                cv_data['embeddings'],
                initial_context=initial_context
            )

            return jsonify({'response': response})

        except Exception as e:
            app.logger.error(f"Error in chat: {str(e)}")
            return jsonify({'error': 'Error processing message'}), 500
