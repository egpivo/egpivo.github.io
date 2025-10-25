---
layout: post
title: "Dify Knowledge Base Assistant via MCP"
tags: [Software, NLP, LLM]
math: false
---

This post outlines a high-level design for a Knowledge Base (KB) Assistant exposed via an MCP server that integrates with the Dify KB backend, with optional reflection, content boosting, and reranking. It's designed to plug easily into other orchestration pipelines (including RAG).

## Sequence Diagram

To render the following Mermaid diagram on this site, we include a minimal script block to initialize Mermaid when the page loads.

<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  if (window.mermaid) {
    mermaid.initialize({ startOnLoad: true, theme: 'default' });
  }
  document.addEventListener('DOMContentLoaded', function() {
    if (window.mermaid) { mermaid.init(); }
  });
</script>

```mermaid
sequenceDiagram
    participant Client
    participant MCP as MCP Server
    participant Auth as Auth Middleware
    participant KB as KB Assistant Service
    participant DifyKB as Dify KB Backend
    participant LLM as LLM API
    participant Rerank as Rerank API

    Client->>MCP: kb_assistant(dataset_info, query, verbose, use_content_booster, enable_reflection)
    MCP->>Auth: require_auth decorator
    Auth->>Auth: Validate credentials from headers
    Auth-->>MCP: Credentials validated
    MCP->>KB: kb_assistant_service()

    Note over KB: Parse dataset_info JSON
    KB->>KB: Extract dataset_id and source_path

    Note over KB: Extract user intention
    KB->>LLM: Generate keywords from query
    LLM-->>KB: Keywords generated

    Note over KB: Naive search approach
    KB->>DifyKB: Search documents (naive method)
    DifyKB-->>KB: Naive search results

    Note over KB: Advanced search approach
    KB->>DifyKB: Search documents (advanced method)
    DifyKB-->>KB: Advanced search results

    Note over KB: Content boosting (if enabled)
    alt use_content_booster = true
        KB->>KB: Apply content boosting
        KB->>KB: Merge and deduplicate results
    end

    Note over KB: Reranking (optional)
    alt rerank available and threshold met
        KB->>Rerank: Rerank combined results
        Rerank-->>KB: Reranked results
    end

    Note over KB: Extract final answer
    KB->>LLM: Generate comprehensive answer
    LLM-->>KB: Final answer with sources

    Note over KB: Reflection (optional)
    alt enable_reflection = true
        KB->>LLM: Reflect on answer quality
        LLM-->>KB: Quality assessment & refinements
        alt quality below threshold
            KB->>LLM: Generate refined answer
            LLM-->>KB: Improved answer
        end
    end

    KB-->>MCP: Complete results with profiling and reflection metadata
    MCP-->>Client: JSON response with answer and metadata
```

## Key Components

- **MCP Server**: Exposes `kb_assistant` tool, performs auth via decorator, forwards to service.
- **Auth Middleware**: Validates headers, short-circuits unauthorized requests.
- **KB Assistant Service**: Orchestrates parsing `dataset_info`, intention extraction, searches, merging, reranking, and final answer generation.
- **Dify KB Backend**: Provides document search for naive/advanced strategies.
- **LLM API**: Used for keyword generation, answer drafting, and optional reflection.
- **Rerank API**: Optional reranking when available and useful.

## Toggling Features

- **Content booster**: If enabled, expands context and merges/dedupes results before answering.
- **Reflection**: If enabled, runs a self-critique pass, and retries if quality is low.
- **Reranking**: Applied when a reranker is configured and results meet a threshold for usefulness.

## Response Shape

The MCP response returns the final answer along with:
- sources and snippets,
- timings/profiling info,
- flags indicating whether content booster, rerank, and reflection were used,
- and intermediate diagnostics (keywords, search stats) when verbose.


