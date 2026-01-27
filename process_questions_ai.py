#!/usr/bin/env python3
"""
AI-powered question processing for Generation Alpha mission

Uses semantic analysis to better understand question relevance
to biology-humanity-technology alignment
"""

import pandas as pd
import json
import sys
from pathlib import Path

# Optional: Use sentence transformers for semantic similarity
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_AI = True
except ImportError:
    HAS_AI = False
    print("Note: Install sentence-transformers for AI-powered categorization")
    print("pip install sentence-transformers")


# Mission statement for semantic matching
MISSION_THEMES = {
    'technology_alignment': """
        Advanced technologies, AI, automation, digital transformation,
        biotechnology, augmented reality, virtual reality, human-computer interaction,
        technological evolution, innovation for humanity
    """,
    'biology_alignment': """
        Human biology, genetics, neuroscience, health optimization,
        longevity, wellness, biological systems, brain function,
        human potential, biohacking, regenerative medicine
    """,
    'humanity_alignment': """
        Human values, ethics, consciousness, collective wisdom,
        social connection, empathy, compassion, human flourishing,
        meaning, purpose, spiritual growth, humanity's future
    """,
    'generation_alpha': """
        Future generations, children, youth, education for tomorrow,
        preparing young minds, generation alpha, next generation,
        childhood development, learning systems, youth empowerment
    """,
    'systems_thinking': """
        Systems thinking, holistic integration, interconnection,
        complexity, emergence, synergy, harmony between systems,
        whole systems design, ecological thinking, integration
    """
}


def process_with_ai(file_path, output_file='questions_ai_prioritized.json'):
    """Process questions using AI semantic analysis"""

    if not HAS_AI:
        print("Error: sentence-transformers not installed")
        print("Install with: pip install sentence-transformers")
        sys.exit(1)

    print("Loading AI model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Encode mission themes
    print("Encoding mission themes...")
    theme_embeddings = {}
    for theme, description in MISSION_THEMES.items():
        theme_embeddings[theme] = model.encode(description)

    # Read questions
    print(f"Reading {file_path}...")
    df = pd.read_excel(file_path)

    # Find question column
    question_col = None
    for col in df.columns:
        if 'question' in col.lower() or 'prompt' in col.lower():
            question_col = col
            break

    if question_col is None:
        question_col = df.columns[0]

    print(f"Found {len(df)} questions")
    print("Analyzing questions with AI...")

    questions = []
    for idx, row in df.iterrows():
        question_text = str(row[question_col]).strip()

        if not question_text or question_text == 'nan' or len(question_text) < 10:
            continue

        # Encode question
        question_embedding = model.encode(question_text)

        # Calculate similarity to each theme
        similarities = {}
        for theme, theme_emb in theme_embeddings.items():
            similarity = np.dot(question_embedding, theme_emb) / (
                np.linalg.norm(question_embedding) * np.linalg.norm(theme_emb)
            )
            similarities[theme] = float(similarity)

        # Calculate overall mission alignment score
        alignment_score = (
            similarities['technology_alignment'] * 1.5 +
            similarities['biology_alignment'] * 1.5 +
            similarities['humanity_alignment'] * 1.0 +
            similarities['generation_alpha'] * 2.0 +  # Highest weight
            similarities['systems_thinking'] * 1.2
        )

        # Determine primary category
        primary_theme = max(similarities.items(), key=lambda x: x[1])[0]

        category_map = {
            'technology_alignment': 'Technology & Future',
            'biology_alignment': 'Biology & Health',
            'humanity_alignment': 'Ethics & Humanity',
            'generation_alpha': 'Generation Alpha',
            'systems_thinking': 'Systems & Integration'
        }

        questions.append({
            'question': question_text,
            'category': category_map[primary_theme],
            'alignment_score': round(alignment_score, 3),
            'theme_scores': {k: round(v, 3) for k, v in similarities.items()},
            'original_index': idx
        })

        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1} questions...")

    # Sort by alignment score
    questions.sort(key=lambda x: x['alignment_score'], reverse=True)

    # Add rank
    for rank, q in enumerate(questions, 1):
        q['priority_rank'] = rank

    # Statistics
    print(f"\n{'='*60}")
    print("AI PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total questions: {len(questions)}")

    # Category distribution
    categories = {}
    for q in questions:
        cat = q['category']
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\nCategory Distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")

    # Alignment tiers
    high = [q for q in questions if q['alignment_score'] >= 4.0]
    medium = [q for q in questions if 3.0 <= q['alignment_score'] < 4.0]
    low = [q for q in questions if q['alignment_score'] < 3.0]

    print(f"\nAlignment Distribution:")
    print(f"  High Alignment (>= 4.0): {len(high)}")
    print(f"  Medium Alignment (3.0-3.9): {len(medium)}")
    print(f"  Lower Alignment (< 3.0): {len(low)}")

    # Save
    with open(output_file, 'w') as f:
        json.dump(questions, f, indent=2)

    print(f"\n✓ Saved to: {output_file}")

    # High priority file
    high_priority_file = output_file.replace('.json', '_high_priority.json')
    with open(high_priority_file, 'w') as f:
        json.dump(high, f, indent=2)

    print(f"✓ High priority saved to: {high_priority_file}")

    # Show top 10
    print(f"\n{'='*60}")
    print("TOP 10 HIGHEST ALIGNMENT QUESTIONS")
    print(f"{'='*60}")
    for i, q in enumerate(questions[:10], 1):
        print(f"\n{i}. [{q['category']}] (Score: {q['alignment_score']:.2f})")
        print(f"   {q['question'][:100]}...")

    return questions


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python process_questions_ai.py <excel_file> [output_file]")
        print("\nRequires: pip install sentence-transformers")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'questions_ai_prioritized.json'

    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)

    process_with_ai(input_file, output_file)
