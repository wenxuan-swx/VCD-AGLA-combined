# Compilation Instructions for VCD+AGLA Academic Papers

This document provides detailed instructions for compiling the LaTeX papers and generating all figures.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Generating Figures](#generating-figures)
3. [Compiling English Paper](#compiling-english-paper)
4. [Compiling Chinese Paper](#compiling-chinese-paper)
5. [Troubleshooting](#troubleshooting)
6. [File Structure](#file-structure)

---

## Prerequisites

### LaTeX Requirements

#### For English Paper (`paper_english.tex`)

Install the following LaTeX packages:

```bash
# On Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended

# Required packages (usually included in texlive-latex-extra):
# - times
# - epsfig
# - graphicx
# - amsmath
# - amssymb
# - booktabs
# - multirow
# - xcolor
# - hyperref
# - algorithm
# - algorithmic
# - subcaption
```

#### For Chinese Paper (`paper_chinese.tex`)

Additional requirements for Chinese support:

```bash
# On Ubuntu/Debian
sudo apt-get install texlive-xetex texlive-lang-chinese

# Required packages:
# - ctex (for Chinese typesetting)
# - xeCJK (for CJK fonts)
```

### Python Requirements for Figure Generation

Install required Python packages:

```bash
pip install matplotlib numpy seaborn
```

Or use the requirements file:

```bash
pip install -r figures/requirements.txt
```

Create `figures/requirements.txt`:
```
matplotlib>=3.5.0
numpy>=1.21.0
seaborn>=0.11.0
```

---

## Generating Figures

### Step 1: Navigate to Figures Directory

```bash
cd COMBINED/figures
```

### Step 2: Generate All Figures

Run the master script to generate all figures at once:

```bash
python generate_all_figures.py
```

This will create:
- **13 figure sets** (26 files total: PNG + PDF for each)
- Performance comparison charts
- Confusion matrices
- Precision-recall curves
- Error reduction visualizations

### Step 3: Verify Figure Generation

Check that all figures were created:

```bash
ls -lh *.png *.pdf
```

Expected output files:
```
f1_comparison_by_model.png/pdf
f1_comparison_by_dataset.png/pdf
metrics_comparison_llava15_coco.png/pdf
improvement_heatmap.png/pdf
confusion_matrix_baseline_llava15_coco.png/pdf
confusion_matrix_combined_llava15_coco.png/pdf
confusion_matrix_comparison_llava15_coco.png/pdf
confusion_matrix_comparison_llava15_aokvqa.png/pdf
error_reduction_llava15_coco.png/pdf
pr_scatter_comparison.png/pdf
pr_improvement_vectors_llava15.png/pdf
precision_recall_bars.png/pdf
```

### Alternative: Generate Figures Individually

If you need to regenerate specific figures:

```bash
# Performance comparison only
python generate_performance_comparison.py

# Confusion matrices only
python generate_confusion_matrices.py

# Precision-recall curves only
python generate_pr_curves.py
```

---

## Compiling English Paper

### Method 1: Using pdflatex (Recommended)

```bash
cd COMBINED

# First compilation
pdflatex paper_english.tex

# Generate bibliography
bibtex paper_english

# Second compilation (resolve references)
pdflatex paper_english.tex

# Third compilation (finalize)
pdflatex paper_english.tex
```

### Method 2: Using latexmk (Automated)

```bash
cd COMBINED
latexmk -pdf paper_english.tex
```

### Output

The compiled PDF will be: `COMBINED/paper_english.pdf`

---

## Compiling Chinese Paper

### Method 1: Using xelatex (Required for Chinese)

```bash
cd COMBINED

# First compilation
xelatex paper_chinese.tex

# Generate bibliography
bibtex paper_chinese

# Second compilation (resolve references)
xelatex paper_chinese.tex

# Third compilation (finalize)
xelatex paper_chinese.tex
```

**Note:** You MUST use `xelatex` (not `pdflatex`) for the Chinese paper due to CJK font requirements.

### Method 2: Using latexmk with xelatex

```bash
cd COMBINED
latexmk -xelatex paper_chinese.tex
```

### Output

The compiled PDF will be: `COMBINED/paper_chinese.pdf`

---

## Troubleshooting

### Common LaTeX Errors

#### Error: "File not found: figures/xxx.pdf"

**Solution:** Make sure you've generated all figures first:
```bash
cd figures
python generate_all_figures.py
cd ..
```

#### Error: "Package ctex Error: CTeX fontset 'fandol' is unavailable"

**Solution:** Install Chinese fonts:
```bash
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei
```

Or specify a different fontset in `paper_chinese.tex`:
```latex
\documentclass[fontset=ubuntu]{ctexart}
```

#### Error: "Undefined control sequence" in bibliography

**Solution:** Make sure `references.bib` is in the same directory and run bibtex:
```bash
bibtex paper_english
# or
bibtex paper_chinese
```

#### Error: "LaTeX Error: File 'times.sty' not found"

**Solution:** Install additional LaTeX packages:
```bash
sudo apt-get install texlive-fonts-recommended texlive-fonts-extra
```

### Common Python Errors

#### Error: "ModuleNotFoundError: No module named 'matplotlib'"

**Solution:** Install required packages:
```bash
pip install matplotlib numpy seaborn
```

#### Error: "FileNotFoundError: comprehensive_results.json"

**Solution:** Make sure you're running from the `figures/` directory:
```bash
cd COMBINED/figures
python generate_all_figures.py
```

#### Error: "Permission denied"

**Solution:** Make scripts executable:
```bash
chmod +x figures/*.py
```

---

## File Structure

After successful compilation, your directory structure should look like:

```
COMBINED/
├── paper_english.tex          # English LaTeX source
├── paper_chinese.tex          # Chinese LaTeX source
├── references.bib             # BibTeX references
├── paper_english.pdf          # Compiled English paper
├── paper_chinese.pdf          # Compiled Chinese paper
├── COMPILE_INSTRUCTIONS.md    # This file
│
├── figures/                   # Figure generation scripts
│   ├── generate_all_figures.py
│   ├── generate_performance_comparison.py
│   ├── generate_confusion_matrices.py
│   ├── generate_pr_curves.py
│   ├── requirements.txt
│   │
│   ├── f1_comparison_by_model.png/pdf
│   ├── f1_comparison_by_dataset.png/pdf
│   ├── metrics_comparison_llava15_coco.png/pdf
│   ├── improvement_heatmap.png/pdf
│   ├── confusion_matrix_*.png/pdf
│   ├── error_reduction_*.png/pdf
│   ├── pr_scatter_comparison.png/pdf
│   ├── pr_improvement_vectors_llava15.png/pdf
│   └── precision_recall_bars.png/pdf
│
└── combined_results/          # Experimental data
    └── comprehensive_results.json
```

---

## Quick Start Guide

For a complete build from scratch:

```bash
# 1. Generate all figures
cd COMBINED/figures
python generate_all_figures.py
cd ..

# 2. Compile English paper
pdflatex paper_english.tex
bibtex paper_english
pdflatex paper_english.tex
pdflatex paper_english.tex

# 3. Compile Chinese paper
xelatex paper_chinese.tex
bibtex paper_chinese
xelatex paper_chinese.tex
xelatex paper_chinese.tex

# 4. View results
ls -lh paper_*.pdf
```

---

## Clean Build

To remove all auxiliary files and start fresh:

```bash
cd COMBINED

# Remove LaTeX auxiliary files
rm -f *.aux *.log *.bbl *.blg *.out *.toc *.lof *.lot *.fls *.fdb_latexmk

# Remove generated PDFs (optional)
rm -f paper_english.pdf paper_chinese.pdf

# Remove generated figures (optional)
rm -f figures/*.png figures/*.pdf
```

---

## Additional Notes

### Figure Format

- All figures are generated in both **PNG** (for preview) and **PDF** (for LaTeX inclusion)
- PDF figures provide vector graphics for publication quality
- Resolution: 300 DPI for both formats

### LaTeX Compilation

- **English paper**: Use `pdflatex` (3 passes + 1 bibtex)
- **Chinese paper**: Use `xelatex` (3 passes + 1 bibtex)
- Multiple passes are required to resolve cross-references and citations

### Bibliography

- All references are in `references.bib`
- Uses plain bibliography style
- Includes VCD paper (arXiv:2311.16922) and AGLA paper (arXiv:2406.12718)

### Customization

To modify figures:
1. Edit the corresponding Python script in `figures/`
2. Re-run the script to regenerate
3. Re-compile the LaTeX document

To modify paper content:
1. Edit `paper_english.tex` or `paper_chinese.tex`
2. Re-compile using the appropriate command

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Verify all prerequisites are installed
3. Ensure you're using the correct compilation commands
4. Check file paths and permissions

---

## Version Information

- LaTeX: Requires TeXLive 2020 or later
- Python: Requires Python 3.7 or later
- Matplotlib: Requires 3.5.0 or later

---

**Last Updated:** 2025-10-18

