# Export Training Data Skill

Prepare captured knowledge for AI model training (fine-tuning or RAG).

## Goal

Transform raw transcriptions into formats suitable for LLM training, RAG systems, or knowledge graphs.

## Approach

1. **Extract all responses from database**
   ```python
   from database import KnowledgeDB
   db = KnowledgeDB()
   responses = db.get_all_responses()
   ```

2. **Format for different use cases**

   **Fine-tuning format (JSONL)**
   ```json
   {"messages": [
     {"role": "system", "content": "You are a reasoning partner..."},
     {"role": "user", "content": "Question"},
     {"role": "assistant", "content": "User's transcribed answer"}
   ]}
   ```

   **RAG format (with embeddings)**
   - Chunk long responses
   - Add metadata (category, date, question)
   - Generate embeddings using sentence-transformers

   **Knowledge graph format**
   - Extract entities and relationships
   - Create nodes (concepts) and edges (connections)
   - Export to graph database format

3. **Quality filtering**
   - Remove very short responses (< 50 chars)
   - Flag unclear transcriptions
   - Identify high-quality insights

4. **Add context enrichment**
   - Link related questions/answers
   - Add category metadata
   - Include temporal information

5. **Export multiple formats**
   - `training_data.jsonl` - For fine-tuning
   - `rag_chunks.json` - For RAG systems
   - `knowledge_graph.json` - For graph databases
   - `insights_summary.md` - Human-readable overview

## Success Criteria

- [ ] All formats generated successfully
- [ ] Quality threshold applied and documented
- [ ] Metadata preserved in all exports
- [ ] Files ready for direct use in training pipelines
- [ ] Summary report showing statistics
