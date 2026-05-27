# Put src/ on sys.path so tests can `import data_update` / `import rag_query`
# directly. pytest imports this conftest before collecting tests.
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
