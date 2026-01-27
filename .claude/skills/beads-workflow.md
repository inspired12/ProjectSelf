# Beads Workflow Skill

Manage ProjectSelf development tasks using the Beads issue tracker.

## Goal

Use beads to maintain persistent task context and dependencies across development sessions.

## Approach

1. **Before starting work**
   ```bash
   # View ready tasks
   bd ready

   # Show task details
   bd show <task-id>
   ```

2. **When starting a task**
   ```bash
   # Mark as in progress
   bd status <task-id> in-progress

   # Review dependencies
   bd show <task-id> | jq '.deps'
   ```

3. **During development**
   ```bash
   # Add progress notes
   bd comment <task-id> "Implemented X feature"

   # Create sub-tasks if needed
   bd create "Sub-task title" -p 1
   bd dep add <sub-task-id> <parent-task-id>
   ```

4. **After completing work**
   ```bash
   # Mark as done
   bd status <task-id> done

   # Check what becomes unblocked
   bd ready
   ```

5. **Mission alignment check**
   - Before marking done, evaluate:
     - Biology alignment: Does it capture biological/health insights?
     - Humanity alignment: Does it preserve human wisdom?
     - Technology alignment: Is it maintainable and enables AI?
     - Generation Alpha: Does it serve future generations?

   ```bash
   # Add alignment scores in comments
   bd comment <task-id> "Alignment: Bio=8, Human=9, Tech=7, GenAlpha=9"
   ```

## Issue Lifecycle

**Creating Issues:**
- Clear, actionable titles
- Appropriate priority (0=critical, 3=nice-to-have)
- Set dependencies for complex tasks
- Add mission alignment context

**Working on Issues:**
- Start: `bd status <id> in-progress`
- Document: Add comments with decisions/learnings
- Test: Verify success criteria met
- Complete: `bd status <id> done`

**Issue Categories:**
- `[CORE]` - Core functionality
- `[ENHANCE]` - Improvements to existing features
- `[DATA]` - Data processing/quality
- `[AI]` - AI integration work
- `[ALIGN]` - Mission alignment features
- `[DOC]` - Documentation
- `[DEPLOY]` - Production/distribution

## Best Practices

1. **One task in-progress at a time** (focus)
2. **Update status promptly** (maintain context)
3. **Comment liberally** (preserve reasoning)
4. **Link related tasks** (dependencies matter)
5. **Review ready queue** (prioritize effectively)

## Integration with Git

```bash
# Commit beads state with code changes
git add .beads/
git commit -m "feat: implement feature X

Closes: bd-a1b2"

# Review beads history
git log -- .beads/
```

## Success Criteria

- [ ] Task context maintained across sessions
- [ ] Dependencies tracked and respected
- [ ] Mission alignment documented for each task
- [ ] Progress visible to all contributors
- [ ] Long-horizon goals broken into actionable tasks
