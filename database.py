import sqlite3
from datetime import datetime
import json

class KnowledgeDB:
    def __init__(self, db_path='knowledge.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                category TEXT,
                order_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                audio_path TEXT,
                transcription TEXT,
                duration_seconds REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        ''')

        # Metadata table for tracking progress
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                current_question_index INTEGER DEFAULT 0,
                total_responses INTEGER DEFAULT 0,
                last_session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Initialize metadata if not exists
        cursor.execute('SELECT COUNT(*) as count FROM session_metadata')
        if cursor.fetchone()['count'] == 0:
            cursor.execute('INSERT INTO session_metadata (current_question_index) VALUES (0)')

        conn.commit()
        conn.close()

    def import_questions(self, questions_list):
        """Import a list of questions into the database

        Args:
            questions_list: List of dicts with 'question', optional 'category'
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        for idx, q in enumerate(questions_list):
            question_text = q if isinstance(q, str) else q.get('question', q.get('text', ''))
            category = q.get('category', 'General') if isinstance(q, dict) else 'General'

            cursor.execute('''
                INSERT INTO questions (question_text, category, order_index)
                VALUES (?, ?, ?)
            ''', (question_text, category, idx))

        conn.commit()
        conn.close()

    def get_question_by_index(self, index):
        """Get a question by its order index"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, question_text, category, order_index
            FROM questions
            WHERE order_index = ?
        ''', (index,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_current_question(self):
        """Get the current question based on session progress"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT current_question_index FROM session_metadata WHERE id = 1')
        index = cursor.fetchone()['current_question_index']

        question = self.get_question_by_index(index)

        # Also get total count
        cursor.execute('SELECT COUNT(*) as total FROM questions')
        total = cursor.fetchone()['total']

        conn.close()

        if question:
            question['current_index'] = index
            question['total_questions'] = total

        return question

    def save_response(self, question_id, transcription, audio_path=None, duration=None):
        """Save a transcribed response"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO responses (question_id, transcription, audio_path, duration_seconds)
            VALUES (?, ?, ?, ?)
        ''', (question_id, transcription, audio_path, duration))

        response_id = cursor.lastrowid

        # Update metadata
        cursor.execute('''
            UPDATE session_metadata
            SET total_responses = total_responses + 1,
                last_session_date = CURRENT_TIMESTAMP
            WHERE id = 1
        ''')

        conn.commit()
        conn.close()

        return response_id

    def advance_to_next_question(self):
        """Move to the next question"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE session_metadata
            SET current_question_index = current_question_index + 1
            WHERE id = 1
        ''')

        conn.commit()
        conn.close()

    def get_all_responses(self, question_id=None):
        """Get all responses, optionally filtered by question"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if question_id:
            cursor.execute('''
                SELECT r.*, q.question_text, q.category
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.question_id = ?
                ORDER BY r.created_at DESC
            ''', (question_id,))
        else:
            cursor.execute('''
                SELECT r.*, q.question_text, q.category
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                ORDER BY r.created_at DESC
            ''')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_stats(self):
        """Get overall statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM questions')
        total_questions = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) as total FROM responses')
        total_responses = cursor.fetchone()['total']

        cursor.execute('SELECT current_question_index FROM session_metadata WHERE id = 1')
        current_index = cursor.fetchone()['current_question_index']

        conn.close()

        return {
            'total_questions': total_questions,
            'total_responses': total_responses,
            'current_question_index': current_index,
            'completion_percentage': (total_responses / total_questions * 100) if total_questions > 0 else 0
        }

    def reset_progress(self):
        """Reset the current question index to start over"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('UPDATE session_metadata SET current_question_index = 0 WHERE id = 1')

        conn.commit()
        conn.close()
