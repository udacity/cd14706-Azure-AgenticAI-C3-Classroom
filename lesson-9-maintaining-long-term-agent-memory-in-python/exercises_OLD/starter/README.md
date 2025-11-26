# Exercise

Implement a long‑term memory system with seeding, search, statistics, pruning, reordering, and AI‑assisted optimization.

### **Prerequisites**

* Comfortable with async Python and class design

* Cosmos DB or local persistence is not required for this in‑memory exercise

* Lessons 1–8 completed

### **Instructions**

1. Import `LongTermMemory` from `long_term_memory.core` in `main.py`.

2. Implement `seed_sample_memories(ltm)` to add sample memories across sessions (conversation, tool_call, system_event, knowledge) with tags and varying importance to enable pruning.

3. In `run_demo()`:
   - Instantiate `LongTermMemory(max_memories=15, importance_threshold=0.3, enable_ai_scoring=True)`.
   - Call `await seed_sample_memories(ltm)`.
   - Search within a session using `ltm.search_memories(session_id, query=..., limit=...)` and log results.
   - Update importance of one memory using `ltm.update_memory_importance(id, session_id, 0.95)`.
   - Log global statistics via `ltm.get_memory_statistics()`.
   - Prune with `ltm.prune_memories(strategy='importance')` and with `strategy='hybrid'`.
   - Reorder a session with `ltm.reorder_memories(session_id, 'importance')`.
   - Run `await ltm.optimize_memory_performance()` and log the returned summary.

4. In `main()`, call `asyncio.run(run_demo())` and ensure exceptions are logged.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`