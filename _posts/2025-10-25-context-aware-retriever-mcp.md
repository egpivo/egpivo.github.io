---
layout: post
title: "MCP Context-Aware Retriever - Introduction"
tags: [Software, NLP, LLM, AI]
math: false
redirect_from:
  - /2025/10/20/knowledge-base-assistant-mcp.html
  - /2025/10/20/knowledge-base-assistant-mcp/
---

In this post, I’ll share how I built a context-aware retriever for knowledge base question answering. It runs on top of an MCP server and can easily plug into RAG or orchestration pipelines like [`Dify`](https://docs.dify.ai/en/guides/knowledge-base/readme) or [`n8n`](https://docs.n8n.io/advanced-ai/rag-in-n8n/). The retriever includes optional steps for reflection, context expansion, and reranking to make results more robust. I’m not covering document chunking here, that is, I’ll assume that’s already handled so the focus is on making query performance smarter and more reliable.

The main goal is to make retrieval more reliable and context-aware, especially in spots where standard RAG pipelines usually fall short such as missing key clauses or struggling with overlapping documents.

## Overview
Our high-level design is depicted below.

<div style="text-align:center; margin: 1rem 0;">
  <img src="{{ site.baseurl }}/assets/images/retriever_flow.svg" alt="Context-Aware Retriever Flow" style="max-width:100%; height:auto;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Context-aware retriever pipeline.</div>
</div>

In the following sections, we’ll break down each step in more detail and show how this design can significantly improve retrieval quality within a RAG pipeline.

#### 1. File Discovery

The first challenge is: how do we find the most meaningful and relevant files when there are so many files saved in knoweldge base? To solve this, we use a structured search strategy:

> Query intent detector → Query rewriter → 
> Funnel retrieval: begin with keyword retrieval on large files to cast a wide net, follow with semantic retrieval on more focused content, and finish with a reranker to prioritize the most relevant results.

For the query intent detector and query rewriter, implemented with corresponding instructions to LLMs (e.g., `gpt-4o`), the main goal is to understand what the user is trying to do — for example, finding an exact sentence or article from a file, comparing multiple files, or focusing on a specific domain like healthcare. The system also identifies key entities, such as people or organizations, and passes this information to the query rewriter. The rewriter then adjusts the query by adding or relaxing context and motivation to make it more effective. After that, we run a multi-layer discovery process: starting with a broad keyword search, then narrowing it down with more focused semantic retrieval. Finally, we adopt a reranker model (e.g., [`jina reranker`](https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual)) to reorder the results based on the original user query and produce the top-k tuples ((file1, score1), (file2, score2), ...).


For example, let’s say we load the contract documents from [`ContractNLI`](https://stanfordnlp.github.io/contract-nli) into our knowledge base. If a user asks
> What confidentiality obligations remain in effect after the NDA expires or is terminated for evaluation of clinical cases in University of Michigan

The file search step will pick up the user’s intent (looking for a specific clause within the healcare domain) and determine there’s only one relevant file to extract the answer from. Note in this case, the ground truth lives in:

> standard_clinical_trial_nda2.pdf (Sections 5.2, 5.3, 6)

#### 2. Parallel Chunk Search
Once the relevant files are identified, the parallel chunk search step runs two retrieval strategies in parallel:
1.	A direct search using the original user query.
2.	A boosted search that expands the query with additional keywords.

The query expander is a separate LLM-based tool. It generates domain-specific keyword variations (based on the domain inferred in the file search stage) to produce `N` different query combinations—while preserving the original meaning through controlled instructions. This helps capture more relevant chunks without drifting away from the user’s intent.


#### 3. Chunk Aggregation
How we aggregate chunks depends on the user’s intent from the file search step.

-  Single-file or small file set (clause lookup):
When the user’s query targets specific clauses or paragraphs in just a few files, we treat the task more like a ranking problem where we can leverage the relevance socre per file from the file search step.
	1.	We first rank the files based on the aggregated relevance of their chunks.
	2.	If the query is about a legal clause, we preserve the original wording as much as possible.
	3.	Otherwise, we generate a concise summary from the relevant chunks.


- Multi-file comparison (cross-file analysis):
When the user wants to compare multiple files, we treat the task like a linking problem.
	1.	We identify and align key entities across files.
	2.	Then we aggregate and summarize the results by comparison, applying a defined set of measures or dimensions (e.g., clause differences, obligations, dates, or entities).

This step can be modularized, allowing additional engineering actions or post-processing layers (e.g., entity alignment).


#### 4. Reflection
There are a few research papers discussing how to build a stage to validate the results (e.g., [Renze and Guven 2024](https://arxiv.org/pdf/2405.06682)).
Nothing fancy here — in this stage, we simply run two reflection passes to improve reliability. We instruct the LLM to handle two types of checks:
1.	Search coverage reflection
- Signals: few or no high-score chunks, missing query entities in the retrieved text, or low source diversity.
- Action: generate a plan to expand or relax the query terms, then re-run file/chunk search with a revised query (e.g., broaden entities, add synonyms, adjust time ranges).

2.	Answer quality reflection
- Criteria: grounding (citations are present and relevant), completeness (answers the intent), internal consistency, and specificity.
- Action: if the score is below min_quality_score (default 0.7), re-compose the answer using the top chunks; otherwise, pass it through as-is.

One important thing to consider in this stage is how to define or find a baseline reference if we want the system to provide a fact-based answer, not just a well-phrased one.

## MCP Implementation
Our implementation leverages the[FastMCP](https://gofastmcp.com/getting-started/welcome) framework, and the overall structure is shown as follows.
<div style="text-align:center; margin: 1rem 0;">
  <img src="{{ site.baseurl }}/assets/images/mcp_arch.svg" alt="MCP Architecture" style="max-width:100%; height:auto;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">MCP server layout.</div>
</div>

Our main `qa_hub` tool acts as the entry point to coordinate all the internal tools introduced earlier.
One key takeaway during implementation was passing the knowledge base authentication through headers, which allows us to reuse the `qa_hub` MCP across different workflows or knowledge base backends.

We’ll walk through a hands-on example of this setup in the next post.
