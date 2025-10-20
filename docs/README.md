# Documentation Index

**All project documentation organized by topic**

---

## 🚀 Getting Started

### New Users Start Here

1. **[../README.md](../README.md)** - Main project overview
   - What is this project?
   - Quick start guide
   - Sample results from Dune
   - Pipeline architecture

2. **[COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md)** - All available commands
   - Process real novels (7 available)
   - Generate synthetic data
   - Jupyter notebook usage
   - Common workflows

3. **[MULTI_NOVEL_GUIDE.md](MULTI_NOVEL_GUIDE.md)** - Multi-novel analysis
   - Available novels table
   - Batch processing
   - Comparison analysis
   - Expected results

---

## 📊 Analysis & Usage

### Jupyter Notebook

**[NOTEBOOK_GUIDE.md](NOTEBOOK_GUIDE.md)** - Complete notebook documentation
- How to open and configure
- Understanding the "50" parameter
- What visualizations to expect
- Troubleshooting

**Location**: `/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/demo.ipynb`

### Processing Novels

**Quick commands**:
```bash
# 50 passages (demo, ~5 min, ~$0.50-1.50)
./scripts/process_individual.sh foundation 50

# Full novel (all passages, ~15-30 min, ~$3-8)
./scripts/process_individual.sh foundation all
```

---

## 🔬 Technical Documentation

### Design & Architecture

1. **[DESIGN_REPORT.md](DESIGN_REPORT.md)** - Complete design justification (550+ lines)
   - Why 7-stage pipeline vs single prompt?
   - Why real data (Dune) vs synthetic?
   - Why Big Five vs MBTI?
   - All trade-offs explained

2. **[SYNTHETIC_DATA_ANALYSIS.md](SYNTHETIC_DATA_ANALYSIS.md)** - Synthetic data deep dive (700+ lines)
   - Template-based generation
   - Real vs synthetic comparison
   - When to use each
   - Precision/recall evaluation

3. **[RESEARCH_SESSION.md](RESEARCH_SESSION.md)** - Development log (340+ lines)
   - LLM-assisted development
   - Research questions
   - Design iterations
   - Debugging sessions

---

## ✅ Submission & Review

**[SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)** - Deliverables checklist (450+ lines)
- All requirements addressed
- File locations
- How to verify each deliverable
- Reviewer guide

---

## 📂 Project Structure

```
Project/
├── README.md                      # Main overview (start here!)
├── demo.ipynb                     # Jupyter notebook (multi-novel analysis)
│
├── docs/                          # All documentation (this directory)
│   ├── README.md                  # This file - documentation index
│   ├── COMMANDS_REFERENCE.md      # All commands
│   ├── MULTI_NOVEL_GUIDE.md       # Multi-novel processing
│   ├── NOTEBOOK_GUIDE.md          # Jupyter notebook guide
│   ├── DESIGN_REPORT.md           # Design justification
│   ├── SYNTHETIC_DATA_ANALYSIS.md # Synthetic data analysis
│   ├── RESEARCH_SESSION.md        # Development log
│   └── SUBMISSION_CHECKLIST.md    # Deliverables checklist
│
├── src/                           # Source code
│   ├── ingest/                    # PDF → JSONL pipeline
│   └── pipeline/                  # Knowledge graph extraction
│
├── scripts/                       # Convenience scripts
│   ├── process_individual.sh      # Process one novel
│   └── process_all_novels.sh      # Batch process 3 novels
│
├── data/
│   ├── jsonl/                     # 7 novels ready to process
│   └── synthetic/                 # Generated synthetic data
│
└── outputs/                       # Pipeline results
    ├── foundation_run_*/          # Foundation results (latest)
    └── run_*/                     # Dune results (13 runs)
```

---

## 🎯 Common Tasks

### I want to...

**...process a new novel**
→ See [COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md#-processing-real-novels)

**...understand the notebook**
→ See [NOTEBOOK_GUIDE.md](NOTEBOOK_GUIDE.md)

**...compare multiple novels**
→ See [MULTI_NOVEL_GUIDE.md](MULTI_NOVEL_GUIDE.md)

**...work with synthetic data**
→ See [SYNTHETIC_DATA_ANALYSIS.md](SYNTHETIC_DATA_ANALYSIS.md)

**...understand design choices**
→ See [DESIGN_REPORT.md](DESIGN_REPORT.md)

**...review the submission**
→ See [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)

---

## 📚 Quick Reference

### Available Novels (7 total)

| Short Name | Full Title | Author |
|------------|------------|--------|
| `dune` | Dune | Frank Herbert |
| `bladerunner` | Do Androids Dream...? | Philip K. Dick |
| `foundation` | Foundation | Isaac Asimov |
| `neuromancer` | Neuromancer | William Gibson |
| `dune2` | Dune Messiah | Frank Herbert |
| `foundation2` | Foundation and Empire | Isaac Asimov |
| `foundation3` | Second Foundation | Isaac Asimov |

### Most Important Commands

```bash
# Process a novel (50 passages demo)
./scripts/process_individual.sh foundation 50

# Analyze results in Jupyter
jupyter notebook demo.ipynb
# Change NOVEL_SELECTION to "foundation"

# View results
open outputs/foundation_run_*/graph.html
```

---

**Created**: October 20, 2025
**Last Updated**: October 20, 2025
