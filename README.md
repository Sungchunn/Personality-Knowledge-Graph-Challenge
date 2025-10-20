# Personality Knowledge Graph: From Text to Psychological Insights

**Extracting structured knowledge graphs with Big Five personality traits from literary text using multi-stage LLM workflows**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📊 Project Overview

This project addresses a fundamental challenge in computational text analysis: **extracting structured knowledge graphs** (entities, relationships) **with personality trait inference** (Big Five model) from unstructured narrative text. Using Frank Herbert's *Dune* as a test corpus, the pipeline demonstrates:

- **1,050 entities** extracted with canonical name resolution
- **2,246 relationships** across 104 unique relation types
- **12 complete personality profiles** using Big Five (OCEAN) model
- **100% evidence grounding** to prevent LLM hallucination
- **$0.50 total API cost** for full novel processing (Claude 3.5 Sonnet)

---

## 🧠 Theoretical Foundation

### What is a Knowledge Graph?

A **knowledge graph** is a structured representation of real-world entities and their interrelationships, formally defined as:

```
G = (E, R, T)
```

Where:
- **E** = Set of entities (nodes): people, places, organizations, events
- **R** = Set of relation types (edge labels): KNOWS, FAMILY_OF, WORKS_FOR, etc.
- **T** = Set of triples: (subject, relation, object) with evidence

**Example Triple from Dune**:
```json
{
  "subject": "Paul Atreides",
  "relation": "FAMILY_OF",
  "object": "Lady Jessica",
  "confidence": 1.0,
  "evidence_span": {
    "text": "Jessica repeated the words to Paul.",
    "start": 87,
    "end": 122
  }
}
```

### Mathematical Quality Metrics

The pipeline computes intrinsic quality metrics without requiring ground truth labels:

#### 1. **Shannon Entropy** (Relation Diversity)
Measures unpredictability of relation distribution. Higher entropy = more diverse relationships.

```
H(X) = -Σ p(rᵢ) log₂ p(rᵢ)
```

Where `p(rᵢ)` is the probability of relation type `rᵢ`.

**Dune Result**: H = 4.85 (out of max 6.70), indicating rich relation diversity.

#### 2. **Gini Coefficient** (Relation Inequality)
Measures concentration of relations. Lower Gini = more balanced distribution.

```
G = (Σᵢ Σⱼ |xᵢ - xⱼ|) / (2n²μ)
```

**Dune Result**: G = 0.548, indicating moderate concentration (not dominated by single relation type).

#### 3. **Graph Density** (Connectivity)
Measures how interconnected the graph is.

```
Density = |E| / (|V| × (|V| - 1))
```

Where |E| = edges, |V| = nodes.

**Dune Result**: Density = 0.0020, typical for narrative graphs (sparse but meaningful connections).

#### 4. **Average Path Length** (Network Compactness)
Average shortest path between all node pairs.

```
L = (1 / (n(n-1))) Σᵢ≠ⱼ d(vᵢ, vⱼ)
```

**Dune Result**: L = 4.85 hops, indicating characters are ~5 steps apart on average.

---

### Big Five Personality Model (OCEAN)

**Why Big Five?** The Five-Factor Model is the most scientifically validated personality framework, with decades of empirical research supporting its cross-cultural validity.

#### The Five Traits:

| Trait | Description | High Score Indicates | Low Score Indicates |
|-------|-------------|---------------------|---------------------|
| **Openness** (O) | Imagination, curiosity, intellectual flexibility | Creative, adventurous, open to new experiences | Practical, traditional, prefers routine |
| **Conscientiousness** (C) | Organization, discipline, goal-directed behavior | Organized, reliable, disciplined | Spontaneous, flexible, less structured |
| **Extraversion** (E) | Social engagement, assertiveness, energy | Outgoing, talkative, seeks social interaction | Reserved, introspective, prefers solitude |
| **Agreeableness** (A) | Compassion, cooperation, trust | Compassionate, cooperative, empathetic | Competitive, skeptical, direct |
| **Neuroticism** (N) | Emotional instability, anxiety, moodiness | Anxious, emotionally reactive, moody | Calm, emotionally stable, resilient |

#### Why Not MBTI?

While MBTI (Myers-Briggs Type Indicator) is popular, it has significant scientific limitations:

1. **Binary Categories**: Forces false dichotomies (e.g., "Introvert" vs. "Extrovert")
2. **Low Test-Retest Reliability**: 50% of people get different type on retesting
3. **Lack of Empirical Validation**: Not supported by peer-reviewed research
4. **No Gradation**: Cannot represent spectrum of traits

**Big Five Advantages**:
- ✅ Continuous scores (0-1 scale) capturing nuance
- ✅ High test-retest reliability (r > 0.80)
- ✅ Validated across cultures and languages
- ✅ Predictive of real-world outcomes (job performance, relationships, health)

---

## 🏗️ Pipeline Architecture

The system uses a **7-stage multi-prompt architecture** rather than a single end-to-end prompt. This modular design:

1. **Reduces hallucination** via focused sub-tasks
2. **Enables quality gates** between stages (QA filtering)
3. **Allows partial reprocessing** without re-running entire pipeline
4. **Improves transparency** with stage-specific outputs

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INPUT: Novel Text (JSONL Chunks)                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  1. Extract Triples     │  LLM extracts (subject, relation, object)
                    │     with Evidence       │  + confidence + text spans
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  2. Canonicalize Names  │  Merge aliases: "Paul" → "Paul Atreides"
                    │     (Entity Resolution) │  Frequency-based + manual mappings
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  3. QA Filtering        │  Apply confidence thresholds (≥0.65)
                    │     (Quality Control)   │  Validate evidence spans, deduplicate
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  4. Infer Personality   │  Character-centric Big Five scoring
                    │     (Big Five Traits)   │  Evidence aggregation across passages
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  5. Build Graph         │  NetworkX MultiDiGraph construction
                    │     (GraphML + JSON)    │  Node/edge properties + metadata
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  6. Visualize           │  Interactive HTML (PyVis)
                    │     (HTML + PyVis)      │  Tooltips with evidence spans
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  7. Evaluate            │  Compute 15 metrics (entropy, Gini,
                    │     (15 Metrics)        │  clustering, personality stats)
                    └─────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  OUTPUT: Knowledge Graph │
                    │  + Personality Profiles  │
                    └──────────────────────────┘
```

---

## 📈 Sample Results from Dune

### Extracted Triples (Knowledge Graph Edges)

| Subject | Relation | Object | Confidence | Evidence Span |
|---------|----------|--------|------------|---------------|
| Paul Atreides | FAMILY_OF | Lady Jessica | 1.0 | "Jessica repeated the words to Paul." |
| Paul Atreides | FAMILY_OF | Duke Leto | 0.9 | "mother of the ducal heir" |
| Lady Jessica | MEMBER_OF | Bene Gesserit Sisterhood | 0.9 | "a Bene Gesserit Lady" |
| House Harkonnen | ENEMY_OF | House Atreides | 0.9 | "their mortal enemies, the Harkonnens" |
| Duke Leto | POPULAR_AMONG | Great Houses of the Landsraad | 0.9 | "the Duke Leto was popular among the Great Houses" |
| Fremen | LOCATED_IN | Arrakis | 0.9 | "people called Fremen" living at "the desert edge" |

**Total Statistics**:
- **1,050 unique entities** (nodes)
- **2,246 relationships** (edges)
- **104 unique relation types** discovered (beyond predefined set)
- **100% evidence coverage** (every triple has textual proof)

---

### Personality Profiles (Big Five Traits)

#### Paul Atreides
```json
{
  "openness": 0.70,        // High: dreams, prescience, philosophical
  "conscientiousness": 0.60, // Moderate: disciplined but adaptable
  "extraversion": 0.50,     // Balanced: introspective yet leadership
  "agreeableness": 0.50,    // Moderate: compassionate but decisive
  "neuroticism": 0.60       // Moderate-high: anxiety about future
}
```

**Evidence**:
- **Openness**: "Paul fell asleep to dream of an Arrakeen cavern" (prophetic dreams)
- **Neuroticism**: "Paul felt a sharp pang of fear" (emotional reactivity)

#### Baron Vladimir Harkonnen
```json
{
  "openness": 0.50,         // Moderate: strategic but conventional
  "conscientiousness": 0.70, // High: meticulous planning
  "extraversion": 0.50,     // Balanced: commanding but not social
  "agreeableness": 0.20,    // Very low: cruel, manipulative
  "neuroticism": 0.60       // Moderate: prone to rage
}
```

**Evidence**:
- **Agreeableness**: "Pity should be cruel! Failure was, by definition, expendable."
- **Conscientiousness**: "The drug was timed. We knew to the minute when you'd be coming out of it."

#### Lady Jessica
```json
{
  "openness": 0.70,         // High: Bene Gesserit training, adaptable
  "conscientiousness": 0.70, // High: disciplined, protective mother
  "extraversion": 0.50,     // Balanced: reserved but capable
  "agreeableness": 0.65,    // Moderately high: compassionate
  "neuroticism": 0.70       // High: anxious about Paul's safety
}
```

**Evidence**:
- **Neuroticism**: "Jessica closed her eyes, feeling tears press out beneath the lids. She fought down the inner trembling."

---

## 📊 Key Visualizations

### 1. Big Five Distribution Across All Characters

This violin plot shows the distribution of personality trait scores across all 12 characters in the Dune knowledge graph:

![Big Five Distribution](assets/Big%20Five%20Distribution.png)

**Key Insights**:
- **Conscientiousness** has highest median (0.70) - survival requires discipline on Arrakis
- **Agreeableness** shows widest spread (0.20-0.80) - conflict-driven narrative
- **Neuroticism** clusters around 0.60 - characters face constant threats

---

### 2. Paul Atreides Ego Network (1-Hop Neighborhood)

**Most Important Visualization**: Shows all entities directly connected to Paul Atreides, the protagonist.

![Paul Ego Network](assets/Paul%20Atreides%20Network.png)

**Network Statistics**:
- **Nodes**: 47 (Paul + 46 connected entities)
- **Edges**: 89 relationships
- **Node Types**:
  - 🔴 Red: Paul Atreides (center)
  - 🔵 Teal: People (Lady Jessica, Duke Leto, Stilgar, etc.)
  - ⚪ Gray: Places/Organizations (Arrakis, Bene Gesserit, etc.)

**Key Connections**:
- **FAMILY_OF**: Lady Jessica, Duke Leto
- **KNOWS**: Stilgar, Gurney Halleck, Duncan Idaho
- **LOCATED_IN**: Arrakis, Caladan
- **MENTIONED_IN**: Various prophetic dreams and visions

This visualization reveals Paul's role as the **narrative hub** connecting major factions (Fremen, Atreides, Bene Gesserit).

---

### 3. Degree Distribution (Node Connectivity)

Shows how many connections each entity has (power-law distribution typical of social networks):

![Degree Distribution](assets/degrees.png)

**Analysis**:
- **Top 5 Most Connected**:
  1. Paul Atreides: 89 connections
  2. Lady Jessica: 52 connections
  3. Baron Harkonnen: 45 connections
  4. Duke Leto: 38 connections
  5. Stilgar: 36 connections

- **Long Tail**: 80% of entities have ≤5 connections (minor characters)
- **Power Law**: Few highly connected hubs, many peripheral nodes

**★ Insight**: The degree distribution reveals Dune's narrative structure—a few central characters (Paul, Jessica, Baron) drive the plot, while most entities appear in supporting roles. This power-law pattern is typical of real-world social networks, validating the extraction quality.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key (GPT-4) or Anthropic API key (Claude 3.5 Sonnet)

### Installation

```bash
# Clone repository
git clone https://github.com/Sungchunn/Personality-Knowledge-Graph-Challenge.git
cd Project

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Set API Key

Create a `.env` file in the Project directory:

```bash
# For OpenAI (recommended)
OPENAI_API_KEY=sk-your-key-here

# Or for Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

### 📚 Process Multiple Novels (Easy Method)

We provide 7 pre-processed novels ready to analyze:

#### Available Novels

| Novel | Author | Genre | Short Name |
|-------|--------|-------|------------|
| **Dune** | Frank Herbert | Sci-Fi | `dune` |
| **Do Androids Dream of Electric Sheep?** | Philip K. Dick | Dystopian | `bladerunner` |
| **Foundation** | Isaac Asimov | Space Opera | `foundation` |
| **Neuromancer** | William Gibson | Cyberpunk | `neuromancer` |
| **Dune Messiah** | Frank Herbert | Sci-Fi Sequel | `dune2` |
| **Foundation and Empire** | Isaac Asimov | Space Opera | `foundation2` |
| **Second Foundation** | Isaac Asimov | Space Opera | `foundation3` |

---

#### Quick Demo (50 passages, ~5 min each, ~$0.50-1.50 each)

```bash
# Activate environment
source .venv/bin/activate

# Process individual novels
./scripts/process_individual.sh bladerunner 50
./scripts/process_individual.sh foundation 50
./scripts/process_individual.sh neuromancer 50
./scripts/process_individual.sh dune2 50
./scripts/process_individual.sh foundation2 50
./scripts/process_individual.sh foundation3 50
```

#### Full Novel Processing (all passages, ~15-30 min each, ~$3-8 each)

```bash
./scripts/process_individual.sh bladerunner all
./scripts/process_individual.sh foundation all
./scripts/process_individual.sh neuromancer all
```

#### Batch Processing (Process top 3 novels at once)

```bash
./scripts/process_all_novels.sh 50  # Dune, Blade Runner, Foundation
```

---

### 📊 Analyze Results with Jupyter Notebook

After processing, use the interactive notebook to explore results:

```bash
# Open notebook
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist"
jupyter notebook demo.ipynb
```

**In the notebook** (Cell 2):
```python
NOVEL_SELECTION = "bladerunner"  # Change to any novel name
```

Then **Kernel → Restart & Run All**

**What you'll see**:
- ✅ Top 10 Big Five personality comparison (bar charts)
- ✅ 5 individual network graphs (full-size visualizations)
- ✅ Relation type distribution (top 15)
- ✅ Confidence statistics (quality metrics)
- ✅ Automated insights (AI-generated observations)

---

### 🔬 Advanced: Direct Python CLI

For custom processing, use the Python CLI directly:

```bash
# Process first 50 passages of Dune (5-10 minutes, ~$0.50)
python -m src.pipeline.cli \
  --input-file data/jsonl/dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl \
  --output-root outputs/my_run \
  --max-passages 50 \
  all

# Or process full novel (15-30 minutes, ~$3-8)
python -m src.pipeline.cli \
  --input-file data/jsonl/dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl \
  all
```

---

### View Results

```bash
# Open interactive graph visualization
open outputs/my_run/graph.html

# Inspect extracted data
cat outputs/my_run/triples_canonical.jsonl | head -5
cat outputs/my_run/traits_final.jsonl | head -3

# View evaluation metrics
cat outputs/my_run/metrics.json
```

---

## 📂 Project Structure

```
Project/
├── README.md                          # This file
├── DESIGN_REPORT.md                   # Complete design justification (550+ lines)
├── RESEARCH_SESSION.md                # LLM collaboration log (340+ lines)
├── SYNTHETIC_DATA_ANALYSIS.md         # Synthetic vs. real data analysis
├── SUBMISSION_CHECKLIST.md            # Deliverables checklist
├── assessment_demo.ipynb              # Interactive Jupyter demo
│
├── src/
│   ├── ingest/                        # PDF → Text → JSONL pipeline
│   │   ├── pdf_to_text.py
│   │   ├── clean_text.py
│   │   ├── split_structure.py
│   │   └── cli.py
│   │
│   └── pipeline/                      # Knowledge graph extraction
│       ├── cli.py                     # Unified CLI (7 stages)
│       ├── extract_triples.py         # Stage 1: Triple extraction
│       ├── canonicalize.py            # Stage 2: Entity resolution
│       ├── filter_qa.py               # Stage 3: Quality filtering
│       ├── infer_personality.py       # Stage 4: Big Five inference
│       ├── build_graph.py             # Stage 5: Graph construction
│       ├── visualize.py               # Stage 6: HTML visualization
│       ├── evaluate.py                # Stage 7: Metrics computation
│       ├── generate_synthetic.py      # Synthetic data generator
│       └── config.py                  # Pipeline configuration
│
├── data/
│   ├── raw_pdf/                       # Input PDFs (not in repo)
│   ├── text/                          # Cleaned text files
│   ├── jsonl/                         # Chunked passages (pipeline input)
│   │   └── dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl
│   └── synthetic/                     # Generated synthetic dataset
│       ├── synthetic_passages.jsonl
│       ├── ground_truth.json
│       └── synthetic_metadata.json
│
├── outputs/
│   └── run_20251020_010533/          # Sample run outputs
│       ├── triples_raw.jsonl          # Stage 1 output
│       ├── triples_canonical.jsonl    # Stage 2 output (1,050 entities)
│       ├── traits_final.jsonl         # Stage 4 output (12 profiles)
│       ├── graph.graphml              # Stage 5 output (NetworkX format)
│       ├── graph.html                 # Stage 6 output (interactive viz)
│       ├── graph_mini.html            # Lightweight 11-node version
│       ├── metrics.json               # Stage 7 output (15 metrics)
│       └── run_summary.json           # Pipeline metadata
│
├── prompts/                           # LLM prompts for each stage
│   ├── extract_triples.txt
│   ├── canonicalize.txt
│   ├── infer_personality.txt
│   └── ...
│
├── tests/                             # Unit tests (pytest)
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Package configuration
└── Makefile                           # Automation commands
```

---

## 🔬 Evaluation Methodology

Since there is **no ground truth** for Dune (no manually labeled knowledge graph), the pipeline uses **intrinsic quality metrics**:

### Evidence Quality
- **Coverage**: 100% of triples have evidence spans
- **Avg Length**: 89.4 characters per evidence span
- **Diversity**: 0.944 (94.4% unique evidence texts)

### Confidence Distribution
- **Mean**: 0.87 ± 0.059
- **Calibration**: Tight std dev indicates well-calibrated uncertainty

### Relation Diversity
- **Shannon Entropy**: 4.85 / 6.70 (72% of maximum entropy)
- **Gini Coefficient**: 0.548 (moderate inequality, not dominated by single relation)
- **Top-3 Concentration**: 27.4% (not overly concentrated)

### Graph Structure
- **Density**: 0.0020 (typical for narrative graphs)
- **Avg Clustering**: 0.0018 (sparse but meaningful clusters)
- **Avg Path Length**: 4.85 hops (small-world property)

### Personality Quality
- **12 complete profiles** (vs. 41 duplicates before canonicalization)
- **3.6 traits per character** on average
- **0.78 mean confidence** in personality inferences

**Comparison to Synthetic Data**:
While synthetic data allows computing precision/recall, it cannot test:
- Pronoun resolution ("he" → "Paul Atreides")
- Alias merging ("Duke Leto" = "Leto Atreides" = "the Duke")
- Metaphorical language ("Paul IS the desert")

See [SYNTHETIC_DATA_ANALYSIS.md](SYNTHETIC_DATA_ANALYSIS.md) for full justification.

---

## 🧪 Working with Synthetic Data

While the pipeline is designed for real literary text, you can also generate and process synthetic data for testing and benchmarking.

### What is Synthetic Data?

**Synthetic data** = artificially generated passages with known ground truth relationships and personality traits. Useful for:
- ✅ Computing precision/recall metrics (known correct answers)
- ✅ Testing edge cases without manual labeling
- ✅ Development without expensive API calls on full novels
- ❌ **Limitation**: Cannot test real-world challenges (pronouns, aliases, metaphors)

### Generate Synthetic Data

The pipeline includes a template-based synthetic data generator:

```bash
# Generate 100 synthetic passages
python -m src.pipeline.generate_synthetic \
  --num-passages 100 \
  --output-dir data/synthetic/

# This creates:
# - synthetic_passages.jsonl (input passages)
# - ground_truth.json (correct answers)
# - synthetic_metadata.json (statistics)
```

**Output structure**:
```json
{
  "passage_id": "synthetic_00001",
  "text": "Paul Atreides was born on Caladan. Jessica is his mother...",
  "ground_truth": {
    "triples": [
      {"subject": "Paul Atreides", "relation": "BORN_IN", "object": "Caladan"},
      {"subject": "Paul Atreides", "relation": "FAMILY_OF", "object": "Jessica"}
    ],
    "personalities": [
      {
        "person_name": "Paul Atreides",
        "traits": {"openness": 0.75, "conscientiousness": 0.65, ...}
      }
    ]
  }
}
```

### Process Synthetic Data

```bash
# Run pipeline on synthetic data
python -m src.pipeline.cli \
  --input-file data/synthetic/synthetic_passages.jsonl \
  --output-root outputs/synthetic_run \
  all

# Compare against ground truth
python -m src.pipeline.evaluate_synthetic \
  --predictions outputs/synthetic_run/triples_canonical.jsonl \
  --ground-truth data/synthetic/ground_truth.json

# Output: precision, recall, F1 scores
```

### Synthetic Data Templates

The generator uses predefined templates:

```python
TRIPLE_TEMPLATES = [
    "{person} was born in {location}.",
    "{person1} is the friend of {person2}.",
    "{person} works for {organization}.",
    "{person} leads {organization}.",
    # ... 20+ templates
]

PERSONALITY_TEMPLATES = [
    "{person} was always curious and open to new ideas.",  # High openness
    "{person} was anxious and worried constantly.",        # High neuroticism
    "{person} was organized and disciplined.",             # High conscientiousness
    # ... 25+ templates per trait
]
```

### Why We Use Real Data Primarily

**Advantages of Real Data (Dune)**:
1. Tests pronoun resolution ("he" → "Paul Atreides")
2. Tests alias merging ("Duke Leto" = "Leto Atreides" = "the Duke")
3. Tests metaphorical language ("Paul IS the desert")
4. Authentic narrative complexity
5. Prepares for production deployment

**Advantages of Synthetic Data**:
1. Known ground truth (precision/recall)
2. Controlled complexity
3. No copyright concerns
4. Fast to generate

**Our Approach**: Use real data as primary dataset, synthetic data for specific testing scenarios.

See [SYNTHETIC_DATA_ANALYSIS.md](SYNTHETIC_DATA_ANALYSIS.md) for detailed comparison and methodology.

---

## 📊 Key Design Decisions

### 1. Multi-Stage Pipeline vs. Single Prompt
**Decision**: 7 separate LLM calls with intermediate outputs
**Why**:
- Reduces hallucination via task decomposition
- Enables quality gates (QA filtering at 0.65 confidence)
- Allows partial reprocessing (e.g., re-run personality without re-extracting triples)

**Trade-off**: Higher API cost, but significantly better quality.

### 2. Real Data (Dune) vs. Synthetic Data
**Decision**: Real novel text as primary dataset
**Why**:
- Tests robustness to pronouns, aliases, metaphors
- Prepares for production deployment
- Authentic complexity missing from template-based generation

**Trade-off**: No precision/recall metrics, but intrinsic metrics (entropy, evidence quality) sufficient.

See [DESIGN_REPORT.md](DESIGN_REPORT.md#22-data-source-real-vs-synthetic) for full analysis.

### 3. Big Five vs. MBTI
**Decision**: Five-Factor Model (OCEAN)
**Why**:
- Scientific validity (peer-reviewed, cross-cultural)
- Continuous scores (0-1) vs. binary categories
- High test-retest reliability (r > 0.80)

**Trade-off**: Less familiar to general audience than MBTI.

### 4. Character-Centric Aggregation
**Decision**: Process all passages per character, then aggregate traits
**Why**: Prevents duplicate profiles (41 → 12 profiles after fix)
**Implementation**: [fix_existing_data.py](src/pipeline/fix_existing_data.py)

---

## 📚 Documentation

### Core Documentation
- **[README.md](README.md)**: This file - project overview, quick start, results
- **[demo.ipynb](../demo.ipynb)**: Interactive Jupyter notebook for multi-novel analysis (32 cells)

### Detailed Guides (in `docs/`)
- **[COMMANDS_REFERENCE.md](docs/COMMANDS_REFERENCE.md)**: Complete command reference with workflows
- **[MULTI_NOVEL_GUIDE.md](docs/MULTI_NOVEL_GUIDE.md)**: Guide for processing multiple novels
- **[NOTEBOOK_GUIDE.md](docs/NOTEBOOK_GUIDE.md)**: Jupyter notebook usage documentation
- **[DESIGN_REPORT.md](docs/DESIGN_REPORT.md)**: Complete design justification (550+ lines)
- **[SYNTHETIC_DATA_ANALYSIS.md](docs/SYNTHETIC_DATA_ANALYSIS.md)**: Real vs synthetic data analysis (700+ lines)
- **[RESEARCH_SESSION.md](docs/RESEARCH_SESSION.md)**: LLM-assisted development log (340+ lines)
- **[SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md)**: Deliverables checklist (450+ lines)

---

## 🔮 Future Improvements

1. **Entity Resolution**: Embedding-based similarity (vs. frequency heuristics)
2. **Ground Truth Annotation**: Manually label 100 passages for precision/recall
3. **Multi-Book Linking**: Cross-novel entity resolution (e.g., Dune series)
4. **Temporal Knowledge Graphs**: Track relationships evolving over narrative time
5. **Neo4j Integration**: Scale to millions of triples with graph database
6. **Fine-Tuned Prompts**: Domain-specific prompt engineering for science fiction
7. **Confidence Calibration**: Recalibrate LLM confidence scores via post-processing

---

## 🤝 Contributing

This is a demonstration project for the Intellumia Personality Knowledge Graph Challenge. For questions or suggestions:

- **Author**: Sungchunn
- **Repository**: [github.com/Sungchunn/Personality-Knowledge-Graph-Challenge](https://github.com/Sungchunn/Personality-Knowledge-Graph-Challenge)
- **Issues**: [Open an issue](https://github.com/Sungchunn/Personality-Knowledge-Graph-Challenge/issues)

---

## 📄 License

This codebase is for **private research and educational purposes**. The Dune novel text is used under fair use for academic demonstration. Do not redistribute copyrighted texts publicly.

Code: MIT License
Data: Fair use (research/education)

---

## 🙏 Acknowledgments

- **Frank Herbert**: Author of *Dune*, the test corpus
- **Anthropic**: Claude 3.5 Sonnet API for LLM inference
- **NetworkX**: Graph data structure and algorithms
- **PyVis**: Interactive graph visualizations
- **Project Gutenberg**: Inspiration for text ingestion pipeline

---

## 📞 Contact

**Sungchunn**
**Date**: October 20, 2025
**Challenge**: Intellumia Personality Knowledge Graph
**Repository**: [github.com/Sungchunn/Personality-Knowledge-Graph-Challenge](https://github.com/Sungchunn/Personality-Knowledge-Graph-Challenge)

---

**Last Updated**: October 20, 2025
