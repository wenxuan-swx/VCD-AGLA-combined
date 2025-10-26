#!/usr/bin/env python3
"""
Generate unified cross-benchmark heatmap showing F1 improvements across all 6 subsets.
This provides a comprehensive view of VCD+AGLA performance across POPE and Hallucinogen benchmarks.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_unified_heatmap():
    """
    Generate unified heatmap showing F1 improvements across all evaluation subsets.
    
    Data structure: 3 models × 6 subsets
    - POPE: COCO, A-OKVQA
    - Hallucinogen: Identification, Localization, Visual Context, Counterfactual
    """
    
    # F1 improvement data (from tables in paper)
    # Rows: LLaVA-1.5, LLaVA-1.6, Qwen-VL
    # Columns: COCO-POPE, A-OKVQA-POPE, ID, Loc, VC, CF
    data = np.array([
        # LLaVA-1.5
        [4.30, 5.06, 5.74, 4.18, 5.16, 5.61],
        # LLaVA-1.6
        [3.49, 4.83, 9.37, 11.49, 6.61, 5.15],
        # Qwen-VL
        [1.35, 1.32, 6.10, 5.35, 2.29, -0.35]
    ])
    
    models = ['LLaVA-1.5', 'LLaVA-1.6', 'Qwen-VL']
    
    # Use multi-line labels for better readability
    subsets = [
        'COCO\nPOPE', 
        'A-OKVQA\nPOPE', 
        'Identification\n(Hallucinogen)', 
        'Localization\n(Hallucinogen)', 
        'Visual Context\n(Hallucinogen)', 
        'Counterfactual\n(Hallucinogen)'
    ]
    
    # Create figure with appropriate size
    fig, ax = plt.subplots(figsize=(14, 4.5))
    
    # Create heatmap with custom colormap
    # Use RdYlGn (Red-Yellow-Green) with center at 3.0 (moderate improvement)
    sns.heatmap(
        data, 
        annot=True,  # Show values
        fmt='.2f',   # Format as 2 decimal places
        cmap='RdYlGn',  # Red (low) -> Yellow (medium) -> Green (high)
        center=3.0,  # Center colormap at 3% improvement
        xticklabels=subsets, 
        yticklabels=models,
        cbar_kws={'label': 'F1 Improvement (%)', 'shrink': 0.8},
        ax=ax,
        vmin=-1,   # Minimum value (for Qwen-VL Counterfactual)
        vmax=12,   # Maximum value (for LLaVA-1.6 Localization)
        linewidths=0.5,  # Add gridlines
        linecolor='gray',
        annot_kws={'fontsize': 10, 'weight': 'bold'}
    )
    
    # Customize labels
    ax.set_xlabel('Evaluation Subset', fontsize=13, weight='bold')
    ax.set_ylabel('Model', fontsize=13, weight='bold')
    
    # Rotate x-axis labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha='center', fontsize=10)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=11)
    
    # Add title
    plt.title('F1 Score Improvements Across All Evaluation Subsets', 
              fontsize=14, weight='bold', pad=15)
    
    # Add vertical line to separate POPE from Hallucinogen
    ax.axvline(x=2, color='black', linewidth=2, linestyle='--', alpha=0.5)
    
    # Add text annotations to indicate benchmark groups
    ax.text(1.0, -0.7, 'POPE Benchmark', ha='center', fontsize=11, 
            weight='bold', transform=ax.transData)
    ax.text(4.0, -0.7, 'Hallucinogen Benchmark', ha='center', fontsize=11, 
            weight='bold', transform=ax.transData)
    
    plt.tight_layout()
    
    # Save in both PDF and PNG formats
    plt.savefig('improvement_heatmap_unified.pdf', bbox_inches='tight', dpi=300)
    plt.savefig('improvement_heatmap_unified.png', bbox_inches='tight', dpi=300)
    
    print("✓ Generated improvement_heatmap_unified.pdf")
    print("✓ Generated improvement_heatmap_unified.png")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    print("\nPer-Model Averages:")
    for i, model in enumerate(models):
        avg = np.mean(data[i, :])
        print(f"  {model}: {avg:+.2f}%")
    
    print("\nPer-Subset Averages:")
    for j, subset in enumerate(['COCO-POPE', 'A-OKVQA-POPE', 'ID', 'Loc', 'VC', 'CF']):
        avg = np.mean(data[:, j])
        print(f"  {subset}: {avg:+.2f}%")
    
    print("\nBenchmark Averages:")
    pope_avg = np.mean(data[:, 0:2])
    hallucinogen_avg = np.mean(data[:, 2:6])
    print(f"  POPE: {pope_avg:+.2f}%")
    print(f"  Hallucinogen: {hallucinogen_avg:+.2f}%")
    
    print("\nOverall Average:")
    overall_avg = np.mean(data)
    print(f"  All subsets: {overall_avg:+.2f}%")
    
    print("\nRange:")
    print(f"  Min: {np.min(data):+.2f}% (Qwen-VL, Counterfactual)")
    print(f"  Max: {np.max(data):+.2f}% (LLaVA-1.6, Localization)")
    
    plt.close()

if __name__ == '__main__':
    print("Generating unified cross-benchmark heatmap...")
    print("="*60)
    generate_unified_heatmap()
    print("="*60)
    print("Done!")

