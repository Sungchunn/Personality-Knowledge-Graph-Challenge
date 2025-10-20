# Synthetic Data Generation Analysis

**Author**: Sungchunn
**Date**: October 20, 2025
**Context**: Personality Knowledge Graph Challenge

---

## Executive Summary

This document addresses the challenge requirement to justify synthetic data generation approaches. While **real data (Dune novel) was chosen for the main implementation**, this analysis demonstrates:

1. **How** synthetic data COULD be generated with ground truth labels
2. **Why** real data was ultimately chosen despite this capability
3. **When** synthetic data would be preferable
4. **How** to evaluate with synthetic vs. real data

---

## 1. Synthetic Data Generation Approach

### 1.1 Template-Based Generation

**Implementation**: `src/pipeline/generate_synthetic.py`

**Method**: Pre-defined character templates + sentence templates → narrative passages

```python
# Example: 5 characters with ground truth personalities
SYNTHETIC_CHARACTERS = {
    "Princess Elena": {
        "personality": {"openness": 0.85, "conscientiousness": 0.70, ...},
        "traits": ["curious", "imaginative", "diplomatic"]
    },
    "Sir Marcus": {
        "personality": {"openness": 0.45, "conscientiousness": 0.90, ...},
        "traits": ["disciplined", "loyal", "brave"]
    },
    ...
}

# Predefined relationships (ground truth)
GROUND_TRUTH_RELATIONSHIPS = [
    ("Princess Elena", "FAMILY_OF", "King Aldwin"),
    ("Sir Marcus", "SERVES", "Princess Elena"),
    ("Sir Marcus", "ENEMY_OF", "General Thorne"),
    ...
]
```

**Generated Output**:
- **synthetic_passages.jsonl**: 50 passages (800-1,500 chars each) for pipeline input
- **ground_truth.json**: Known triples and personalities for evaluation
- **synthetic_metadata.json**: Generation parameters

---

### 1.2 Generation Process

#### Step 1: Character Definition
```python
{
    "character_name": "Princess Elena",
    "ground_truth_personality": {
        "openness": 0.85,       # High: curious, imaginative
        "conscientiousness": 0.70,  # Moderate-high: organized
        "extraversion": 0.60,       # Moderate: balanced social
        "agreeableness": 0.75,      # High: compassionate
        "neuroticism": 0.40         # Low: emotionally stable
    }
}
```

#### Step 2: Relationship Templates
```python
SENTENCE_TEMPLATES = {
    "SERVES": [
        "{subj} pledged loyalty to {obj}, serving with dedication.",
        "Day and night, {subj} stood ready to serve {obj}."
    ],
    "ENEMY_OF": [
        "{subj} despised {obj}, their enmity known throughout the land.",
        "Conflict between {subj} and {obj} was inevitable."
    ]
}
```

#### Step 3: Personality Templates
```python
TRAIT_TEMPLATES = {
    "openness": {
        "high": [
            "{char} eagerly explored new ideas, seeking knowledge.",
            "Curiosity drove {char} to question everything."
        ],
        "low": [
            "{char} preferred tradition, uncomfortable with change."
        ]
    }
}
```

#### Step 4: Passage Assembly
```python
def generate_passage():
    # 1. Select 2-4 relationships
    # 2. Select 2-3 characters
    # 3. Generate relationship sentences
    # 4. Generate personality demonstration sentences
    # 5. Combine into 800-1,500 char passage
    # 6. Store ground truth separately
```

**Sample Generated Passage**:
```
In the Kingdom of Light, events unfolded that would change everything.
Princess Elena had known Sir Marcus for many years, their paths crossing
often. Sir Marcus pledged loyalty to Princess Elena, serving with unwavering
dedication. Princess Elena eagerly explored new ideas, always seeking
knowledge beyond the familiar. Sir Marcus meticulously planned every detail,
leaving nothing to chance. Princess Elena showed compassion to all, always
seeking harmony over conflict...
```

---

### 1.3 Evaluation with Synthetic Data

**Advantage**: Can compute precision/recall with ground truth

```python
# Ground truth
gt_triples = [
    ("Princess Elena", "KNOWS", "Sir Marcus"),
    ("Sir Marcus", "SERVES", "Princess Elena")
]

gt_personalities = {
    "Princess Elena": {"openness": 0.85, "agreeableness": 0.75, ...}
}

# Pipeline predictions
pred_triples = pipeline.extract_triples(passage)
pred_personalities = pipeline.infer_personality(passage)

# Compute metrics
precision = len(pred ∩ gt) / len(pred)
recall = len(pred ∩ gt) / len(gt)
f1_score = 2 * (precision * recall) / (precision + recall)

# Personality MAE (Mean Absolute Error)
mae = mean(|pred_score - gt_score|) for all traits
```

**Example Results** (hypothetical):
```
Triple Extraction:
  Precision: 0.82 (82% of extracted triples are correct)
  Recall: 0.74 (74% of ground truth triples found)
  F1-Score: 0.78

Personality Inference:
  Openness MAE: 0.12 (off by 0.12 on 0-1 scale)
  Overall MAE: 0.15 (average error across all traits)
```

---

## 2. Why Real Data Was Chosen Over Synthetic

### 2.1 Limitations of Synthetic Data

| Issue | Impact | Example |
|-------|--------|---------|
| **Unrealistic language patterns** | Doesn't test robustness to natural text | "Princess Elena eagerly explored..." is artificial |
| **No ambiguity** | Misses pronoun resolution challenges | No "he/she" requiring context |
| **Predictable structure** | Pipeline could overfit to templates | All SERVES relations use same sentence form |
| **Limited complexity** | Doesn't test edge cases | No sarcasm, metaphor, indirect references |
| **Ground truth bias** | Temptation to tune for known answers | Risk of overfitting to synthetic patterns |

### 2.2 Advantages of Real Data (Dune)

| Advantage | Benefit | Evidence |
|-----------|---------|----------|
| **Authentic complexity** | Tests pronoun resolution, aliases | "Paul" vs "his son" vs "the boy" |
| **Rich relationships** | 104 unique relation types | Beyond template-defined relations |
| **Nuanced personalities** | Traits emerge from context | Baron Harkonnen: low agreeableness from actions, not labels |
| **Edge cases** | Metaphorical language, sarcasm | "Paul IS the desert" (metaphor, not location) |
| **Realistic deployment** | Prepares for production use | Real books have these challenges |

---

### 2.3 Comparison: Synthetic vs. Real Data

**Scenario**: Extract knowledge graph from 50 passages

| Metric | Synthetic Data | Real Data (Dune) |
|--------|----------------|------------------|
| **Precision** (calculable) | ✅ Yes (vs ground truth) | ❌ No (no labels) |
| **Recall** (calculable) | ✅ Yes (vs ground truth) | ❌ No (no labels) |
| **Robustness to ambiguity** | ❌ Low (templates clear) | ✅ High (real pronouns) |
| **Entity resolution testing** | ❌ Weak (names consistent) | ✅ Strong (many aliases) |
| **Generalization to real text** | ❌ Unknown | ✅ Direct test |
| **Development cost** | 💰 Low (templates) | 💰💰 High (API calls) |

**Conclusion**: Real data sacrifices precision/recall metrics but gains robustness testing.

---

## 3. Hybrid Approach (Recommended for Production)

### 3.1 Phase 1: Synthetic Data for Initial Development

**Use synthetic data to**:
1. Validate pipeline architecture (extract → canonicalize → infer → build)
2. Tune confidence thresholds (e.g., what threshold gives best F1?)
3. Debug prompts (does LLM extract known relationships?)
4. Establish baseline metrics

**Example Workflow**:
```bash
# 1. Generate synthetic data
python -m src.pipeline.generate_synthetic --output-dir data/synthetic --num-passages 50

# 2. Run pipeline on synthetic
python -m src.pipeline.cli --input-file data/synthetic/synthetic_passages.jsonl all

# 3. Evaluate against ground truth
python -m src.pipeline.evaluate_synthetic \
  --predictions outputs/synthetic_run/ \
  --ground-truth data/synthetic/ground_truth.json

# Output:
#   Triple Extraction: P=0.82, R=0.74, F1=0.78
#   Personality MAE: 0.15
```

### 3.2 Phase 2: Real Data for Robustness Testing

**Use real data to**:
1. Test pronoun resolution
2. Validate entity canonicalization
3. Assess handling of ambiguous relationships
4. Verify production readiness

**Example Workflow**:
```bash
# Run pipeline on Dune
python -m src.pipeline.cli --input-file data/jsonl/dune.jsonl all

# Evaluate with intrinsic metrics (no ground truth)
#   - Evidence coverage: 100%
#   - Confidence calibration: std dev 0.059
#   - Relation diversity: entropy 0.604
```

### 3.3 Phase 3: Manual Annotation for Validation

**Create small labeled dataset**:
1. Select 100 random passages from real data
2. Manually annotate ground truth triples and personalities
3. Compute precision/recall on this subset

**Effort**: ~20 hours of manual work
**Benefit**: Precision/recall on realistic data

---

## 4. When to Use Each Approach

### Use Synthetic Data When:

1. **Early development** - Need quick validation of pipeline logic
2. **Hyperparameter tuning** - Want to optimize confidence thresholds with known answers
3. **Debugging** - Isolate whether issues are in code vs. data complexity
4. **Teaching/demos** - Need simple, explainable examples
5. **Baseline metrics** - Establish upper bound on performance

### Use Real Data When:

1. **Production readiness** - Need to test on authentic complexity
2. **Robustness testing** - Want to find edge cases and failure modes
3. **Generalization** - Verify system works beyond training distribution
4. **User acceptance** - Demonstrate on actual use case (literary analysis)
5. **Research publication** - Realistic evaluation for peer review

---

## 5. Implementation: Running Synthetic Data Pipeline

### 5.1 Generate Synthetic Data

```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"

# Generate 50 passages with ground truth
python -m src.pipeline.generate_synthetic

# Output:
#   data/synthetic/synthetic_passages.jsonl  # Pipeline input
#   data/synthetic/ground_truth.json         # Evaluation labels
#   data/synthetic/synthetic_metadata.json   # Generation params
```

### 5.2 Run Pipeline on Synthetic Data

```bash
# Process synthetic passages
python -m src.pipeline.cli \
  --input-file data/synthetic/synthetic_passages.jsonl \
  --output-root outputs/synthetic_run \
  all
```

### 5.3 Evaluate Against Ground Truth

```python
# Example evaluation script (to be implemented)
import json
from src.pipeline.io_utils import load_jsonl

# Load predictions
pred_triples = load_jsonl("outputs/synthetic_run/triples_canonical.jsonl")
pred_traits = load_jsonl("outputs/synthetic_run/traits_final.jsonl")

# Load ground truth
with open("data/synthetic/ground_truth.json") as f:
    gt = json.load(f)

# Compute triple metrics
tp = 0  # True positives
fp = 0  # False positives
fn = 0  # False negatives

for pred in pred_triples:
    pred_tuple = (pred["subject"], pred["relation"], pred["object"])
    if pred_tuple in gt["relationships"]:
        tp += 1
    else:
        fp += 1

fn = len(gt["relationships"]) - tp

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"Triple Extraction:")
print(f"  Precision: {precision:.3f}")
print(f"  Recall: {recall:.3f}")
print(f"  F1-Score: {f1:.3f}")

# Compute personality MAE
mae_per_trait = {}
for pred_profile in pred_traits:
    char = pred_profile["person_name"]
    if char in gt["characters"]:
        gt_personality = gt["characters"][char]["personality"]
        for trait in pred_profile["traits"]:
            trait_name = trait["trait_name"]
            if trait_name in gt_personality:
                error = abs(trait["score"] - gt_personality[trait_name])
                if trait_name not in mae_per_trait:
                    mae_per_trait[trait_name] = []
                mae_per_trait[trait_name].append(error)

print(f"\nPersonality Inference (MAE):")
for trait_name, errors in mae_per_trait.items():
    print(f"  {trait_name}: {sum(errors)/len(errors):.3f}")
```

---

## 6. Justification Summary

### Challenge Question: "How and what synthetic data to generate?"

**Answer**:

1. **How to generate**: Template-based approach with:
   - Predefined characters (5 with ground truth personalities)
   - Relationship templates (12 ground truth triples)
   - Sentence templates for each relation type (SERVES, ENEMY_OF, etc.)
   - Personality demonstration templates (high/low openness, etc.)
   - Random assembly into 800-1,500 char passages

2. **What data**: 50 synthetic passages featuring fantasy novel scenario (Kingdom of Light)
   - 5 characters: Princess Elena, Sir Marcus, Wizard Aldric, General Thorne, Lady Aria
   - 12 relationships: FAMILY_OF, KNOWS, SERVES, ENEMY_OF, MENTORS, LEADS, etc.
   - Ground truth personalities: Big Five scores (0-1) for each character
   - Output format: Same JSONL as real data pipeline

3. **Why real data was ultimately chosen**:
   - Synthetic data can't test pronoun resolution ("he" → "Paul Atreides")
   - Synthetic data can't test entity canonicalization robustness
   - Synthetic data has predictable patterns (overfitting risk)
   - Real data better demonstrates production readiness
   - Intrinsic metrics (evidence coverage, confidence calibration) sufficient without ground truth

4. **When synthetic would be preferable**:
   - Early development phase (validate architecture)
   - Hyperparameter tuning (optimize thresholds)
   - Debugging (isolate code vs. data issues)
   - Baseline establishment (upper bound on performance)

---

## 7. Conclusion

**The project demonstrates understanding of BOTH approaches**:

✅ **Synthetic data generation** - Implemented in `generate_synthetic.py`
✅ **Real data processing** - Used for main evaluation (Dune)
✅ **Justification** - Documented why real data chosen despite synthetic capability
✅ **Hybrid approach** - Recommended for production systems

**Key Insight**: Synthetic data is valuable for **controlled evaluation**, but real data is essential for **robustness testing**. The ideal approach uses both: synthetic for development, real for validation.

---

**Document Created**: October 20, 2025
**Author**: Sungchunn
**Related Files**:
- `src/pipeline/generate_synthetic.py` - Synthetic data generator
- `DESIGN_REPORT.md` Section 2.2 - Real vs synthetic justification
- `data/synthetic/` - Generated synthetic dataset (if created)
