---
layout: post
title: "How I’m Building a Context-Aware Retriever to Boost RAG Quality (Part 1: Introduction)"
tags: [Software, NLP, LLM, AI]
math: false
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
As a quick note: chunking is assumed to be handled upstream so we can focus here on retrieval and orchestration.

#### 1. File Discovery

The first challenge is: how do we find the most meaningful and relevant files when there are so many files saved in knowledge base? To solve this, we use a structured search strategy:

> Query intent detector → optional query rewriter →
> Semantic retrieval with optional file-level reranking (e.g., `Jina`) to prioritize the most relevant files. Keyword generation is used later as a content booster during per-file processing rather than as the first pass.

For the query intent detector and query rewriter (implemented with LLMs such as `gpt-4o`), the main goal is to understand what the user is trying to do — for example, finding an exact sentence or article from a file, comparing multiple files, or focusing on a specific domain like healthcare. The system also identifies key entities, such as people or organizations, and passes this information to the query rewriter. The rewriter then adjusts the query by adding or relaxing context to make it more effective. After that, we run semantic retrieval and, when configured, apply a file reranker (e.g., [`jina reranker`](https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual)) to reorder the files and produce the top-k tuples ((file1, score1), (file2, score2), ...).


For example, let’s say we load the contract documents from [`ContractNLI`](https://stanfordnlp.github.io/contract-nli) into our knowledge base. If a user asks
> What confidentiality obligations remain in effect after the NDA expires or is terminated for evaluation of clinical cases in University of Michigan

The file search step will pick up the user’s intent (looking for a specific clause within the healthcare domain) and determine there’s only one relevant file to extract the answer from. Note in this case, the ground truth lives in:

> standard_clinical_trial_nda2.pdf (Sections 5.2, 5.3, 6)

#### 2. Multi-variant Chunk Search
Once the relevant files are identified, the system runs multiple query variants per file:
1.	A direct search using the original user query.
2.	Additional boosted queries generated from LLM-based keyword sets.

Files are processed in parallel, while per-file query variants may execute sequentially depending on configuration. The query expander is a separate LLM-based tool. It generates domain-specific keyword variations (based on the domain inferred in the file search stage) to produce `N` different query combinations—while preserving the original meaning through controlled instructions. This helps capture more relevant chunks without drifting away from the user’s intent.


#### 3. Chunk Aggregation
How we aggregate chunks depends on the user’s intent from the file search step.

-  Single-file or small file set (clause lookup):
When the user’s query targets specific clauses or paragraphs in just a few files, we treat the task more like a ranking problem where we can leverage the relevance score per file from the file search step.
	1.	We first rank the files based on the aggregated relevance of their chunks.
	2.	If the query is about a legal clause, we preserve the original wording as much as possible.
	3.	Otherwise, we generate a concise summary from the relevant chunks.


- Multi-file comparison (cross-file analysis):
When the user wants to compare multiple files, we treat the task like a linking problem.
	1.	We identify and align key entities across files.
	2.	Then we aggregate and summarize the results by comparison, applying a defined set of measures or dimensions (e.g., clause differences, obligations, dates, or entities).

This step can be modularized, allowing additional engineering actions or post-processing layers (e.g., entity alignment).


#### 4. Reflection
There are a few research papers discussing how to validate results (e.g., [Renze and Guven 2024](https://arxiv.org/pdf/2405.06682)).
Currently, we implement answer quality reflection: the LLM evaluates grounding, completeness, internal consistency, and specificity, and can refine the answer up to a small number of iterations if quality is below a threshold. A search-coverage reflection stage (which would broaden or relax queries and re-run retrieval) is planned but not yet enabled in this release.

## MCP Implementation
Our implementation leverages the [FastMCP](https://gofastmcp.com/getting-started/welcome) framework, and the overall structure is shown as follows.
<div style="text-align:center; margin: 1rem 0;">
  <img src="{{ site.baseurl }}/assets/images/mcp_arch.svg" alt="MCP Architecture" style="max-width:100%; height:auto;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">MCP server layout.</div>
</div>

Our main `assistant` tool (served by the `kbbridge` MCP server) acts as the entry point to coordinate the internal tools introduced earlier.
One key takeaway during implementation was passing the knowledge base authentication through headers, which allows us to reuse the MCP server across different workflows or knowledge base backends. Typical headers include `X-RETRIEVAL-ENDPOINT`, `X-RETRIEVAL-API-KEY`, `X-LLM-API-URL`, `X-LLM-MODEL`, and optional reranker headers like `X-RERANK-URL` and `X-RERANK-MODEL`.

We’ll walk through a hands-on example of this setup in the next post.
