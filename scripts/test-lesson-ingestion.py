#!/usr/bin/env python3
"""
Test script for ingesting educational lessons into RAG and testing retrieval.

This script:
1. Verifies Java loader is not needed (lessons are markdown)
2. Tests ingestion of all lessons
3. Tests retrieval for each language (Python, TypeScript, Java)
4. Tests lesson generation with error patterns
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "libs" / "agentic-py" / "src"))

from agentic_py.rag.loaders import load_markdown  # noqa: E402
from agentic_py.rag.service import RagService  # noqa: E402


async def test_loader():
    """Verify markdown loader can handle lesson files with frontmatter."""
    print("=" * 60)
    print("Test 1: Verifying Markdown Loader with Frontmatter")
    print("=" * 60)

    # Test with a sample lesson
    test_lesson = (
        project_root
        / "docs"
        / "lessons"
        / "python"
        / "beginner"
        / "01-variables-and-data-types.md"
    )

    if not test_lesson.exists():
        print(f"❌ Test lesson not found: {test_lesson}")
        return False

    try:
        doc = load_markdown(test_lesson)

        # Check that frontmatter was extracted
        assert "title" in doc.metadata, "Title not in metadata"
        assert "language" in doc.metadata, "Language not in metadata"
        assert "difficulty" in doc.metadata, "Difficulty not in metadata"
        assert (
            doc.metadata["language"] == "python"
        ), f"Expected python, got {doc.metadata['language']}"
        assert (
            doc.metadata["difficulty"] == "beginner"
        ), f"Expected beginner, got {doc.metadata['difficulty']}"

        print("✅ Markdown loader works correctly")
        print(f"   Title: {doc.metadata.get('title')}")
        print(f"   Language: {doc.metadata.get('language')}")
        print(f"   Difficulty: {doc.metadata.get('difficulty')}")
        print(f"   Keywords: {doc.metadata.get('keywords', [])}")
        print(f"   Content length: {len(doc.page_content)} characters")
        return True

    except Exception as e:
        print(f"❌ Error loading lesson: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_ingestion():
    """Test ingesting all lessons into RAG."""
    print("\n" + "=" * 60)
    print("Test 2: Ingesting All Lessons")
    print("=" * 60)

    lessons_dir = project_root / "docs" / "lessons"

    if not lessons_dir.exists():
        print(f"❌ Lessons directory not found: {lessons_dir}")
        return False

    # Count lesson files
    lesson_files = list(lessons_dir.rglob("*.md"))
    lesson_files = [f for f in lesson_files if f.name not in ["README.md", "INDEX.md"]]

    print(f"Found {len(lesson_files)} lesson files")

    # Initialize RAG service
    service = RagService(enabled=True)

    try:
        # Ingest directory
        print("Ingesting lessons directory...")
        result = await service.ingest_directory(
            lessons_dir, file_patterns=["*.md"], recursive=True
        )

        print("✅ Ingestion completed!")
        print(f"   Files processed: {result['files_processed']}")
        print(f"   Total chunks: {result['total_chunks']}")

        if result["errors"]:
            print(f"   ⚠️  Errors: {len(result['errors'])}")
            for error in result["errors"][:5]:
                print(f"      - {error}")

        return result["files_processed"] > 0

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_retrieval():
    """Test retrieval for each language."""
    print("\n" + "=" * 60)
    print("Test 3: Testing Retrieval for Each Language")
    print("=" * 60)

    service = RagService(enabled=True)

    test_queries = [
        ("Python", "How do I create variables in Python?"),
        ("TypeScript", "How do I declare variables with types in TypeScript?"),
        ("Java", "How do I declare variables in Java?"),
        ("Python", "What are Python list comprehensions?"),
        ("TypeScript", "How do I use async/await in TypeScript?"),
        ("Java", "How do I use streams in Java?"),
    ]

    results = []

    for language, query in test_queries:
        try:
            print(f"\nQuery ({language}): {query}")
            context = await service.query_knowledge(query, top_k=3)

            if context and "Vector store not available" not in context:
                print(f"✅ Retrieved context ({len(context)} chars)")
                # Show first 200 chars
                preview = context[:200].replace("\n", " ")
                print(f"   Preview: {preview}...")
                results.append(True)
            else:
                print("⚠️  No context retrieved or vector store not available")
                results.append(False)

        except Exception as e:
            print(f"❌ Error querying: {e}")
            results.append(False)

    success_count = sum(results)
    print(
        f"\n✅ Retrieval test: {success_count}/{len(test_queries)} queries successful"
    )
    return success_count > 0


async def test_error_pattern_retrieval():
    """Test retrieval with error patterns (simulating struggle detection)."""
    print("\n" + "=" * 60)
    print("Test 4: Testing Retrieval with Error Patterns")
    print("=" * 60)

    service = RagService(enabled=True)

    test_cases = [
        {
            "query": "Help with errors",
            "error_patterns": [
                "NameError: name 'x' is not defined",
                "undefined variable",
            ],
            "language": "Python",
        },
        {
            "query": "Type errors",
            "error_patterns": [
                "TypeError: Cannot read property",
                "undefined is not a function",
            ],
            "language": "TypeScript",
        },
        {
            "query": "Null pointer exception",
            "error_patterns": ["NullPointerException", "null reference"],
            "language": "Java",
        },
    ]

    results = []

    for case in test_cases:
        try:
            print(f"\nError Pattern Test ({case['language']}):")
            print(f"  Query: {case['query']}")
            print(f"  Errors: {case['error_patterns']}")

            context = await service.query_knowledge(
                case["query"], error_patterns=case["error_patterns"], top_k=3
            )

            if context and "Vector store not available" not in context:
                print(f"✅ Retrieved relevant context ({len(context)} chars)")
                preview = context[:200].replace("\n", " ")
                print(f"   Preview: {preview}...")
                results.append(True)
            else:
                print("⚠️  No context retrieved")
                results.append(False)

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)

    success_count = sum(results)
    print(
        f"\n✅ Error pattern test: {success_count}/{len(test_cases)} cases successful"
    )
    return success_count > 0


async def main():
    """Run all tests."""
    print("Educational Lessons RAG Integration Test")
    print("=" * 60)

    results = []

    # Test 1: Verify loader
    results.append(await test_loader())

    # Test 2: Ingest lessons
    results.append(await test_ingestion())

    # Test 3: Test retrieval
    results.append(await test_retrieval())

    # Test 4: Test error pattern retrieval
    results.append(await test_error_pattern_retrieval())

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {sum(results)}/{len(results)}")

    if all(results):
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
