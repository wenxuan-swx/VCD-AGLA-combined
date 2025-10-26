# F1 Comparison Figures Fix Summary

**Date:** 2025-10-26  
**Status:** ✅ COMPLETE

---

## Issues Identified

### Issue 1: POPE Figure Contains Incorrect Data ❌

**Figure:** `fig:f1_comparison_pope` (file: `f1_comparison_by_model.pdf`)

**Problem:**
- The figure was showing data from ALL 6 subsets (COCO, A-OKVQA, ID, Loc, VC, CF)
- Should only show POPE subsets (COCO and A-OKVQA)
- Hallucinogen data (ID, Loc, VC, CF) should NOT appear in this figure

**Root Cause:**
- The `generate_f1_comparison_by_model()` function in `generate_performance_comparison.py` was iterating through ALL datasets in the `dataset_names` dictionary:
  ```python
  dataset_names = {
      'coco_pope': 'COCO-POPE',
      'aokvqa_pope': 'AOKVQA-POPE',
      'hallucinogen_identification': 'Hallucinogen-ID',      # ❌ Should not be here
      'hallucinogen_localization': 'Hallucinogen-Loc',       # ❌ Should not be here
      'hallucinogen_visual_context': 'Hallucinogen-VC',      # ❌ Should not be here
      'hallucinogen_counterfactual': 'Hallucinogen-CF'       # ❌ Should not be here
  }
  ```

### Issue 2: Inconsistent Visual Styles ❌

**Figures:**
- `fig:f1_comparison_pope` (file: `f1_comparison_by_model.pdf`)
- `fig:f1_comparison_hallucinogen` (file: `f1_comparison_hallucinogen.pdf`)

**Problem:**
- Different color schemes
- Different bar arrangements
- Different legend formats
- Different axis labels and formatting
- Inconsistent visual presentation for the same type of information

**Comparison:**

| Aspect | POPE Figure (OLD) | Hallucinogen Figure (OLD) |
|--------|-------------------|---------------------------|
| **Colors** | 2 colors (Baseline: blue, Combined: red) | 4 colors (Baseline: red, VCD: blue, AGLA: green, Combined: purple) |
| **Methods shown** | Only Baseline + Combined | All 4 methods |
| **Bar width** | 0.35 | 0.2 |
| **Layout** | Side-by-side comparison | Grouped by method |
| **Annotations** | Improvement on Combined bars | Improvement on Combined bars |

---

## Solution Implemented

### Created New Unified Script

**File:** `figures/regenerate_f1_comparison_figures.py`

**Key Features:**
1. ✅ Separate data dictionaries for POPE and Hallucinogen
2. ✅ Identical visual styling for both figures
3. ✅ Both figures show all 4 methods: Baseline, VCD, AGLA, Combined
4. ✅ Consistent color scheme, layout, and formatting

**Unified Visual Style:**
```python
# Same for both figures
methods = ['Baseline', 'VCD', 'AGLA', 'Combined']
colors = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6']  # Red, Blue, Green, Purple
width = 0.2
```

### Figure 1: POPE F1 Comparison (FIXED)

**File:** `f1_comparison_by_model.pdf`

**Data shown:**
- ✅ COCO (POPE)
- ✅ A-OKVQA (POPE)
- ❌ NO Hallucinogen data

**Models:** LLaVA-1.5, LLaVA-1.6, Qwen-VL

**Methods:** Baseline, VCD, AGLA, Combined

**Visual style:**
- 4 colored bars per dataset (red, blue, green, purple)
- Improvement annotations on Combined bars
- Y-axis range: 70-95
- Grid lines with alpha=0.3

### Figure 2: Hallucinogen F1 Comparison (UPDATED)

**File:** `f1_comparison_hallucinogen.pdf`

**Data shown:**
- ✅ Identification
- ✅ Localization
- ✅ Visual Context
- ✅ Counterfactual

**Models:** LLaVA-1.5, LLaVA-1.6, Qwen-VL

**Methods:** Baseline, VCD, AGLA, Combined

**Visual style:**
- 4 colored bars per task (red, blue, green, purple) - SAME as POPE
- Improvement annotations on Combined bars
- Y-axis range: 65-90
- Grid lines with alpha=0.3

---

## Changes Made

### 1. Created New Script

**File:** `figures/regenerate_f1_comparison_figures.py`

**Purpose:** Generate both F1 comparison figures with:
- Correct data (POPE only for first figure)
- Consistent visual styling
- All 4 methods shown

### 2. Regenerated Figures

**Generated files:**
- `figures/f1_comparison_by_model.pdf` (POPE only - FIXED)
- `figures/f1_comparison_by_model.png` (POPE only - FIXED)
- `figures/f1_comparison_hallucinogen.pdf` (Updated styling)
- `figures/f1_comparison_hallucinogen.png` (Updated styling)

**Copied to Overleaf:**
- `overleaf_upload/figures/f1_comparison_by_model.pdf`
- `overleaf_upload/figures/f1_comparison_hallucinogen.pdf`

### 3. Updated Figure Captions

**POPE Figure Caption (Updated):**

**Before:**
```latex
\caption{F1 score comparison across models and POPE datasets. VCD+AGLA 
consistently outperforms baseline across all configurations. Improvement 
values are shown above bars.}
```

**After:**
```latex
\caption{F1 score comparison across models and POPE datasets (COCO and 
A-OKVQA). Shows performance of Baseline, VCD Only, AGLA Only, and VCD+AGLA 
(Combined) methods. The Combined method consistently outperforms all other 
approaches. Improvement values (relative to Baseline) are shown above 
Combined bars.}
```

**Hallucinogen Figure Caption (Updated):**

**Before:**
```latex
\caption{F1 score comparison across models and Hallucinogen task types. 
VCD+AGLA consistently outperforms baseline across all configurations. 
Improvement values are shown above bars. Note the particularly strong 
gains on Identification and Localization tasks.}
```

**After:**
```latex
\caption{F1 score comparison across models and Hallucinogen task types 
(Identification, Localization, Visual Context, Counterfactual). Shows 
performance of Baseline, VCD Only, AGLA Only, and VCD+AGLA (Combined) 
methods. The Combined method consistently outperforms all other approaches. 
Improvement values (relative to Baseline) are shown above Combined bars. 
Note the particularly strong gains on Identification and Localization tasks.}
```

---

## Verification

### Data Correctness ✅

**POPE Figure (`f1_comparison_by_model.pdf`):**
- ✅ Shows only COCO and A-OKVQA
- ✅ No Hallucinogen data present
- ✅ All 3 models shown (LLaVA-1.5, LLaVA-1.6, Qwen-VL)
- ✅ All 4 methods shown (Baseline, VCD, AGLA, Combined)

**Hallucinogen Figure (`f1_comparison_hallucinogen.pdf`):**
- ✅ Shows all 4 task types (ID, Loc, VC, CF)
- ✅ All 3 models shown
- ✅ All 4 methods shown

### Visual Consistency ✅

**Both figures now have:**
- ✅ Same color scheme (Red, Blue, Green, Purple)
- ✅ Same bar width (0.2)
- ✅ Same layout (4 bars per category)
- ✅ Same legend format
- ✅ Same grid style (alpha=0.3, dashed)
- ✅ Same annotation style (improvement on Combined bars)
- ✅ Same font sizes and weights

### References ✅

**In paper:**
- ✅ `fig:f1_comparison_pope` referenced in Section 5.1.1 (line 400)
- ✅ `fig:f1_comparison_hallucinogen` referenced in Section 5.2.1 (line 548)
- ✅ Both figures properly labeled and captioned

---

## Before vs After Comparison

### POPE Figure

**Before:**
- ❌ Showed 6 datasets (COCO, A-OKVQA, ID, Loc, VC, CF)
- ❌ Only 2 methods (Baseline, Combined)
- ❌ Different color scheme than Hallucinogen figure

**After:**
- ✅ Shows 2 datasets (COCO, A-OKVQA) - POPE only
- ✅ All 4 methods (Baseline, VCD, AGLA, Combined)
- ✅ Same color scheme as Hallucinogen figure

### Hallucinogen Figure

**Before:**
- ✅ Showed 4 task types (correct)
- ✅ All 4 methods (correct)
- ❌ Different color scheme than POPE figure

**After:**
- ✅ Shows 4 task types (unchanged)
- ✅ All 4 methods (unchanged)
- ✅ Same color scheme as POPE figure

---

## Benefits

### 1. Data Accuracy ✅
- POPE figure now shows only POPE data
- No confusion between benchmarks
- Clear separation of POPE vs Hallucinogen results

### 2. Visual Consistency ✅
- Both figures use identical styling
- Easier for readers to compare across benchmarks
- Professional, cohesive presentation

### 3. Completeness ✅
- Both figures now show all 4 methods
- Readers can see individual contributions of VCD and AGLA
- Better understanding of ablation results

### 4. Clarity ✅
- Updated captions clearly describe what's shown
- Explicit mention of datasets/tasks included
- Clear explanation of improvement annotations

---

## Files Modified

### Created:
- `figures/regenerate_f1_comparison_figures.py` - New unified generation script

### Modified:
- `figures/f1_comparison_by_model.pdf` - Regenerated with correct POPE data
- `figures/f1_comparison_by_model.png` - Regenerated with correct POPE data
- `figures/f1_comparison_hallucinogen.pdf` - Regenerated with consistent styling
- `figures/f1_comparison_hallucinogen.png` - Regenerated with consistent styling
- `overleaf_upload/figures/f1_comparison_by_model.pdf` - Updated
- `overleaf_upload/figures/f1_comparison_hallucinogen.pdf` - Updated
- `paper_english.tex` - Updated both figure captions (lines 414, 563)

---

## Next Steps for User

### 1. Upload to Overleaf

Upload the updated figures:
- `overleaf_upload/figures/f1_comparison_by_model.pdf`
- `overleaf_upload/figures/f1_comparison_hallucinogen.pdf`

### 2. Compile and Verify

1. Click "Recompile" in Overleaf
2. Check Section 5.1.1 (POPE Overall Performance):
   - ✅ Figure shows only COCO and A-OKVQA
   - ✅ Figure shows all 4 methods with consistent colors
   - ✅ Caption correctly describes the content
3. Check Section 5.2.1 (Hallucinogen Overall Performance):
   - ✅ Figure shows all 4 task types
   - ✅ Figure uses same visual style as POPE figure
   - ✅ Caption correctly describes the content

### 3. Visual Inspection

Compare the two figures side-by-side:
- ✅ Same color scheme (Red, Blue, Green, Purple)
- ✅ Same bar arrangement and spacing
- ✅ Same legend format and position
- ✅ Same grid and axis styling

---

## Conclusion

Both issues have been successfully resolved:

1. ✅ **Issue 1 (Incorrect Data):** POPE figure now shows only POPE data (COCO + A-OKVQA)
2. ✅ **Issue 2 (Inconsistent Styling):** Both figures now use identical visual style

The figures are now:
- ✅ Accurate (correct data)
- ✅ Consistent (same visual style)
- ✅ Complete (all 4 methods shown)
- ✅ Clear (updated captions)
- ✅ Publication-ready

**Git Status:** Ready to commit

