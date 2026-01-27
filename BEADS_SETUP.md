# Beads Issue Tracker Setup for ProjectSelf

Beads is a git-backed, AI-agent-optimized issue tracker that maintains task context and dependencies.

## Installation

Choose one method:

```bash
# Option 1: npm (recommended)
npm install -g @beads/bd

# Option 2: Homebrew (macOS)
brew install beads

# Option 3: Install script (Linux/macOS)
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash

# Option 4: Go
go install github.com/steveyegge/beads/cmd/bd@latest
```

## Project Initialization

```bash
cd ProjectSelf
bd init
```

This creates a `.beads/` directory with JSONL issue storage.

## Initial Issue Structure

Run these commands to set up the ProjectSelf roadmap:

### Phase 1: Core System (Current)

```bash
# Epic: Core voice capture system
bd create "Core voice knowledge capture system" -p 0 --status done
CORE_EPIC=$(bd list --format json | jq -r '.[0].id')

# Completed tasks
bd create "Voice recording interface" -p 0 --status done
bd create "Whisper transcription integration" -p 0 --status done
bd create "SQLite database design" -p 0 --status done
bd create "Question import system" -p 0 --status done
bd create "Export knowledge utility" -p 0 --status done
```

### Phase 2: Question Processing (In Progress)

```bash
# Epic: Question prioritization
bd create "Question processing and prioritization system" -p 0 --status open
PRIORITY_EPIC=$(bd list --format json | jq -r '.[0].id')

bd create "Keyword-based prioritization" -p 0 --status done
bd create "AI-powered semantic analysis" -p 1 --status done
bd create "Mission alignment scoring" -p 1 --status open
bd dep add $(bd list --last) $PRIORITY_EPIC

bd create "Import 1000 SaveWisdom questions" -p 0 --status open
bd dep add $(bd list --last) $PRIORITY_EPIC

bd create "Analyze question quality and coverage" -p 2 --status open
bd dep add $(bd list --last) $PRIORITY_EPIC
```

### Phase 3: Data Quality & Enhancement

```bash
# Epic: Transcription quality
bd create "Enhance transcription accuracy and quality" -p 1 --status open
QUALITY_EPIC=$(bd list --format json | jq -r '.[0].id')

bd create "Test Whisper models (tiny/base/small/medium)" -p 1 --status open
bd dep add $(bd list --last) $QUALITY_EPIC

bd create "Implement confidence scoring" -p 2 --status open
bd dep add $(bd list --last) $QUALITY_EPIC

bd create "Add post-processing cleanup" -p 2 --status open
bd dep add $(bd list --last) $QUALITY_EPIC

bd create "Speaker diarization for multi-speaker responses" -p 3 --status open
bd dep add $(bd list --last) $QUALITY_EPIC

# Epic: Data enrichment
bd create "Knowledge enrichment and linking" -p 2 --status open
ENRICH_EPIC=$(bd list --format json | jq -r '.[0].id')

bd create "Extract entities from transcriptions" -p 2 --status open
bd dep add $(bd list --last) $ENRICH_EPIC

bd create "Link related questions/responses" -p 2 --status open
bd dep add $(bd list --last) $ENRICH_EPIC

bd create "Generate embeddings for semantic search" -p 1 --status open
bd dep add $(bd list --last) $ENRICH_EPIC

bd create "Build knowledge graph from responses" -p 2 --status open
bd dep add $(bd list --last) $ENRICH_EPIC
```

### Phase 4: AI Integration & Reasoning Partner

```bash
# Epic: Personal reasoning partner
bd create "Build personal reasoning partner from captured knowledge" -p 0 --status open
PARTNER_EPIC=$(bd list --format json | jq -r '.[0].id')

bd create "Export training data for fine-tuning" -p 1 --status open
bd dep add $(bd list --last) $PARTNER_EPIC

bd create "Build RAG system with captured knowledge" -p 1 --status open
bd dep add $(bd list --last) $PARTNER_EPIC

bd create "Fine-tune small model on user's knowledge" -p 2 --status open
bd dep add $(bd list --last) $PARTNER_EPIC

bd create "Create reasoning partner interface" -p 2 --status open
bd dep add $(bd list --last) $PARTNER_EPIC

bd create "Integrate with Generation Alpha resources" -p 2 --status open
bd dep add $(bd list --last) $PARTNER_EPIC
```

### Phase 5: Biology-Humanity-Technology Alignment

```bash
# Epic: Alignment features
bd create "Biology-Humanity-Technology alignment features" -p 1 --status open
ALIGN_EPIC=$(bd list --format json | jq -r '.[0].id')

bd create "Health & wellness tracking integration" -p 2 --status open
bd dep add $(bd list --last) $ALIGN_EPIC

bd create "Personal values alignment scoring" -p 2 --status open
bd dep add $(bd list --last) $ALIGN_EPIC

bd create "Technology usage patterns analysis" -p 2 --status open
bd dep add $(bd list --last) $ALIGN_EPIC

bd create "Generation Alpha impact assessment" -p 1 --status open
bd dep add $(bd list --last) $ALIGN_EPIC

bd create "Systems thinking visualization" -p 3 --status open
bd dep add $(bd list --last) $ALIGN_EPIC
```

### Phase 6: Polish & Distribution

```bash
# Epic: Production readiness
bd create "Production deployment and distribution" -p 3 --status open
PROD_EPIC=$(bd list --format json | jq -r '.[0].id')

bd create "Add comprehensive error handling" -p 2 --status open
bd dep add $(bd list --last) $PROD_EPIC

bd create "Implement data backup/restore" -p 1 --status open
bd dep add $(bd list --last) $PROD_EPIC

bd create "Create Docker container" -p 2 --status open
bd dep add $(bd list --last) $PROD_EPIC

bd create "Write deployment documentation" -p 2 --status open
bd dep add $(bd list --last) $PROD_EPIC

bd create "Build desktop app (Electron)" -p 3 --status open
bd dep add $(bd list --last) $PROD_EPIC

bd create "Mobile app (React Native)" -p 3 --status open
bd dep add $(bd list --last) $PROD_EPIC
```

## Daily Workflow

### View ready tasks
```bash
bd ready
```

Shows all tasks with no blocking dependencies that are ready to work on.

### Check specific task
```bash
bd show bd-a1b2
```

### Update task status
```bash
bd status bd-a1b2 in-progress
bd status bd-a1b2 done
```

### Add notes to task
```bash
bd comment bd-a1b2 "Implemented using sentence-transformers model"
```

### Create new task
```bash
bd create "New feature description" -p 1
```

### View all tasks
```bash
bd list --format json | jq
```

## Integration with Claude Code

Beads maintains persistent context across sessions. Before each coding session:

```bash
# Check what's ready to work on
bd ready

# Show details for selected task
bd show <task-id>

# Update status when starting
bd status <task-id> in-progress

# Add notes as you work
bd comment <task-id> "Implementation notes..."

# Mark complete when done
bd status <task-id> done
```

## Benefits for ProjectSelf

1. **Persistent Memory**: Beads stores all task history in git
2. **Dependency Tracking**: Know what's blocking progress
3. **AI-Optimized**: JSON output perfect for Claude Code
4. **Mission Alignment**: Track how each task serves Generation Alpha goals
5. **Long-Horizon Planning**: Maintain context across months of development

## File Structure

```
ProjectSelf/
├── .beads/
│   ├── issues.jsonl        # All issues stored here
│   └── cache.db           # SQLite cache (optional)
└── BEADS_SETUP.md         # This file
```

The `.beads/` directory should be committed to git for full version control.

## Next Steps

1. Install beads using one of the methods above
2. Run `bd init` in the ProjectSelf directory
3. Execute the issue creation commands from this document
4. Run `bd ready` to see what's ready to work on
5. Start building the reasoning partner!

---

**Resources:**
- GitHub: https://github.com/steveyegge/beads
- Documentation: Check the repository README for full command reference
