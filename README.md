# Personality Knowledge Graph Challenge - PDF Ingestion Pipeline

Complete Python pipeline to extract, clean, and chunk PDF novels into analysis-ready text datasets for Knowledge Graph extraction and personality inference.

## Purpose

This pipeline converts raw PDF novels (both text-based and scanned) into clean, structured text and JSONL chunks suitable for downstream LLM-based tasks:

1. **Knowledge Graph Extraction**: Extract entities (people, places, events) and relationships
2. **Personality Inference**: Infer Big Five personality traits for characters mentioned in text
3. **LLM-Driven Workflow**: Chain extraction, canonicalization, and analysis steps

## Features

- ✅ **Dual-mode extraction**: Text-based PDFs (PyMuPDF) + OCR for scanned PDFs (ocrmypdf/pytesseract)
- ✅ **Smart text cleaning**: Unicode normalization, dehyphenation, header/footer removal
- ✅ **Structure-aware chunking**: Chapter detection with fallback to overlapping length-based chunks
- ✅ **Provenance tracking**: SHA256 checksums, extraction metadata, processing logs
- ✅ **Idempotent pipeline**: Skips unchanged files automatically
- ✅ **JSONL output**: Ready for LLM consumption with rich metadata

## Data Sources & Legal

These texts are for **private research and educational purposes only**. Ensure you have legal rights to process any PDFs. Do not redistribute copyrighted full texts publicly.

## Project Structure

```
Project/
├── README.md                     # This file
├── pyproject.toml                # Python package configuration
├── requirements.txt              # Pinned dependencies
├── Makefile                      # Automation targets
├── .gitignore                    # Ignore generated files
├── src/
│   └── ingest/
│       ├── __init__.py
│       ├── detect_pdf_type.py    # Text vs. scanned detection
│       ├── pdf_to_text.py        # PyMuPDF + OCR extraction
│       ├── clean_text.py         # Text normalization pipeline
│       ├── split_structure.py    # Chapter detection + chunking
│       ├── make_jsonl.py         # JSONL export with metadata
│       ├── manifest.py           # Provenance metadata generation
│       └── cli.py                # Command-line interface
├── data/
│   ├── raw_pdf/                  # Symlink to external PDF directory
│   ├── text/                     # Clean .txt outputs
│   ├── jsonl/                    # Chunked .jsonl outputs
│   └── metadata/                 # Per-book manifests + run logs
└── scripts/
    ├── run_ingest.sh             # Bash wrapper for ingestion
    └── link_raw.sh               # Create symlink to raw PDFs
```

## Quick Start

### 1. Setup Environment

```bash
cd Project
make setup
```

This creates a Python 3.10+ virtual environment and installs dependencies.

### 2. (Optional) Install OCR Tools

For scanned PDFs, install `ocrmypdf`:

```bash
# macOS
brew install ocrmypdf

# Ubuntu/Debian
sudo apt-get install ocrmypdf tesseract-ocr
```

If `ocrmypdf` is unavailable, the pipeline falls back to `pytesseract` (slower but works).

### 3. Run Ingestion

```bash
make ingest
```

Or customize paths:

```bash
source .venv/bin/activate
python -m src.ingest.cli \
  --pdf-root "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Data" \
  --out-root ./data \
  --ocr auto \
  --min-chars 1200 \
  --max-chars 2000 \
  --overlap 200
```

### 4. View Outputs

- **Clean text**: `data/text/<book_id>.txt`
- **JSONL chunks**: `data/jsonl/<book_id>.jsonl`
- **Metadata**: `data/metadata/<book_id>.json`
- **Run logs**: `data/metadata/ingest_run_<timestamp>.json`

## CLI Options

```
python -m src.ingest.cli --help

Options:
  --pdf-root PATH       Root directory with PDFs (required)
  --out-root PATH       Output directory (default: ./data)
  --ocr MODE            Extraction mode: auto, text, ocr (default: auto)
  --min-chars N         Minimum chunk size (default: 1200)
  --max-chars N         Maximum chunk size (default: 2000)
  --overlap N           Chunk overlap (default: 200)
  --only-mode MODE      Filter: only process 'text' or 'ocr' PDFs
```

## JSONL Schema

Each line in `<book_id>.jsonl`:

```json
{
  "book_id": "pride-and-prejudice",
  "title": "Pride and Prejudice",
  "authors": ["Jane Austen"],
  "source_path": "/path/to/Pride and Prejudice.pdf",
  "extraction_mode": "text",
  "chapter": 3,
  "chunk_index": 2,
  "start_char": 12345,
  "end_char": 14123,
  "text": "It is a truth universally acknowledged..."
}
```

## Quality Checks

### Sample Random Chunks

```bash
source .venv/bin/activate
python << 'EOF'
import json
import random
from pathlib import Path

jsonl_files = list(Path("data/jsonl").glob("*.jsonl"))
if jsonl_files:
    sample_file = random.choice(jsonl_files)
    with sample_file.open() as f:
        chunks = [json.loads(line) for line in f]
    sample = random.choice(chunks)
    print(f"Book: {sample['title']}")
    print(f"Chapter: {sample.get('chapter', 'N/A')}")
    print(f"Chunk {sample['chunk_index']} ({sample['start_char']}-{sample['end_char']}):")
    print(sample['text'][:500])
EOF
```

### Basic Statistics

```bash
python << 'EOF'
import json
from pathlib import Path

jsonl_files = list(Path("data/jsonl").glob("*.jsonl"))
total_chunks = 0
total_chars = 0

for jf in jsonl_files:
    with jf.open() as f:
        for line in f:
            chunk = json.loads(line)
            total_chunks += 1
            total_chars += len(chunk['text'])

print(f"Total books: {len(jsonl_files)}")
print(f"Total chunks: {total_chunks}")
print(f"Avg chunk length: {total_chars // total_chunks if total_chunks else 0} chars")
EOF
```

## Makefile Targets

- `make help` - Show all available commands
- `make setup` - Create venv and install dependencies
- `make link` - Symlink external PDF directory to `data/raw_pdf`
- `make ingest` - Run full ingestion pipeline
- `make clean` - Remove generated outputs (text, jsonl, metadata)
- `make clean-all` - Remove everything including venv
- `make test` - Run pytest suite (when tests are added)
- `make lint` - Run ruff linter
- `make format` - Format code with black

## Idempotency

The pipeline **skips reprocessing** if:
- All outputs exist (`.txt`, `.jsonl`, manifest)
- PDF checksum matches stored value in manifest

To force reprocessing, delete the relevant outputs or change the source PDF.

---

## Phase 2: Extraction Pipeline

**Purpose**: Transform ingested JSONL passages into a knowledge graph with entity relationships and Big Five personality profiles, using LLM-assisted extraction, canonicalization, and inference.

### Pipeline Stages

The extraction pipeline consists of 7 stages executed via a unified CLI:

1. **Extract Triples** - LLM-based extraction of (subject, relation, object) triples with confidence scores and evidence spans
2. **Canonicalize Entities** - Merge aliases and variants (e.g., "Elizabeth" → "Elizabeth Bennet")
3. **QA Filtering** - Apply confidence thresholds, span validation, deduplication
4. **Infer Personality** - Big Five trait scoring for people with textual evidence
5. **Build Graph** - Construct NetworkX property graph with personality attributes
6. **Visualize** - Generate interactive HTML graph (pyvis)
7. **Evaluate** - Compute metrics and descriptive statistics

### Quick Start

**Install pipeline dependencies:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Set Anthropic API key:**

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Run complete pipeline:**

```bash
python -m src.pipeline.cli all \
  --input-jsonl-root "./data/jsonl" \
  --output-root "./outputs/run_01" \
  --confidence-threshold 0.65 \
  --max-passages 10
```

### CLI Commands

Run individual stages:

```bash
# Extract raw triples
python -m src.pipeline.cli extract --output-root ./outputs/run_01

# Canonicalize entities
python -m src.pipeline.cli canonicalize --output-root ./outputs/run_01

# Infer personality traits
python -m src.pipeline.cli traits --output-root ./outputs/run_01

# Build graph and visualize
python -m src.pipeline.cli graph --output-root ./outputs/run_01

# Generate evaluation metrics
python -m src.pipeline.cli eval --output-root ./outputs/run_01
```

### Pipeline Outputs

After running the pipeline, artifacts are saved to `outputs/run_<timestamp>/`:

```
outputs/run_01/
├── triples_raw.jsonl          # Extracted triples before canonicalization
├── triples_canonical.jsonl    # Canonicalized and filtered triples
├── traits_raw.jsonl           # All personality inferences
├── traits_final.jsonl         # High-confidence personality profiles
├── graph.graphml              # NetworkX graph (GraphML format)
├── graph.json                 # Graph in JSON format
├── graph.html                 # Interactive visualization
├── metrics.json               # Evaluation metrics
├── run_summary.json           # Pipeline execution summary
└── trace.jsonl                # Structured log of all stages
```

### Example Output Schemas

**Triple (triples_canonical.jsonl):**
```json
{
  "subject": "Elizabeth Bennet",
  "relation": "KNOWS",
  "object": "Mr. Darcy",
  "confidence": 0.95,
  "evidence_span": {
    "text": "Elizabeth had known Mr. Darcy for several months",
    "start": 245,
    "end": 298
  },
  "source_passage_id": "pride-and-prejudice_12",
  "book_id": "pride-and-prejudice"
}
```

**Personality Profile (traits_final.jsonl):**
```json
{
  "person_name": "Elizabeth Bennet",
  "traits": [
    {
      "trait_name": "openness",
      "score": 0.85,
      "confidence": 0.90,
      "evidence_spans": [
        {"text": "...", "start": 0, "end": 50}
      ]
    },
    ...
  ],
  "source_passage_ids": ["pride-and-prejudice_5", "pride-and-prejudice_12"],
  "book_id": "pride-and-prejudice"
}
```

### Configuration Options

Default settings in `src/pipeline/config.py`:

- **Model**: `claude-3-5-sonnet-20241022`
- **Confidence threshold**: `0.65`
- **Min/max span length**: `10` / `500` characters
- **Allowed relations**: `KNOWS`, `FAMILY_OF`, `FRIENDS_WITH`, `ENEMY_OF`, `LOVES`, `HATES`, `WORKS_FOR`, `LEADS`, `MEMBER_OF`, `OWNS`, `LOCATED_IN`, `PARTICIPATES_IN`, `CREATED`, `MENTIONED_IN`
- **Big Five traits**: `openness`, `conscientiousness`, `extraversion`, `agreeableness`, `neuroticism`

### Caveats & Limitations

- **API costs**: LLM calls are made for each passage/entity. Use `--max-passages` to limit processing during development.
- **No ground truth**: Evaluation metrics are descriptive statistics, not accuracy scores (no labeled test set).
- **Prompt sensitivity**: Extraction quality depends on prompt engineering; prompts are in `prompts/` directory.
- **Canonicalization imperfect**: Entity resolution uses heuristics; manual review may be needed for critical applications.
- **Personality inference**: Based on limited text; not clinical assessments.

### Testing

Run smoke tests (no API calls):

```bash
pytest tests/
```

### Next Steps

- Add more sophisticated entity resolution (e.g., embedding-based similarity)
- Integrate Neo4j for large-scale graph storage and querying
- Implement evaluation against human-annotated ground truth
- Fine-tune prompts for specific genres or domains
- Add support for multi-book entity linking

## Git Workflow

Initialize and push to GitHub:

```bash
cd Project

# If not already a git repo
git init
git remote add origin git@github.com:Sungchunn/Personality-Knowledge-Graph-Challenge.git

# Stage all files
git add .

# Commit
git commit -m "Ingestion pipeline: PDF→TXT→JSONL with manifests"

# Push
git push -u origin main
```

**Note**: Do **not** add collaborators to the repository. All development is local.

## Dependencies

Core libraries (see `requirements.txt`):
- `pymupdf` - Fast PDF text extraction
- `pytesseract` - OCR fallback
- `pillow` - Image processing for OCR
- `regex` - Advanced text cleaning
- `python-slugify` - Generate clean IDs
- `tqdm` - Progress bars

Optional:
- `ocrmypdf` (CLI tool, not Python package) - Production OCR

## Troubleshooting

### OCR not working

Install `ocrmypdf`:
```bash
brew install ocrmypdf  # macOS
```

Or ensure `tesseract` is available:
```bash
tesseract --version
```

### Empty text extraction

- Check if PDF is password-protected (unsupported)
- Try forcing OCR mode: `--ocr ocr`
- Inspect PDF manually to verify it contains text

### Memory errors on large PDFs

Reduce `--max-chars` or process fewer files at once.

## License

This codebase is for private research. PDFs must comply with copyright law.

---

**Author**: Your Name
**Repository**: https://github.com/Sungchunn/Personality-Knowledge-Graph-Challenge
**Last Updated**: 2025-10-18
