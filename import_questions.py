#!/usr/bin/env python3
"""
Helper script to import questions from a JSON file into the database
"""

import json
import sys
from database import KnowledgeDB

def import_from_file(file_path):
    """Import questions from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            questions = json.load(f)

        db = KnowledgeDB()
        db.import_questions(questions)

        print(f"✓ Successfully imported {len(questions)} questions!")
        print(f"\nYou can now run the app with: python app.py")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_questions.py <json_file>")
        print("\nExample: python import_questions.py sample_questions.json")
        print("         python import_questions.py my_1000_questions.json")
        sys.exit(1)

    file_path = sys.argv[1]
    import_from_file(file_path)
