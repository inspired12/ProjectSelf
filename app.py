from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import whisper
import os
import tempfile
from database import KnowledgeDB
import json

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize database
db = KnowledgeDB()

# Load Whisper model (using base model for balance of speed/accuracy)
# Options: tiny, base, small, medium, large
print("Loading Whisper model...")
whisper_model = whisper.load_model("base")
print("Whisper model loaded!")

# Create uploads directory
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory('static', 'index.html')


@app.route('/api/current-question', methods=['GET'])
def get_current_question():
    """Get the current question to answer"""
    question = db.get_current_question()

    if question:
        return jsonify({
            'success': True,
            'question': question
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No more questions available'
        })


@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio using Whisper"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        question_id = request.form.get('question_id')

        if not question_id:
            return jsonify({'success': False, 'error': 'No question_id provided'}), 400

        # Save the audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_path = temp_audio.name

        try:
            # Transcribe using Whisper
            print(f"Transcribing audio for question {question_id}...")
            result = whisper_model.transcribe(temp_path)
            transcription = result['text'].strip()

            # Save to permanent location
            audio_filename = f"response_{question_id}_{len(os.listdir(UPLOAD_DIR))}.wav"
            audio_path = os.path.join(UPLOAD_DIR, audio_filename)
            os.rename(temp_path, audio_path)

            # Save to database
            response_id = db.save_response(
                question_id=int(question_id),
                transcription=transcription,
                audio_path=audio_path
            )

            return jsonify({
                'success': True,
                'transcription': transcription,
                'response_id': response_id
            })

        finally:
            # Clean up temp file if it still exists
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/next-question', methods=['POST'])
def next_question():
    """Move to the next question"""
    db.advance_to_next_question()
    return jsonify({'success': True})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    stats = db.get_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })


@app.route('/api/responses', methods=['GET'])
def get_responses():
    """Get all responses"""
    question_id = request.args.get('question_id')

    if question_id:
        responses = db.get_all_responses(int(question_id))
    else:
        responses = db.get_all_responses()

    return jsonify({
        'success': True,
        'responses': responses
    })


@app.route('/api/import-questions', methods=['POST'])
def import_questions():
    """Import questions from JSON"""
    try:
        data = request.get_json()
        questions = data.get('questions', [])

        if not questions:
            return jsonify({'success': False, 'error': 'No questions provided'}), 400

        db.import_questions(questions)

        return jsonify({
            'success': True,
            'message': f'Imported {len(questions)} questions'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reset-progress', methods=['POST'])
def reset_progress():
    """Reset progress to start from the beginning"""
    db.reset_progress()
    return jsonify({'success': True, 'message': 'Progress reset'})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("ProjectSelf - Knowledge Capture System")
    print("="*60)
    print("\nServer starting on http://localhost:5000")
    print("\nReady to capture your knowledge and wisdom!")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
