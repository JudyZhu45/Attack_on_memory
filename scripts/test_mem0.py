#!/usr/bin/env python
"""Smoke test for mem0 integration with OpenAI backend."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_mem0_with_openai():
    """Test basic mem0 functionality with OpenAI LLM and embeddings."""
    print("=" * 70)
    print("mem0 Smoke Test (OpenAI Backend)")
    print("=" * 70)
    print()

    # Check API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key.strip() == "":
        print("❌ OPENAI_API_KEY not set or empty in .env")
        return False

    print("✓ OPENAI_API_KEY found")
    print()

    # Initialize mem0 with OpenAI
    try:
        from mem0 import Memory

        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-3.5-turbo",
                    "api_key": openai_key,
                },
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                    "api_key": openai_key,
                },
            },
        }

        print("Initializing mem0 with OpenAI backend...")
        memory = Memory.from_config(config)
        print("✓ mem0 client initialized")
        print()

    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return False
    except Exception as e:
        print(f"❌ Initialization failed: {type(e).__name__}: {e}")
        return False

    # Test 1: Add 3 initial facts
    print("-" * 70)
    print("TEST 1: Adding 3 initial facts about alice")
    print("-" * 70)
    user_id = "alice"

    facts_1 = [
        "I love BlueBottle coffee",
        "My favorite programming language is Rust",
        "I work at a startup in San Francisco",
    ]

    try:
        for fact in facts_1:
            print(f"  Adding: {fact}")
            memory.add(fact, user_id=user_id)  # add() still uses user_id
        print("✓ All 3 facts added")
        print()
    except Exception as e:
        print(f"❌ Failed to add facts: {type(e).__name__}: {e}")
        return False

    # Test 2: Search memory
    print("-" * 70)
    print("TEST 2: Searching memory with query")
    print("-" * 70)
    query = "What does Alice like?"
    print(f"  Query: '{query}'")

    try:
        search_results = memory.search(query=query, filters={"user_id": user_id})
        print(f"  Search results type: {type(search_results)}")

        if isinstance(search_results, dict) and "results" in search_results:
            results_list = search_results["results"]
            print(f"  Number of results: {len(results_list)}")
            if len(results_list) > 0:
                print("  First result structure:")
                first = results_list[0]
                for key in sorted(first.keys()):
                    value = first[key]
                    if isinstance(value, str) and len(value) > 60:
                        print(f"      {key}: <str, {len(value)} chars>")
                    else:
                        print(f"      {key}: {repr(value)}")
        print()
    except Exception as e:
        print(f"❌ Search failed: {type(e).__name__}: {e}")
        return False

    # Test 3: Dump all memories (first batch)
    print("-" * 70)
    print("TEST 3: Dump all memories (after initial facts)")
    print("-" * 70)

    try:
        all_memories_resp = memory.get_all(filters={"user_id": user_id})
        print(f"  Response type: {type(all_memories_resp)}")

        # Extract results list from response
        if isinstance(all_memories_resp, dict) and "results" in all_memories_resp:
            all_memories_1 = all_memories_resp["results"]
        else:
            all_memories_1 = all_memories_resp if isinstance(all_memories_resp, list) else []

        print(f"  Total memories: {len(all_memories_1)}")
        print()

        if isinstance(all_memories_1, list) and len(all_memories_1) > 0:
            print("  Memory object structure (first item):")
            first_mem = all_memories_1[0]
            print(f"    Type: {type(first_mem)}")
            if isinstance(first_mem, dict):
                for key in sorted(first_mem.keys()):
                    value = first_mem[key]
                    if isinstance(value, str) and len(value) > 80:
                        print(f"      {key}: <str, {len(value)} chars>")
                    else:
                        print(f"      {key}: {repr(value)}")

            print()
            print("  All memories:")
            for i, mem in enumerate(all_memories_1, 1):
                if isinstance(mem, dict):
                    mem_text = mem.get("memory", str(mem)[:80])
                    mem_id = mem.get("id", "")[:8]
                    print(f"    {i}. [{mem_id}...] {mem_text}")
                else:
                    mem_text = getattr(mem, "memory", str(mem)[:80])
                    print(f"    {i}. {mem_text}")

        print()
    except Exception as e:
        print(f"❌ get_all failed: {type(e).__name__}: {e}")
        return False

    # Test 4: Add duplicate facts
    print("-" * 70)
    print("TEST 4: Testing deduplication with duplicate facts")
    print("-" * 70)

    facts_2 = [
        "I love BlueBottle coffee",  # exact duplicate
        "BlueBottle is my favorite coffee shop",  # semantic duplicate
    ]

    try:
        for fact in facts_2:
            print(f"  Adding: {fact}")
            memory.add(fact, user_id=user_id)  # add() still uses user_id
        print("✓ Duplicate facts added")
        print()
    except Exception as e:
        print(f"❌ Failed to add duplicate facts: {type(e).__name__}: {e}")
        return False

    # Test 5: Dump all memories (final state)
    print("-" * 70)
    print("TEST 5: Final memory dump (after duplicates)")
    print("-" * 70)

    try:
        all_memories_resp_2 = memory.get_all(filters={"user_id": user_id})

        # Extract results list from response
        if isinstance(all_memories_resp_2, dict) and "results" in all_memories_resp_2:
            all_memories_2 = all_memories_resp_2["results"]
        else:
            all_memories_2 = (
                all_memories_resp_2 if isinstance(all_memories_resp_2, list) else []
            )

        print(f"  Total memories: {len(all_memories_2)}")

        if len(all_memories_1) > 0 and len(all_memories_2) > 0:
            delta = len(all_memories_2) - len(all_memories_1)
            if delta == 0:
                print(f"  ℹ Deduplication: Duplicates were MERGED (no growth)")
            else:
                print(f"  ℹ Deduplication: Duplicates kept as SEPARATE entries (+{delta} items)")

        print()
        print("  Final memories:")
        for i, mem in enumerate(all_memories_2, 1):
            if isinstance(mem, dict):
                mem_text = mem.get("memory", str(mem)[:80])
                mem_id = mem.get("id", "")[:8]
                created = mem.get("created_at", "")
                print(
                    f"    {i}. [{mem_id}...] {mem_text}"
                )
                print(f"       Created: {created}")
            else:
                mem_text = getattr(mem, "memory", str(mem)[:80])
                print(f"    {i}. {mem_text}")

        print()
    except Exception as e:
        print(f"❌ Final get_all failed: {type(e).__name__}: {e}")
        return False

    print("=" * 70)
    print("✅ mem0 smoke test PASSED!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_mem0_with_openai()
    exit(0 if success else 1)
