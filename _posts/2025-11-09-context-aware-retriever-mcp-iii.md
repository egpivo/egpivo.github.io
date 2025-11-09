---
layout: post
title: "How I'm Building a Context-Aware Retriever to Boost RAG Quality (Part 3: Evaluation)"
tags: [Software, NLP, LLM, AI]
math: true
---

In [Part 1]({{ site.baseurl }}{% post_url 2025-10-25-context-aware-retriever-mcp %}) and [Part 2]({{ site.baseurl }}{% post_url 2025-11-02-context-aware-retriever-mcp-ii %}), I walked through the design and implementation. Now let's evaluate how well it performs on the [`ContractNLI`](https://stanfordnlp.github.io/contract-nli) dataset and see if the added complexity pays off. Figure 1 shows the components I used in the evaluation experiment.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-11-09-context-aware-retriever-mcp-iii/eval_workflow.dot.svg" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-11-09-context-aware-retriever-mcp-iii/eval_workflow.dot.svg" alt="Evaluation workflow overview" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 1. Evaluation workflow overview.</div>
</div>


## Evaluation Approach

I used a simple **entity‑based** check inspired by NER. For each question I define the ground‑truth entities (with acceptable variants) and then check whether the answer includes them. I score with precision/recall. The whole flow can be depicted as

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-11-09-context-aware-retriever-mcp-iii/eval_flow.dot.svg" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-11-09-context-aware-retriever-mcp-iii/eval_flow.dot.svg" alt="Entity extraction flow" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 2. Entity extraction flow.</div>
</div>



### Entity Types

Each ground‑truth answer is annotated with these types: **TIME**, **MONEY**, **LOCATION**, **ORGANIZATION**, **CONDITION**, **ACTION**, **PERCENTAGE**.

For each query, I also marked **critical entity types** the classes essential to answering that question. For example, termination questions typically treat TIME as critical because the notice period is decisive.

### Answer Quality Metrics

For each generated answer, I:
1. **Extract entities** from the answer text using fuzzy matching against ground‑truth variants
2. **Compute**:
   - **Entity Precision**: Proportion of extracted entities that match ground‑truth
   - **Entity Recall**: Proportion of ground‑truth entities found in the answer
   - **Entity F1**: Harmonic mean of precision and recall

This measures not only plausibility, but whether the answer captures the *exact* critical details (durations, conditions, parties) that matter in legal and compliance settings.

Dataset and cases: 20 ContractNLI test cases (with annotations) (see the [Gist](https://gist.github.com/egpivo/1158d9a9ed17963423c36a48e701a178)). Each case has a query, clause, source file, entity annotations, and critical types.

**Sample Case**:
```json
{
  "query": "Does the agreement include a non-compete clause restricting the employee from joining competitors?",
  "entities": {
    "TIME": [
      "12 months",
      "following termination",
      "after termination"
    ],
    "LOCATION": [
      "50 miles"
    ],
    "CONDITION": [
      "non-compete",
      "not engage in any business that competes"
    ]
  }
}
```

### Entity Extraction (DSPy + GPT‑4o)

I extract entities from answers with a small DSPy module backed by GPT‑4o at temperature 0. The LLM returns a structured JSON object keyed by entity type. I then compare the extracted strings against ground‑truth variants to compute precision and recall.

```python
STANDARD_ENTITY_TYPES = [
    "TIME", "MONEY", "LOCATION", "ORGANIZATION", "CONDITION", "ACTION", "PERCENTAGE",
]

class EntityExtractionSignature(dspy.Signature):
    answer_text: str = dspy.InputField(desc="Answer text to extract entities from")
    entity_types: str = dspy.InputField(
        desc=(
            "Comma-separated list of entity types to extract. "
            f"Standard types: {', '.join(STANDARD_ENTITY_TYPES)}"
        )
    )

    extracted_entities: str = dspy.OutputField(
        desc=(
            "Return a valid JSON object where keys are entity types and values are arrays of exact spans. "
            'Example: {"TIME": ["12 months", "30 days"], "MONEY": ["$150 per hour"], "LOCATION": ["50-mile radius"], '
            '"CONDITION": [], "ACTION": [], "ORGANIZATION": [], "PERCENTAGE": []}'
        )
    )
```

Then wire it up with a tiny extractor that takes a pre‑configured DSPy LM and returns the JSON string (parse upstream as needed). For a fuller version with retries/validation, see the [Gist](https://gist.github.com/egpivo/167cfaac6ccbfcc391cbd7a0597319bf)

```python
class LLMEntityExtractor:
    def __init__(self, lm):
        self._lm = lm
        self.extractor = dspy.ChainOfThought(EntityExtractionSignature)

    def extract(self, answer_text, types=STANDARD_ENTITY_TYPES):
        with dspy.settings.context(lm=self._lm):
            out = self.extractor(
                answer_text=answer_text,
                entity_types=", ".join(types),
            )
        return out.extracted_entities  # JSON string like {"TIME": [...], ...}
```




## Comparison

### Experimental Setups

Shared: GPT‑4o (temp 0, non‑reasoning), Jina reranker‑v2 (top‑k 50), ContractNLI.

| Attribute | Standard Dify | Context‑Aware Agent |
|---|---|---|
| Retrieval | Single‑pass | Multi‑stage (agent) |
| Query expansion | No | Yes |
| File discovery | No | Yes |
| Reflection | No | Yes |
| Orchestration | None | Agent (function calling) |

#### Workflows (Dify):
Two workflows compared side‑by‑side in the experiments:
- Standard Dify: single‑pass semantic search with Jina rerank; GPT‑4o summarizes
- Context‑Aware: GPT‑4o agent orchestrates multi‑stage retrieval with query expansion and reflection

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-11-09-context-aware-retriever-mcp-iii/base_workflow.png" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-11-09-context-aware-retriever-mcp-iii/base_workflow.png" alt="Standard Dify workflow" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 3. Standard Dify: single‑pass semantic search with Jina rerank; GPT‑4o summarization.</div>
</div>

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-11-09-context-aware-retriever-mcp-iii/context_aware_workflow.png" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-11-09-context-aware-retriever-mcp-iii/context_aware_workflow.png" alt="Context‑Aware workflow" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 4. Context‑Aware: GPT‑4o agent orchestrates MCP service: multi‑stage retrieval with query expansion and reflection.</div>
</div>

### Results
#### Overall Performance
Micro-averaged across test cases:

| Metric | Context-Aware | Baseline Dify | **Improvement** |
|--------|---------------|---------------|-----------------|
| **Precision** | **85.00%** | 45.00% | **+40.00%** (+88.9%) |
| **Recall** | **42.49%** | 18.58% | **+23.91%** (+128.7%) |
| **F1 Score** | **54.14%** | 25.18% | **+28.96%** (+115.0%) |

#### Example: [`test_006`](https://gist.github.com/egpivo/1158d9a9ed17963423c36a48e701a178#file-contractnli_test_cases-json-L130)

**Query**: "Is there a confidentiality obligation that survives contract termination?"

**Ground Truth Entities**:
- **TIME**: 5 years, from the date of disclosure
- **CONDITION**: termination, expiration, confidential
- **Total**: 5 entities (Critical types: TIME, CONDITION)

| Baseline | Context-Aware |
|----------|---------------|
| **Answer**: Yes, confidentiality obligations often survive the termination of a contract. Many contracts include specific clauses that state confidentiality obligations will continue even after the contract has ended. The specific duration and terms can vary depending on the contract language and applicable laws. | **Answer**: Yes, confidentiality obligations often survive the termination of a contract. Here are some examples:<br><br>1. Confidentiality obligations with respect to trade secrets survive termination in perpetuity.<br>2. All obligations of confidentiality shall survive the termination of the Agreement.<br>3. The obligations of confidentiality set forth in this Agreement shall survive termination or expiration of this Agreement and shall continue for a period of five (5) years from the date of disclosure of the Confidential Information, or for such longer period as may be required by applicable law. |
| **Entities Found**: 2/5<br>✅ termination<br>✅ confidential | **Entities Found**: 5/5<br>✅ 5 years<br>✅ from the date of disclosure<br>✅ termination<br>✅ expiration<br>✅ confidential |


**Key Observation**: The baseline gives a generic answer without specific details. The context-aware approach retrieves multiple examples and includes the exact ground truth clause with all critical entities (5 years, date of disclosure, termination, expiration).

## Conclusion

The context-aware setup doubles the baseline's performance by using multi-stage retrieval, query expansion, and reflection. The nice part: it's modular, so I can swap out components, i.e., try different rerankers, add new retrieval strategies, or improve the extractor, without rebuilding everything. It costs more in retrieval calls and latency, but for domains where getting the facts right matters (legal, compliance, technical docs), having a system I can keep improving makes the trade-off worth it.

