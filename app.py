from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import tempfile
import re
from uuid import uuid4
import requests
from database import KnowledgeDB

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize database
db = KnowledgeDB()


def _parse_question_file(file_path):
    """Parse JSON question files or numbered plain-text question lists."""
    if not os.path.exists(file_path):
        return []

    # Try JSON first.
    try:
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            out = []
            for item in data:
                if isinstance(item, str):
                    text = item.strip()
                    if text:
                        out.append({"question": text, "category": "General"})
                elif isinstance(item, dict):
                    text = str(item.get("question", item.get("text", ""))).strip()
                    if text:
                        out.append({
                            "question": text,
                            "category": str(item.get("category", "General")).strip() or "General",
                        })
            return out
    except Exception:
        pass

    # Fallback: parse numbered text lines and category headings.
    questions = []
    category = "General"
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            cat_match = re.match(r"^Category\s+\d+\s*:\s*(.+?)\s*\(Questions", line, flags=re.I)
            if cat_match:
                category = cat_match.group(1).strip()
                continue
            q_match = re.match(r"^\d{1,4}\.\s*(.+)$", line)
            if q_match:
                text = q_match.group(1).strip()
                if text:
                    questions.append({"question": text, "category": category})

    # De-duplicate exact question text while preserving order.
    deduped = []
    seen = set()
    for q in questions:
        key = q["question"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(q)
    return deduped


def ensure_questions_seeded():
    """Ensure DB has questions; seed from local files if empty."""
    stats = db.get_stats()
    if stats["total_questions"] > 0:
        return

    for candidate in ("1000questions.json", "sample_questions.json"):
        parsed = _parse_question_file(candidate)
        if parsed:
            imported = db.import_questions(parsed)
            print(f"Seeded questions from {candidate}: imported {imported}")
            return

    print("No seed question file found; database remains empty.")

# OpenAI-compatible speech service configuration
STT_BASE_URL = os.getenv("SPEECH_STT_BASE_URL", "http://localhost:5002/v1").rstrip("/")
STT_API_KEY = os.getenv("SPEECH_STT_API_KEY", "none")
STT_MODEL = os.getenv("SPEECH_STT_MODEL", "whisper-1")

TTS_BASE_URL = os.getenv("SPEECH_TTS_BASE_URL", "http://localhost:5001/v1").rstrip("/")
TTS_API_KEY = os.getenv("SPEECH_TTS_API_KEY", "none")
TTS_MODEL = os.getenv("SPEECH_TTS_MODEL", "piper")
TTS_VOICE = os.getenv("SPEECH_TTS_VOICE", "en_US-lessac-medium")
TTS_RESPONSE_FORMAT = os.getenv("SPEECH_TTS_RESPONSE_FORMAT", "mp3")


def _auth_headers(api_key):
    return {"Authorization": f"Bearer {api_key}"} if api_key and api_key != "none" else {}

# Create uploads directory
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory('static', 'index.html')


@app.after_request
def add_no_cache_headers(response):
    """Disable client/proxy caching to avoid stale frontend assets."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


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
    """Transcribe audio through external OpenAI-compatible STT service."""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        question_id = request.form.get('question_id')

        if not question_id:
            return jsonify({'success': False, 'error': 'No question_id provided'}), 400
        if not question_id.isdigit():
            return jsonify({'success': False, 'error': 'Invalid question_id'}), 400

        question_id_int = int(question_id)
        if not db.question_exists(question_id_int):
            return jsonify({'success': False, 'error': 'Question not found'}), 404

        # Save the audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_path = temp_audio.name

        try:
            print(f"Transcribing audio for question {question_id} via {STT_BASE_URL}...")
            with open(temp_path, "rb") as audio_handle:
                stt_resp = requests.post(
                    f"{STT_BASE_URL}/audio/transcriptions",
                    headers=_auth_headers(STT_API_KEY),
                    files={"file": ("recording.wav", audio_handle, "audio/wav")},
                    data={"model": STT_MODEL},
                    timeout=120,
                )
            stt_resp.raise_for_status()
            payload = stt_resp.json()
            transcription = str(payload.get("text", "")).strip()
            if not transcription:
                raise RuntimeError("STT response did not include transcription text")

            # Save to permanent location
            audio_filename = f"response_{question_id_int}_{uuid4().hex}.wav"
            audio_path = os.path.join(UPLOAD_DIR, audio_filename)
            os.replace(temp_path, audio_path)

            # Save to database
            response_id = db.save_response(
                question_id=question_id_int,
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


@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Synthesize text through external OpenAI-compatible TTS service."""
    try:
        data = request.get_json(silent=True) or {}
        text = str(data.get("text", "")).strip()
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400

        voice = str(data.get("voice") or TTS_VOICE)
        tts_resp = requests.post(
            f"{TTS_BASE_URL}/audio/speech",
            headers={
                **_auth_headers(TTS_API_KEY),
                "Content-Type": "application/json",
            },
            json={
                "model": TTS_MODEL,
                "input": text,
                "voice": voice,
                "response_format": TTS_RESPONSE_FORMAT,
            },
            timeout=120,
        )
        tts_resp.raise_for_status()
        return Response(
            tts_resp.content,
            status=200,
            mimetype=tts_resp.headers.get("Content-Type", "audio/mpeg"),
        )
    except Exception as e:
        print(f"Error during text-to-speech: {str(e)}")
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
        data = request.get_json(silent=True) or {}
        questions = data.get('questions', [])

        if not isinstance(questions, list):
            return jsonify({'success': False, 'error': 'questions must be a JSON array'}), 400
        if not questions:
            return jsonify({'success': False, 'error': 'No questions provided'}), 400

        imported_count = db.import_questions(questions)
        if imported_count == 0:
            return jsonify({'success': False, 'error': 'No valid questions found'}), 400

        return jsonify({
            'success': True,
            'message': f'Imported {imported_count} questions'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reset-progress', methods=['POST'])
def reset_progress():
    """Reset progress to start from the beginning"""
    db.reset_progress()
    return jsonify({'success': True, 'message': 'Progress reset'})


if __name__ == '__main__':
    ensure_questions_seeded()
    print("\n" + "="*60)
    print("ProjectSelf - Knowledge Capture System")
    print("="*60)
    print("\nServer starting on http://localhost:5000")
    print(f"STT backend: {STT_BASE_URL} (model={STT_MODEL})")
    print(f"TTS backend: {TTS_BASE_URL} (model={TTS_MODEL}, voice={TTS_VOICE})")
    print("\nReady to capture your knowledge and wisdom!")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
