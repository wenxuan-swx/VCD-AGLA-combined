# Figure Generation Scripts for VCD+AGLA Paper

This directory contains Python scripts to generate all publication-quality figures for the VCD+AGLA academic paper.

## Overview

All figures are generated from the experimental results stored in `../combined_results/comprehensive_results.json`. The scripts use matplotlib and seaborn to create publication-quality visualizations in both PNG and PDF formats.

## Scripts

### 1. `generate_all_figures.py`
**Master script** that runs all individual figure generation scripts.

**Usage:**
```bash
python generate_all_figures.py
```

**Output:** All 13 figure sets (26 files total)

---

### 2. `generate_performance_comparison.py`
Generates performance comparison charts showing F1 scores, accuracy, precision, and recall.

**Figures generated:**
- `f1_comparison_by_model.png/pdf` - F1 scores grouped by model (3 subplots)
- `f1_comparison_by_dataset.png/pdf` - F1 scores grouped by dataset (POPE benchmarks)
- `metrics_comparison_llava15_coco.png/pdf` - All metrics for LLaVA-1.5 on COCO-POPE
- `improvement_heatmap.png/pdf` - Heatmap of F1 improvements across all configurations

**Usage:**
```bash
python generate_performance_comparison.py
```

**Key Features:**
- Bar charts with improvement annotations
- Color-coded by method (Baseline vs VCD+AGLA)
- Publication-quality formatting (300 DPI)

---

### 3. `generate_confusion_matrices.py`
Generates confusion matrix heatmaps and error analysis visualizations.

**Figures generated:**
- `confusion_matrix_baseline_llava15_coco.png/pdf` - Baseline confusion matrix
- `confusion_matrix_combined_llava15_coco.png/pdf` - VCD+AGLA confusion matrix
- `confusion_matrix_comparison_llava15_coco.png/pdf` - Side-by-side comparison (COCO-POPE)
- `confusion_matrix_comparison_llava15_aokvqa.png/pdf` - Side-by-side comparison (AOKVQA-POPE)
- `error_reduction_llava15_coco.png/pdf` - Error reduction analysis (FP, FN, Total)

**Usage:**
```bash
python generate_confusion_matrices.py
```

**Key Features:**
- Heatmaps with both counts and percentages
- Error reduction percentages (FP: -37.1%, FN: -16.1%, Total: -21.6%)
- Seaborn styling for professional appearance

---

### 4. `generate_pr_curves.py`
Generates precision-recall visualizations and trade-off analysis.

**Figures generated:**
- `pr_scatter_comparison.png/pdf` - Precision-recall scatter plot with improvement arrows
- `pr_improvement_vectors_llava15.png/pdf` - Improvement vectors for all datasets (LLaVA-1.5)
- `precision_recall_bars.png/pdf` - Grouped bar charts for precision and recall (6 subplots)

**Usage:**
```bash
python generate_pr_curves.py
```

**Key Features:**
- Scatter plots with F1 iso-curves
- Arrows showing baseline → VCD+AGLA improvement
- Color-coded by model/dataset

---

## Requirements

### Python Packages

```bash
pip install matplotlib numpy seaborn
```

Or install from requirements file:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
matplotlib>=3.5.0
numpy>=1.21.0
seaborn>=0.11.0
```

### Python Version

- Python 3.7 or later

---

## Quick Start

```bash
# Navigate to figures directory
cd COMBINED/figures

# Generate all figures
python generate_all_figures.py

# Verify output
ls -lh *.png *.pdf
```

---

## Output Files

After running `generate_all_figures.py`, you will have:

### Performance Comparison (4 figure sets)
```
f1_comparison_by_model.png/pdf          # 3 subplots: one per model
f1_comparison_by_dataset.png/pdf        # 2 subplots: COCO-POPE, AOKVQA-POPE
metrics_comparison_llava15_coco.png/pdf # 4 metrics: Acc, Prec, Rec, F1
improvement_heatmap.png/pdf             # 3×6 heatmap: models × datasets
```

### Confusion Matrices (5 figure sets)
```
confusion_matrix_baseline_llava15_coco.png/pdf      # Baseline only
confusion_matrix_combined_llava15_coco.png/pdf      # VCD+AGLA only
confusion_matrix_comparison_llava15_coco.png/pdf    # Side-by-side (COCO)
confusion_matrix_comparison_llava15_aokvqa.png/pdf  # Side-by-side (AOKVQA)
error_reduction_llava15_coco.png/pdf                # Error analysis
```

### Precision-Recall (3 figure sets)
```
pr_scatter_comparison.png/pdf           # 2 subplots with F1 iso-curves
pr_improvement_vectors_llava15.png/pdf  # All datasets for LLaVA-1.5
precision_recall_bars.png/pdf           # 6 subplots: 3 models × 2 datasets
```

**Total:** 13 figure sets = 26 files (PNG + PDF)

---

## Figure Specifications

### Format
- **PNG:** 300 DPI, RGB color space
- **PDF:** Vector graphics, publication-ready

### Styling
- **Font:** Serif (Times-like)
- **Font sizes:** 
  - Title: 12pt
  - Axis labels: 11pt
  - Tick labels: 9pt
  - Legend: 9pt
- **Colors:**
  - Baseline: Blue (#3498db)
  - VCD+AGLA: Red (#e74c3c)
  - Model-specific: Red, Blue, Green

### Dimensions
- Single plots: 8×5 inches
- Multi-panel: 12×5 or 15×4 inches
- Heatmaps: 10×4 inches

---

## Data Source

All figures are generated from:
```
../combined_results/comprehensive_results.json
```

This JSON file contains experimental results for:
- **3 models:** LLaVA-1.5-7B, LLaVA-1.6-7B, Qwen-VL
- **6 datasets:** COCO-POPE, AOKVQA-POPE, 4× Hallucinogen subsets
- **2 methods:** Baseline, VCD+AGLA Combined
- **Metrics:** Accuracy, Precision, Recall, F1, Yes Proportion

---

## Customization

### Modifying Figure Appearance

Edit the matplotlib rcParams at the top of each script:

```python
plt.rcParams['figure.dpi'] = 300        # Resolution
plt.rcParams['font.size'] = 10          # Base font size
plt.rcParams['font.family'] = 'serif'   # Font family
```

### Changing Colors

Modify the color definitions in each script:

```python
# In generate_performance_comparison.py
bars1 = ax.bar(..., color='#3498db')  # Baseline color
bars2 = ax.bar(..., color='#e74c3c')  # Combined color
```

### Adding New Figures

1. Create a new Python script in this directory
2. Import the data from `comprehensive_results.json`
3. Use matplotlib/seaborn to create visualizations
4. Save as both PNG and PDF
5. Add the script to `generate_all_figures.py`

---

## Troubleshooting

### Issue: "FileNotFoundError: comprehensive_results.json"

**Solution:** Make sure you're running from the `figures/` directory:
```bash
cd COMBINED/figures
python generate_all_figures.py
```

### Issue: "ModuleNotFoundError: No module named 'matplotlib'"

**Solution:** Install required packages:
```bash
pip install matplotlib numpy seaborn
```

### Issue: Figures look different than expected

**Solution:** Check matplotlib version:
```bash
python -c "import matplotlib; print(matplotlib.__version__)"
```
Requires matplotlib >= 3.5.0

### Issue: Permission denied

**Solution:** Make scripts executable:
```bash
chmod +x *.py
```

---

## Integration with LaTeX

The generated PDF figures are automatically included in the LaTeX papers:

**In `paper_english.tex` or `paper_chinese.tex`:**
```latex
\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{figures/f1_comparison_by_model.pdf}
\caption{F1 score comparison across models and datasets.}
\label{fig:f1_comparison}
\end{figure}
```

**Note:** Use PDF format for LaTeX (vector graphics, scalable)

---

## Performance

- **Total generation time:** ~10-15 seconds (all figures)
- **Individual scripts:** ~3-5 seconds each
- **Memory usage:** < 500 MB

---

## Version History

- **v1.0** (2025-10-18): Initial release
  - 13 figure sets
  - 3 generation scripts
  - Master script for batch generation

---

## Contact

For questions or issues with figure generation, please refer to the main project documentation or the compilation instructions in `../COMPILE_INSTRUCTIONS.md`.

---

**Last Updated:** 2025-10-18

