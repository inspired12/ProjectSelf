# Test Transcription Skill

Test the Whisper transcription system with various audio inputs and scenarios.

## Goal

Verify transcription accuracy and identify potential improvements without running the full Flask app.

## Approach

1. **Create test audio samples** (if not provided)
   - Generate synthetic speech or use sample audio
   - Vary: speech rate, accent, background noise, audio quality

2. **Test transcription directly**
   ```python
   import whisper
   model = whisper.load_model("base")
   result = model.transcribe("test_audio.wav")
   print(f"Transcription: {result['text']}")
   print(f"Language: {result['language']}")
   ```

3. **Compare models** (tiny, base, small)
   - Measure: accuracy, speed, memory usage
   - Document tradeoffs

4. **Test edge cases**
   - Very short audio (< 1 second)
   - Very long audio (> 5 minutes)
   - Silence or noise only
   - Multiple speakers
   - Technical jargon

5. **Verify success**
   - All test cases complete without errors
   - Transcription quality meets expectations
   - Performance metrics documented

## Success Criteria

- [ ] At least 5 different test audio samples processed
- [ ] Transcription accuracy rated for each model
- [ ] Edge cases documented with behavior
- [ ] Recommendation provided for default model
