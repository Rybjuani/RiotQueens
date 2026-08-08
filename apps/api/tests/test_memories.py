"""Unit tests for the memory store.

Covers scope isolation, FIFO eviction at the bound, stable IDs, and
explicit-fact-only schema.

All tests are deterministic and do NOT call any paid model.
"""

from __future__ import annotations

import pytest

from app.domain.memories import (
    MEMORY_CONFIDENCE_HIGH,
    MEMORY_SOURCE_EXPLICIT,
    MEMORY_TYPE_USER_FACT,
    InProcessMemoryStore,
    MemoryScopeKey,
    memory_context_section,
)


def _scope(user: str = "user-1", character: str = "vane") -> MemoryScopeKey:
    return MemoryScopeKey(user_id=user, character_id=character)


@pytest.mark.asyncio
async def test_add_memory_returns_explicit_fact_record() -> None:
    store = InProcessMemoryStore(max_per_scope=32)
    rec = await store.add_memory(_scope(), "Mi color favorito es negro.")
    assert rec.content == "Mi color favorito es negro."
    assert rec.memory_type == MEMORY_TYPE_USER_FACT
    assert rec.source == MEMORY_SOURCE_EXPLICIT
    assert rec.confidence == MEMORY_CONFIDENCE_HIGH
    assert rec.inferred is False
    assert rec.id  # stable id present
    assert rec.user_id == "user-1"
    assert rec.character_id == "vane"


@pytest.mark.asyncio
async def test_list_memories_returns_only_correct_scope() -> None:
    store = InProcessMemoryStore(max_per_scope=32)
    await store.add_memory(_scope(user="alice"), "fact A")
    await store.add_memory(_scope(user="alice"), "fact B")
    await store.add_memory(_scope(user="bob"), "fact C")
    # Alice has 2, Bob has 1, different character is fully isolated
    await store.add_memory(_scope(user="alice", character="other"), "fact D")

    alice = await store.list_memories(_scope(user="alice"))
    bob = await store.list_memories(_scope(user="bob"))
    alice_other = await store.list_memories(_scope(user="alice", character="other"))

    assert {r.content for r in alice} == {"fact A", "fact B"}
    assert {r.content for r in bob} == {"fact C"}
    assert {r.content for r in alice_other} == {"fact D"}


@pytest.mark.asyncio
async def test_delete_memory_by_id_only_within_scope() -> None:
    store = InProcessMemoryStore(max_per_scope=32)
    rec = await store.add_memory(_scope(user="alice"), "to delete")
    # Try to delete from a different user — should fail (returns False).
    cross = await store.delete_memory(_scope(user="bob"), rec.id)
    assert cross is False
    # Delete from the correct scope.
    ok = await store.delete_memory(_scope(user="alice"), rec.id)
    assert ok is True
    # Verify it's gone.
    alice = await store.list_memories(_scope(user="alice"))
    assert alice == []


@pytest.mark.asyncio
async def test_delete_unknown_id_returns_false() -> None:
    store = InProcessMemoryStore(max_per_scope=32)
    ok = await store.delete_memory(_scope(), "does-not-exist")
    assert ok is False


@pytest.mark.asyncio
async def test_max_per_scope_evicts_oldest_fifo() -> None:
    store = InProcessMemoryStore(max_per_scope=2)
    scope = _scope()
    await store.add_memory(scope, "first")  # will be evicted
    r2 = await store.add_memory(scope, "second")
    r3 = await store.add_memory(scope, "third")  # evicts "first"
    listed = await store.list_memories(scope)
    assert [r.id for r in listed] == [r2.id, r3.id]
    assert [r.content for r in listed] == ["second", "third"]


@pytest.mark.asyncio
async def test_delete_all_for_scope_returns_count() -> None:
    store = InProcessMemoryStore(max_per_scope=32)
    scope_a = _scope(user="alice")
    scope_b = _scope(user="bob")
    await store.add_memory(scope_a, "a1")
    await store.add_memory(scope_a, "a2")
    await store.add_memory(scope_b, "b1")
    n_a = await store.delete_all_for_scope(scope_a)
    assert n_a == 2
    # scope_b untouched
    bob = await store.list_memories(scope_b)
    assert [r.content for r in bob] == ["b1"]
    # Re-delete scope_a → 0
    n_a_again = await store.delete_all_for_scope(scope_a)
    assert n_a_again == 0


def test_memory_context_section_returns_none_when_empty() -> None:
    assert memory_context_section([]) is None


def test_memory_context_section_returns_bullets() -> None:
    """Verify the injected memory context section is a clearly-delimited
    Spanish bullet list with the explicit facts.
    """
    from app.domain.memories import MemoryRecord

    records = [
        MemoryRecord(
            id="1",
            user_id="u",
            character_id="vane",
            content="Mi color favorito es negro.",
        ),
        MemoryRecord(
            id="2",
            user_id="u",
            character_id="vane",
            content="Me gusta el café por la tarde.",
        ),
    ]
    section = memory_context_section(records)
    assert section is not None
    assert section.startswith("Memorias explícitas del usuario:")
    assert "- Mi color favorito es negro." in section
    assert "- Me gusta el café por la tarde." in section


def test_memory_context_section_is_separate_from_vane_prompt() -> None:
    """The memory section must NOT contain the canonical Vane system prompt
    content (e.g. "Sos Vane"). It is its own block, prepended separately.
    """
    from app.domain.memories import MemoryRecord

    records = [
        MemoryRecord(
            id="1",
            user_id="u",
            character_id="vane",
            content="algo simple.",
        ),
    ]
    section = memory_context_section(records)
    assert section is not None
    assert "Sos Vane" not in section
    assert "compañera IA adulta" not in section
