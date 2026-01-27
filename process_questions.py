#!/usr/bin/env python3
"""
Process and categorize 1000 questions for Generation Alpha mission

This script:
1. Reads questions from Excel file
2. Categorizes them based on priority for the mission
3. Scores questions by relevance to biology/humanity/technology alignment
4. Outputs prioritized JSON for import
"""

import pandas as pd
import json
import sys
import re
from pathlib import Path


# Mission-focused keywords for prioritization
PRIORITY_KEYWORDS = {
    'high': [
        # Technology & Future
        'technology', 'future', 'innovation', 'ai', 'artificial intelligence',
        'automation', 'digital', 'virtual', 'augmented', 'biotechnology',

        # Biology & Health
        'biology', 'health', 'genetic', 'wellness', 'longevity', 'medical',
        'neuroscience', 'brain', 'body', 'human potential',

        # Humanity & Society
        'generation', 'children', 'education', 'learning', 'youth', 'future generations',
        'humanity', 'human', 'society', 'community', 'collective',

        # Alignment & Integration
        'alignment', 'integration', 'harmony', 'balance', 'synergy', 'convergence',
        'ethics', 'values', 'wisdom', 'sustainability', 'regenerative',

        # Systems Thinking
        'systems', 'holistic', 'interconnected', 'ecosystem', 'complex',
    ],
    'medium': [
        'relationship', 'communication', 'collaboration', 'creativity',
        'consciousness', 'awareness', 'mindfulness', 'purpose', 'meaning',
        'leadership', 'vision', 'transformation', 'evolution', 'growth',
        'nature', 'environment', 'planet', 'earth',
    ],
    'low': [
        'personal', 'individual', 'preference', 'opinion', 'favorite',
        'routine', 'daily', 'habit',
    ]
}


def calculate_priority_score(question_text):
    """Calculate priority score based on keyword matching"""
    text_lower = question_text.lower()
    score = 0

    # High priority keywords
    for keyword in PRIORITY_KEYWORDS['high']:
        if keyword in text_lower:
            score += 3

    # Medium priority keywords
    for keyword in PRIORITY_KEYWORDS['medium']:
        if keyword in text_lower:
            score += 2

    # Low priority keywords (negative score)
    for keyword in PRIORITY_KEYWORDS['low']:
        if keyword in text_lower:
            score -= 1

    return max(0, score)  # Don't go negative


def categorize_question(question_text):
    """Categorize question based on content"""
    text_lower = question_text.lower()

    # Technology categories
    if any(word in text_lower for word in ['ai', 'technology', 'digital', 'automation', 'virtual', 'augmented']):
        return 'Technology & Future'

    # Biology categories
    if any(word in text_lower for word in ['health', 'biology', 'body', 'brain', 'genetic', 'medical', 'wellness']):
        return 'Biology & Health'

    # Youth & Education
    if any(word in text_lower for word in ['children', 'generation', 'youth', 'education', 'learning', 'young']):
        return 'Generation Alpha & Youth'

    # Systems & Integration
    if any(word in text_lower for word in ['system', 'integration', 'alignment', 'harmony', 'balance', 'holistic']):
        return 'Systems & Alignment'

    # Ethics & Wisdom
    if any(word in text_lower for word in ['ethics', 'values', 'wisdom', 'meaning', 'purpose', 'consciousness']):
        return 'Ethics & Wisdom'

    # Environment & Sustainability
    if any(word in text_lower for word in ['environment', 'nature', 'planet', 'sustainability', 'earth', 'climate']):
        return 'Environment & Sustainability'

    # Leadership & Transformation
    if any(word in text_lower for word in ['leadership', 'transform', 'vision', 'change', 'innovation']):
        return 'Leadership & Vision'

    # Personal Growth
    if any(word in text_lower for word in ['growth', 'development', 'learning', 'mindset', 'creativity']):
        return 'Personal Growth'

    # Relationships & Community
    if any(word in text_lower for word in ['relationship', 'community', 'collaboration', 'social', 'connection']):
        return 'Relationships & Community'

    return 'General Wisdom'


def process_excel_file(file_path, output_file='questions_prioritized.json'):
    """Process Excel file and create prioritized question list"""

    try:
        # Read Excel file
        print(f"Reading {file_path}...")
        df = pd.read_excel(file_path)

        # Try to find the question column
        question_col = None
        for col in df.columns:
            if 'question' in col.lower() or 'prompt' in col.lower():
                question_col = col
                break

        if question_col is None:
            # Use first column if no question column found
            question_col = df.columns[0]
            print(f"No 'question' column found, using '{question_col}'")

        print(f"Found {len(df)} questions in column '{question_col}'")

        # Process each question
        questions = []
        for idx, row in df.iterrows():
            question_text = str(row[question_col]).strip()

            # Skip empty or invalid questions
            if not question_text or question_text == 'nan' or len(question_text) < 10:
                continue

            # Calculate priority score
            priority_score = calculate_priority_score(question_text)

            # Categorize
            category = categorize_question(question_text)

            questions.append({
                'question': question_text,
                'category': category,
                'priority_score': priority_score,
                'original_index': idx
            })

        # Sort by priority score (highest first)
        questions.sort(key=lambda x: x['priority_score'], reverse=True)

        # Add rank
        for rank, q in enumerate(questions, 1):
            q['priority_rank'] = rank

        # Statistics
        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Total questions processed: {len(questions)}")
        print(f"\nCategory Distribution:")

        categories = {}
        for q in questions:
            cat = q['category']
            categories[cat] = categories.get(cat, 0) + 1

        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")

        # Priority tiers
        high_priority = [q for q in questions if q['priority_score'] >= 6]
        medium_priority = [q for q in questions if 3 <= q['priority_score'] < 6]
        low_priority = [q for q in questions if q['priority_score'] < 3]

        print(f"\nPriority Distribution:")
        print(f"  High Priority (score >= 6): {len(high_priority)}")
        print(f"  Medium Priority (score 3-5): {len(medium_priority)}")
        print(f"  Low Priority (score < 3): {len(low_priority)}")

        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(questions, f, indent=2)

        print(f"\n✓ Saved to: {output_file}")

        # Create separate high-priority file
        high_priority_file = output_file.replace('.json', '_high_priority.json')
        with open(high_priority_file, 'w') as f:
            json.dump(high_priority, f, indent=2)

        print(f"✓ High priority questions saved to: {high_priority_file}")

        # Show top 10 high priority questions
        print(f"\n{'='*60}")
        print("TOP 10 HIGH PRIORITY QUESTIONS")
        print(f"{'='*60}")
        for i, q in enumerate(high_priority[:10], 1):
            print(f"\n{i}. [{q['category']}] (Score: {q['priority_score']})")
            print(f"   {q['question'][:100]}...")

        return questions

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python process_questions.py <excel_file> [output_file]")
        print("\nExample:")
        print("  python process_questions.py SaveWisdomQuestions.xlsx")
        print("  python process_questions.py questions.xlsx custom_output.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'questions_prioritized.json'

    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)

    process_excel_file(input_file, output_file)
