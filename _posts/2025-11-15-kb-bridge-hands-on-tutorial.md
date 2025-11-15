---
layout: post
title: "Hands-On: `kb-bridge` for Context-Aware Knowledge Base Search"
tags: [Software, NLP, LLM, AI, Python]
---

In the previous posts ([Part 1]({{ site.baseurl }}{% post_url 2025-10-25-context-aware-retriever-mcp %}), [Part 2]({{ site.baseurl }}{% post_url 2025-11-02-context-aware-retriever-mcp-ii %}), [Part 3]({{ site.baseurl }}{% post_url 2025-11-09-context-aware-retriever-mcp-iii %})) I showed how we built the context-aware retriever. This post covers how to use `kb-bridge`, the Python package that exposes it.

Modern RAG stacks are powerful but brittle—each new trick (GraphRAG, PageIndex, reranker cascades, etc.) helps some queries and hurts others. `kb-bridge` acts as an adapter instead of a replacement: it layers direct search, boosted queries, file-level narrowing, and answer reflection on top of whatever retriever you already run.

`kb-bridge` is an MCP adapter for the RAG stack you already run. It layers on semantic search, keyword boosting, multi-stage retrieval, and quality checks without forcing a rebuild.

> **Installation & Setup:** details live in [PyPI](https://pypi.org/project/kbbridge/) + [GitHub](https://github.com/egpivo/kb-bridge). This post stays focused on usage.

## Client Setup

This tutorial uses the FastMCP reference client for clarity, but `kb-bridge` works with any MCP-compatible client (e.g., Dify agents, custom orchestrators). Below is the minimal FastMCP wrapper used in the examples:

```python
import json
from fastmcp import Client

# Server configuration
SERVER_URL = "http://localhost:5210/mcp"
RESOURCE_ID = "your-knowledge-base-id"  # Replace with your actual KB ID

# Use Client as context manager
async with Client(SERVER_URL) as client:
    result = await client.call_tool("assistant", {"resource_id": RESOURCE_ID, "query": "..."})
    response = json.loads(result.content[0].text)
```

Let's look at each tool in action.

## Core Tools: One Example Per Tool

`kb-bridge` exposes six MCP tools (`assistant`, `file_discover`, `keyword_generator`, `retriever`, `file_lister`, `file_count`). Here's a quick look at each:

### 1. `assistant` · Q&A with answer + citations

```python
query = "Does the agreement include a non-compete clause restricting the employee from joining competitors?"

async with Client(SERVER_URL) as client:
    result = await client.call_tool(
        "assistant",
        {
            "resource_id": RESOURCE_ID,
            "query": query,
            "custom_instructions": "Extract: time periods, geographic scope, restrictions. Cite exact text.",
            "enable_query_rewriting": True,
            "enable_reflection": True,
            "reflection_threshold": 0.7,
        },
    )
    response = json.loads(result.content[0].text)
```

- Notebook run: produced a multi-bullet non-compete summary, extracted entities (time/location/condition), and cited five documents.

---

### 2. `file_discover` · shortlist candidate documents

```python
result = await client.call_tool("file_discover", {
    "query": "employment policies and termination procedures",
    "resource_id": RESOURCE_ID,
    "top_k_return": 10,
    "do_file_rerank": True
})

files = json.loads(result.content[0].text)["distinct_files"]
```

**Output:**
```
Found 20 relevant files:
  - 1628908_0001193125-15-169530_d838828dex1016.htm
  - 1084817_0001193125-14-004957_d648340dex99e2.htm
  - 1592288_0001193125-17-306543_d469659dex99e2.htm
  - 880562_0001193125-15-346821_d93800dex3.htm
  - 714562_0001104659-19-001345_a18-42231_6ex10d8.htm
  - 1177845_0001193125-18-219243_d519554dex99d3.htm
  - 792130_0001193125-18-326077_d601641dex99d3.htm
  - 703361_0001193125-12-242586_d356019dex9910.htm
  - 1485469_0001193125-19-222469_d760929dex99d3.htm
  - Kerber_Non_Disclosure_Agreement.pdf
  ...
```

---

### 3. `keyword_generator` · expand terse queries

```python
result = await client.call_tool("keyword_generator", {
    "query": "employee benefits and compensation",
    "max_sets": 3
})

keyword_sets = json.loads(result.content[0].text)["keyword_sets"]
```

**Output:**
```
Generated keyword sets:

Set 1:
  - employee benefits
  - compensation package

Set 2:
  - benefits policy
  - compensation plan

Set 3:
  - salary structure
  - employee perks

Set 4:
  - health benefits
  - retirement plan

Set 5:
  - compensation agreement
  - benefits summary
```

**When to use:** Original query is too terse or you want to capture related terminology for broader recall.

---

### 4. `retriever` · Low-Level Search Access

**Example:** Retrieve chunks about confidentiality obligations.

```python
result = await client.call_tool("retriever", {
    "resource_id": RESOURCE_ID,
    "query": "confidentiality obligations after NDA termination",
    "search_method": "hybrid_search",
    "does_rerank": True,
    "top_k": 5
})

chunks = json.loads(result.content[0].text)["result"]
```

**Output:**
```
Retrieved 10 results:

Result 1:
  Document: standard_clinical_trial_nda2.pdf
  Content preview: Version 2.1 Last Revised Date: 8/2/16 
Approved by: Last Revised By: C. Colthorp
3.3 Care. Institution shall protect Discloser's Confidential Information using not less than 
the same care it uses wi...

Result 2:
  Document: NDA_118.pdf
  Content preview: Each party will promptly advise the other in writing of any misappropriation or misuse by any person of such Confidential 
Information of which it may become aware.
4. EXCLUSIONS. Information that Re...

Result 3:
  Document: Data Use Agreement New York City.pdf
  Content preview: DOHMH Standard DUA/NDA 5-16-2014 Page 2
2. Demand assurances from the Data Recipient that remedial actions will be 
taken to remedy the circumstances that gave rise to the violation within a time 
fr...

Result 4:
  Document: NDA-ONSemi_IndustryAnalystConf-2011.pdf
  Content preview: NDA Form 1009 
5. Term and Termination. This Agreement shall terminate thirty (30) days after the effective date of this Agreement. 
Termination shall not, however, affect the rights and obligations i...

Result 5:
  Document: pp 11 - non-disclosure agreement mutual.pdf
  Content preview: Legal Office Universiti Sains Malaysia ~ PP11 Page 4
warrants as providing adequate protection on such information from 
unauthorized use or disclosure.
(f) not to reverse engineer, disassemble or d...
```

**`retriever` vs `assistant`:**
- `assistant` → Synthesized answer with citations (for end users)
- `retriever` → Raw chunks (for custom pipelines, fine-grained control)

---

### 5. `file_lister` / `file_count` · quick inventory

```python
# Count files
count_result = await client.call_tool("file_count", {"resource_id": RESOURCE_ID})
file_count = json.loads(count_result.content[0].text)["file_count"]

# List files (with pagination)
list_result = await client.call_tool("file_lister", {
    "resource_id": RESOURCE_ID,
    "limit": 20,
    "offset": 0
})
files = json.loads(list_result.content[0].text)["files"]
```

**Output:**
```
Total files: 50

Files:
  - Roundhouse-Creative-Mutual-NDA.pdf
  - annex-iii---nda-agreement..pdf
  - Aspiegel_NDA_template.pdf
  - 1094814_0001140361-18-017998_s002178x1_ex99d7.htm
  - 1110929_0001047469-00-005025_document_6.txt
  - 1123713_0001021408-00-003137_0016.txt
  - 1172317_0001193125-11-037877_dex101.htm
  - 1177845_0001193125-18-219243_d519554dex99d3.htm
  ...
```

## Complete Workflow: Information Flow Example

Here's an end-to-end example showing how all the pieces work together. This demonstrates the **full information flow** from query to final answer with quality evaluation.

**Query:** "What obligations remain in effect after the NDA expires, specifically regarding return or destruction of confidential information and survival of obligations for clinical trial data at University of Michigan?"

```python
# Using the Client from the setup section above
async with Client(SERVER_URL) as client:
        keyword_result = await client.call_tool("keyword_generator", {
            "query": query,
            "max_sets": 3
        })
        keyword_data = json.loads(keyword_result.content[0].text)
        
        file_result = await client.call_tool("file_discover", {
            "query": query,
            "resource_id": RESOURCE_ID,
            "top_k_return": 10
        })
        file_data = json.loads(file_result.content[0].text)
        files = file_data.get("distinct_files", [])
        
        answer_result = await client.call_tool("assistant", {
            "resource_id": RESOURCE_ID,
            "query": query,
            "enable_query_rewriting": True,
            "enable_reflection": True,
            "reflection_threshold": 0.7
        })
        answer_data = json.loads(answer_result.content[0].text)
```

**Example execution log (separate run, with reflection_threshold=0.5)**:
```
============================================================
🔄 Complete Workflow Example
   Reflection Threshold: 0.5
============================================================

1️⃣ Generating keywords...
   ✅ Generated 3 keyword sets

2️⃣ Discovering relevant files...
   ✅ Found 10 relevant files

3️⃣ Querying assistant with reflection...
   Server log: Content Booster: ENABLED (max_boost_keywords=1)

============================================================
📤 Final Answer
============================================================
The obligations that remain in effect after the NDA expires, specifically regarding the return or destruction of confidential information, include the following:

1. **Confidentiality Obligations**: Notwithstanding the return or destruction of the Evaluation Material and Discussion Information, the Receiving Party and its Representatives will continue to be bound by their obligations of confidentiality and other obligations under the agreement.

2. **Return or Destruction of Information**: Upon the request of the Disclosing Party, the Receiving Party is required to promptly (and in no event later than five business days after the request) deliver to the Disclosing Party or destroy all Evaluation Material and Discussion Information and provide written confirmation of destruction. However, outside counsel to the Receiving Party may retain one copy of the Evaluation Material in confidential restricted access files for use only in the event a dispute arises between the parties.

3. **Survival of Obligations**: The obligations shall survive the termination of the Agreement for any reason whatsoever. The obligations are unlimited in territory and only expire ten (10) years from the date of the Agreement or at the end of the commercial usefulness to the disclosing party for technical Information.

Upon the expiration of the Data Use Agreement, the Data Recipient is required to return or destroy the Data provided by DOHMH within 60 days of the termination of the Agreement. If returning or destroying the Data is infeasible, the Data Recipient must notify DOHMH and extend the protections of the Agreement to the Data.

*Note: There is no specific mention of obligations related to clinical trial data at the University of Michigan in the provided context.*

📚 Sources (8):
   • standard_clinical_trial_nda2.pdf
   • Data Use Agreement New York City.pdf
   • NDA_118.pdf
   • pp 11 - non-disclosure agreement mutual.pdf
   • NDA-ONSemi_IndustryAnalystConf-2011.pdf
   ...
```

### Execution Overview

<a href="{{ site.baseurl }}/assets/2025-11-15-kb-bridge-hands-on-tutorial/kb_bridge_flow.svg" target="_blank">
  <img src="{{ site.baseurl }}/assets/2025-11-15-kb-bridge-hands-on-tutorial/kb_bridge_flow.svg" 
       alt="`kb-bridge` Information Flow" 
       style="margin: 1rem 0; max-width:100%; height:auto; cursor: pointer;">
</a>

*Figure: `kb-bridge` Information Flow showing the complete workflow with real execution data (3 keyword sets, 10 files found, Content Booster enabled, quality score 0.51, 8 sources total)*

The complete workflow shows:
1. **Query expansion** via keyword generation (3 sets)
2. **File-level filtering** discovers relevant documents (10 files found)
3. **Parallel search strategies** with different approaches:
   - **Direct Search**: Runs straight from the user query across **all files** in KB (skips keyword generation + file discovery) → **1 fallback candidate**
   - **Advanced Search**: Searches only the **10 discovered files** with Content Booster enabled → **one candidate per file (7 survived scoring in this run)**
4. **Answer synthesis** prioritising higher-scoring advanced candidates (direct fallback stays available if needed)
5. **Quality evaluation** with reflection (score: 0.51, passed threshold 0.5)
6. **Structured output** with sources and confidence scores

**Key architectural insight:**
- **Direct Search** bypasses both keyword generation and file discovery, searching the entire knowledge base (simpler, broader coverage)
- **Advanced Search** uses file discovery results + Content Booster for targeted per-file search (more sophisticated, better precision)
- Candidate math: each discovered file yields at most one advanced candidate; the direct pipeline contributes at most one fallback candidate. In this run we processed 10 files, kept 7 advanced candidates, plus 1 direct fallback.
- Keeping the raw direct path matters because every rewriting/boosting step can add bias; the unmodified search guarantees at least one “as typed” retrieval path.

**Key insight from logs:**
- `Content Booster: ENABLED (max_boost_keywords=1)` — Advanced search with Content Booster contributed 7 sources vs. direct search's 1 source, demonstrating the effectiveness of the query expansion + file filtering strategy described in Part 2.

<a href="{{ site.baseurl }}/assets/2025-11-15-kb-bridge-hands-on-tutorial/kb_bridge_log_timeline.svg" target="_blank">
  <img src="{{ site.baseurl }}/assets/2025-11-15-kb-bridge-hands-on-tutorial/kb_bridge_log_timeline.svg"
       alt="`kb-bridge` Execution Timeline"
       style="margin: 1rem 0; max-width:100%; height:auto; cursor: pointer;">
</a>

*Timeline: keyword generation → file discovery → assistant call (Content Booster enabled) → reflection.*

## Integration with Dify (Quick Start)

- **MCP connection:** `http://localhost:5210/mcp` + headers (`X-RETRIEVAL-ENDPOINT`, `X-RETRIEVAL-API-KEY`, `X-LLM-API-URL`, `X-LLM-MODEL`)
- **Workflow:** Add an MCP Tool node → select `assistant` → map user input + dataset ID
- **Result:** User message → `kb-bridge` → structured answer with citations (same outputs shown above)

## Tips and Best Practices

### When to Enable Query Rewriting (and Content Booster)

In a multi-agent setup, the planner/outer LLM decides when rewriting or boosting helps. A practical playbook:

- **Use rewriting/keyword boosting** when the user question is incomplete (“termination notice period?”), grammatically broken, or heavily jargon-dependent. In practice the agent relies heavily on conversational cache and still receives fragmentary user text; the booster fabricates variant phrases so the per-file search still finds the right segments.
- **Skip rewriting** when the planner already has a clean paraphrase from history/cache, or the workflow needs exact-phrase matching / minimal latency.
- **Direct search stays on** regardless, so even if rewriting adds bias, the raw query still runs against the entire KB.

If you call `kb-bridge` manually (no planner), enable rewriting for short/ambiguous prompts and turn it off for precise requests.

### Reflection Modes

`kb-bridge` exposes reflection as two knobs today: `enable_reflection` (True/False) and `reflection_threshold` (0–1, defaults to 0.70 when omitted). Internally the server runs a “standard” quality check; more advanced modes/iterations are not user-configurable yet.

```python
# Fast queries, no quality check needed
result = await client.call_tool("assistant", {
    "resource_id": RESOURCE_ID,
    "query": "What is the company name?",
    "enable_reflection": False
})

# Standard quality check (recommended for most use cases)
result = await client.call_tool("assistant", {
    "resource_id": RESOURCE_ID,
    "query": "What are the payment terms?",
    "enable_reflection": True,
    "reflection_threshold": 0.70  # Default
})

# Stricter check for critical queries
result = await client.call_tool("assistant", {
    "resource_id": RESOURCE_ID,
    "query": "What are the liability limitations?",
    "enable_reflection": True,
    "reflection_threshold": 0.90
})
```

**Quality metrics evaluated** (per [official docs](https://pypi.org/project/kbbridge/)):
- **Completeness** (30%): Does the answer fully address the query?
- **Accuracy** (30%): Are sources relevant and correctly cited?
- **Relevance** (20%): Does the answer stay on topic?
- **Clarity** (10%): Is the answer clear and well-structured?
- **Confidence** (10%): Quality of supporting sources?

Adjust `reflection_threshold` (0-1) based on your use case (or let the outer agent decide per domain). `kb-bridge` defaults to **0.70** when you omit it:
- `0.5`: More lenient, useful for exploration
- `0.7`: Default, balanced quality bar
- `0.9`: Very strict, high-confidence answers only

**Example: Quality evaluation feedback when score is low:**

```
──────────────────────────────────────────────────────────
🔍 Reflection Analysis: Why Quality Score is Low
──────────────────────────────────────────────────────────

📊 Quality Assessment:
   Quality Score: 0.42 / 0.70
   Status: ❌ Below threshold
   Confidence: ⚠️  Low confidence - answer quality is below acceptable threshold

💡 Reflection Feedback:
   Answer lacks specific timeframes and payment amounts. Consider expanding search 
   to include related documents (invoicing_terms, billing_schedule) or using query 
   rewriting to capture payment-related terminology.

📈 Detailed Quality Scores:
   Completeness: 0.35
   Specificity: 0.48
   Citation quality: 0.65

💡 Recommendation:
   Enable query rewriting and search in document: "payment_terms_master.pdf"
```

The reflection module provides actionable feedback to improve retrieval quality.

### Tool Selection Strategy

Use the right tool for your use case:

| Tool | When to Use |
|------|-------------|
| `assistant` | End-to-end Q&A, conversational interfaces |
| `file_discover` | Large KBs, need to inspect relevant documents first |
| `keyword_generator` | Terse queries, domain terminology expansion |
| `retriever` | Custom pipelines, fine-grained control over chunks |
| `file_lister` | Browse KB contents, pagination needed |
| `file_count` | Quick health check: confirm KB ingestion status / totals |

## What's Next

`kb-bridge` is modular, so you can:
- Swap rerankers (Jina, Cohere, custom models)
- Add new search strategies (e.g., graph-based retrieval)
- Integrate custom extractors (domain-specific NER, structured data extraction)
- Wire into orchestration frameworks — `Dify` is supported today; integrations with other RAG backends/frameworks will land as we see what each ecosystem prefers.

Check out the [demo notebook](https://github.com/egpivo/kb-bridge/blob/main/examples/contract_nli_example.ipynb) for more examples, including workflow visualization and error handling.

## Resources

- **PyPI** (v0.2.1): [pypi.org/project/kbbridge](https://pypi.org/project/kbbridge/)
- **GitHub**: [github.com/egpivo/kb-bridge](https://github.com/egpivo/kb-bridge)
- **Demo Notebook**: [contract_nli_example.ipynb](https://github.com/egpivo/kb-bridge/blob/main/examples/contract_nli_example.ipynb)
- **Related Posts**: [Part 1]({{ site.baseurl }}{% post_url 2025-10-25-context-aware-retriever-mcp %}), [Part 2]({{ site.baseurl }}{% post_url 2025-11-02-context-aware-retriever-mcp-ii %}), [Part 3]({{ site.baseurl }}{% post_url 2025-11-09-context-aware-retriever-mcp-iii %})
