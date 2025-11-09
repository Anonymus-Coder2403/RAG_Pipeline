# RAG Performance Test Questions

Test your RAG system with these questions across different difficulty levels. Upload a document (PDF) and try these questions to evaluate performance.

## 📊 Difficulty Level 1: Direct Fact Retrieval (Easy)
**Tests:** Basic keyword matching and simple semantic similarity

### Sample Questions:
1. **What is [specific term/concept] mentioned in the document?**
2. **Who is the author/creator of [something]?**
3. **When did [event] happen?**
4. **What is the definition of [key term]?**
5. **List the main topics covered in this document.**

**Expected:** High accuracy (>90%). These test if your system can retrieve exact information.

---

## 📊 Difficulty Level 2: Semantic Understanding (Medium)
**Tests:** Understanding synonyms, paraphrasing, and conceptual relationships

### Sample Questions:
1. **How does [concept A] relate to [concept B]?**
   - Tests: Understanding relationships between concepts
2. **What are the advantages/benefits of [approach]?**
   - Tests: Extracting implied positive aspects
3. **Explain [concept] in simple terms.**
   - Tests: Ability to find detailed explanations
4. **What is the purpose/goal of [process/system]?**
   - Tests: Understanding intent and objectives
5. **Compare [item A] with [item B].**
   - Tests: Multi-document retrieval and synthesis

**Expected:** Good accuracy (70-85%). Tests semantic understanding beyond keywords.

---

## 📊 Difficulty Level 3: Multi-Hop Reasoning (Hard)
**Tests:** Connecting information across multiple sections/chunks

### Sample Questions:
1. **Based on [concept A] discussed earlier, what implications does this have for [concept B] mentioned later?**
2. **How did [factor X] contribute to [outcome Y], considering the context of [condition Z]?**
3. **What is the relationship between [entity A], [entity B], and [entity C]?**
4. **Given [situation], what would be the expected result according to the document?**
5. **Why does the document recommend [approach A] for [scenario X] but [approach B] for [scenario Y]?**

**Expected:** Moderate accuracy (50-70%). Requires retrieving and synthesizing multiple chunks.

---

## 📊 Difficulty Level 4: Inference & Implicit Information (Very Hard)
**Tests:** Understanding implicit relationships and unstated conclusions

### Sample Questions:
1. **What can we infer about [topic] based on the discussion of [related topic]?**
2. **What are the potential limitations of [approach] not explicitly mentioned?**
3. **How might [concept] apply to [novel scenario not in document]?**
4. **What assumptions underlie the argument about [topic]?**
5. **What would happen if [condition] changed, based on the principles described?**

**Expected:** Lower accuracy (30-50%). Tests deep understanding and reasoning.

---

## 📊 Difficulty Level 5: Edge Cases & Adversarial (Expert)
**Tests:** System robustness and failure modes

### Sample Questions:
1. **What does the document say about [topic that doesn't exist in document]?**
   - Expected: System should say "not found" rather than hallucinate
2. **Are there any contradictions between [section A] and [section B]?**
   - Tests: Detecting inconsistencies
3. **What is NOT mentioned about [topic]?**
   - Tests: Handling negation queries
4. **Summarize the most important points in order of significance.**
   - Tests: Ranking and prioritization
5. **What questions does this document leave unanswered about [topic]?**
   - Tests: Identifying gaps

**Expected:** Variable accuracy. Tests system reliability and edge cases.

---

## 🎯 Evaluation Metrics

For each question, evaluate:

### 1. **Retrieval Quality** (Check the "Sources" in your UI)
- Are the retrieved chunks relevant?
- Do they contain the information needed to answer?
- Is the top result the most relevant?

### 2. **Answer Quality**
- **Correctness:** Is the answer factually accurate?
- **Completeness:** Does it fully address the question?
- **Groundedness:** Is it based on the document or hallucinated?
- **Clarity:** Is the answer well-structured and clear?

### 3. **Source Attribution**
- Are sources properly cited?
- Can you verify the answer by reading the sources?

---

## 📝 Example Test Document

If you need a test document, try these types:

1. **Technical Paper:** Tests understanding of complex concepts
2. **Business Report:** Tests extraction of metrics and conclusions
3. **Legal Document:** Tests precision and detail handling
4. **Educational Material:** Tests explanation quality
5. **News Article:** Tests factual extraction and context

---

## 🔬 Advanced Testing

### Test Scenarios by Document Type:

#### For Technical Documentation:
- "What are the system requirements?"
- "How do I troubleshoot [error]?"
- "What is the difference between [version A] and [version B]?"

#### For Research Papers:
- "What methodology was used in this study?"
- "What were the main findings?"
- "What are the limitations of this research?"

#### For Business Documents:
- "What was the revenue for Q1?"
- "What are the key risks mentioned?"
- "What are the strategic priorities?"

---

## 💡 Tips for Testing

1. **Start Simple:** Begin with Level 1 questions to verify basic functionality
2. **Check Sources:** Always review the retrieved sources to understand retrieval quality
3. **Test Edge Cases:** Try questions about non-existent topics to test hallucination handling
4. **Compare Answers:** Try the same question multiple times to check consistency
5. **Vary Phrasing:** Ask the same question in different ways to test semantic understanding

---

## 🎓 Embedding Model Performance Expectations

**BAAI/bge-large-en-v1.5** (your current model):
- ✅ Excellent: Semantic similarity, cross-lingual understanding
- ✅ Very Good: Paraphrase detection, concept relationships
- ✅ Good: Multi-hop reasoning (with good chunk size)
- ⚠️ Moderate: Negation handling, implicit inference
- ⚠️ Challenging: Absence detection ("what is NOT mentioned")

---

## 📊 Quick Performance Benchmark

Use this scorecard:

| Difficulty | Questions Tested | Correct | Score |
|------------|------------------|---------|-------|
| Level 1    | 5               |         | /5    |
| Level 2    | 5               |         | /5    |
| Level 3    | 5               |         | /5    |
| Level 4    | 5               |         | /5    |
| Level 5    | 5               |         | /5    |
| **Total**  | **25**          |         | **/25** |

**Interpretation:**
- 20-25: Excellent RAG system
- 15-19: Good performance, minor improvements needed
- 10-14: Moderate, needs optimization (chunk size, top-k, prompt tuning)
- <10: Needs significant improvements

---

## 🔧 If Performance is Low

1. **Adjust Chunk Size:** Smaller chunks (500-700) for precise facts, larger (1000-1500) for context
2. **Increase TOP_K:** Try 5-10 instead of 3 for more context
3. **Improve Prompts:** Add more specific instructions to the LLM
4. **Document Quality:** Ensure PDFs are text-based, not scanned images
5. **Model Temperature:** Lower (0.0-0.1) for factual, higher (0.3-0.5) for creative

---

**Happy Testing! 🚀**
