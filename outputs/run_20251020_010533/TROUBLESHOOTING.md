# UI Loading Troubleshooting Guide

## Symptoms
The graph.html file doesn't seem to load properly when opened in a browser.

## Diagnosis Results

✅ **HTML file is structurally valid**
- File size: 4.4 MB (2,754 lines)
- Contains 1,050 nodes and 2,246 edges
- All required libraries (vis.js) are properly referenced
- No syntax errors detected
- Personality trait data is present for 12 characters

## Most Likely Causes

### 1. **Large Graph Rendering Time** (Most Likely)
With 1,050 nodes and 2,246 edges, the graph takes significant time to:
- Parse the data
- Calculate initial layout
- Stabilize the physics simulation

**Expected behavior:**
- You'll see a loading bar that says "0%" initially
- It will slowly progress to 100% (this can take 30-60 seconds on slower machines)
- The graph will then appear

### 2. **Browser Console Errors**
There might be JavaScript errors preventing rendering.

## Troubleshooting Steps

### Step 1: Check Browser Console
1. Open `graph.html` in Chrome or Firefox
2. Press `F12` or `Cmd+Option+I` (Mac) to open Developer Tools
3. Click the "Console" tab
4. Look for any red error messages
5. **If you see errors, copy them and share them**

### Step 2: Wait for Stabilization
The graph uses physics simulation to lay out nodes:
1. Open `graph.html`
2. **Wait at least 60 seconds** without interacting
3. Watch the loading bar at the bottom
4. The visualization should appear when it reaches 100%

### Step 3: Try a Smaller Graph
I can create a filtered version with just the main characters:

```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"
.venv/bin/python create_mini_graph.py
```

This will create `graph_mini.html` with only:
- 12 characters with personality traits
- Direct relationships between them
- Much faster loading

### Step 4: Check Network Tab
If the page is completely blank:
1. Open Developer Tools (F12)
2. Click "Network" tab
3. Reload the page
4. Check if vis-network.min.js and vis-network.min.css loaded successfully (should show 200 status)

## Common Issues and Solutions

### Issue: Blank White Page
**Cause:** CDN files not loading (no internet or blocked)
**Solution:** The HTML uses CDN links for vis.js - you need internet connection

### Issue: Stuck at "Loading..."
**Cause:** Graph is still calculating layout
**Solution:** Wait longer (up to 2 minutes for large graphs)

### Issue: Browser Freezes
**Cause:** Not enough RAM for 1,050 nodes
**Solution:**
1. Close other tabs
2. Try creating mini graph (see Step 3)
3. Use a more powerful computer

### Issue: "Script Error" in Console
**Cause:** JavaScript exception
**Solution:** Share the exact error message for debugging

## Quick Validation Test

Run this command to verify the data is correct:

```bash
cd "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"

python3 << 'EOF'
from src.pipeline.io_utils import load_jsonl
from pathlib import Path

output_dir = Path("outputs/run_20251020_010533")

# Check triples
triples = load_jsonl(output_dir / "triples_canonical.jsonl")
print(f"✓ Triples: {len(triples)}")

# Check personalities
traits = load_jsonl(output_dir / "traits_final.jsonl")
print(f"✓ Personality profiles: {len(traits)}")
for profile in traits:
    print(f"  - {profile['person_name']} ({len(profile['traits'])} traits)")

# Check graph file exists
if (output_dir / "graph.html").exists():
    size_mb = (output_dir / "graph.html").stat().st_size / (1024 * 1024)
    print(f"✓ graph.html exists ({size_mb:.1f} MB)")
EOF
```

## What To Report

If the graph still doesn't load, please provide:

1. **Browser and version** (e.g., "Chrome 120", "Firefox 115")
2. **Operating system** (macOS, Windows, Linux)
3. **What you see:**
   - Blank white page?
   - Loading bar stuck at X%?
   - Error message?
4. **Browser console errors** (F12 → Console tab)
5. **How long you waited** before determining it "doesn't load"

## Alternative: Create Mini Graph

If the full graph is too large, I can create a smaller version focusing on the main characters only. This will load instantly and let you verify the visualization works.

Would you like me to create this lightweight version?
