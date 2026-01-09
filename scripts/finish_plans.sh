#!/bin/bash
# Run at 1 AM PST to finish paleoseismic plans

cd /Users/catherine/projects/quake

# Run Claude Code with the task
claude -p "Continue and finish all tasks from these plan files:
1. ~/.claude/plans/declarative-mapping-valley.md (index papers into RAG)
2. ~/.claude/plans/optimized-churning-music.md (analyze 939 CE Eldgjá window)
3. ~/.claude/plans/fuzzy-pondering-aho.md (Titan terminology audit - update 11 files)

Execute all tasks completely. Save a summary to paleoseismic_caves/COMPLETED_TASKS.md when done."
