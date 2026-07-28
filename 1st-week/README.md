# Week 1 Deliverables - Ali Mojarrad

This folder contains the Week 1 deliverables for the "Multi-Agent
Architecture and Contrastive-Reflection-Based Test Automation Framework"
project.

1. **`synthetic_files/`** - Synthetic Python files deliberately designed
   to contain architecture errors:
   - `module_a.py` + `module_b.py` -> intentional **CircularDependency**
     (they import each other)
   - `module_bad_calls.py` -> intentional **UndefinedCall** errors (calls
     helper functions that don't exist anywhere - the most common type
     of LLM hallucination)
   - `module_c.py` + `module_main.py` -> **clean files** (negative
     control, used to confirm the Watcher/Bekçi doesn't produce false
     positives on correct code)

2. **`schemas.py`** - The pinned schemas from the project document,
   reproduced exactly (`FunctionCall`, `ArchitectureError`,
   `GroundTruthSchema`).

3. **`parser.py`** - A static-analysis pipeline built on the `ast`
   module that produces a deterministic `graph.json`. It runs in two
   stages:
   - Extracts imports, defined functions, and every call inside each
     function body, per file.
   - Resolves each call (local definition / import / builtin) and runs
     a DFS-based cycle detection over the import graph.

## Running it

```bash
pip install pydantic
python3 parser.py synthetic_files/ -o graph.json
```

Output: a JSON list containing one `GroundTruthSchema` record per file
in `synthetic_files/`, sorted by `file_id`. The same input always
produces the exact same output (determinism verified - see below).

## Verification

The pipeline was run twice and the two outputs were compared with
`diff` - the results were byte-for-byte identical (satisfies the
determinism requirement).

Result summary (with the current synthetic files):
- 5 files processed, 18 calls detected, 5 architecture errors reported
- 2 CircularDependency errors (module_a <-> module_b)
- 3 UndefinedCall errors (inside module_bad_calls.py)
- module_c.py and module_main.py came back with zero errors (negative
  control passed)