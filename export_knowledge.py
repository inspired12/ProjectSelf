#!/usr/bin/env python3
"""
Helper script to export all captured knowledge to JSON format
"""

import json
import sys
from datetime import datetime
from database import KnowledgeDB

def export_responses(output_file=None):
    """Export all responses to JSON"""
    try:
        db = KnowledgeDB()
        responses = db.get_all_responses()
        stats = db.get_stats()

        # Create export data structure
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'statistics': stats,
            'responses': responses
        }

        # Determine output filename
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'knowledge_export_{timestamp}.json'

        # Write to file
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"✓ Successfully exported {len(responses)} responses!")
        print(f"✓ File saved to: {output_file}")
        print(f"\nStatistics:")
        print(f"  Total Questions: {stats['total_questions']}")
        print(f"  Total Responses: {stats['total_responses']}")
        print(f"  Completion: {stats['completion_percentage']:.1f}%")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    export_responses(output_file)
