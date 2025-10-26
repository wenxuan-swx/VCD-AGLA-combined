# VCD+AGLA Academic Papers - Quick Reference Card

## 🎯 What You Have

✅ **2 Academic Papers** (English + Chinese) in LaTeX format  
✅ **12 Publication-Quality Figures** (PNG + PDF)  
✅ **Complete Bibliography** with 25+ citations  
✅ **Python Scripts** to regenerate all figures  
✅ **Full Documentation** for compilation and usage

---

## ⚡ Quick Start (3 Steps)

### Step 1: Generate Figures (10 seconds)
```bash
cd /root/autodl-tmp/COMBINED/figures
python generate_all_figures.py
```

### Step 2: Compile English Paper (30 seconds)
```bash
cd /root/autodl-tmp/COMBINED
pdflatex paper_english.tex && bibtex paper_english && pdflatex paper_english.tex && pdflatex paper_english.tex
```

### Step 3: Compile Chinese Paper (30 seconds)
```bash
cd /root/autodl-tmp/COMBINED
xelatex paper_chinese.tex && bibtex paper_chinese && xelatex paper_chinese.tex && xelatex paper_chinese.tex
```

**Done!** You now have `paper_english.pdf` and `paper_chinese.pdf`

---

## 📁 Key Files

| File | Description |
|------|-------------|
| `paper_english.tex` | English academic paper (LaTeX) |
| `paper_chinese.tex` | Chinese academic paper (LaTeX) |
| `references.bib` | Bibliography (25+ citations) |
| `figures/*.png` | Figures in PNG format (12 files) |
| `figures/*.pdf` | Figures in PDF format (12 files) |
| `COMPILE_INSTRUCTIONS.md` | Detailed compilation guide |
| `ACADEMIC_PAPERS_README.md` | Complete package overview |
| `DELIVERABLES_SUMMARY.md` | Full deliverables list |

---

## 📊 Paper Structure

Both papers follow the same structure:

1. **Abstract** (200-250 words)
2. **Introduction** (background, motivation, contributions)
3. **Related Work** (VCD, AGLA, hallucination mitigation)
4. **Methodology** (VCD, AGLA, proposed combination)
   - **Key:** Theoretical justification for combining methods
5. **Experimental Setup** (3 models, 6 datasets)
6. **Results and Analysis** (comprehensive evaluation)
7. **Discussion** (interpretation, limitations)
8. **Conclusion** (summary, future work)
9. **References** (25+ citations)

---

## 🎨 Figures Included

### Performance (4 figures)
- F1 comparison by model
- F1 comparison by dataset
- All metrics comparison
- Improvement heatmap

### Confusion Matrices (5 figures)
- Baseline confusion matrix
- VCD+AGLA confusion matrix
- Side-by-side comparison (COCO)
- Side-by-side comparison (AOKVQA)
- Error reduction analysis

### Precision-Recall (3 figures)
- P-R scatter with F1 iso-curves
- Improvement vectors
- P-R bar charts

**Total:** 12 figure sets (24 files)

---

## 📈 Key Results

### F1 Score Improvements
- **LLaVA-1.5:** +4.36% average (best: +5.06%)
- **LLaVA-1.6:** +3.34% average (best: +4.83%)
- **Qwen-VL:** +1.17% average (best: +1.35%)

### Error Reduction (LLaVA-1.5, COCO-POPE)
- **False Positives:** -37.1%
- **False Negatives:** -16.1%
- **Total Errors:** -21.6%

---

## 🔧 Requirements

### For English Paper
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
```

### For Chinese Paper
```bash
sudo apt-get install texlive-xetex texlive-lang-chinese
```

### For Figures
```bash
pip install matplotlib numpy seaborn
```

---

## 🚨 Important Notes

1. **Chinese paper MUST use `xelatex`** (not `pdflatex`)
2. **Generate figures BEFORE compiling** LaTeX
3. **Run LaTeX 3 times + bibtex once** for proper references
4. **Figures are in `figures/` subdirectory**

---

## 🎓 Theoretical Contribution

### Three-Way Contrastive Decoding
```
l_final = (1 + α_vcd + α_agla) × l_orig - α_vcd × l_noisy + α_agla × l_aug
```

### Why It Works
- **VCD:** Suppresses language-prior hallucinations (↓ false positives)
- **AGLA:** Enhances visual grounding (↓ false negatives)
- **Combined:** Dual-direction guidance (negative + positive)

---

## 📝 Suitable For

✅ Conference submissions (CVPR, NeurIPS, ICCV, ECCV)  
✅ Journal submissions (TPAMI, IJCV)  
✅ Capstone projects  
✅ Master's thesis  
✅ PhD dissertation  
✅ ArXiv preprints

---

## 🆘 Troubleshooting

### "File not found: figures/xxx.pdf"
```bash
cd figures && python generate_all_figures.py && cd ..
```

### "Package ctex Error" (Chinese paper)
```bash
sudo apt-get install texlive-xetex texlive-lang-chinese
```

### "ModuleNotFoundError: matplotlib"
```bash
pip install matplotlib numpy seaborn
```

### "Undefined references"
```bash
# Run bibtex and recompile
bibtex paper_english
pdflatex paper_english.tex
pdflatex paper_english.tex
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `QUICK_REFERENCE.md` | This file - quick commands |
| `COMPILE_INSTRUCTIONS.md` | Detailed compilation guide |
| `ACADEMIC_PAPERS_README.md` | Complete package overview |
| `DELIVERABLES_SUMMARY.md` | Full deliverables checklist |
| `figures/README.md` | Figure generation guide |

---

## ✅ Verification Checklist

Before submission:
- [ ] All figures generated (24 files in `figures/`)
- [ ] English paper compiles without errors
- [ ] Chinese paper compiles without errors
- [ ] All references appear correctly
- [ ] All figures appear in PDFs
- [ ] No LaTeX warnings
- [ ] PDFs are ~10 pages each

---

## 🎯 One-Command Build

### Build Everything
```bash
cd /root/autodl-tmp/COMBINED && \
cd figures && python generate_all_figures.py && cd .. && \
pdflatex paper_english.tex && bibtex paper_english && pdflatex paper_english.tex && pdflatex paper_english.tex && \
xelatex paper_chinese.tex && bibtex paper_chinese && xelatex paper_chinese.tex && xelatex paper_chinese.tex && \
echo "✅ Done! Check paper_english.pdf and paper_chinese.pdf"
```

---

## 📞 Need Help?

1. **Quick answers:** This file
2. **Compilation issues:** `COMPILE_INSTRUCTIONS.md`
3. **Figure problems:** `figures/README.md`
4. **General info:** `ACADEMIC_PAPERS_README.md`

---

## 🎉 You're Ready!

Your academic papers are **publication-ready**. Just:
1. Generate figures
2. Compile papers
3. Review PDFs
4. Submit!

**Good luck with your submission! 🚀**

---

**Location:** `/root/autodl-tmp/COMBINED/`  
**Status:** ✅ Complete  
**Version:** 1.0  
**Date:** 2025-10-18

