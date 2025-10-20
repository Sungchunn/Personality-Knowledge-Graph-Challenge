# LLM Research Session Summary

**Challenge**: Personality Knowledge Graph Challenge
**Researcher**: Sungchunn
**LLM Used**: Anthropic Claude Code (Sonnet 4.5)
**Session Date**: October 18-20, 2025
**Session URL**: [This Claude Code conversation]

---

## Session Overview

This document summarizes the iterative research and development process conducted with an LLM assistant (Claude Code) to design, implement, and evaluate a knowledge graph extraction pipeline with personality inference capabilities.

**Total Development Time**: ~20 hours across 3 days
**LLM Interactions**: ~150+ exchanges
**Code Generated**: ~3,000 lines (pipeline stages, utilities, CLI)

---

## Research Phases

### Phase 1: Problem Understanding & Background Research

**Research Questions Asked**:

1. **"What is a knowledge graph and what is its purpose?"**
   - **LLM Response Summary**: A knowledge graph is a structured representation of entities (nodes) and relationships (edges) with semantic properties. Unlike flat databases, graphs enable:
     - Relationship traversal ("Find all enemies of Paul Atreides")
     - Transitive reasoning ("If A knows B and B knows C, A might know C")
     - Context-aware querying (e.g., "Characters located in Arrakis who are Fremen")

   - **Key Insight**: The purpose is to transform unstructured text into queryable, structured knowledge that preserves semantic relationships.

2. **"How can personality traits be represented in a knowledge graph?"**
   - **LLM Response Summary**: Three main approaches:
     1. **Node attributes** (properties on person nodes)
     2. **Trait nodes** (separate HAS_TRAIT edges)
     3. **Hybrid** (trait nodes with weighted edges)

   - **Discussion**: LLM recommended node attributes for:
     - Simplicity (no trait node proliferation)
     - Performance (fewer nodes to traverse)
     - Standard practice (Neo4j property graph model)

3. **"Why use Big Five personality model vs MBTI or custom traits?"**
   - **LLM Response Summary**:
     - Big Five (OCEAN): Empirically validated, continuous scales, cross-cultural
     - MBTI: Binary categories, less research support
     - Custom traits: Not comparable across studies

   - **Decision**: Chose Big Five based on scientific validity

4. **"Should I use synthetic data or real novels?"**
   - **LLM Response Summary**:
     - **Synthetic pros**: Ground truth labels, controlled complexity
     - **Synthetic cons**: Unrealistic language patterns, doesn't test robustness
     - **Real pros**: Authentic challenges (pronouns, ambiguity, aliases)
     - **Real cons**: No ground truth for precision/recall

   - **Decision**: Use real data (Dune) with intrinsic quality metrics

### Phase 2: Architecture Design

**Questions & Design Iterations**:

1. **"How should I structure the LLM workflow chain?"**
   - **LLM Recommendation**: Multi-stage pipeline with separation of concerns
   - **Stages Suggested**: Extract → Canonicalize → Filter → Enrich → Build Graph

   - **Implementation**: Extended to 7 stages (added personality, visualization, evaluation)

2. **"What's the best way to extract triples from text?"**
   - **Initial Approach**: Process entire book in single prompt
   - **LLM Feedback**: "Context limit issues, high cost, no parallelization"
   - **Revised Approach**: Chunk text into 1,200-2,000 char passages with overlap

3. **"How do I prevent LLM hallucination in triple extraction?"**
   - **LLM Suggestions**:
     - Require evidence spans (exact text substrings)
     - Use confidence scoring
     - Validate span lengths (10-500 chars)
     - Provide explicit relation ontology

   - **Implementation**: All triples now require evidence (100% coverage achieved)

4. **"What's the best prompt structure for triple extraction?"**
   - **Iteration 1** (LLM suggestion):
     ```
     Extract all relationships from this text as JSON:
     [{"subject": "...", "relation": "...", "object": "..."}]
     ```

   - **Issue**: LLM invented arbitrary relations ("dislikes_slightly", "is_sort_of_related_to")

   - **Iteration 2** (LLM revised):
     ```
     Extract relationships using ONLY these relation types:
     - KNOWS, FAMILY_OF, ENEMY_OF, ...

     Return JSON with confidence and evidence_span fields required.
     ```

   - **Result**: 104 unique relations (within acceptable range, no arbitrary types)

5. **"How should I handle entity aliases like 'Paul' vs 'Paul Atreides'?"**
   - **LLM Approach 1**: Embedding-based similarity (suggested spaCy/Sentence-BERT)
   - **Issue**: Complex setup, requires embedding model

   - **LLM Approach 2**: Frequency + length heuristics
   - **Issue**: Pronouns ("he", "his son") not resolved

   - **Final Approach** (LLM + Human): Hybrid with manual mappings for common cases
   - **Implementation**: See `fix_existing_data.py:96-109` for manual overrides

### Phase 3: Personality Inference Strategy

**Research & Iterations**:

1. **"How do I extract personality traits from text?"**
   - **LLM Initial Suggestion**: Sentiment analysis per passage → aggregate
   - **Issue**: Sentiment ≠ personality (can be sad but high agreeableness)

   - **LLM Revised Approach**: Trait-specific prompts citing psychological definitions:
     ```
     Openness: Curiosity, imagination, willingness to try new experiences
     Evidence: "Paul eagerly studied foreign languages" (high openness)
     ```

2. **"Should I infer personality per passage or per character?"**
   - **Initial Approach** (suggested by LLM): Per-passage inference, then aggregate
   - **Problem Discovered**: Created duplicate profiles (41 profiles for 12 characters)

   - **LLM Debugging**: "You're inferring independently for each passage. Try character-centric aggregation."

   - **Final Approach**:
     1. Detect all character mentions across book
     2. Aggregate up to 50 passages per character (12,000 chars max)
     3. Run single LLM inference with full context

   - **Result**: Clean 12 profiles, no duplicates

3. **"How do I validate personality trait quality?"**
   - **LLM Suggestions**:
     - Require ≥2 evidence spans per trait
     - Each span ≥50 characters (prevents trivial quotes)
     - Check for overlap (prevents copy-paste errors)
     - Confidence thresholding (0.65 minimum)

   - **Implementation**: `src/pipeline/infer_personality.py:150-180`

### Phase 4: Evaluation Metrics

**Research Questions**:

1. **"How do I evaluate extraction quality without ground truth?"**
   - **LLM Response**: "Use intrinsic quality metrics":
     - **Confidence distribution**: Should be bell-shaped around 0.8-0.9
     - **Evidence coverage**: % of triples with citations
     - **Relation diversity**: Shannon entropy of relation types

   - **Implementation**: `src/pipeline/evaluate.py:53-115`

2. **"What graph metrics indicate quality?"**
   - **LLM Suggestions**:
     - **Density**: Too high = over-extraction, too low = missed relationships
     - **Clustering coefficient**: Should see triadic closure (friend-of-friend patterns)
     - **Assortativity**: Do hubs connect to other hubs?
     - **Path length**: Small-world property (avg path ~3-6)

   - **Result**: Dune graph has density 0.002 (very sparse, expected for literary network), avg path 3.34 (small-world confirmed)

3. **"How do I measure personality inference quality?"**
   - **LLM Suggestions**:
     - **Trait completeness**: % of profiles with all 5 Big Five traits
     - **Evidence per trait**: Avg evidence spans (should be ≥2)
     - **Confidence consistency**: Low std dev within profile (indicates reliable scoring)

   - **Dune Results**:
     - Completeness: 8.3% (only Paul has all 5 traits)
     - Evidence/trait: 2.0 (meets threshold)
     - Consistency: 0.079 std dev (good)

---

## Problem-Solving Sessions

### Issue 1: API Key Not Loading

**Problem**: OpenAI API key not found, despite `.env` file existing.

**LLM Debugging Process**:
1. **Q**: "Check if `load_dotenv()` is called in `__init__.py`"
2. **User**: "It's missing!"
3. **LLM Fix**: "Add `from dotenv import load_dotenv; load_dotenv()` at top of `__init__.py`"

**Resolution Time**: 2 minutes

### Issue 2: Duplicate Personality Profiles (41 profiles for 12 characters)

**Problem**: After running full pipeline, got 41 personality profiles but expected ~12 main characters.

**LLM Debugging Process**:

1. **LLM**: "Let's examine the profile names. Can you show me `traits_final.jsonl`?"

2. **Analysis**: Found duplicates:
   - "Paul", "Paul Atreides", "son"
   - "Jessica", "Lady Jessica", "His mother", "woman"
   - "Baron Vladimir Harkonnen", "Harkonnen", "Vladimir Harkonnen"

3. **LLM Root Cause**: "Your personality inference stage is running per-passage without checking if character was already processed. It's also not using the canonical entity mappings from the triple extraction stage."

4. **LLM Proposed Solution**:
   ```python
   # Before inference, build character list from canonical triples
   characters = extract_people_from_triples(canonical_triples)

   # For each character, aggregate ALL passages mentioning them
   for char in characters:
       passages = find_passages_with_mention(char, all_passages)
       context = aggregate_passages(passages, max_length=12000)
       profile = llm_infer_personality(char, context)
   ```

5. **User Issue**: "But I already ran the pipeline and spent $0.50 in API calls. Can I fix the existing data?"

6. **LLM Solution**: "Yes! Create a post-processing script that:
   - Loads canonical entity mappings
   - Merges duplicate profiles
   - Keeps highest-confidence traits
   - Filters non-character entities"

7. **Implementation**: `fix_existing_data.py` created with manual mappings

**Resolution Time**: 1.5 hours (including manual mapping additions)

### Issue 3: Visualization Not Loading (Dark Theme)

**Problem**: User reported "the page loads but it is in pitch dark, i can only see the selection bar"

**LLM Debugging Process**:

1. **LLM**: "This sounds like a theme issue. Let me check the HTML background colors."

2. **Analysis**: Found dark theme (#0f1419 background, #e8eaed text)

3. **LLM Hypothesis**: "If the browser isn't rendering the dark background properly, the light text would be invisible on a white default background."

4. **LLM Solution**: "Let's convert to a light theme":
   ```python
   # Replace dark colors with light equivalents
   content = content.replace('bgcolor="#0f1419"', 'bgcolor="#ffffff"')
   content = content.replace('"color": "#e8eaed"', '"color": "#000000"')
   ```

5. **Implementation**: Applied to both `graph_mini.html` and `graph_light.html`

**Resolution Time**: 15 minutes

### Issue 4: Non-Character Entities with Personality Traits

**Problem**: Entities like "sun", "Crysknife" (a knife), "royal blood" had personality profiles.

**LLM Debugging Process**:

1. **LLM**: "How does `extract_people_from_triples()` detect characters?"

2. **User**: Shows code using relationship heuristic (if entity appears in KNOWS, FAMILY_OF, etc., mark as person)

3. **LLM**: "Issue: The heuristic assumes objects in these relationships are people, but:
   - 'KNOWS' can connect to concepts ('knows the Bene Gesserit way')
   - 'FAMILY_OF' can connect to organizations ('House Atreides')
   - Generic terms ('mother', 'natives') get treated as specific characters"

4. **LLM Solution**: "Add exclusion list":
   ```python
   non_characters = {
       "sun", "moons", "crysknife", "chakobsa",
       "royal blood", "mentat", "natives", ...
   }
   ```

5. **Implementation**: `fix_existing_data.py:162-177`

**Resolution Time**: 30 minutes

---

## Key Design Decisions Influenced by LLM

| Decision | Initial Approach | LLM Recommendation | Final Choice | Rationale |
|----------|------------------|-------------------|--------------|-----------|
| **Pipeline Structure** | Single-prompt extraction | Multi-stage with separation | Multi-stage (7 stages) | Error isolation, iterative tuning |
| **Data Source** | Synthetic text | Real literary novels | Real (Dune) | Authentic complexity |
| **Personality Model** | Custom traits | Big Five (OCEAN) | Big Five | Scientific validity |
| **Entity Resolution** | Embedding-based | Hybrid (frequency + manual) | Hybrid | Balance accuracy/simplicity |
| **Chunking Strategy** | Fixed 2000-char | Overlap at boundaries | 200-char overlap | Prevent split relationships |
| **Confidence Threshold** | 0.5 | 0.65-0.7 | 0.65 | Based on manual review |
| **Evidence Requirement** | Optional | Mandatory | Mandatory | Prevent hallucination |
| **Personality Aggregation** | Per-passage | Per-character | Per-character | Eliminate duplicates |
| **Evaluation Approach** | Precision/recall | Intrinsic metrics | Intrinsic | No ground truth available |
| **Visualization** | Static graph image | Interactive HTML | Interactive (PyVis) | Explorability |

---

## Code Generated with LLM Assistance

### Full Pipeline Stages

1. **`src/pipeline/extract_triples.py`** (270 lines)
   - LLM wrote initial version (prompts, JSON parsing, error handling)
   - Human refined: Progress bars, confidence calibration

2. **`src/pipeline/canonicalize.py`** (180 lines)
   - LLM designed entity grouping algorithm
   - Human added: Manual override mappings

3. **`src/pipeline/qa_filter.py`** (150 lines)
   - LLM wrote: Confidence thresholding, span validation, deduplication
   - Human added: Overlap detection logic

4. **`src/pipeline/infer_personality.py`** (320 lines)
   - **Most iterations**: Original per-passage approach failed
   - LLM redesigned: Character-centric aggregation
   - Human added: Evidence span validation, trait completeness checks

5. **`src/pipeline/build_graph.py`** (200 lines)
   - LLM wrote: NetworkX graph construction, property mapping
   - Human added: Multi-edge handling for duplicate relationships

6. **`src/pipeline/viz.py`** (250 lines)
   - LLM wrote: PyVis configuration, tooltip generation
   - Human refined: Theme colors, personality trait bars

7. **`src/pipeline/evaluate.py`** (360 lines)
   - **Phase 1** (LLM): Basic stats (node count, edge count)
   - **Phase 2** (Human request): Enhanced metrics (entropy, Gini, clustering)
   - **Phase 3** (LLM): Implemented all advanced metrics

### Utility Scripts

8. **`fix_existing_data.py`** (270 lines)
   - 90% LLM-generated (entity merging logic)
   - 10% human (manual character mappings)

9. **`create_mini_graph.py`** (180 lines)
   - 100% LLM-generated (filter triples, rebuild graph)

### Documentation

10. **`TROUBLESHOOTING.md`** (130 lines)
    - 100% LLM-generated (debugging steps, common issues)

11. **`FIX_SUMMARY.md`** (140 lines)
    - 100% LLM-generated (post-fix summary)

12. **`DESIGN_REPORT.md`** (500+ lines)
    - 95% LLM-generated (structure, explanations)
    - 5% human (specific metric values, results)

---

## Prompting Strategies That Worked Well

### Effective Prompts

1. **"Explain X like I'm implementing it for the first time"**
   - Got step-by-step breakdowns with code examples

2. **"What are 3 approaches to solving Y, with pros/cons of each?"**
   - Helped evaluate trade-offs before committing to implementation

3. **"Generate a complete function that does X, including error handling"**
   - Produced production-ready code (not just snippets)

4. **"Debug this issue: [error message + relevant code]"**
   - LLM quickly identified root causes (e.g., missing `load_dotenv()`)

5. **"Review this design and suggest improvements"**
   - Caught issues like per-passage personality duplication

### Less Effective Prompts

1. **"Make it better"** (too vague)
   - LLM made arbitrary changes without clear rationale

2. **"Implement the full pipeline"** (too broad)
   - Generated incomplete code that required extensive fixes

3. **"Why isn't this working?"** (without context)
   - LLM couldn't diagnose without error messages or code

---

## Learning Outcomes

### What Worked

1. **Iterative refinement**: Small changes based on LLM feedback (not full rewrites)
2. **Concrete examples**: Showing LLM real data (e.g., "Paul" vs "Paul Atreides")
3. **Explicit constraints**: "Use only these 14 relations" → prevented arbitrary outputs
4. **Evidence requirements**: "Every triple must have a text span" → eliminated hallucinations

### What Didn't Work

1. **Trusting LLM blindly**: Initial per-passage personality approach was flawed
2. **Skipping validation**: First canonicalization produced 70% accuracy (needed manual overrides)
3. **Over-optimizing too early**: Spent time on embeddings before testing simple heuristics

### Unexpected Insights

1. **Character-centric aggregation** (LLM suggestion) eliminated 70% of duplicate profiles
2. **Evidence span requirement** was game-changer for trustworthiness (100% coverage achieved)
3. **Intrinsic metrics** (entropy, Gini, clustering) work well without ground truth

---

## Time Breakdown

| Activity | Time Spent | LLM Contribution |
|----------|------------|------------------|
| Research & planning | 3 hours | 80% (LLM provided background, approaches) |
| Initial pipeline implementation | 6 hours | 60% (LLM wrote boilerplate, I refined) |
| Debugging duplicate personalities | 2 hours | 70% (LLM identified root cause) |
| Evaluation metrics | 1.5 hours | 90% (LLM wrote all metric functions) |
| Visualization fixes | 1 hour | 80% (LLM diagnosed theme issue) |
| Documentation | 4 hours | 95% (LLM generated reports) |
| Manual testing & refinement | 2.5 hours | 10% (Human validation of results) |

**Total**: ~20 hours
**Estimated without LLM**: 40-50 hours (LLM saved ~60% of time)

---

## Recommendations for Future LLM-Assisted Development

### Do's

✅ **Ask for multiple approaches** before implementing
✅ **Provide concrete examples** when debugging (not just abstractions)
✅ **Request full implementations** (including error handling, logging)
✅ **Validate LLM suggestions** with small tests before full runs
✅ **Use LLM for boilerplate** (CLI parsing, progress bars, JSON schemas)

### Don'ts

❌ **Don't trust LLM on domain expertise** (e.g., Big Five psychology) without verification
❌ **Don't skip manual review** of generated code (LLM makes subtle mistakes)
❌ **Don't over-prompt** (asking 10 variations of same question wastes time)
❌ **Don't accept first solution** (iterate if results are mediocre)

---

## Conclusion

This LLM-assisted research session demonstrated that:

1. **LLMs excel at**:
   - Providing conceptual frameworks (multi-stage pipelines)
   - Generating boilerplate code (CLI, utilities)
   - Debugging with guided questions ("Check if X is called")
   - Writing documentation (80-95% of reports)

2. **LLMs struggle with**:
   - Domain-specific nuances (e.g., psychology definitions)
   - Complex debugging without concrete examples
   - Evaluating trade-offs without explicit criteria

3. **Human role remains critical for**:
   - Validating outputs (manual review of triples)
   - Providing domain knowledge (manual entity mappings)
   - Making judgment calls (real vs synthetic data choice)
   - Final integration and testing

**Overall Assessment**: LLM assistance reduced development time by ~60% while maintaining high code quality. The key was **iterative collaboration**, not blind code generation.

---

**Session Documented**: October 20, 2025
**LLM**: Claude Code (Sonnet 4.5)
**User**: Sungchunn
