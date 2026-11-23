# 0016. LangMem retrieval patterns for enterprise LangGraph (Microsoft + LangGraph + LangChain)

- **Status:** Proposed (2026-11-23)
- **Scope:** This is a forward-looking decision for Pedro's enterprise stack: Azure OpenAI with Entra ID, LangChain, LangGraph `StateGraph`, and Azure Cosmos DB for NoSQL. It is **not** retrospective, and nothing in this repo's code evidences it. It is filed here because this repo is the reference for LangGraph stores, which is where cross-thread memory lives (see the README and ADRs 0004 and 0007).
- **Versions:** LangMem 0.0.30 and LangGraph 1.2.24.

## Context

Long-term memory in LangGraph lives in a `BaseStore`. LangMem 0.0.30 is a pre-1.0 library on top of that store. It offers three ways to read and write memory, and they differ on **who decides** when memory is read or written.

| # | Pattern | How it works | Who decides |
|---|---|---|---|
| 1 | Hot-path tools | `create_manage_memory_tool` and `create_search_memory_tool` are attached to the agent | The model, on every turn |
| 2 | Prompt-function injection | A callable runs before the LLM node, calls `get_store()` and `store.search()` on the current input, and injects the hits into the system message as a `<memories>` block | Code, never the model |
| 3 | Background consolidation | After the thread ends, a memory manager (`create_memory_store_manager`, optionally through `ReflectionExecutor`) extracts semantic, episodic and procedural memories and merges them into the store under defined namespaces | Code chooses when; an LLM chooses what is kept |

Pattern 3 is the closest analog to Pedro's Dreaming Bot nightly distill.

LangMem's hot-path quickstart shows Pattern 2 directly, with `get_store()` and `store.search()` inside the `prompt` callable. It also says the tools "work in any node in `StateGraph`, `@entrypoint`", not only in the prebuilt `create_react_agent`.

**Security premise (Pedro):** memory is a persistent prompt. An indirect prompt injection can plant an entry that writes to memory instead of firing immediately. That entry survives restarts and context wipes. Later, the distillation step can launder it into clean-looking memory.

### Comparison

| Dimension | 1. Hot-path tools | 2. Prompt-function | 3. Background |
|---|---|---|---|
| Turn latency | High: extra tool-call round trips | Low: one embedding call and one search | None on the turn |
| Determinism / audit | Low | High: a fixed code path | Medium: fixed trigger, but the LLM chooses what to keep |
| Injection exposure | Highest. Poisoned memory can steer whether retrieval happens at all, and injected text can trigger writes mid-turn | On the read side, a validation gate can sit between `search` and the context window | On the write side, the consolidator can launder a planted entry |
| Flexibility | High | Medium: fixed query rule | n/a (write path) |
| Cosmos DB fit | Writes are scattered mid-turn | `CosmosDBStore.search` (needs `index`) | Batched writes, each visible in the change feed |

## Decision

1. **Primary read path: Pattern 2, prompt-function injection.** A pre-LLM node or callable runs `store.search(namespace, query=<current input>)`. The hits go through a **read-side validation gate** before the `<memories>` block is rendered. The model gets no memory tools by default.
2. **Write-side validation gate, audited through the Azure Cosmos DB change feed** on the store container. Every memory write is observable outside the agent. Caveat: the default latest-version mode records no deletes and no intermediate updates. A full audit trail needs **all-versions-and-deletes** mode. That mode requires continuous backup, works only on the NoSQL API, cannot read from the beginning, and gives no previous version of an item.
3. **Secondary write path: Pattern 3, background consolidation, gated separately.** It runs off the hot path, under its own namespace and identity, and its output goes through the write-side gate before it becomes retrievable.
4. **Pattern 1 is not used** in enterprise graphs.

The gate contents are not specified yet. Provenance (namespace, writer identity, source thread), an instruction-like-content filter, a size cap and a quarantine flag are candidate checks, not decisions (A-020).

## Consequences

**Positive**
- Retrieval is deterministic and testable, with one choke point between memory and the context window.
- No model judgement over recall, and no tool round trip on the turn.
- There is no mid-turn write channel for injected text.
- Writes are auditable outside the agent, through the change feed.
- Pattern 2 needs only the LangGraph `BaseStore` API, so it survives dropping LangMem.

**Negative**
- Every turn pays for an embedding and a search, even when memory is irrelevant.
- A fixed query rule can miss memories that a model-driven search would find.
- The read-side gate does not catch laundered memory that already looks clean. Provenance and the write-side audit have to carry that risk.
- The gates are new code to own, and a weak gate is false comfort.
- Full change-feed audit needs all-versions-and-deletes mode and its prerequisites.
- **Dependency risk.** LangMem is pre-1.0, and 0.0.30 (2025-10-27) is its latest release. LangChain's current long-term-memory docs build memory directly on the LangGraph store and don't name LangMem. The add-memory page mentions only `langmem.short_term`. For an enterprise decision, the open question is whether LangMem should stay the dependency for Pattern 3 or whether consolidation should be built natively on the store (A-016).
- LangMem hard-depends on `langchain-anthropic`, `langchain-openai` and `trustcall`. That widens the supply-chain surface of an Azure-only stack.

## Alternatives considered

- **Pattern 1 as the default.** Rejected. It has the highest injection exposure, recall is non-deterministic, and it adds latency. It may be acceptable for low-risk single-user assistants.
- **Pattern 3 only, with retrieval left to the model.** Rejected. Retrieval would still need either tools, which brings Pattern 1's exposure, or a pre-LLM search, which is Pattern 2.
- **Native memory on the LangGraph store, without LangMem.** Kept open. Pattern 2 is already native. The prototype decides whether LangMem's extraction is worth the dependency.

## Next step

1. Build a prototype `StateGraph` on `AsyncCosmosDBStore` with `index` and Entra ID, on a non-production account.
2. Add a Pattern 2 node with a stub gate that logs what it passes and blocks.
3. Run LangMem extraction on fixed test sessions, including seeded injection and planted-fact sessions.
4. Inspect what it keeps, merges and drops.
5. Consume the change feed in both modes.

## Evidence

Sources were accessed 2026-11-23 unless marked otherwise.

- Pedro, conversation 2026-11-23: the patterns, the security premise, the decision lean, the versions, and the docs-shift risk.
- LangMem 0.0.30 on PyPI, wheel uploaded 2025-10-27T22:21Z. Its `requires_dist` includes `langgraph<2,>=0.6.0` and `langchain-anthropic`: <https://pypi.org/pypi/langmem/0.0.30/json>
- LangGraph 1.2.24 on PyPI, uploaded 2026-11-20T01:10Z: <https://pypi.org/pypi/langgraph/1.2.24/json>
- LangMem hot-path quickstart (Pattern 2 `prompt` callable; "any node in `StateGraph`, `@entrypoint`"): <https://langchain-ai.github.io/langmem/hot_path_quickstart/>
- LangMem background quickstart (`create_memory_store_manager`, `ReflectionExecutor`): <https://langchain-ai.github.io/langmem/background_quickstart/>
- LangMem conceptual guide (semantic, episodic and procedural memory): <https://langchain-ai.github.io/langmem/concepts/conceptual_guide/>
- LangChain docs. The add-memory page references only `langmem.short_term`. The long-term-memory and memory-concepts pages have no "LangMem" string:
  - <https://docs.langchain.com/oss/python/langgraph/add-memory>
  - <https://docs.langchain.com/oss/python/langchain/long-term-memory>
  - <https://docs.langchain.com/oss/python/concepts/memory>
- `CosmosDBStore` / `AsyncCosmosDBStore` in `langchain-azure-cosmosdb` 1.0.1 (2026-09-24):
  - <https://github.com/langchain-ai/langchain-azure/blob/main/libs/azure-cosmosdb/README.md>
  - <https://reference.langchain.com/python/langchain-azure-cosmosdb/_langgraph_store/CosmosDBStore>
- Cosmos DB change feed modes: <https://learn.microsoft.com/en-us/azure/cosmos-db/change-feed-modes>
- In this repo: `README.md` (stores vs checkpoints), `docs/references.md`, ADR 0004 (backend factory) and ADR 0007 (store semantic search).
- Assumptions: A-016 to A-023 in [`../assumptions.md`](../assumptions.md).
