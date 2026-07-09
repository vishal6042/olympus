"""Make the milestone2/ package modules importable when running pytest from anywhere.

prompts.py imports sibling modules (examples, schema, ...) by top-level name, so the
milestone2/ directory must be on sys.path. Importing prompts here does NOT touch the LLM
or network — config.py is only imported by analyzer.py, which these tests never load.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
