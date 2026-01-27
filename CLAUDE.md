# ProjectSelf - Claude Code Guidelines

This project builds a voice knowledge capture system to create a personal reasoning partner. These guidelines ensure high-quality, maintainable code aligned with our mission.

## Core Principles

### 1. Think Before Coding

**Surface assumptions and confusion rather than proceeding blindly.**

When implementing features:
- Explicitly state uncertainties about requirements
- Present multiple interpretations when they exist
- Suggest simpler alternatives before complex solutions
- Stop to clarify confusing requirements rather than guessing

Example: If asked to "improve transcription accuracy," don't assume which approach. Instead ask: "Do you want to use a larger Whisper model, add post-processing, or implement confidence scoring?"

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

Reject:
- Speculative features ("users might want X")
- Unnecessary abstractions (don't create a factory for one class)
- Unrequested flexibility (don't add config for things that won't change)
- Error handling for impossible scenarios (don't catch errors that can't happen)

Ask yourself: Would a senior engineer call this overcomplicated? If yes, simplify.

### 3. Surgical Changes

**When modifying existing code, targeted intervention only.**

DO:
- Change only what's needed for the stated goal
- Match existing code style and patterns
- Remove imports/variables made unused by YOUR changes

DON'T:
- "Improve" adjacent code not related to the task
- Reformat unrelated sections
- Add type hints to unchanged functions
- Remove pre-existing dead code (unless that's the task)

### 4. Goal-Driven Execution

**Transform vague tasks into verifiable objectives.**

Instead of: "Add validation"
Do this:
1. Write tests for invalid inputs
2. Make tests pass
3. Verify all tests pass

Instead of: "Improve performance"
Do this:
1. Profile to identify bottleneck
2. Measure baseline performance
3. Implement fix
4. Verify improvement with metrics

Use explicit checkpoints and success criteria.

## ProjectSelf-Specific Guidelines

### Voice & Transcription
- **Whisper model choice**: Default to `base` for speed/accuracy balance
- **Audio format**: Stick with WAV for compatibility
- **Error handling**: Always provide user-friendly messages for mic/browser issues

### Database
- **Keep it simple**: SQLite is perfect for this use case
- **No premature optimization**: Don't add caching/indexing until proven necessary
- **Migrations**: For schema changes, provide clear upgrade path

### Frontend
- **Vanilla JS**: No frameworks unless complexity demands it
- **Progressive enhancement**: Work without JS where possible
- **Mobile-first**: Voice capture is often mobile use case

### Question Processing
- **Transparent scoring**: Make prioritization logic visible and tweakable
- **Preserve original data**: Never lose original question ordering/metadata
- **Multiple methods**: Provide both keyword and AI options for different needs

## Mission Alignment

Every feature should serve the goal: **Capturing knowledge to build a personal reasoning partner for Generation Alpha's future.**

Ask before adding features:
1. Does this help capture knowledge better?
2. Does this make the data more useful for future AI training?
3. Does this align with biology-humanity-technology integration?

If no to all three, reconsider.

## Quality Standards

### Code Quality
- Type hints for public APIs
- Docstrings for non-obvious functions
- Comments explain "why," not "what"
- No commented-out code in commits

### Testing Approach
- Manual testing for UI/UX flows
- Automated tests for data processing/transformations
- Test with real voice recordings, not just mock data

### Performance Targets
- Transcription: < 5 seconds for 1-minute audio (base model)
- UI: < 100ms response to user actions
- Database: < 50ms for typical queries

## When to Break These Rules

These guidelines favor **caution over speed**. For trivial fixes or obvious improvements, use judgment. But when in doubt, err on the side of asking questions and keeping things simple.

---

*Inspired by Andrej Karpathy's observations on LLM coding patterns*
