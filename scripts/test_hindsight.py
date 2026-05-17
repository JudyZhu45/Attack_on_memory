#!/usr/bin/env python
"""Smoke test for real Hindsight API."""

import os
import json
from dotenv import load_dotenv
import httpx

load_dotenv()


def test_hindsight_real():
    """Test real Hindsight REST API."""
    print("=" * 70)
    print("Hindsight Smoke Test (Real Service)")
    print("=" * 70)
    print()

    # Check environment
    endpoint = os.getenv("HINDSIGHT_ENDPOINT", "http://localhost:8888")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key.strip() == "":
        print("❌ OPENAI_API_KEY not set in .env")
        return False

    print(f"✓ OPENAI_API_KEY found")
    print(f"✓ Hindsight endpoint: {endpoint}")
    print()

    # Create HTTP client
    try:
        client = httpx.Client(base_url=endpoint, timeout=30.0)
        print("✓ HTTP client created")
    except Exception as e:
        print(f"❌ HTTP client failed: {type(e).__name__}: {e}")
        return False

    user_id = "alice"
    bank_id = f"bank-{user_id}"

    # Test 0: Check health
    print("-" * 70)
    print("TEST 0: Checking Hindsight connectivity")
    print("-" * 70)

    try:
        response = client.get("/health", timeout=5.0)
        print(f"  Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("  ✓ Hindsight is running")
            health_data = response.json()
            print(f"  Health data: {health_data}")
        print()
    except Exception as e:
        print(f"❌ Cannot connect: {type(e).__name__}: {e}")
        return False

    # Test 1: Add 3 initial facts using POST /memories
    print("-" * 70)
    print("TEST 1: Retaining 3 facts about Alice")
    print("-" * 70)

    facts_1 = [
        "I love BlueBottle coffee",
        "My favorite programming language is Rust",
        "I work at a startup in San Francisco",
    ]

    try:
        # Create memory items list
        items = [{"content": fact} for fact in facts_1]

        print(f"  Adding {len(items)} facts...")
        response = client.post(
            f"/v1/default/banks/{bank_id}/memories",
            json={"items": items, "async": False},
        )
        print(f"  Retain status: {response.status_code}")

        if response.status_code in [200, 201]:
            retain_result = response.json()
            print(f"  Retain response: {json.dumps(retain_result, indent=2)[:400]}")
            print("✓ Facts retained successfully")
        else:
            print(f"  Error: {response.text[:300]}")

        print()
    except Exception as e:
        print(f"❌ Retain failed: {type(e).__name__}: {e}")
        return False

    # Test 2: List memories
    print("-" * 70)
    print("TEST 2: Listing memories after initial facts")
    print("-" * 70)

    try:
        response = client.get(f"/v1/default/banks/{bank_id}/memories/list")
        print(f"  List memories status: {response.status_code}")
        if response.status_code == 200:
            memories = response.json()
            num_memories = memories.get("total", 0)
            print(f"  Total memories: {num_memories}")

            if num_memories > 0:
                print("  First memory object structure:")
                first_mem = memories["items"][0]
                for key in sorted(first_mem.keys()):
                    value = first_mem[key]
                    if isinstance(value, str) and len(value) > 80:
                        print(f"      {key}: <{type(value).__name__}, {len(value)} chars>")
                    else:
                        print(f"      {key}: {repr(value)[:100]}")

            print()
    except Exception as e:
        print(f"⚠ List memories: {type(e).__name__}")
        print()

    # Test 3: Recall with query
    print("-" * 70)
    print("TEST 3: Recalling memories")
    print("-" * 70)
    query = "What does Alice like?"
    print(f"  Query: '{query}'")

    try:
        response = client.post(
            f"/v1/default/banks/{bank_id}/memories/recall",
            json={"query": query},
        )
        print(f"  Recall status: {response.status_code}")
        if response.status_code == 200:
            recall_data = response.json()
            num_results = len(recall_data.get("results", []))
            print(f"  Number of results: {num_results}")

            if num_results > 0:
                print("  First result:")
                result = recall_data["results"][0]
                for key in sorted(result.keys()):
                    value = result[key]
                    if isinstance(value, str) and len(value) > 80:
                        print(f"      {key}: <{type(value).__name__}, {len(value)} chars>")
                    else:
                        print(f"      {key}: {repr(value)[:100]}")
        else:
            print(f"  Error: {response.text[:300]}")

        print()
    except Exception as e:
        print(f"❌ Recall failed: {type(e).__name__}: {e}")
        return False

    # Test 4: Test deduplication with duplicate facts
    print("-" * 70)
    print("TEST 4: Testing deduplication")
    print("-" * 70)

    facts_2 = [
        "I love BlueBottle coffee",  # exact duplicate
        "BlueBottle is my favorite coffee shop",  # semantic duplicate
    ]

    try:
        items_2 = [{"content": fact} for fact in facts_2]

        print(f"  Adding {len(items_2)} duplicate facts...")
        response = client.post(
            f"/v1/default/banks/{bank_id}/memories",
            json={"items": items_2, "async": False},
        )
        print(f"  Status: {response.status_code}")

        if response.status_code in [200, 201]:
            print("✓ Duplicates handled")
        else:
            print(f"  Error: {response.text[:300]}")

        print()
    except Exception as e:
        print(f"❌ Duplicate test failed: {type(e).__name__}: {e}")
        return False

    # Test 5: Final recall to see all memories
    print("-" * 70)
    print("TEST 5: Final recall after duplicates")
    print("-" * 70)
    print(f"  Query: '{query}'")

    try:
        response = client.post(
            f"/v1/default/banks/{bank_id}/memories/recall",
            json={"query": query},
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            recall_data = response.json()
            num_results = len(recall_data.get("results", []))
            print(f"  Number of results: {num_results}")

            print("  Results:")
            for i, result in enumerate(recall_data.get("results", []), 1):
                content = result.get("fact", {}).get("content", "N/A")
                print(f"    {i}. {content}")

        print()
    except Exception as e:
        print(f"❌ Final recall failed: {type(e).__name__}: {e}")
        return False

    # Test 6: Reflect
    print("-" * 70)
    print("TEST 6: Reflecting on memories")
    print("-" * 70)
    reflect_query = "Recommend a coffee shop"
    print(f"  Reflect query: '{reflect_query}'")

    try:
        response = client.post(
            f"/v1/default/banks/{bank_id}/reflect",
            json={"query": reflect_query},
        )
        print(f"  Reflect status: {response.status_code}")
        if response.status_code == 200:
            reflect_data = response.json()
            text = reflect_data.get("text", "")
            tokens = reflect_data.get("usage", {})

            print(f"  Response: {text[:200]}")
            print(f"  Tokens used: input={tokens.get('input_tokens')}, output={tokens.get('output_tokens')}")

        print()
    except Exception as e:
        print(f"❌ Reflect failed: {type(e).__name__}: {e}")
        return False

    # Test 7: Bank statistics
    print("-" * 70)
    print("TEST 7: Bank statistics")
    print("-" * 70)

    try:
        response = client.get(f"/v1/default/banks/{bank_id}/stats")
        print(f"  Stats status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"  Total nodes: {stats.get('total_nodes', 0)}")
            print(f"  Total links: {stats.get('total_links', 0)}")
            print(f"  Total observations: {stats.get('total_observations', 0)}")

        print()
    except Exception as e:
        print(f"⚠ Stats check: {type(e).__name__}")
        print()

    # Test 8: Entities and Mental Models
    print("-" * 70)
    print("TEST 8: Entities and Mental Models")
    print("-" * 70)

    try:
        response = client.get(f"/v1/default/banks/{bank_id}/entities")
        print(f"  Entities status: {response.status_code}")
        if response.status_code == 200:
            entities = response.json()
            num_entities = entities.get("total", 0)
            print(f"  Total entities: {num_entities}")

        response = client.get(f"/v1/default/banks/{bank_id}/mental-models")
        print(f"  Mental models status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            num_models = len(models.get("items", []))
            print(f"  Total mental models: {num_models}")

            if num_models > 0:
                print("  Mental model structure (first one):")
                model = models["items"][0]
                for key in sorted(model.keys()):
                    value = model[key]
                    if isinstance(value, (dict, list)):
                        print(f"      {key}: {type(value).__name__}")
                    elif isinstance(value, str) and len(value) > 100:
                        print(f"      {key}: <str, {len(value)} chars>")
                    else:
                        print(f"      {key}: {repr(value)[:100]}")

        print()
    except Exception as e:
        print(f"⚠ Entities/models check: {type(e).__name__}")
        print()

    client.close()

    print("=" * 70)
    print("✅ Real Hindsight API test COMPLETED!")
    print("=" * 70)
    print()
    print("📍 Hindsight Services:")
    print("  API:            http://localhost:8888")
    print("  Control Plane:  http://localhost:9999")
    print("  Swagger UI:     http://localhost:8888/docs")
    print()

    return True


if __name__ == "__main__":
    success = test_hindsight_real()
    exit(0 if success else 1)
