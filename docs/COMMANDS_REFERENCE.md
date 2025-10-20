# Complete Commands Reference

**Quick reference for all pipeline commands**

---

## 📚 Processing Real Novels

### Setup (Once per session)

```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"
source .venv/bin/activate
```

**Note**: API key is already in `.env` file - no need to export!

---

### Available Novels

| Short Name | Full Title | Author | Genre |
|------------|------------|--------|-------|
| `dune` | Dune | Frank Herbert | Sci-Fi |
| `bladerunner` | Do Androids Dream of Electric Sheep? | Philip K. Dick | Dystopian |
| `foundation` | Foundation | Isaac Asimov | Space Opera |
| `neuromancer` | Neuromancer | William Gibson | Cyberpunk |
| `dune2` | Dune Messiah | Frank Herbert | Sci-Fi Sequel |
| `foundation2` | Foundation and Empire | Isaac Asimov | Space Opera |
| `foundation3` | Second Foundation | Isaac Asimov | Space Opera |

---

### Quick Demo (50 passages, ~5 min, ~$0.50-1.50 each)

```bash
./scripts/process_individual.sh bladerunner 50
./scripts/process_individual.sh foundation 50
./scripts/process_individual.sh neuromancer 50
./scripts/process_individual.sh dune2 50
./scripts/process_individual.sh foundation2 50
./scripts/process_individual.sh foundation3 50
```

### Full Novel (all passages, ~15-30 min, ~$3-8 each)

```bash
./scripts/process_individual.sh bladerunner all
./scripts/process_individual.sh foundation all
./scripts/process_individual.sh neuromancer all
```

### Batch Processing (Top 3 novels)

```bash
./scripts/process_all_novels.sh 50  # Dune, Blade Runner, Foundation
```

---

## 🧪 Synthetic Data

### Generate Synthetic Data

Synthetic data already exists at `data/synthetic/`, but you can regenerate:

```bash
# Generate 100 new synthetic passages
python -m src.pipeline.generate_synthetic

# Output:
# - data/synthetic/synthetic_passages.jsonl (input)
# - data/synthetic/ground_truth.json (correct answers)
# - data/synthetic/synthetic_metadata.json (statistics)
```

**What's in synthetic data?**
- 100 passages with known ground truth
- ~400-500 relationships (triples)
- ~20-30 character personality profiles
- Template-based generation (predictable patterns)

### Process Synthetic Data

```bash
# Run pipeline on synthetic data
python -m src.pipeline.cli \
  --input-file data/synthetic/synthetic_passages.jsonl \
  --output-root outputs/synthetic_run \
  --max-passages 100 \
  all

# Results will be in: outputs/synthetic_run/
```

### Evaluate Against Ground Truth

```bash
# Compare predictions vs ground truth
python -m src.pipeline.evaluate_synthetic \
  --predictions outputs/synthetic_run/triples_canonical.jsonl \
  --ground-truth data/synthetic/ground_truth.json

# Shows: precision, recall, F1 scores
```

---

## 📊 Analyze Results (Jupyter Notebook)

### Open Notebook

```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist"
jupyter notebook demo.ipynb
```

### Configure Novel (Cell 2)

```python
NOVEL_SELECTION = "bladerunner"  # Change to any novel name
```

### Run Analysis

**Kernel → Restart & Run All**

### What You'll See:
- ✅ Top 10 Big Five personality bar charts
- ✅ 5 individual network graphs (full-size)
- ✅ Relation type distribution (top 15)
- ✅ Confidence statistics
- ✅ AI-generated insights

---

## 🔬 Advanced: Direct Python CLI

### Process Specific File

```bash
# Process 50 passages
python -m src.pipeline.cli \
  --input-file data/jsonl/foundation-1-asimov-isaac-foundation-libgen-li.jsonl \
  --output-root outputs/my_custom_run \
  --max-passages 50 \
  all

# Process entire novel
python -m src.pipeline.cli \
  --input-file data/jsonl/neuromancer-libgen-li-2.jsonl \
  --output-root outputs/neuromancer_full \
  all
```

### Run Individual Stages

```bash
# Stage 1: Extract triples only
python -m src.pipeline.cli \
  --input-file data/jsonl/dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl \
  --output-root outputs/test_run \
  extract

# Stage 2: Canonicalize (requires stage 1 output)
python -m src.pipeline.cli \
  --input-file data/jsonl/dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl \
  --output-root outputs/test_run \
  canonicalize

# Run all stages
python -m src.pipeline.cli \
  --input-file data/jsonl/dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl \
  --output-root outputs/test_run \
  all
```

---

## 📁 Output Structure

After processing, each run creates:

```
outputs/NOVEL_run_TIMESTAMP/
├── triples_raw.jsonl          # Stage 1: Raw extractions
├── triples_canonical.jsonl    # Stage 2: Deduplicated entities
├── traits_raw.jsonl           # Stage 4: All personality inferences
├── traits_final.jsonl         # Stage 4: High-confidence profiles
├── graph.graphml              # Stage 5: NetworkX format
├── graph.json                 # Stage 5: JSON format
├── graph.html                 # Stage 6: Interactive visualization
├── metrics.json               # Stage 7: Quality metrics
├── run_summary.json           # Pipeline metadata
└── trace.jsonl                # Execution log
```

---

## 🎯 Common Workflows

### Workflow 1: Quick Test on Synthetic Data

```bash
# 1. Generate synthetic data (if not exists)
python -m src.pipeline.generate_synthetic

# 2. Process it (fast, ~2 min)
python -m src.pipeline.cli \
  --input-file data/synthetic/synthetic_passages.jsonl \
  --output-root outputs/synthetic_test \
  all

# 3. Check precision/recall
python -m src.pipeline.evaluate_synthetic \
  --predictions outputs/synthetic_test/triples_canonical.jsonl \
  --ground-truth data/synthetic/ground_truth.json

# 4. View results
open outputs/synthetic_test/graph.html
```

### Workflow 2: Process New Novel

```bash
# 1. Process 50 passages first (demo)
./scripts/process_individual.sh foundation 50

# 2. Check results in notebook
jupyter notebook demo.ipynb
# Change NOVEL_SELECTION to "foundation"

# 3. If good, process full novel
./scripts/process_individual.sh foundation all

# 4. Analyze full results
jupyter notebook demo.ipynb
```

### Workflow 3: Compare Multiple Novels

```bash
# 1. Process 3 novels
./scripts/process_all_novels.sh 50

# 2. Analyze each in notebook
jupyter notebook demo.ipynb
# Switch NOVEL_SELECTION between "dune", "bladerunner", "foundation"

# 3. Compare personality distributions, network structures
```

---

## 💡 Tips & Tricks

### Reduce API Costs

```bash
# Test with 10 passages first
./scripts/process_individual.sh bladerunner 10

# Then scale up if results look good
./scripts/process_individual.sh bladerunner 50
```

### Reprocess Specific Stages

```bash
# If you want to re-run personality inference without re-extracting triples
python -m src.pipeline.cli \
  --input-file data/jsonl/dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl \
  --output-root outputs/existing_run \
  traits
```

### View Results Quickly

```bash
# Count entities and relationships
wc -l outputs/bladerunner_run_*/triples_canonical.jsonl

# See top character profiles
cat outputs/bladerunner_run_*/traits_final.jsonl | jq '.person_name'

# Check quality metrics
cat outputs/bladerunner_run_*/metrics.json | jq '.relation_diversity'
```

---

## 🐛 Troubleshooting

### Error: "declare: -A: invalid option"
**Fixed**: Scripts updated for bash 3.2 compatibility (macOS default)

### Error: "No outputs found for 'bladerunner'"
**Solution**: You haven't processed that novel yet. Run:
```bash
./scripts/process_individual.sh bladerunner 50
```

### Jupyter kernel crashes
**Solution**: Restart kernel: **Kernel → Restart & Clear Output**

### API rate limits
**Solution**: Reduce passages or wait between runs:
```bash
./scripts/process_individual.sh foundation 10  # Smaller batch
sleep 60  # Wait 1 minute
./scripts/process_individual.sh neuromancer 10
```

---

## 📚 Documentation

- **[README.md](README.md)**: Project overview and results
- **[DESIGN_REPORT.md](DESIGN_REPORT.md)**: Design justification (550+ lines)
- **[MULTI_NOVEL_GUIDE.md](MULTI_NOVEL_GUIDE.md)**: Multi-novel analysis guide
- **[NOTEBOOK_GUIDE.md](NOTEBOOK_GUIDE.md)**: Jupyter notebook documentation
- **[SYNTHETIC_DATA_ANALYSIS.md](SYNTHETIC_DATA_ANALYSIS.md)**: Synthetic vs real data comparison

---

**Created**: October 20, 2025
**Last Updated**: October 20, 2025
