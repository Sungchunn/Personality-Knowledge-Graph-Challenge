# Multi-Novel Analysis Guide

**Process and compare knowledge graphs from multiple novels**

---

## 📚 Available Novels

| Novel | Author | Genre | JSONL Path |
|-------|--------|-------|------------|
| **Dune** | Frank Herbert | Sci-Fi | `data/jsonl/dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl` |
| **Blade Runner** (Do Androids Dream...) | Philip K. Dick | Dystopian | `data/jsonl/bladerunner-1-dick-philip-kindred-do-androids-dream-of-electric-sheep-libgen-li-2.jsonl` |
| **Foundation** | Isaac Asimov | Space Opera | `data/jsonl/foundation-1-asimov-isaac-foundation-libgen-li.jsonl` |
| **Neuromancer** | William Gibson | Cyberpunk | `data/jsonl/cyberpunk-1-gibson-william-neuromancer-libgen-li-2.jsonl` |
| **Dune Messiah** | Frank Herbert | Sci-Fi | `data/jsonl/dune-2-herbert-brian-herbert-frank-dune-messiah-libgen-li.jsonl` |
| **Foundation and Empire** | Isaac Asimov | Space Opera | `data/jsonl/foundation-2-asimov-isaac-foundation-and-empire-libgen-li.jsonl` |
| **Second Foundation** | Isaac Asimov | Space Opera | `data/jsonl/foundation-3-asimov-isaac-second-foundation-libgen-li.jsonl` |

---

## 🚀 Quick Start: Process Multiple Novels

### Option 1: Process All Three Main Novels (Recommended)

```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"
source .venv/bin/activate
export ANTHROPIC_API_KEY="your-api-key-here"

# Process 50 passages from each (~15-20 min total, ~$1.50)
./scripts/process_all_novels.sh 50
```

**This will create**:
- `outputs/dune_run_TIMESTAMP/`
- `outputs/bladerunner_run_TIMESTAMP/`
- `outputs/foundation_run_TIMESTAMP/`

---

### Option 2: Process Individual Novels

#### Blade Runner (Do Androids Dream of Electric Sheep)

**Demo** (50 passages, ~5 min, ~$0.50):
```bash
./scripts/process_individual.sh bladerunner 50
```

**Full novel** (~15 min, ~$2):
```bash
./scripts/process_individual.sh bladerunner all
```

#### Foundation

**Demo** (50 passages, ~5 min, ~$0.50):
```bash
./scripts/process_individual.sh foundation 50
```

**Full novel** (~20 min, ~$2.50):
```bash
./scripts/process_individual.sh foundation all
```

#### Neuromancer

```bash
./scripts/process_individual.sh neuromancer 50
```

---

### Option 3: Direct Python Commands

If scripts don't work, use these direct commands:

**Blade Runner**:
```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"
source .venv/bin/activate

python -m src.pipeline.cli \
  --input-file data/jsonl/bladerunner-1-dick-philip-kindred-do-androids-dream-of-electric-sheep-libgen-li-2.jsonl \
  --output-root outputs/bladerunner_run_$(date +%Y%m%d_%H%M%S) \
  --max-passages 50 \
  all
```

**Foundation**:
```bash
python -m src.pipeline.cli \
  --input-file data/jsonl/foundation-1-asimov-isaac-foundation-libgen-li.jsonl \
  --output-root outputs/foundation_run_$(date +%Y%m%d_%H%M%S) \
  --max-passages 50 \
  all
```

**Neuromancer**:
```bash
python -m src.pipeline.cli \
  --input-file data/jsonl/cyberpunk-1-gibson-william-neuromancer-libgen-li-2.jsonl \
  --output-root outputs/neuromancer_run_$(date +%Y%m%d_%H%M%S) \
  --max-passages 50 \
  all
```

---

## 📊 Analyze Results with Jupyter Notebook

### Using the Customizable Notebook

1. **Open notebook**:
   ```bash
   cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"
   jupyter notebook analysis_custom.ipynb
   ```

2. **Configure novel** (in first code cell):
   ```python
   NOVEL_SELECTION = "bladerunner"  # Change to: foundation, neuromancer, dune, etc.
   ```

3. **Run all cells**: The notebook will automatically load the latest run for that novel

### Available Analyses

The custom notebook provides:
- ✅ Sample extracted triples
- ✅ Character personality profiles (Big Five)
- ✅ Detailed main character analysis
- ✅ Relation type distribution
- ✅ Confidence score statistics
- ✅ Big Five trait distribution across characters
- ✅ Network visualization (ego graph of main character)
- ✅ Degree distribution (connectivity analysis)
- ✅ Comprehensive quality metrics
- ✅ Automated insights generation

---

## 📂 Output Structure

After processing, each novel creates:

```
outputs/NOVEL_run_TIMESTAMP/
├── triples_raw.jsonl          # Stage 1: Raw extractions
├── triples_canonical.jsonl    # Stage 2: Canonical entities
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

## 🔍 Quick Comparison Commands

### Compare Triple Counts

```bash
for novel in dune bladerunner foundation; do
    latest=$(ls -d outputs/${novel}_run_* 2>/dev/null | tail -1)
    if [ -d "$latest" ]; then
        count=$(wc -l < "$latest/triples_canonical.jsonl")
        echo "$novel: $count triples"
    fi
done
```

### Compare Character Profiles

```bash
for novel in dune bladerunner foundation; do
    latest=$(ls -d outputs/${novel}_run_* 2>/dev/null | tail -1)
    if [ -d "$latest" ]; then
        count=$(wc -l < "$latest/traits_final.jsonl")
        echo "$novel: $count characters"
    fi
done
```

### View Top Relations by Novel

```bash
cat outputs/dune_run_*/triples_canonical.jsonl | jq -r '.relation' | sort | uniq -c | sort -rn | head -5
echo "---"
cat outputs/bladerunner_run_*/triples_canonical.jsonl | jq -r '.relation' | sort | uniq -c | sort -rn | head -5
echo "---"
cat outputs/foundation_run_*/triples_canonical.jsonl | jq -r '.relation' | sort | uniq -c | sort -rn | head -5
```

---

## 📈 Expected Results (50 Passages Demo)

Based on Dune baseline, expect similar scale:

| Novel | Entities | Relationships | Character Profiles | Time | Cost |
|-------|----------|---------------|-------------------|------|------|
| Dune | ~200-300 | ~400-600 | ~5-10 | 5 min | $0.50 |
| Blade Runner | ~150-250 | ~300-500 | ~4-8 | 5 min | $0.50 |
| Foundation | ~200-350 | ~450-700 | ~6-12 | 5 min | $0.50 |
| Neuromancer | ~180-280 | ~350-550 | ~5-9 | 5 min | $0.50 |

**Full novels** (all passages):
- Time: 15-30 min per novel
- Cost: $2-5 per novel
- Entities: 800-1,500 per novel
- Relationships: 1,500-3,000 per novel

---

## 🎯 Next Steps

### 1. Process Novels
```bash
# Choose one:
./scripts/process_all_novels.sh 50           # All three (dune, bladerunner, foundation)
./scripts/process_individual.sh foundation 50  # Just Foundation
```

### 2. Analyze with Jupyter
```bash
jupyter notebook analysis_custom.ipynb
# Change NOVEL_SELECTION in first cell
```

### 3. Create Comparison Documentation

After processing multiple novels, create subpages in README:
- `docs/dune_results.md` - Dune-specific findings
- `docs/bladerunner_results.md` - Blade Runner analysis
- `docs/foundation_results.md` - Foundation analysis
- `docs/cross_novel_comparison.md` - Compare all three

### 4. Export Visualizations

```bash
# Save graphs as images for documentation
# (Requires browser automation or screenshot tool)
open outputs/bladerunner_run_*/graph.html  # Screenshot manually
open outputs/foundation_run_*/graph.html
```

---

## 🐛 Troubleshooting

### Issue: Scripts not executable
```bash
chmod +x scripts/process_all_novels.sh
chmod +x scripts/process_individual.sh
```

### Issue: API key not set
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
# Or add to ~/.bashrc or ~/.zshrc
```

### Issue: "No outputs found" in notebook
Make sure you've run the pipeline first:
```bash
./scripts/process_individual.sh bladerunner 50
```

### Issue: Out of API credits
- Reduce passages: `--max-passages 10`
- Wait for credits to refresh
- Use caching (automatic in pipeline)

---

## 📚 Documentation Structure (Proposed)

```
README.md                      # Main overview
├── docs/
│   ├── dune_results.md       # Dune: Politics, religion, ecology
│   ├── bladerunner_results.md # Blade Runner: Identity, humanity, empathy
│   ├── foundation_results.md  # Foundation: Psychohistory, civilization, mathematics
│   └── comparison.md          # Cross-novel insights
├── analysis_custom.ipynb      # Customizable analysis notebook
├── assessment_demo.ipynb      # Original Dune-focused demo
└── MULTI_NOVEL_GUIDE.md       # This file
```

---

## 💡 Comparative Research Questions

Once you have multiple novels processed:

1. **Personality Differences**:
   - Do sci-fi characters have higher Openness than dystopian?
   - Is Neuroticism higher in cyberpunk (high-stress) vs space opera?

2. **Relationship Patterns**:
   - Which genre has most ENEMY_OF relations? (conflict-driven)
   - Do political novels (Dune) have more LEADS/SERVES relations?

3. **Network Structure**:
   - Are cyberpunk networks denser (interconnected tech)?
   - Do space operas have longer path lengths (galactic scale)?

4. **Entity Types**:
   - Do dystopian novels have more LOCATED_IN (place-focused)?
   - Do political novels have more MEMBER_OF (factions)?

---

## 🔗 Resources

- **GitHub**: https://github.com/Sungchunn/Personality-Knowledge-Graph-Challenge
- **Design Report**: `DESIGN_REPORT.md`
- **Pipeline Documentation**: `README.md`
- **Troubleshooting**: `outputs/run_*/TROUBLESHOOTING.md`

---

**Created**: October 20, 2025
**Author**: Sungchunn
**Last Updated**: October 20, 2025
