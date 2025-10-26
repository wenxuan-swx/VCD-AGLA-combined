# VCD+AGLA Academic Papers - Complete Package

This directory contains the complete academic paper package for the VCD+AGLA combined hallucination mitigation method, formatted for conference/journal submission (CVPR/NeurIPS style).

## 📋 Overview

This package includes:
- ✅ **2 LaTeX papers** (English + Chinese)
- ✅ **BibTeX references** with all citations
- ✅ **13 publication-quality figures** (26 files: PNG + PDF)
- ✅ **Python scripts** to regenerate all figures
- ✅ **Compilation instructions** for both papers

## 📁 Package Contents

```
COMBINED/
├── paper_english.tex              # English LaTeX source (main paper)
├── paper_chinese.tex              # Chinese LaTeX source (中文论文)
├── references.bib                 # BibTeX references (shared)
├── COMPILE_INSTRUCTIONS.md        # Detailed compilation guide
├── ACADEMIC_PAPERS_README.md      # This file
│
├── figures/                       # All figures and generation scripts
│   ├── generate_all_figures.py   # Master script (run this!)
│   ├── generate_performance_comparison.py
│   ├── generate_confusion_matrices.py
│   ├── generate_pr_curves.py
│   ├── requirements.txt          # Python dependencies
│   ├── README.md                 # Figure generation guide
│   │
│   └── [26 figure files]         # 13 sets × 2 formats (PNG + PDF)
│       ├── f1_comparison_by_model.png/pdf
│       ├── f1_comparison_by_dataset.png/pdf
│       ├── metrics_comparison_llava15_coco.png/pdf
│       ├── improvement_heatmap.png/pdf
│       ├── confusion_matrix_*.png/pdf (5 sets)
│       ├── error_reduction_*.png/pdf
│       └── pr_*.png/pdf (3 sets)
│
└── combined_results/              # Experimental data
    └── comprehensive_results.json # Source data for all figures
```

## 🚀 Quick Start

### 1. Generate All Figures

```bash
cd COMBINED/figures
python generate_all_figures.py
```

This creates 26 files (13 PNG + 13 PDF) in about 10-15 seconds.

### 2. Compile English Paper

```bash
cd COMBINED
pdflatex paper_english.tex
bibtex paper_english
pdflatex paper_english.tex
pdflatex paper_english.tex
```

Output: `paper_english.pdf`

### 3. Compile Chinese Paper

```bash
cd COMBINED
xelatex paper_chinese.tex
bibtex paper_chinese
xelatex paper_chinese.tex
xelatex paper_chinese.tex
```

Output: `paper_chinese.pdf`

**Note:** Chinese paper requires `xelatex` (not `pdflatex`) for CJK font support.

## 📄 Paper Structure

Both papers follow the same academic structure:

### 1. Abstract (200-250 words)
Concise summary of research, methods, and key results.

### 2. Introduction
- Background on LVLMs and hallucination problem
- Motivation for combining VCD and AGLA
- Research question and contributions
- Paper organization

### 3. Related Work
- Object hallucination in LVLMs
- Hallucination mitigation approaches
- VCD and AGLA methods
- Contrastive decoding frameworks

### 4. Methodology
**4.1 Preliminaries** - LVLM formulation

**4.2 Visual Contrastive Decoding (VCD)**
- Noise injection via DDPM
- Contrastive formulation
- Plausibility constraint

**4.3 Attention-Guided Language Augmentation (AGLA)**
- GradCAM attention maps
- Adaptive masking
- Additive formulation

**4.4 Proposed VCD+AGLA Combination**
- **Theoretical justification** (complementary error types, dual-direction guidance)
- **Three-way contrastive decoding** formulation
- Mathematical derivation
- Implementation details

### 5. Experimental Setup
- Datasets: POPE (COCO, AOKVQA) + Hallucinogen (4 subsets)
- Models: LLaVA-1.5-7B, LLaVA-1.6-7B, Qwen-VL
- Metrics: Accuracy, Precision, Recall, F1
- Baselines: Baseline, VCD Only, AGLA Only, VCD+AGLA

### 6. Results and Analysis
- Main results on POPE benchmarks (Table 1)
- Hallucinogen benchmark results (Table 2)
- Error analysis with confusion matrices (Figures 1-2)
- Ablation studies (Table 3)
- Precision-recall trade-offs (Figure 3)

### 7. Discussion
- Why the combination works (complementary mechanisms)
- Model-dependent effectiveness
- Limitations (computational cost, hyperparameters, auxiliary model)
- Practical recommendations

### 8. Conclusion
- Summary of contributions
- Key findings (F1 improvements, error reduction)
- Future work directions

### 9. References
- 25+ citations including VCD, AGLA, LLaVA, BLIP, POPE, Hallucinogen

## 📊 Key Results Highlighted

### Performance Improvements
- **LLaVA-1.5:** +4.36% average F1 (best: +5.06% on AOKVQA-POPE)
- **LLaVA-1.6:** +3.34% average F1
- **Qwen-VL:** +1.17% average F1

### Error Reduction (LLaVA-1.5 on COCO-POPE)
- **False Positives:** -37.1% (140 → 88)
- **False Negatives:** -16.1% (397 → 333)
- **Total Errors:** -21.6%

### Complementary Mechanisms
- VCD targets false positives (hallucinated objects)
- AGLA targets false negatives (missed objects)
- Combined method achieves super-additive improvements

## 🎨 Figures Included

### Performance Comparison (4 figures)
1. **f1_comparison_by_model** - F1 scores across models and datasets
2. **f1_comparison_by_dataset** - F1 scores grouped by dataset
3. **metrics_comparison_llava15_coco** - All metrics for LLaVA-1.5
4. **improvement_heatmap** - F1 improvements across all configurations

### Confusion Matrices (5 figures)
5. **confusion_matrix_baseline_llava15_coco** - Baseline confusion matrix
6. **confusion_matrix_combined_llava15_coco** - VCD+AGLA confusion matrix
7. **confusion_matrix_comparison_llava15_coco** - Side-by-side (COCO)
8. **confusion_matrix_comparison_llava15_aokvqa** - Side-by-side (AOKVQA)
9. **error_reduction_llava15_coco** - Error reduction analysis

### Precision-Recall (3 figures)
10. **pr_scatter_comparison** - P-R scatter with F1 iso-curves
11. **pr_improvement_vectors_llava15** - Improvement vectors
12. **precision_recall_bars** - P-R bar charts (6 subplots)

All figures are publication-quality (300 DPI, vector PDF).

## 🔧 Requirements

### LaTeX (English Paper)
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
```

### LaTeX (Chinese Paper)
```bash
sudo apt-get install texlive-xetex texlive-lang-chinese
```

### Python (Figure Generation)
```bash
pip install matplotlib numpy seaborn
```

## 📖 Theoretical Contributions

### Novel Three-Way Contrastive Decoding

The paper introduces a principled formulation combining VCD and AGLA:

```
l_final = (1 + α_vcd + α_agla) × l_orig - α_vcd × l_noisy + α_agla × l_aug
```

### Theoretical Justification

**Complementary Error Types:**
- VCD: Suppresses language-prior-driven hallucinations (reduces FP)
- AGLA: Enhances visual grounding (reduces FN)

**Dual-Direction Guidance:**
- Negative constraint (VCD): Suppresses unsupported tokens
- Positive enhancement (AGLA): Amplifies visually-grounded tokens

**Synergistic Mechanism:**
- VCD operates on visual encoding (degradation reveals biases)
- AGLA operates on visual attention (focusing improves grounding)

## 📝 Writing Style

Both papers use:
- **Third person** perspective
- **Formal academic tone**
- **Past tense** for methods and experiments
- **Present tense** for general truths and contributions
- **Passive voice** where appropriate
- **Mathematical notation** in LaTeX math mode

## 🌐 Language Versions

### English Paper (`paper_english.tex`)
- Full academic paper in English
- ~8,000 words
- Suitable for CVPR, NeurIPS, ICCV, ECCV, etc.

### Chinese Paper (`paper_chinese.tex`)
- Complete translation in Chinese (中文)
- Identical structure and content
- Uses `ctex` package for proper Chinese typesetting
- Suitable for Chinese academic journals/conferences

## 📚 Citations

The papers cite:
- **VCD paper:** arXiv:2311.16922 (Leng et al., 2023)
- **AGLA paper:** arXiv:2406.12718 (Sun et al., 2024)
- **LLaVA papers:** NeurIPS 2023, arXiv:2310.03744, arXiv:2401.13601
- **Qwen-VL:** arXiv:2308.12966
- **BLIP:** ICML 2022
- **POPE:** EMNLP 2023
- **Hallucinogen:** arXiv:2310.14566
- **GradCAM:** ICCV 2017
- **DDPM:** NeurIPS 2020
- And more...

All references are in `references.bib` with proper BibTeX formatting.

## 🎯 Intended Use

These papers are designed for:
- ✅ Conference submissions (CVPR, NeurIPS, ICCV, ECCV, AAAI, etc.)
- ✅ Journal submissions (TPAMI, IJCV, etc.)
- ✅ Capstone project reports
- ✅ Master's thesis chapters
- ✅ PhD dissertation chapters
- ✅ Technical reports
- ✅ ArXiv preprints

## 🔄 Regenerating Content

### To regenerate figures:
```bash
cd figures
python generate_all_figures.py
```

### To modify paper content:
1. Edit `paper_english.tex` or `paper_chinese.tex`
2. Recompile using appropriate commands

### To add new references:
1. Add entries to `references.bib`
2. Cite in paper using `\cite{key}`
3. Recompile with bibtex

## 📦 Distribution

This package is self-contained and includes:
- All source files (LaTeX, Python, BibTeX)
- All generated figures
- All experimental data
- Complete documentation

You can share the entire `COMBINED/` directory for reproducibility.

## ⚠️ Important Notes

1. **Chinese paper requires xelatex** (not pdflatex)
2. **Figures must be generated before compiling** LaTeX
3. **Multiple LaTeX passes required** (3× + 1× bibtex)
4. **Python 3.7+ required** for figure generation
5. **Seaborn must be installed** for confusion matrices

## 📞 Support

For detailed instructions, see:
- `COMPILE_INSTRUCTIONS.md` - Complete compilation guide
- `figures/README.md` - Figure generation guide

## ✅ Quality Checklist

Before submission, verify:
- [ ] All figures generated successfully (26 files)
- [ ] English paper compiles without errors
- [ ] Chinese paper compiles without errors
- [ ] All references resolve correctly
- [ ] All figures appear in PDFs
- [ ] No LaTeX warnings about missing references
- [ ] Page count is reasonable (~8-10 pages)
- [ ] Figures are high quality (300 DPI)
- [ ] Mathematical notation is correct
- [ ] Citations are properly formatted

## 🎓 Academic Integrity

These papers are based on genuine experimental results from the VCD+AGLA combined method. All data, code, and results are reproducible from the files in this package.

---

**Last Updated:** 2025-10-18

**Package Version:** 1.0

**Status:** ✅ Complete and ready for submission

