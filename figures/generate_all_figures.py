#!/usr/bin/env python3
"""
Master script to generate all figures for VCD+AGLA paper.
Runs all individual figure generation scripts.
"""

import os
import sys

def main():
    """Generate all figures for the paper."""
    print("=" * 70)
    print("VCD+AGLA Paper - Figure Generation")
    print("=" * 70)
    print()
    
    # Change to figures directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    scripts = [
        'generate_performance_comparison.py',
        'generate_confusion_matrices.py',
        'generate_pr_curves.py'
    ]
    
    for script in scripts:
        print(f"\n{'=' * 70}")
        print(f"Running: {script}")
        print('=' * 70)
        
        try:
            # Import and run the script
            script_name = script.replace('.py', '')
            module = __import__(script_name)
            module.main()
        except Exception as e:
            print(f"ERROR running {script}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 70)
    print("All figures generated successfully!")
    print("=" * 70)
    print("\nGenerated files in COMBINED/figures/:")
    print("\nPerformance Comparison:")
    print("  - f1_comparison_by_model.png/pdf")
    print("  - f1_comparison_by_dataset.png/pdf")
    print("  - metrics_comparison_llava15_coco.png/pdf")
    print("  - improvement_heatmap.png/pdf")
    print("\nConfusion Matrices:")
    print("  - confusion_matrix_baseline_llava15_coco.png/pdf")
    print("  - confusion_matrix_combined_llava15_coco.png/pdf")
    print("  - confusion_matrix_comparison_llava15_coco.png/pdf")
    print("  - confusion_matrix_comparison_llava15_aokvqa.png/pdf")
    print("  - error_reduction_llava15_coco.png/pdf")
    print("\nPrecision-Recall:")
    print("  - pr_scatter_comparison.png/pdf")
    print("  - pr_improvement_vectors_llava15.png/pdf")
    print("  - precision_recall_bars.png/pdf")
    print("\nTotal: 13 figure sets (26 files: PNG + PDF)")
    print("=" * 70)

if __name__ == '__main__':
    main()

