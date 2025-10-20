# Jupyter Notebook Guide

## 📍 Location
**Main Notebook**: `/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/demo.ipynb`

---

## 🚀 Quick Start

### 1. Open the Notebook
```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist"
jupyter notebook demo.ipynb
```

### 2. Configure Which Novel to Analyze (Cell #2)
```python
NOVEL_SELECTION = "dune"  # Change to: bladerunner, foundation, neuromancer, dune2
```

### 3. Run All Cells
- Click **Cell → Run All** or press **Shift+Enter** through each cell
- The notebook will auto-detect your latest run for that novel

---

## 🔍 Understanding the `50` Parameter

### Command Breakdown
```bash
./scripts/process_individual.sh bladerunner 50
                                 │           │
                                 │           └─ Number of passages to process
                                 └─ Novel name
```

### What is a "Passage"?

A **passage** = **~500 words** (roughly 1-2 pages) of the novel.

The pipeline:
1. **Splits the book** into ~500-word chunks with slight overlap
2. **Sends each passage** to Claude API for knowledge extraction
3. **Costs ~$0.01 per passage** and takes ~5-10 seconds

### Why Limit to 50?

| Parameter | Passages | Coverage | Time | Cost | Use Case |
|-----------|----------|----------|------|------|----------|
| **50** | 50 | ~10-20% | ~5 min | ~$0.50 | **Quick demo/testing** ✅ |
| 100 | 100 | ~20-30% | ~10 min | ~$1.00 | Proof of concept |
| 200 | 200 | ~40-50% | ~20 min | ~$2.00 | Substantial sample |
| **all** | 200-400 | 100% | ~30-60 min | ~$3-6 | **Full novel** 📚 |

### Real Examples

**Quick Demo (Recommended for Testing)**:
```bash
./scripts/process_individual.sh bladerunner 50
# Time: ~5 minutes
# Cost: ~$0.50
# Result: ~20-30 entities, ~40-60 relationships, 3-5 character profiles
```

**Full Novel Analysis**:
```bash
./scripts/process_individual.sh foundation all
# Time: ~30-45 minutes
# Cost: ~$3-5
# Result: ~300-500 entities, ~600-1000 relationships, 15-25 character profiles
```

---

## 📊 What the Notebook Shows

The notebook includes **30 cells** with comprehensive analysis:

### 1. Novel Overview
- Title, author, genre, description
- Summary statistics (entities, relationships, profiles)

### 2. Sample Data (Cells 9-14)
- **Extracted Triples**: Subject-Relation-Object examples
- **Character Profiles**: All characters with Big Five traits
- **Main Character Deep Dive**: Most developed character with bar chart

### 3. Visualizations (Cells 15-26)
- **Top 10 Big Five Comparison**: Horizontal bar charts comparing personality traits across top 10 characters (NEW!)
- **Relation Type Distribution**: Top 15 most common relationships (horizontal bar chart)
- **Confidence Distribution**: Histogram + boxplot of extraction confidence scores
- **Big Five Distribution**: Violin plots showing trait scores across all characters
- **Top 5 Network Graphs**: Individual full-size graphs for each of the 5 most connected nodes (NEW!)
- **Degree Distribution**: Connectivity analysis with log-scale histogram

### 4. Quality Metrics (Cells 25-26)
Comprehensive table showing:
- Triple quality (count, confidence, evidence coverage)
- Relation diversity (entropy, Gini coefficient)
- Personality quality (profiles, evidence per trait)
- Graph statistics (nodes, edges, density, path length)

### 5. Automated Insights (Cell 28)
AI-generated observations about:
- Most common relationship types and patterns
- Network structure (connected vs sparse)
- Character depth and dominant traits
- Extraction quality and calibration

---

## 🔧 Backward Compatibility

The notebook now supports **both naming patterns**:

1. **New pattern** (recommended): `outputs/dune_run_20251020_123456/`
2. **Old pattern** (legacy): `outputs/run_20251020_123456/`

The notebook will:
- First try to find `{novel}_run_*` directories
- If not found, scan old `run_*` directories and check which novel they contain
- Automatically select the most recent matching run

### Your Existing Dune Runs

You have 12 existing Dune runs in the old format:
```
outputs/run_20251019_005742/
outputs/run_20251019_170622/
... (and 10 more)
```

The notebook will automatically find and use the **latest one** when you set `NOVEL_SELECTION = "dune"`.

---

## 🎨 Customization Options

### Use Specific Run (Instead of Latest)
```python
NOVEL_SELECTION = "dune"
CUSTOM_OUTPUT_DIR = "outputs/run_20251019_170622"  # Specify exact directory
```

### Add New Novel

Edit cell #4, add to `NOVEL_INFO`:
```python
"my_novel": {
    "title": "My Novel Title",
    "author": "Author Name",
    "genre": "Genre",
    "description": "Short description",
    "book_id": "filename-prefix-from-jsonl"
}
```

Then process it:
```bash
./scripts/process_individual.sh my_novel 50
```

---

## 🐛 Troubleshooting

### Error: "No outputs found for 'bladerunner'"

**Solution**: You haven't processed that novel yet. Run:
```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"
source .venv/bin/activate
export ANTHROPIC_API_KEY="your-key"
./scripts/process_individual.sh bladerunner 50
```

### Error: "ModuleNotFoundError: No module named 'pipeline'"

**Solution**: The `project_root` path in cell #4 is wrong. Update to:
```python
project_root = Path("/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project")
```

### Notebook Won't Open

**Solution**: Make sure Jupyter is installed:
```bash
pip install jupyter notebook
```

### Visualizations Don't Show

**Solution**: Make sure matplotlib is installed and using correct backend:
```bash
pip install matplotlib seaborn networkx
```

---

## 📚 Processing Multiple Novels

### Process All Three Main Novels at Once
```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"
source .venv/bin/activate
export ANTHROPIC_API_KEY="your-key"

# Process Dune, Blade Runner, and Foundation (50 passages each)
./scripts/process_all_novels.sh 50
# Time: ~15-20 minutes total
# Cost: ~$1.50 total
```

### Then Analyze Each One
1. Open notebook: `jupyter notebook demo.ipynb`
2. Change `NOVEL_SELECTION` to `"dune"` → Run All
3. Change to `"bladerunner"` → Run All
4. Change to `"foundation"` → Run All

---

## 💡 Key Insights

`★ Insight ─────────────────────────────────────`
**The "50" parameter is a cost/time control**:
- Enables rapid experimentation ($0.50, 5 min) before committing to full runs ($5, 30+ min)
- Each passage = 1 API call = ~$0.01
- Perfect for validating the pipeline works and getting initial insights
`─────────────────────────────────────────────────`

---

## 🔗 Related Documentation

- **Multi-Novel Guide**: `MULTI_NOVEL_GUIDE.md` - Complete guide for processing multiple novels
- **Main README**: `README.md` - Project overview and architecture
- **Design Report**: `DESIGN_REPORT.md` - Technical implementation details

---

**Created**: October 20, 2025
**Last Updated**: October 20, 2025
**Notebook Location**: `/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/demo.ipynb`
