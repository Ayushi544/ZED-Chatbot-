"""
test_rag.py — RAG retrieval quality audit
==========================================
Run this after every index rebuild to verify retrieval correctness.

Usage:
    cd backend
    python test_rag.py

Each test query checks:
1. Were relevant chunks retrieved? (keyword presence)
2. What was the confidence level?
3. What source documents were used?
"""

import sys
from pathlib import Path

# Ensure we can import rag.py
sys.path.insert(0, str(Path(__file__).parent))

from rag import retrieve, INDEX_LOADED, FAISS_AVAILABLE, EMBEDDER_AVAILABLE

print("=" * 60)
print("ZED Mitra — RAG Retrieval Quality Test")
print("=" * 60)
print(f"  FAISS available:    {FAISS_AVAILABLE}")
print(f"  Embedder available: {EMBEDDER_AVAILABLE}")
print(f"  Index loaded:       {INDEX_LOADED}")
print()

if not INDEX_LOADED:
    print("[WARN] FAISS index not loaded — tests will use keyword fallback only.")
    print("       Run extract_docs.py first to build the index.")
    print()

# ── Test queries ──
# Each tuple: (query, list_of_expected_keywords, description)
TEST_QUERIES = [
    (
        "What documents are needed for Bronze certification?",
        ["document", "bronze", "udyam"],
        "Bronze documents"
    ),
    (
        "What is the subsidy for micro enterprises?",
        ["subsidy", "micro", "80"],
        "Subsidy info"
    ),
    (
        "Tell me about textile sector ZED guidance",
        ["textile"],
        "Textile sector"
    ),
    (
        "How to get Gold certification?",
        ["gold"],
        "Gold process"
    ),
    (
        "What is 5S workplace organisation?",
        ["5s", "workplace"],
        "5S parameter"
    ),
    (
        "What are the 10 ZED parameters?",
        ["parameter", "leadership"],
        "ZED parameters"
    ),
    (
        "ISO 9001 waiver in ZED",
        ["iso", "waiv"],
        "ISO waivers"
    ),
    (
        "What is ZED Pledge?",
        ["pledge"],
        "ZED Pledge"
    ),
    (
        "How to register on UDYAM?",
        ["udyam", "registr"],
        "UDYAM registration"
    ),
    (
        "Food processing sector ZED requirements",
        ["food"],
        "Food sector"
    ),
]

# ── Run tests ──
passed = 0
failed = 0
total  = len(TEST_QUERIES)

print("-" * 60)
for i, (query, expected_keywords, desc) in enumerate(TEST_QUERIES, 1):
    context, source = retrieve(query)
    context_lower = context.lower()

    # Check if ANY expected keyword is present
    found = [kw for kw in expected_keywords if kw.lower() in context_lower]
    missing = [kw for kw in expected_keywords if kw.lower() not in context_lower]

    if found:
        status = "✅ PASS"
        passed += 1
    else:
        status = "❌ FAIL"
        failed += 1

    print(f"\n  Test {i}/{total}: {desc}")
    print(f"  {status}")
    print(f"  Query:   {query}")
    print(f"  Source:   {source}")
    print(f"  Found:   {found}")
    if missing:
        print(f"  Missing: {missing}")
    print(f"  Preview: {context[:120]}...")

print("\n" + "=" * 60)
print(f"  Results: {passed}/{total} passed, {failed}/{total} failed")
if failed == 0:
    print("  🎉 All tests passed!")
elif failed <= 2:
    print("  ⚠️  Some tests failed — consider tuning DISTANCE_THRESHOLD in rag.py")
else:
    print("  ❌ Many tests failed — rebuild your index or check your documents")
print("=" * 60)
"""
Description: Test script to audit RAG retrieval quality. Run after every index rebuild.
"""
