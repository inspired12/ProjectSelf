# ProjectSelf - Voice Knowledge Capture System

A personal knowledge repository system that uses voice transcription to capture your thoughts, insights, and wisdom. This tool helps you build a comprehensive database of your knowledge that can eventually be used to create a personal reasoning partner.

## Features

- 🎙️ **Voice Recording**: Simple browser-based audio recording
- 🤖 **AI Transcription**: Uses OpenAI Whisper for accurate voice-to-text conversion
- 📊 **Progress Tracking**: Visual progress indicators and statistics
- 💾 **Local Database**: SQLite for simple, portable storage
- 🎯 **Question-Guided**: Structured approach with customizable questions
- 📱 **Responsive UI**: Clean, modern interface that works on desktop and mobile

## System Requirements

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Microphone access
- ~2GB free disk space (for Whisper models)

## Installation

### 1. Clone or Download the Repository

```bash
cd ProjectSelf
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The first time you run the app, Whisper will download the model (~140MB for the base model), which may take a few minutes.

## Quick Start

### 1. Import Questions

You can start with the sample questions or import your own:

```bash
# Use the sample questions (30 questions)
python import_questions.py sample_questions.json

# Or import your own questions
python import_questions.py your_questions.json
```

### 2. Start the Application

```bash
python app.py
```

### 3. Open Your Browser

Navigate to: `http://localhost:5000`

### 4. Start Capturing Knowledge!

1. Grant microphone permissions when prompted
2. Read the question
3. Click "Start Recording"
4. Speak your answer
5. Click "Stop Recording"
6. Review the transcription
7. Click "Next Question" to continue

## Question Format

Questions should be in JSON format. You can use either simple strings or objects with categories:

### Simple Format
```json
[
    "What is your core philosophy on life?",
    "How do you approach problem-solving?",
    "What are your most important values?"
]
```

### Detailed Format (with categories)
```json
[
    {
        "question": "What is your core philosophy on life?",
        "category": "Philosophy"
    },
    {
        "question": "How do you approach problem-solving?",
        "category": "Problem Solving"
    }
]
```

## Creating Your 1000 Questions

To create a comprehensive knowledge base, consider organizing your questions into categories:

- **Philosophy & Values** (10-15%)
- **Personal Growth & Development** (15-20%)
- **Professional & Career** (15-20%)
- **Relationships & Communication** (10-15%)
- **Problem Solving & Decision Making** (10-15%)
- **Health & Wellness** (5-10%)
- **Creativity & Innovation** (5-10%)
- **Specific Domain Knowledge** (15-20%)

### Tips for Good Questions

- Make questions open-ended
- Focus on "how" and "why" rather than "what"
- Include scenarios and examples
- Ask about principles, not just facts
- Cover different time perspectives (past lessons, current practices, future goals)

## Database Structure

The system uses SQLite with three main tables:

- **questions**: Stores all questions with categories
- **responses**: Stores transcriptions linked to questions
- **session_metadata**: Tracks progress and statistics

## API Endpoints

The Flask backend provides these endpoints:

- `GET /api/current-question` - Get the current question
- `POST /api/transcribe` - Transcribe audio and save response
- `POST /api/next-question` - Move to next question
- `GET /api/stats` - Get overall statistics
- `GET /api/responses` - Get all responses
- `POST /api/import-questions` - Import questions
- `POST /api/reset-progress` - Reset progress to start

## Whisper Model Options

The default configuration uses the "base" model. You can change this in `app.py`:

```python
whisper_model = whisper.load_model("base")  # Change to: tiny, small, medium, or large
```

| Model  | Size  | Speed | Accuracy |
|--------|-------|-------|----------|
| tiny   | 39M   | Fast  | Good     |
| base   | 74M   | Fast  | Better   |
| small  | 244M  | Medium| Great    |
| medium | 769M  | Slow  | Excellent|
| large  | 1550M | Slower| Best     |

## Exporting Your Knowledge

To export all your responses to JSON:

```python
from database import KnowledgeDB

db = KnowledgeDB()
responses = db.get_all_responses()

import json
with open('my_knowledge.json', 'w') as f:
    json.dump(responses, f, indent=2)
```

## Future Enhancements

This system is designed as the foundation for creating a personal reasoning partner. Potential next steps:

1. **Fine-tuning a Model**: Use your responses to fine-tune an LLM
2. **RAG System**: Build a retrieval-augmented generation system
3. **Vector Database**: Create embeddings for semantic search
4. **Knowledge Graph**: Extract entities and relationships
5. **Multi-modal**: Add support for images and documents

## Troubleshooting

### Microphone Not Working
- Ensure you've granted microphone permissions in your browser
- Check browser settings (Settings → Privacy → Microphone)
- Try a different browser

### Whisper Installation Issues
- On Mac with M1/M2: Install specific PyTorch version
- On Windows: May need Microsoft C++ Build Tools

### Port 5000 Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

## Project Structure

```
ProjectSelf/
├── app.py                      # Flask backend
├── database.py                 # Database management
├── requirements.txt            # Python dependencies
├── import_questions.py         # Question import utility
├── sample_questions.json       # Example questions
├── static/
│   ├── index.html             # Main UI
│   ├── styles.css             # Styling
│   └── app.js                 # Frontend logic
├── uploads/                   # Audio files (created automatically)
└── knowledge.db              # SQLite database (created automatically)
```

## Contributing

This is a personal knowledge capture system, but feel free to fork and adapt it for your own needs!

## License

MIT License - Feel free to use and modify as needed.

## Development & Task Management

This project uses [Beads](https://github.com/steveyegge/beads) for AI-optimized issue tracking:

```bash
# Install beads
npm install -g @beads/bd

# View ready tasks
bd ready

# See full setup guide
cat BEADS_SETUP.md
```

Beads maintains persistent task context and dependencies, perfect for long-horizon AI development.

## Acknowledgments

- Built with [OpenAI Whisper](https://github.com/openai/whisper)
- Powered by Flask and vanilla JavaScript
- Task management via [Beads](https://github.com/steveyegge/beads)
- Inspired by the goal of creating personal AI reasoning partners

---

**Ready to capture your knowledge and wisdom!** 🚀
