# Figure Audit Report - paper_english.tex

**Date:** 2025-10-26  
**Purpose:** Identify unreferenced and redundant figures for cleanup

---

## Summary

### Current State
- **Total PDF figures in `figures/`:** 18
- **Total PDF figures in `overleaf_upload/figures/`:** 11
- **Figures defined in LaTeX (with `\label{fig:...}`):** 11
- **Figures actually referenced in text (with `\ref{fig:...}`):** 5

### Issues Found
1. **6 figures defined but NEVER referenced** in the main text
2. **7 unreferenced PDF files** in `figures/` directory
3. **Potential redundancy** between separate and unified heatmaps

---

## Detailed Analysis

### 1. Figures Defined in LaTeX but NEVER Referenced

These figures have `\label{fig:...}` and `\includegraphics` but are NEVER cited with `\ref{fig:...}`:

| Label | File | Section | Status |
|-------|------|---------|--------|
| `fig:f1_comparison_pope` | `f1_comparison_by_model.pdf` | 5.1.1 | ❌ UNREFERENCED |
| `fig:improvement_heatmap_pope` | `improvement_heatmap.pdf` | 5.1.1 | ❌ UNREFERENCED |
| `fig:error_reduction_pope` | `error_reduction_llava15_coco.pdf` | 5.1.2 | ❌ UNREFERENCED |
| `fig:f1_comparison_hallucinogen` | `f1_comparison_hallucinogen.pdf` | 5.2.1 | ❌ UNREFERENCED |
| `fig:improvement_heatmap_hallucinogen` | `improvement_heatmap_hallucinogen.pdf` | 5.2.1 | ❌ UNREFERENCED |
| `fig:error_reduction_hallucinogen` | `error_reduction_hallucinogen.pdf` | 5.2.2 | ❌ UNREFERENCED |

### 2. Figures Actually Referenced in Text

Only these 5 figures are cited in the main text:

| Label | File | Referenced In | Status |
|-------|------|---------------|--------|
| `fig:confusion_pope` | `confusion_matrix_comparison_llava15_coco.pdf` | Section 5.1.2, 6.1 | ✅ USED |
| `fig:confusion_hallucinogen` | `confusion_matrix_comparison_hallucinogen.pdf` | Section 5.2.2, 6.1 | ✅ USED |
| `fig:pr_curve_pope` | `pr_scatter_comparison.pdf` | Section 5.1.3 | ✅ USED |
| `fig:pr_curve_hallucinogen` | `pr_scatter_hallucinogen.pdf` | Section 5.2.3 | ✅ USED |
| `fig:improvement_heatmap_unified` | `improvement_heatmap_unified.pdf` | Section 5.3 | ✅ USED |

### 3. Unreferenced PDF Files in `figures/` Directory

These PDF files exist but are NOT included in the LaTeX document at all:

| File | Likely Purpose | Status |
|------|----------------|--------|
| `confusion_matrix_baseline_llava15_coco.pdf` | Individual baseline confusion matrix | ❌ UNUSED |
| `confusion_matrix_combined_llava15_coco.pdf` | Individual combined confusion matrix | ❌ UNUSED |
| `confusion_matrix_comparison_llava15_aokvqa.pdf` | A-OKVQA confusion matrix | ❌ UNUSED |
| `f1_comparison_by_dataset.pdf` | Alternative F1 comparison | ❌ UNUSED |
| `metrics_comparison_llava15_coco.pdf` | Metrics comparison | ❌ UNUSED |
| `precision_recall_bars.pdf` | PR bar chart | ❌ UNUSED |
| `pr_improvement_vectors_llava15.pdf` | PR improvement vectors | ❌ UNUSED |

---

## Redundancy Analysis

### Heatmap Redundancy

**Current situation:**
- `improvement_heatmap.pdf` - POPE only (2 subsets × 3 models)
- `improvement_heatmap_hallucinogen.pdf` - Hallucinogen only (4 subsets × 3 models)
- `improvement_heatmap_unified.pdf` - Both benchmarks (6 subsets × 3 models)

**Analysis:**
- The unified heatmap **contains all information** from the two separate heatmaps
- The separate heatmaps are **NOT referenced** in the text
- The unified heatmap **IS referenced** in Section 5.3

**Recommendation:**
- ✅ **KEEP:** `improvement_heatmap_unified.pdf` (referenced and comprehensive)
- ❌ **DELETE:** `improvement_heatmap.pdf` (redundant, unreferenced)
- ❌ **DELETE:** `improvement_heatmap_hallucinogen.pdf` (redundant, unreferenced)

### F1 Comparison Redundancy

**Current situation:**
- `f1_comparison_by_model.pdf` - POPE F1 comparison (included but unreferenced)
- `f1_comparison_by_dataset.pdf` - Alternative POPE F1 comparison (not included)
- `f1_comparison_hallucinogen.pdf` - Hallucinogen F1 comparison (included but unreferenced)

**Analysis:**
- These figures provide detailed F1 comparisons by model
- They are displayed in the paper but NEVER cited in the text
- They provide useful visual information not captured by tables

**Recommendation:**
- **OPTION A:** Delete all F1 comparison figures (rely on tables only)
- **OPTION B:** Keep and add references to them in the text
- **OPTION C:** Keep without references (visual support for tables)

**My recommendation:** OPTION B - Add references to make them useful

### Error Reduction Redundancy

**Current situation:**
- `error_reduction_llava15_coco.pdf` - POPE error reduction (included but unreferenced)
- `error_reduction_hallucinogen.pdf` - Hallucinogen error reduction (included but unreferenced)

**Analysis:**
- These figures visualize the error reduction statistics
- They complement the confusion matrices
- They are displayed but NEVER cited

**Recommendation:**
- **OPTION A:** Delete (information already in confusion matrices)
- **OPTION B:** Keep and add references to them in the text

**My recommendation:** OPTION B - Add references for completeness

---

## Cleanup Recommendations

### HIGH PRIORITY: Delete Unreferenced Files

**From `figures/` directory (7 files):**
```
confusion_matrix_baseline_llava15_coco.pdf
confusion_matrix_combined_llava15_coco.pdf
confusion_matrix_comparison_llava15_aokvqa.pdf
f1_comparison_by_dataset.pdf
metrics_comparison_llava15_coco.pdf
precision_recall_bars.pdf
pr_improvement_vectors_llava15.pdf
```

**From both directories (2 redundant heatmaps):**
```
improvement_heatmap.pdf
improvement_heatmap_hallucinogen.pdf
```

### MEDIUM PRIORITY: Add References to Existing Figures

Add `\ref{fig:...}` citations for these 6 figures that are displayed but unreferenced:

1. `fig:f1_comparison_pope` - Reference in Section 5.1.1 text
2. `fig:improvement_heatmap_pope` - **DELETE** (redundant with unified)
3. `fig:error_reduction_pope` - Reference in Section 5.1.2 text
4. `fig:f1_comparison_hallucinogen` - Reference in Section 5.2.1 text
5. `fig:improvement_heatmap_hallucinogen` - **DELETE** (redundant with unified)
6. `fig:error_reduction_hallucinogen` - Reference in Section 5.2.2 text

---

## Proposed Final Figure List

After cleanup, the paper should have **7 figures** (down from 11):

### POPE Benchmark (3 figures)
1. `f1_comparison_by_model.pdf` - F1 comparison by model
2. `confusion_matrix_comparison_llava15_coco.pdf` - Confusion matrix
3. `error_reduction_llava15_coco.pdf` - Error reduction analysis

### Hallucinogen Benchmark (3 figures)
4. `f1_comparison_hallucinogen.pdf` - F1 comparison
5. `confusion_matrix_comparison_hallucinogen.pdf` - Confusion matrix
6. `error_reduction_hallucinogen.pdf` - Error reduction analysis

### Cross-Benchmark Analysis (1 figure)
7. `improvement_heatmap_unified.pdf` - Unified heatmap (all 6 subsets)

### Precision-Recall Plots
**DECISION NEEDED:** Keep or delete?
- `pr_scatter_comparison.pdf` - POPE PR scatter (currently referenced)
- `pr_scatter_hallucinogen.pdf` - Hallucinogen PR scatter (currently referenced)

**If kept:** 9 figures total  
**If deleted:** 7 figures total

**My recommendation:** Keep PR plots (they provide unique insights on precision-recall trade-offs)

---

## Implementation Plan

### Step 1: Delete Redundant Heatmaps
- Remove `improvement_heatmap.pdf` from both directories
- Remove `improvement_heatmap_hallucinogen.pdf` from both directories
- Remove their `\includegraphics` and `\label` from LaTeX

### Step 2: Delete Unreferenced Files
- Remove 7 unused PDF files from `figures/` directory

### Step 3: Add References to Remaining Figures
- Add `\ref{fig:f1_comparison_pope}` in Section 5.1.1
- Add `\ref{fig:error_reduction_pope}` in Section 5.1.2
- Add `\ref{fig:f1_comparison_hallucinogen}` in Section 5.2.1
- Add `\ref{fig:error_reduction_hallucinogen}` in Section 5.2.2

### Step 4: Update UPLOAD_INSTRUCTIONS.txt
- Update figure count from 11 to 9
- Update file list

### Step 5: Verify
- Ensure all remaining figures are referenced
- Ensure all `\ref{fig:...}` have corresponding `\label{fig:...}`
- Test LaTeX compilation

---

## Final Statistics

### Before Cleanup
- PDF files in `figures/`: 18
- PDF files in `overleaf_upload/figures/`: 11
- Figures in LaTeX: 11
- Referenced figures: 5

### After Cleanup
- PDF files in `figures/`: 11 (delete 7)
- PDF files in `overleaf_upload/figures/`: 9 (delete 2)
- Figures in LaTeX: 9 (delete 2)
- Referenced figures: 9 (add 4 references)

### Space Saved
- Approximately 2-3 MB in `figures/` directory
- Cleaner, more maintainable codebase
- All figures properly referenced and justified

